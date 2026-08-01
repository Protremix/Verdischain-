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

class StakeFragment : Fragment() {
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val view = inflater.inflate(R.layout.fragment_stake, container, false)

        val container_layout = view.findViewById<LinearLayout>(R.id.validators_container)
        val progress = view.findViewById<ProgressBar>(R.id.stake_progress)

        lifecycleScope.launch {
            try {
                val validators = withContext(Dispatchers.IO) {
                    VerdisApi.getValidators()
                }

                container_layout.removeAllViews()
                validators.take(27).forEach { v ->
                    val itemView = layoutInflater.inflate(R.layout.item_validator, container_layout, false)
                    itemView.findViewById<TextView>(R.id.validator_rank).text = v.rank.toString()
                    itemView.findViewById<TextView>(R.id.validator_addr).text =
                        v.address.take(10) + "..." + v.address.takeLast(6)
                    itemView.findViewById<TextView>(R.id.validator_stats).text =
                        "Blocks: ${v.blocksProduced} · Votes: ${v.votes}"
                    itemView.findViewById<TextView>(R.id.validator_score).text = v.greenScore.toString()

                    if (!v.active) {
                        itemView.alpha = 0.5f
                    }

                    container_layout.addView(itemView)
                }
            } catch (e: Exception) {
                val tv = TextView(requireContext()).apply {
                    text = "Unable to load validators"
                    setTextColor(0xFF8BA898.toInt())
                    textSize = 14f
                    setPadding(40, 40, 40, 40)
                }
                container_layout.addView(tv)
            } finally {
                progress.visibility = View.GONE
            }
        }

        return view
    }
}
