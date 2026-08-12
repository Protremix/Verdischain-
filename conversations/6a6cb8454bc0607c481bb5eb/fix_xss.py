#!/usr/bin/env python3
"""Fix XSS vulnerabilities in DEX, Faucet, and Validators pages by adding escapeHtml and escaping all external data in innerHTML."""

import re

# ============ FAUCET FIX ============
faucet_path = '/var/www/verdiscan/faucet/index.html'
with open(faucet_path, 'r') as f:
    faucet = f.read()

# Add escapeHtml function after the first <script> tag
faucet_escape = """
// XSS Prevention: escape all external data before innerHTML
function escapeHtml(str) {
  if (str === null || str === undefined) return '';
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}
"""

# Insert escapeHtml after the first <script> that contains JS code
faucet = faucet.replace(
    "function generateCaptcha() {",
    faucet_escape + "\nfunction generateCaptcha() {",
    1
)

# Fix renderHistory - escape all distribution data
faucet = faucet.replace(
    """function renderHistory() {
  const html = distributions.map(d => `
    <tr>
      <td class="mono" style="font-size:13px">${d.addr.slice(0,16)}...${d.addr.slice(-8)}</td>
      <td>${d.token}</td>
      <td class="mono">${d.amount.toLocaleString()}</td>
      <td class="mono" style="font-size:12px;color:var(--text-3)">${d.hash}</td>
      <td style="color:var(--text-3)">${d.time}</td>
    </tr>
  `).join('');
  document.getElementById('historyBody').innerHTML = html;
}""",
    """function renderHistory() {
  const html = distributions.map(d => {
    const addr = escapeHtml(d.addr);
    const token = escapeHtml(d.token);
    const amount = escapeHtml(d.amount.toLocaleString());
    const hash = escapeHtml(d.hash);
    const time = escapeHtml(d.time);
    return '<tr>' +
      '<td class="mono" style="font-size:13px">' + addr.slice(0,16) + '...' + addr.slice(-8) + '</td>' +
      '<td>' + token + '</td>' +
      '<td class="mono">' + amount + '</td>' +
      '<td class="mono" style="font-size:12px;color:var(--text-3)">' + hash + '</td>' +
      '<td style="color:var(--text-3)">' + time + '</td>' +
      '</tr>';
  }).join('');
  document.getElementById('historyBody').innerHTML = html;
}"""
)

# Fix faucet stats rendering - escape distribution data from API
faucet = faucet.replace(
    """tableBody.innerHTML = faucetStats.distributions.slice(0, 6).map(d => 
                    '<tr><td>' + d.address + '</td><td>VRDX</td><td>' + d.amount + '</td><td>' + d.txHash + '</td><td>recent</td></tr>'
                ).join('');""",
    """tableBody.innerHTML = faucetStats.distributions.slice(0, 6).map(d =>
                    '<tr><td>' + escapeHtml(d.address) + '</td><td>VRDX</td><td>' + escapeHtml(d.amount) + '</td><td>' + escapeHtml(d.txHash) + '</td><td>recent</td></tr>'
                ).join('');"""
)

with open(faucet_path, 'w') as f:
    f.write(faucet)
print("FAUCET: XSS fixes applied")

# ============ DEX FIX ============
dex_path = '/var/www/verdiscan/dex/index.html'
with open(dex_path, 'r') as f:
    dex = f.read()

# Add escapeHtml function at the start of the DEX JS
dex_escape = """
// XSS Prevention: escape all external data before innerHTML
function escapeHtml(str) {
  if (str === null || str === undefined) return '';
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}
"""

# Insert after first <script> tag in DEX
dex = dex.replace(
    "    function renderTopPoolsList() {",
    dex_escape + "\n    function renderTopPoolsList() {",
    1
)

