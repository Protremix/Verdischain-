import subprocess

result = subprocess.run(
    ["ssh", "-o", "ConnectTimeout=10", "root@91.98.160.145", "cat /var/www/verdiscan/explorer/index.html"],
    capture_output=True, text=True
)
content = result.stdout

# Add loadHolders function after loadTopAccounts function (before "async function init()")
old_init = '''async function init() {
  updateInfoCards();
  initScroll();
  initCanvas();
  updateTps();
  updateValidatorsQuick();'''

new_code = '''async function loadHolders() {
  const tbody = document.getElementById('holdersTable');
  if (!tbody) return;
  tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:20px;color:var(--text-3)">Loading holders...</td></tr>';
  try {
    const resp = await fetch('/api/v1/token/holders');
    if (!resp.ok) throw new Error('API error');
    const json = await resp.json();
    if (!json.success || !json.data) throw new Error('No data');

    document.getElementById('holdersCount').textContent = json.count + ' holders';

    tbody.innerHTML = json.data.map(function(h, i) {
      var isModule = h.address.startsWith('Module:');
      var addrDisplay;
      if (isModule) {
        addrDisplay = '<span style="font-family:var(--mono);font-size:12px;color:var(--text-2)">' + h.address + '</span>';
      } else {
        var short = h.address.slice(0, 8) + '...' + h.address.slice(-6);
        addrDisplay = '<a href="#" onclick="switchTab(\\'accounts\\');searchAccount(\\'' + h.address + '\\');return false" style="font-family:var(--mono);font-size:12px">' + short + '</a>';
      }
      var typeBadge;
      if (isModule) {
        typeBadge = '<span style="background:#ede9fe;color:#5b21b6;padding:2px 8px;border-radius:4px;font-size:11px">Module</span>';
      } else if (h.is_validator) {
        typeBadge = '<span style="background:#dcfce7;color:#166534;padding:2px 8px;border-radius:4px;font-size:11px">Validator</span>';
      } else {
        typeBadge = '<span style="background:#f1f5f9;color:#475569;padding:2px 8px;border-radius:4px;font-size:11px">Account</span>';
      }
      return '<tr>' +
        '<td style="font-weight:600">' + (i+1) + '</td>' +
        '<td>' + addrDisplay + '</td>' +
        '<td>' + typeBadge + '</td>' +
        '<td style="font-family:var(--mono);font-weight:600">' + h.balance_formatted + '</td>' +
        '<td style="font-family:var(--mono);color:var(--text-2)">' + h.free_formatted + '</td>' +
        '<td style="font-family:var(--mono);color:var(--text-3)">' + h.reserved_formatted + '</td>' +
        '</tr>';
    }).join('');
  } catch(e) {
    console.error('Holders error:', e);
    tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:20px;color:#dc2626">Failed to load: ' + e.message + '</td></tr>';
  }
}

async function init() {
  updateInfoCards();
  initScroll();
  initCanvas();
  updateTps();
  updateValidatorsQuick();'''

if old_init in content:
    content = content.replace(old_init, new_code)
    print("Added loadHolders function")
else:
    print("ERROR: init function not found")

# Write back
proc = subprocess.run(
    ["ssh", "-o", "ConnectTimeout=10", "root@91.98.160.145", "cat > /var/www/verdiscan/explorer/index.html"],
    input=content,
    capture_output=True,
    text=True
)
print(f"Written: exit {proc.returncode}")
