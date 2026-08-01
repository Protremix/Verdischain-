package com.verdis.wallet

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class SendFragment : Fragment() {
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val view = inflater.inflate(R.layout.fragment_send, container, false)

        val etTo = view.findViewById<EditText>(R.id.et_to)
        val etAmount = view.findViewById<EditText>(R.id.et_amount)
        val btnSend = view.findViewById<Button>(R.id.btn_send)

        btnSend.setOnClickListener {
            val to = etTo.text.toString().trim()
            val amount = etAmount.text.toString().toDoubleOrNull()

            if (to.isEmpty() || !to.startsWith("0x") || to.length < 40) {
                Toast.makeText(requireContext(), "Enter valid recipient address", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            if (amount == null || amount <= 0) {
                Toast.makeText(requireContext(), "Enter valid amount", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            val wallet = WalletManager.loadWallet(requireContext())
            if (wallet == null) {
                Toast.makeText(requireContext(), "No wallet loaded", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            btnSend.isEnabled = false
            btnSend.text = "Sending..."

            lifecycleScope.launch {
                try {
                    val result = withContext(Dispatchers.IO) {
                        VerdisApi.send(wallet, to, amount)
                    }
                    if (result.success) {
                        Toast.makeText(requireContext(), "Sent ${amount} VCO ✓", Toast.LENGTH_LONG).show()
                        etTo.setText("")
                        etAmount.setText("")
                        requireActivity().onBackPressed()
                    } else {
                        Toast.makeText(requireContext(), "Failed: ${result.error}", Toast.LENGTH_LONG).show()
                    }
                } catch (e: Exception) {
                    Toast.makeText(requireContext(), "Error: ${e.message}", Toast.LENGTH_LONG).show()
                } finally {
                    btnSend.isEnabled = true
                    btnSend.text = "Send Transaction"
                }
            }
        }

        return view
    }
}
