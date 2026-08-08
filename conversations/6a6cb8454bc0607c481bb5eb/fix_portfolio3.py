#!/usr/bin/env python3
"""Fix total value race condition: use shared variable instead of DOM parsing."""

EXP_PATH = "/var/www/verdiscan/explorer/index.html"

with open(EXP_PATH, "r") as f:
    html = f.read()

# Add a shared variable for total value tracking
old_pfaddr = "var pfAddress = null;"
new_pfaddr = """var pfAddress = null;
var pfBalanceTotal = 0;
var pfStakeTotal = 0;

function updatePfTotal() {
  var total = pfBalanceTotal + pfStakeTotal;
  document.getElementById("pfTotalValue").textContent = total.toLocaleString("en-US", {maximumFractionDigits: 2}) + " VRDX";
}"""

if old_pfaddr in html:
    html = html.replace(old_pfaddr, new_pfaddr)
    print("Shared total variable added")

# Fix balance function to use shared variable
old_bal_set = '''document.getElementById("pfFree").textContent = free.toLocaleString("en-US", {maximumFractionDigits: 2}) + " VRDX";
      document.getElementById("pfReserved").textContent = reserved.toLocaleString("en-US", {maximumFractionDigits: 2}) + " VRDX";
      document.getElementById("pfTotalValue").textContent = total.toLocaleString("en-US", {maximumFractionDigits: 2}) + " VRDX";'''

new_bal_set = '''document.getElementById("pfFree").textContent = free.toLocaleString("en-US", {maximumFractionDigits: 2}) + " VRDX";
      document.getElementById("pfReserved").textContent = reserved.toLocaleString("en-US", {maximumFractionDigits: 2}) + " VRDX";
      pfBalanceTotal = total;
      updatePfTotal();'''

if old_bal_set in html:
    html = html.replace(old_bal_set, new_bal_set)
    print("Balance function fixed")

# Fix stake function to use shared variable
old_stake_update = '''var currentTotal = parseFloat(document.getElementById("pfTotalValue").textContent) || 0;
      document.getElementById("pfTotalValue").textContent = (currentTotal + stakeVrx).toLocaleString("en-US", {maximumFractionDigits: 2}) + " VRDX";'''

new_stake_update = '''pfStakeTotal = stakeVrx;
      updatePfTotal();'''

if old_stake_update in html:
    html = html.replace(old_stake_update, new_stake_update)
    print("Stake function fixed")

# Also reset the shared variables in loadPortfolio
old_reset = '''// Reset fields
  ["pfTotalValue","pfFree","pfReserved","pfNonce"].forEach(function(id) {
    document.getElementById(id).textContent = "--";
  });'''
new_reset = '''// Reset fields
  pfBalanceTotal = 0;
  pfStakeTotal = 0;
  ["pfTotalValue","pfFree","pfReserved","pfNonce"].forEach(function(id) {
    document.getElementById(id).textContent = "--";
  });'''

if old_reset in html:
    html = html.replace(old_reset, new_reset)
    print("Reset logic fixed")

with open(EXP_PATH, "w") as f:
    f.write(html)
print(f"Race condition fixed ({len(html)} bytes)")
