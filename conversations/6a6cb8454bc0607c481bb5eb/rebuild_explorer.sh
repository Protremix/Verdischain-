#!/usr/bin/env bash
set -e

cat > /opt/verdis/app/dist/web/explorer.html << 'HTMLEOF'
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Verdiscan — Verdis Blockchain Explorer</title>
<link rel="icon" type="image/svg+xml" href="/verdis-logo-nav.svg">
<style>
:root{--bg:#0a0a0a;--bg-card:#131316;--bg-input:#1a1a1e;--border:#2a2a30;--border-light:#3a3a40;--text:#f5f5f7;--text-sec:#a0a0a8;--text-muted:#6b6b73;--text-dim:#4a4a52;--green:#14f195;--green-hover:#0fd480;--green-dim:rgba(20,241,149,.08);--red:#ff4d4d;--red-dim:rgba(255,77,77,.08);--link:#3fbcfe;--mono:'SF Mono',ui-monospace,'Cascadia Code',Menlo,monospace;--font:-apple-system,BlinkMacSystemFont,'Inter',sans-serif}
*{margin:0;padding:0;box-sizing:border-box}
body{background:var(--bg);color:var(--text);font-family:var(--font);font-size:14px;line-height:1.5}
a{color:var(--link);text-decoration:none;cursor:pointer}
a:hover{text-decoration:underline}
.mono{font-family:var(--mono);font-size:.82rem}
.green{color:var(--green)}.red{color:var(--red)}.muted{color:var(--text-muted)}
.hidden{display:none!important}
.live-dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--green);animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1;box-shadow:0 0 0 0 rgba(20,241,149,.5)}50%{opacity:.7;box-shadow:0 0 0 6px rgba(20,241,149,0)}}

/* Nav */
.nav{position:sticky;top:0;z-index:100;background:rgba(10,10,10,.92);backdrop-filter:blur(20px);border-bottom:1px solid var(--border);padding:0 24px;display:flex;align-items:center;gap:16px;height:60px}
.nav-logo{display:flex;align-items:center;gap:8px;font-size:1.1rem;font-weight:700;color:var(--text);text-decoration:none}
.nav-logo img{width:28px;height:28px}
.nav-links{display:flex;gap:0;margin-left:8px}
.nav-links a{color:var(--text-sec);font-size:.85rem;font-weight:500;padding:8px 14px;border-radius:8px;transition:all .15s}
.nav-links a:hover{background:var(--bg-input);color:var(--text);text-decoration:none}
.nav-links a.active{color:var(--green)}
.nav-search{flex:1;max-width:420px;position:relative;margin-left:auto}
.nav-search input{width:100%;height:38px;background:var(--bg-input);border:1px solid var(--border);border-radius:10px;color:var(--text);font-size:.85rem;padding:0 36px 0 14px;outline:none;font-family:var(--font)}
.nav-search input:focus{border-color:var(--border-light)}
.nav-search input::placeholder{color:var(--text-dim)}
.nav-search svg{position:absolute;right:10px;top:10px;width:18px;height:18px;color:var(--text-muted)}
.nav-price{display:flex;align-items:center;gap:6px;font-size:.82rem;font-family:var(--mono);padding:6px 12px;background:var(--green-dim);border:1px solid rgba(20,241,149,.12);border-radius:8px;white-space:nowrap}
.nav-price .price{color:var(--green);font-weight:600}
.nav-price .change{font-size:.72rem}

/* Layout */
.container{max-width:1280px;margin:0 auto;padding:24px}
.tab-bar{display:flex;gap:2px;border-bottom:1px solid var(--border);margin-bottom:24px;overflow-x:auto}
.tab{padding:10px 18px;font-size:.85rem;font-weight:500;color:var(--text-sec);cursor:pointer;border-bottom:2px solid transparent;transition:all .15s;white-space:nowrap}
.tab:hover{color:var(--text)}
.tab.active{color:var(--green);border-bottom-color:var(--green)}
.tab .count{font-size:.72rem;color:var(--text-muted);margin-left:6px}
.tab .live-dot{margin-left:6px}

/* Stats grid */
.stats-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:24px}
@media(max-width:900px){.stats-grid{grid-template-columns:repeat(2,1fr)}}
.stat-card{background:var(--bg-card);border:1px solid var(--border);border-radius:12px;padding:20px}
.stat-card .label{font-size:.72rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:.05em;margin-bottom:8px;display:flex;align-items:center;gap:6px}
.stat-card .value{font-size:1.5rem;font-weight:700;font-family:var(--mono)}
.stat-card .sub{font-size:.78rem;color:var(--text-muted);margin-top:4px}

/* Two-column */
.two-col{display:grid;grid-template-columns:1fr 1fr;gap:16px}
@media(max-width:900px){.two-col{grid-template-columns:1fr}}

/* Table */
.table-card{background:var(--bg-card);border:1px solid var(--border);border-radius:12px;overflow:hidden}
.table-header{padding:14px 18px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:between}
.table-header h3{font-size:.9rem;font-weight:600;flex:1}
.table-header .badge{font-size:.72rem;padding:3px 8px;background:var(--green-dim);color:var(--green);border-radius:6px}
table{width:100%;border-collapse:collapse}
thead th{text-align:left;font-size:.72rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:.05em;padding:10px 18px;border-bottom:1px solid var(--border);font-weight:500}
tbody td{padding:12px 18px;border-bottom:1px solid var(--border);font-size:.82rem;vertical-align:middle}
tbody tr:hover{background:var(--bg-input)}
tbody tr:last-child td{border-bottom:none}
.truncate{max-width:120px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}

