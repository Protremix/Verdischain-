with open('src/web/dashboard.html', 'r') as f:
    content = f.read()

# Add Monitoring tab before Security
old_tabs = """    <div class="tab" onclick="showTab('security',this)">🛡️ Security</div>"""
new_tabs = """    <div class="tab" onclick="showTab('monitoring',this)">📊 Monitoring</div>
    <div class="tab" onclick="showTab('security',this)">🛡️ Security</div>"""
content = content.replace(old_tabs, new_tabs)

# Add monitoring section before security section
monitoring_section = """  <!-- Monitoring Tab -->
  <div class="section" id="tab-monitoring">
    <h2>📊 Network Monitoring</h2>
    
    <div class="card" style="margin-bottom:16px">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <h3 id="monitorStatus" style="color:var(--accent)">Checking...</h3>
        <div id="monitorUptime" style="font-size:0.9rem;color:var(--muted)"></div>
      </div>
    </div>

    <div class="grid grid-4" style="margin-bottom:16px" id="monitorStats"></div>

    <div class="card" style="margin-bottom:16px">
      <h3>Chain Health</h3>
      <table style="width:100%;border-collapse:collapse" id="monitorChain"></table>
    </div>

    <div class="grid grid-2">
      <div class="card">
        <h3>Performance</h3>
        <div id="monitorPerf"></div>
      </div>
      <div class="card">
        <h3>Mempool</h3>
        <div id="monitorMempool"></div>
      </div>
    </div>

    <div class="card" style="margin-top:16px">
      <h3>Auto-Update</h3>
      <p class="subtle">The node can be updated without losing state:</p>
      <div style="padding:8px;background:var(--bg);border-radius:8px;margin:8px 0;font-family:monospace;font-size:0.85rem;color:var(--accent)">
        sudo bash deploy/update.sh &lt;archive-url-or-path&gt;
      </div>
      <p class="subtle" style="font-size:0.85rem">Backs up current version, applies update, auto-rolls back if health check fails.</p>
    </div>

    <div class="card" style="margin-top:16px">
      <h3>Monitoring Endpoints</h3>
      <table style="width:100%;border-collapse:collapse">
        <tr><td style="padding:8px;color:var(--muted)">Health Check</td><td class="mono" style="padding:8px;font-size:0.85rem">/api/monitoring/health</td></tr>
        <tr style="border-top:1px solid var(--border)"><td style="padding:8px;color:var(--muted)">Uptime Badge</td><td class="mono" style="padding:8px;font-size:0.85rem">/api/monitoring/uptime</td></tr>
        <tr style="border-top:1px solid var(--border)"><td style="padding:8px;color:var(--muted)">Security Audit</td><td class="mono" style="padding:8px;font-size:0.85rem">/api/security/audit</td></tr>
        <tr style="border-top:1px solid var(--border)"><td style="padding:8px;color:var(--muted)">Network Info</td><td class="mono" style="padding:8px;font-size:0.85rem">/api/network/info</td></tr>
      </table>
      <p class="subtle" style="font-size:0.85rem;margin-top:8px">Use these with UptimeRobot, Pingdom, or Better Stack.</p>
    </div>
  </div>

  <!-- Security Tab -->"""

content = content.replace("  <!-- Security Tab -->", monitoring_section)

# Add showTab handler
content = content.replace(
    "  if (name === 'security') loadSecurity();",
    "  if (name === 'security') loadSecurity();\n  if (name === 'monitoring') loadMonitoring();"
)

