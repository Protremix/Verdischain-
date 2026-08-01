package com.verdis.wallet

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
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

class StakeFragment : Fragment() {

    private lateinit var rvValidators: RecyclerView
    private lateinit var tvYourStake: TextView
    private lateinit var tvRewards: TextView
    private lateinit var btnClaim: Button
    private lateinit var swipeRefresh: SwipeRefreshLayout

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val view = inflater.inflate(R.layout.fragment_stake, container, false)

        rvValidators = view.findViewById(R.id.rv_validators)
        tvYourStake = view.findViewById(R.id.tv_your_stake)
        tvRewards = view.findViewById(R.id.tv_rewards)
        btnClaim = view.findViewById(R.id.btn_claim_rewards)
        swipeRefresh = view.findViewById(R.id.swipe_refresh)

        rvValidators.layoutManager = LinearLayoutManager(context)
        rvValidators.isNestedScrollingEnabled = false

        swipeRefresh.setOnRefreshListener { loadData() }

        btnClaim.setOnClickListener {
            Toast.makeText(context, "Claiming rewards...", Toast.LENGTH_SHORT).show()
        }

        loadData()
        return view
    }

    private fun loadData() {
        lifecycleScope.launch {
            val wallet = WalletManager.loadWallet(requireContext())
            try {
                val validators = withContext(Dispatchers.IO) { VerdisApi.getValidators() }
                if (validators != null) {
                    rvValidators.adapter = ValidatorAdapter(validators, wallet?.address ?: "")
                }

                if (wallet != null) {
                    val details = withContext(Dispatchers.IO) { VerdisApi.getWalletDetails(wallet.address) }
                    val staked = (details?.staked ?: 0.0) / 1_000_000_000_000_000_000.0
                    tvYourStake.text = "${String.format("%.4f", staked)} VCO"
                    tvRewards.text = "${String.format("%.4f", staked * 0.05)} VCO" // 5% APY estimate
                }
            } catch (e: Exception) {
                Toast.makeText(context, "Connection error", Toast.LENGTH_SHORT).show()
            } finally {
                swipeRefresh.isRefreshing = false
            }
        }
    }

    class ValidatorAdapter(
        private val validators: List<Validator>,
        private val walletAddress: String
    ) : RecyclerView.Adapter<ValidatorAdapter.VH>() {
        class VH(view: View) : RecyclerView.ViewHolder(view) {
            val initial: TextView = view.findViewById(R.id.tv_validator_initial)
            val address: TextView = view.findViewById(R.id.tv_validator_address)
            val stake: TextView = view.findViewById(R.id.tv_validator_stake)
            val votes: TextView = view.findViewById(R.id.tv_validator_votes)
            val greenScore: TextView = view.findViewById(R.id.tv_green_score)
            val status: TextView = view.findViewById(R.id.tv_validator_status)
            val btnStake: Button = view.findViewById(R.id.btn_stake_validator)
        }

        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int) =
            VH(LayoutInflater.from(parent.context).inflate(R.layout.item_validator, parent, false))

        override fun onBindViewHolder(holder: VH, position: Int) {
            val v = validators[position]
            holder.initial.text = v.address.firstOrNull()?.toString() ?: "V"
            holder.address.text = "${v.address.take(10)}...${v.address.takeLast(6)}"
            holder.stake.text = "${String.format("%.0f", v.totalRewards)} VCO"
            holder.votes.text = "${v.votes} votes"
            holder.greenScore.text = v.greenScore.toString()
            holder.status.text = if (v.active) "Active" else "Inactive"
            holder.status.setTextColor(if (v.active) 0xFF00FF88.toInt() else 0xFF547363.toInt())

            holder.btnStake.setOnClickListener {
                Toast.makeText(it.context, "Staking to ${v.address.take(10)}...", Toast.LENGTH_SHORT).show()
            }
        }

        override fun getItemCount() = validators.size
    }
}