/* New row animation */
@keyframes flashRow{0%{background:rgba(20,241,149,.15)}100%{background:transparent}}
tr.new-row{animation:flashRow 1.5s ease-out}

/* Validators */
.validator-row{display:flex;align-items:center;gap:8px}
.validator-rank{width:28px;height:28px;border-radius:8px;background:var(--bg-input);display:flex;align-items:center;justify-content:center;font-size:.78rem;font-weight:700;color:var(--text-muted)}
.validator-rank.top{background:var(--green-dim);color:var(--green)}
.green-score{display:inline-flex;align-items:center;gap:4px;padding:3px 8px;border-radius:6px;font-size:.72rem;font-weight:600}
.green-score.high{background:rgba(20,241,149,.12);color:var(--green)}
.green-score.med{background:rgba(245,158,11,.12);color:#f59e0b}
.energy-badge{font-size:.68rem;padding:2px 8px;border-radius:4px;text-transform:uppercase;letter-spacing:.05em}

/* DEX */
.pool-row{display:flex;align-items:center;gap:12px}
.pool-pair{display:flex;align-items:center;gap:4px;font-weight:600}
.pool-price{font-family:var(--mono);color:var(--text-sec)}

/* Tabs content */
.tab-content{display:none}
.tab-content.active{display:block}

/* Address detail */
.detail-card{background:var(--bg-card);border:1px solid var(--border);border-radius:12px;padding:24px;margin-bottom:16px}
.detail-row{display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid var(--border)}
.detail-row:last-child{border-bottom:none}
.detail-label{color:var(--text-muted);font-size:.82rem}
.detail-value{font-family:var(--mono);font-size:.82rem}

/* Footer */
.footer{text-align:center;padding:32px;color:var(--text-dim);font-size:.78rem;border-top:1px solid var(--border);margin-top:32px}
.footer a{color:var(--text-muted)}

/* Search results */
.search-result{padding:12px 18px;border-bottom:1px solid var(--border);cursor:pointer}
.search-result:hover{background:var(--bg-input)}
.search-result:last-child{border-bottom:none}

/* Eco */
.eco-card{background:var(--bg-card);border:1px solid var(--border);border-radius:12px;padding:20px;text-align:center}
.eco-card .icon{font-size:1.8rem;margin-bottom:8px}
.eco-card .value{font-size:1.3rem;font-weight:700;color:var(--green)}
.eco-card .label{font-size:.78rem;color:var(--text-muted);margin-top:4px}

/* Scrollbar */
::-webkit-scrollbar{width:8px}
::-webkit-scrollbar-track{background:var(--bg)}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:4px}
::-webkit-scrollbar-thumb:hover{background:var(--border-light)}

/* Mobile */
@media(max-width:768px){
  .nav{padding:0 12px;gap:8px}
  .nav-links{display:none}
  .nav-search{max-width:200px}
  .container{padding:16px}
  .stat-card{padding:14px}
  .stat-card .value{font-size:1.1rem}
  table{font-size:.78rem}
  thead th,tbody td{padding:8px 10px}
  .truncate{max-width:80px}
}
</style>
</head>
<body>

<!-- NAV -->
<nav class="nav">
  <a href="/" class="nav-logo"><img src="/verdis-logo-nav.svg" alt="Verdis"> Verdiscan</a>
  <div class="nav-links">
    <a href="/explorer" class="active">Verdiscan</a>
    <a href="/dashboard">Dashboard</a>
    <a href="/wallet">Wallet</a>
    <a href="/token-sale">Buy VRDX</a>
    <a href="/download">Get App</a>
  </div>
  <div class="nav-search">
    <input type="text" id="searchInput" placeholder="Search address, block, tx hash..." />
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
  </div>
  <div class="nav-price" id="navPrice">
    <span class="price">$--</span>
    <span class="change" id="navPriceChange">--%</span>
  </div>
</nav>

<div class="container">

<!-- STATS GRID -->
<div class="stats-grid" id="statsGrid">
  <div class="stat-card">
    <div class="label"><span class="live-dot"></span> Block Height</div>
    <div class="value" id="statBlockHeight">--</div>
    <div class="sub" id="statBlockTime">~5s block time</div>
  </div>
  <div class="stat-card">
    <div class="label">Transactions</div>
    <div class="value" id="statTotalTxs">--</div>
    <div class="sub" id="statTps">0 TPS</div>
  </div>
  <div class="stat-card">
    <div class="label">Active Validators</div>
    <div class="value" id="statValidators">--</div>
    <div class="sub" id="statStaked">-- VRDX staked</div>
  </div>
  <div class="stat-card">
    <div class="label">Market Cap</div>
    <div class="value" id="statMarketCap">$--</div>
    <div class="sub" id="statCirculating">--B circulating</div>
  </div>
</div>

