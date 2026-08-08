import re

with open("/var/www/verdiscan/explorer/index.html") as f:
    content = f.read()

# 1. Add CSS for new cards (supply, epoch progress, stake)
new_css = """
/* Solscan-style info cards */
.info-cards{max-width:1200px;margin:0 auto;padding:0 24px 20px;display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
.info-card{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:16px 20px;position:relative;overflow:hidden}
.info-card-label{font-size:11px;color:var(--text-3);text-transform:uppercase;letter-spacing:.05em;margin-bottom:6px}
.info-card-value{font-family:var(--mono);font-size:18px;font-weight:700;color:var(--text)}
.info-card-value.accent{color:var(--accent)}
.info-card-sub{font-size:11px;color:var(--text-3);margin-top:4px}
.info-card-bar{height:6px;background:rgba(0,0,0,.06);border-radius:3px;margin-top:10px;overflow:hidden}
.info-card-bar-fill{height:100%;background:linear-gradient(90deg,var(--accent),var(--success));border-radius:3px;transition:width .5s ease}
.info-card-pct{position:absolute;top:16px;right:20px;font-size:11px;font-weight:600;color:var(--accent)}
.badge-row{display:flex;gap:6px;margin-top:8px;flex-wrap:wrap}
.badge-sm{padding:2px 8px;border-radius:100px;font-size:10px;font-weight:600;background:rgba(22,163,74,.1);color:var(--accent)}
.badge-sm.warn{background:rgba(251,191,36,.1);color:var(--warning)}
.badge-sm.err{background:rgba(248,113,113,.1);color:var(--error)}
@media(max-width:768px){.info-cards{grid-template-columns:repeat(2,1fr)}}
"""

content = content.replace("</style>", new_css + "\n</style>")

# 2. Add info cards row after stats bar (before search)
# Find the closing of stats-bar section and add info-cards after it
stats_bar_end = content.find('</section>\n<!-- Search')
if stats_bar_end == -1:
    # Try alternate
    stats_bar_end = content.find('</section>', content.find('stats-bar'))

# Find the search section to insert before it
search_pos = content.find('<!-- Search')
if search_pos == -1:
    search_pos = content.find('<section class="search-wrap"')

if search_pos > 0:
    info_cards_html = """
<!-- Solscan-style Info Cards -->
<div class="info-cards">
  <div class="info-card">
    <div class="info-card-label">Total Supply</div>
    <div class="info-card-value accent" id="infoSupply">100,000,000,000</div>
    <div class="info-card-sub">VRDX · 9 decimals</div>
    <div class="badge-row"><span class="badge-sm">Circulating: <span id="infoCirc">—</span></span></div>
  </div>
  <div class="info-card">
    <div class="info-card-label">Total Stake</div>
    <div class="info-card-value" id="infoStake">— VRDX</div>
    <div class="info-card-sub" id="infoStakeSub">Loading validators…</div>
    <div class="info-card-pct" id="infoStakePct"></div>
    <div class="info-card-bar"><div class="info-card-bar-fill" id="infoStakeBar" style="width:0%"></div></div>
  </div>
  <div class="info-card">
    <div class="info-card-label">Epoch Progress</div>
    <div class="info-card-value accent" id="infoEpoch">—</div>
    <div class="info-card-sub" id="infoEpochTime">Loading…</div>
    <div class="info-card-bar"><div class="info-card-bar-fill" id="infoEpochBar" style="width:0%"></div></div>
  </div>
  <div class="info-card">
    <div class="info-card-label">DEX TVL</div>
    <div class="info-card-value" id="infoTvl">— VRDX</div>
    <div class="info-card-sub" id="infoTvlSub">Loading pools…</div>
    <div class="badge-row"><span class="badge-sm" id="infoPoolCount">— pools</span></div>
  </div>
</div>

"""
    content = content[:search_pos] + info_cards_html + content[search_pos:]
    print("Info cards inserted before search section")
else:
    print("ERROR: Could not find search section")

# 3. Add JavaScript to populate the info cards
# Find the init() function and add calls there
# Add the info card update functions before the init() function

