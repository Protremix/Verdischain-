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
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import okhttp3.MediaType.Companion.toMediaType
import com.google.gson.Gson
import com.google.gson.JsonParser
import java.util.concurrent.TimeUnit

class IdoFragment : Fragment() {

    private lateinit var tvPrice: TextView
    private lateinit var tvSold: TextView
    private lateinit var tvRemaining: TextView
    private lateinit var tvPurchasers: TextView
    private lateinit var progressSale: ProgressBar
    private lateinit var etAmount: EditText
    private lateinit var btnBuy: View
    private lateinit var tvStatus: TextView
    private lateinit var tvCost: TextView
    private lateinit var tvYourBalance: TextView

    private val client = OkHttpClient.Builder()
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .build()
    private val gson = Gson()
    private val baseUrl = "https://verdischain.com"

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

        loadIdoInfo(wallet.address)

        etAmount.addTextChangedListener(object : android.text.TextWatcher {
            override fun afterTextChanged(s: android.text.Editable?) {
                val amount = s?.toString()?.toDoubleOrNull() ?: 0.0
                val cost = amount * 0.001
                tvCost.text = "Cost: \$$cost"
            }
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}
        })

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

    private fun loadIdoInfo(walletAddress: String) {
        lifecycleScope.launch {
            try {
                val info = withContext(Dispatchers.IO) {
                    val req = Request.Builder().url("$baseUrl/api/ido/info").get().build()
                    client.newCall(req).execute().use { it.body?.string() ?: "" }
                }
                val json = JsonParser.parseString(info).asJsonObject
                tvPrice.text = "$${json.get("priceUSD")?.asDouble ?: 0.001} per VCO"
                val sold = json.get("sold")?.asLong ?: 0L
                val remaining = json.get("remaining")?.asLong ?: 0L
                tvSold.text = String.format("%,d", sold) + " VCO sold"
                tvRemaining.text = String.format("%,d", remaining) + " VCO remaining"
                tvPurchasers.text = "${json.get("purchasers")?.asInt ?: 0} purchasers"
                progressSale.progress = json.get("progressPct")?.asDouble?.toInt() ?: 0

                // Load wallet balance
                val balanceResp = withContext(Dispatchers.IO) {
                    val req = Request.Builder().url("$baseUrl/api/wallet/$walletAddress/balance").get().build()
                    client.newCall(req).execute().use { it.body?.string() ?: "" }
                }
                val balJson = JsonParser.parseString(balanceResp).asJsonObject
                val balance = balJson.get("balance")?.asDouble ?: 0.0
                tvYourBalance.text = "Your balance: ${String.format("%.2f", balance)} VCO"
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
        tvStatus.setTextColor(0xFF34D399.toInt())

        lifecycleScope.launch {
            try {
                val result = withContext(Dispatchers.IO) {
                    val body = gson.toJson(mapOf(
                        "address" to address,
                        "amountVCO" to amountVCO.toString()
                    ))
                    val req = Request.Builder()
                        .url("$baseUrl/api/ido/purchase")
                        .post(body.toRequestBody("application/json".toMediaType()))
                        .build()
                    client.newCall(req).execute().use { it.body?.string() ?: "" }
                }
                val json = JsonParser.parseString(result).asJsonObject
                if (json.get("success")?.asBoolean == true) {
                    val amount = json.get("amountVCO")?.asDouble ?: 0.0
                    val cost = json.get("totalCostUSD")?.asString ?: "0"
                    val newBalance = json.get("newBalance")?.asDouble ?: 0.0
                    tvStatus.text = "Purchased $amount VCO for \$$cost\nNew balance: ${String.format("%.2f", newBalance)} VCO"
                    tvStatus.setTextColor(0xFF34D399.toInt())
                    etAmount.text.clear()
                    loadIdoInfo(address)
                    (activity as? MainActivity)?.refreshHome()
                } else {
                    tvStatus.text = "Failed: ${json.get("error")?.asString ?: "Unknown error"}"
                    tvStatus.setTextColor(0xFFEF4444.toInt())
                }
            } catch (e: Exception) {
                tvStatus.text = "Error: ${e.message}"
                tvStatus.setTextColor(0xFFEF4444.toInt())
            } finally {
                btnBuy.isEnabled = true
            }
        }
    }
}