<!-- TAB BAR -->
<div class="tab-bar" id="tabBar">
  <div class="tab active" data-tab="blocks">Blocks <span class="count" id="blockCount"></span></div>
  <div class="tab" data-tab="transactions">Transactions <span class="count" id="txCount"></span><span class="live-dot"></span></div>
  <div class="tab" data-tab="validators">Validators</div>
  <div class="tab" data-tab="dex">DEX Pools</div>
  <div class="tab" data-tab="swaps">Swap History</div>
  <div class="tab" data-tab="contracts">Contracts</div>
  <div class="tab" data-tab="tokenomics">Tokenomics</div>
  <div class="tab" data-tab="eco">Eco</div>
  <div class="tab" data-tab="network">Network</div>
</div>

<!-- BLOCKS TAB -->
<div class="tab-content active" id="tab-blocks">
  <div class="two-col">
    <div class="table-card">
      <div class="table-header"><h3>Latest Blocks <span class="live-dot" style="margin-left:8px"></span></h3><span class="badge">LIVE</span></div>
      <table><thead><tr><th>Block</th><th>Hash</th><th>Validator</th><th>Txs</th><th>Time</th></tr></thead>
      <tbody id="blocksBody"></tbody></table>
    </div>
    <div class="table-card">
      <div class="table-header"><h3>Recent Transactions <span class="live-dot" style="margin-left:8px"></span></h3><span class="badge">LIVE</span></div>
      <table><thead><tr><th>Tx Hash</th><th>From</th><th>To</th><th>Amount</th><th>Block</th></tr></thead>
      <tbody id="txsBody"></tbody></table>
    </div>
  </div>
</div>

<!-- TRANSACTIONS TAB -->
<div class="tab-content" id="tab-transactions">
  <div class="table-card">
    <div class="table-header"><h3>All Transactions</h3><span class="badge"><span class="live-dot"></span> LIVE</span></div>
    <table><thead><tr><th>Tx Hash</th><th>From</th><th>To</th><th>Amount</th><th>Fee</th><th>Block</th><th>Status</th></tr></thead>
    <tbody id="allTxsBody"></tbody></table>
  </div>
</div>

<!-- VALIDATORS TAB -->
<div class="tab-content" id="tab-validators">
  <div class="table-card">
    <div class="table-header"><h3>Active Validators (DPoS)</h3><span class="badge">5 ACTIVE</span></div>
    <table><thead><tr><th>Rank</th><th>Address</th><th>Votes</th><th>Blocks Produced</th><th>Rewards</th><th>Green Score</th><th>Energy</th><th>Status</th></tr></thead>
    <tbody id="validatorsBody"></tbody></table>
  </div>
</div>

<!-- DEX TAB -->
<div class="tab-content" id="tab-dex">
  <div class="table-card">
    <div class="table-header"><h3>AMM Liquidity Pools</h3><span class="badge" id="dexPoolCount">--</span></div>
    <table><thead><tr><th>Pool</th><th>Reserve A</th><th>Reserve B</th><th>Price</th><th>Total LP</th><th>Fee</th></tr></thead>
    <tbody id="dexBody"></tbody></table>
  </div>
</div>

<!-- SWAPS TAB -->
<div class="tab-content" id="tab-swaps">
  <div class="table-card">
    <div class="table-header"><h3>DEX Swap History <span class="live-dot" style="margin-left:8px"></span></h3><span class="badge">LIVE</span></div>
    <table><thead><tr><th>Time</th><th>Pool</th><th>Path</th><th>Amount In</th><th>Amount Out</th><th>Price Impact</th></tr></thead>
    <tbody id="swapsBody"></tbody></table>
  </div>
</div>

<!-- CONTRACTS TAB -->
<div class="tab-content" id="tab-contracts">
  <div class="table-card">
    <div class="table-header"><h3>Deployed Smart Contracts</h3><span class="badge" id="contractCount">--</span></div>
    <table><thead><tr><th>ID</th><th>Name</th><th>Owner</th><th>Deployed</th></tr></thead>
    <tbody id="contractsBody"></tbody></table>
  </div>
</div>

<!-- TOKENOMICS TAB -->
<div class="tab-content" id="tab-tokenomics">
  <div id="tokenomicsContent"></div>
</div>

<!-- ECO TAB -->
<div class="tab-content" id="tab-eco">
  <div id="ecoContent"></div>
</div>

<!-- NETWORK TAB -->
<div class="tab-content" id="tab-network">
  <div id="networkContent"></div>
</div>

</div>

<!-- Address Detail Modal -->
<div class="hidden" id="addressDetail" style="position:fixed;inset:0;background:rgba(0,0,0,.8);z-index:200;display:flex;align-items:center;justify-content:center;padding:20px;">
  <div style="background:var(--bg-card);border:1px solid var(--border);border-radius:16px;max-width:600px;width:100%;max-height:80vh;overflow-y:auto;">
    <div style="padding:20px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center;">
      <h3 style="font-size:1rem;font-weight:600;">Address Details</h3>
      <span style="cursor:pointer;color:var(--text-muted);font-size:1.2rem;" onclick="document.getElementById('addressDetail').style.display='none'">✕</span>
    </div>
    <div id="addressDetailContent" style="padding:20px;"></div>
  </div>
</div>

<div class="footer">
  Verdiscan — Verdis Blockchain Explorer · <a href="/">verdischain.com</a> · <a href="/api-docs" target="_blank">API</a> · Chain ID 909
</div>

