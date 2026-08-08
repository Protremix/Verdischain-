#!/usr/bin/env python3
"""Fix Portfolio: token names as strings, add stake to total, improve DEX display."""

EXP_PATH = "/var/www/verdiscan/explorer/index.html"

with open(EXP_PATH, "r") as f:
    html = f.read()

# 1. Fix DEX token name display - convert byte arrays to ASCII strings
old_dex_render = '''    var html_out = '<div style="font-size:12px;color:var(--text-2);margin-bottom:8px">' + allPools.length + ' pools on the network. LP positions require on-chain storage query per pool.</div>';
    html_out += '<table class="data-table" style="width:100%"><thead><tr><th style="padding:6px 10px;font-size:11px">POOL</th><th style="padding:6px 10px;font-size:11px">RESERVE A</th><th style="padding:6px 10px;font-size:11px">RESERVE B</th></tr></thead><tbody>';
    for (var p of allPools) {
      var ra = (p.reserve_a || 0) / 1e9;
      var rb = (p.reserve_b || 0) / 1e9;
      html_out += '<tr><td style="padding:6px 10px;font-family:var(--mono);font-size:11px">' + (p.token_a || "?") + '/' + (p.token_b || "?") + '</td>';
      html_out += '<td style="padding:6px 10px;font-family:var(--mono);font-size:11px">' + ra.toLocaleString("en-US", {maximumFractionDigits: 0}) + '</td>';
      html_out += '<td style="padding:6px 10px;font-family:var(--mono);font-size:11px">' + rb.toLocaleString("en-US", {maximumFractionDigits: 0}) + '</td></tr>';
    }'''

new_dex_render = '''    var html_out = '<div style="font-size:12px;color:var(--text-2);margin-bottom:8px">' + allPools.length + ' pools on the network. LP positions require on-chain storage query per pool.</div>';
    html_out += '<table class="data-table" style="width:100%"><thead><tr><th style="padding:6px 10px;font-size:11px">POOL</th><th style="padding:6px 10px;font-size:11px">RESERVE A</th><th style="padding:6px 10px;font-size:11px">RESERVE B</th><th style="padding:6px 10px;font-size:11px">PRICE</th></tr></thead><tbody>';
    for (var p of allPools) {
      var ra = (p.reserve_a || 0) / 1e9;
      var rb = (p.reserve_b || 0) / 1e9;
      var ta = bytesToStr(p.token_a);
      var tb = bytesToStr(p.token_b);
      var price = ra > 0 ? (rb / ra).toFixed(4) : "--";
      html_out += '<tr><td style="padding:6px 10px;font-family:var(--mono);font-size:11px;font-weight:600">' + ta + '/' + tb + '</td>';
      html_out += '<td style="padding:6px 10px;font-family:var(--mono);font-size:11px">' + ra.toLocaleString("en-US", {maximumFractionDigits: 0}) + '</td>';
      html_out += '<td style="padding:6px 10px;font-family:var(--mono);font-size:11px">' + rb.toLocaleString("en-US", {maximumFractionDigits: 0}) + '</td>';
      html_out += '<td style="padding:6px 10px;font-family:var(--mono);font-size:11px;color:var(--accent)">' + price + '</td></tr>';
    }'''

if old_dex_render in html:
    html = html.replace(old_dex_render, new_dex_render)
    print("DEX display fixed")
else:
    print("DEX render code not found")

# 2. Add bytesToStr helper function after escapeHtml
old_escape = '''function escapeHtml(s) {
  if (!s) return "";
  return s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}'''

new_escape = old_escape + '''
function bytesToStr(b) {
  if (!b) return "?";
  if (typeof b === "string") return b;
  if (Array.isArray(b)) return b.map(function(x) { return String.fromCharCode(x); }).join("");
  return String(b);
}'''

if old_escape in html:
    html = html.replace(old_escape, new_escape)
    print("bytesToStr helper added")

# 3. Update the staking section to add stake to total value
# After getting the stake, update pfTotalValue
old_stake_display = '''html_out += '<div><span class="stat-label" style="font-size:11px">STAKE</span><br><span class="mono" style="font-size:13px;font-weight:600;color:var(--accent)">' + (stake / 1e9).toLocaleString("en-US", {maximumFractionDigits: 2}) + ' VRDX</span></div>';'''
new_stake_display = '''var stakeVrx = stake / 1e9;
      html_out += '<div><span class="stat-label" style="font-size:11px">STAKE</span><br><span class="mono" style="font-size:13px;font-weight:600;color:var(--accent)">' + stakeVrx.toLocaleString("en-US", {maximumFractionDigits: 2}) + ' VRDX</span></div>';
      // Update total value to include stake
      var currentTotal = parseFloat(document.getElementById("pfTotalValue").textContent) || 0;
      document.getElementById("pfTotalValue").textContent = (currentTotal + stakeVrx).toLocaleString("en-US", {maximumFractionDigits: 2}) + ' VRDX';'''

if old_stake_display in html:
    html = html.replace(old_stake_display, new_stake_display)
    print("Stake added to total value")
else:
    print("Stake display code not found")

with open(EXP_PATH, "w") as f:
    f.write(html)
print(f"All fixes applied ({len(html)} bytes)")
