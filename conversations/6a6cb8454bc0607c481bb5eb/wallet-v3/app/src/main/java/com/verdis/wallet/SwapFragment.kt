package com.verdis.wallet

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
import kotlinx.coroutines.launch

class SwapFragment : Fragment() {
    private var tvPoolInfo: TextView? = null

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        val v = inflater.inflate(R.layout.fragment_swap, container, false)
        val spinnerIn = v.findViewById<Spinner>(R.id.spinner_token_in)
        val spinnerOut = v.findViewById<Spinner>(R.id.spinner_token_out)
        val etAmount = v.findViewById<EditText>(R.id.et_swap_amount)
        val btnSwap = v.findViewById<Button>(R.id.btn_swap)
        val tvResult = v.findViewById<TextView>(R.id.tv_swap_result)
        tvPoolInfo = v.findViewById(R.id.tv_pool_info)

        val tokens = arrayOf("VRDX", "CARBON", "ECO")
        spinnerIn.adapter = ArrayAdapter(requireContext(), android.R.layout.simple_spinner_dropdown_item, tokens)
        spinnerOut.adapter = ArrayAdapter(requireContext(), android.R.layout.simple_spinner_dropdown_item, tokens)
        spinnerOut.setSelection(1)

        // Load pool info
        lifecycleScope.launch {
            try {
                val pools = VerdisApi.getDexPools()
                if (pools.isNotEmpty()) {
                    val info = pools.joinToString("\n") { p ->
                        "${p["pair"]}: ${p["reserveA"]} / ${p["reserveB"]}"
                    }
                    tvPoolInfo?.text = info
                } else {
                    tvPoolInfo?.text = "No pools available"
                }
            } catch (e: Exception) {
                tvPoolInfo?.text = "Failed to load pools"
            }
        }

        btnSwap.setOnClickListener {
            val tokenIn = spinnerIn.selectedItem.toString()
            val tokenOut = spinnerOut.selectedItem.toString()
            val amountStr = etAmount.text.toString().trim()
            val amount = amountStr.toDoubleOrNull()

            if (tokenIn == tokenOut) {
                Toast.makeText(context, "Cannot swap same token", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            if (amount == null || amount <= 0) {
                Toast.makeText(context, "Invalid amount", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            btnSwap.isEnabled = false
            tvResult.text = "Swapping $amount $tokenIn → $tokenOut..."

            lifecycleScope.launch {
                val ctx = context ?: return@launch
                val w = WalletManager.loadWallet(ctx)
                if (w == null) {
                    tvResult.text = "No wallet"
                    btnSwap.isEnabled = true
                    return@launch
                }
                // API uses VRS internally for pool IDs
                val apiTokenIn = if (tokenIn == "VRDX") "VRS" else tokenIn
                val apiTokenOut = if (tokenOut == "VRDX") "VRS" else tokenOut
                val success = VerdisApi.swap(w.address, apiTokenIn, apiTokenOut, amount)
                btnSwap.isEnabled = true
                if (success) {
                    tvResult.text = "✅ Swapped $amount $tokenIn → $tokenOut"
                    Toast.makeText(ctx, "Swap successful!", Toast.LENGTH_LONG).show()
                    etAmount.text.clear()
                } else {
                    tvResult.text = "❌ Swap failed"
                    Toast.makeText(ctx, "Swap failed", Toast.LENGTH_SHORT).show()
                }
            }
        }
        return v
    }

    override fun onDestroyView() { super.onDestroyView(); tvPoolInfo = null }
}
