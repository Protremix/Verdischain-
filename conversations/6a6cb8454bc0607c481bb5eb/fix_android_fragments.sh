#!/usr/bin/env bash
set -e

# Fix HistoryFragment.kt — replace Material TabLayout with native LinearLayout tabs
cat > /opt/verdis-wallet-native/app/src/main/java/com/verdis/wallet/HistoryFragment.kt << 'KOTLIN_EOF'
package com.verdis.wallet

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
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

        // Create native tabs
        tabContainer?.let { container ->
            container.orientation = LinearLayout.HORIZONTAL
            tabNames.forEachIndexed { index, name ->
                val tab = TextView(requireContext()).apply {
                    text = name
                    textSize = 13f
                    setPadding(32, 24, 32, 24)
                    setTextColor(if (index == 0) 0xFF00FF88.toInt() else 0xFF8BA898.toInt())
                    setBackgroundColor(if (index == 0) 0x1500FF88 else 0x00000000)
                    setOnClickListener {
                        selectedTab = index
                        for (i in 0 until container.childCount) {
                            val child = container.getChildAt(i) as TextView
                            child.setTextColor(if (i == index) 0xFF00FF88.toInt() else 0xFF8BA898.toInt())
                            child.setBackgroundColor(if (i == index) 0x1500FF88 else 0x00000000)
                        }
                        loadTransactions(rvTransactions, index - 1)
                    }
                }
                val params = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
                container.addView(tab, params)
            }
        }

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

    class TxAdapter(private val txs: List<Transaction>, private val myAddress: String) :
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
            holder.amount.text = (if (isReceived) "+" else "-") + String.format("%.4f", tx.amount) + " VRDX"
            holder.amount.setTextColor(if (isReceived) 0xFF00FF88.toInt() else 0xFFFF5F5F.toInt())
            holder.time.text = tx.timestamp ?: "---"
            holder.status.text = tx.status ?: "Confirmed"
        }

        override fun getItemCount() = txs.size
    }
}
KOTLIN_EOF

# Fix DappFragment.kt — replace Material TabLayout with native LinearLayout tabs
cat > /opt/verdis-wallet-native/app/src/main/java/com/verdis/wallet/DappFragment.kt << 'KOTLIN_EOF'
package com.verdis.wallet

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
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

        tabContainer?.let { container ->
            container.orientation = LinearLayout.HORIZONTAL
            tabNames.forEachIndexed { index, name ->
                val tab = TextView(requireContext()).apply {
                    text = name
                    textSize = 13f
                    setPadding(32, 24, 32, 24)
                    setTextColor(if (index == 0) 0xFF00FF88.toInt() else 0xFF8BA898.toInt())
                    setBackgroundColor(if (index == 0) 0x1500FF88 else 0x00000000)
                    setOnClickListener {
                        for (i in 0 until container.childCount) {
                            val child = container.getChildAt(i) as TextView
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
                container.addView(tab, params)
            }
        }

        // DApp buttons
        view.findViewById<View>(R.id.dapp_dex)?.setOnClickListener {
            (activity as? MainActivity)?.navigateTo(R.id.nav_swap)
        }
        view.findViewById<View>(R.id.dapp_ido)?.setOnClickListener {
            Toast.makeText(context, "Opening Token Sale...", Toast.LENGTH_SHORT).show()
        }
        view.findViewById<View>(R.id.dapp_bridge)?.setOnClickListener {
            Toast.makeText(context, "Opening Bridge...", Toast.LENGTH_SHORT).show()
        }
        view.findViewById<View>(R.id.dapp_explorer)?.setOnClickListener {
            Toast.makeText(context, "Opening Explorer...", Toast.LENGTH_SHORT).show()
        }
        view.findViewById<View>(R.id.dapp_markets)?.setOnClickListener {
            Toast.makeText(context, "Opening Markets...", Toast.LENGTH_SHORT).show()
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
                if (result.success) {
                    Toast.makeText(context, "Contract '$name' deployed ✓", Toast.LENGTH_LONG).show()
                    loadContracts()
                } else {
                    Toast.makeText(context, "Deploy failed", Toast.LENGTH_LONG).show()
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
                if (contracts != null) {
                    rvContracts.adapter = ContractAdapter(contracts)
                }
            } catch (e: Exception) {}
        }
    }

    class ContractAdapter(private val contracts: List<ContractInfo>) :
        RecyclerView.Adapter<ContractAdapter.VH>() {
        class VH(view: View) : RecyclerView.ViewHolder(view)

        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int) =
            VH(LayoutInflater.from(parent.context).inflate(R.layout.item_credit, parent, false))

        override fun onBindViewHolder(holder: VH, position: Int) {
            val c = contracts[position]
            holder.itemView.findViewById<TextView>(R.id.tv_credit_id).text = "#${position + 1}"
            holder.itemView.findViewById<TextView>(R.id.tv_credit_amount).text = c.name
            holder.itemView.findViewById<TextView>(R.id.tv_credit_verified).text = c.id.take(12) + "..."
            holder.itemView.findViewById<TextView>(R.id.tv_credit_project).text = c.owner.take(8)
        }

        override fun getItemCount() = contracts.size
    }
}
KOTLIN_EOF

