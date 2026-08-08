import sys

content = open("/dev/stdin").read() if False else None

# Read the remote file content via SSH
import subprocess
result = subprocess.run(
    ["ssh", "-o", "ConnectTimeout=10", "root@91.98.160.145", "cat /var/www/verdiscan/explorer/index.html"],
    capture_output=True, text=True
)
content = result.stdout

# 1. Add Top Accounts tab button after Accounts button
old_btn = '    <button class="tab" data-t="accounts" onclick="switchTab(\'accounts\')">Accounts</button>\n  </div>'
new_btn = '''    <button class="tab" data-t="accounts" onclick="switchTab('accounts')">Accounts</button>
    <button class="tab" data-t="topaccounts" onclick="switchTab('topaccounts')">Top Accounts</button>
  </div>'''
content = content.replace(old_btn, new_btn)

# 2. Add Top Accounts tab content before the Modal div
old_close = "  </div>\n\n<!-- Modal -->"
new_close = """  </div>

  <!-- Top Accounts -->
  <div class="tab-content" id="tab-topaccounts">
    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">Top Accounts by Stake</span>
        <span class="panel-link" id="topAcctCount">Loading...</span>
      </div>
      <table class="tbl">
        <thead><tr><th>RANK</th><th>ADDRESS</th><th>NAME</th><th>STAKE (VRDX)</th><th>GREEN SCORE</th><th>VALIDATOR</th></tr></thead>
        <tbody id="topAccountsTable">
          <tr><td colspan="6" style="text-align:center;padding:20px"><span class="skel" style="width:100%"></span></td></tr>
        </tbody>
      </table>
    </div>
  </div>

<!-- Modal -->"""
content = content.replace(old_close, new_close)

# 3. Add loadTopAccounts function before the init function
old_init = "// Init\nasync function init() {"
new_init = """// ===== Top Accounts =====
async function loadTopAccounts() {
  const tbody = document.getElementById('topAccountsTable');
  if (!tbody) return;
  tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:20px;color:var(--text-3)">Loading accounts...</td></tr>';

  try {
    const vals = await rpc('dpos_allValidators', []);
    if (!vals || !Array.isArray(vals) || vals.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:20px;color:var(--text-3)">No accounts found</td></tr>';
      return;
    }

    // Fetch stake, name, and green score for each validator in parallel
    const accountData = await Promise.all(vals.map(async (addr, i) => {
      let stake = 0, name = 'Validator ' + (i + 1), greenScore = 0;
      try { const s = await rpc('dpos_validatorStake', [addr]); stake = BigInt(s || 0); } catch(e) {}
      try { const n = await rpc('dpos_validatorName', [addr]); if (n) name = n; } catch(e) {}
      try { const gs = await rpc('eco_getGreenScore', [addr]); greenScore = gs || 0; } catch(e) {}
      return { addr, stake, name, greenScore };
    }));

    // Sort by stake descending
    accountData.sort((a, b) => b.stake > a.stake ? 1 : b.stake < a.stake ? -1 : 0);

    // Update count
    const countEl = document.getElementById('topAcctCount');
    if (countEl) countEl.textContent = accountData.length + ' accounts';

    tbody.innerHTML = accountData.map((a, i) => {
      const stakeVRDX = (Number(a.stake) / 10**9).toLocaleString(undefined, {maximumFractionDigits: 2});
      const shortAddr = a.addr.slice(0, 8) + '...' + a.addr.slice(-6);
      const rank = i + 1;
      const rankBadge = rank <= 3 ? '<span style="color:#f59e0b;font-weight:700">#' + rank + '</span>' : '#' + rank;
      const valBadge = '<span class="badge badge-sm" style="background:#dcfce7;color:#15803d">Validator</span>';
      const greenBadge = a.greenScore > 0
        ? '<span class="badge badge-sm" style="background:#dcfce7;color:#16a34a">&#127807; ' + a.greenScore + '</span>'
        : '<span style="color:var(--text-3)">-</span>';
      return '<tr style="cursor:pointer" onclick="switchTab(\'accounts\');searchAccount(\'' + a.addr + '\')">' +
        '<td style="font-family:var(--mono);font-weight:600">' + rankBadge + '</td>' +
        '<td style="font-family:var(--mono);font-size:13px">' + shortAddr + '</td>' +
        '<td style="font-weight:500">' + a.name + '</td>' +
        '<td style="font-family:var(--mono);font-weight:600">' + stakeVRDX + '</td>' +
        '<td>' + greenBadge + '</td>' +
        '<td>' + valBadge + '</td>' +
        '</tr>';
    }).join('');
  } catch(e) {
    console.log('Top accounts error:', e);
    tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:20px;color:#dc2626">Error loading accounts</td></tr>';
  }
}

// Init
async function init() {"""
content = content.replace(old_init, new_init)

# 4. Add loadTopAccounts to switchTab handler
old_switch = "  if (t==='eco') loadEgo();"
new_switch = "  if (t==='eco') loadEco();\n  if (t==='topaccounts') loadTopAccounts();"

# Try both possible spellings
if old_switch in content:
    content = content.replace(old_switch, new_switch)
else:
    old_switch2 = "  if (t==='eco') loadEco();"
    new_switch2 = "  if (t==='eco') loadEco();\n  if (t==='topaccounts') loadTopAccounts();"
    content = content.replace(old_switch2, new_switch2)

# Write back
proc = subprocess.run(
    ["ssh", "-o", "ConnectTimeout=10", "root@91.98.160.145", "cat > /var/www/verdiscan/explorer/index.html"],
    input=content,
    capture_output=True,
    text=True
)
print("Top Accounts tab added. Exit:", proc.returncode)
if proc.stderr:
    print("Stderr:", proc.stderr[:200])
