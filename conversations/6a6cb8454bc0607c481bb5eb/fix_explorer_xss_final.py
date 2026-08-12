#!/usr/bin/env python3
"""Final XSS fixes for explorer."""
import re

PATH = "/var/www/verdiscan/explorer/index.html"

with open(PATH, "r") as f:
    h = f.read()

r = 0

# Fix ext.hash in td
old = """'<td class="hash">'+ext.hash+'</td>'"""
new = """'<td class="hash">'+escapeHtml(ext.hash)+'</td>'"""
if old in h:
    h = h.replace(old, new)
    r += 1
    print("Fixed: ext.hash in td")

# Fix b.hash in showBlock onclick
h2 = re.sub(
    r"showBlock\(([^)]*)b\.hash([^)]*)\)",
    lambda m: m.group(0).replace("b.hash", "escapeAttr(b.hash)"),
    h
)
if h2 != h:
    h = h2
    r += 1
    print("Fixed: b.hash in showBlock onclick")

# Check for any remaining unescaped chain data in innerHTML
remaining = []
for pattern_name, pattern in [
    ("ext.method", r"'\+ext\.method[+'\"]"),
    ("ext.signer", r"'\+ext\.signer[+'\"]"),
    ("ext.hash", r"'\+ext\.hash[+'\"]"),
    ("signerDisplay", r"'\+signerDisplay[+'\"]"),
    ("pool.token", r"'\+pool\.token[+\"]"),
    ("v.name", r"'\+v\.name[+'\"]"),
]:
    matches = re.findall(pattern, h)
    if matches:
        remaining.append(f"{pattern_name}: {len(matches)} unescaped")

if remaining:
    print(f"\nRemaining unescaped: {', '.join(remaining)}")
else:
    print("\nAll known chain data patterns are escaped!")

with open(PATH, "w") as f:
    f.write(h)

print(f"Total: {r} fixes")
