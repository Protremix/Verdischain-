package com.verdis.wallet

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.LinearLayout
import android.widget.Switch
import android.widget.TextView
import android.widget.Toast
import androidx.biometric.BiometricManager
import androidx.biometric.BiometricPrompt
import androidx.fragment.app.Fragment
import androidx.fragment.app.FragmentActivity
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch

class SettingsFragment : Fragment() {
    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        val v = inflater.inflate(R.layout.fragment_settings, container, false)

        val tvAddress = v.findViewById<TextView>(R.id.tv_settings_address)
        val tvPrivateKey = v.findViewById<TextView>(R.id.tv_settings_privkey)
        val btnShowKey = v.findViewById<Button>(R.id.btn_show_privkey)
        val btnCopyAddr = v.findViewById<Button>(R.id.btn_copy_addr)
        val swBiometric = v.findViewById<Switch>(R.id.sw_biometric)
        val btnSetPin = v.findViewById<Button>(R.id.btn_set_pin)
        val btnClearPin = v.findViewById<Button>(R.id.btn_clear_pin)
        val btnExport = v.findViewById<Button>(R.id.btn_export_wallet)
        val btnDelete = v.findViewById<Button>(R.id.btn_delete_wallet)
        val tvVersion = v.findViewById<TextView>(R.id.tv_version)

        val ctx = requireContext()
        val wallet = WalletManager.loadWallet(ctx)

        if (wallet != null) {
            tvAddress.text = wallet.address
            tvPrivateKey.text = "••••••••••••••••••••••••••"
        }

        tvVersion.text = "Verdis Wallet v3.0.0"

        // Biometric toggle
        val canBiometric = BiometricManager.from(ctx)
            .canAuthenticate(BiometricManager.Authenticators.BIOMETRIC_STRONG) == BiometricManager.BIOMETRIC_SUCCESS
        swBiometric.isEnabled = canBiometric
        swBiometric.isChecked = SecurityManager.isBiometric(ctx)

        swBiometric.setOnCheckedChangeListener { _, checked ->
            if (checked && canBiometric) {
                SecurityManager.setBiometric(ctx, true)
                Toast.makeText(ctx, "Biometric enabled", Toast.LENGTH_SHORT).show()
            } else if (!checked) {
                SecurityManager.setBiometric(ctx, false)
                Toast.makeText(ctx, "Biometric disabled", Toast.LENGTH_SHORT).show()
            }
        }

        // PIN controls
        val secState = SecurityManager.getState(ctx)
        btnClearPin.visibility = if (secState.pinEnabled) View.VISIBLE else View.GONE

        btnSetPin.setOnClickListener {
            (activity as? MainActivity)?.let { act ->
                val intent = android.content.Intent(ctx, CreatePinActivity::class.java)
                startActivity(intent)
            }
        }

        btnClearPin.setOnClickListener {
            SecurityManager.clearPin(ctx)
            Toast.makeText(ctx, "PIN removed", Toast.LENGTH_SHORT).show()
            btnClearPin.visibility = View.GONE
        }

        // Show private key
        var keyVisible = false
        btnShowKey.setOnClickListener {
            if (wallet == null) return@setOnClickListener
            keyVisible = !keyVisible
            tvPrivateKey.text = if (keyVisible) wallet.privateKey else "••••••••••••••••••••••••••"
            btnShowKey.text = if (keyVisible) "Hide" else "Show"
        }

        // Copy address
        btnCopyAddr.setOnClickListener {
            if (wallet == null) return@setOnClickListener
            val clipboard = ctx.getSystemService(android.content.Context.CLIPBOARD_SERVICE) as android.content.ClipboardManager
            clipboard.setPrimaryClip(android.content.ClipData.newPlainText("address", wallet.address))
            Toast.makeText(ctx, "Address copied!", Toast.LENGTH_SHORT).show()
        }

        // Export wallet
        btnExport.setOnClickListener {
            if (wallet == null) return@setOnClickListener
            val text = "Verdis Wallet Export\nAddress: ${wallet.address}\nPrivate Key: ${wallet.privateKey}\nSeed: ${wallet.seedPhrase ?: "N/A"}"
            val shareIntent = android.content.Intent(android.content.Intent.ACTION_SEND).apply {
                type = "text/plain"
                putExtra(android.content.Intent.EXTRA_TEXT, text)
            }
            startActivity(android.content.Intent.createChooser(shareIntent, "Export Wallet"))
        }

        // Delete wallet
        btnDelete.setOnClickListener {
            WalletManager.clearWallet(ctx)
            SecurityManager.clearPin(ctx)
            SecurityManager.setBiometric(ctx, false)
            Toast.makeText(ctx, "Wallet deleted", Toast.LENGTH_LONG).show()
            (activity as? MainActivity)?.showOnboarding()
        }

        return v
    }
}
