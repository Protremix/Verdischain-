package com.verdis.wallet

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.fragment.app.Fragment
import com.google.android.material.button.MaterialButton
import com.google.android.material.textfield.TextInputEditText

class OnboardingFragment : Fragment() {

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val view = inflater.inflate(R.layout.fragment_onboarding, container, false)

        view.findViewById<MaterialButton>(R.id.btn_create).setOnClickListener {
            // Show seed phrase warning, then create
            val wallet = WalletManager.createWallet(requireContext())
            showSeedPhraseDialog(wallet.seedPhrase)
        }

        view.findViewById<MaterialButton>(R.id.btn_import).setOnClickListener {
            showImportDialog()
        }

        return view
    }

    private fun showSeedPhraseDialog(seed: String?) {
        val message = if (seed != null) {
            "Your 12-word seed phrase:\n\n$seed\n\nWrite this down and keep it safe. You will need it to recover your wallet."
        } else {
            "Wallet created. Remember to backup your private key from Settings."
        }

        AlertDialog.Builder(requireContext())
            .setTitle("Wallet Created ✓")
            .setMessage(message)
            .setPositiveButton("I've saved it") { _, _ ->
                (activity as? MainActivity)?.onWalletCreated()
            }
            .setCancelable(false)
            .show()
    }

    private fun showImportDialog() {
        val input = TextInputEditText(requireContext())
        input.hint = "Enter private key (0x...) or seed phrase"
        input.setPadding(48, 32, 48, 32)

        AlertDialog.Builder(requireContext())
            .setTitle("Import Wallet")
            .setView(input)
            .setPositiveButton("Import") { _, _ ->
                val key = input.text?.toString()?.trim() ?: ""
                if (key.isEmpty()) {
                    Toast.makeText(context, "Enter a key or seed phrase", Toast.LENGTH_SHORT).show()
                    return@setPositiveButton
                }
                try {
                    WalletManager.importWallet(requireContext(), key)
                    Toast.makeText(context, "Wallet imported ✓", Toast.LENGTH_SHORT).show()
                    (activity as? MainActivity)?.onWalletCreated()
                } catch (e: Exception) {
                    Toast.makeText(context, "Import failed: ${e.message}", Toast.LENGTH_LONG).show()
                }
            }
            .setNegativeButton("Cancel", null)
            .show()
    }
}
