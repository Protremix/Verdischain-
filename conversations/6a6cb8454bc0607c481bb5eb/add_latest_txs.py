#!/usr/bin/env python3
"""Add Latest Transactions box to Verdiscan explorer overview."""

EXP_PATH = "/var/www/verdiscan/explorer/index.html"

with open(EXP_PATH, "r") as f:
    html = f.read()

# 1. Add Latest Transactions panel below the grid-2 in overview
old_overview = '''      <div class="panel">
        <div class="panel-header"><span class="panel-title">Latest Extrinsics</span><a class="panel-link" onclick="switchTab('extrinsics')">View all →</a></div>
        <table class="tbl"><thead><tr><th>TYPE</th><th>METHOD / DATA</th><th>HASH</th><th>BLOCK</th></tr></thead><tbody id="latestExts"></tbody></table>
      </div>
    </div>
  </div>'''

new_overview = '''      <div class="panel">
        <div class="panel-header"><span class="panel-title">Latest Extrinsics</span><a class="panel-link" onclick="switchTab('extrinsics')">View all →</a></div>
        <table class="tbl"><thead><tr><th>TYPE</th><th>METHOD / DATA</th><th>HASH</th><th>BLOCK</th></tr></thead><tbody id="latestExts"></tbody></table>
      </div>
    </div>
    <!-- Latest Transactions -->
    <div class="panel" style="margin-top:16px">
      <div class="panel-header">
        <span class="panel-title">Latest Transactions</span>
        <a class="panel-link" onclick="window.location.href='/transactions/'">View all →</a>
      </div>
      <table class="tbl"><thead><tr><th>BLOCK</th><th>HASH</th><th>METHOD</th><th>SIGNER</th><th>VALUE</th></tr></thead><tbody id="latestTxs"></tbody></table>
    </div>
  </div>'''

if 'latestTxs' not in html:
    html = html.replace(old_overview, new_overview)
    print("Added Latest Transactions panel to overview")

# 2. Add loadLatestTxs function after renderLatestExts (before showExtrinsic)
old_fn_end = '''// Show transaction detail modal
function showExtrinsic('''

new_fn = '''// Load latest transactions into overview
function loadLatestTxs() {
  const tbody = document.getElementById('latestTxs');
  if (!tbody) return;
  let html = '';
  let count = 0;
  for (let i = 0; i < blocksData.length && count < 10; i++) {
    const b = blocksData[i];
    const exts = b.exts || [];
    for (let j = 0; j < exts.length && count < 10; j++) {
      const ext = decodeExtrinsic(exts[j], b.hash, b.num);
      if (!ext) continue;
      if (ext.type !== 'Signed') continue;
      const safeSigner = (ext.signer || '—').replace(/'/g, "\\'");
      const val = ext.value || '0';
      html += '<tr style="cursor:pointer" onclick="showExtrinsic(\\''+ext.hash+'\\', '+b.num+', \\''+ext.type+'\\', \\''+ext.method+'\\', \\''+safeSigner+'\\', \\'\\')">' +
        '<td class="hash hash-accent">#' + b.num + '</td>' +
        '<td class="hash">' + ext.hash + '</td>' +
        '<td><span class="badge ' + ext.badge + '">' + ext.method + '</span></td>' +
        '<td class="hash">' + (ext.signer || '—') + '</td>' +
        '<td>' + val + '</td>' +
        '</tr>';
      count++;
    }
  }
  if (count === 0) {
    tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:var(--text-3);padding:24px">Waiting for signed transactions...</td></tr>';
  } else {
    tbody.innerHTML = html;
  }
}

// Show transaction detail modal
function showExtrinsic('''

if 'loadLatestTxs' not in html:
    html = html.replace(old_fn_end, new_fn)
    print("Added loadLatestTxs function")

# 3. Call loadLatestTxs after loadLatestExts in the init flow
old_call = '''  try { await loadLatestBlocks(); } catch(e) { console.log("blocks err:", e); }'''
new_call = '''  try { await loadLatestBlocks(); loadLatestTxs(); } catch(e) { console.log("blocks err:", e); }'''

if 'loadLatestTxs()' not in html.split('try { await loadLatestBlocks()')[0]:
    html = html.replace(old_call, new_call)
    print("Added loadLatestTxs call to init flow")

# 4. Also call loadLatestTxs in the interval
old_interval = 'setInterval(loadLatestBlocks, 10000);'
new_interval = 'setInterval(function() { loadLatestBlocks(); loadLatestTxs(); }, 10000);'

if 'loadLatestTxs()' not in html.split('setInterval(')[0]:
    html = html.replace(old_interval, new_interval)
    print("Added loadLatestTxs to refresh interval")

with open(EXP_PATH, "w") as f:
    f.write(html)
print(f"File saved: {len(html)} bytes")
