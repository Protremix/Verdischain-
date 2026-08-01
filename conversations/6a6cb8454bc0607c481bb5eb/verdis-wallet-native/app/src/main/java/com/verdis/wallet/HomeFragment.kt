package com.verdis.wallet

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class HomeFragment : Fragment() {

    private lateinit var tvAddress: TextView
    private lateinit var tvBalance: TextView
    private lateinit var tvBalanceUsd: TextView
    private lateinit var tvChange24h: TextView
    private lateinit var tvBlockHeight: TextView
    private lateinit var tvValidators: TextView
    private lateinit var rvTokens: RecyclerView
    private lateinit var rvTransactions: RecyclerView
    private lateinit var swipeRefresh: SwipeRefreshLayout

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val view = inflater.inflate(R.layout.fragment_home, container, false)

        tvAddress = view.findViewById(R.id.tv_address)
        tvBalance = view.findViewById(R.id.tv_total_balance)
        tvBalanceUsd = view.findViewById(R.id.tv_balance_usd)
        tvChange24h = view.findViewById(R.id.tv_change_24h)
        tvBlockHeight = view.findViewById(R.id.tv_block_height)
        tvValidators = view.findViewById(R.id.tv_validators)
        rvTokens = view.findViewById(R.id.rv_tokens)
        rvTransactions = view.findViewById(R.id.rv_transactions)
        swipeRefresh = view.findViewById(R.id.swipe_refresh)

        rvTokens.layoutManager = LinearLayoutManager(context)
        rvTokens.isNestedScrollingEnabled = false
        rvTransactions.layoutManager = LinearLayoutManager(context)
        rvTransactions.isNestedScrollingEnabled = false

        // Quick action buttons
        view.findViewById<View>(R.id.btn_send).setOnClickListener {
            (activity as? MainActivity)?.navigateTo(R.id.nav_swap)
        }
        view.findViewById<View>(R.id.btn_receive).setOnClickListener {
            (activity as? MainActivity)?.showReceive()
        }
        view.findViewById<View>(R.id.btn_swap).setOnClickListener {
            (activity as? MainActivity)?.navigateTo(R.id.nav_swap)
        }
        view.findViewById<View>(R.id.btn_stake).setOnClickListener {
            (activity as? MainActivity)?.navigateTo(R.id.nav_stake)
        }

        view.findViewById<View>(R.id.btn_qr).setOnClickListener {
            (activity as? MainActivity)?.showReceive()
        }

        swipeRefresh.setOnRefreshListener { loadData() }

        loadData()
        return view
    }

    private fun loadData() {
        lifecycleScope.launch {
            val wallet = WalletManager.loadWallet(requireContext())
            if (wallet == null) {
                (activity as? MainActivity)?.showOnboarding()
                return@launch
            }

            tvAddress.text = wallet.address

            try {
                // Load balance
                val balanceResp = withContext(Dispatchers.IO) { VerdisApi.getBalance(wallet.address) }
                val balance = balanceResp.balance
                val market = withContext(Dispatchers.IO) { VerdisApi.getMarketData() }
                val chainInfo = withContext(Dispatchers.IO) { VerdisApi.getBlockchainInfo() }
                val tokenBalances = withContext(Dispatchers.IO) { VerdisApi.getTokenBalances(wallet.address) }
                val transactions = withContext(Dispatchers.IO) { VerdisApi.getTransactions(wallet.address) }

                val balanceVco = balance / 1_000_000_000_000_000_000.0
                tvBalance.text = String.format("%.4f", balanceVco)

                val price = market?.priceUSD ?: 0.0
                tvBalanceUsd.text = "$${String.format("%.2f", balanceVco * price)}"

                val change = market?.priceChange24h ?: 0.0
                val changeStr = if (change >= 0) "+${String.format("%.1f", change)}%" else "${String.format("%.1f", change)}%"
                tvChange24h.text = " $changeStr"
                tvChange24h.setTextColor(
                    if (change >= 0) 0xFF00FF88.toInt() else 0xFFFF5F5F.toInt()
                )

                tvBlockHeight.text = chainInfo?.height?.toString() ?: "---"
                tvValidators.text = "${chainInfo?.validatorCount ?: 0}"

                // Token list
                val tokens = mutableListOf<TokenItem>()
                tokens.add(TokenItem("VCO", "Verdis", balanceVco, price))
                if (tokenBalances != null) {
                    for ((symbol, rawBalance) in tokenBalances.balances) {
                        if (symbol != "VCO") {
                            val bal = rawBalance
                            tokens.add(TokenItem(symbol, symbol, bal, 0.0))
                        }
                    }
                }
                rvTokens.adapter = TokenAdapter(tokens)

                // Transactions
                val txList = transactions ?: emptyList()
                rvTransactions.adapter = TxAdapter(txList, wallet.address)

            } catch (e: Exception) {
                Toast.makeText(context, "Connection error: ${e.message}", Toast.LENGTH_SHORT).show()
            } finally {
                swipeRefresh.isRefreshing = false
            }
        }
    }

    data class TokenItem(val symbol: String, val name: String, val balance: Double, val price: Double)

    class TokenAdapter(private val tokens: List<TokenItem>) : RecyclerView.Adapter<TokenAdapter.VH>() {
        class VH(view: View) : RecyclerView.ViewHolder(view) {
            val initial: TextView = view.findViewById(R.id.tv_token_initial)
            val name: TextView = view.findViewById(R.id.tv_token_name)
            val price: TextView = view.findViewById(R.id.tv_token_price)
            val balance: TextView = view.findViewById(R.id.tv_token_balance)
            val value: TextView = view.findViewById(R.id.tv_token_value)
        }

        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int) =
            VH(LayoutInflater.from(parent.context).inflate(R.layout.item_token, parent, false))

        override fun onBindViewHolder(holder: VH, position: Int) {
            val t = tokens[position]
            holder.initial.text = t.symbol.first().toString()
            holder.name.text = t.symbol
            holder.price.text = if (t.price > 0) "$${String.format("%.4f", t.price)}" else "—"
            holder.balance.text = String.format("%.4f", t.balance)
            holder.value.text = if (t.price > 0) "$${String.format("%.2f", t.balance * t.price)}" else "—"
        }

        override fun getItemCount() = tokens.size
    }

    class TxAdapter(
        private val txs: List<Transaction>,
        private val myAddress: String
    ) : RecyclerView.Adapter<TxAdapter.VH>() {
        class VH(view: View) : RecyclerView.ViewHolder(view) {
            val type: TextView = view.findViewById(R.id.tv_tx_type)
            val time: TextView = view.findViewById(R.id.tv_tx_time)
            val amount: TextView = view.findViewById(R.id.tv_tx_amount)
            val status: TextView = view.findViewById(R.id.tv_tx_status)
        }

        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int) =
            VH(LayoutInflater.from(parent.context).inflate(R.layout.item_tx, parent, false))

        override fun onBindViewHolder(holder: VH, position: Int) {
            val tx = txs[position]
            val isReceived = tx.from != myAddress
            holder.type.text = if (isReceived) "Received" else "Sent"
            holder.amount.text = if (isReceived) "+" else "-" + String.format("%.4f", tx.amount) + " VCO"
            holder.amount.setTextColor(if (isReceived) 0xFF00FF88.toInt() else 0xFFFF5F5F.toInt())
            holder.time.text = tx.timestamp ?: "---"
            holder.status.text = tx.status ?: "Confirmed"
        }

        override fun getItemCount() = txs.size
    }
}
