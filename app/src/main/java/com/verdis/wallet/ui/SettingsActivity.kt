package com.verdis.wallet.ui

import android.app.Activity
import android.app.AlertDialog
import android.os.Build
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.SeekBar
import android.widget.Switch
import android.widget.TextView
import android.widget.Toast
import com.verdis.wallet.R
import com.verdis.wallet.VerdisApp
import com.verdis.wallet.crypto.KeyManager
import com.verdis.wallet.notification.NotificationMonitorService
import com.verdis.wallet.notification.NotificationPrefs
import com.verdis.wallet.security.SecurityHelper

class SettingsActivity : androidx.fragment.app.FragmentActivity() {

    private lateinit var securityHelper: SecurityHelper
    private lateinit var notifPrefs: NotificationPrefs
    private var keyManager: KeyManager? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_settings)

        securityHelper = (application as VerdisApp).securityHelper
        notifPrefs = NotificationPrefs(this)
        keyManager = KeyManager(this)

        // Network
        val rpcInput = findViewById<EditText>(R.id.rpcUrlInput)
        rpcInput.setText((application as VerdisApp).networkConfig.rpcUrl)

        findViewById<Button>(R.id.saveRpcBtn).setOnClickListener {
            val newUrl = rpcInput.text.toString().trim()
            (application as VerdisApp).updateRpcUrl(newUrl)
            Toast.makeText(this, "RPC URL saved", Toast.LENGTH_SHORT).show()
        }

        // Security
        findViewById<Switch>(R.id.biometricSwitch).apply {
            isChecked = securityHelper.isBiometricEnabled()
            setOnCheckedChangeListener { _, isChecked ->
                securityHelper.setBiometricEnabled(isChecked)
                Toast.makeText(this@SettingsActivity,
                    if (isChecked) "Biometric enabled" else "Biometric disabled",
                    Toast.LENGTH_SHORT).show()
            }
        }

        findViewById<Button>(R.id.changePinBtn).setOnClickListener {
            val input = EditText(this)
            input.inputType = android.text.InputType.TYPE_CLASS_NUMBER
            input.hint = "Enter new 6-digit PIN"
            AlertDialog.Builder(this)
                .setTitle("Change PIN")
                .setView(input)
                .setPositiveButton("OK") { _, _ ->
                    val newPin = input.text.toString().trim()
                    if (securityHelper.setPin(newPin)) {
                        Toast.makeText(this, "PIN changed", Toast.LENGTH_SHORT).show()
                    } else {
                        Toast.makeText(this, "PIN must be 6 digits", Toast.LENGTH_SHORT).show()
                    }
                }
                .setNegativeButton("Cancel", null)
                .show()
        }

        findViewById<Button>(R.id.exportWalletBtn).setOnClickListener {
            // Biometric gate for export
            val securityHelper = (application as com.verdis.wallet.VerdisApp).securityHelper
            com.verdis.wallet.security.BiometricGate.requireForExport(this, securityHelper, {
            AlertDialog.Builder(this)
                .setTitle("Export Wallet")
                .setMessage("WARNING: This will display your private key. Anyone with this key has full access to your funds. Continue?")
                .setPositiveButton("Show Key") { _, _ ->
                    try {
                        val pin = (application as VerdisApp).sessionPin ?: throw Exception("App locked — unlock first")
                    val seed = keyManager?.exportPrivateKey("main", pin)
                        val hexSeed = seed?.joinToString("") { "%02x".format(it) } ?: "No wallet"
                        AlertDialog.Builder(this)
                            .setTitle("Private Key (Hex)")
                            .setMessage(hexSeed)
                            .setPositiveButton("Copy") { _, _ ->
                                val clipboard = getSystemService(android.content.Context.CLIPBOARD_SERVICE)
                                        as android.content.ClipboardManager
                                clipboard.setPrimaryClip(
                                    android.content.ClipData.newPlainText("Private Key", hexSeed)
                                )
                                Toast.makeText(this, "Copied", Toast.LENGTH_SHORT).show()
                            }
                            .setNegativeButton("Close", null)
                            .show()
                    } catch (e: Exception) {
                        Toast.makeText(this, "Error: ${e.message}", Toast.LENGTH_LONG).show()
                    }
                }
                .setNegativeButton("Cancel", null)
                .show()
            }, {
                Toast.makeText(this, "Biometric/PIN required to export", Toast.LENGTH_SHORT).show()
            })
        }

        // ===== Notifications =====
        setupNotificationSettings()

        // Test notification button
        findViewById<Button>(R.id.testNotifBtn)?.setOnClickListener {
            com.verdis.wallet.notification.NotificationHelper.showTransactionNotification(
                this, "1.5", true, "5GrwvaEF5zX"
            )
            Toast.makeText(this, "Test notification sent", Toast.LENGTH_SHORT).show()
        }
    }

    private fun setupNotificationSettings() {
        // Master toggle
        findViewById<Switch>(R.id.notifMasterSwitch)?.apply {
            isChecked = notifPrefs.masterEnabled
            setOnCheckedChangeListener { switch, isChecked ->
                notifPrefs.masterEnabled = isChecked
                if (isChecked) {
                    // Request permission on Android 13+
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                        requestPermissions(arrayOf(android.Manifest.permission.POST_NOTIFICATIONS), 101)
                    }
                    NotificationMonitorService.start(this@SettingsActivity)
                    Toast.makeText(this@SettingsActivity, "Notifications enabled", Toast.LENGTH_SHORT).show()
                } else {
                    NotificationMonitorService.stop(this@SettingsActivity)
                    Toast.makeText(this@SettingsActivity, "Notifications disabled", Toast.LENGTH_SHORT).show()
                }
                // Enable/disable sub-toggles
                updateNotificationSubToggles(isChecked)
            }
        }

        // Transaction notifications
        findViewById<Switch>(R.id.notifTxSwitch)?.apply {
            isChecked = notifPrefs.transactionsEnabled
            setOnCheckedChangeListener { _, isChecked ->
                notifPrefs.transactionsEnabled = isChecked
            }
        }

        // Staking notifications
        findViewById<Switch>(R.id.notifStakingSwitch)?.apply {
            isChecked = notifPrefs.stakingEnabled
            setOnCheckedChangeListener { _, isChecked ->
                notifPrefs.stakingEnabled = isChecked
            }
        }

        // Epoch notifications
        findViewById<Switch>(R.id.notifEpochSwitch)?.apply {
            isChecked = notifPrefs.epochEnabled
            setOnCheckedChangeListener { _, isChecked ->
                notifPrefs.epochEnabled = isChecked
            }
        }

        // Validator notifications
        findViewById<Switch>(R.id.notifValidatorSwitch)?.apply {
            isChecked = notifPrefs.validatorsEnabled
            setOnCheckedChangeListener { _, isChecked ->
                notifPrefs.validatorsEnabled = isChecked
            }
        }

        // Monitor interval seekbar
        findViewById<SeekBar>(R.id.notifIntervalSeekbar)?.apply {
            progress = (notifPrefs.monitorIntervalSec - 10) / 5
            setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
                override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) {
                    val seconds = 10 + progress * 5
                    findViewById<TextView>(R.id.notifIntervalText)?.text = "${seconds}s"
                    notifPrefs.monitorIntervalSec = seconds
                }
                override fun onStartTrackingTouch(seekBar: SeekBar?) {}
                override fun onStopTrackingTouch(seekBar: SeekBar?) {}
            })
            // Set initial text
            findViewById<TextView>(R.id.notifIntervalText)?.text = "${notifPrefs.monitorIntervalSec}s"
        }

        updateNotificationSubToggles(notifPrefs.masterEnabled)
    }

    private fun updateNotificationSubToggles(enabled: Boolean) {
        listOf(R.id.notifTxSwitch, R.id.notifStakingSwitch, R.id.notifEpochSwitch, R.id.notifValidatorSwitch)
            .forEach { id ->
                findViewById<Switch>(id)?.isEnabled = enabled
            }
        findViewById<SeekBar>(R.id.notifIntervalSeekbar)?.isEnabled = enabled
    }
}