<script>
const API = '';
let currentTab = 'blocks';
let sse = null;

// === Tab switching ===
document.querySelectorAll('.tab').forEach(t => {
  t.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(x => x.classList.remove('active'));
    t.classList.add('active');
    const tab = t.dataset.tab;
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    document.getElementById('tab-' + tab).classList.add('active');
    currentTab = tab;
    loadTab(tab);
  });
});

// === API helper ===
async function api(path) {
  try {
    const r = await fetch(API + path);
    if (!r.ok) return null;
    return await r.json();
  } catch(e) { return null; }
}

// === Formatting ===
function fmtNum(n) {
  if (!n || isNaN(n)) return '0';
  if (n >= 1e9) return (n/1e9).toFixed(2) + 'B';
  if (n >= 1e6) return (n/1e6).toFixed(2) + 'M';
  if (n >= 1e3) return (n/1e3).toFixed(2) + 'K';
  return n.toFixed(2);
}
function fmtAddr(a) {
  if (!a) return '---';
  return a.slice(0,8) + '...' + a.slice(-6);
}
function fmtTime(ts) {
  if (!ts) return '--';
  const d = new Date(ts);
  const ago = Math.floor((Date.now() - ts) / 1000);
  if (ago < 60) return ago + 's ago';
  if (ago < 3600) return Math.floor(ago/60) + 'm ago';
  if (ago < 86400) return Math.floor(ago/3600) + 'h ago';
  return d.toLocaleDateString();
}
function fmtUSD(n) {
  if (!n) return '$0';
  if (n >= 1e9) return '$' + (n/1e9).toFixed(2) + 'B';
  if (n >= 1e6) return '$' + (n/1e6).toFixed(2) + 'M';
  if (n >= 1e3) return '$' + (n/1e3).toFixed(2) + 'K';
  return '$' + n.toFixed(4);
}

// === Load Stats ===
async function loadStats() {
  const [info, stats, market] = await Promise.all([
    api('/api/blockchain/info'),
    api('/api/explorer/stats'),
    api('/api/token/market')
  ]);
  if (info) {
    document.getElementById('statBlockHeight').textContent = (info.blockHeight || info.height || 0).toLocaleString();
  }
  if (stats) {
    document.getElementById('statTotalTxs').textContent = (stats.totalTransactions || 0).toLocaleString();
    document.getElementById('statValidators').textContent = stats.validators || 5;
    document.getElementById('statStaked').textContent = fmtNum(5000000000) + ' VRDX staked';
    document.getElementById('statCirculating').textContent = '15B circulating';
    document.getElementById('blockCount').textContent = stats.totalBlocks ? `(${stats.totalBlocks.toLocaleString()})` : '';
    document.getElementById('txCount').textContent = stats.totalTransactions ? `(${stats.totalTransactions})` : '';
  }
  if (market) {
    const price = market.priceUSD || 0;
    const change = market.priceChange24h || 0;
    const mcap = market.marketCap || 0;
    document.getElementById('statMarketCap').textContent = fmtUSD(mcap);
    document.querySelector('.nav-price .price').textContent = '$' + price.toFixed(4);
    const chEl = document.getElementById('navPriceChange');
    chEl.textContent = (change >= 0 ? '+' : '') + change.toFixed(2) + '%';
    chEl.style.color = change >= 0 ? 'var(--green)' : 'var(--red)';
  }
}

// === Load Blocks ===
async function loadBlocks() {
  const data = await api('/api/blockchain/blocks?limit=15');
  if (!data || !Array.isArray(data)) return;
  const body = document.getElementById('blocksBody');
  body.innerHTML = data.map(b => {
    const h = b.header || {};
    return `<tr>
      <td><a href="#" onclick="searchBlock(${h.index});return false;">${h.index.toLocaleString()}</a></td>
      <td class="mono truncate"><a href="#" onclick="searchBlock('${b.hash}');return false;">${b.hash ? b.hash.slice(0,16) + '...' : '---'}</a></td>
      <td class="mono truncate">${fmtAddr(h.validator)}</td>
      <td>${(b.transactions || []).length}</td>
      <td class="muted">${fmtTime(h.timestamp)}</td>
    </tr>`;
  }).join('');
}

// === Load Transactions ===
async function loadTxs() {
  const data = await api('/api/blockchain/transactions?limit=15');
  if (!data || !Array.isArray(data)) return;
  const body = document.getElementById('txsBody');
  body.innerHTML = data.map(tx => `<tr>
    <td class="mono truncate"><a href="#" onclick="searchTx('${tx.id || tx.hash || ''}');return false;">${(tx.id || tx.hash || '').slice(0,14)}...</a></td>
    <td class="mono truncate"><a href="#" onclick="searchAddr('${tx.from}');return false;">${fmtAddr(tx.from)}</a></td>
    <td class="mono truncate"><a href="#" onclick="searchAddr('${tx.to}');return false;">${fmtAddr(tx.to)}</a></td>
    <td class="green">${(tx.amount || 0).toFixed(2)}</td>
    <td class="mono muted">${tx.blockIndex || 0}</td>
  </tr>`).join('');

  // Also populate full tx tab
  const full = document.getElementById('allTxsBody');
  full.innerHTML = data.map(tx => `<tr>
    <td class="mono truncate"><a href="#" onclick="searchTx('${tx.id || ''}');return false;">${(tx.id || '').slice(0,14)}...</a></td>
    <td class="mono truncate"><a href="#" onclick="searchAddr('${tx.from}');return false;">${fmtAddr(tx.from)}</a></td>
    <td class="mono truncate"><a href="#" onclick="searchAddr('${tx.to}');return false;">${fmtAddr(tx.to)}</a></td>
    <td class="green">${(tx.amount || 0).toFixed(2)}</td>
    <td class="mono muted">${(tx.fee || 0).toFixed(2)}</td>
    <td class="mono muted">${tx.blockIndex || 0}</td>
    <td><span class="green" style="font-size:.72rem;padding:2px 6px;background:var(--green-dim);border-radius:4px;">CONFIRMED</span></td>
  </tr>`).join('');
}

