import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add .btn-export CSS
btn_export_css = """
.btn-export{padding:3px 8px;font-size:11px;font-weight:600;color:var(--accent);background:var(--accent-glow);border:1px solid rgba(22,163,74,0.3);border-radius:var(--radius-sm);cursor:pointer;transition:all .2s;display:inline-flex;align-items:center;gap:4px}
.btn-export:hover{background:var(--accent);color:#ffffff;border-color:var(--accent)}
"""

if ".btn-export" not in content:
    content = content.replace("/* Table */", btn_export_css + "\n/* Table */")

# 2. Add API tab button in .tabs
old_tab_transfers = '<button class="tab" data-t="transfers" onclick="switchTab(\'transfers\')">Transfers</button>'
new_tab_api = old_tab_transfers + '\n    <button class="tab" data-t="api" onclick="switchTab(\'api\')">API</button>'

if 'data-t="api"' not in content:
    content = content.replace(old_tab_transfers, new_tab_api)

# 3. Add Export buttons to Blocks panel header and add id="blocksTable" to table
old_blocks_header = '<div class="panel-header"><span class="panel-title">All Blocks</span><span style="font-size:12px;color:var(--text-3)" id="blockCount"></span></div>'
new_blocks_header = '''<div class="panel-header">
        <span class="panel-title">All Blocks</span>
        <div style="display:flex;align-items:center;gap:8px">
          <span style="font-size:12px;color:var(--text-3)" id="blockCount"></span>
          <button class="btn-export" onclick="exportToCSV('blocksTable', 'verdiscan_blocks.csv')">Export CSV</button>
          <button class="btn-export" onclick="exportToJSON('blocksTable', 'verdiscan_blocks.json')">Export JSON</button>
        </div>
      </div>'''

if "exportToCSV('blocksTable'" not in content:
    content = content.replace(old_blocks_header, new_blocks_header)
    content = content.replace(
        '<table class="tbl"><thead><tr><th>BLOCK</th><th>TIME</th><th>EXT</th><th>EXTRINSICS ROOT</th><th>HASH</th></tr></thead><tbody id="allBlocks"></tbody></table>',
        '<table class="tbl" id="blocksTable"><thead><tr><th>BLOCK</th><th>TIME</th><th>EXT</th><th>EXTRINSICS ROOT</th><th>HASH</th></tr></thead><tbody id="allBlocks"></tbody></table>'
    )

# 4. Add Export buttons to Holders panel header
old_holders_header = '''      <div class="panel-header">
        <span class="panel-title">VRDX Token Holders</span>
        <span class="panel-link" id="holdersCount">Loading...</span>
      </div>'''

new_holders_header = '''      <div class="panel-header">
        <span class="panel-title">VRDX Token Holders</span>
        <div style="display:flex;align-items:center;gap:8px">
          <span style="font-size:12px;color:var(--text-3)" id="holdersCount">Loading...</span>
          <button class="btn-export" onclick="exportToCSV('holdersTable', 'verdiscan_token_holders.csv')">Export CSV</button>
          <button class="btn-export" onclick="exportToJSON('holdersTable', 'verdiscan_token_holders.json')">Export JSON</button>
        </div>
      </div>'''

if "exportToCSV('holdersTable'" not in content:
    content = content.replace(old_holders_header, new_holders_header)

# 5. Add Export buttons to Transfers panel header
old_transfers_header = '''      <div class="panel-header">
        <span class="panel-title">VRDX Token Transfers</span>
        <span class="panel-link" id="transfersCount">Loading...</span>
      </div>'''

new_transfers_header = '''      <div class="panel-header">
        <span class="panel-title">VRDX Token Transfers</span>
        <div style="display:flex;align-items:center;gap:8px">
          <span style="font-size:12px;color:var(--text-3)" id="transfersCount">Loading...</span>
          <button class="btn-export" onclick="exportToCSV('transfersTable', 'verdiscan_transfers.csv')">Export CSV</button>
          <button class="btn-export" onclick="exportToJSON('transfersTable', 'verdiscan_transfers.json')">Export JSON</button>
        </div>
      </div>'''

if "exportToCSV('transfersTable'" not in content:
    content = content.replace(old_transfers_header, new_transfers_header)

