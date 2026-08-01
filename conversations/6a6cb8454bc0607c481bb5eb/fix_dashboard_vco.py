#!/usr/bin/env python3
"""Fix VCO -> VRS in dashboard.html"""
import re

path = "/opt/verdis/app/dist/web/dashboard.html"
with open(path) as f:
    c = f.read()

original_count = c.count("VCO")

# === UI Label replacements (safe) ===
labels = [
    ("Buy VCO tokens with cryptocurrency", "Buy VRS tokens with cryptocurrency"),
    ("Buy VCO with crypto", "Buy VRS with crypto"),
    ("Buy VCO Tokens", "Buy VRS Tokens"),
    ("Buy VCO", "Buy VRS"),
    ("VCO Balance", "VRS Balance"),
    ("VCO Supply", "VRS Supply"),
    ("Add VCO Token", "Add VRS Token"),
    ("Staked VCO", "Staked VRS"),
    ("Send VCO", "Send VRS"),
    ("Claim 1000 VCO", "Claim 1000 VRS"),
    ("1000 VCO claimed!", "1000 VRS claimed!"),
    ("1000 VCO sent to", "1000 VRS sent to"),
    ("Per VCO Token", "Per VRS Token"),
    ("per VCO Token", "per VRS Token"),
    ("VCO tokens to test", "VRS tokens to test"),
    ("Claim Free VCO", "Claim Free VRS"),
    ("Free VCO", "Free VRS"),
    ("Delegate VCO", "Delegate VRS"),
    ("Stake VCO to validators", "Stake VRS to validators"),
    ("0 VCO", "0 VRS"),
    ("500,000 VCO", "500,000 VRS"),
    ("100,000 VCO", "100,000 VRS"),
    ("1,000 VCO", "1,000 VRS"),
    ("40,000,000,000 VCO", "40,000,000,000 VRS"),
    ("10,000,000,000 VCO", "10,000,000,000 VRS"),
    ("0.001 VCO", "0.001 VRS"),
    ("value='VCO'", "value='VRS'"),
    ('value="VCO"', 'value="VRS"'),
    (">VCO</option>", ">VRS</option>"),
    ("symbol:'VCO'", "symbol:'VRS'"),
    ('symbol:"VCO"', 'symbol:"VRS"'),
    ("addVCOToken", "addVRSToken"),
]

for old, new in labels:
    if old in c:
        n = c.count(old)
        c = c.replace(old, new)
        print(f"  {n}x: {old[:60]}")

# Fix dynamic JS balance strings like: + ' VCO'  or  +' VCO'
c = re.sub(r"(\+\s*['\"])\s*VCO(['\"])", r"\g<1> VRS\2", c)
print("  Regex: JS balance strings + ' VCO'")

# Fix .toLocaleString()+'B VCO' style
c = re.sub(r"(\.toLocaleString\(\)\s*\+\s*['\"][^'\"]*?)VCO(['\"])", r"\g<1>VRS\2", c)
print("  Regex: toLocaleString VCO patterns")

# Fix validator staked display: +' VCO' in template literals
c = re.sub(r"'([^']*)\bVCO\b([^']*)'", lambda m: "'" + m.group(1) + "VRS" + m.group(2) + "'"
           if "VCO" in m.group(1) + m.group(2) or True else m.group(0), c)

with open(path, "w") as f:
    f.write(c)

remaining = c.count("VCO")
print(f"\nOriginal VCO count: {original_count}")
print(f"Remaining VCO count: {remaining}")

# Show remaining
if remaining > 0:
    for i, line in enumerate(c.splitlines(), 1):
        if "VCO" in line:
            print(f"  Line {i}: {line.strip()[:100]}")