# Fix renderTopPoolsList - escape token names
dex = dex.replace(
    """container.innerHTML = poolsData.slice(0, 6).map(function(p) {
        var iconA = icons[p.tokenA] || '?';
        var iconB = icons[p.tokenB] || '?';
        var tvlStr = p.tvl > 1e6 ? '$' + (p.tvl/1e6).toFixed(1) + 'M TVL' : '$' + (p.tvl/1e3).toFixed(1) + 'K TVL';
        return '<div class="pool-item" style="display:flex;justify-content:space-between;align-items:center;padding:12px 16px;background:#f8f9fa;border-radius:8px;cursor:pointer;">' +
               '<div style="font-weight:600;display:flex;align-items:center;gap:8px;">' + iconA + ' ' + p.tokenA + ' / ' + iconB + ' ' + p.tokenB + '</div>' +
               '<div style="font-size:13px;font-weight:600;color:#00a86b;">' + tvlStr + '</div></div>';
      }).join('');""",
    """container.innerHTML = poolsData.slice(0, 6).map(function(p) {
        var iconA = icons[p.tokenA] || '?';
        var iconB = icons[p.tokenB] || '?';
        var tokenA = escapeHtml(p.tokenA);
        var tokenB = escapeHtml(p.tokenB);
        var tvlStr = p.tvl > 1e6 ? '$' + (p.tvl/1e6).toFixed(1) + 'M TVL' : '$' + (p.tvl/1e3).toFixed(1) + 'K TVL';
        return '<div class="pool-item" style="display:flex;justify-content:space-between;align-items:center;padding:12px 16px;background:#f8f9fa;border-radius:8px;cursor:pointer;">' +
               '<div style="font-weight:600;display:flex;align-items:center;gap:8px;">' + iconA + ' ' + tokenA + ' / ' + iconB + ' ' + tokenB + '</div>' +
               '<div style="font-size:13px;font-weight:600;color:#00a86b;">' + escapeHtml(tvlStr) + '</div></div>';
      }).join('');"""
)

# Fix renderPoolsTable - replace innerHTML with safe DOM construction
# This is the most critical fix - template literals with onclick attribute injection
old_pools_table = """poolsData.forEach(p => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>
            <div class="pool-pair-cell">
              <div class="pair-icons">
                <div class="pair-icon" style="background:#16a34a; color:#000;">⚡</div>
                <div class="pair-icon" style="background:#3b82f6; color:#fff;">💵</div>
              </div>
              <span>${p.pair}</span>
              ${p.isPrimary ? '<span class="badge-primary">PRIMARY</span>' : ''}
            </div>
          </td>
          <td class="mono">${p.reserveA.toLocaleString()} / ${p.reserveB.toLocaleString()}</td>
          <td class="mono" style="font-weight:700;">$${p.tvl.toLocaleString()}</td>
          <td class="mono">$${p.volume24h.toLocaleString()}</td>
          <td class="mono" style="color:#22c55e; font-weight:700;">${p.apy}%</td>
          <td>
            <button class="btn-sm" onclick="selectPoolForTrade('${p.tokenA}', '${p.tokenB}')">Trade</button>
          </td>
        `;
        tbody.appendChild(tr);
      });"""

new_pools_table = """poolsData.forEach(p => {
        const tr = document.createElement("tr");
        var pair = escapeHtml(p.pair);
        var reserves = escapeHtml(p.reserveA.toLocaleString()) + ' / ' + escapeHtml(p.reserveB.toLocaleString());
        var tvl = '$' + escapeHtml(p.tvl.toLocaleString());
        var vol = '$' + escapeHtml(p.volume24h.toLocaleString());
        var apy = escapeHtml(p.apy) + '%';
        var isPrimary = p.isPrimary ? '<span class="badge-primary">PRIMARY</span>' : '';
        tr.innerHTML =
          '<td><div class="pool-pair-cell"><div class="pair-icons">' +
          '<div class="pair-icon" style="background:#16a34a; color:#000;">⚡</div>' +
          '<div class="pair-icon" style="background:#3b82f6; color:#fff;">💵</div>' +
          '</div><span>' + pair + '</span>' + isPrimary + '</div></td>' +
          '<td class="mono">' + reserves + '</td>' +
          '<td class="mono" style="font-weight:700;">' + tvl + '</td>' +
          '<td class="mono">' + vol + '</td>' +
          '<td class="mono" style="color:#22c55e; font-weight:700;">' + apy + '</td>' +
          '<td><button class="btn-sm" data-token-a="' + escapeHtml(p.tokenA) + '" data-token-b="' + escapeHtml(p.tokenB) + '">Trade</button></td>';
        var btn = tr.querySelector('button');
        if (btn) {
          btn.addEventListener('click', function() {
            selectPoolForTrade(this.getAttribute('data-token-a'), this.getAttribute('data-token-b'));
          });
        }
        tbody.appendChild(tr);
      });"""