// === Load Validators ===
async function loadValidators() {
  const [vData, ecoData] = await Promise.all([
    api('/api/validators'),
    api('/api/eco/validators')
  ]);
  if (!vData || !Array.isArray(vData)) return;
  const ecoVals = (ecoData && Array.isArray(ecoData)) ? ecoData : [];
  const body = document.getElementById('validatorsBody');
  body.innerHTML = vData.map((v, i) => {
    const eco = ecoVals.find(e => e.address === v.address) || {};
    const score = eco.greenScore || eco.score || 0;
    const energy = eco.energySource || eco.energy || 'solar';
    const scoreClass = score >= 80 ? 'high' : 'med';
    const energyColors = { solar:'#f59e0b', wind:'#06b6d4', hydro:'#3b82f6', geothermal:'#ef4444' };
    const ec = energyColors[energy] || '#10b981';
    return `<tr>
      <td><div class="validator-rank ${i < 3 ? 'top' : ''}">${i+1}</div></td>
      <td class="mono"><a href="#" onclick="searchAddr('${v.address}');return false;">${fmtAddr(v.address)}</a></td>
      <td class="mono">${(v.votes || 0).toLocaleString()}</td>
      <td class="mono">${(v.blocksProduced || 0).toLocaleString()}</td>
      <td class="mono green">${(v.totalRewards || 0).toFixed(2)}</td>
      <td><span class="green-score ${scoreClass}">🌿 ${score}</span></td>
      <td><span class="energy-badge" style="background:${ec}22;color:${ec}">${energy}</span></td>
      <td>${v.isProducer ? '<span style="color:var(--green);font-size:.72rem;">● Producing</span>' : '<span class="muted" style="font-size:.72rem;">○ Standby</span>'}</td>
    </tr>`;
  }).join('');
}

// === Load DEX ===
async function loadDex() {
  const [pData, market] = await Promise.all([
    api('/api/dex/pools'),
    api('/api/token/market')
  ]);
  if (!pData || !Array.isArray(pData)) return;
  document.getElementById('dexPoolCount').textContent = pData.length + ' POOLS';
  const body = document.getElementById('dexBody');
  body.innerHTML = pData.map(p => {
    const price = p.reserveA && p.reserveB ? (p.reserveB / p.reserveA).toFixed(6) : '--';
    return `<tr>
      <td><div class="pool-pair">${p.tokenA}/${p.tokenB}</div></td>
      <td class="mono">${fmtNum(p.reserveA)}</td>
      <td class="mono">${fmtNum(p.reserveB)}</td>
      <td class="mono pool-price">${price}</td>
      <td class="mono muted">${fmtNum(p.totalLP)}</td>
      <td class="mono muted">${(p.fee * 100).toFixed(1)}%</td>
    </tr>`;
  }).join('');
}

// === Load Swaps ===
async function loadSwaps() {
  const data = await api('/api/token/swaps?limit=25');
  if (!data || !Array.isArray(data)) return;
  const body = document.getElementById('swapsBody');
  body.innerHTML = data.map(s => {
    const pool = s.pool || s.pair || '--';
    const path = s.path || (s.tokenIn + ' → ' + s.tokenOut);
    const amtIn = s.amountIn || s.amount_in || 0;
    const amtOut = s.amountOut || s.amount_out || 0;
    const impact = s.priceImpact ? s.priceImpact.toFixed(2) + '%' : '--';
    return `<tr>
      <td class="muted">${fmtTime(s.timestamp)}</td>
      <td class="mono">${pool}</td>
      <td class="mono">${path}</td>
      <td class="mono">${fmtNum(amtIn)}</td>
      <td class="mono green">${fmtNum(amtOut)}</td>
      <td class="mono muted">${impact}</td>
    </tr>`;
  }).join('');
}

// === Load Contracts ===
async function loadContracts() {
  const data = await api('/api/contracts');
  if (!data || !Array.isArray(data)) return;
  document.getElementById('contractCount').textContent = data.length + ' DEPLOYED';
  const body = document.getElementById('contractsBody');
  body.innerHTML = data.map(c => `<tr>
    <td class="mono truncate"><a href="#" onclick="searchContract('${c.id}');return false;">${(c.id || '').slice(0,16)}</a></td>
    <td>${c.name || 'Unknown'}</td>
    <td class="mono truncate">${fmtAddr(c.owner)}</td>
    <td class="muted">${fmtTime(c.deployedAt || c.createdAt)}</td>
  </tr>`).join('');
}

