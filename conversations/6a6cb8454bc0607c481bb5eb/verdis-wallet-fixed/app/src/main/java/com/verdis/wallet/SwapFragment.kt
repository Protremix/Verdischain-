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

    private var spinnerFrom: Spinner? = null
    private var spinnerTo: Spinner? = null
    private var etFromAmount: EditText? = null
    private var tvToAmount: TextView? = null
    private var tvRate: TextView? = null
    private var tvPriceImpact: TextView? = null
    private var tvFromBalance: TextView? = null
    private var tvToBalance: TextView? = null
    private var btnSwap: Button? = null
    private var btnSwitch: Button? = null

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val view = inflater.inflate(R.layout.fragment_swap, container, false)

        spinnerFrom = view.findViewById(R.id.spinner_from)
        spinnerTo = view.findViewById(R.id.spinner_to)
        etFromAmount = view.findViewById(R.id.et_from_amount)
        tvToAmount = view.findViewById(R.id.tv_to_amount)
        tvRate = view.findViewById(R.id.tv_rate)
        tvPriceImpact = view.findViewById(R.id.tv_price_impact)
        tvFromBalance = view.findViewById(R.id.tv_from_balance)
        tvToBalance = view.findViewById(R.id.tv_to_balance)
        btnSwap = view.findViewById(R.id.btn_swap)
        btnSwitch = view.findViewById(R.id.btn_switch)

        val tokens = listOf("VCO", "CARBON", "ECO")
        val adapter = ArrayAdapter(requireContext(), android.R.layout.simple_spinner_dropdown_item, tokens)
        spinnerFrom?.adapter = adapter
        spinnerTo?.adapter = ArrayAdapter(requireContext(), android.R.layout.simple_spinner_dropdown_item, tokens)
        spinnerTo?.setSelection(1)

        etFromAmount?.addTextChangedListener(object : TextWatcher {
            override fun afterTextChanged(s: Editable?) { updateQuote() }
            override fun beforeTextChanged(s: CharSequence?, p1: Int, p2: Int, p3: Int) {}
            override fun onTextChanged(s: CharSequence?, p1: Int, p2: Int, p3: Int) {}
        })

        val spinListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(parent: AdapterView<*>?, view: View?, position: Int, id: Long) { updateQuote() }
            override fun onNothingSelected(parent: AdapterView<*>?) {}
        }
        spinnerFrom?.onItemSelectedListener = spinListener
        spinnerTo?.onItemSelectedListener = spinListener

        btnSwitch?.setOnClickListener {
            val from = spinnerFrom?.selectedItemPosition
            spinnerFrom?.setSelection(spinnerTo?.selectedItemPosition)
            spinnerTo?.setSelection(from)
        }

        btnSwap?.setOnClickListener {
            val fromToken = spinnerFrom?.selectedItem as String
            val toToken = spinnerTo?.selectedItem as String
            val amount = etFromAmount?.text.toString().toDoubleOrNull()

            if (fromToken == toToken) {
                Toast.makeText(context, "Select different tokens", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            if (amount == null || amount <= 0) {
                Toast.makeText(context, "Enter amount", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            val wallet = WalletManager.loadWallet(requireContext())
            if (wallet == null) {
                Toast.makeText(context, "No wallet", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            btnSwap?.isEnabled = false
            btnSwap?.text = "Swapping..."

            lifecycleScope.launch {
                try {
                    val details = withContext(Dispatchers.IO) { VerdisApi.getWalletDetails(wallet.address) }
                    val nonce = details?.nonce?.toLong() ?: 0L
                    val signature = WalletManager.signTransaction(wallet, "", amount, 0.0, nonce)

                    val result = withContext(Dispatchers.IO) {
                        VerdisApi.executeSwap(wallet.address, fromToken, toToken, amount, signature, wallet.publicKey)
                    }

                    if (result?.success == true) {
                        Toast.makeText(context, "Swapped ${amount} ${fromToken} → ${result.amountOut} ${toToken} ✓", Toast.LENGTH_LONG).show()
                        etFromAmount?.setText("")
                        tvToAmount?.text = "0.0"
                    } else {
                        Toast.makeText(context, "Swap failed: ${result?.error ?: "Unknown"}", Toast.LENGTH_LONG).show()
                    }
                } catch (e: Exception) {
                    Toast.makeText(context, "Error: ${e.message}", Toast.LENGTH_LONG).show()
                } finally {
                    btnSwap?.isEnabled = true
                    btnSwap?.text = "Swap"
                }
            }
        }

        loadBalances()
        return view
    }

    private fun updateQuote() {
        val fromToken = spinnerFrom?.selectedItem as? String ?: return
        val toToken = spinnerTo?.selectedItem as? String ?: return
        val amount = etFromAmount?.text.toString().toDoubleOrNull() ?: return

        if (fromToken == toToken || amount <= 0) {
            tvToAmount?.text = "0.0"
            tvRate?.text = "Select different tokens"
            return
        }

        lifecycleScope.launch {
            try {
                val quote = withContext(Dispatchers.IO) { VerdisApi.getSwapQuote(fromToken, toToken, amount) }
                if (quote != null) {
                    tvToAmount?.text = String.format("%.6f", quote.amountOut)
                    val rate = if (amount > 0) quote.amountOut / amount else 0.0
                    tvRate?.text = "1 $fromToken = ${String.format("%.4f", rate)} $toToken"
                    tvPriceImpact?.text = "${String.format("%.2f", quote.priceImpact)}%"
                } else {
                    tvRate?.text = "No liquidity pool"
                    tvToAmount?.text = "0.0"
                }
            } catch (e: Exception) {
                tvRate?.text = "No liquidity pool"
            }
        }
    }

    private fun loadBalances() {
        val wallet = WalletManager.loadWallet(requireContext()) ?: return
        lifecycleScope.launch {
            try {
                val balancesResp = withContext(Dispatchers.IO) { VerdisApi.getTokenBalances(wallet.address) }
                val fromToken = spinnerFrom?.selectedItem as? String ?: "VCO"
                val toToken = spinnerTo?.selectedItem as? String ?: "CARBON"
                val balances = balancesResp.balances
                tvFromBalance?.text = "Balance: ${balances[fromToken] ?: 0.0}"
                tvToBalance?.text = "Balance: ${balances[toToken] ?: 0.0}"
            } catch (e: Exception) {}
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        spinnerFrom = null; spinnerTo = null; etFromAmount = null
        tvToAmount = null; tvRate = null; tvPriceImpact = null
        tvFromBalance = null; tvToBalance = null; btnSwap = null; btnSwitch = null
    }
}
