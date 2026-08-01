package com.verdis.wallet

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
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class EcoFragment : Fragment() {

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val view = inflater.inflate(R.layout.fragment_eco, container, false)

        val tvCo2 = view.findViewById<TextView>(R.id.tv_co2)
        val tvTrees = view.findViewById<TextView>(R.id.tv_trees)
        val tvCredits = view.findViewById<TextView>(R.id.tv_credits)
        val tvGreenScore = view.findViewById<TextView>(R.id.tv_green_score)
        val rvCredits = view.findViewById<RecyclerView>(R.id.rv_credits)
        val rvProjects = view.findViewById<RecyclerView>(R.id.rv_projects)
        val swipeRefresh = view.findViewById<SwipeRefreshLayout>(R.id.swipe_refresh)

        rvCredits.layoutManager = LinearLayoutManager(context)
        rvCredits.isNestedScrollingEnabled = false
        rvProjects.layoutManager = LinearLayoutManager(context)
        rvProjects.isNestedScrollingEnabled = false

        swipeRefresh.setOnRefreshListener { loadData() }
        loadData()

        fun loadData() {
            lifecycleScope.launch {
                try {
                    val impact = withContext(Dispatchers.IO) { VerdisApi.getEcoImpact() }
                    if (impact != null) {
                        tvCo2.text = "${String.format("%.0f", impact.co2Offset)} tons"
                        tvTrees.text = "${impact.treesPlanted}"
                        tvCredits.text = "${impact.carbonCredits}"
                        tvGreenScore.text = "${impact.greenScore}"
                    }

                    val credits = withContext(Dispatchers.IO) { VerdisApi.getCarbonCredits() }
                    if (credits != null) {
                        rvCredits.adapter = CreditAdapter(credits)
                    }

                    val projects = withContext(Dispatchers.IO) { VerdisApi.getReforestProjects() }
                    if (projects != null) {
                        rvProjects.adapter = ProjectAdapter(projects)
                    }
                } catch (e: Exception) {
                    Toast.makeText(context, "Connection error", Toast.LENGTH_SHORT).show()
                } finally {
                    swipeRefresh.isRefreshing = false
                }
            }
        }

        loadData()
        return view
    }

    class CreditAdapter(private val credits: List<VerdisApi.CarbonCredit>) :
        RecyclerView.Adapter<CreditAdapter.VH>() {
        class VH(view: View) : RecyclerView.ViewHolder(view) {
            val id: TextView = view.findViewById(R.id.tv_credit_id)
            val amount: TextView = view.findViewById(R.id.tv_credit_amount)
            val verified: TextView = view.findViewById(R.id.tv_credit_verified)
            val project: TextView = view.findViewById(R.id.tv_credit_project)
        }

        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int) =
            VH(LayoutInflater.from(parent.context).inflate(R.layout.item_credit, parent, false))

        override fun onBindViewHolder(holder: VH, position: Int) {
            val c = credits[position]
            holder.id.text = "#${c.id}"
            holder.amount.text = "${String.format("%.2f", c.amount)} tons CO₂"
            holder.verified.text = if (c.verified) "✓ Verified" else "Pending"
            holder.verified.setTextColor(if (c.verified) 0xFF00FF88.toInt() else 0xFFFF5F5F.toInt())
            holder.project.text = c.project ?: "Unknown"
        }

        override fun getItemCount() = credits.size
    }

    class ProjectAdapter(private val projects: List<VerdisApi.ReforestProject>) :
        RecyclerView.Adapter<ProjectAdapter.VH>() {
        class VH(view: View) : RecyclerView.ViewHolder(view) {
            val id: TextView = view.findViewById(R.id.tv_credit_id)
            val amount: TextView = view.findViewById(R.id.tv_credit_amount)
            val verified: TextView = view.findViewById(R.id.tv_credit_verified)
            val project: TextView = view.findViewById(R.id.tv_credit_project)
        }

        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int) =
            VH(LayoutInflater.from(parent.context).inflate(R.layout.item_credit, parent, false))

        override fun onBindViewHolder(holder: VH, position: Int) {
            val p = projects[position]
            holder.id.text = "#${p.id}"
            holder.amount.text = "${p.treesPlanted} trees"
            holder.verified.text = if (p.verified) "✓ Verified" else "Pending"
            holder.verified.setTextColor(if (p.verified) 0xFF00FF88.toInt() else 0xFFFF5F5F.toInt())
            holder.project.text = p.location ?: "Unknown"
        }

        override fun getItemCount() = projects.size
    }
}