# 6. Add tab-content id="tab-api"
api_tab_html = '''
  <!-- API Documentation -->
  <div class="tab-content" id="tab-api">
    <div style="display:flex;flex-direction:column;gap:20px">
      <!-- REST API Section -->
      <div class="panel">
        <div class="panel-header">
          <span class="panel-title">REST API Endpoints</span>
          <span style="font-size:12px;color:var(--text-3)">Base URL: https://verdischain.com</span>
        </div>
        <div style="overflow-x:auto">
          <table class="tbl">
            <thead>
              <tr>
                <th style="width:20%">ENDPOINT</th>
                <th style="width:10%">METHOD</th>
                <th style="width:25%">DESCRIPTION</th>
                <th style="width:45%">EXAMPLE CURL</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><code class="mono" style="color:var(--accent);font-weight:600">/api/v1/health</code></td>
                <td><span class="badge" style="background:rgba(22,163,74,.15);color:var(--accent)">GET</span></td>
                <td>Check network node health and API status</td>
                <td><pre class="mono" style="background:#1e293b;color:#f8fafc;padding:6px 10px;border-radius:4px;font-size:11px;margin:0;white-space:pre-wrap;word-break:break-all">curl -s https://verdischain.com/api/v1/health</pre></td>
              </tr>
              <tr>
                <td><code class="mono" style="color:var(--accent);font-weight:600">/api/v1/block/latest</code></td>
                <td><span class="badge" style="background:rgba(22,163,74,.15);color:var(--accent)">GET</span></td>
                <td>Get the latest block details</td>
                <td><pre class="mono" style="background:#1e293b;color:#f8fafc;padding:6px 10px;border-radius:4px;font-size:11px;margin:0;white-space:pre-wrap;word-break:break-all">curl -s https://verdischain.com/api/v1/block/latest</pre></td>
              </tr>
              <tr>
                <td><code class="mono" style="color:var(--accent);font-weight:600">/api/v1/block/:num</code></td>
                <td><span class="badge" style="background:rgba(22,163,74,.15);color:var(--accent)">GET</span></td>
                <td>Get block details by block number</td>
                <td><pre class="mono" style="background:#1e293b;color:#f8fafc;padding:6px 10px;border-radius:4px;font-size:11px;margin:0;white-space:pre-wrap;word-break:break-all">curl -s https://verdischain.com/api/v1/block/100</pre></td>
              </tr>
              <tr>
                <td><code class="mono" style="color:var(--accent);font-weight:600">/api/v1/validators</code></td>
                <td><span class="badge" style="background:rgba(22,163,74,.15);color:var(--accent)">GET</span></td>
                <td>List active DPoS validators and stakes</td>
                <td><pre class="mono" style="background:#1e293b;color:#f8fafc;padding:6px 10px;border-radius:4px;font-size:11px;margin:0;white-space:pre-wrap;word-break:break-all">curl -s https://verdischain.com/api/v1/validators</pre></td>
              </tr>
              <tr>
                <td><code class="mono" style="color:var(--accent);font-weight:600">/api/v1/dex/pools</code></td>
                <td><span class="badge" style="background:rgba(22,163,74,.15);color:var(--accent)">GET</span></td>
                <td>List AMM DEX liquidity pools and reserves</td>
                <td><pre class="mono" style="background:#1e293b;color:#f8fafc;padding:6px 10px;border-radius:4px;font-size:11px;margin:0;white-space:pre-wrap;word-break:break-all">curl -s https://verdischain.com/api/v1/dex/pools</pre></td>
              </tr>
              <tr>
                <td><code class="mono" style="color:var(--accent);font-weight:600">/api/v1/eco/metrics</code></td>
                <td><span class="badge" style="background:rgba(22,163,74,.15);color:var(--accent)">GET</span></td>
                <td>Fetch green energy & carbon credit metrics</td>
                <td><pre class="mono" style="background:#1e293b;color:#f8fafc;padding:6px 10px;border-radius:4px;font-size:11px;margin:0;white-space:pre-wrap;word-break:break-all">curl -s https://verdischain.com/api/v1/eco/metrics</pre></td>
              </tr>
              <tr>
                <td><code class="mono" style="color:var(--accent);font-weight:600">/api/v1/token/holders</code></td>
                <td><span class="badge" style="background:rgba(22,163,74,.15);color:var(--accent)">GET</span></td>
                <td>List top VRDX token holders and balances</td>
                <td><pre class="mono" style="background:#1e293b;color:#f8fafc;padding:6px 10px;border-radius:4px;font-size:11px;margin:0;white-space:pre-wrap;word-break:break-all">curl -s https://verdischain.com/api/v1/token/holders</pre></td>
              </tr>
              <tr>
                <td><code class="mono" style="color:var(--accent);font-weight:600">/api/v1/faucet/stats</code></td>
                <td><span class="badge" style="background:rgba(22,163,74,.15);color:var(--accent)">GET</span></td>
                <td>Get testnet faucet distribution statistics</td>
                <td><pre class="mono" style="background:#1e293b;color:#f8fafc;padding:6px 10px;border-radius:4px;font-size:11px;margin:0;white-space:pre-wrap;word-break:break-all">curl -s https://verdischain.com/api/v1/faucet/stats</pre></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Substrate RPC Section -->
      <div class="panel">
        <div class="panel-header">
          <span class="panel-title">Substrate RPC Methods</span>
          <span style="font-size:12px;color:var(--text-3)">Endpoint: https://verdischain.com/rpc</span>
        </div>
        <div style="overflow-x:auto">
          <table class="tbl">
            <thead>
              <tr>
                <th style="width:20%">METHOD</th>
                <th style="width:10%">TYPE</th>
                <th style="width:25%">DESCRIPTION</th>
                <th style="width:45%">EXAMPLE CURL</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><code class="mono" style="color:var(--accent);font-weight:600">chain_getBlock</code></td>
                <td><span class="badge" style="background:#e0f2fe;color:#0369a1">POST</span></td>
                <td>Get header and extrinsics of a block</td>
                <td><pre class="mono" style="background:#1e293b;color:#f8fafc;padding:6px 10px;border-radius:4px;font-size:11px;margin:0;white-space:pre-wrap;word-break:break-all">curl -s -H "Content-Type: application/json" -d \'{"jsonrpc":"2.0","method":"chain_getBlock","params":[],"id":1}\' https://verdischain.com/rpc</pre></td>
              </tr>
              <tr>
                <td><code class="mono" style="color:var(--accent);font-weight:600">chain_getHeader</code></td>
                <td><span class="badge" style="background:#e0f2fe;color:#0369a1">POST</span></td>
                <td>Get block header by hash or latest</td>
                <td><pre class="mono" style="background:#1e293b;color:#f8fafc;padding:6px 10px;border-radius:4px;font-size:11px;margin:0;white-space:pre-wrap;word-break:break-all">curl -s -H "Content-Type: application/json" -d \'{"jsonrpc":"2.0","method":"chain_getHeader","params":[],"id":1}\' https://verdischain.com/rpc</pre></td>
              </tr>
              <tr>
                <td><code class="mono" style="color:var(--accent);font-weight:600">chain_getBlockHash</code></td>
                <td><span class="badge" style="background:#e0f2fe;color:#0369a1">POST</span></td>
                <td>Get block hash for a given block number</td>
                <td><pre class="mono" style="background:#1e293b;color:#f8fafc;padding:6px 10px;border-radius:4px;font-size:11px;margin:0;white-space:pre-wrap;word-break:break-all">curl -s -H "Content-Type: application/json" -d \'{"jsonrpc":"2.0","method":"chain_getBlockHash","params":[100],"id":1}\' https://verdischain.com/rpc</pre></td>
              </tr>
              <tr>
                <td><code class="mono" style="color:var(--accent);font-weight:600">chain_getFinalizedHead</code></td>
                <td><span class="badge" style="background:#e0f2fe;color:#0369a1">POST</span></td>
                <td>Get hash of the latest finalized block</td>
                <td><pre class="mono" style="background:#1e293b;color:#f8fafc;padding:6px 10px;border-radius:4px;font-size:11px;margin:0;white-space:pre-wrap;word-break:break-all">curl -s -H "Content-Type: application/json" -d \'{"jsonrpc":"2.0","method":"chain_getFinalizedHead","params":[],"id":1}\' https://verdischain.com/rpc</pre></td>
              </tr>
              <tr>
                <td><code class="mono" style="color:var(--accent);font-weight:600">system_health</code></td>
                <td><span class="badge" style="background:#e0f2fe;color:#0369a1">POST</span></td>
                <td>Get health status of the node (peers, syncing)</td>
                <td><pre class="mono" style="background:#1e293b;color:#f8fafc;padding:6px 10px;border-radius:4px;font-size:11px;margin:0;white-space:pre-wrap;word-break:break-all">curl -s -H "Content-Type: application/json" -d \'{"jsonrpc":"2.0","method":"system_health","params":[],"id":1}\' https://verdischain.com/rpc</pre></td>
              </tr>
              <tr>
                <td><code class="mono" style="color:var(--accent);font-weight:600">system_peers</code></td>
                <td><span class="badge" style="background:#e0f2fe;color:#0369a1">POST</span></td>
                <td>Get list of connected P2P network peers</td>
                <td><pre class="mono" style="background:#1e293b;color:#f8fafc;padding:6px 10px;border-radius:4px;font-size:11px;margin:0;white-space:pre-wrap;word-break:break-all">curl -s -H "Content-Type: application/json" -d \'{"jsonrpc":"2.0","method":"system_peers","params":[],"id":1}\' https://verdischain.com/rpc</pre></td>
              </tr>
              <tr>
                <td><code class="mono" style="color:var(--accent);font-weight:600">system_properties</code></td>
                <td><span class="badge" style="background:#e0f2fe;color:#0369a1">POST</span></td>
                <td>Get chain properties (ss58Format, tokenSymbol)</td>
                <td><pre class="mono" style="background:#1e293b;color:#f8fafc;padding:6px 10px;border-radius:4px;font-size:11px;margin:0;white-space:pre-wrap;word-break:break-all">curl -s -H "Content-Type: application/json" -d \'{"jsonrpc":"2.0","method":"system_properties","params":[],"id":1}\' https://verdischain.com/rpc</pre></td>
              </tr>
              <tr>
                <td><code class="mono" style="color:var(--accent);font-weight:600">system_version</code></td>
                <td><span class="badge" style="background:#e0f2fe;color:#0369a1">POST</span></td>
                <td>Get node client software version</td>
                <td><pre class="mono" style="background:#1e293b;color:#f8fafc;padding:6px 10px;border-radius:4px;font-size:11px;margin:0;white-space:pre-wrap;word-break:break-all">curl -s -H "Content-Type: application/json" -d \'{"jsonrpc":"2.0","method":"system_version","params":[],"id":1}\' https://verdischain.com/rpc</pre></td>
              </tr>
              <tr>
                <td><code class="mono" style="color:var(--accent);font-weight:600">dpos_allValidators</code></td>
                <td><span class="badge" style="background:#e0f2fe;color:#0369a1">POST</span></td>
                <td>Get list of all registered DPoS validator addresses</td>
                <td><pre class="mono" style="background:#1e293b;color:#f8fafc;padding:6px 10px;border-radius:4px;font-size:11px;margin:0;white-space:pre-wrap;word-break:break-all">curl -s -H "Content-Type: application/json" -d \'{"jsonrpc":"2.0","method":"dpos_allValidators","params":[],"id":1}\' https://verdischain.com/rpc</pre></td>
              </tr>
              <tr>
                <td><code class="mono" style="color:var(--accent);font-weight:600">dpos_validatorStake</code></td>
                <td><span class="badge" style="background:#e0f2fe;color:#0369a1">POST</span></td>
                <td>Get total stake for a validator address</td>
                <td><pre class="mono" style="background:#1e293b;color:#f8fafc;padding:6px 10px;border-radius:4px;font-size:11px;margin:0;white-space:pre-wrap;word-break:break-all">curl -s -H "Content-Type: application/json" -d \'{"jsonrpc":"2.0","method":"dpos_validatorStake","params":["5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY"],"id":1}\' https://verdischain.com/rpc</pre></td>
              </tr>
              <tr>
                <td><code class="mono" style="color:var(--accent);font-weight:600">eco_getGreenScore</code></td>
                <td><span class="badge" style="background:#e0f2fe;color:#0369a1">POST</span></td>
                <td>Get green score metric for node/validator</td>
                <td><pre class="mono" style="background:#1e293b;color:#f8fafc;padding:6px 10px;border-radius:4px;font-size:11px;margin:0;white-space:pre-wrap;word-break:break-all">curl -s -H "Content-Type: application/json" -d \'{"jsonrpc":"2.0","method":"eco_getGreenScore","params":[],"id":1}\' https://verdischain.com/rpc</pre></td>
              </tr>
              <tr>
                <td><code class="mono" style="color:var(--accent);font-weight:600">eco_getAllGreenValidators</code></td>
                <td><span class="badge" style="background:#e0f2fe;color:#0369a1">POST</span></td>
                <td>Get list of eco-certified green validators</td>
                <td><pre class="mono" style="background:#1e293b;color:#f8fafc;padding:6px 10px;border-radius:4px;font-size:11px;margin:0;white-space:pre-wrap;word-break:break-all">curl -s -H "Content-Type: application/json" -d \'{"jsonrpc":"2.0","method":"eco_getAllGreenValidators","params":[],"id":1}\' https://verdischain.com/rpc</pre></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
'''

