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
import kotlinx.coroutines.launch

class SendFragment : Fragment() {
    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        val v = inflater.inflate(R.layout.fragment_send, container, false)
        val etTo = v.findViewById<EditText>(R.id.et_to_address)
        val etAmount = v.findViewById<EditText>(R.id.et_amount)
        val etFee = v.findViewById<EditText>(R.id.et_fee)
        val btnSend = v.findViewById<Button>(R.id.btn_send_tx)
        val tvStatus = v.findViewById<TextView>(R.id.tv_send_status)
        val btnBack = v.findViewById<Button>(R.id.btn_back)

        etFee.setText("1")
        btnBack.setOnClickListener { (activity as? MainActivity)?.navigateTo(R.id.nav_home) }

        btnSend.setOnClickListener {
            val to = etTo.text.toString().trim()
            val amountStr = etAmount.text.toString().trim()
            val feeStr = etFee.text.toString().trim()

            if (to.isEmpty() || !to.startsWith("0x") || to.length < 40) {
                Toast.makeText(context, "Invalid recipient address", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            val amount = amountStr.toDoubleOrNull()
            if (amount == null || amount <= 0) {
                Toast.makeText(context, "Invalid amount", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            val fee = feeStr.toDoubleOrNull() ?: 1.0

            btnSend.isEnabled = false
            tvStatus.visibility = View.VISIBLE
            tvStatus.text = "Sending $amount VRDX..."

            lifecycleScope.launch {
                val ctx = context ?: return@launch
                val w = WalletManager.loadWallet(ctx)
                if (w == null) {
                    tvStatus.text = "No wallet loaded"
                    btnSend.isEnabled = true
                    return@launch
                }
                val success = VerdisApi.sendTransaction(w.address, to, amount, fee, w.privateKey, w.publicKey)
                btnSend.isEnabled = true
                if (success) {
                    tvStatus.text = "✅ Sent $amount VRDX to ${to.take(10)}..."
                    Toast.makeText(ctx, "Transaction sent!", Toast.LENGTH_LONG).show()
                    etTo.text.clear()
                    etAmount.text.clear()
                } else {
                    tvStatus.text = "❌ Transaction failed"
                    Toast.makeText(ctx, "Failed to send", Toast.LENGTH_SHORT).show()
                }
            }
        }
        return v
    }
}