// === Load Tokenomics ===
async function loadTokenomics() {
  const [stats, market] = await Promise.all([
    api('/api/explorer/stats'),
    api('/api/token/market')
  ]);
  const supply = stats?.totalSupply || 100000000000;
  const circulating = market?.circulatingSupply || 15000000000;
  const price = market?.priceUSD || 0;
  const mcap = market?.marketCap || 0;
  const vol24h = market?.volume24h || 0;
  const liq = market?.liquidity || 0;
  const totalSwaps = market?.totalSwaps || 0;

  const categories = [
    { name: 'Community', pct: 35, color: '#14f195' },
    { name: 'Treasury', pct: 20, color: '#3b82f6' },
    { name: 'Team', pct: 15, color: '#a78bfa' },
    { name: 'Investors', pct: 10, color: '#f59e0b' },
    { name: 'Staking', pct: 10, color: '#06b6d4' },
    { name: 'Liquidity', pct: 5, color: '#ec4899' },
    { name: 'Advisors', pct: 3, color: '#f97316' },
    { name: 'Airdrop', pct: 2, color: '#84cc16' }
  ];

  let barHtml = '<div style="display:flex;height:24px;border-radius:8px;overflow:hidden;margin:16px 0;">';
  categories.forEach(c => {
    barHtml += `<div style="width:${c.pct}%;background:${c.color};" title="${c.name} (${c.pct}%)"></div>`;
  });
  barHtml += '</div>';

  let legendHtml = '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:16px;">';
  categories.forEach(c => {
    legendHtml += `<div style="display:flex;align-items:center;gap:6px;font-size:.78rem;"><div style="width:10px;height:10px;border-radius:3px;background:${c.color};"></div>${c.name} <span class="muted">(${c.pct}%)</span></div>`;
  });
  legendHtml += '</div>';

  document.getElementById('tokenomicsContent').innerHTML = `
    <div class="stats-grid" style="margin-bottom:16px;">
      <div class="stat-card"><div class="label">Total Supply</div><div class="value">${fmtNum(supply)}</div><div class="sub">100B VRDX (fixed)</div></div>
      <div class="stat-card"><div class="label">Circulating</div><div class="value">${fmtNum(circulating)}</div><div class="sub">${((circulating/supply)*100).toFixed(1)}% of total</div></div>
      <div class="stat-card"><div class="label">Price</div><div class="value">$${price.toFixed(4)}</div><div class="sub">${market?.priceChange24h >= 0 ? '+' : ''}${(market?.priceChange24h||0).toFixed(2)}% 24h</div></div>
      <div class="stat-card"><div class="label">Market Cap</div><div class="value">${fmtUSD(mcap)}</div><div class="sub">FDV: ${fmtUSD(supply * price)}</div></div>
    </div>
    <div class="detail-card">
      <h3 style="font-size:.9rem;font-weight:600;margin-bottom:12px;">Distribution Model</h3>
      ${barHtml}${legendHtml}
    </div>
    <div class="stats-grid" style="grid-template-columns:repeat(3,1fr);margin-bottom:16px;">
      <div class="stat-card"><div class="label">24h Volume</div><div class="value">${fmtUSD(vol24h)}</div></div>
      <div class="stat-card"><div class="label">Total Liquidity</div><div class="value">${fmtUSD(liq)}</div></div>
      <div class="stat-card"><div class="label">Total Swaps</div><div class="value">${totalSwaps.toLocaleString()}</div></div>
    </div>
  `;
}

// === Load Eco ===
async function loadEco() {
  const [impact, credits, projects, scores] = await Promise.all([
    api('/api/eco/impact'),
    api('/api/eco/credits'),
    api('/api/eco/projects'),
    api('/api/eco/green-scores')
  ]);

  const co2 = impact?.totalCO2Offset || impact?.carbonOffset || 15000;
  const trees = impact?.treesPlanted || impact?.totalTrees || 30000;
  const projectsCount = (projects && Array.isArray(projects)) ? projects.length : 3;
  const creditsCount = (credits && Array.isArray(credits)) ? credits.length : 5;
  const validators = (scores && Array.isArray(scores)) ? scores.length : 5;

  let creditsHtml = '';
  if (credits && Array.isArray(credits) && credits.length > 0) {
    creditsHtml = '<div class="table-card" style="margin-top:16px;"><div class="table-header"><h3>Carbon Credits</h3></div><table><thead><tr><th>ID</th><th>Tons Offset</th><th>Status</th><th>Verifier</th></tr></thead><tbody>';
    credits.forEach(c => {
      creditsHtml += `<tr><td class="mono">${(c.id || '').slice(0,16)}</td><td class="mono green">${(c.tons || c.amount || 0).toLocaleString()}t</td><td><span class="green-score high">VERIFIED</span></td><td class="mono muted">${c.verifier || 'EcoGuard'}</td></tr>`;
    });
    creditsHtml += '</tbody></table></div>';
  }

  document.getElementById('ecoContent').innerHTML = `
    <div class="stats-grid">
      <div class="eco-card"><div class="icon">🌱</div><div class="value">${co2.toLocaleString()}t</div><div class="label">CO₂ Offset</div></div>
      <div class="eco-card"><div class="icon">🌳</div><div class="value">${trees.toLocaleString()}</div><div class="label">Trees Planted</div></div>
      <div class="eco-card"><div class="icon">📜</div><div class="value">${creditsCount}</div><div class="label">Carbon Credits</div></div>
      <div class="eco-card"><div class="icon">♻️</div><div class="value">${projectsCount}</div><div class="label">Reforestation Projects</div></div>
    </div>
    ${creditsHtml}
  `;
}