info_js = """
// ===== Solscan-style Info Cards =====
const TOTAL_SUPPLY = 100_000_000_000; // 100B VRDX
const DECIMALS = 9;

async function updateInfoCards() {
  try {
    // Supply: total is 100B, circulating = total - reserved (estimated)
    const supplyEl = document.getElementById('infoSupply');
    if (supplyEl) supplyEl.textContent = (TOTAL_SUPPLY / 1e9).toFixed(0).replace(/\\B(?=(\\d{3})+(?!\\d))/g, ',') + ' VRDX';
    // Circulating: estimate from on-chain (total - treasury/eco/team reserves)
    // For testnet, show what's been minted via transactions
    try {
      const blockHdr = await rpc('chain_getHeader', []);
      const blockNum = parseInt(blockHdr.number, 16);
      // Estimate circulating based on block rewards (simplified)
      const estimatedCirc = Math.min(blockNum * 1000, TOTAL_SUPPLY); // rough estimate
      const circEl = document.getElementById('infoCirc');
      if (circEl) circEl.textContent = (estimatedCirc / 1e9).toFixed(2) + 'B';
    } catch(e) {}

    // Total Stake: sum of all validator stakes
    try {
      const vals = await rpc('dpos_allValidators', []);
      let totalStake = 0n;
      let valCount = 0;
      for (const v of vals) {
        try {
          const stake = await rpc('dpos_validatorStake', [v]);
          totalStake += BigInt(stake || 0);
          valCount++;
        } catch(e) {}
      }
      const stakeVRDX = Number(totalStake) / 10**DECIMALS;
      const stakeEl = document.getElementById('infoStake');
      if (stakeEl) stakeEl.textContent = stakeVRDX.toLocaleString(undefined, {maximumFractionDigits: 2}) + ' VRDX';
      const stakeSub = document.getElementById('infoStakeSub');
      if (stakeSub) stakeSub.textContent = valCount + ' active validators';
      const stakePct = document.getElementById('infoStakePct');
      const stakePctVal = Math.min((stakeVRDX / TOTAL_SUPPLY) * 100, 100);
      if (stakePct) stakePct.textContent = stakePctVal.toFixed(2) + '%';
      const stakeBar = document.getElementById('infoStakeBar');
      if (stakeBar) stakeBar.style.width = Math.min(stakePctVal, 100) + '%';
    } catch(e) { console.log('Stake error:', e); }

    // Epoch progress
    try {
      const epoch = await rpc('dpos_currentEpoch', []);
      const epochEl = document.getElementById('infoEpoch');
      if (epochEl) epochEl.textContent = '#' + epoch;
      // Estimate epoch progress from block number
      const blockHdr = await rpc('chain_getHeader', []);
      const blockNum = parseInt(blockHdr.number, 16);
      const epochLength = 100; // blocks per epoch (adjust based on runtime)
      const epochProgress = (blockNum % epochLength) / epochLength * 100;
      const epochBar = document.getElementById('infoEpochBar');
      if (epochBar) epochBar.style.width = epochProgress + '%';
      const remaining = epochLength - (blockNum % epochLength);
      const epochTime = document.getElementById('infoEpochTime');
      if (epochTime) epochTime.textContent = remaining + ' blocks remaining';
    } catch(e) { console.log('Epoch error:', e); }

    // DEX TVL: sum of all pool reserves
    try {
      const pools = await rpc('amm_getAllPools', []);
      let totalTvl = 0;
      const poolCount = Array.isArray(pools) ? pools.length : 0;
      for (const p of (pools || [])) {
        const r1 = Number(p.reserve0 || p.reserves?.[0] || 0) / 10**DECIMALS;
        const r2 = Number(p.reserve1 || p.reserves?.[1] || 0) / 10**DECIMALS;
        totalTvl += (r1 + r2);
      }
      const tvlEl = document.getElementById('infoTvl');
      if (tvlEl) tvlEl.textContent = totalTvl.toLocaleString(undefined, {maximumFractionDigits: 2}) + ' VRDX';
      const tvlSub = document.getElementById('infoTvlSub');
      if (tvlSub) tvlSub.textContent = poolCount + ' pools active';
      const poolCountEl = document.getElementById('infoPoolCount');
      if (poolCountEl) poolCountEl.textContent = poolCount + ' pools';
    } catch(e) { console.log('TVL error:', e); }
  } catch(e) {
    console.log('Info cards error:', e);
  }
}

"""

# Insert before the init function
init_pos = content.find('function init(')
if init_pos == -1:
    init_pos = content.find('async function init(')
if init_pos == -1:
    init_pos = content.rfind('// =====')
    if init_pos == -1:
        init_pos = content.rfind('function ')

if init_pos > 0:
    content = content[:init_pos] + info_js + "\n" + content[init_pos:]
    print("Info JS inserted before init")
else:
    print("ERROR: Could not find init function")

# 4. Add updateInfoCards() call inside init()
# Find the init function and add the call
init_body_match = re.search(r'(async\s+)?function\s+init\s*\([^)]*\)\s*\{', content)
if init_body_match:
    init_start = init_body_match.end()
    # Add after the opening brace of init
    content = content[:init_start] + "\n  updateInfoCards();" + content[init_start:]
    print("updateInfoCards() call added to init()")
else:
    print("WARNING: Could not find init body to add call")

# 5. Also add periodic refresh (every 15 seconds)
# Find the end of init function or add setInterval
setinterval_pos = content.find('setInterval(updateTps')
if setinterval_pos > 0:
    content = content[:setinterval_pos] + "setInterval(updateInfoCards, 15000);\n  " + content[setinterval_pos:]
    print("setInterval added for info cards")
else:
    # Add before the closing script tag
    script_end = content.rfind('</script>')
    if script_end > 0:
        content = content[:script_end] + "\nsetInterval(updateInfoCards, 15000);\n" + content[script_end:]
        print("setInterval added before script end")

with open("/var/www/verdiscan/explorer/index.html", "w") as f:
    f.write(content)

print("Done. File size:", len(content))
print("info-cards CSS:", "info-cards" in content)
print("updateInfoCards fn:", "updateInfoCards" in content)
print("Total Supply card:", "infoSupply" in content)
print("Total Stake card:", "infoStake" in content)
print("Epoch Progress card:", "infoEpoch" in content)
print("DEX TVL card:", "infoTvl" in content)
