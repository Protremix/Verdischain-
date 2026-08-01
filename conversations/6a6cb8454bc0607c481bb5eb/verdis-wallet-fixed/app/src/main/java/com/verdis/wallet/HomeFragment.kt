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

    // Use nullable refs to avoid memory leaks and post-detach crashes
    private var tvAddress: TextView? = null
    private var tvBalance: TextView? = null
    private var tvBalanceUsd: TextView? = null
    private var tvChange24h: TextView? = null
    private var tvBlockHeight: TextView? = null
    private var tvValidators: TextView? = null
    private var rvTokens: RecyclerView? = null
    private var rvTransactions: RecyclerView? = null
    private var swipeRefresh: SwipeRefreshLayout? = null

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val view = inflater.inflate(R.layout.fragment_home, container, false)

        tvAddress      = view.findViewById(R.id.tv_address)
        tvBalance      = view.findViewById(R.id.tv_total_balance)
        tvBalanceUsd   = view.findViewById(R.id.tv_balance_usd)
        tvChange24h    = view.findViewById(R.id.tv_change_24h)
        tvBlockHeight  = view.findViewById(R.id.tv_block_height)
        tvValidators   = view.findViewById(R.id.tv_validators)
        rvTokens       = view.findViewById(R.id.rv_tokens)
        rvTransactions = view.findViewById(R.id.rv_transactions)
        swipeRefresh   = view.findViewById(R.id.swipe_refresh)

        rvTokens?.layoutManager = LinearLayoutManager(context)
        rvTokens?.isNestedScrollingEnabled = false
        rvTransactions?.layoutManager = LinearLayoutManager(context)
        rvTransactions?.isNestedScrollingEnabled = false

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
        tvAddress?.setOnClickListener {
            val addr = tvAddress?.text?.toString() ?: return@setOnClickListener
            val cm = requireContext().getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
            cm.setPrimaryClip(ClipData.newPlainText("address", addr))
            Toast.makeText(context, "Address copied!", Toast.LENGTH_SHORT).show()
        }

        swipeRefresh?.setOnRefreshListener { loadData() }
        loadData()
        return view
    }

    override fun onDestroyView() {
        super.onDestroyView()
        tvAddress = null; tvBalance = null; tvBalanceUsd = null
        tvChange24h = null; tvBlockHeight = null; tvValidators = null
        rvTokens = null; rvTransactions = null; swipeRefresh = null
    }

    private fun loadData() {
        if (!isAdded || context == null) return
        lifecycleScope.launch {
            val ctx = context ?: return@launch
            val wallet = WalletManager.loadWallet(ctx)
            if (wallet == null) {
                if (isAdded) (activity as? MainActivity)?.showOnboarding()
                return@launch
            }

            // Show shortened address
            val shortAddr = "${wallet.address.take(10)}...${wallet.address.takeLast(8)}"
            tvAddress?.text = shortAddr

            try {
                // Fetch each endpoint independently — one failure won't crash the rest
                val balanceResp = withContext(Dispatchers.IO) {
                    runCatching { VerdisApi.getBalance(wallet.address) }.getOrNull()
                }
                val market = withContext(Dispatchers.IO) {
                    runCatching { VerdisApi.getMarketData() }.getOrNull()
                }
                val chainInfo = withContext(Dispatchers.IO) {
                    runCatching { VerdisApi.getBlockchainInfo() }.getOrNull()
                }
                val tokenBalances = withContext(Dispatchers.IO) {
                    runCatching { VerdisApi.getTokenBalances(wallet.address) }.getOrNull()
                }
                val transactions = withContext(Dispatchers.IO) {
                    runCatching { VerdisApi.getTransactions(wallet.address) }.getOrNull()
                }

                if (!isAdded) return@launch

                // Balance — server returns VCO directly (not wei). Guard both cases.
                val rawBalance = balanceResp?.balance ?: 0.0
                val balanceVco = when {
                    rawBalance > 1_000_000_000_000_000.0 -> rawBalance / 1_000_000_000_000_000_000.0
                    else -> rawBalance
                }
                tvBalance?.text = String.format("%.4f VCO", balanceVco)

                val price = market?.priceUSD ?: 0.001
                tvBalanceUsd?.text = "\$${String.format("%.4f", balanceVco * price)}"

                val change = market?.priceChange24h ?: 0.0
                tvChange24h?.text = if (change >= 0) "+${String.format("%.2f", change)}%"
                                    else "${String.format("%.2f", change)}%"
                tvChange24h?.setTextColor(if (change >= 0) 0xFF00FF88.toInt() else 0xFFFF5F5F.toInt())

                tvBlockHeight?.text = chainInfo?.height?.toString() ?: "—"
                tvValidators?.text = (chainInfo?.validatorCount
                    ?: chainInfo?.validators
                    ?: chainInfo?.activeValidators
                    ?: 0).toString()

                val tokens = mutableListOf<TokenItem>()
                tokens.add(TokenItem("VCO", "Verdis Token", balanceVco, price))
                tokenBalances?.balances?.forEach { (sym, bal) ->
                    if (sym != "VCO") tokens.add(TokenItem(sym, sym, bal, 0.0))
                }
                rvTokens?.adapter = TokenAdapter(tokens)
                rvTransactions?.adapter = TxAdapter(transactions ?: emptyList(), wallet.address)

            } catch (e: Exception) {
                if (isAdded) {
                    Toast.makeText(context, "Network error — check connection", Toast.LENGTH_SHORT).show()
                }
            } finally {
                swipeRefresh?.isRefreshing = false
            }
        }
    }

    data class TokenItem(val symbol: String, val name: String, val balance: Double, val price: Double)

    class TokenAdapter(private val tokens: List<TokenItem>) :
        RecyclerView.Adapter<TokenAdapter.VH>() {
        class VH(view: View) : RecyclerView.ViewHolder(view) {
            val initial: TextView = view.findViewById(R.id.tv_token_initial)
            val name: TextView   = view.findViewById(R.id.tv_token_name)
            val price: TextView  = view.findViewById(R.id.tv_token_price)
            val balance: TextView = view.findViewById(R.id.tv_token_balance)
            val value: TextView  = view.findViewById(R.id.tv_token_value)
        }
        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int) =
            VH(LayoutInflater.from(parent.context).inflate(R.layout.item_token, parent, false))
        override fun onBindViewHolder(holder: VH, position: Int) {
            val t = tokens[position]
            holder.initial.text  = t.symbol.take(1)
            holder.name.text     = t.symbol
            holder.price.text    = if (t.price > 0) "\$${String.format("%.6f", t.price)}" else "—"
            holder.balance.text  = String.format("%.4f", t.balance)
            holder.value.text    = if (t.price > 0) "\$${String.format("%.4f", t.balance * t.price)}" else "—"
        }
        override fun getItemCount() = tokens.size
    }

    class TxAdapter(private val txs: List<Transaction>, private val myAddress: String) :
        RecyclerView.Adapter<TxAdapter.VH>() {
        class VH(view: View) : RecyclerView.ViewHolder(view) {
            val type: TextView    = view.findViewById(R.id.tv_tx_type)
            val address: TextView = view.findViewById(R.id.tv_tx_address)
            val amount: TextView  = view.findViewById(R.id.tv_tx_amount)
            val time: TextView    = view.findViewById(R.id.tv_tx_time)
        }
        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int) =
            VH(LayoutInflater.from(parent.context).inflate(R.layout.item_tx, parent, false))
        override fun onBindViewHolder(holder: VH, position: Int) {
            val tx = txs[position]
            val isRx = tx.to.equals(myAddress, ignoreCase = true)
            holder.type.text    = if (isRx) "↓ Received" else "↑ Sent"
            holder.address.text = if (isRx) "From: ${tx.from.take(10)}..." else "To: ${tx.to.take(10)}..."
            holder.amount.text  = if (isRx) "+${tx.amount} VCO" else "-${tx.amount} VCO"
            holder.amount.setTextColor(if (isRx) 0xFF00FF88.toInt() else 0xFFFF5F5F.toInt())
            holder.time.text = tx.timestamp.take(16)
        }
        override fun getItemCount() = txs.size
    }
}
