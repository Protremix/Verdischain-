package com.verdis.wallet

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.text.InputType
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.fragment.app.Fragment

class SettingsFragment : Fragment() {
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val view = inflater.inflate(R.layout.fragment_settings, container, false)

        val wallet = WalletManager.loadWallet(requireContext())
        val etRpc = view.findViewById<EditText>(R.id.et_rpc)
        val etChainId = view.findViewById<EditText>(R.id.et_chain_id)
        val etExplorer = view.findViewById<EditText>(R.id.et_explorer)
        val etPrivateKey = view.findViewById<EditText>(R.id.et_private_key)
        val btnShowKey = view.findViewById<Button>(R.id.btn_show_key)
        val btnDisconnect = view.findViewById<Button>(R.id.btn_disconnect)
        val tvVersion = view.findViewById<TextView>(R.id.tv_version)

        etRpc.setText("https://rpc.verdischain.com")
        etChainId.setText("909")
        etExplorer.setText("https://verdischain.com/explorer")

        if (wallet != null) {
            etPrivateKey.setText(wallet.privateKey)
        }
        etPrivateKey.inputType = InputType.TYPE_TEXT_VARIATION_PASSWORD

        btnShowKey.setOnClickListener {
            if (etPrivateKey.inputType == InputType.TYPE_TEXT_VARIATION_PASSWORD) {
                etPrivateKey.inputType = InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_VARIATION_VISIBLE_PASSWORD
                btnShowKey.text = "Hide Key"
            } else {
                etPrivateKey.inputType = InputType.TYPE_TEXT_VARIATION_PASSWORD
                btnShowKey.text = "Show Key"
            }
        }

        btnDisconnect.setOnClickListener {
            AlertDialog.Builder(requireContext(), R.style.DialogTheme)
                .setTitle("Disconnect Wallet")
                .setMessage("This will remove your private key from this device. Make sure you have a backup!")
                .setPositiveButton("Disconnect") { _, _ ->
                    WalletManager.clearWallet(requireContext())
                    (activity as MainActivity).showOnboarding()
                    Toast.makeText(requireContext(), "Wallet disconnected", Toast.LENGTH_SHORT).show()
                }
                .setNegativeButton("Cancel", null)
                .show()
        }

        tvVersion.text = "Verdis Wallet v1.0.0 · Native\n© 2026 Verdis Blockchain\nThe First Fully Green Blockchain Ecosystem"

        return view
    }
}
