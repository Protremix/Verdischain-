package com.verdis.wallet.ui

import android.app.Activity
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.ProgressBar
import android.widget.Toast
import android.view.View
import androidx.fragment.app.FragmentActivity
import com.verdis.wallet.R
import com.verdis.wallet.VerdisApp
import com.verdis.wallet.crypto.ExtrinsicBuilder
import com.verdis.wallet.crypto.KeyManager
import com.verdis.wallet.crypto.Ss58Codec
import com.verdis.wallet.net.SubstrateApi
import com.verdis.wallet.security.BiometricGate
import com.verdis.wallet.security.SecurityHelper
import java.math.BigInteger
import java.util.concurrent.Executors

class SendActivity : FragmentActivity() {

    private val executor = Executors.newSingleThreadExecutor()
    private var keyManager: KeyManager? = null
    private lateinit var securityHelper: SecurityHelper

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_send)
        keyManager = KeyManager(this)
        securityHelper = SecurityHelper(this)

        val sendBtn = findViewById<Button>(R.id.sendBtn)
        val recipientInput = findViewById<EditText>(R.id.recipientInput)
        val amountInput = findViewById<EditText>(R.id.amountInput)

        sendBtn.setOnClickListener {
            val recipient = recipientInput.text.toString().trim()
            val amountStr = amountInput.text.toString().trim()

            if (recipient.isEmpty()) {
                Toast.makeText(this, "Enter recipient address", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            if (amountStr.isEmpty()) {
                Toast.makeText(this, "Enter amount", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            // P1 fix: Require biometric auth before sending
            BiometricGate.requireForSend(
                activity = this,
                securityHelper = securityHelper,
                onProceed = { executeSend(recipient, amountStr, sendBtn) },
                onCancel = { Toast.makeText(this, "Authentication cancelled", Toast.LENGTH_SHORT).show() }
            )
        }
    }

    private fun executeSend(recipient: String, amountStr: String, sendBtn: Button) {
        sendBtn.isEnabled = false
        sendBtn.text = "Sending..."
        // P1 fix: Show loading indicator during network operation
        findViewById<ProgressBar>(R.id.sendProgressBar)?.visibility = View.VISIBLE

        executor.execute {
            try {
                val app = application as VerdisApp
                val api = app.substrateApi

                // Get nonce
                val km = keyManager ?: throw IllegalStateException("KeyManager not initialized")
                val senderAddress = km.getAddress("main")
                val nonce = api.getNonce(senderAddress)

                // Get genesis hash
                val genesisHash = api.chainGetBlockHash(0)
                val blockHash = api.chainGetBlockHash(null)

                // Get runtime version
                val rtVersion = api.stateGetRuntimeVersion()
                val specVersion = rtVersion.optInt("specVersion", 0)
                val txVersion = rtVersion.optInt("transactionVersion", 0)

                // Decode recipient
                val destPubKey = Ss58Codec.decode(recipient)

                // Build call
                val (palletIdx, callIdx) = ExtrinsicBuilder.getPalletAndCallIndices(
                    app.networkConfig.rpcUrl, "Balances", "transfer"
                )

                val amount = BigInteger(amountStr).multiply(BigInteger.valueOf(1_000_000_000L))
                val callData = ExtrinsicBuilder.buildBalancesTransferCall(
                    palletIdx, callIdx, destPubKey, amount
                )

                // P1 fix: Get PIN from VerdisApp session (no hardcoded PIN)
                val pin = app.sessionPin
                    ?: throw Exception("PIN not available — please unlock the app first")

                // Sign and submit
                val extrinsic = ExtrinsicBuilder.buildAndSignExtrinsic(
                    km, "main", pin,
                    callData, nonce, BigInteger.ZERO,
                    specVersion, txVersion,
                    Ss58Codec.decode(genesisHash),
                    Ss58Codec.decode(blockHash)
                )

                val hexExtrinsic = "0x" + extrinsic.joinToString("") { "%02x".format(it) }
                val txHash = api.authorSubmitExtrinsic(hexExtrinsic)

                runOnUiThread {
                    findViewById<ProgressBar>(R.id.sendProgressBar)?.visibility = View.GONE
                    Toast.makeText(this, "TX sent: $txHash", Toast.LENGTH_LONG).show()
                    sendBtn.isEnabled = true
                    sendBtn.text = "Send"
                    finish()
                }
            } catch (e: Exception) {
                runOnUiThread {
                    findViewById<ProgressBar>(R.id.sendProgressBar)?.visibility = View.GONE
                    Toast.makeText(this, "Error: ${'$'}{e.message}", Toast.LENGTH_LONG).show()
                    sendBtn.isEnabled = true
                    sendBtn.text = "Send"
                }
            } finally {
                // P1 fix: Always hide progress bar, even if an unexpected error occurs
                runOnUiThread {
                    findViewById<ProgressBar>(R.id.sendProgressBar)?.visibility = View.GONE
                }
            }
        }
    }
    override fun onDestroy() {
        super.onDestroy()
        // P1 fix: Shut down executor to prevent memory leaks
        executor.shutdownNow()
    }
}
