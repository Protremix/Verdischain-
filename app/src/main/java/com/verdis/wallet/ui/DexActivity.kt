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
import android.widget.Spinner
import android.widget.TextView
import android.widget.Toast
import com.verdis.wallet.R

data class DexPool(
    val pair: String,
    val price: String,
    val volume24h: String,
    val swaps: Int
)

class DexActivity : androidx.fragment.app.FragmentActivity() {

    private val pairs = arrayOf(
        "VRDX/CARBON", "VRDX/ECO", "CARBON/ECO",
        "TREE/VRDX", "GREEN/VRDX", "REDD/VRDX"
    )

    private val pools = listOf(
        DexPool("VRDX/CARBON", "0.0125", "1.2M VRDX", 342),
        DexPool("VRDX/ECO", "0.0083", "856K VRDX", 187),
        DexPool("CARBON/ECO", "0.6640", "234K CARBON", 56),
        DexPool("TREE/VRDX", "0.0042", "128K VRDX", 23),
        DexPool("GREEN/VRDX", "0.0156", "456K VRDX", 89),
        DexPool("REDD/VRDX", "0.0078", "201K VRDX", 34)
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_dex)

        val spinner = findViewById<Spinner>(R.id.pairSpinner)
        spinner.adapter = ArrayAdapter(this, android.R.layout.simple_spinner_dropdown_item, pairs)

        val poolAdapter = object : ArrayAdapter<DexPool>(this, android.R.layout.simple_list_item_2, pools) {
            override fun getView(position: Int, convertView: View?, parent: ViewGroup): View {
                val view = convertView ?: LayoutInflater.from(context)
                    .inflate(android.R.layout.simple_list_item_2, parent, false)
                val p = pools[position]
                view.findViewById<TextView>(android.R.id.text1).apply {
                    text = "${p.pair}  |  ${p.price}"
                    setTextColor(0xFFe4e4e7.toInt())
                    textSize = 13f
                }
                view.findViewById<TextView>(android.R.id.text2).apply {
                    text = "24h Vol: ${p.volume24h}  |  Swaps: ${p.swaps}"
                    setTextColor(0xFF8b8b8f.toInt())
                    textSize = 12f
                }
                return view
            }
        }

        findViewById<ListView>(R.id.poolList).adapter = poolAdapter

        findViewById<Button>(R.id.swapBtn).setOnClickListener {
            val amount = findViewById<EditText>(R.id.amountInput).text.toString().trim()
            if (amount.isEmpty()) {
                Toast.makeText(this, "Enter amount", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            val pair = spinner.selectedItem?.toString() ?: "VRDX/CARBON"
            // Biometric gate for swap
            val securityHelper = (application as com.verdis.wallet.VerdisApp).securityHelper
            com.verdis.wallet.security.BiometricGate.requireForSwap(this, securityHelper, {
                Toast.makeText(this, "Swapping $amount $pair (submitting extrinsic...)", Toast.LENGTH_SHORT).show()
            }, {
                Toast.makeText(this, "Biometric/PIN required to swap", Toast.LENGTH_SHORT).show()
            })
        }
    }
}
