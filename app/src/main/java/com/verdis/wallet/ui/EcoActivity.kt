package com.verdis.wallet.ui

import android.app.Activity
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.ListView
import android.widget.ProgressBar
import android.widget.TextView
import android.widget.Toast
import com.verdis.wallet.R

data class ReforestationProject(
    val name: String,
    val treesPlanted: Int,
    val location: String
)

class EcoActivity : Activity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_eco)

        val projects = listOf(
            ReforestationProject("Amazon Restoration", 45000, "Brazil"),
            ReforestationProject("Borneo Reforestation", 28000, "Indonesia"),
            ReforestationProject("Congo Basin Project", 18000, "DR Congo"),
            ReforestationProject("Madagascar Green Corridor", 12000, "Madagascar")
        )

        val adapter = object : ArrayAdapter<ReforestationProject>(this, android.R.layout.simple_list_item_2, projects) {
            override fun getView(position: Int, convertView: View?, parent: ViewGroup): View {
                val view = convertView ?: LayoutInflater.from(context)
                    .inflate(android.R.layout.simple_list_item_2, parent, false)
                val p = projects[position]
                view.findViewById<TextView>(android.R.id.text1).apply {
                    text = "${p.name}  |  ${p.location}"
                    setTextColor(0xFF00d97e.toInt())
                    textSize = 13f
                }
                view.findViewById<TextView>(android.R.id.text2).apply {
                    text = "${p.treesPlanted} trees planted"
                    setTextColor(0xFF8b8b8f.toInt())
                    textSize = 12f
                }
                return view
            }
        }

        findViewById<ListView>(R.id.projectList).adapter = adapter
        findViewById<TextView>(R.id.carbonCreditsText).text = "0 CARBON"
        findViewById<ProgressBar>(R.id.greenScoreBar).progress = 0
        findViewById<TextView>(R.id.greenScoreText).text = "Score: 0/100"

        findViewById<Button>(R.id.mintCarbonBtn).setOnClickListener {
            Toast.makeText(this, "Minting carbon credit (submitting extrinsic...)", Toast.LENGTH_SHORT).show()
        }
    }
}