# Place api_tab_html right after tab-transfers closing div
old_transfers_end = '  <!-- Token Transfers -->\n  <div class="tab-content" id="tab-transfers">'
if 'id="tab-api"' not in content:
    # find where tab-transfers ends (next element or before Modal)
    target = '<!-- Modal -->'
    if target in content:
        content = content.replace(target, api_tab_html + '\n' + target)

# 7. Add JS export functions exportToCSV and exportToJSON, and switchTab update
js_export_functions = '''
// Export Data Utilities
function exportToCSV(tableId, filename) {
  let el = typeof tableId === 'string' ? document.getElementById(tableId) : tableId;
  if (!el) return;
  let table = el.tagName === 'TABLE' ? el : el.closest('table') || el;
  let rows = Array.from(table.querySelectorAll('tr'));
  let csv = [];
  rows.forEach(row => {
    let cols = Array.from(row.querySelectorAll('th, td'));
    let rowData = cols.map(c => {
      let text = (c.innerText || c.textContent || '').trim().replace(/\\s+/g, ' ');
      text = text.replace(/"/g, '""');
      return '"' + text + '"';
    });
    if (rowData.length > 0) csv.push(rowData.join(','));
  });
  if (csv.length === 0) return;
  let blob = new Blob([csv.join('\\n')], { type: 'text/csv;charset=utf-8;' });
  let link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.setAttribute('download', filename || 'export.csv');
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

function exportToJSON(data, filename) {
  let jsonString = '';
  if (typeof data === 'string') {
    let el = document.getElementById(data);
    if (el) {
      let table = el.tagName === 'TABLE' ? el : el.closest('table') || el;
      let rows = Array.from(table.querySelectorAll('tr'));
      if (rows.length > 0) {
        let headerRow = rows.find(r => r.querySelector('th'));
        let headers = headerRow ? Array.from(headerRow.querySelectorAll('th')).map(th => th.innerText.trim().replace(/\\s+/g, ' ')) : [];
        let dataRows = rows.filter(r => r.querySelector('td'));
        let items = dataRows.map(row => {
          let cells = Array.from(row.querySelectorAll('td'));
          let obj = {};
          cells.forEach((td, idx) => {
            let key = headers[idx] || ('column_' + (idx + 1));
            obj[key] = td.innerText.trim().replace(/\\s+/g, ' ');
          });
          return obj;
        });
        jsonString = JSON.stringify(items, null, 2);
      }
    }
  } else {
    jsonString = JSON.stringify(data, null, 2);
  }
  if (!jsonString) return;
  let blob = new Blob([jsonString], { type: 'application/json;charset=utf-8;' });
  let link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.setAttribute('download', filename || 'export.json');
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
'''

if 'function exportToCSV(' not in content:
    content = content.replace("// Tab switching", js_export_functions + "\n// Tab switching")

# Update switchTab if needed
old_switch_tab_transfers = "if (t==='transfers') loadTransfers();"
new_switch_tab_api = "if (t==='transfers') loadTransfers();\n  if (t==='api') {}"

if "if (t==='api')" not in content:
    content = content.replace(old_switch_tab_transfers, new_switch_tab_api)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)

print("index.html updated successfully.")
