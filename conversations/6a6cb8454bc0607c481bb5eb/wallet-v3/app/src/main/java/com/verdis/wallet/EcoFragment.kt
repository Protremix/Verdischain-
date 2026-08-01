package com.verdis.wallet

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch

class EcoFragment : Fragment() {
    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        val v = inflater.inflate(R.layout.fragment_eco, container, false)
        val tvCo2 = v.findViewById<TextView>(R.id.tv_co2)
        val tvTrees = v.findViewById<TextView>(R.id.tv_trees)
        val tvValidators = v.findViewById<TextView>(R.id.tv_green_validators)
        val tvScore = v.findViewById<TextView>(R.id.tv_eco_score)
        val tvInfo = v.findViewById<TextView>(R.id.tv_eco_info)

        lifecycleScope.launch {
            try {
                val eco = VerdisApi.getEcoImpact()
                val co2 = eco["totalCO2Offset"] ?: eco["co2Offset"] ?: 0
                val trees = eco["totalTreesPlanted"] ?: eco["treesPlanted"] ?: 0
                val vals = eco["greenValidatorCount"] ?: eco["greenValidators"] ?: 0
                val score = eco["averageGreenScore"] ?: eco["avgScore"] ?: 0

                tvCo2?.text = "${co2} t"
                tvTrees?.text = "$trees"
                tvValidators?.text = "$vals"
                tvScore?.text = "$score"
            } catch (e: Exception) {
                tvInfo?.text = "Failed to load eco data"
            }
        }
        return v
    }
}