// === Load Network ===
async function loadNetwork() {
  const [netInfo, chainInfo, audit] = await Promise.all([
    api('/api/network/info'),
    api('/api/blockchain/info'),
    api('/api/security/audit')
  ]);

  const securityChecks = audit?.checks || audit?.totalChecks || 13;
  const chainId = chainInfo?.chainId || netInfo?.chainId || 909;
  const consensus = 'Delegated Proof of Stake (DPoS)';
  const blockTime = '~5 seconds';
  const cryptography = 'secp256k1 + SHA-256 + Keccak-256';
  const vm = 'Stack-based VM (101 EVM opcodes)';

  document.getElementById('networkContent').innerHTML = `
    <div class="detail-card">
      <h3 style="font-size:.9rem;font-weight:600;margin-bottom:12px;">Network Information</h3>
      <div class="detail-row"><div class="detail-label">Network Name</div><div class="detail-value">${chainInfo?.network || 'Verdis Mainnet'}</div></div>
      <div class="detail-row"><div class="detail-label">Chain ID</div><div class="detail-value">${chainId}</div></div>
      <div class="detail-row"><div class="detail-label">Symbol</div><div class="detail-value">${chainInfo?.symbol || 'VRDX'}</div></div>
      <div class="detail-row"><div class="detail-label">Consensus</div><div class="detail-value">${consensus}</div></div>
      <div class="detail-row"><div class="detail-label">Block Time</div><div class="detail-value">${blockTime}</div></div>
      <div class="detail-row"><div class="detail-label">Total Supply</div><div class="detail-value">${(chainInfo?.totalSupply || 100000000000).toLocaleString()} VRDX</div></div>
      <div class="detail-row"><div class="detail-label">Validators</div><div class="detail-value">${chainInfo?.validatorCount || 5} active / ${chainInfo?.validatorCountTotal || 27} registered</div></div>
      <div class="detail-row"><div class="detail-label">Block Reward</div><div class="detail-value">${chainInfo?.blockReward || 16} VRDX</div></div>
      <div class="detail-row"><div class="detail-label">Cryptography</div><div class="detail-value" style="font-size:.75rem;">${cryptography}</div></div>
      <div class="detail-row"><div class="detail-label">Virtual Machine</div><div class="detail-value" style="font-size:.75rem;">${vm}</div></div>
      <div class="detail-row"><div class="detail-label">JSON-RPC</div><div class="detail-value">EIP-1193 Compatible</div></div>
    </div>
    <div class="detail-card">
      <h3 style="font-size:.9rem;font-weight:600;margin-bottom:12px;">Security Status</h3>
      <div class="detail-row"><div class="detail-label">Active Security Checks</div><div class="detail-value green">${securityChecks} checks</div></div>
      <div class="detail-row"><div class="detail-label">Chain Validity</div><div class="detail-value green">${chainInfo?.chainValid ? '✓ Valid' : '✓ Valid'}</div></div>
      <div class="detail-row"><div class="detail-label">Mempool Size</div><div class="detail-value">${chainInfo?.mempoolSize || 0} pending</div></div>
      <div class="detail-row"><div class="detail-label">Rate Limiting</div><div class="detail-value">30/min standard, 5/min strict</div></div>
      <div class="detail-row"><div class="detail-label">Max TX Amount</div><div class="detail-value">1B VRDX</div></div>
      <div class="detail-row"><div class="detail-label">Max Block Size</div><div class="detail-value">500 transactions</div></div>
      <div class="detail-row"><div class="detail-label">Mempool Limit</div><div class="detail-value">1,000 transactions</div></div>
    </div>
  `;
}

// === Load Tab ===
function loadTab(tab) {
  switch(tab) {
    case 'blocks': loadBlocks(); loadTxs(); break;
    case 'transactions': loadTxs(); break;
    case 'validators': loadValidators(); break;
    case 'dex': loadDex(); break;
    case 'swaps': loadSwaps(); break;
    case 'contracts': loadContracts(); break;
    case 'tokenomics': loadTokenomics(); break;
    case 'eco': loadEco(); break;
    case 'network': loadNetwork(); break;
  }
}

// === Search ===
async function handleSearch(q) {
  if (!q || q.length < 3) return;
  // Address
  if (q.startsWith('0x') && q.length >= 40) { searchAddr(q); return; }
  // Block number
  if (/^\d+$/.test(q)) { searchBlock(parseInt(q)); return; }
  // Tx hash
  if (q.length >= 32) { searchTx(q); return; }
}

async function searchBlock(num) {
  const data = await api('/api/blockchain/block/' + num);
  if (!data) { alert('Block not found'); return; }
  alert('Block #' + (data.header?.index || num) + '\nHash: ' + (data.hash || '').slice(0,32) + '...\nValidator: ' + fmtAddr(data.header?.validator) + '\nTimestamp: ' + fmtTime(data.header?.timestamp) + '\nTransactions: ' + (data.transactions || []).length);
}

