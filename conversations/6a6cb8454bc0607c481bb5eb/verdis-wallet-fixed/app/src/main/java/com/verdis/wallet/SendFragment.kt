package com.verdis.wallet

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.EditText
import android.widget.Spinner
import android.widget.TextView
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class SendFragment : Fragment() {

    private lateinit var spinnerAsset: Spinner
    private lateinit var etAddress: EditText
    private lateinit var etAmount: EditText
    private lateinit var btnSend: Button
    private lateinit var tvAvailable: TextView
    private lateinit var btnMax: Button
    private lateinit var btnPaste: Button

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val view = inflater.inflate(R.layout.fragment_send, container, false)

        spinnerAsset = view.findViewById(R.id.spinner_asset)
        etAddress = view.findViewById(R.id.et_address)
        etAmount = view.findViewById(R.id.et_amount)
        btnSend = view.findViewById(R.id.btn_send)
        tvAvailable = view.findViewById(R.id.tv_available)
        btnMax = view.findViewById(R.id.btn_max)
        btnPaste = view.findViewById(R.id.btn_paste)

        val tokens = arrayOf("VCO", "CARBON", "ECO")
        spinnerAsset.adapter = ArrayAdapter(requireContext(), android.R.layout.simple_spinner_dropdown_item, tokens)

        btnPaste.setOnClickListener {
            val clipboard = requireContext().getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
            val clip = clipboard.primaryClip
            if (clip != null && clip.itemCount > 0) {
                etAddress.setText(clip.getItemAt(0).text.toString())
            }
        }

        btnMax.setOnClickListener {
            val wallet = WalletManager.loadWallet(requireContext()) ?: return@setOnClickListener
            lifecycleScope.launch {
                try {
                    val balanceResp = withContext(Dispatchers.IO) { VerdisApi.getBalance(wallet.address) }
                    val balVco = balanceResp.balance / 1_000_000_000_000_000_000.0
                    val max = balVco - 0.001 // minus fee
                    if (max > 0) etAmount.setText(String.format("%.4f", max))
                } catch (e: Exception) {
                    Toast.makeText(context, "Failed to load balance", Toast.LENGTH_SHORT).show()
                }
            }
        }

        btnSend.setOnClickListener {
            val to = etAddress.text.toString().trim()
            val amountStr = etAmount.text.toString().trim()

            if (to.isEmpty() || !to.startsWith("0x")) {
                Toast.makeText(context, "Enter valid address (0x...)", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            val amount = amountStr.toDoubleOrNull()
            if (amount == null || amount <= 0) {
                Toast.makeText(context, "Enter valid amount", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            val wallet = WalletManager.loadWallet(requireContext())
            if (wallet == null) {
                Toast.makeText(context, "No wallet", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            btnSend.isEnabled = false
            btnSend.text = "Sending..."

            lifecycleScope.launch {
                try {
                    val details = withContext(Dispatchers.IO) { VerdisApi.getWalletDetails(wallet.address) }
                    val nonce = details?.nonce?.toLong() ?: 0L
                    val fee = 0.001
                    val signature = WalletManager.signTransaction(wallet, to, amount, fee, nonce)

                    val result = withContext(Dispatchers.IO) {
                        VerdisApi.sendTransaction(
                            wallet.address, to, amount, fee, nonce, signature, wallet.publicKey
                        )
                    }

                    if (result?.success == true) {
                        Toast.makeText(context, "Sent ${amount} VCO ✓", Toast.LENGTH_LONG).show()
                        etAddress.setText("")
                        etAmount.setText("")
                    } else {
                        Toast.makeText(context, "Failed: ${result?.error ?: "Unknown error"}", Toast.LENGTH_LONG).show()
                    }
                } catch (e: Exception) {
                    Toast.makeText(context, "Error: ${e.message}", Toast.LENGTH_LONG).show()
                } finally {
                    btnSend.isEnabled = true
                    btnSend.text = "Send"
                }
            }
        }

        // Load available balance
        loadBalance()

        return view
    }

    private fun loadBalance() {
        val wallet = WalletManager.loadWallet(requireContext()) ?: return
        lifecycleScope.launch {
            try {
                val balanceResp = withContext(Dispatchers.IO) { VerdisApi.getBalance(wallet.address) }
                val balVco = (balanceResp.balance as Number).toDouble() / 1_000_000_000_000_000_000.0
                tvAvailable.text = "Avail: ${String.format("%.4f", balVco)}"
            } catch (e: Exception) {}
        }
    }
}
