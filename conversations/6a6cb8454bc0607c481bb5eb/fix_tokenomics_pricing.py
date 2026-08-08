#!/usr/bin/env python3
"""Update Tokenomics page pricing to match $17.5M total raise."""

with open("/var/www/verdiscan/tokenomics/index.html") as f:
    html = f.read()

# --- IDO Phase Cards ---

# Seed: price $0.005 → $0.0005, allocation 2.4B → 3B, hard cap $12M → $1.5M
html = html.replace(
    '$0.005 / VRDX',
    '$0.0005 / VRDX'
)
html = html.replace(
    '2.4B VRDX allocation. Minimum $50,000. 12-month cliff, 24-month vest. 30% bonus tokens.',
    '3B VRDX allocation. Minimum $50,000. 12-month cliff, 24-month vest. 30% bonus tokens.'
)
html = html.replace(
    '<div><strong>Allocation</strong>2.4B VRDX</div>\n        <div><strong>Hard Cap</strong>$12M</div>',
    '<div><strong>Allocation</strong>3B VRDX</div>\n        <div><strong>Hard Cap</strong>$1.5M</div>'
)

# Private: price $0.010 → $0.001, allocation 3.6B → 3B, hard cap $36M → $3M
html = html.replace(
    '$0.010 / VRDX',
    '$0.001 / VRDX'
)
html = html.replace(
    '3.6B VRDX allocation. Minimum $25,000. 12-month cliff, 24-month vest. 20% bonus tokens.',
    '3B VRDX allocation. Minimum $25,000. 12-month cliff, 24-month vest. 20% bonus tokens.'
)
html = html.replace(
    '<div><strong>Allocation</strong>3.6B VRDX</div>\n        <div><strong>Hard Cap</strong>$36M</div>',
    '<div><strong>Allocation</strong>3B VRDX</div>\n        <div><strong>Hard Cap</strong>$3M</div>'
)

# Presale: price $0.025 → $0.002, allocation 4.0B → 4B (same), hard cap $100M → $8M
html = html.replace(
    '$0.025 / VRDX',
    '$0.002 / VRDX'
)
html = html.replace(
    '4.0B VRDX allocation. Minimum $100. 25% at TGE, 3-month cliff, 12-month vest. 20% bonus.',
    '4B VRDX allocation. Minimum $100. 25% at TGE, 3-month cliff, 12-month vest. 20% bonus.'
)
html = html.replace(
    '<div><strong>Allocation</strong>4.0B VRDX</div>\n        <div><strong>Hard Cap</strong>$100M</div>',
    '<div><strong>Allocation</strong>4B VRDX</div>\n        <div><strong>Hard Cap</strong>$8M</div>'
)

# Public: price $0.05 → $0.0025, allocation 2.0B → 2B, hard cap $100M → $5M
html = html.replace(
    '$0.05 / VRDX',
    '$0.0025 / VRDX'
)
html = html.replace(
    '2.0B VRDX allocation. No minimum. 40% at TGE, 1-month cliff, 6-month vest. First-come, first-served.',
    '2B VRDX allocation. No minimum. 40% at TGE, 1-month cliff, 6-month vest. First-come, first-served.'
)
html = html.replace(
    '<div><strong>Allocation</strong>2.0B VRDX</div>\n        <div><strong>Hard Cap</strong>$100M</div>',
    '<div><strong>Allocation</strong>2B VRDX</div>\n        <div><strong>Hard Cap</strong>$5M</div>'
)

# --- Category breakdown text ---
html = html.replace(
    '4 IDO phases \u2014 Phase 1 (Seed, 2.4B at $0.005), Phase 2 (Private, 3.6B at $0.010), Phase 3 (Presale, 4.0B at $0.025), Phase 4 (Public, 2.0B at $0.05).',
    '4 IDO phases \u2014 Phase 1 (Seed, 3B at $0.0005), Phase 2 (Private, 3B at $0.001), Phase 3 (Presale, 4B at $0.002), Phase 4 (Public, 2B at $0.0025).'
)

# --- Hard cap in category card ---
html = html.replace(
    'Hard cap $250M',
    'Hard cap $17.5M'
)

# --- Floating card investor breakdown ---
html = html.replace(
    '<span class="l">Phase 1 (Seed)</span><span class="v">2.4B</span>',
    '<span class="l">Phase 1 (Seed)</span><span class="v">3B</span>'
)
html = html.replace(
    '<span class="l">Phase 2 (Private)</span><span class="v">3.6B</span>',
    '<span class="l">Phase 2 (Private)</span><span class="v">3B</span>'
)
html = html.replace(
    '<span class="l">Phase 3 (Presale)</span><span class="v">4.0B</span>',
    '<span class="l">Phase 3 (Presale)</span><span class="v">4B</span>'
)
html = html.replace(
    '<span class="l">Phase 4 (Public)</span><span class="v">2.0B</span>',
    '<span class="l">Phase 4 (Public)</span><span class="v">2B</span>'
)

# --- Vesting monthly releases ---
# Seed: 3B / 24 months = 125M/month
html = html.replace(
    '<td class="mono">100M / month</td>',
    '<td class="mono">125M / month</td>'
)
# Private: 3B / 24 months = 125M/month
html = html.replace(
    '<td class="mono">150M / month</td>',
    '<td class="mono">125M / month</td>'
)

with open("/var/www/verdiscan/tokenomics/index.html", "w") as f:
    f.write(html)

# Verify
checks = [
    ("$0.0005", "seed price"),
    ("$0.001", "private price"),
    ("$0.002", "presale price"),
    ("$0.0025", "public price"),
    ("$1.5M", "seed hard cap"),
    ("$3M", "private hard cap"),
    ("$8M", "presale hard cap"),
    ("$5M", "public hard cap"),
    ("$17.5M", "total hard cap"),
    ("3B VRDX", "seed alloc"),
    ("3B at $0.0005", "category text"),
]
for text, label in checks:
    if text in html:
        print(f"  \u2713 {label}")
    else:
        print(f"  \u2717 {label}: NOT FOUND")

print("Tokenomics page updated")
