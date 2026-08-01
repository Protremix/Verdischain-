package com.verdis.wallet

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch

class OnboardingFragment : Fragment() {

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        val v = inflater.inflate(R.layout.fragment_onboarding, container, false)
        val btnCreate = v.findViewById<Button>(R.id.btn_create_wallet)
        val btnImport = v.findViewById<Button>(R.id.btn_import_wallet)
        val importLayout = v.findViewById<LinearLayout>(R.id.import_layout)
        val etKey = v.findViewById<EditText>(R.id.et_private_key)
        val btnConfirmImport = v.findViewById<Button>(R.id.btn_confirm_import)
        val btnCancelImport = v.findViewById<Button>(R.id.btn_cancel_import)

        btnCreate.setOnClickListener {
            try {
                val wallet = WalletManager.createWallet(requireContext())
                Toast.makeText(context, "Wallet created! Address: ${wallet.address.take(10)}...", Toast.LENGTH_LONG).show()
                (activity as? MainActivity)?.onWalletCreated()
            } catch (e: Throwable) {
                Toast.makeText(context, "Failed: ${e.message}", Toast.LENGTH_SHORT).show()
            }
        }

        btnImport.setOnClickListener {
            importLayout.visibility = View.VISIBLE
            btnCreate.visibility = View.GONE
            btnImport.visibility = View.GONE
        }

        btnCancelImport.setOnClickListener {
            importLayout.visibility = View.GONE
            btnCreate.visibility = View.VISIBLE
            btnImport.visibility = View.VISIBLE
        }

        btnConfirmImport.setOnClickListener {
            val key = etKey.text.toString().trim()
            if (key.length < 64) {
                Toast.makeText(context, "Invalid key length", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            try {
                val wallet = WalletManager.importWallet(requireContext(), key)
                Toast.makeText(context, "Wallet imported! ${wallet.address.take(10)}...", Toast.LENGTH_LONG).show()
                (activity as? MainActivity)?.onWalletCreated()
            } catch (e: Throwable) {
                Toast.makeText(context, "Import failed: ${e.message}", Toast.LENGTH_SHORT).show()
            }
        }

        return v
    }
}
