#!/usr/bin/bash
# Fix Android wallet bugs and rebuild APK

echo "=== 1. FIX HomeFragment.kt ==="
cat > /opt/verdis-wallet-native/app/src/main/java/com/verdis/wallet/HomeFragment.kt << 'KOTLINEOF'
package com.verdis.wallet

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

class HomeFragment : Fragment() {
    private var tvAddr: TextView? = null
    private var fullAddress: String = ""
    private var tvBal: TextView? = null
    private var tvUsd: TextView? = null
    private var tvChange: TextView? = null
    private var tvBlock: TextView? = null
    private var tvVals: TextView? = null
    private var rvTx: RecyclerView? = null
    private var swipe: SwipeRefreshLayout? = null
    private var tvNoTx: TextView? = null

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        val v = inflater.inflate(R.layout.fragment_home, container, false)
        tvAddr = v.findViewById(R.id.tv_address)
        tvBal = v.findViewById(R.id.tv_total_balance)
        tvUsd = v.findViewById(R.id.tv_balance_usd)
        tvChange = v.findViewById(R.id.tv_change_24h)
        tvBlock = v.findViewById(R.id.tv_block_height)
        tvVals = v.findViewById(R.id.tv_validators)
        rvTx = v.findViewById(R.id.rv_transactions)
        swipe = v.findViewById(R.id.swipe_refresh)
        tvNoTx = v.findViewById(R.id.tv_no_transactions)
        rvTx?.layoutManager = LinearLayoutManager(context)
        rvTx?.isNestedScrollingEnabled = false
        v.findViewById<View>(R.id.btn_send).setOnClickListener { (activity as? MainActivity)?.load(SendFragment()) }
        v.findViewById<View>(R.id.btn_receive).setOnClickListener { (activity as? MainActivity)?.showReceive() }
        v.findViewById<View>(R.id.btn_swap).setOnClickListener { (activity as? MainActivity)?.navigateTo(R.id.nav_swap) }
        v.findViewById<View>(R.id.btn_stake).setOnClickListener { (activity as? MainActivity)?.navigateTo(R.id.nav_stake) }
        tvAddr?.setOnClickListener {
            if (fullAddress.isEmpty()) return@setOnClickListener
            (requireContext().getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager).setPrimaryClip(ClipData.newPlainText("addr", fullAddress))
            Toast.makeText(context, "Address copied!", Toast.LENGTH_SHORT).show()
        }
        swipe?.setOnRefreshListener { load() }
        load()
        return v
    }

    override fun onDestroyView() {
        super.onDestroyView()
        tvAddr = null; tvBal = null; tvUsd = null; tvChange = null
        tvBlock = null; tvVals = null; rvTx = null; swipe = null; tvNoTx = null; fullAddress = ""
    }

    private fun load() {
        if (!isAdded) return
        lifecycleScope.launch {
            val ctx = context ?: return@launch
            val w = WalletManager.loadWallet(ctx)
            if (w == null) { if (isAdded) (activity as? MainActivity)?.showOnboarding(); return@launch }
            fullAddress = w.address
            tvAddr?.text = "${w.address.take(10)}...${w.address.takeLast(6)}"
            try {
                val bal = VerdisApi.getBalance(w.address)
                tvBal?.text = "%.2f VRDX".format(bal)
                tvUsd?.text = "$%.2f".format(bal * 0.0005)
                tvChange?.text = "+0%"
            } catch (e: Exception) {}
            try {
                val info = VerdisApi.getBlockchainInfo()
                tvBlock?.text = (info["height"] ?: 0).toString()
                tvVals?.text = (info["validatorCount"] ?: 0).toString()
            } catch (e: Exception) {}
            try {
                val txs = VerdisApi.getTransactions(w.address)
                if (txs.isNotEmpty()) {
                    tvNoTx?.visibility = View.GONE
                    rvTx?.visibility = View.VISIBLE
                    rvTx?.adapter = TxAdapter(txs.take(20), w.address)
                } else {
                    tvNoTx?.visibility = View.VISIBLE
                    rvTx?.visibility = View.GONE
                    tvNoTx?.text = "No transactions yet"
                }
            } catch (e: Exception) {
                tvNoTx?.visibility = View.VISIBLE
                rvTx?.visibility = View.GONE
                tvNoTx?.text = "Unable to load transactions"
            }
            swipe?.isRefreshing = false
        }
    }
}

