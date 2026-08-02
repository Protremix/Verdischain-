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
        tvAddr = v.findViewById(R.id.tv_address); tvBal = v.findViewById(R.id.tv_total_balance)
        tvUsd = v.findViewById(R.id.tv_balance_usd); tvChange = v.findViewById(R.id.tv_change_24h)
        tvBlock = v.findViewById(R.id.tv_block_height); tvVals = v.findViewById(R.id.tv_validators)
        rvTx = v.findViewById(R.id.rv_transactions); swipe = v.findViewById(R.id.swipe_refresh)
        tvNoTx = v.findViewById(R.id.tv_no_transactions)
        rvTx?.layoutManager = LinearLayoutManager(context); rvTx?.isNestedScrollingEnabled = false
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
    override fun onDestroyView() { super.onDestroyView(); tvAddr=null; tvBal=null; tvUsd=null; tvChange=null; tvBlock=null; tvVals=null; rvTx=null; swipe=null; tvNoTx=null; fullAddress="" }
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
                    val adapter = TxAdapter(txs.take(20), w.address)
                    rvTx?.adapter = adapter
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
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int) = VH(LayoutInflater.from(parent.context).inflate(R.layout.item_tx, parent, false))
    override fun onBindViewHolder(h: VH, pos: Int) {
        val tx = items[pos]
        val from = tx["from"]?.toString() ?: ""
        val to = tx["to"]?.toString() ?: ""
        val isOut = from.equals(myAddr, ignoreCase = true)
        h.type.text = if (isOut) "↑" else "↓"
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
