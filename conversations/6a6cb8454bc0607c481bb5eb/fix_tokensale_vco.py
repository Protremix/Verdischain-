#!/usr/bin/env python3
"""Fix VCO -> VRS in token-sale.html"""
import re

path = "/opt/verdis/app/dist/web/token-sale.html"
with open(path) as f:
    c = f.read()

original = c.count("VCO")

# Title/meta
c = c.replace("Verdis ($VCO) Token Sale & IDO", "Verdis ($VRS) Token Sale & IDO")
c = c.replace("Official Token Sale / IDO page for Verdis, the first net carbon-negative Layer-1 blockchain. Buy $VCO tokens", 
              "Official Token Sale / IDO page for Verdis, the first net carbon-negative Layer-1 blockchain. Buy $VRS tokens")

# UI text
replacements = [
    ("Buy VCO", "Buy VRS"),
    ("Buy $VCO", "Buy $VRS"),
    ("$VCO) Token Sale", "$VRS) Token Sale"),
    ("Verdis ($VCO)", "Verdis ($VRS)"),
    ("$VCO tokens", "$VRS tokens"),
    ("$VCO Tokens", "$VRS Tokens"),
    ("$VCO TOKENS", "$VRS TOKENS"),
    ("claim your $VCO", "claim your $VRS"),
    ("Base $VCO Allocation", "Base $VRS Allocation"),
    ("1 VCO = $0.001", "1 VRS = $0.001"),
    ("1 VCO =", "1 VRS ="),
    ("VCO = $0.001", "VRS = $0.001"),
    ("= 3,200,000 VCO", "= 3,200,000 VRS"),
    ("= 580,000 VCO", "= 580,000 VRS"),
    ("= 1,000 VCO", "= 1,000 VRS"),
    ("100,000,000,000 VCO", "100,000,000,000 VRS"),
    ("4850200000", "4850200000"),  # keep counter
    ("10B VCO", "10B VRS"),
    ("10% of total supply (10B VCO)", "10% of total supply (10B VRS)"),
    # dynamic text IDs
    (">1,600,000 VCO<", ">1,600,000 VRS<"),
    (">+160,000 VCO<", ">+160,000 VRS<"),
    (">1,760,000 VCO<", ">1,760,000 VRS<"),
    # carbon offsets note - VCO here is "Verdis Carbon Offsets" acronym, NOT the token
    # Keep that one as-is: "Verdis Carbon Offsets (VCO)" -> leave
]

for old, new in replacements:
    if old in c:
        n = c.count(old)
        c = c.replace(old, new)
        print(f"  {n}x: {old[:60]}")

# Fix remaining VCO that are token references (not "Verdis Carbon Offsets")
# The carbon offset line: "Verdis Carbon Offsets (VCO)" - keep this one
# All other VCO -> VRS
def replace_vco(m):
    # Check surrounding context
    start = max(0, m.start()-50)
    ctx = c[start:m.start()]
    if "Carbon Offsets" in ctx or "carbon offset" in ctx.lower():
        return m.group(0)  # keep as acronym for carbon offset
    return "VRS"

# Apply regex for remaining VCO tokens
c_before = c.count("VCO")
c = re.sub(r'\bVCO\b', replace_vco, c)

with open(path, "w") as f:
    f.write(c)

remaining = c.count("VCO")
print(f"\nOriginal: {original}, Remaining: {remaining}")
if remaining:
    for i, line in enumerate(c.splitlines(), 1):
        if "VCO" in line:
            print(f"  L{i}: {line.strip()[:100]}")
