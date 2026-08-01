package com.verdis.wallet

import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ArrayAdapter
import android.widget.AdapterView
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

class SwapFragment : Fragment() {

    private lateinit var etFromAmount: EditText
    private lateinit var tvToAmount: TextView
    private lateinit var spinnerFrom: Spinner
    private lateinit var spinnerTo: Spinner
    private lateinit var tvRate: TextView
    private lateinit var btnSwap: Button

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val view = inflater.inflate(R.layout.fragment_swap, container, false)

        etFromAmount = view.findViewById(R.id.et_from_amount)
        tvToAmount = view.findViewById(R.id.tv_to_amount)
        spinnerFrom = view.findViewById(R.id.spinner_from)
        spinnerTo = view.findViewById(R.id.spinner_to)
        tvRate = view.findViewById(R.id.tv_rate)
        btnSwap = view.findViewById(R.id.btn_swap)

        val tokens = listOf("VCO", "CARBON", "ECO")
        val adapter = ArrayAdapter(requireContext(), android.R.layout.simple_spinner_dropdown_item, tokens)
        spinnerFrom.adapter = adapter
        spinnerTo.adapter = ArrayAdapter(requireContext(), android.R.layout.simple_spinner_dropdown_item, tokens)
        spinnerTo.setSelection(1)

        val watcher = object : TextWatcher {
            override fun afterTextChanged(s: Editable?) { updateQuote() }
            override fun beforeTextChanged(s: CharSequence?, p1: Int, p2: Int, p3: Int) {}
            override fun onTextChanged(s: CharSequence?, p1: Int, p2: Int, p3: Int) {}
        }
        etFromAmount.addTextChangedListener(watcher)

        val spinListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(parent: AdapterView<*>?, view: View?, position: Int, id: Long) { updateQuote() }
            override fun onNothingSelected(parent: AdapterView<*>?) {}
        }
        spinnerFrom.onItemSelectedListener = spinListener
        spinnerTo.onItemSelectedListener = spinListener

        btnSwap.setOnClickListener {
            val fromToken = spinnerFrom.selectedItem as String
            val toToken = spinnerTo.selectedItem as String
            val amount = etFromAmount.text.toString().toDoubleOrNull()

            if (fromToken == toToken) {
                Toast.makeText(requireContext(), "Select different tokens", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            if (amount == null || amount <= 0) {
                Toast.makeText(requireContext(), "Enter amount", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            val wallet = WalletManager.loadWallet(requireContext())
            if (wallet == null) {
                Toast.makeText(requireContext(), "No wallet", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            btnSwap.isEnabled = false
            btnSwap.text = "Swapping..."

            lifecycleScope.launch {
                try {
                    val result = withContext(Dispatchers.IO) {
                        VerdisApi.swap(wallet, fromToken, toToken, amount)
                    }
                    if (result.success) {
                        Toast.makeText(requireContext(), "Swapped ${amount} ${fromToken} → ${result.amountOut} ${toToken} ✓", Toast.LENGTH_LONG).show()
                        etFromAmount.setText("")
                        tvToAmount.text = "0.0"
                    } else {
                        Toast.makeText(requireContext(), "Swap failed: ${result.error}", Toast.LENGTH_LONG).show()
                    }
                } catch (e: Exception) {
                    Toast.makeText(requireContext(), "Error: ${e.message}", Toast.LENGTH_LONG).show()
                } finally {
                    btnSwap.isEnabled = true
                    btnSwap.text = "Swap"
                }
            }
        }

        return view
    }

    private fun updateQuote() {
        val fromToken = spinnerFrom.selectedItem as? String ?: return
        val toToken = spinnerTo.selectedItem as? String ?: return
        val amount = etFromAmount.text.toString().toDoubleOrNull() ?: return

        if (fromToken == toToken || amount <= 0) {
            tvToAmount.text = "0.0"
            tvRate.text = "Select different tokens"
            return
        }

        lifecycleScope.launch {
            try {
                val outAmount = withContext(Dispatchers.IO) {
                    VerdisApi.getQuote(fromToken, toToken, amount)
                }
                tvToAmount.text = String.format("%.6f", outAmount)
                val rate = if (amount > 0) outAmount / amount else 0.0
                tvRate.text = "1 $fromToken = ${String.format("%.4f", rate)} $toToken · Fee: 0.3%"
            } catch (e: Exception) {
                tvRate.text = "No liquidity pool"
            }
        }
    }
}