class TxAdapter(private val items: List<Map<String, Any?>>, private val myAddr: String) : RecyclerView.Adapter<TxAdapter.VH>() {
    class VH(v: View) : RecyclerView.ViewHolder(v) {
        val type: TextView = v.findViewById(R.id.tv_tx_type)
        val addr: TextView = v.findViewById(R.id.tv_tx_address)
        val time: TextView = v.findViewById(R.id.tv_tx_time)
        val amt: TextView = v.findViewById(R.id.tv_tx_amount)
    }
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int) =
        VH(LayoutInflater.from(parent.context).inflate(R.layout.item_tx, parent, false))
    override fun onBindViewHolder(h: VH, pos: Int) {
        val tx = items[pos]
        val from = tx["from"]?.toString() ?: ""
        val to = tx["to"]?.toString() ?: ""
        val isOut = from.equals(myAddr, ignoreCase = true)
        h.type.text = if (isOut) "Out" else "In"
        h.addr.text = (if (isOut) to else from).take(16) + "..."
        val ts = tx["timestamp"]?.toString()?.toLongOrNull() ?: 0L
        h.time.text = if (ts > 0) {
            val fmt = SimpleDateFormat("MMM dd, HH:mm", Locale.getDefault())
            fmt.format(Date(ts))
        } else ""
        val amount = tx["amount"]?.toString()?.toDoubleOrNull() ?: 0.0
        h.amt.text = "%.2f VRDX".format(amount)
        h.amt.setTextColor(if (isOut) 0xFFEF4444.toInt() else 0xFF10B981.toInt())
    }
    override fun getItemCount() = items.size
}
KOTLINEOF
echo "  HomeFragment.kt updated"

echo "=== 2. FIX StakeFragment.kt (VRS -> VRDX, show green score) ==="
cat > /opt/verdis-wallet-native/app/src/main/java/com/verdis/wallet/StakeFragment.kt << 'KOTLINEOF'
package com.verdis.wallet

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import android.widget.EditText
import android.widget.Button
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import kotlinx.coroutines.launch

class StakeFragment : Fragment() {
    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        val v = inflater.inflate(R.layout.fragment_stake, container, false)
        val rv = v.findViewById<RecyclerView>(R.id.rv_validators)
        rv?.layoutManager = LinearLayoutManager(context)
        rv?.isNestedScrollingEnabled = false
        lifecycleScope.launch {
            val vals = VerdisApi.getValidators()
            if (vals.isNotEmpty()) rv?.adapter = ValAdapter(vals)
        }
        v.findViewById<Button>(R.id.btn_stake).setOnClickListener {
            val ctx = context ?: return@setOnClickListener
            val w = WalletManager.loadWallet(ctx) ?: return@setOnClickListener
            val amt = v.findViewById<EditText>(R.id.et_amount).text?.toString()?.trim()?.toDoubleOrNull()
            if (amt == null || amt <= 0) { Toast.makeText(ctx, "Enter amount", Toast.LENGTH_SHORT).show(); return@setOnClickListener }
            lifecycleScope.launch { Toast.makeText(ctx, if (VerdisApi.stake(w.address, amt)) "Staked OK" else "Failed", Toast.LENGTH_SHORT).show() }
        }
        v.findViewById<Button>(R.id.btn_unstake).setOnClickListener {
            val ctx = context ?: return@setOnClickListener
            val w = WalletManager.loadWallet(ctx) ?: return@setOnClickListener
            val amt = v.findViewById<EditText>(R.id.et_amount).text?.toString()?.trim()?.toDoubleOrNull()
            if (amt == null || amt <= 0) { Toast.makeText(ctx, "Enter amount", Toast.LENGTH_SHORT).show(); return@setOnClickListener }
            lifecycleScope.launch { Toast.makeText(ctx, if (VerdisApi.unstake(w.address, amt)) "Unstaked OK" else "Failed", Toast.LENGTH_SHORT).show() }
        }
        return v
    }
}

