package com.verdis.wallet.notification

import android.app.Service
import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.os.PowerManager
import android.util.Log
import com.verdis.wallet.VerdisApp
import com.verdis.wallet.crypto.KeyManager
import com.verdis.wallet.crypto.Ss58Codec
import com.verdis.wallet.net.SubstrateApi
import org.json.JSONObject
import java.math.BigInteger

/**
 * Foreground service that monitors the Verdis blockchain for events and shows push notifications.
 * Polls the RPC endpoint at configurable intervals for:
 *  - Balance changes (incoming/outgoing transactions)
 *  - Staking reward events
 *  - Epoch transitions
 *  - Validator count changes
 *  - Block production status
 */
class NotificationMonitorService : Service() {

    companion object {
        private const val TAG = "VerdisNotifMonitor"
        const val ACTION_START = "com.verdis.wallet.START_MONITOR"
        const val ACTION_STOP = "com.verdis.wallet.STOP_MONITOR"
        const val ACTION_CHECK_NOW = "com.verdis.wallet.CHECK_NOW"

        fun start(context: Context) {
            val intent = Intent(context, NotificationMonitorService::class.java)
            intent.action = ACTION_START
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                context.startForegroundService(intent)
            } else {
                context.startService(intent)
            }
        }

        fun stop(context: Context) {
            val intent = Intent(context, NotificationMonitorService::class.java)
            context.stopService(intent)
        }
    }

    private val handler = Handler(Looper.getMainLooper())
    private var monitorRunnable: Runnable? = null
    private lateinit var prefs: NotificationPrefs
    private var keyManager: KeyManager? = null
    private var wakeLock: PowerManager.WakeLock? = null

    override fun onCreate() {
        super.onCreate()
        Log.i(TAG, "Notification monitor service created")

        // Create notification channels
        NotificationHelper.createChannels(this)
        prefs = NotificationPrefs(this)
        keyManager = KeyManager(this)

        // Acquire a partial wake lock so monitoring continues when screen is off
        val pm = getSystemService(Context.POWER_SERVICE) as PowerManager
        wakeLock = pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "Verdis:MonitorWakeLock")
        wakeLock?.acquire(10 * 60 * 1000L) // 10 minutes, re-acquired on each cycle
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_STOP -> {
                stopMonitoring()
                stopForeground(STOP_FOREGROUND_REMOVE)
                stopSelf()
                return START_NOT_STICKY
            }
            ACTION_CHECK_NOW -> {
                checkBlockchain()
            }
            else -> {
                startMonitoring()
            }
        }
        return START_STICKY
    }

    /**
     * Start the periodic monitoring loop.
     */
    private fun startMonitoring() {
        // Start as foreground service immediately
        startForeground(
            NotificationHelper.NOTIF_ID_FOREGROUND,
            NotificationHelper.buildForegroundNotification(this, 0, 0)
        )

        // Reset monitoring state on first start so we don't fire false notifications
        if (prefs.lastBlock == 0L) {
            prefs.resetMonitoringState()
        }

        scheduleCheck()
        Log.i(TAG, "Monitoring started, interval=${prefs.monitorIntervalSec}s")
    }

    /**
     * Stop the monitoring loop.
     */
    private fun stopMonitoring() {
        monitorRunnable?.let { handler.removeCallbacks(it) }
        monitorRunnable = null
        if (wakeLock?.isHeld == true) wakeLock?.release()
        Log.i(TAG, "Monitoring stopped")
    }

    private fun scheduleCheck() {
        monitorRunnable?.let { handler.removeCallbacks(it) }
        val interval = prefs.monitorIntervalSec * 1000L
        monitorRunnable = Runnable {
            checkBlockchain()
            scheduleCheck()
        }
        handler.postDelayed(monitorRunnable!!, interval)
    }

    /**
     * Main monitoring cycle — queries the blockchain and fires notifications.
     */
    private fun checkBlockchain() {
        if (!prefs.masterEnabled) return

        try {
            val app = application as VerdisApp
            val api = app.substrateApi

            // 1. Get current block number
            val headerResp = app.rpcClient.request("chain_getHeader")
            val blockNumber = headerResp.optJSONObject("result")?.optString("number") ?: "0x0"
            val currentBlock = blockNumber.removePrefix("0x").toLong(16)

            // 2. Get system health (peers)
            val healthResp = app.rpcClient.request("system_health")
            val peers = healthResp.optJSONObject("result")?.optInt("peers", 0) ?: 0

            // Update foreground notification
            startForeground(
                NotificationHelper.NOTIF_ID_FOREGROUND,
                NotificationHelper.buildForegroundNotification(this, currentBlock, peers)
            )

            // 3. Check epoch transition
            checkEpochTransition(api, currentBlock)

            // 4. Check balance change (transaction notification)
            checkBalanceChange(api)

            // 5. Check validator count change
            checkValidatorCount(api)

            // Re-acquire wake lock for next cycle
            if (wakeLock?.isHeld == false || wakeLock?.isHeld == null) {
                try { wakeLock?.acquire(10 * 60 * 1000L) } catch (e: Exception) { }
            }

        } catch (e: Exception) {
            Log.w(TAG, "Monitor cycle error: ${e.message}")
            // Don't stop the service — retry on next cycle
        }
    }

    /**
     * Check for epoch transitions by querying the DPoS session info.
     */
    private fun checkEpochTransition(api: SubstrateApi, currentBlock: Long) {
        if (!prefs.epochEnabled) return

        try {
            // Query session/epoch info — DPoS uses 600 blocks per epoch
            val epoch = currentBlock / 600

            if (prefs.lastEpoch > 0 && epoch > prefs.lastEpoch) {
                val app = application as VerdisApp
                val validatorsResp = app.rpcClient.request("session_validators")
                val validatorCount = validatorsResp.optJSONArray("result")?.length() ?: 5

                NotificationHelper.showEpochNotification(this, epoch, validatorCount)
            }

            prefs.lastEpoch = epoch
        } catch (e: Exception) {
            Log.w(TAG, "Epoch check error: ${e.message}")
        }
    }

    /**
     * Check for balance changes — fires transaction notifications.
     */
    private fun checkBalanceChange(api: SubstrateApi) {
        if (!prefs.transactionsEnabled) return

        try {
            val address = keyManager?.getAddress("main") ?: return

            val balance = api.getBalance(address)
            val balanceStr = balance.toString()

            val lastBalanceStr = prefs.lastBalance

            if (lastBalanceStr.isNotEmpty() && lastBalanceStr != balanceStr) {
                val lastBalance = BigInteger(lastBalanceStr)
                val diff = balance.subtract(lastBalance)
                val decimals = BigInteger.valueOf(1_000_000_000L)

                val amountDecimal = diff.abs().toDouble() / decimals.toDouble()

                if (amountDecimal > 0.0001) {
                    val amountStr = String.format("%.4f", amountDecimal)
                    val isIncoming = diff > BigInteger.ZERO

                    // Try to get the counterparty address from recent blocks
                    val counterparty = try {
                        getRecentTransactionCounterparty(api, address, isIncoming)
                    } catch (e: Exception) {
                        "unknown"
                    }

                    NotificationHelper.showTransactionNotification(
                        this,
                        amountStr,
                        isIncoming,
                        counterparty
                    )
                }
            }

            prefs.lastBalance = balanceStr
        } catch (e: Exception) {
            Log.w(TAG, "Balance check error: ${e.message}")
        }
    }

    /**
     * Try to find the counterparty address from recent block events.
     */
    private fun getRecentTransactionCounterparty(
        api: SubstrateApi,
        ourAddress: String,
        isIncoming: Boolean
    ): String {
        // Query the last few blocks for transfer events
        val app = application as VerdisApp
        val headerResp = app.rpcClient.request("chain_getHeader")
        val blockHex = headerResp.optJSONObject("result")?.optString("number") ?: "0x0"
        val currentBlock = blockHex.removePrefix("0x").toLong(16)

        // Check last 5 blocks
        for (i in 0..5) {
            val blockNum = currentBlock - i
            if (blockNum < 0) break

            val blockHash = try {
                val resp = app.rpcClient.request("chain_getBlockHash", listOf(blockNum))
                resp.optString("result")
            } catch (e: Exception) { continue }

            if (blockHash.isEmpty() || blockHash == "null") continue

            try {
                val blockResp = app.rpcClient.request("chain_getBlock", listOf(blockHash))
                val block = blockResp.optJSONObject("result")?.optJSONObject("block") ?: continue
                val extrinsics = block.optJSONArray("extrinsics") ?: continue

                for (j in 0 until extrinsics.length()) {
                    val ext = extrinsics.optJSONObject(j) ?: continue
                    // Check if this is a balance transfer
                    val method = ext.optJSONObject("method") ?: continue
                    val section = method.optString("section", "")
                    val method1 = method.optString("method", "")

                    if (section == "balances" && method1 == "transfer") {
                        // This is a transfer — extract counterparty
                        val args = method.optJSONObject("args") ?: continue
                        val dest = args.optString("dest", "")
                        val value = args.optString("value", "")

                        if (dest.isNotEmpty()) {
                            // If incoming, dest is our address, counterparty is the signer
                            // If outgoing, dest is the counterparty
                            if (isIncoming && (dest == ourAddress || dest.contains(ourAddress))) {
                                // Try to extract signer from signature payload
                                val signer = ext.optString("signer", "")
                                return if (signer.isNotEmpty()) signer else "unknown"
                            } else if (!isIncoming && !dest.contains(ourAddress)) {
                                return dest
                            }
                        }
                    }
                }
            } catch (e: Exception) {
                continue
            }
        }

        return "unknown"
    }

    /**
     * Check for changes in validator count.
     */
    private fun checkValidatorCount(api: SubstrateApi) {
        if (!prefs.validatorsEnabled) return

        try {
            val app = application as VerdisApp
            val resp = app.rpcClient.request("session_validators")
            val validatorCount = resp.optJSONArray("result")?.length() ?: 0

            if (prefs.lastValidatorCount > 0 && validatorCount != prefs.lastValidatorCount) {
                val change = validatorCount - prefs.lastValidatorCount
                val event = if (change > 0) {
                    "New validator joined (${validatorCount} active)"
                } else {
                    "Validator went offline (${validatorCount} active)"
                }
                NotificationHelper.showValidatorNotification(this, "Network", event)
            }

            prefs.lastValidatorCount = validatorCount
        } catch (e: Exception) {
            Log.w(TAG, "Validator check error: ${e.message}")
        }
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        stopMonitoring()
        Log.i(TAG, "Notification monitor service destroyed")
        super.onDestroy()
    }
}
