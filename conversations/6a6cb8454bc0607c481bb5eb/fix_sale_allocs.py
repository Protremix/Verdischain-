#!/usr/bin/env python3
"""Fix remaining allocation values on Sale page."""

with open("/var/www/verdiscan/sale/index.html") as f:
    html = f.read()

# Fix Seed allocation: 2.4B → 3B
html = html.replace(
    '<div class="phase-meta-item"><div class="l">Allocation</div><div class="v">2.4B VRDX</div></div>',
    '<div class="phase-meta-item"><div class="l">Allocation</div><div class="v">3B VRDX</div></div>'
)

# Fix Private allocation: 3.6B → 3B
html = html.replace(
    '<div class="phase-meta-item"><div class="l">Allocation</div><div class="v">3.6B VRDX</div></div>',
    '<div class="phase-meta-item"><div class="l">Allocation</div><div class="v">3B VRDX</div></div>'
)

# Fix Private price text "Minimum $25,000 commitment. 20% bonus tokens." — price already updated
# Check if Private minimum should change — Rojs didn't specify, keep $25K

# Fix vesting monthly: Private was 150M → should be 125M (3B/24mo)
# Already done in previous script

with open("/var/www/verdiscan/sale/index.html", "w") as f:
    f.write(html)

# Verify
if "3B VRDX" in html and "2.4B VRDX" not in html and "3.6B VRDX" not in html:
    print("  \u2713 Allocations fixed: Seed=3B, Private=3B")
else:
    if "2.4B VRDX" in html:
        print("  \u2717 Still has 2.4B VRDX")
    if "3.6B VRDX" in html:
        print("  \u2717 Still has 3.6B VRDX")
    if "3B VRDX" in html:
        print("  \u2713 Has 3B VRDX")

print("Done")
