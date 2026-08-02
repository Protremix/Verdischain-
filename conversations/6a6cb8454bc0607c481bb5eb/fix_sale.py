#!/usr/bin/env python3
"""
Fix token sale page:
1. Fix currency selector - event is not passed as parameter, causing crash
2. Fix bonus calculation - should be 85% (Seed stage), not 10%
"""

import re

FILE = "/opt/verdis/app/dist/web/token-sale.html"

with open(FILE, "r") as f:
    content = f.read()

changes = []

# Fix 1: Pass event parameter to selectAsset in onclick handlers
old_onclicks = [
    """onclick="selectAsset('ETH', 3200, 'fa-brands fa-ethereum')\"""",
    """onclick="selectAsset('BNB', 580, 'fa-solid fa-coins')\"""",
    """onclick="selectAsset('USDT', 1.00, 'fa-solid fa-dollar-sign')\"""",
    """onclick="selectAsset('USDC', 1.00, 'fa-solid fa-circle-dollar-to-slot')\"""",
]

new_onclicks = [
    """onclick="selectAsset('ETH', 3200, 'fa-brands fa-ethereum', event)\"""",
    """onclick="selectAsset('BNB', 580, 'fa-solid fa-coins', event)\"""",
    """onclick="selectAsset('USDT', 1.00, 'fa-solid fa-dollar-sign', event)\"""",
    """onclick="selectAsset('USDC', 1.00, 'fa-solid fa-circle-dollar-to-slot', event)\"""",
]

for old, new in zip(old_onclicks, new_onclicks):
    if old in content:
        content = content.replace(old, new)
        changes.append(f"Fixed onclick: {new}")
    else:
        # Try without the trailing quote (might be different)
        print(f"WARNING: Could not find: {old[:50]}...")

# Fix 2: Fix the selectAsset function to accept event parameter
old_func = """function selectAsset(symbol, priceUsd, iconClass) {
      selectedAsset = symbol;
      assetPriceUSD = priceUsd;

      document.querySelectorAll('.asset-btn').forEach(btn => btn.classList.remove('active'));
      event.currentTarget.classList.add('active');

      document.getElementById('selectedAssetSymbol').innerText = symbol;
      document.getElementById('selectedAssetIcon').className = iconClass;

      calculateTokens();
    }"""

new_func = """function selectAsset(symbol, priceUsd, iconClass, evt) {
      selectedAsset = symbol;
      assetPriceUSD = priceUsd;

      document.querySelectorAll('.asset-btn').forEach(btn => btn.classList.remove('active'));
      if (evt && evt.currentTarget) {
        evt.currentTarget.classList.add('active');
      } else {
        // Fallback: find the button by symbol
        document.querySelectorAll('.asset-btn').forEach(btn => {
          const name = btn.querySelector('.asset-name');
          if (name && name.textContent.trim() === symbol) {
            btn.classList.add('active');
          }
        });
      }

      document.getElementById('selectedAssetSymbol').innerText = symbol;
      document.getElementById('selectedAssetIcon').className = iconClass;

      calculateTokens();
    }"""

if old_func in content:
    content = content.replace(old_func, new_func)
    changes.append("Fixed selectAsset function to accept event parameter with fallback")
else:
    print("WARNING: Could not find selectAsset function definition")

# Fix 3: Fix bonus calculation from 10% to 85% (Seed stage bonus)
# In calculateTokens():
old_calc = """const baseVRDX = Math.floor(totalUSD / vrdxPriceUSD);
      const bonusVRDX = Math.floor(baseVRDX * 0.10);
      const totalVRDX = baseVRDX + bonusVRDX;"""

new_calc = """const baseVRDX = Math.floor(totalUSD / vrdxPriceUSD);
      const bonusPct = 85; // Seed stage: 85% bonus
      const bonusVRDX = Math.floor(baseVRDX * (bonusPct / 100));
      const totalVRDX = baseVRDX + bonusVRDX;"""

if old_calc in content:
    content = content.replace(old_calc, new_calc)
    changes.append("Fixed bonus calculation: 10% -> 85% (Seed stage)")
else:
    print("WARNING: Could not find bonus calculation in calculateTokens")

# Fix 4: Also fix the bonus in executePurchase
old_purchase_calc = """const baseVRDX = Math.floor(totalUSD / vrdxPriceUSD);
      const bonusVRDX = Math.floor(baseVRDX * 0.10);
      const totalVRDX = baseVRDX + bonusVRDX;"""

new_purchase_calc = """const baseVRDX = Math.floor(totalUSD / vrdxPriceUSD);
      const bonusPct = 85;
      const bonusVRDX = Math.floor(baseVRDX * (bonusPct / 100));
      const totalVRDX = baseVRDX + bonusVRDX;"""

if old_purchase_calc in content:
    content = content.replace(old_purchase_calc, new_purchase_calc)
    changes.append("Fixed bonus in executePurchase: 10% -> 85%")
else:
    print("WARNING: Could not find bonus in executePurchase")

# Fix 5: Update the live rate display to show correct bonus
old_rate_display = """<div>1 ETH = <span id="liveRateETH">1,835,000</span> VRDX</div>
            <div>1 BNB = <span id="liveRateBNB">575,000</span> VRDX</div>
            <div>1 USDT = 1,000 VRDX</div>
            <div>1 USDC = 1,000 VRDX</div>"""

new_rate_display = """<div>1 ETH = <span id="liveRateETH">3,405,000</span> VRDX <span style="color:#10B981">(+85% bonus)</span></div>
            <div>1 BNB = <span id="liveRateBNB">1,067,500</span> VRDX <span style="color:#10B981">(+85% bonus)</span></div>
            <div>1 USDT = 1,850 VRDX <span style="color:#10B981">(+85% bonus)</span></div>
            <div>1 USDC = 1,850 VRDX <span style="color:#10B981">(+85% bonus)</span></div>"""

if old_rate_display in content:
    content = content.replace(old_rate_display, new_rate_display)
    changes.append("Updated live rate display to include 85% bonus")

with open(FILE, "w") as f:
    f.write(content)

print(f"\n=== {len(changes)} fixes applied ===")
for c in changes:
    print(f"  ✓ {c}")
