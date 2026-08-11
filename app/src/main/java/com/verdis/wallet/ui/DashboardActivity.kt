package com.verdis.wallet.ui

import android.app.Activity
import android.content.Intent
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.View
import android.widget.Button
import android.widget.LinearLayout
import android.widget.ListView
import android.widget.TextView
import android.widget.Toast
import com.verdis.wallet.R
import com.verdis.wallet.VerdisApp
import com.verdis.wallet.crypto.KeyManager
import com.verdis.wallet.net.SubstrateApi
import com.verdis.wallet.notification.NotificationMonitorService
import com.verdis.wallet.notification.NotificationPrefs
import java.math.BigInteger
import java.util.concurrent.Executors

class DashboardActivity : Activity() {

    private val executor = Executors.newSingleThreadExecutor()
    private val handler = Handler(Looper.getMainLooper()) // P1 fix: use main looper to prevent leak
    private var refreshRunnable: Runnable? = null
    private var keyManager: KeyManager? = null
    private lateinit var notifPrefs: NotificationPrefs

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_dashboard)
        keyManager = KeyManager(this)
        notifPrefs = NotificationPrefs(this)

        // Set address
        try {
            val address = keyManager?.getAddress("main")
            findViewById<TextView>(R.id.addressText)?.text = address
        } catch (e: Exception) {
            // Account not found
        }

        // Navigation buttons
        findViewById<Button>(R.id.sendBtn)?.setOnClickListener {
            startActivity(Intent(this, SendActivity::class.java))
        }
        findViewById<Button>(R.id.receiveBtn)?.setOnClickListener {
            startActivity(Intent(this, ReceiveActivity::class.java))
        }
        findViewById<Button>(R.id.stakeBtn)?.setOnClickListener {
            startActivity(Intent(this, StakingActivity::class.java))
        }
        findViewById<Button>(R.id.swapBtn)?.setOnClickListener {
            startActivity(Intent(this, DexActivity::class.java))
        }

        // Bottom nav
        findViewById<LinearLayout>(R.id.navHome)?.setOnClickListener { }
        findViewById<LinearLayout>(R.id.navDex)?.setOnClickListener {
            startActivity(Intent(this, DexActivity::class.java))
        }
        findViewById<LinearLayout>(R.id.navEco)?.setOnClickListener {
            startActivity(Intent(this, EcoActivity::class.java))
        }
        findViewById<LinearLayout>(R.id.navSettings)?.setOnClickListener {
            startActivity(Intent(this, SettingsActivity::class.java))
        }

        // Settings icon
        findViewById<Button>(R.id.settingsBtn)?.setOnClickListener {
            startActivity(Intent(this, SettingsActivity::class.java))
        }

        // Start notification monitoring if enabled
        if (notifPrefs.masterEnabled) {
            NotificationMonitorService.start(this)
        }

        refreshBalance()
    }

    private fun refreshBalance() {
        executor.execute {
            try {
                val api = (application as VerdisApp).substrateApi
                val address = keyManager?.getAddress("main") ?: return@execute
                val pubKey = com.verdis.wallet.crypto.Ss58Codec.decode(address)
                val balance = api.getBalance(address)
                val balanceDouble = balance.toDouble() / 1_000_000_000.0

                handler.post {
                    findViewById<TextView>(R.id.balanceText)?.text = String.format("%.4f VRDX", balanceDouble)
                }
            } catch (e: Exception) {
                handler.post {
                    findViewById<TextView>(R.id.balanceText)?.text = "0.0000 VRDX"
                }
            }
        }

        refreshRunnable = Runnable { refreshBalance() }
        val r = refreshRunnable; if (r != null) handler.postDelayed(r, 10000)
    }

    override fun onDestroy() {
        super.onDestroy()
        refreshRunnable?.let { handler.removeCallbacks(it) }
        // P1 fix: Shut down executor to prevent memory leaks
        executor.shutdownNow()
    }
}
