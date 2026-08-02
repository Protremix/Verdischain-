#!/usr/bin/env python3
"""Add Smart Contracts section with holders to the explorer page."""

with open("/opt/verdis/app/dist/web/explorer.html", "r") as f:
    c = f.read()

# Add the Smart Contracts section before the Footer
contracts_section = """
<!-- Smart Contracts -->
<section class="pools-grid">
  <div class="panel">
    <div class="panel-header">
      <h2>📜 Smart Contracts</h2>
      <span class="badge" id="contractCount">— contracts</span>
    </div>
    <div class="panel-body">
      <table class="table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Contract ID</th>
            <th>Owner</th>
            <th>Holders</th>
            <th>Deployed</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody id="contractsBody"></tbody>
      </table>
    </div>
  </div>
</section>

<!-- Holders Modal -->
<div id="holdersModal" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.7);z-index:9999;backdrop-filter:blur(4px)">
  <div style="max-width:700px;margin:80px auto;background:var(--bg-card,#111);border:1px solid var(--border);border-radius:12px;padding:24px;max-height:70vh;overflow-y:auto">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
      <h3 style="margin:0;font-size:16px">👥 Contract Holders — <span id="holdersContractName"></span></h3>
      <button onclick="closeHoldersModal()" style="background:none;border:none;color:var(--text);font-size:20px;cursor:pointer">×</button>
    </div>
    <div id="holdersModalBody"></div>
  </div>
</div>

"""

# Insert before footer
footer_marker = "<!-- Footer -->"
if footer_marker in c:
    c = c.replace(footer_marker, contracts_section + footer_marker)
    print("Added Smart Contracts section to explorer")
else:
    print("ERROR: Could not find footer marker")

# Add JavaScript to load contracts and holders
js_code = """
// Load Smart Contracts
async function loadContracts() {
  try {
    const resp = await fetch('/api/contracts');
    const contracts = await resp.json();
    document.getElementById('contractCount').textContent = contracts.length + ' contracts';
    const tbody = document.getElementById('contractsBody');
    if (!contracts.length) {
      tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:var(--text-muted)">No contracts deployed</td></tr>';
      return;
    }
    tbody.innerHTML = contracts.map(c => {
      const shortId = c.id.substring(0, 16) + '...';
      const shortOwner = c.owner.substring(0, 10) + '...' + c.owner.substring(c.owner.length - 4);
      const deployDate = c.deployedAt ? new Date(c.deployedAt).toLocaleDateString() : '—';
      const holderCount = c.holderCount || 1;
      return '<tr onclick="showContractHolders(\\''+c.id+'\\',\\''+c.name+'\\')">' +
        '<td style="font-weight:600">' + c.name + '</td>' +
        '<td class="mono">' + shortId + '</td>' +
        '<td class="mono">' + shortOwner + '</td>' +
        '<td><span class="badge" style="background:rgba(63,185,80,.15);color:#3fb950">' + holderCount + '</span></td>' +
        '<td style="color:var(--text-muted)">' + deployDate + '</td>' +
        '<td><button class="btn btn-sm" onclick="event.stopPropagation();showContractHolders(\\''+c.id+'\\',\\''+c.name+'\\')" style="font-size:11px;padding:4px 10px">👥 Holders</button></td>' +
      '</tr>';
    }).join('');
  } catch(e) {
    console.error('Error loading contracts:', e);
  }
}

async function showContractHolders(contractId, contractName) {
  document.getElementById('holdersContractName').textContent = contractName;
  document.getElementById('holdersModal').style.display = 'block';
  document.getElementById('holdersModalBody').innerHTML = '<p style="color:var(--text-muted)">Loading holders...</p>';
  try {
    const resp = await fetch('/api/contract/' + contractId + '/holders');
    const data = await resp.json();
    if (data.holders && data.holders.length > 0) {
      let html = '<table class="table"><thead><tr><th>Role</th><th>Address</th><th>Balance</th></tr></thead><tbody>';
      data.holders.forEach(h => {
        const roleColor = h.role === 'owner' ? '#3fb950' : h.role === 'holder' ? '#58a6ff' : '#8b949e';
        const roleLabel = h.role === 'owner' ? 'Owner' : h.role === 'holder' ? 'Holder' : 'Ecosystem';
        const balStr = h.balance > 0 ? h.balance.toLocaleString() + ' VRDX' : '—';
        html += '<tr>' +
          '<td><span style="color:'+roleColor+';font-weight:600;text-transform:uppercase;font-size:11px">'+roleLabel+'</span></td>' +
          '<td class="mono" style="word-break:break-all">' + h.address + '</td>' +
          '<td>' + balStr + '</td>' +
        '</tr>';
      });
      html += '</tbody></table>';
      html += '<div style="margin-top:12px;text-align:center;color:var(--text-muted);font-size:12px">Total holders: ' + data.holderCount + '</div>';
      document.getElementById('holdersModalBody').innerHTML = html;
    } else {
      document.getElementById('holdersModalBody').innerHTML = '<p style="color:var(--text-muted)">No holders found.</p>';
    }
  } catch(e) {
    document.getElementById('holdersModalBody').innerHTML = '<p style="color:#f85149">Error: ' + e.message + '</p>';
  }
}

function closeHoldersModal() {
  document.getElementById('holdersModal').style.display = 'none';
}

// Load contracts on page load
loadContracts();
"""

# Add JS before the closing script tag
script_end = "</script>"
# Find the last script tag
last_script = c.rfind(script_end)
if last_script != -1:
    c = c[:last_script] + js_code + c[last_script:]
    print("Added contract holders JS to explorer")
else:
    print("ERROR: Could not find script end tag")

with open("/opt/verdis/app/dist/web/explorer.html", "w") as f:
    f.write(c)

print("Explorer updated with Smart Contracts + Holders!")
