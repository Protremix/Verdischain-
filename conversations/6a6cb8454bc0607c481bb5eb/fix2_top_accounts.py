import subprocess, re

# Read the remote file
result = subprocess.run(
    ["ssh", "-o", "ConnectTimeout=10", "root@91.98.160.145", "cat /var/www/verdiscan/explorer/index.html"],
    capture_output=True, text=True
)
content = result.stdout

# 1. Fix the broken loadValidators function - restore the original line
broken_line = "      try { const n = await rpc('dpos_validatorName', [addr]); if (n) { name = Array.isArray(n) ? String.fromCharCode.apply(null, n) : n; } } catch(e) {}"
fixed_line = "      rpc('dpos_validatorName', [id])"

if broken_line in content:
    content = content.replace(broken_line, fixed_line)
    print("Fixed loadValidators broken line")
else:
    print("WARNING: broken line not found exactly, trying regex")
    # Try to find and fix it
    content = re.sub(
        r"try \{ const n = await rpc\('dpos_validatorName', \[addr\]\).*?\} catch\(e\) \{\}",
        "rpc('dpos_validatorName', [id])",
        content
    )

# 2. Now add the loadTopAccounts function before "// Init"
# Find the "// Init" section
init_marker = "// Init\nasync function init() {"

load_top_accounts_func = """// ===== Top Accounts =====
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
      try {
        const n = await rpc('dpos_validatorName', [addr]);
        if (n) {
          if (Array.isArray(n)) {
            name = String.fromCharCode.apply(null, n).trim();
          } else if (typeof n === 'string') {
            name = n.trim();
          }
        }
      } catch(e) {}
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
        ? '<span class="badge badge-sm" style="background:#dcfce7;color:#16a34a">Green ' + a.greenScore + '</span>'
        : '<span style="color:var(--text-3)">-</span>';
      return '<tr style="cursor:pointer" onclick="switchTab(\\'accounts\\');searchAccount(\\'' + a.addr + '\\')">' +
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

"""

if init_marker in content:
    content = content.replace(init_marker, load_top_accounts_func + init_marker)
    print("Added loadTopAccounts function")
else:
    print("ERROR: init marker not found")
    # Try alternative
    if "async function init() {" in content:
        content = content.replace("async function init() {", load_top_accounts_func + "async function init() {", 1)
        print("Added loadTopAccounts function (alternative)")

# Write back
proc = subprocess.run(
    ["ssh", "-o", "ConnectTimeout=10", "root@91.98.160.145", "cat > /var/www/verdiscan/explorer/index.html"],
    input=content,
    capture_output=True,
    text=True
)
print("Written. Exit:", proc.returncode)
if proc.stderr:
    print("Stderr:", proc.stderr[:200])
