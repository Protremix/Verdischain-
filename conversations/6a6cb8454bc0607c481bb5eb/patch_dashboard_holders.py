#!/usr/bin/env python3
"""Patch the dashboard to show contract holders."""

with open("/opt/verdis/app/dist/web/dashboard.html", "r") as f:
    c = f.read()

# 1. Replace the loadContracts function to show holders
old_load = """async function loadContracts() {
  const c = await api('contracts');
  if (!c || !Array.isArray(c)) return;
  document.getElementById('contractList').innerHTML = c.map(x => {
    const id = (x.id || '—').substring(0, 20);
    const bytecodeLen = (x.bytecode || x.code || []).length || 0;
    const deployDate = x.deployedAt ? new Date(x.deployedAt).toLocaleString() : '';
    return '<div class="card" style="background:var(--bg)">' +
      '<div class="flex justify-between" style="align-items:flex-start">' +
        '<div>' +
          '<span class="badge badge-blue" style="cursor:pointer" onclick="selectContract(\\''+x.id+'\\',\\''+(x.name||'Contract')+'\\')">'+(x.name||'Contract')+'</span>' +
          '<div class="mono text-sm text-muted mt-1" style="word-break:break-all">' + id + '...</div>' +
        '</div>' +
        '<div style="text-align:right">' +
          '<div class="text-sm text-muted">'+bytecodeLen+' bytes</div>' +
          '<div class="text-xs text-muted" style="margin-top:2px">'+deployDate+'</div>' +
        '</div>' +
      '</div>' +
      '<div style="margin-top:8px;display:flex;gap:6px">' +
        '<button class="btn btn-sm" onclick="selectContract(\\''+x.id+'\\',\\''+(x.name||'Contract')+'\\')">&#9889; Execute</button>' +
        '<button class="btn btn-sm" onclick="copyContractId(\\''+x.id+'\\')">&#128203; Copy ID</button>' +
      '</div>' +
    '</div>';
  }).join('') || '<div class="text-muted text-sm">No contracts deployed yet. Choose a template above to get started!</div>';
}"""

new_load = """async function loadContracts() {
  const c = await api('contracts');
  if (!c || !Array.isArray(c)) return;
  document.getElementById('contractList').innerHTML = c.map(x => {
    const id = (x.id || '—').substring(0, 20);
    const bytecodeLen = (x.bytecode || x.code || []).length || 0;
    const deployDate = x.deployedAt ? new Date(x.deployedAt).toLocaleString() : '';
    const holderCount = x.holderCount || 1;
    const holderBadge = holderCount > 0 ? '<span class="badge badge-green" style="font-size:10px;margin-left:6px">&#128100; '+holderCount+' holders</span>' : '';
    return '<div class="card" style="background:var(--bg)" id="contract-card-'+x.id+'">' +
      '<div class="flex justify-between" style="align-items:flex-start">' +
        '<div>' +
          '<span class="badge badge-blue" style="cursor:pointer" onclick="selectContract(\\''+x.id+'\\',\\''+(x.name||'Contract')+'\\')">'+(x.name||'Contract')+'</span>' +
          holderBadge +
          '<div class="mono text-sm text-muted mt-1" style="word-break:break-all">' + id + '...</div>' +
        '</div>' +
        '<div style="text-align:right">' +
          '<div class="text-sm text-muted">'+bytecodeLen+' bytes</div>' +
          '<div class="text-xs text-muted" style="margin-top:2px">'+deployDate+'</div>' +
        '</div>' +
      '</div>' +
      '<div style="margin-top:8px;display:flex;gap:6px;flex-wrap:wrap">' +
        '<button class="btn btn-sm" onclick="selectContract(\\''+x.id+'\\',\\''+(x.name||'Contract')+'\\')">&#9889; Execute</button>' +
        '<button class="btn btn-sm" onclick="copyContractId(\\''+x.id+'\\')">&#128203; Copy ID</button>' +
        '<button class="btn btn-sm" onclick="toggleHolders(\\''+x.id+'\\')">&#128100; View Holders</button>' +
      '</div>' +
      '<div id="holders-'+x.id+'" style="display:none;margin-top:10px;padding-top:10px;border-top:1px solid var(--border)"></div>' +
    '</div>';
  }).join('') || '<div class="text-muted text-sm">No contracts deployed yet. Choose a template above to get started!</div>';
}

async function toggleHolders(contractId) {
  const el = document.getElementById('holders-'+contractId);
  if (!el) return;
  if (el.style.display === 'none') {
    el.style.display = 'block';
    el.innerHTML = '<div class="text-sm text-muted">Loading holders...</div>';
    try {
      const resp = await fetch('/api/contract/'+contractId+'/holders');
      const data = await resp.json();
      if (data.holders && data.holders.length > 0) {
        let html = '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">' +
          '<span style="font-weight:600;font-size:13px">&#128100; Holders ('+data.holderCount+')</span>' +
          '<span class="text-xs text-muted">Contract: '+data.contractName+'</span>' +
        '</div>';
        html += '<div style="max-height:300px;overflow-y:auto;border:1px solid var(--border);border-radius:6px">';
        data.holders.forEach((h, i) => {
          const roleColor = h.role === 'owner' ? '#3fb950' : h.role === 'holder' ? '#58a6ff' : '#8b949e';
          const roleLabel = h.role === 'owner' ? 'Owner' : h.role === 'holder' ? 'Holder' : 'Ecosystem';
          const balStr = h.balance > 0 ? (h.balance.toLocaleString() + ' VRDX') : '—';
          const shortAddr = h.address.substring(0, 10) + '...' + h.address.substring(h.address.length - 6);
          html += '<div style="display:flex;justify-content:space-between;align-items:center;padding:8px 10px;border-bottom:1px solid var(--border)">' +
            '<div style="display:flex;align-items:center;gap:8px">' +
              '<span style="font-size:11px;color:'+roleColor+';font-weight:600;text-transform:uppercase;min-width:70px">'+roleLabel+'</span>' +
              '<span class="mono text-sm" style="word-break:break-all">'+shortAddr+'</span>' +
            '</div>' +
            '<span class="text-sm text-muted" style="white-space:nowrap;margin-left:8px">'+balStr+'</span>' +
          '</div>';
        });
        html += '</div>';
        el.innerHTML = html;
      } else {
        el.innerHTML = '<div class="text-sm text-muted">No holders found for this contract.</div>';
      }
    } catch(e) {
      el.innerHTML = '<div class="text-sm text-red">Error loading holders: '+e.message+'</div>';
    }
  } else {
    el.style.display = 'none';
  }
}"""

if old_load in c:
    c = c.replace(old_load, new_load)
    print("Updated loadContracts with holders display")
else:
    print("ERROR: Could not find loadContracts function")
    # Try to find it with different escaping
    import re
    # Find the function by its signature
    pattern = r'async function loadContracts\(\).*?^\}'
    match = re.search(pattern, c, re.MULTILINE | re.DOTALL)
    if match:
        print(f"Found loadContracts at position {match.start()}-{match.end()}")
        print(f"First 200 chars: {c[match.start():match.start()+200]}")
    else:
        print("Could not find loadContracts function at all")

with open("/opt/verdis/app/dist/web/dashboard.html", "w") as f:
    f.write(c)

print("Dashboard updated!")
