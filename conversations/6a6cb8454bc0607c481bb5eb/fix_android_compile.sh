#!/usr/bin/env bash
set -e

# 1. Add ContractInfo and related functions to VerdisApi.kt
python3 << 'PYEOF'
with open('/opt/verdis-wallet-native/app/src/main/java/com/verdis/wallet/VerdisApi.kt', 'r') as f:
    content = f.read()

# Add data classes before the final closing brace of VerdisApi object/class
# Find a good insertion point - after the getTransactions function
insert_after = '''    suspend fun getTransactions(addr: String): List<Map<String, Any?>> {
        val r = get("/api/explorer/address/$addr") ?: return emptyList()
        return try {
            val obj = JsonParser.parseString(r).asJsonObject
            val txs = obj.get("transactions") ?: obj.get("txs")
            if (txs != null) gson.fromJson(txs, List::class.java) as List<Map<String, Any?>> else emptyList()
        } catch (e: Exception) { emptyList() }
    }'''

contract_code = '''

    suspend fun getContracts(): List<Map<String, Any?>> {
        val r = get("/api/contracts") ?: return emptyList()
        return try {
            val obj = JsonParser.parseString(r).asJsonObject
            val contracts = obj.get("contracts") ?: obj.get("data")
            if (contracts != null) gson.fromJson(contracts, List::class.java) as List<Map<String, Any?>> else emptyList()
        } catch (e: Exception) { emptyList() }
    }

    suspend fun deployContract(from: String, name: String, bytecode: String, signature: String, publicKey: String): Map<String, Any?> {
        val body = gson.toJson(mapOf(
            "from" to from,
            "name" to name,
            "bytecode" to bytecode,
            "signature" to signature,
            "publicKey" to publicKey
        ))
        val r = post("/api/contract/deploy", body) ?: return mapOf("success" to false)
        return try {
            gson.fromJson(r, Map::class.java) as Map<String, Any?>
        } catch (e: Exception) { mapOf("success" to false) }
    }'''

if 'getContracts' not in content:
    content = content.replace(insert_after, insert_after + contract_code, 1)
    with open('/opt/verdis-wallet-native/app/src/main/java/com/verdis/wallet/VerdisApi.kt', 'w') as f:
        f.write(content)
    print('VerdisApi.kt updated with contract functions')
else:
    print('getContracts already exists, skipping')
PYEOF

# 2. Rewrite HistoryFragment to use Map<String, Any?> instead of Transaction
cat > /opt/verdis-wallet-native/app/src/main/java/com/verdis/wallet/HistoryFragment.kt << 'KOTLIN_EOF'
package com.verdis.wallet

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.LinearLayout
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

class HistoryFragment : Fragment() {

    private val tabNames = listOf("All", "Sent", "Received", "Swaps")
    private var selectedTab = 0

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val view = inflater.inflate(R.layout.fragment_history, container, false)

        val rvTransactions = view.findViewById<RecyclerView>(R.id.rv_transactions)
        val swipeRefresh = view.findViewById<SwipeRefreshLayout>(R.id.swipe_refresh)
        val tabContainer = view.findViewById<LinearLayout>(R.id.tab_container)

        rvTransactions.layoutManager = LinearLayoutManager(context)
        rvTransactions.isNestedScrollingEnabled = false

        swipeRefresh.setOnRefreshListener { loadTransactions(rvTransactions, selectedTab - 1) }

        tabContainer?.let { c ->
            c.orientation = LinearLayout.HORIZONTAL
            tabNames.forEachIndexed { index, name ->
                val tab = TextView(requireContext()).apply {
                    text = name
                    textSize = 13f
                    setPadding(32, 24, 32, 24)
                    setTextColor(if (index == 0) 0xFF00FF88.toInt() else 0xFF8BA898.toInt())
                    setBackgroundColor(if (index == 0) 0x1500FF88 else 0x00000000)
                    setOnClickListener {
                        selectedTab = index
                        for (i in 0 until c.childCount) {
                            val child = c.getChildAt(i) as TextView
                            child.setTextColor(if (i == index) 0xFF00FF88.toInt() else 0xFF8BA898.toInt())
                            child.setBackgroundColor(if (i == index) 0x1500FF88 else 0x00000000)
                        }
                        loadTransactions(rvTransactions, index - 1)
                    }
                }
                val params = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
                c.addView(tab, params)
            }
        }

