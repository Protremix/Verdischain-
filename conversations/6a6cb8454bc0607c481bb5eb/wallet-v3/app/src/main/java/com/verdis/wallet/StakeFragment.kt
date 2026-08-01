package com.verdis.wallet

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
import kotlinx.coroutines.launch

class StakeFragment : Fragment() {
    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        val v = inflater.inflate(R.layout.fragment_stake, container, false)
        val etAmount = v.findViewById<EditText>(R.id.et_stake_amount)
        val btnStake = v.findViewById<Button>(R.id.btn_stake)
        val btnUnstake = v.findViewById<Button>(R.id.btn_unstake)
        val tvResult = v.findViewById<TextView>(R.id.tv_stake_result)
        val tvInfo = v.findViewById<TextView>(R.id.tv_stake_info)

        lifecycleScope.launch {
            try {
                val info = VerdisApi.getBlockchainInfo()
                val vals = VerdisApi.getValidators()
                val activeVals = vals.count { it["isProducer"] == true }
                tvInfo?.text = "Active Validators: $activeVals\nStaking APY: 18%\nMin Stake: 1 VRDX"
            } catch (e: Exception) {
                tvInfo?.text = "Staking APY: 18%\nMin Stake: 1 VRDX"
            }
        }

        btnStake.setOnClickListener {
            val amountStr = etAmount.text.toString().trim()
            val amount = amountStr.toDoubleOrNull()
            if (amount == null || amount <= 0) {
                Toast.makeText(context, "Invalid amount", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            btnStake.isEnabled = false
            tvResult.text = "Staking $amount VRDX..."
            lifecycleScope.launch {
                val ctx = context ?: return@launch
                val w = WalletManager.loadWallet(ctx)
                if (w == null) { tvResult.text = "No wallet"; btnStake.isEnabled = true; return@launch }
                val success = VerdisApi.stake(w.address, amount)
                btnStake.isEnabled = true
                if (success) {
                    tvResult.text = "✅ Staked $amount VRDX"
                    etAmount.text.clear()
                } else {
                    tvResult.text = "❌ Staking failed"
                }
            }
        }

        btnUnstake.setOnClickListener {
            val amountStr = etAmount.text.toString().trim()
            val amount = amountStr.toDoubleOrNull()
            if (amount == null || amount <= 0) {
                Toast.makeText(context, "Invalid amount", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            btnUnstake.isEnabled = false
            tvResult.text = "Unstaking $amount VRDX..."
            lifecycleScope.launch {
                val ctx = context ?: return@launch
                val w = WalletManager.loadWallet(ctx)
                if (w == null) { tvResult.text = "No wallet"; btnUnstake.isEnabled = true; return@launch }
                val success = VerdisApi.unstake(w.address, amount)
                btnUnstake.isEnabled = true
                if (success) {
                    tvResult.text = "✅ Unstaked $amount VRDX"
                    etAmount.text.clear()
                } else {
                    tvResult.text = "❌ Unstaking failed"
                }
            }
        }
        return v
    }
}
