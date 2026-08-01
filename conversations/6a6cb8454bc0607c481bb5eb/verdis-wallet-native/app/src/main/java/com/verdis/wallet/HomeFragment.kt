package com.verdis.wallet

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.ProgressBar
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class HomeFragment : Fragment() {

    private lateinit var tvBalance: TextView
    private lateinit var tvAddress: TextView
    private lateinit var tokensContainer: LinearLayout
    private lateinit var progressBar: ProgressBar

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val view = inflater.inflate(R.layout.fragment_home, container, false)

        tvBalance = view.findViewById(R.id.tv_balance)
        tvAddress = view.findViewById(R.id.tv_address)
        tokensContainer = view.findViewById(R.id.tokens_container)
        progressBar = view.findViewById(R.id.progress)

        val wallet = WalletManager.loadWallet(requireContext())
        if (wallet != null) {
            tvAddress.text = wallet.address.take(10) + "..." + wallet.address.takeLast(6)
            tvAddress.setOnClickListener { copyToClipboard(wallet.address) }
            loadData(wallet)
        }

        view.findViewById<ImageView>(R.id.action_send).setOnClickListener {
            (activity as MainActivity).navigateTo(SendFragment())
        }
        view.findViewById<ImageView>(R.id.action_receive).setOnClickListener {
            (activity as MainActivity).navigateTo(ReceiveFragment())
        }
        view.findViewById<ImageView>(R.id.action_swap).setOnClickListener {
            (activity as MainActivity).navigateTo(SwapFragment())
        }
        view.findViewById<ImageView>(R.id.action_history).setOnClickListener {
            (activity as MainActivity).navigateTo(HistoryFragment())
        }

        return view
    }

    private fun loadData(wallet: WalletManager.Wallet) {
        progressBar.visibility = View.VISIBLE
        lifecycleScope.launch {
            try {
                val balance = withContext(Dispatchers.IO) {
                    VerdisApi.getWalletBalance(wallet.address)
                }
                val pools = withContext(Dispatchers.IO) {
                    VerdisApi.getDexPools()
                }

                tvBalance.text = String.format("%,.2f", balance.balance)

                // Build token cards
                val tokens = mutableListOf<Pair<String, String>>()
                tokens.add(Pair("VCO", String.format("%,.2f", balance.balance)))
                
                val tokenNames = mutableSetOf<String>()
                pools.forEach { pool ->
                    if (pool.tokenA != "VCO" && pool.tokenA !in tokenNames) {
                        tokenNames.add(pool.tokenA)
                        tokens.add(Pair(pool.tokenA, "0.00"))
                    }
                    if (pool.tokenB != "VCO" && pool.tokenB !in tokenNames) {
                        tokenNames.add(pool.tokenB)
                        tokens.add(Pair(pool.tokenB, "0.00"))
                    }
                }

                tokensContainer.removeAllViews()
                tokens.forEach { (name, bal) ->
                    val tokenView = layoutInflater.inflate(R.layout.item_token, tokensContainer, false)
                    val icon = tokenView.findViewById<TextView>(R.id.token_icon)
                    val nameView = tokenView.findViewById<TextView>(R.id.token_name)
                    val balView = tokenView.findViewById<TextView>(R.id.token_balance)
                    val priceView = tokenView.findViewById<TextView>(R.id.token_price)

                    icon.text = name.take(3)
                    when (name) {
                        "VCO" -> { icon.setBackgroundResource(R.drawable.bg_token_icon_green); nameView.text = "Verdis"; }
                        "CARBON" -> { icon.setBackgroundResource(R.drawable.bg_token_icon_teal); nameView.text = "Carbon Credits"; }
                        "ECO" -> { icon.setBackgroundResource(R.drawable.bg_token_icon_dark_green); nameView.text = "Eco Token"; }
                        else -> { nameView.text = name; }
                    }
                    balView.text = bal
                    priceView.text = if (name == "VCO") "$0.001" else "—"

                    tokensContainer.addView(tokenView)
                }
            } catch (e: Exception) {
                tvBalance.text = "0.00"
            } finally {
                progressBar.visibility = View.GONE
            }
        }
    }

    private fun copyToClipboard(text: String) {
        val clipboard = requireContext().getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
        clipboard.setPrimaryClip(ClipData.newPlainText("Verdis", text))
        Toast.makeText(requireContext(), "Address copied ✓", Toast.LENGTH_SHORT).show()
    }
}