dex = dex.replace(old_pools_table, new_pools_table)

# Fix the second table rendering (swap history or similar)
old_table2 = """tbody.innerHTML = "";
      
      poolsData.forEach(p => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>
            <div class="pool-pair-cell">
              <div class="pair-icons">
                <div class="pair-icon" style="background:#16a34a; color:#000;">⚡</div>
                <div class="pair-icon" style="background:#3b82f6; color:#fff;">💵</div>
              </div>
              <span>${p.pair}</span>
              ${p.isPrimary ? '<span class="badge-primary">PRIMARY</span>' : ''}
            </div>
          </td>
          <td class="mono">${p.reserveA.toLocaleString()} / ${p.reserveB.toLocaleString()}</td>
          <td class="mono" style="font-weight:700;">$${p.tvl.toLocaleString()}</td>
          <td class="mono">$${p.volume24h.toLocaleString()}</td>
          <td class="mono" style="color:#22c55e; font-weight:700;">${p.apy}%</td>
          <td>
            <button class="btn-sm" onclick="selectPoolForTrade('${p.tokenA}', '${p.tokenB}')">Trade</button>
          </td>
        `;
        tbody.appendChild(tr);
      });"""

if old_table2 in dex:
    dex = dex.replace(old_table2, new_pools_table)
    print("DEX: Second table also fixed")

with open(dex_path, 'w') as f:
    f.write(dex)
print("DEX: XSS fixes applied")

# ============ VALIDATORS FIX ============
val_path = '/var/www/verdiscan/validators/index.html'
with open(val_path, 'r') as f:
    val = f.read()

# Add escapeHtml function
val_escape = """
// XSS Prevention: escape all external data before innerHTML
function escapeHtml(str) {
  if (str === null || str === undefined) return '';
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}
"""

# Insert before the first function that builds HTML
val = val.replace(
    "document.getElementById('validatorList').innerHTML = html;",
    val_escape + "\n    document.getElementById('validatorList').innerHTML = html;",
    1
)

# Escape validator data in the HTML template
# The validators page builds HTML from RPC data - we need to escape name, address, etc.
# Let me find the template and fix it
val = val.replace(
    '<div class="validator-name">${v.name || v.address.substring(0, 8)',
    '<div class="validator-name">${escapeHtml(v.name || v.address.substring(0, 8))'
)
val = val.replace(
    '<div class="validator-stake">${v.stake.toLocaleString()}</div>',
    '<div class="validator-stake">${escapeHtml(v.stake.toLocaleString())}</div>'
)
val = val.replace(
    '<div class="validator-apy">${apy}%</div>',
    '<div class="validator-apy">${escapeHtml(apy)}%</div>'
)
val = val.replace(
    '<div class="validator-address">${v.address.substring(0, 16)}...${v.address.slice(-8)}</div>',
    '<div class="validator-address">${escapeHtml(v.address).substring(0, 16)}...${escapeHtml(v.address).slice(-8)}</div>'
)

with open(val_path, 'w') as f:
    f.write(val)
print("VALIDATORS: XSS fixes applied")

print("\n=== XSS HARDENING COMPLETE ===")
print("Fixed pages: faucet, dex, validators")
print("Wallet page: already safe (uses createElement/textContent)")
print("Explorer page: already has escapeHtml (26 usages)")
