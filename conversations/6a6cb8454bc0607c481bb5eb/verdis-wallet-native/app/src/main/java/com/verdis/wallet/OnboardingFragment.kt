package com.verdis.wallet

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.os.Bundle
import android.text.InputType
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.fragment.app.Fragment

class OnboardingFragment : Fragment() {

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val view = inflater.inflate(R.layout.fragment_onboarding, container, false)

        view.findViewById<Button>(R.id.btn_create).setOnClickListener {
            val wallet = WalletManager.createWallet(requireContext())
            showSeedDialog(wallet.seedPhrase ?: "")
            (activity as MainActivity).showMainUI(wallet)
        }

        view.findViewById<Button>(R.id.btn_import).setOnClickListener {
            showImportDialog()
        }

        return view
    }

    private fun showSeedDialog(seed: String) {
        val words = seed.split(" ")
        val message = StringBuilder()
        words.forEachIndexed { i, word ->
            message.append("${i + 1}. $word   ")
            if ((i + 1) % 3 == 0) message.append("\n")
        }

        AlertDialog.Builder(requireContext(), R.style.DialogTheme)
            .setTitle("🔐 Your Seed Phrase")
            .setMessage("$message\n\n⚠️ Write these 12 words down and keep them safe. Never share them with anyone!")
            .setPositiveButton("I've Saved It") { _, _ ->
                Toast.makeText(requireContext(), "Wallet created! 🎉", Toast.LENGTH_SHORT).show()
            }
            .setCancelable(false)
            .show()
    }

    private fun showImportDialog() {
        val input = EditText(requireContext()).apply {
            hint = "Private key (0x...) or 12-word seed phrase"
            inputType = InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_VARIATION_PASSWORD
            setPadding(40, 30, 40, 30)
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            )
        }

        AlertDialog.Builder(requireContext(), R.style.DialogTheme)
            .setTitle("Import Wallet")
            .setView(input)
            .setPositiveButton("Import") { _, _ ->
                val key = input.text.toString().trim()
                if (key.isEmpty()) {
                    Toast.makeText(requireContext(), "Enter a key or seed phrase", Toast.LENGTH_SHORT).show()
                    return@setPositiveButton
                }
                try {
                    val wallet = WalletManager.importWallet(requireContext(), key)
                    Toast.makeText(requireContext(), "Wallet imported! ✓", Toast.LENGTH_SHORT).show()
                    (activity as MainActivity).showMainUI(wallet)
                } catch (e: Exception) {
                    Toast.makeText(requireContext(), "Import failed: ${e.message}", Toast.LENGTH_LONG).show()
                }
            }
            .setNegativeButton("Cancel", null)
            .show()
    }
}