echo "Kotlin files updated"

# Fix fragment_history.xml — replace TabLayout with native LinearLayout
cat > /opt/verdis-wallet-native/app/src/main/res/layout/fragment_history.xml << 'XML_EOF'
<?xml version="1.0" encoding="utf-8"?>
<androidx.swiperefreshlayout.widget.SwipeRefreshLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:id="@+id/swipe_refresh"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="#050A08">

    <ScrollView
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:fillViewport="true">

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical">

            <TextView
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="Transaction History"
                android:textSize="20sp"
                android:textStyle="bold"
                android:textColor="#F0FDF4"
                android:padding="16dp" />

            <LinearLayout
                android:id="@+id/tab_container"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="horizontal"
                android:paddingStart="16dp"
                android:paddingEnd="16dp"
                android:paddingBottom="8dp" />

            <View
                android:layout_width="match_parent"
                android:layout_height="1dp"
                android:background="#1A00FF88" />

            <androidx.recyclerview.widget.RecyclerView
                android:id="@+id/rv_transactions"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:padding="8dp"
                android:nestedScrollingEnabled="false" />

        </LinearLayout>
    </ScrollView>
</androidx.swiperefreshlayout.widget.SwipeRefreshLayout>
XML_EOF

# Fix fragment_dapp.xml — replace TabLayout with native LinearLayout
cat > /opt/verdis-wallet-native/app/src/main/res/layout/fragment_dapp.xml << 'XML_EOF'
<?xml version="1.0" encoding="utf-8"?>
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="#050A08"
    android:fillViewport="true">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical">

        <TextView
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:text="DApp Browser"
            android:textSize="20sp"
            android:textStyle="bold"
            android:textColor="#F0FDF4"
            android:padding="16dp" />

        <LinearLayout
            android:id="@+id/tab_container"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal"
            android:paddingStart="16dp"
            android:paddingEnd="16dp"
            android:paddingBottom="8dp" />

        <View
            android:layout_width="match_parent"
            android:layout_height="1dp"
            android:background="#1A00FF88" />

        <!-- Content: DApps -->
        <LinearLayout
            android:id="@+id/content_dapps"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:padding="16dp"
            android:visibility="visible">

            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="horizontal"
                android:layout_marginBottom="8dp">
                <EditText
                    android:id="@+id/et_dapp_url"
                    android:layout_width="0dp"
                    android:layout_height="44dp"
                    android:layout_weight="1"
                    android:hint="Enter DApp URL"
                    android:textColorHint="#547363"
                    android:textColor="#F0FDF4"
                    android:background="#0D1A14"
                    android:padding="12dp"
                    android:inputType="textUri"
                    android:textSize="13sp" />
                <Button
                    android:id="@+id/btn_open_dapp"
                    android:layout_width="wrap_content"
                    android:layout_height="44dp"
                    android:text="Open"
                    android:textColor="#050A08"
                    android:backgroundTint="#00FF88"
                    android:layout_marginStart="8dp" />
            </LinearLayout>

            <TextView
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="Quick Access"
                android:textSize="14sp"
                android:textColor="#8BA898"
                android:layout_marginTop="16dp"
                android:layout_marginBottom="8dp" />

            <GridLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:columnCount="3"
                android:rowCount="2">

                <Button
                    android:id="@+id/dapp_dex"
                    android:text="Swap"
                    android:textColor="#F0FDF4"
                    android:background="#0D1A14"
                    android:layout_margin="4dp"
                    android:layout_columnWeight="1"
                    android:minHeight="48dp" />
                <Button
                    android:id="@+id/dapp_ido"
                    android:text="Buy VRDX"
                    android:textColor="#F0FDF4"
                    android:background="#0D1A14"
                    android:layout_margin="4dp"
                    android:layout_columnWeight="1"
                    android:minHeight="48dp" />
                <Button
                    android:id="@+id/dapp_bridge"
                    android:text="Bridge"
                    android:textColor="#F0FDF4"
                    android:background="#0D1A14"
                    android:layout_margin="4dp"
                    android:layout_columnWeight="1"
                    android:minHeight="48dp" />
                <Button
                    android:id="@+id/dapp_explorer"
                    android:text="Explorer"
                    android:textColor="#F0FDF4"
                    android:background="#0D1A14"
                    android:layout_margin="4dp"
                    android:layout_columnWeight="1"
                    android:minHeight="48dp" />
                <Button
                    android:id="@+id/dapp_markets"
                    android:text="Markets"
                    android:textColor="#F0FDF4"
                    android:background="#0D1A14"
                    android:layout_margin="4dp"
                    android:layout_columnWeight="1"
                    android:minHeight="48dp" />
                <Button
                    android:id="@+id/dapp_eco"
                    android:text="Eco"
                    android:textColor="#F0FDF4"
                    android:background="#0D1A14"
                    android:layout_margin="4dp"
                    android:layout_columnWeight="1"
                    android:minHeight="48dp" />
            </GridLayout>
        </LinearLayout>

        <!-- Content: Deploy -->
        <LinearLayout
            android:id="@+id/content_deploy"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:padding="16dp"
            android:visibility="gone">

            <TextView
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="Deploy Smart Contract"
                android:textSize="16sp"
                android:textColor="#00FF88"
                android:textStyle="bold"
                android:layout_marginBottom="12dp" />

            <EditText
                android:id="@+id/et_contract_name"
                android:layout_width="match_parent"
                android:layout_height="44dp"
                android:hint="Contract Name"
                android:textColorHint="#547363"
                android:textColor="#F0FDF4"
                android:background="#0D1A14"
                android:padding="12dp"
                android:textSize="13sp"
                android:layout_marginBottom="8dp" />

            <EditText
                android:id="@+id/et_bytecode"
                android:layout_width="match_parent"
                android:layout_height="100dp"
                android:hint="Bytecode (EVM opcodes)"
                android:textColorHint="#547363"
                android:textColor="#F0FDF4"
                android:background="#0D1A14"
                android:padding="12dp"
                android:textSize="13sp"
                android:gravity="top"
                android:layout_marginBottom="8dp" />

            <Button
                android:id="@+id/btn_deploy"
                android:layout_width="match_parent"
                android:layout_height="44dp"
                android:text="Deploy Contract"
                android:textColor="#050A08"
                android:backgroundTint="#00FF88"
                android:layout_marginBottom="16dp" />

            <TextView
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="Quick Templates"
                android:textSize="14sp"
                android:textColor="#8BA898"
                android:layout_marginBottom="8dp" />

            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="horizontal">
                <Button
                    android:id="@+id/btn_template_token"
                    android:text="Token"
                    android:textColor="#F0FDF4"
                    android:background="#0D1A14"
                    android:layout_width="0dp"
                    android:layout_weight="1"
                    android:layout_height="44dp"
                    android:layout_margin="4dp" />
                <Button
                    android:id="@+id/btn_template_multisig"
                    android:text="MultiSig"
                    android:textColor="#F0FDF4"
                    android:background="#0D1A14"
                    android:layout_width="0dp"
                    android:layout_weight="1"
                    android:layout_height="44dp"
                    android:layout_margin="4dp" />
                <Button
                    android:id="@+id/btn_template_timelock"
                    android:text="TimeLock"
                    android:textColor="#F0FDF4"
                    android:background="#0D1A14"
                    android:layout_width="0dp"
                    android:layout_weight="1"
                    android:layout_height="44dp"
                    android:layout_margin="4dp" />
            </LinearLayout>
        </LinearLayout>

        <!-- Content: Contracts -->
        <LinearLayout
            android:id="@+id/content_contracts"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:padding="16dp"
            android:visibility="gone">

            <TextView
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="Deployed Contracts"
                android:textSize="16sp"
                android:textColor="#00FF88"
                android:textStyle="bold"
                android:layout_marginBottom="12dp" />

            <androidx.recyclerview.widget.RecyclerView
                android:id="@+id/rv_contracts"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:nestedScrollingEnabled="false" />
        </LinearLayout>

    </LinearLayout>
</ScrollView>
XML_EOF

echo "Layouts updated"
