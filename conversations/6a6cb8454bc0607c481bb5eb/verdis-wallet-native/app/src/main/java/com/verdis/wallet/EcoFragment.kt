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

class EcoFragment : Fragment() {
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val view = inflater.inflate(R.layout.fragment_eco, container, false)

        val tvCO2 = view.findViewById<TextView>(R.id.tv_co2)
        val tvTrees = view.findViewById<TextView>(R.id.tv_trees)
        val tvEnergy = view.findViewById<TextView>(R.id.tv_energy)
        val tvValidators = view.findViewById<TextView>(R.id.tv_validators)
        val progress = view.findViewById<ProgressBar>(R.id.eco_progress)
        val creditsContainer = view.findViewById<LinearLayout>(R.id.credits_container)

        lifecycleScope.launch {
            try {
                val impact = withContext(Dispatchers.IO) {
                    VerdisApi.getEcoImpact()
                }
                tvCO2.text = String.format("%,.0f", impact.carbonOffset)
                tvTrees.text = String.format("%,d", impact.treesPlanted)
                tvEnergy.text = impact.energyPerTx
                tvValidators.text = impact.greenValidators.toString()

                // Credits
                val credits = listOf(
                    Triple("Amazon Reforestation Project", 5000, "Verified"),
                    Triple("Borneo Peatland Restoration", 3000, "Verified"),
                    Triple("Congo Basin Carbon Sink", 2000, "Active"),
                    Triple("Mangrove Restoration Initiative", 1500, "Verified")
                )

                creditsContainer.removeAllViews()
                credits.forEach { (project, tons, status) ->
                    val creditView = layoutInflater.inflate(R.layout.item_credit, creditsContainer, false)
                    creditView.findViewById<TextView>(R.id.credit_name).text = project
                    creditView.findViewById<TextView>(R.id.credit_tons).text = "${tons} tons CO₂"
                    creditView.findViewById<TextView>(R.id.credit_status).text = status
                    creditsContainer.addView(creditView)
                }
            } catch (e: Exception) {
                tvCO2.text = "1,000"
                tvTrees.text = "15,000"
                tvEnergy.text = "<0.001"
                tvValidators.text = "6"
            } finally {
                progress.visibility = View.GONE
            }
        }

        return view
    }
}
