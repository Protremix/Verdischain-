import subprocess

result = subprocess.run(
    ["ssh", "-o", "ConnectTimeout=10", "root@91.98.160.145", "cat /var/www/verdiscan/explorer/index.html"],
    capture_output=True, text=True
)
content = result.stdout

# 1. Add tab button after Top Accounts
old_tab_buttons = '''    <button class="tab" data-t="topaccounts" onclick="switchTab('topaccounts')">Top Accounts</button>'''
new_tab_buttons = '''    <button class="tab" data-t="topaccounts" onclick="switchTab('topaccounts')">Top Accounts</button>
    <button class="tab" data-t="holders" onclick="switchTab('holders')">Token Holders</button>'''
content = content.replace(old_tab_buttons, new_tab_buttons)

# 2. Add tab content section after Top Accounts section (before <!-- Modal -->)
old_top_accounts_end = '''  </div>

<!-- Modal -->'''
new_top_accounts_end = '''  </div>

  <!-- Token Holders -->
  <div class="tab-content" id="tab-holders">
    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">VRDX Token Holders</span>
        <span class="panel-link" id="holdersCount">Loading...</span>
      </div>
      <table class="tbl">
        <thead><tr><th>RANK</th><th>ADDRESS</th><th>TYPE</th><th>BALANCE (VRDX)</th><th>FREE</th><th>RESERVED</th></tr></thead>
        <tbody id="holdersTable">
          <tr><td colspan="6" style="text-align:center;padding:20px"><span class="skel" style="width:100%"></span></td></tr>
        </tbody>
      </table>
    </div>
  </div>

<!-- Modal -->'''
content = content.replace(old_top_accounts_end, new_top_accounts_end, 1)

# 3. Add JavaScript to load token holders
# Find the loadTopAccounts function and add loadHolders after it
old_top_accounts_js = '''window.loadTopAccounts = loadTopAccounts;'''
new_js = '''window.loadTopAccounts = loadTopAccounts;

async function loadHolders() {
  const tbody = document.getElementById('holdersTable');
  if (!tbody) return;
  try {
    const resp = await fetch('/api/v1/token/holders');
    if (!resp.ok) throw new Error('API error');
    const json = await resp.json();
    if (!json.success || !json.data) throw new Error('No data');

    document.getElementById('holdersCount').textContent = json.count + ' holders';

    tbody.innerHTML = json.data.map((h, i) => {
      const isModule = h.address.startsWith('Module:');
      const addrDisplay = isModule
        ? '<span style="font-family:JetBrains Mono,monospace;font-size:12px;color:var(--text-2)">' + h.address + '</span>'
        : '<a href="#" onclick="searchAccount(\\''+h.address+'\\');return false" style="font-family:JetBrains Mono,monospace;font-size:12px">' + h.address.substring(0,8) + '...' + h.address.slice(-6) + '</a>';
      const typeBadge = isModule
        ? '<span class="badge" style="background:#ede9fe;color:#5b21b6;padding:2px 8px;border-radius:4px;font-size:11px">Module</span>'
        : h.is_validator
          ? '<span class="badge" style="background:#dcfce7;color:#166534;padding:2px 8px;border-radius:4px;font-size:11px">Validator</span>'
          : '<span class="badge" style="background:#f1f5f9;color:#475569;padding:2px 8px;border-radius:4px;font-size:11px">Account</span>';
      return '<tr>' +
        '<td>' + (i+1) + '</td>' +
        '<td>' + addrDisplay + '</td>' +
        '<td>' + typeBadge + '</td>' +
        '<td style="font-family:JetBrains Mono,monospace">' + h.balance_formatted + '</td>' +
        '<td style="font-family:JetBrains Mono,monospace;color:var(--text-2)">' + h.free_formatted + '</td>' +
        '<td style="font-family:JetBrains Mono,monospace;color:var(--text-3)">' + h.reserved_formatted + '</td>' +
        '</tr>';
    }).join('');
  } catch(e) {
    tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:20px;color:var(--text-3)">Failed to load token holders</td></tr>';
    console.error('Holders error:', e);
  }
}
window.loadHolders = loadHolders;'''

content = content.replace(old_top_accounts_js, new_js)

# 4. Add holders loading to switchTab
old_switch_top = '''    if (tab === 'topaccounts') loadTopAccounts();'''
new_switch = '''    if (tab === 'topaccounts') loadTopAccounts();
    if (tab === 'holders') loadHolders();'''
content = content.replace(old_switch_top, new_switch)

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
