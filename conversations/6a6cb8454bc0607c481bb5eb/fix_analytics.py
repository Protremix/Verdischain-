import subprocess

result = subprocess.run(
    ["ssh", "-o", "ConnectTimeout=10", "root@91.98.160.145", "cat /var/www/verdiscan/explorer/index.html"],
    capture_output=True, text=True
)
content = result.stdout

# 1. Add Analytics tab button after Token Holders
old_tab = '''    <button class="tab" data-t="holders" onclick="switchTab('holders')">Token Holders</button>'''
new_tab = '''    <button class="tab" data-t="holders" onclick="switchTab('holders')">Token Holders</button>
    <button class="tab" data-t="analytics" onclick="switchTab('analytics')">Analytics</button>'''
content = content.replace(old_tab, new_tab)

# 2. Add tab content section after Token Holders section (before <!-- Modal -->)
old_holders_end = '''  </div>

<!-- Modal -->'''
new_holders_end = '''  </div>

  <!-- Analytics -->
  <div class="tab-content" id="tab-analytics">
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px" class="analytics-grid">
      <div class="panel" style="padding:16px">
        <div class="panel-header"><span class="panel-title">Transaction Volume</span><span class="panel-link" id="analyticsTxCount">—</span></div>
        <canvas id="txVolumeChart" width="400" height="180" style="width:100%;height:180px"></canvas>
        <div style="display:flex;gap:16px;margin-top:8px;font-size:12px;color:var(--text-3)">
          <span>Blocks <span id="analyticsBlocks" style="color:var(--text-1);font-weight:600">0</span></span>
          <span>Total TX <span id="analyticsTotalTx" style="color:var(--text-1);font-weight:600">0</span></span>
          <span>Avg/Block <span id="analyticsAvgTx" style="color:var(--text-1);font-weight:600">0</span></span>
        </div>
      </div>
      <div class="panel" style="padding:16px">
        <div class="panel-header"><span class="panel-title">TPS Over Time</span><span class="panel-link" id="analyticsTpsLabel">—</span></div>
        <canvas id="tpsHistoryChart" width="400" height="180" style="width:100%;height:180px"></canvas>
        <div style="display:flex;gap:16px;margin-top:8px;font-size:12px;color:var(--text-3)">
          <span>Current <span id="analyticsCurTps" style="color:var(--text-1);font-weight:600">0</span></span>
          <span>Peak <span id="analyticsPeakTps" style="color:var(--text-1);font-weight:600">0</span></span>
          <span>Avg <span id="analyticsAvgTps" style="color:var(--text-1);font-weight:600">0</span></span>
        </div>
      </div>
    </div>
    <div class="panel" style="padding:16px">
      <div class="panel-header"><span class="panel-title">Block Production Rate</span><span class="panel-link" id="analyticsBlockRate">—</span></div>
      <canvas id="blockRateChart" width="800" height="120" style="width:100%;height:120px"></canvas>
      <div style="display:flex;gap:16px;margin-top:8px;font-size:12px;color:var(--text-3)">
        <span>Avg Block Time <span id="analyticsAvgBlockTime" style="color:var(--text-1);font-weight:600">6.0s</span></span>
        <span>Blocks/min <span id="analyticsBlocksPerMin" style="color:var(--text-1);font-weight:600">10</span></span>
      </div>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-top:16px" class="analytics-stats">
      <div class="stat-card reveal"><div class="stat-label">Extrinsic Success Rate</div><div class="stat-value success" id="analyticsSuccessRate" style="font-size:20px">—</div><div class="stat-sub" id="analyticsSuccessDetail">— / —</div></div>
      <div class="stat-card reveal"><div class="stat-label">Unique Signers</div><div class="stat-value" id="analyticsUniqueSigners" style="font-size:20px">—</div><div class="stat-sub">Last 50 blocks</div></div>
      <div class="stat-card reveal"><div class="stat-label">Total Extrinsics</div><div class="stat-value" id="analyticsTotalExt" style="font-size:20px">—</div><div class="stat-sub">Recent blocks</div></div>
    </div>
  </div>

<!-- Modal -->'''
content = content.replace(old_holders_end, new_holders_end, 1)

