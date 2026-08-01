package com.verdis.wallet

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.LinearLayout
import android.widget.ProgressBar
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
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
        val containerLayout = view.findViewById<LinearLayout>(R.id.history_container)
        val progress = view.findViewById<ProgressBar>(R.id.history_progress)

        val wallet = WalletManager.loadWallet(requireContext())

        lifecycleScope.launch {
            try {
                val txs = withContext(Dispatchers.IO) {
                    VerdisApi.getTransactions(wallet?.address)
                }

                containerLayout.removeAllViews()

                if (txs.isEmpty()) {
                    val tv = TextView(requireContext()).apply {
                        text = "No transactions yet"
                        setTextColor(0xFF8BA898.toInt())
                        textSize = 14f
                        setPadding(40, 60, 40, 60)
                        gravity = View.TEXT_ALIGNMENT_CENTER
                    }
                    containerLayout.addView(tv)
                } else {
                    txs.forEach { tx ->
                        val isOut = wallet?.address?.lowercase() == tx.from.lowercase()
                        val itemView = layoutInflater.inflate(R.layout.item_tx, containerLayout, false)
                        val dirText = if (isOut) "↑" else "↓"
                        itemView.findViewById<TextView>(R.id.tx_dir).text = dirText
                        itemView.findViewById<TextView>(R.id.tx_addr).text =
                            (if (isOut) tx.to else tx.from).take(10) + "..." + (if (isOut) tx.to else tx.from).takeLast(6)
                        itemView.findViewById<TextView>(R.id.tx_time).text = tx.timestamp
                        val amtView = itemView.findViewById<TextView>(R.id.tx_amount)
                        amtView.text = (if (isOut) "-" else "+") + String.format("%,.2f", tx.amount)
                        amtView.setTextColor(if (isOut) 0xFFFF5F5F.toInt() else 0xFF00FF88.toInt())
                        containerLayout.addView(itemView)
                    }
                }
            } catch (e: Exception) {
                val tv = TextView(requireContext()).apply {
                    text = "No transactions yet"
                    setTextColor(0xFF8BA898.toInt())
                    textSize = 14f
                    setPadding(40, 60, 40, 60)
                }
                containerLayout.addView(tv)
            } finally {
                progress.visibility = View.GONE
            }
        }

        return view
    }
}