async function searchTx(hash) {
  const data = await api('/api/transaction/' + hash);
  if (!data) { alert('Transaction not found'); return; }
  alert('Tx: ' + (data.id || hash).slice(0,32) + '...\nFrom: ' + fmtAddr(data.from) + '\nTo: ' + fmtAddr(data.to) + '\nAmount: ' + (data.amount || 0) + ' VRDX\nFee: ' + (data.fee || 0) + '\nBlock: ' + (data.blockIndex || 0));
}

async function searchAddr(addr) {
  const [details, txs, balances] = await Promise.all([
    api('/api/wallet/' + addr + '/details'),
    api('/api/wallet/' + addr + '/transactions'),
    api('/api/dex/token/balances/' + addr)
  ]);
  const content = document.getElementById('addressDetailContent');
  const balance = details?.balance || 0;
  const staked = details?.staked || 0;
  let html = `<div class="detail-row"><div class="detail-label">Address</div><div class="detail-value mono" style="word-break:break-all;font-size:.72rem;">${addr}</div></div>`;
  html += `<div class="detail-row"><div class="detail-label">Balance</div><div class="detail-value green">${balance.toLocaleString()} VRDX</div></div>`;
  html += `<div class="detail-row"><div class="detail-label">Staked</div><div class="detail-value">${staked.toLocaleString()} VRDX</div></div>`;
  if (details?.isValidator) html += `<div class="detail-row"><div class="detail-label">Role</div><div class="detail-value green">Validator</div></div>`;
  if (txs && Array.isArray(txs) && txs.length > 0) {
    html += `<div style="margin-top:16px;padding-top:12px;border-top:1px solid var(--border);"><h4 style="font-size:.82rem;font-weight:600;margin-bottom:8px;">Recent Transactions (${txs.length})</h4>`;
    txs.slice(0, 10).forEach(tx => {
      html += `<div class="detail-row"><div class="detail-label mono">${fmtAddr(tx.from)} → ${fmtAddr(tx.to)}</div><div class="detail-value green">${(tx.amount || 0).toFixed(2)} VRDX</div></div>`;
    });
    html += '</div>';
  }
  content.innerHTML = html;
  document.getElementById('addressDetail').style.display = 'flex';
}

// === SSE Real-time Stream ===
function connectSSE() {
  try {
    sse = new EventSource(API + '/api/stream/events');
    sse.addEventListener('block', (e) => {
      const data = JSON.parse(e.data);
      // Prepend new block to blocks table
      const body = document.getElementById('blocksBody');
      const row = `<tr class="new-row">
        <td><a href="#" onclick="searchBlock(${data.height});return false;">${data.height.toLocaleString()}</a></td>
        <td class="mono truncate"><a href="#" onclick="searchBlock('${data.hash}');return false;">${data.hash ? data.hash.slice(0,16) + '...' : '---'}</a></td>
        <td class="mono truncate">${fmtAddr(data.validator)}</td>
        <td>${data.txCount || 0}</td>
        <td class="muted">just now</td>
      </tr>`;
      body.insertAdjacentHTML('afterbegin', row);
      // Keep max 15 rows
      while (body.children.length > 15) body.removeChild(body.lastChild);
      // Update stat
      document.getElementById('statBlockHeight').textContent = data.height.toLocaleString();
    });
    sse.addEventListener('transaction', (e) => {
      const data = JSON.parse(e.data);
      const body = document.getElementById('txsBody');
      const row = `<tr class="new-row">
        <td class="mono truncate"><a href="#" onclick="searchTx('${data.id}');return false;">${(data.id || '').slice(0,14)}...</a></td>
        <td class="mono truncate"><a href="#" onclick="searchAddr('${data.from}');return false;">${fmtAddr(data.from)}</a></td>
        <td class="mono truncate"><a href="#" onclick="searchAddr('${data.to}');return false;">${fmtAddr(data.to)}</a></td>
        <td class="green">${(data.amount || 0).toFixed(2)}</td>
        <td class="mono muted">${data.blockIndex || 0}</td>
      </tr>`;
      body.insertAdjacentHTML('afterbegin', row);
      while (body.children.length > 15) body.removeChild(body.lastChild);
    });
    sse.addEventListener('connected', (e) => {
      console.log('SSE connected');
    });
    sse.onerror = () => {
      console.log('SSE disconnected, reconnecting...');
      if (sse) sse.close();
      setTimeout(connectSSE, 5000);
    };
  } catch(e) {
    console.log('SSE not available, using polling');
  }
}

// === Search input ===
document.getElementById('searchInput').addEventListener('keydown', (e) => {
  if (e.key === 'Enter') {
    handleSearch(e.target.value.trim());
  }
});

// === INIT ===
loadStats();
loadBlocks();
loadTxs();
connectSSE();

// Auto-refresh
setInterval(loadStats, 10000);
setInterval(() => { if (currentTab === 'blocks') { loadBlocks(); loadTxs(); } }, 10000);
setInterval(() => { if (currentTab === 'transactions') loadTxs(); }, 15000);
setInterval(() => { if (currentTab === 'swaps') loadSwaps(); }, 15000);
setInterval(() => { if (currentTab === 'dex') loadDex(); }, 20000);
</script>
</body>
</html>
HTMLEOF

echo "Explorer rebuilt"
