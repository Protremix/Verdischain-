package com.verdis.wallet

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout
import com.google.android.material.tabs.TabLayout
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class HistoryFragment : Fragment() {

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val view = inflater.inflate(R.layout.fragment_history, container, false)

        val rvTransactions = view.findViewById<RecyclerView>(R.id.rv_transactions)
        val tabLayout = view.findViewById<TabLayout>(R.id.tab_layout)
        val swipeRefresh = view.findViewById<SwipeRefreshLayout>(R.id.swipe_refresh)

        rvTransactions.layoutManager = LinearLayoutManager(context)
        rvTransactions.isNestedScrollingEnabled = false

        swipeRefresh.setOnRefreshListener { loadTransactions(rvTransactions, -1) }

        tabLayout.addOnTabSelectedListener(object : TabLayout.OnTabSelectedListener {
            override fun onTabSelected(tab: TabLayout.Tab) {
                loadTransactions(rvTransactions, tab.position)
            }
            override fun onTabUnselected(tab: TabLayout.Tab) {}
            override fun onTabReselected(tab: TabLayout.Tab) {}
        })

        loadTransactions(rvTransactions, -1)
        return view
    }

    private fun loadTransactions(rv: RecyclerView, filter: Int) {
        val wallet = WalletManager.loadWallet(requireContext()) ?: return
        lifecycleScope.launch {
            try {
                val allTxs = withContext(Dispatchers.IO) { VerdisApi.getTransactions(wallet.address) } ?: emptyList()
                val filtered = when (filter) {
                    1 -> allTxs.filter { it.from == wallet.address }
                    2 -> allTxs.filter { it.to == wallet.address }
                    3 -> allTxs.filter { it.type == "swap" || it.type == "dex" }
                    else -> allTxs
                }
                rv.adapter = TxAdapter(filtered, wallet.address)
            } catch (e: Exception) {
                Toast.makeText(context, "Connection error", Toast.LENGTH_SHORT).show()
            } finally {
                view?.findViewById<SwipeRefreshLayout>(R.id.swipe_refresh)?.isRefreshing = false
            }
        }
    }

    class TxAdapter(private val txs: List<VerdisApi.Transaction>, private val myAddress: String) :
        RecyclerView.Adapter<TxAdapter.VH>() {
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
            holder.amount.text = (if (isReceived) "+" else "-") + String.format("%.4f", tx.amount) + " VCO"
            holder.amount.setTextColor(if (isReceived) 0xFF00FF88.toInt() else 0xFFFF5F5F.toInt())
            holder.time.text = tx.timestamp ?: "---"
            holder.status.text = tx.status ?: "Confirmed"
        }

        override fun getItemCount() = txs.size
    }
}