        loadTransactions(rvTransactions, -1)
        return view
    }

    private fun loadTransactions(rv: RecyclerView, filter: Int) {
        val wallet = WalletManager.loadWallet(requireContext()) ?: return
        lifecycleScope.launch {
            try {
                val allTxs = withContext(Dispatchers.IO) { VerdisApi.getTransactions(wallet.address) }
                val filtered = when (filter) {
                    1 -> allTxs.filter { it["from"]?.toString() == wallet.address }
                    2 -> allTxs.filter { it["to"]?.toString() == wallet.address }
                    3 -> allTxs.filter {
                        val type = it["type"]?.toString() ?: ""
                        type.contains("swap") || type.contains("dex")
                    }
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

    class TxAdapter(private val txs: List<Map<String, Any?>>, private val myAddress: String) :
        RecyclerView.Adapter<TxAdapter.VH>() {
        class VH(view: View) : RecyclerView.ViewHolder(view) {
            val type: TextView = view.findViewById(R.id.tv_tx_type)
            val time: TextView = view.findViewById(R.id.tv_tx_time)
            val amount: TextView = view.findViewById(R.id.tv_tx_amount)
        }

        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int) =
            VH(LayoutInflater.from(parent.context).inflate(R.layout.item_tx, parent, false))

        override fun onBindViewHolder(holder: VH, position: Int) {
            val tx = txs[position]
            val from = tx["from"]?.toString() ?: ""
            val to = tx["to"]?.toString() ?: ""
            val isReceived = from != myAddress
            holder.type.text = if (isReceived) "↓" else "↑"
            val amt = tx["amount"]?.toString() ?: "0"
            holder.amount.text = (if (isReceived) "+" else "-") + String.format("%.4f", amt.toDoubleOrNull() ?: 0.0) + " VRDX"
            holder.amount.setTextColor(if (isReceived) 0xFF00FF88.toInt() else 0xFFFF5F5F.toInt())
            holder.time.text = tx["timestamp"]?.toString() ?: tx["time"]?.toString() ?: "---"
        }

        override fun getItemCount() = txs.size
    }
}
KOTLIN_EOF

# 3. Rewrite DappFragment to use Map<String, Any?> instead of ContractInfo
cat > /opt/verdis-wallet-native/app/src/main/java/com/verdis/wallet/DappFragment.kt << 'KOTLIN_EOF'
package com.verdis.wallet

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class DappFragment : Fragment() {

    private val tabNames = listOf("DApps", "Deploy", "Contracts")
    private lateinit var contentDapps: View
    private lateinit var contentDeploy: View
    private lateinit var contentContracts: View

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val view = inflater.inflate(R.layout.fragment_dapp, container, false)

        val tabContainer = view.findViewById<LinearLayout>(R.id.tab_container)
        contentDapps = view.findViewById(R.id.content_dapps)
        contentDeploy = view.findViewById(R.id.content_deploy)
        contentContracts = view.findViewById(R.id.content_contracts)

        tabContainer?.let { c ->
            c.orientation = LinearLayout.HORIZONTAL
            tabNames.forEachIndexed { index, name ->
                val tab = TextView(requireContext()).apply {
                    text = name
                    textSize = 13f
                    setPadding(32, 24, 32, 24)
                    setTextColor(if (index == 0) 0xFF00FF88.toInt() else 0xFF8BA898.toInt())
                    setBackgroundColor(if (index == 0) 0x1500FF88 else 0x00000000)
                    setOnClickListener {
                        for (i in 0 until c.childCount) {
                            val child = c.getChildAt(i) as TextView
                            child.setTextColor(if (i == index) 0xFF00FF88.toInt() else 0xFF8BA898.toInt())
                            child.setBackgroundColor(if (i == index) 0x1500FF88 else 0x00000000)
                        }
                        contentDapps.visibility = if (index == 0) View.VISIBLE else View.GONE
                        contentDeploy.visibility = if (index == 1) View.VISIBLE else View.GONE
                        contentContracts.visibility = if (index == 2) View.VISIBLE else View.GONE
                        if (index == 2) loadContracts()
                    }
                }
                val params = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
                c.addView(tab, params)
            }
        }

        // DApp buttons
        view.findViewById<View>(R.id.dapp_dex)?.setOnClickListener {
            (activity as? MainActivity)?.navigateTo(R.id.nav_swap)
        }
        view.findViewById<View>(R.id.dapp_ido)?.setOnClickListener {
            (activity as? MainActivity)?.navigateTo(R.id.nav_ido)
        }
        view.findViewById<View>(R.id.dapp_bridge)?.setOnClickListener {
            Toast.makeText(context, "Bridge coming soon", Toast.LENGTH_SHORT).show()
        }
        view.findViewById<View>(R.id.dapp_explorer)?.setOnClickListener {
            Toast.makeText(context, "Open verdischain.com/explorer.html", Toast.LENGTH_SHORT).show()
        }
        view.findViewById<View>(R.id.dapp_markets)?.setOnClickListener {
            Toast.makeText(context, "Open verdischain.com/markets.html", Toast.LENGTH_SHORT).show()
        }
        view.findViewById<View>(R.id.dapp_eco)?.setOnClickListener {
            (activity as? MainActivity)?.navigateTo(R.id.nav_eco)
        }

        // Open DApp URL
        val etUrl = view.findViewById<EditText>(R.id.et_dapp_url)
        view.findViewById<Button>(R.id.btn_open_dapp)?.setOnClickListener {
            val url = etUrl.text.toString().trim()
            if (url.isNotEmpty()) {
                Toast.makeText(context, "Opening $url...", Toast.LENGTH_SHORT).show()
            }
        }

        // Deploy contract
        val etName = view.findViewById<EditText>(R.id.et_contract_name)
        val etBytecode = view.findViewById<EditText>(R.id.et_bytecode)
        view.findViewById<Button>(R.id.btn_deploy)?.setOnClickListener {
            val name = etName.text.toString().trim()
            val bytecode = etBytecode.text.toString().trim()
            if (name.isEmpty() || bytecode.isEmpty()) {
                Toast.makeText(context, "Fill in name and bytecode", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            deployContract(name, bytecode)
        }

        // Quick templates
        view.findViewById<Button>(R.id.btn_template_token)?.setOnClickListener {
            etName.setText("CustomToken")
            etBytecode.setText("PUSH1 0x60 PUSH1 0x40 MSTORE CALLDATASIZE")
        }
        view.findViewById<Button>(R.id.btn_template_multisig)?.setOnClickListener {
            etName.setText("MultiSigWallet")
            etBytecode.setText("PUSH1 0x02 PUSH1 0x00 SSTORE PUSH1 0x02 PUSH1 0x01 SSTORE")
        }
        view.findViewById<Button>(R.id.btn_template_timelock)?.setOnClickListener {
            etName.setText("TimeLockVault")
            etBytecode.setText("PUSH1 0x00 TIMESTAMP GT PUSH1 0x01 JUMPI REVERT")
        }

        return view
    }

    private fun deployContract(name: String, bytecode: String) {
        val wallet = WalletManager.loadWallet(requireContext()) ?: return
        lifecycleScope.launch {
            try {
                val signature = WalletManager.signTransaction(wallet, "", 0.0, 0.01, 0)
                val result = withContext(Dispatchers.IO) {
                    VerdisApi.deployContract(wallet.address, name, bytecode, signature, wallet.publicKey)
                }
                val success = result["success"]?.toString()?.toBoolean() ?: false
                if (success) {
                    Toast.makeText(context, "Contract '$name' deployed ✓", Toast.LENGTH_LONG).show()
                    loadContracts()
                } else {
                    Toast.makeText(context, "Deploy failed: ${result["error"] ?: "unknown"}", Toast.LENGTH_LONG).show()
                }
            } catch (e: Exception) {
                Toast.makeText(context, "Error: ${e.message}", Toast.LENGTH_LONG).show()
            }
        }
    }

    private fun loadContracts() {
        val rvContracts = view?.findViewById<RecyclerView>(R.id.rv_contracts) ?: return
        rvContracts.layoutManager = LinearLayoutManager(context)
        rvContracts.isNestedScrollingEnabled = false

        lifecycleScope.launch {
            try {
                val contracts = withContext(Dispatchers.IO) { VerdisApi.getContracts() }
                if (contracts.isNotEmpty()) {
                    rvContracts.adapter = ContractAdapter(contracts)
                } else {
                    Toast.makeText(context, "No contracts deployed yet", Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {}
        }
    }

    class ContractAdapter(private val contracts: List<Map<String, Any?>>) :
        RecyclerView.Adapter<ContractAdapter.VH>() {
        class VH(view: View) : RecyclerView.ViewHolder(view) {
            val id: TextView = view.findViewById(R.id.tv_credit_id)
            val name: TextView = view.findViewById(R.id.tv_credit_amount)
            val addr: TextView = view.findViewById(R.id.tv_credit_verified)
            val owner: TextView = view.findViewById(R.id.tv_credit_project)
        }

        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int) =
            VH(LayoutInflater.from(parent.context).inflate(R.layout.item_credit, parent, false))

        override fun onBindViewHolder(holder: VH, position: Int) {
            val c = contracts[position]
            holder.id.text = "#${position + 1}"
            holder.name.text = c["name"]?.toString() ?: "Unknown"
            holder.addr.text = (c["id"]?.toString() ?: c["address"]?.toString() ?: "").take(12) + "..."
            holder.owner.text = (c["owner"]?.toString() ?: "").take(8)
        }

        override fun getItemCount() = contracts.size
    }
}
KOTLIN_EOF

# 4. Check if VerdisApi has a 'post' function
grep -n 'suspend fun post\|fun post\|private.*post' /opt/verdis-wallet-native/app/src/main/java/com/verdis/wallet/VerdisApi.kt | head -5

echo "All Kotlin files fixed"
