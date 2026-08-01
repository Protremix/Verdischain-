package com.verdis.wallet

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.SwitchCompat
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.biometric.BiometricManager
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class SettingsFragment : Fragment() {

    companion object {
        private const val REQ_CREATE_PIN = 1001
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val view = inflater.inflate(R.layout.fragment_settings, container, false)

        val wallet = WalletManager.loadWallet(requireContext())
        if (wallet == null) {
            (activity as? MainActivity)?.showOnboarding()
            return view
        }

        // Wallet address
        view.findViewById<TextView>(R.id.tv_address).text = wallet.address
        view.findViewById<ImageView>(R.id.btn_copy_address).setOnClickListener {
            val clipboard = requireContext().getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
            clipboard.setPrimaryClip(ClipData.newPlainText("address", wallet.address))
            Toast.makeText(context, "Address copied!", Toast.LENGTH_SHORT).show()
        }

        // Security setup
        setupSecurity(view)

        // Backup seed phrase
        view.findViewById<LinearLayout>(R.id.btn_backup).setOnClickListener {
            if (wallet.seedPhrase != null) {
                AlertDialog.Builder(requireContext())
                    .setTitle("Seed Phrase")
                    .setMessage("Keep this safe — anyone with it can access your wallet:\n\n${wallet.seedPhrase}")
                    .setPositiveButton("Copy") { _, _ ->
                        val clipboard = requireContext().getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                        clipboard.setPrimaryClip(ClipData.newPlainText("seed", wallet.seedPhrase))
                        Toast.makeText(context, "Seed copied (keep safe!)", Toast.LENGTH_SHORT).show()
                    }
                    .setNegativeButton("Close", null)
                    .show()
            } else {
                Toast.makeText(context, "No seed phrase stored", Toast.LENGTH_SHORT).show()
            }
        }

        // Export private key
        view.findViewById<LinearLayout>(R.id.btn_export_key).setOnClickListener {
            AlertDialog.Builder(requireContext())
                .setTitle("Private Key")
                .setMessage("⚠️ WARNING: Anyone with this key has full access to your wallet!\n\n${wallet.privateKey}")
                .setPositiveButton("Copy") { _, _ ->
                    val clipboard = requireContext().getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                    clipboard.setPrimaryClip(ClipData.newPlainText("key", wallet.privateKey))
                    Toast.makeText(context, "Key copied (keep secret!)", Toast.LENGTH_SHORT).show()
                }
                .setNegativeButton("Close", null)
                .show()
        }

        // Block explorer
        view.findViewById<LinearLayout>(R.id.btn_explorer).setOnClickListener {
            val url = "https://verdischain.com/explorer"
            startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url)))
        }

        // Delete wallet
        view.findViewById<LinearLayout>(R.id.btn_delete_wallet).setOnClickListener {
            AlertDialog.Builder(requireContext())
                .setTitle("Delete Wallet")
                .setMessage("Are you sure? Make sure you have backed up your seed phrase or private key first.")
                .setPositiveButton("Delete") { _, _ ->
                    WalletManager.clearWallet(requireContext())
                    SecurityManager.removePin(requireContext())
                    SecurityManager.setBiometricEnabled(requireContext(), false)
                    (activity as? MainActivity)?.showOnboarding()
                    Toast.makeText(context, "Wallet deleted", Toast.LENGTH_SHORT).show()
                }
                .setNegativeButton("Cancel", null)
                .show()
        }

        // Network status
        loadNetworkInfo(view)
        return view
    }

    private fun setupSecurity(view: View) {
        val state = SecurityManager.getState(requireContext())
        val switchBiometric = view.findViewById<SwitchCompat>(R.id.switch_biometric)
        val tvBiometricStatus = view.findViewById<TextView>(R.id.tv_biometric_status)
        val tvPinStatus = view.findViewById<TextView>(R.id.tv_pin_status)
        val btnPin = view.findViewById<LinearLayout>(R.id.btn_pin)

        // Biometric toggle
        val canUseBio = BiometricManager.from(requireContext()).canAuthenticate(
            BiometricManager.Authenticators.BIOMETRIC_STRONG
        ) == BiometricManager.BIOMETRIC_SUCCESS

        if (!canUseBio) {
            switchBiometric.isEnabled = false
            tvBiometricStatus.text = "Not available on this device"
            tvBiometricStatus.setTextColor(0xFF4A6B5A.toInt())
        } else {
            switchBiometric.isChecked = state.biometricEnabled
            tvBiometricStatus.text = if (state.biometricEnabled) "Enabled" else "Fingerprint / Face ID"
        }

        switchBiometric.setOnCheckedChangeListener { _, isChecked ->
            if (isChecked && canUseBio) {
                SecurityManager.setBiometricEnabled(requireContext(), true)
                tvBiometricStatus.text = "Enabled"
                Toast.makeText(context, "Biometric unlock enabled", Toast.LENGTH_SHORT).show()
            } else {
                SecurityManager.setBiometricEnabled(requireContext(), false)
                tvBiometricStatus.text = if (canUseBio) "Fingerprint / Face ID" else "Not available"
                if (!isChecked) Toast.makeText(context, "Biometric disabled", Toast.LENGTH_SHORT).show()
            }
        }

        // PIN status
        tvPinStatus.text = if (state.hasPin) "Enabled • Tap to change" else "Tap to set PIN"

        // PIN management
        btnPin.setOnClickListener {
            if (state.hasPin) {
                // Show options: change or remove
                AlertDialog.Builder(requireContext())
                    .setTitle("PIN Code")
                    .setItems(arrayOf("Change PIN", "Remove PIN")) { _, which ->
                        when (which) {
                            0 -> {
                                // Change PIN — go through create flow
                                SecurityManager.removePin(requireContext())
                                startActivityForResult(Intent(requireContext(), CreatePinActivity::class.java), REQ_CREATE_PIN)
                            }
                            1 -> {
                                AlertDialog.Builder(requireContext())
                                    .setTitle("Remove PIN")
                                    .setMessage("Remove PIN protection? You'll need to set a new PIN to re-enable.")
                                    .setPositiveButton("Remove") { _, _ ->
                                        SecurityManager.removePin(requireContext())
                                        tvPinStatus.text = "Tap to set PIN"
                                        Toast.makeText(context, "PIN removed", Toast.LENGTH_SHORT).show()
                                    }
                                    .setNegativeButton("Cancel", null)
                                    .show()
                            }
                        }
                    }
                    .show()
            } else {
                // Create new PIN
                startActivityForResult(Intent(requireContext(), CreatePinActivity::class.java), REQ_CREATE_PIN)
            }
        }
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == REQ_CREATE_PIN && resultCode == android.app.Activity.RESULT_OK) {
            val tvPinStatus = view?.findViewById<TextView>(R.id.tv_pin_status)
            tvPinStatus?.text = "Enabled • Tap to change"
            Toast.makeText(context, "PIN protection enabled", Toast.LENGTH_SHORT).show()
        }
    }

    private fun loadNetworkInfo(view: View) {
        lifecycleScope.launch {
            try {
                val info = withContext(Dispatchers.IO) { VerdisApi.getBlockchainInfo() }
                view.findViewById<TextView>(R.id.tv_net_status).text =
                    if (info != null) "● Connected" else "● Offline"
                view.findViewById<TextView>(R.id.tv_net_status).setTextColor(
                    if (info != null) 0xFF34D399.toInt() else 0xFFEF4444.toInt()
                )
            } catch (e: Exception) {
                view.findViewById<TextView>(R.id.tv_net_status).text = "● Offline"
                view.findViewById<TextView>(R.id.tv_net_status).setTextColor(0xFFEF4444.toInt())
            }
        }
    }
}
