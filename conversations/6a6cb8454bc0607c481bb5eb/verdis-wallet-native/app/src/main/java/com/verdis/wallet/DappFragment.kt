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
import android.widget.TextView
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.tabs.TabLayout
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class DappFragment : Fragment() {

    private lateinit var tabLayout: TabLayout
    private lateinit var contentDapps: View
    private lateinit var contentDeploy: View
    private lateinit var contentContracts: View

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val view = inflater.inflate(R.layout.fragment_dapp, container, false)

        tabLayout = view.findViewById(R.id.tab_layout)
        contentDapps = view.findViewById(R.id.content_dapps)
        contentDeploy = view.findViewById(R.id.content_deploy)
        contentContracts = view.findViewById(R.id.content_contracts)

        tabLayout.addOnTabSelectedListener(object : TabLayout.OnTabSelectedListener {
            override fun onTabSelected(tab: TabLayout.Tab) {
                contentDapps.visibility = if (tab.position == 0) View.VISIBLE else View.GONE
                contentDeploy.visibility = if (tab.position == 1) View.VISIBLE else View.GONE
                contentContracts.visibility = if (tab.position == 2) View.VISIBLE else View.GONE
                if (tab.position == 2) loadContracts()
            }
            override fun onTabUnselected(tab: TabLayout.Tab) {}
            override fun onTabReselected(tab: TabLayout.Tab) {}
        })

        // DApp buttons
        view.findViewById<View>(R.id.dapp_dex).setOnClickListener {
            (activity as? MainActivity)?.navigateTo(R.id.nav_swap)
        }
        view.findViewById<View>(R.id.dapp_ido).setOnClickListener {
            Toast.makeText(context, "Opening Token Sale...", Toast.LENGTH_SHORT).show()
        }
        view.findViewById<View>(R.id.dapp_bridge).setOnClickListener {
            Toast.makeText(context, "Opening Bridge...", Toast.LENGTH_SHORT).show()
        }
        view.findViewById<View>(R.id.dapp_explorer).setOnClickListener {
            Toast.makeText(context, "Opening Explorer...", Toast.LENGTH_SHORT).show()
        }
        view.findViewById<View>(R.id.dapp_markets).setOnClickListener {
            Toast.makeText(context, "Opening Markets...", Toast.LENGTH_SHORT).show()
        }
        view.findViewById<View>(R.id.dapp_eco).setOnClickListener {
            (activity as? MainActivity)?.navigateTo(R.id.nav_eco)
        }

        // Open DApp URL
        val etUrl = view.findViewById<EditText>(R.id.et_dapp_url)
        view.findViewById<Button>(R.id.btn_open_dapp).setOnClickListener {
            val url = etUrl.text.toString().trim()
            if (url.isNotEmpty()) {
                Toast.makeText(context, "Opening $url...", Toast.LENGTH_SHORT).show()
            }
        }

        // Deploy contract
        val etName = view.findViewById<EditText>(R.id.et_contract_name)
        val etBytecode = view.findViewById<EditText>(R.id.et_bytecode)
        view.findViewById<Button>(R.id.btn_deploy).setOnClickListener {
            val name = etName.text.toString().trim()
            val bytecode = etBytecode.text.toString().trim()
            if (name.isEmpty() || bytecode.isEmpty()) {
                Toast.makeText(context, "Fill in name and bytecode", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            deployContract(name, bytecode)
        }

        // Quick templates
        view.findViewById<Button>(R.id.btn_template_token).setOnClickListener {
            etName.setText("CustomToken")
            etBytecode.setText("PUSH1 0x60 PUSH1 0x40 MSTORE CALLDATASIZE")
        }
        view.findViewById<Button>(R.id.btn_template_multisig).setOnClickListener {
            etName.setText("MultiSigWallet")
            etBytecode.setText("PUSH1 0x02 PUSH1 0x00 SSTORE PUSH1 0x02 PUSH1 0x01 SSTORE")
        }
        view.findViewById<Button>(R.id.btn_template_timelock).setOnClickListener {
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
            holder.itemView.findViewById<TextView>(R.id.tv_credit_verified).text = c.address.take(12) + "..."
            holder.itemView.findViewById<TextView>(R.id.tv_credit_project).text = c.owner.take(8)
        }

        override fun getItemCount() = contracts.size
    }
}
