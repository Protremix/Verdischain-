package com.verdis.wallet

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.ProgressBar
import android.widget.TextView
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import com.google.gson.Gson
import com.google.gson.JsonObject

class IdoFragment : Fragment() {

    private lateinit var tvPrice: TextView
    private lateinit var tvSold: TextView
    private lateinit var tvRemaining: TextView
    private lateinit var tvPurchasers: TextView
    private lateinit var progressSale: ProgressBar
    private lateinit var etAmount: EditText
    private lateinit var btnBuy: LinearLayout
    private lateinit var tvStatus: TextView
    private lateinit var tvCost: TextView
    private lateinit var tvYourBalance: TextView

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val view = inflater.inflate(R.layout.fragment_ido, container, false)

        tvPrice = view.findViewById(R.id.tv_ido_price)
        tvSold = view.findViewById(R.id.tv_ido_sold)
        tvRemaining = view.findViewById(R.id.tv_ido_remaining)
        tvPurchasers = view.findViewById(R.id.tv_ido_purchasers)
        progressSale = view.findViewById(R.id.progress_sale)
        etAmount = view.findViewById(R.id.et_ido_amount)
        btnBuy = view.findViewById(R.id.btn_ido_buy)
        tvStatus = view.findViewById(R.id.tv_ido_status)
        tvCost = view.findViewById(R.id.tv_ido_cost)
        tvYourBalance = view.findViewById(R.id.tv_ido_balance)

        val wallet = WalletManager.loadWallet(requireContext())
        if (wallet == null) {
            (activity as? MainActivity)?.showOnboarding()
            return view
        }

        // Load IDO info
        loadIdoInfo()

        // Update cost preview on amount change
        etAmount.addTextChangedListener(object : android.text.TextWatcher {
            override fun afterTextChanged(s: android.text.Editable?) {
                val amount = s?.toString()?.toDoubleOrNull() ?: 0.0
                val cost = amount * 0.001
                tvCost.text = "Cost: $$cost"
            }
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}
        })

        // Buy button
        btnBuy.setOnClickListener {
            val amount = etAmount.text.toString().toDoubleOrNull()
            if (amount == null || amount < 100) {
                Toast.makeText(context, "Minimum purchase is 100 VCO", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            purchaseTokens(wallet.address, amount)
        }

        return view
    }

    private fun loadIdoInfo() {
        lifecycleScope.launch {
            try {
                val info = withContext(Dispatchers.IO) { VerdisApi.getIdoInfo() }
                if (info != null) {
                    tvPrice.text = "$${info.priceUSD} per VCO"
                    tvSold.text = "${info.sold.toLong().toLocaleString()} VCO sold"
                    tvRemaining.text = "${info.remaining.toLong().toLocaleString()} VCO remaining"
                    tvPurchasers.text = "${info.purchasers} purchasers"
                    progressSale.progress = info.progressPct.toInt()

                    // Load wallet balance
                    val wallet = WalletManager.loadWallet(requireContext())
                    if (wallet != null) {
                        val balance = withContext(Dispatchers.IO) { VerdisApi.getBalance(wallet.address) }
                        tvYourBalance.text = "Your balance: ${String.format("%.2f", balance)} VCO"
                    }
                }
            } catch (e: Exception) {
                tvStatus.text = "Failed to load sale info"
                tvStatus.visibility = View.VISIBLE
            }
        }
    }

    private fun purchaseTokens(address: String, amountVCO: Double) {
        btnBuy.isEnabled = false
        tvStatus.text = "Processing purchase..."
        tvStatus.visibility = View.VISIBLE

        lifecycleScope.launch {
            try {
                val result = withContext(Dispatchers.IO) {
                    VerdisApi.purchaseIdoTokens(address, amountVCO)
                }
                if (result != null && result.success) {
                    tvStatus.text = "✓ Purchased ${result.amountVCO} VCO for $${result.totalCostUSD}"
                    tvStatus.setTextColor(0xFF34D399.toInt())
                    etAmount.text.clear()
                    loadIdoInfo() // Refresh

                    // Update home balance
                    (activity as? MainActivity)?.refreshHome()
                } else {
                    tvStatus.text = "✗ ${result?.error ?: "Purchase failed"}"
                    tvStatus.setTextColor(0xFFEF4444.toInt())
                }
            } catch (e: Exception) {
                tvStatus.text = "✗ Error: ${e.message}"
                tvStatus.setTextColor(0xFFEF4444.toInt())
            } finally {
                btnBuy.isEnabled = true
            }
        }
    }
}