class ValAdapter(private val items: List<Map<String, Any?>>) : RecyclerView.Adapter<ValAdapter.VH>() {
    class VH(v: View) : RecyclerView.ViewHolder(v) {
        val addr: TextView = v.findViewById(R.id.tv_val_address)
        val blk: TextView = v.findViewById(R.id.tv_val_blocks)
        val rwd: TextView = v.findViewById(R.id.tv_val_rewards)
    }
    override fun onCreateViewHolder(p: ViewGroup, t: Int) =
        VH(LayoutInflater.from(p.context).inflate(R.layout.item_validator, p, false))
    override fun onBindViewHolder(h: VH, p: Int) {
        val v = items[p]
        h.addr.text = (v["address"]?.toString() ?: "?").take(16) + "..."
        h.blk.text = "${v["blocksProduced"] ?: 0} blocks"
        val greenScore = v["greenScore"]?.toString()?.toIntOrNull() ?: 0
        val energy = v["energySource"]?.toString() ?: ""
        val rewards = v["totalRewards"]?.toString()?.toDoubleOrNull() ?: 0.0
        h.rwd.text = "%.0f VRDX".format(rewards) + if (greenScore > 0) " | Green: $greenScore ($energy)" else ""
    }
    override fun getItemCount() = items.size
}
KOTLINEOF
echo "  StakeFragment.kt updated"

echo "=== 3. ADD tv_no_transactions to fragment_home.xml ==="
# Check if the view exists, if not add it
if ! grep -q "tv_no_transactions" /opt/verdis-wallet-native/app/src/main/res/layout/fragment_home.xml; then
    # Insert before the closing tag of the SwipeRefreshLayout or the transactions RecyclerView
    sed -i '/rv_transactions/i\
        <TextView\
            android:id="@+id/tv_no_transactions"\
            android:layout_width="match_parent"\
            android:layout_height="wrap_content"\
            android:text="No transactions yet"\
            android:textColor="#888888"\
            android:textSize="13sp"\
            android:gravity="center"\
            android:padding="16dp"\
            android:visibility="gone" />' /opt/verdis-wallet-native/app/src/main/res/layout/fragment_home.xml
    echo "  tv_no_transactions added to layout"
else
    echo "  tv_no_transactions already in layout"
fi

echo "=== 4. FIX SendFragment.kt (VRDX label) ==="
# Just need to make sure toast messages are clear
# The send function itself is already correct (no 1e9 multiplier)

echo "=== 5. UPDATE VERSION ==="
# Update version code in build.gradle
sed -i 's/versionCode [0-9]*/versionCode 4/' /opt/verdis-wallet-native/app/build.gradle
sed -i 's/versionName "[^"]*"/versionName "2.4.0"/' /opt/verdis-wallet-native/app/build.gradle
echo "  Version updated to 2.4.0"

echo "=== 6. BUILD APK ==="
cd /opt/verdis-wallet-native
export ANDROID_HOME=/opt/android-sdk
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk
./gradlew assembleDebug --no-daemon -q 2>&1 | tail -20

echo ""
echo "=== BUILD RESULT ==="
APK=$(find /opt/verdis-wallet-native -name "app-debug.apk" -newer /opt/verdis-wallet-native/app/build.gradle 2>/dev/null | head -1)
if [ -n "$APK" ]; then
    cp "$APK" /opt/verdis/app/dist/web/verdis-wallet.apk
    cp "$APK" /opt/verdis/app/dist/web/verdis-wallet-v2.4.0.apk
    ls -la /opt/verdis/app/dist/web/verdis-wallet*.apk
    echo "APK BUILD SUCCESS"
else
    echo "APK BUILD FAILED - checking for errors"
    find /opt/verdis-wallet-native -name "app-debug.apk" 2>/dev/null
fi
