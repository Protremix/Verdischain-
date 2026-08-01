package com.verdis.wallet

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class SettingsFragment : Fragment() {

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

        view.findViewById<TextView>(R.id.tv_address).text = wallet.address

        view.findViewById<Button>(R.id.btn_copy_address).setOnClickListener {
            val clipboard = requireContext().getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
            clipboard.setPrimaryClip(ClipData.newPlainText("address", wallet.address))
            Toast.makeText(context, "Address copied!", Toast.LENGTH_SHORT).show()
        }

        view.findViewById<Button>(R.id.btn_backup).setOnClickListener {
            if (wallet.seedPhrase != null) {
                AlertDialog.Builder(requireContext())
                    .setTitle("Seed Phrase")
                    .setMessage(wallet.seedPhrase)
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

        view.findViewById<Button>(R.id.btn_export_key).setOnClickListener {
            AlertDialog.Builder(requireContext())
                .setTitle("Private Key")
                .setMessage("WARNING: Anyone with this key has full access to your wallet!\n\n${wallet.privateKey}")
                .setPositiveButton("Copy") { _, _ ->
                    val clipboard = requireContext().getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                    clipboard.setPrimaryClip(ClipData.newPlainText("key", wallet.privateKey))
                    Toast.makeText(context, "Key copied (keep secret!)", Toast.LENGTH_SHORT).show()
                }
                .setNegativeButton("Close", null)
                .show()
        }

        view.findViewById<Button>(R.id.btn_delete_wallet).setOnClickListener {
            AlertDialog.Builder(requireContext())
                .setTitle("Delete Wallet")
                .setMessage("Are you sure? Make sure you have backed up your seed phrase or private key.")
                .setPositiveButton("Delete") { _, _ ->
                    WalletManager.clearWallet(requireContext())
                    (activity as? MainActivity)?.showOnboarding()
                    Toast.makeText(context, "Wallet deleted", Toast.LENGTH_SHORT).show()
                }
                .setNegativeButton("Cancel", null)
                .show()
        }

        // Load network status
        loadNetworkInfo(view)
        return view
    }

    private fun loadNetworkInfo(view: View) {
        lifecycleScope.launch {
            try {
                val info = withContext(Dispatchers.IO) { VerdisApi.getBlockchainInfo() }
                view.findViewById<TextView>(R.id.tv_block_height).text = info?.height?.toString() ?: "---"
                view.findViewById<TextView>(R.id.tv_net_status).text =
                    if (info != null) "● Connected" else "● Offline"
                view.findViewById<TextView>(R.id.tv_net_status).setTextColor(
                    if (info != null) 0xFF00FF88.toInt() else 0xFFFF5F5F.toInt()
                )
            } catch (e: Exception) {
                view.findViewById<TextView>(R.id.tv_net_status).text = "● Offline"
                view.findViewById<TextView>(R.id.tv_net_status).setTextColor(0xFFFF5F5F.toInt())
            }
        }
    }
}
