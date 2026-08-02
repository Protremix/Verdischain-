#!/usr/bin/env python3
"""
Fix token sale page:
1. Fix ETH price from 3200 to 1835 (match displayed live price)
2. Fix BNB price from 580 to 575
3. Fix initial assetPriceUSD from 3200 to 1835
4. Fix static bonus text
5. Update live rate display to include 85% bonus
"""

import re

FILE = "/opt/verdis/app/dist/web/token-sale.html"

with open(FILE, "r") as f:
    content = f.read()

changes = []

# Fix 1: ETH onclick price 3200 -> 1835
content = content.replace(
    "selectAsset('ETH', 3200, 'fa-brands fa-ethereum', event)",
    "selectAsset('ETH', 1835, 'fa-brands fa-ethereum', event)"
)
changes.append("Fixed ETH onclick price: 3200 -> 1835")

# Fix 2: BNB onclick price 580 -> 575
content = content.replace(
    "selectAsset('BNB', 580, 'fa-solid fa-coins', event)",
    "selectAsset('BNB', 575, 'fa-solid fa-coins', event)"
)
changes.append("Fixed BNB onclick price: 580 -> 575")

# Fix 3: Initial assetPriceUSD
content = content.replace(
    "let assetPriceUSD = 3200;",
    "let assetPriceUSD = 1835;"
)
changes.append("Fixed initial assetPriceUSD: 3200 -> 1835")

# Fix 4: Update live rate display (already updated in previous fix, verify)
old_rates = """<div>1 ETH = <span id="liveRateETH">3,405,000</span> VRDX <span style="color:#10B981">(+85% bonus)</span></div>
            <div>1 BNB = <span id="liveRateBNB">1,067,500</span> VRDX <span style="color:#10B981">(+85% bonus)</span></div>
            <div>1 USDT = 1,850 VRDX <span style="color:#10B981">(+85% bonus)</span></div>
            <div>1 USDC = 1,850 VRDX <span style="color:#10B981">(+85% bonus)</span></div>"""

new_rates = """<div>1 ETH = <span id="liveRateETH">6,789,500</span> VRDX <span style="color:#10B981">(+85% bonus)</span></div>
            <div>1 BNB = <span id="liveRateBNB">2,127,500</span> VRDX <span style="color:#10B981">(+85% bonus)</span></div>
            <div>1 USDT = 3,700 VRDX <span style="color:#10B981">(+85% bonus)</span></div>
            <div>1 USDC = 3,700 VRDX <span style="color:#10B981">(+85% bonus)</span></div>"""

if old_rates in content:
    content = content.replace(old_rates, new_rates)
    changes.append("Updated live rate display with correct 85% bonus rates")
else:
    # Try old format (before previous fix)
    old_rates2 = """<div>1 ETH = <span id="liveRateETH">1,835,000</span> VRDX</div>
            <div>1 BNB = <span id="liveRateBNB">575,000</span> VRDX</div>
            <div>1 USDT = 1,000 VRDX</div>
            <div>1 USDC = 1,000 VRDX</div>"""
    if old_rates2 in content:
        content = content.replace(old_rates2, new_rates)
        changes.append("Updated live rate display from old format")
    else:
        # Try to find and replace whatever exists
        content = re.sub(
            r'<div>1 ETH = <span id="liveRateETH">[^<]*</span> VRDX[^<]*</div>\s*<div>1 BNB = <span id="liveRateBNB">[^<]*</span> VRDX[^<]*</div>\s*<div>1 USDT = [^<]*</div>\s*<div>1 USDC = [^<]*</div>',
            new_rates,
            content
        )
        changes.append("Updated live rate display (regex replace)")

# Fix 5: Update static bonus text from +160,000 to correct value
content = content.replace(
    '+160,000 VRDX',
    '+3,119,500 VRDX'
)
changes.append("Updated static bonus text to 85% value")

# Fix 6: Update static base allocation
content = content.replace(
    '1,600,000 VRDX',
    '3,670,000 VRDX'
)
changes.append("Updated static base allocation to match $1,835 ETH")

# Fix 7: Update static total tokens
content = content.replace(
    '1,760,000 VRDX',
    '6,789,500 VRDX'
)
changes.append("Updated static total tokens to include 85% bonus")

# Fix 8: Update static USD value
content = content.replace(
    '$1,600.00',
    '$1,835.00'
)
changes.append("Updated static USD value to match 1 ETH at $1,835")

with open(FILE, "w") as f:
    f.write(content)

print(f"\n=== {len(changes)} fixes applied ===")
for c in changes:
    print(f"  ✓ {c}")