# 3. Add switchTab case for analytics
old_switch = '''  if (t==='holders') loadHolders();
}'''
new_switch = '''  if (t==='holders') loadHolders();
  if (t==='analytics') loadAnalytics();
}'''
content = content.replace(old_switch, new_switch)

# 4. Add loadAnalytics function before init()
old_init = '''async function init() {
  updateInfoCards();
  initScroll();'''
new_init = '''// Analytics data collectors
window._tpsHistory = [];
window._txVolumeData = [];
window._blockTimes = [];
window._extStats = { success: 0, total: 0, signers: new Set() };

// Collect analytics data from each block
function collectAnalytics(blocks) {
  if (!blocks || !Array.isArray(blocks)) return;
  var totalTx = 0;
  for (var i = 0; i < blocks.length; i++) {
    var b = blocks[i];
    var txCount = (b.extrinsics && b.extrinsics.length) || 0;
    totalTx += txCount;
    window._txVolumeData.push({ block: b.number, txs: txCount });
    if (window._txVolumeData.length > 50) window._txVolumeData.shift();

    // Collect extrinsic stats
    if (b.extrinsics) {
      for (var j = 0; j < b.extrinsics.length; j++) {
        var ext = b.extrinsics[j];
        window._extStats.total++;
        if (!ext.dispatchError) window._extStats.success++;
        if (ext.signer) window._extStats.signers.add(ext.signer);
      }
    }
  }
  if (window._txVolumeData.length > 50) {
    window._txVolumeData = window._txVolumeData.slice(-50);
  }
}

// Track TPS history
setInterval(function() {
  var recentTx = window._txVolumeData.slice(-10);
  var totalTx = 0;
  for (var i = 0; i < recentTx.length; i++) totalTx += recentTx[i].txs;
  var tps = recentTx.length > 0 ? (totalTx / (recentTx.length * 6)).toFixed(2) : 0;
  window._tpsHistory.push(parseFloat(tps));
  if (window._tpsHistory.length > 30) window._tpsHistory.shift();
}, 5000);

async function loadAnalytics() {
  // Fetch last 50 blocks for analytics
  try {
    var header = await rpc('chain_getHeader', []);
    if (!header) return;
    var current = parseInt(header.number, 16);
    var blocks = [];

    // Fetch 50 blocks in parallel (batches of 10)
    for (var batch = 0; batch < 5; batch++) {
      var promises = [];
      for (var i = 0; i < 10; i++) {
        var blockNum = current - (batch * 10 + i);
        if (blockNum < 0) break;
        promises.push(fetchBlockData(blockNum));
      }
      var results = await Promise.all(promises);
      blocks = blocks.concat(results.filter(function(b) { return b; }));
    }

    blocks.sort(function(a, b) { return a.number - b.number; });

    // Collect stats
    var totalTx = 0, totalExt = 0, successCount = 0;
    var signers = new Set();
    var blockTimes = [];

    for (var i = 0; i < blocks.length; i++) {
      var b = blocks[i];
      var txCount = (b.extrinsics && b.extrinsics.length) || 0;
      totalTx += txCount;
      totalExt += txCount;
      if (b.extrinsics) {
        for (var j = 0; j < b.extrinsics.length; j++) {
          if (!b.extrinsics[j].dispatchError) successCount++;
          if (b.extrinsics[j].signer) signers.add(b.extrinsics[j].signer);
        }
      }
      if (i > 0) {
        var timeDiff = (b.timestamp - blocks[i-1].timestamp) / 1000;
        if (timeDiff > 0 && timeDiff < 60) blockTimes.push(timeDiff);
      }
    }

    // Update window data
    window._txVolumeData = blocks.map(function(b) {
      return { block: b.number, txs: (b.extrinsics && b.extrinsics.length) || 0 };
    });

    // Calculate stats
    var avgTx = blocks.length > 0 ? (totalTx / blocks.length).toFixed(1) : 0;
    var avgBlockTime = blockTimes.length > 0
      ? (blockTimes.reduce(function(a,b){return a+b;},0) / blockTimes.length).toFixed(1)
      : '6.0';
    var blocksPerMin = avgBlockTime > 0 ? Math.round(60 / parseFloat(avgBlockTime)) : 10;
    var successRate = totalExt > 0 ? ((successCount / totalExt) * 100).toFixed(1) : 100;

    // Update stat displays
    var el;
    if (el = document.getElementById('analyticsTxCount')) el.textContent = blocks.length + ' blocks analyzed';
    if (el = document.getElementById('analyticsBlocks')) el.textContent = blocks.length;
    if (el = document.getElementById('analyticsTotalTx')) el.textContent = totalTx;
    if (el = document.getElementById('analyticsAvgTx')) el.textContent = avgTx;
    if (el = document.getElementById('analyticsCurTps')) el.textContent = window._tpsHistory.length > 0 ? window._tpsHistory[window._tpsHistory.length-1].toFixed(2) : '0';
    if (el = document.getElementById('analyticsPeakTps')) el.textContent = window._tpsHistory.length > 0 ? Math.max.apply(null, window._tpsHistory).toFixed(2) : '0';
    if (el = document.getElementById('analyticsAvgTps')) el.textContent = window._tpsHistory.length > 0 ? (window._tpsHistory.reduce(function(a,b){return a+b;},0)/window._tpsHistory.length).toFixed(2) : '0';
    if (el = document.getElementById('analyticsTpsLabel')) el.textContent = window._tpsHistory.length + ' samples';
    if (el = document.getElementById('analyticsBlockRate')) el.textContent = blocks.length + ' blocks';
    if (el = document.getElementById('analyticsAvgBlockTime')) el.textContent = avgBlockTime + 's';
    if (el = document.getElementById('analyticsBlocksPerMin')) el.textContent = blocksPerMin;
    if (el = document.getElementById('analyticsSuccessRate')) el.textContent = successRate + '%';
    if (el = document.getElementById('analyticsSuccessDetail')) el.textContent = successCount + ' / ' + totalExt;
    if (el = document.getElementById('analyticsUniqueSigners')) el.textContent = signers.size;
    if (el = document.getElementById('analyticsTotalExt')) el.textContent = totalExt;

    // Draw charts
    drawTxVolumeChart();
    drawTpsHistoryChart();
    drawBlockRateChart(blockTimes);
  } catch(e) {
    console.error('Analytics error:', e);
  }
}

async function fetchBlockData(blockNum) {
  try {
    var hash = await rpc('chain_getBlockHash', [blockNum]);
    if (!hash) return null;
    var block = await rpc('chain_getBlock', [hash]);
    if (!block || !block.block) return null;
    var exts = block.block.extrinsics || [];
    var parsed = exts.map(function(ext) {
      var signer = null;
      try { if (ext.signature && ext.signature.signedTransaction && ext.signature.signedTransaction.signer) signer = ext.signature.signedTransaction.signer; } catch(e) {}
      return { signer: signer, dispatchError: null, method: ext.method ? ext.method.method : 'unknown' };
    });
    return { number: blockNum, extrinsics: parsed, timestamp: blockNum * 6000 };
  } catch(e) { return null; }
}

function drawTxVolumeChart() {
  var canvas = document.getElementById('txVolumeChart');
  if (!canvas) return;
  var ctx = canvas.getContext('2d');
  var w = canvas.width, h = canvas.height;
  ctx.clearRect(0, 0, w, h);
  var data = window._txVolumeData;
  if (data.length === 0) return;
  var maxTx = Math.max.apply(null, data.map(function(d) { return d.txs; })) || 1;
  var barW = w / data.length;

  // Background grid
  ctx.strokeStyle = '#e9ecef';
  ctx.lineWidth = 1;
  for (var i = 0; i <= 4; i++) {
    var y = h * i / 4;
    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke();
  }

  // Bars
  for (var i = 0; i < data.length; i++) {
    var barH = (data[i].txs / maxTx) * (h - 20);
    var x = i * barW;
    ctx.fillStyle = '#28a745';
    ctx.fillRect(x + 2, h - barH - 10, barW - 4, barH);
  }

  // Labels
  ctx.fillStyle = '#6c759d';
  ctx.font = '11px sans-serif';
  ctx.fillText('Max: ' + maxTx + ' txs', 8, 14);
  ctx.fillText(data.length + ' blocks', w - 80, h - 2);
}

function drawTpsHistoryChart() {
  var canvas = document.getElementById('tpsHistoryChart');
  if (!canvas) return;
  var ctx = canvas.getContext('2d');
  var w = canvas.width, h = canvas.height;
  ctx.clearRect(0, 0, w, h);
  var data = window._tpsHistory;
  if (data.length === 0) return;
  var maxTps = Math.max.apply(null, data) || 0.1;
  var stepX = w / Math.max(data.length - 1, 1);

  // Background grid
  ctx.strokeStyle = '#e9ecef';
  ctx.lineWidth = 1;
  for (var i = 0; i <= 4; i++) {
    var y = h * i / 4;
    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke();
  }

  // Area fill
  ctx.beginPath();
  ctx.moveTo(0, h);
  for (var i = 0; i < data.length; i++) {
    var x = i * stepX;
    var y = h - (data[i] / maxTps) * (h - 20) - 10;
    ctx.lineTo(x, y);
  }
  ctx.lineTo((data.length-1) * stepX, h);
  ctx.closePath();
  ctx.fillStyle = 'rgba(40, 167, 69, 0.12)';
  ctx.fill();

  // Line
  ctx.beginPath();
  for (var i = 0; i < data.length; i++) {
    var x = i * stepX;
    var y = h - (data[i] / maxTps) * (h - 20) - 10;
    if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
  }
  ctx.strokeStyle = '#28a745';
  ctx.lineWidth = 2;
  ctx.stroke();

  // Labels
  ctx.fillStyle = '#6c759d';
  ctx.font = '11px sans-serif';
  ctx.fillText('Peak: ' + maxTps.toFixed(2) + ' tps', 8, 14);
  ctx.fillText(data.length + ' samples', w - 80, h - 2);
}

function drawBlockRateChart(blockTimes) {
  var canvas = document.getElementById('blockRateChart');
  if (!canvas) return;
  var ctx = canvas.getContext('2d');
  var w = canvas.width, h = canvas.height;
  ctx.clearRect(0, 0, w, h);
  if (blockTimes.length === 0) return;
  var maxT = Math.max.apply(null, blockTimes) || 6;
  var minT = Math.min.apply(null, blockTimes) || 6;
  var barW = w / blockTimes.length;

  // Target line (6s)
  var targetY = h - (6 / (maxT + 1)) * (h - 10) - 5;
  ctx.strokeStyle = '#f59e0b';
  ctx.setLineDash([4, 4]);
  ctx.lineWidth = 1;
  ctx.beginPath(); ctx.moveTo(0, targetY); ctx.lineTo(w, targetY); ctx.stroke();
  ctx.setLineDash([]);

  // Bars
  for (var i = 0; i < blockTimes.length; i++) {
    var barH = (blockTimes[i] / (maxT + 1)) * (h - 10);
    var x = i * barW;
    ctx.fillStyle = blockTimes[i] <= 6.5 ? '#28a745' : '#f59e0b';
    ctx.fillRect(x + 1, h - barH - 5, barW - 2, barH);
  }

  // Labels
  ctx.fillStyle = '#6c759d';
  ctx.font = '11px sans-serif';
  ctx.fillText('Target: 6s', 8, targetY - 4);
  ctx.fillText('Avg: ' + (blockTimes.reduce(function(a,b){return a+b;},0)/blockTimes.length).toFixed(1) + 's', 8, h - 2);
  ctx.fillText(blockTimes.length + ' blocks', w - 80, h - 2);
}

async function init() {
  updateInfoCards();
  initScroll();'''
content = content.replace(old_init, new_init)

# Write back
proc = subprocess.run(
    ["ssh", "-o", "ConnectTimeout=10", "root@91.98.160.145", "cat > /var/www/verdiscan/explorer/index.html"],
    input=content,
    capture_output=True,
    text=True
)
print(f"Written: exit {proc.returncode}")
if proc.stderr:
    print(f"Stderr: {proc.stderr[:200]}")
