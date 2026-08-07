import os

part2 = """
  <!-- MAIN CONTENT AREA (Light background) -->
  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 w-full flex-1">

    <!-- OVERVIEW TAB CONTENT -->
    <div id="tab-content-overview" class="tab-pane space-y-6">
      
      <!-- 2-Column Section: Blocks (60%) & Extrinsics (40%) -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        <!-- Left 60%: Latest Blocks -->
        <div class="lg:col-span-7 bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
          <div class="p-4 sm:p-5 border-b border-slate-100 flex items-center justify-between">
            <div class="flex items-center gap-2">
              <div class="bg-slate-100 text-slate-700 p-1.5 rounded-lg">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/></svg>
              </div>
              <h2 class="font-heading font-bold text-base text-slate-900">Latest Blocks</h2>
            </div>
            <button onclick="switchTab('blocks')" class="text-xs font-semibold text-slate-600 hover:text-[#0f172a] bg-slate-100 hover:bg-slate-200 px-3 py-1.5 rounded-lg transition-colors">
              View All Blocks &rarr;
            </button>
          </div>

          <div class="overflow-x-auto">
            <table class="w-full text-left text-xs">
              <thead class="bg-slate-50 text-slate-500 uppercase tracking-wider font-semibold border-b border-slate-100">
                <tr>
                  <th class="py-3 px-4">Block #</th>
                  <th class="py-3 px-4">Age</th>
                  <th class="py-3 px-4 text-center">Extrinsics</th>
                  <th class="py-3 px-4">Proposer</th>
                  <th class="py-3 px-4">Block Hash</th>
                </tr>
              </thead>
              <tbody id="overview-blocks-tbody" class="divide-y divide-slate-100">
                <tr>
                  <td colspan="5" class="py-8 text-center text-slate-400 font-mono">Loading live blocks...</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Right 40%: Latest Extrinsics -->
        <div class="lg:col-span-5 bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
          <div class="p-4 sm:p-5 border-b border-slate-100 flex items-center justify-between">
            <div class="flex items-center gap-2">
              <div class="bg-slate-100 text-slate-700 p-1.5 rounded-lg">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
              </div>
              <h2 class="font-heading font-bold text-base text-slate-900">Latest Extrinsics</h2>
            </div>
            <button onclick="switchTab('extrinsics')" class="text-xs font-semibold text-slate-600 hover:text-[#0f172a] bg-slate-100 hover:bg-slate-200 px-3 py-1.5 rounded-lg transition-colors">
              View All &rarr;
            </button>
          </div>

          <div class="overflow-x-auto">
            <table class="w-full text-left text-xs">
              <thead class="bg-slate-50 text-slate-500 uppercase tracking-wider font-semibold border-b border-slate-100">
                <tr>
                  <th class="py-3 px-4">Hash</th>
                  <th class="py-3 px-4">Method</th>
                  <th class="py-3 px-4 text-right">Block</th>
                </tr>
              </thead>
              <tbody id="overview-extrinsics-tbody" class="divide-y divide-slate-100">
                <tr>
                  <td colspan="3" class="py-8 text-center text-slate-400 font-mono">Loading extrinsics...</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

      </div>

      <!-- Eco Layer Metrics Bar -->
      <div class="bg-gradient-to-r from-emerald-900 to-slate-900 text-white rounded-2xl p-5 sm:p-6 shadow-md border border-emerald-800/50">
        <div class="flex items-center justify-between mb-4 border-b border-emerald-800/60 pb-3">
          <div class="flex items-center gap-2.5">
            <div class="bg-[#caff33] text-[#0f172a] p-1.5 rounded-lg font-bold">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"/></svg>
            </div>
            <div>
              <h3 class="font-heading font-bold text-lg text-white">Verdis Eco Layer Live Impact</h3>
              <p class="text-xs text-emerald-300">On-chain carbon credit tracking & green validator consensus</p>
            </div>
          </div>
          <button onclick="switchTab('eco')" class="text-xs font-semibold bg-[#caff33] text-[#0f172a] hover:bg-[#bbf82e] px-3.5 py-1.5 rounded-lg transition-colors">
            Eco Dashboard &rarr;
          </button>
        </div>

        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="bg-slate-900/60 p-3.5 rounded-xl border border-emerald-800/40">
            <div class="text-xs text-emerald-300 font-medium">Total CO2 Offset</div>
            <div id="eco-bar-co2" class="font-mono font-bold text-lg text-[#caff33] mt-1">0 kg</div>
            <div class="text-[11px] text-slate-400 mt-0.5">Verified on-chain</div>
          </div>
          <div class="bg-slate-900/60 p-3.5 rounded-xl border border-emerald-800/40">
            <div class="text-xs text-emerald-300 font-medium">Trees Planted</div>
            <div id="eco-bar-trees" class="font-mono font-bold text-lg text-white mt-1">0 Trees</div>
            <div class="text-[11px] text-slate-400 mt-0.5">Reforestation projects</div>
          </div>
          <div class="bg-slate-900/60 p-3.5 rounded-xl border border-emerald-800/40">
            <div class="text-xs text-emerald-300 font-medium">Carbon Credits Issued</div>
            <div id="eco-bar-credits" class="font-mono font-bold text-lg text-white mt-1">0 Credits</div>
            <div class="text-[11px] text-slate-400 mt-0.5">Eco Pallet Registry</div>
          </div>
          <div class="bg-slate-900/60 p-3.5 rounded-xl border border-emerald-800/40">
            <div class="text-xs text-emerald-300 font-medium">Green Validators</div>
            <div id="eco-bar-green-vals" class="font-mono font-bold text-lg text-emerald-400 mt-1">0 Certified</div>
            <div class="text-[11px] text-slate-400 mt-0.5">Renewable powered</div>
          </div>
        </div>
      </div>

      <!-- DEX Pools Summary Section -->
      <div class="bg-white rounded-2xl shadow-sm border border-slate-200 p-5 sm:p-6">
        <div class="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
          <div class="flex items-center gap-2">
            <div class="bg-indigo-50 text-indigo-600 p-1.5 rounded-lg">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"/></svg>
            </div>
            <div>
              <h3 class="font-heading font-bold text-base text-slate-900">AMM DEX Top Liquidity Pools</h3>
              <p class="text-xs text-slate-500">Live decentralized exchange pools on Verdis Chain</p>
            </div>
          </div>
          <button onclick="switchTab('dex')" class="text-xs font-semibold text-slate-600 hover:text-[#0f172a] bg-slate-100 hover:bg-slate-200 px-3 py-1.5 rounded-lg transition-colors">
            All DEX Pools &rarr;
          </button>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs">
            <thead class="bg-slate-50 text-slate-500 uppercase tracking-wider font-semibold border-b border-slate-100">
              <tr>
                <th class="py-3 px-4">Pool ID</th>
                <th class="py-3 px-4">Token Pair</th>
                <th class="py-3 px-4 text-right">Reserve Token A</th>
                <th class="py-3 px-4 text-right">Reserve Token B</th>
                <th class="py-3 px-4 text-right">Total LP</th>
                <th class="py-3 px-4 text-right">Fee Rate</th>
                <th class="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody id="overview-dex-tbody" class="divide-y divide-slate-100">
              <tr>
                <td colspan="7" class="py-6 text-center text-slate-400 font-mono">Loading DEX pools...</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </div>

    <!-- BLOCKS TAB CONTENT -->
    <div id="tab-content-blocks" class="tab-pane hidden space-y-4">
      <div class="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
        
        <div class="p-4 sm:p-5 border-b border-slate-100 flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 class="font-heading font-bold text-lg text-slate-900">Block Explorer</h2>
            <p class="text-xs text-slate-500">All mined Substrate blocks on Verdis Chain</p>
          </div>
          <div class="flex items-center gap-2">
            <button onclick="loadRecentBlocks()" class="bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold px-3 py-1.5 rounded-lg transition-colors flex items-center gap-1">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
              Refresh
            </button>
          </div>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs">
            <thead class="bg-slate-50 text-slate-500 uppercase tracking-wider font-semibold border-b border-slate-100">
              <tr>
                <th class="py-3.5 px-4">Block #</th>
                <th class="py-3.5 px-4">Age</th>
                <th class="py-3.5 px-4 text-center">Extrinsics</th>
                <th class="py-3.5 px-4">Proposer / Validator</th>
                <th class="py-3.5 px-4">State Root</th>
                <th class="py-3.5 px-4">Block Hash</th>
                <th class="py-3.5 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody id="blocks-tbody" class="divide-y divide-slate-100">
              <tr>
                <td colspan="7" class="py-12 text-center text-slate-400 font-mono">Loading block history...</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination Bar -->
        <div class="p-4 bg-slate-50 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
          <span id="blocks-page-info">Showing recent blocks</span>
          <div class="flex items-center gap-2">
            <button onclick="loadMoreBlocks()" class="bg-white hover:bg-slate-100 border border-slate-200 text-slate-700 font-semibold px-3.5 py-1.5 rounded-lg transition-colors shadow-sm">
              Load Older Blocks
            </button>
          </div>
        </div>

      </div>
    </div>

    <!-- EXTRINSICS TAB CONTENT -->
    <div id="tab-content-extrinsics" class="tab-pane hidden space-y-4">
      <div class="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
        
        <div class="p-4 sm:p-5 border-b border-slate-100 flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 class="font-heading font-bold text-lg text-slate-900">Extrinsics & Transactions</h2>
            <p class="text-xs text-slate-500">Decoded SCALE extrinsic calls executed on Verdis Chain</p>
          </div>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs">
            <thead class="bg-slate-50 text-slate-500 uppercase tracking-wider font-semibold border-b border-slate-100">
              <tr>
                <th class="py-3.5 px-4">Extrinsic Hash</th>
                <th class="py-3.5 px-4">Block #</th>
                <th class="py-3.5 px-4">Sender</th>
                <th class="py-3.5 px-4">Method / Call</th>
                <th class="py-3.5 px-4">Status</th>
                <th class="py-3.5 px-4 text-right">Details</th>
              </tr>
            </thead>
            <tbody id="extrinsics-tbody" class="divide-y divide-slate-100">
              <tr>
                <td colspan="6" class="py-12 text-center text-slate-400 font-mono">Loading extrinsics...</td>
              </tr>
            </tbody>
          </table>
        </div>

      </div>
    </div>

    <!-- VALIDATORS TAB CONTENT -->
    <div id="tab-content-validators" class="tab-pane hidden space-y-6">
      
      <!-- Validators Summary Bar -->
      <div class="bg-white rounded-2xl shadow-sm border border-slate-200 p-5 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div>
          <span class="text-xs text-slate-500 font-medium">Active Validators</span>
          <div id="val-summary-active" class="font-mono font-bold text-xl text-slate-900 mt-1">0</div>
        </div>
        <div>
          <span class="text-xs text-slate-500 font-medium">Total Registered</span>
          <div id="val-summary-total" class="font-mono font-bold text-xl text-slate-900 mt-1">0</div>
        </div>
        <div>
          <span class="text-xs text-slate-500 font-medium">Current Epoch</span>
          <div id="val-summary-epoch" class="font-mono font-bold text-xl text-slate-900 mt-1">#1</div>
        </div>
        <div>
          <span class="text-xs text-slate-500 font-medium">Green Certified</span>
          <div id="val-summary-green" class="font-mono font-bold text-xl text-emerald-600 mt-1">0</div>
        </div>
      </div>

      <!-- Validators List -->
      <div class="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
        <div class="p-4 sm:p-5 border-b border-slate-100 flex items-center justify-between">
          <h2 class="font-heading font-bold text-lg text-slate-900">DPoS Validator Set</h2>
          <span class="text-xs text-slate-500 font-mono">Consensus: BABE + GRANDPA</span>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs">
            <thead class="bg-slate-50 text-slate-500 uppercase tracking-wider font-semibold border-b border-slate-100">
              <tr>
                <th class="py-3.5 px-4">Validator Address</th>
                <th class="py-3.5 px-4 text-right">Self Stake (VRDX)</th>
                <th class="py-3.5 px-4 text-center">Status</th>
                <th class="py-3.5 px-4 text-center">Eco Badge</th>
                <th class="py-3.5 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody id="validators-tbody" class="divide-y divide-slate-100">
              <tr>
                <td colspan="5" class="py-12 text-center text-slate-400 font-mono">Loading validators...</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </div>

    <!-- DEX TAB CONTENT -->
    <div id="tab-content-dex" class="tab-pane hidden space-y-6">
      
      <!-- DEX Stats Header -->
      <div class="bg-white rounded-2xl shadow-sm border border-slate-200 p-5 grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div>
          <span class="text-xs text-slate-500 font-medium">Active AMM Pools</span>
          <div id="dex-total-pools" class="font-mono font-bold text-xl text-slate-900 mt-1">0</div>
        </div>
        <div>
          <span class="text-xs text-slate-500 font-medium">Trading Fee</span>
          <div class="font-mono font-bold text-xl text-indigo-600 mt-1">0.30%</div>
        </div>
        <div>
          <span class="text-xs text-slate-500 font-medium">Protocol Fee Recipient</span>
          <div class="font-mono text-xs font-semibold text-slate-700 mt-2 truncate">Verdis Treasury / Eco Pool</div>
        </div>
      </div>

      <!-- DEX Cards Grid -->
      <div id="dex-pools-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        <div class="col-span-full py-12 text-center text-slate-400 font-mono bg-white rounded-2xl border border-slate-200">
          Loading AMM DEX pools...
        </div>
      </div>

    </div>

    <!-- ECO TAB CONTENT -->
    <div id="tab-content-eco" class="tab-pane hidden space-y-6">
      
      <!-- Eco Hero Banner -->
      <div class="bg-gradient-to-br from-slate-900 via-emerald-950 to-slate-900 text-white rounded-2xl p-6 shadow-xl border border-emerald-800/40">
        <div class="max-w-3xl">
          <span class="bg-[#caff33] text-[#0f172a] text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider">
            Green Blockchain Innovation
          </span>
          <h2 class="font-heading font-extrabold text-2xl sm:text-3xl mt-3 text-white">
            Verdis Eco-Friendly Layer & Carbon Protocol
          </h2>
          <p class="text-slate-300 text-sm mt-2 leading-relaxed">
            Verdis Chain incorporates zero-carbon consensus incentives, on-chain carbon credit issuance, and transparent reforestation tracking directly into the Substrate runtime.
          </p>
        </div>
      </div>

      <!-- Eco Metrics Grid -->
      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <div class="bg-white p-4 rounded-xl shadow-sm border border-slate-200">
          <span class="text-xs text-slate-500 font-medium">Total CO2 Offset</span>
          <div id="eco-total-co2" class="font-mono font-bold text-lg text-emerald-600 mt-1">0 kg</div>
        </div>
        <div class="bg-white p-4 rounded-xl shadow-sm border border-slate-200">
          <span class="text-xs text-slate-500 font-medium">Trees Planted</span>
          <div id="eco-trees-planted" class="font-mono font-bold text-lg text-slate-900 mt-1">0</div>
        </div>
        <div class="bg-white p-4 rounded-xl shadow-sm border border-slate-200">
          <span class="text-xs text-slate-500 font-medium">Carbon Credits</span>
          <div id="eco-credit-count" class="font-mono font-bold text-lg text-slate-900 mt-1">0</div>
        </div>
        <div class="bg-white p-4 rounded-xl shadow-sm border border-slate-200">
          <span class="text-xs text-slate-500 font-medium">Credits Retired</span>
          <div id="eco-credits-retired" class="font-mono font-bold text-lg text-purple-600 mt-1">0</div>
        </div>
        <div class="bg-white p-4 rounded-xl shadow-sm border border-slate-200">
          <span class="text-xs text-slate-500 font-medium">Green Validators</span>
          <div id="eco-green-validators" class="font-mono font-bold text-lg text-emerald-600 mt-1">0</div>
        </div>
        <div class="bg-white p-4 rounded-xl shadow-sm border border-slate-200">
          <span class="text-xs text-slate-500 font-medium">Reforest Projects</span>
          <div id="eco-reforest-projects" class="font-mono font-bold text-lg text-slate-900 mt-1">0</div>
        </div>
      </div>

    </div>

  </main>

  <!-- FOOTER -->
  <footer class="bg-[#0f172a] text-slate-400 text-xs py-8 border-t border-slate-800 mt-auto">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-wrap items-center justify-between gap-4">
      <div class="flex items-center gap-2">
        <div class="bg-[#caff33] text-[#0f172a] font-bold rounded p-1 text-xs">V</div>
        <span class="font-heading font-bold text-white text-sm">Verdiscan</span>
        <span class="text-slate-500 ml-2">© 2026 Verdis Chain Network. All rights reserved.</span>
      </div>
      <div class="flex items-center gap-4 font-mono text-[11px] text-slate-400">
        <span>RPC: <code class="text-emerald-400">/rpc</code></span>
        <span>WS: <code class="text-emerald-400">/ws</code></span>
        <span class="bg-slate-800 px-2 py-0.5 rounded text-slate-300">v2.4.0 Production</span>
      </div>
    </div>
  </footer>
"""

with open("part2.html", "w") as f:
    f.write(part2)

print("Part 2 written successfully")
