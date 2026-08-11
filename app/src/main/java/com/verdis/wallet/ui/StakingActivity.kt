package com.verdis.wallet.ui

import android.app.Activity
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.EditText
import android.widget.ListView
import android.widget.TextView
import android.widget.Toast
import com.verdis.wallet.R
import com.verdis.wallet.VerdisApp

data class Validator(
    val name: String,
    val greenScore: Int,
    val energySource: String,
    val totalStake: String
)

class StakingActivity : androidx.fragment.app.FragmentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_staking)

        // Mock validators (in production, fetch from chain)
        val validators = listOf(
            Validator("Verdis-Eco-01", 98, "Solar", "12.5M VRDX"),
            Validator("GreenNode-02", 95, "Wind", "8.3M VRDX"),
            Validator("Forest-Val-03", 92, "Hydro", "5.1M VRDX"),
            Validator("CarbonNode-04", 88, "Solar", "3.2M VRDX"),
            Validator("EcoVal-05", 85, "Wind", "2.7M VRDX")
        )

        val adapter = object : ArrayAdapter<Validator>(this, android.R.layout.simple_list_item_1, validators) {
            override fun getView(position: Int, convertView: View?, parent: ViewGroup): View {
                val view = convertView ?: LayoutInflater.from(context)
                    .inflate(android.R.layout.simple_list_item_2, parent, false)
                val v = validators[position]
                view.findViewById<TextView>(android.R.id.text1).apply {
                    text = "${v.name}  |  Score: ${v.greenScore}/100  |  ${v.energySource}"
                    setTextColor(0xFFe4e4e7.toInt())
                    textSize = 13f
                }
                view.findViewById<TextView>(android.R.id.text2).apply {
                    text = "Total Stake: ${v.totalStake}"
                    setTextColor(0xFF8b8b8f.toInt())
                    textSize = 12f
                }
                return view
            }
        }

        findViewById<ListView>(R.id.validatorList).adapter = adapter
        findViewById<TextView>(R.id.totalStakedText).text = "0 VRDX"

        findViewById<Button>(R.id.stakeBtn).setOnClickListener {
            val amount = findViewById<EditText>(R.id.stakeAmountInput).text.toString().trim()
            if (amount.isEmpty()) {
                Toast.makeText(this, "Enter amount", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            // Biometric gate for staking
            val securityHelper = (application as com.verdis.wallet.VerdisApp).securityHelper
            com.verdis.wallet.security.BiometricGate.requireForStake(this, securityHelper, {
                Toast.makeText(this, "Staking $amount VRDX (submitting extrinsic...)", Toast.LENGTH_SHORT).show()
            }, {
                Toast.makeText(this, "Biometric/PIN required to stake", Toast.LENGTH_SHORT).show()
            })
        }
    }
}
