#!/usr/bin/env python3
"""
Completely rewrite selectAsset to not use event at all.
Use data attributes on the buttons for identification.
"""

import re

FILE = "/opt/verdis/app/dist/web/token-sale.html"

with open(FILE, "r") as f:
    content = f.read()

changes = []

# Replace the onclick handlers - remove event parameter
content = content.replace(
    "onclick=\"selectAsset('ETH', 1835, 'fa-brands fa-ethereum', event)\"",
    "onclick=\"selectAsset('ETH', 1835, 'fa-brands fa-ethereum')\""
)
content = content.replace(
    "onclick=\"selectAsset('BNB', 575, 'fa-solid fa-coins', event)\"",
    "onclick=\"selectAsset('BNB', 575, 'fa-solid fa-coins')\""
)
content = content.replace(
    "onclick=\"selectAsset('USDT', 1.00, 'fa-solid fa-dollar-sign', event)\"",
    "onclick=\"selectAsset('USDT', 1.00, 'fa-solid fa-dollar-sign')\""
)
content = content.replace(
    "onclick=\"selectAsset('USDC', 1.00, 'fa-solid fa-circle-dollar-to-slot', event)\"",
    "onclick=\"selectAsset('USDC', 1.00, 'fa-solid fa-circle-dollar-to-slot')\""
)
changes.append("Removed event parameter from all onclick handlers")

# Replace the selectAsset function - no event dependency
old_func = re.compile(r"function selectAsset\(symbol, priceUsd, iconClass, evt\).*?\{.*?\n    \}", re.DOTALL)

new_func = """function selectAsset(symbol, priceUsd, iconClass) {
      console.log('selectAsset called:', symbol, priceUsd);
      selectedAsset = symbol;
      assetPriceUSD = priceUsd;

      // Remove active from all buttons
      document.querySelectorAll('.asset-btn').forEach(function(btn) {
        btn.classList.remove('active');
      });
      
      // Add active to the clicked button by matching symbol text
      var buttons = document.querySelectorAll('.asset-btn');
      for (var i = 0; i < buttons.length; i++) {
        var nameEl = buttons[i].querySelector('.asset-name');
        if (nameEl && nameEl.textContent.trim() === symbol) {
          buttons[i].classList.add('active');
          break;
        }
      }

      // Update the display
      var symEl = document.getElementById('selectedAssetSymbol');
      if (symEl) symEl.innerText = symbol;
      
      var iconEl = document.getElementById('selectedAssetIcon');
      if (iconEl) iconEl.className = iconClass;

      // Update the currency label on the pay input
      var payLabel = document.getElementById('payCurrencyLabel');
      if (payLabel) payLabel.innerText = symbol;
      
      // Update preset buttons to show crypto amounts
      var presets = document.querySelectorAll('.preset-btn');
      presets.forEach(function(btn) {
        var usd = parseFloat(btn.getAttribute('data-usd') || btn.textContent.replace(/[^0-9]/g, '')) || 0;
        var cryptoAmt = (usd / priceUsd).toFixed(4);
        btn.textContent = cryptoAmt + ' ' + symbol;
      });

      calculateTokens();
    }"""

content = old_func.sub(new_func, content)
changes.append("Rewrote selectAsset function without event dependency")

with open(FILE, "w") as f:
    f.write(content)

print(f"\n=== {len(changes)} fixes applied ===")
for c in changes:
    print(f"  ✓ {c}")