# Add monitoring JavaScript before security JS
monitoring_js = """// Monitoring Tab
let monitorInterval = null;
async function loadMonitoring() {
  await updateMonitoring();
  if (monitorInterval) clearInterval(monitorInterval);
  monitorInterval = setInterval(updateMonitoring, 10000);
}

async function updateMonitoring() {
  try {
    const h = await fetch(API + '/api/monitoring/health').then(r => r.json());
    const statusEl = document.getElementById('monitorStatus');
    if (h.status === 'healthy') {
      statusEl.innerHTML = '✅ Network Healthy';
      statusEl.style.color = 'var(--accent)';
    } else {
      statusEl.innerHTML = '⚠️ Network Issues Detected';
      statusEl.style.color = 'var(--destructive)';
    }
    document.getElementById('monitorUptime').textContent = 'Uptime: ' + h.uptime.human;
    
    document.getElementById('monitorStats').innerHTML = [
      { label: 'Block Height', value: h.chain.height, icon: '⛓️' },
      { label: 'Validators', value: h.consensus.validators, icon: '🔑' },
      { label: 'DEX Pools', value: h.dex.pools, icon: '💱' },
      { label: 'Mempool', value: h.mempool.size + '/' + h.mempool.maxSize, icon: '🏊' },
    ].map(s => '<div style="padding:12px;background:var(--bg);border-radius:8px;border:1px solid var(--border);text-align:center"><div style="font-size:1.3rem">' + s.icon + '</div><div style="font-size:1.1rem;font-weight:600;color:var(--accent)">' + s.value + '</div><div style="font-size:0.75rem;color:var(--muted)">' + s.label + '</div></div>').join('');
    
    document.getElementById('monitorChain').innerHTML = 
      '<tr><td style="padding:8px;color:var(--muted);width:200px">Chain Valid</td><td style="padding:8px;color:' + (h.chain.chainValid ? 'var(--accent)' : 'var(--destructive)') + '">' + (h.chain.chainValid ? '✅ Valid' : '❌ Invalid') + '</td></tr>' +
      '<tr style="border-top:1px solid var(--border)"><td style="padding:8px;color:var(--muted)">Total Blocks</td><td style="padding:8px">' + h.chain.totalBlocks + '</td></tr>' +
      '<tr style="border-top:1px solid var(--border)"><td style="padding:8px;color:var(--muted)">Last Block</td><td style="padding:8px">' + h.chain.blockStalenessHuman + ' ago</td></tr>' +
      '<tr style="border-top:1px solid var(--border)"><td style="padding:8px;color:var(--muted)">Block Time</td><td style="padding:8px">' + (h.chain.blockTime / 1000) + 's</td></tr>' +
      '<tr style="border-top:1px solid var(--border)"><td style="padding:8px;color:var(--muted)">Version</td><td style="padding:8px">v' + h.version + '</td></tr>' +
      '<tr style="border-top:1px solid var(--border)"><td style="padding:8px;color:var(--muted)">Chain ID</td><td style="padding:8px">' + h.chainId + '</td></tr>';
    
    document.getElementById('monitorPerf').innerHTML = 
      '<div style="display:flex;justify-content:space-between;padding:8px 0"><span style="color:var(--muted)">TPS (last 100 blocks)</span><span style="font-weight:600;color:var(--accent)">' + h.performance.tps + '</span></div>' +
      '<div style="display:flex;justify-content:space-between;padding:8px 0;border-top:1px solid var(--border)"><span style="color:var(--muted)">Avg TX per block</span><span style="font-weight:600">' + h.performance.avgBlockTx + '</span></div>';
    
    const mempoolPct = Math.round((h.mempool.size / h.mempool.maxSize) * 100);
    document.getElementById('monitorMempool').innerHTML = 
      '<div style="display:flex;justify-content:space-between;padding:8px 0"><span style="color:var(--muted)">Pending TXs</span><span style="font-weight:600">' + h.mempool.size + '</span></div>' +
      '<div style="padding:8px 0;border-top:1px solid var(--border)"><div style="background:var(--bg);border-radius:4px;overflow:hidden;height:8px"><div style="background:' + (mempoolPct > 80 ? 'var(--destructive)' : 'var(--accent)') + ';height:100%;width:' + mempoolPct + '%"></div></div><div style="font-size:0.75rem;color:var(--muted);margin-top:4px">' + mempoolPct + '% of max (' + h.mempool.size + '/' + h.mempool.maxSize + ')</div></div>';
  } catch (e) {
    console.error('Monitoring error:', e);
  }
}

// Security Tab"""

content = content.replace("// Security Tab", monitoring_js)

with open('src/web/dashboard.html', 'w') as f:
    f.write(content)

print("Monitoring dashboard tab added")
