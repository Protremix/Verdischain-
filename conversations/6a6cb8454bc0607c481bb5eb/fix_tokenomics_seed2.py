#!/usr/bin/env python3
"""Fix tokenomics IDO section - match actual file content."""

with open("/var/www/verdiscan/tokenomics/index.html") as f:
    html = f.read()

# The grid has repeat(3,1fr) not repeat(4,1fr) - fix that
html = html.replace(
    '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:24px">',
    '<div id="ido-grid" style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px">'
)

# Replace Phase 1 Private Sale with Seed Sale
html = html.replace(
    'Phase 1 \u2014 Private Sale',
    'Phase 1 \u2014 Seed Sale'
)
html = html.replace(
    '<div class="cat-pct" style="margin:8px 0">$0.010 / VRDX</div>\n      <div class="cat-body" style="font-size:12px">3.6B VRDX allocation. Minimum $25,000. 12-month cliff, 24-month vest. 20% bonus tokens.</div>\n      <div class="cat-grid">\n        <div><strong>Allocation</strong>3.6B VRDX</div>\n        <div><strong>Hard Cap</strong>$36M</div>\n      </div>\n    </div>',
    '<div class="cat-pct" style="margin:8px 0">$0.005 / VRDX</div>\n      <div class="cat-body" style="font-size:12px">2.4B VRDX allocation. Minimum $50,000. 12-month cliff, 24-month vest. 30% bonus tokens.</div>\n      <div class="cat-grid">\n        <div><strong>Allocation</strong>2.4B VRDX</div>\n        <div><strong>Hard Cap</strong>$12M</div>\n      </div>\n    </div>'
)

# Renumber Phase 2 Presale → Phase 2 Private Sale
html = html.replace(
    'Phase 2 \u2014 Presale',
    'Phase 2 \u2014 Private Sale'
)
html = html.replace(
    '<div class="cat-pct" style="margin:8px 0">$0.025 / VRDX</div>\n      <div class="cat-body" style="font-size:12px">6.0B VRDX allocation. Minimum $100. 25% at TGE, 3-month cliff, 12-month vest. 20% bonus.</div>\n      <div class="cat-grid">\n        <div><strong>Allocation</strong>6.0B VRDX</div>\n        <div><strong>Hard Cap</strong>$150M</div>\n      </div>\n    </div>',
    '<div class="cat-pct" style="margin:8px 0">$0.010 / VRDX</div>\n      <div class="cat-body" style="font-size:12px">3.6B VRDX allocation. Minimum $25,000. 12-month cliff, 24-month vest. 20% bonus tokens.</div>\n      <div class="cat-grid">\n        <div><strong>Allocation</strong>3.6B VRDX</div>\n        <div><strong>Hard Cap</strong>$36M</div>\n      </div>\n    </div>'
)

# Renumber Phase 3 Public Sale → Phase 3 Presale
html = html.replace(
    'Phase 3 \u2014 Public Sale',
    'Phase 3 \u2014 Presale'
)
html = html.replace(
    '<div class="cat-pct" style="margin:8px 0">$0.05 / VRDX</div>\n      <div class="cat-body" style="font-size:12px">2.4B VRDX allocation. No minimum. 40% at TGE, 1-month cliff, 6-month vest. First-come, first-served.</div>\n      <div class="cat-grid">\n        <div><strong>Allocation</strong>2.4B VRDX</div>\n        <div><strong>Hard Cap</strong>$120M</div>\n      </div>\n    </div>\n  </div>',
    '<div class="cat-pct" style="margin:8px 0">$0.025 / VRDX</div>\n      <div class="cat-body" style="font-size:12px">4.0B VRDX allocation. Minimum $100. 25% at TGE, 3-month cliff, 12-month vest. 20% bonus.</div>\n      <div class="cat-grid">\n        <div><strong>Allocation</strong>4.0B VRDX</div>\n        <div><strong>Hard Cap</strong>$100M</div>\n      </div>\n    </div>\n    <div class="cat-card">\n      <div class="cat-header">\n        <div class="cat-title">Phase 4 \u2014 Public Sale</div>\n        <span class="badge badge-locked">Upcoming</span>\n      </div>\n      <div class="cat-pct" style="margin:8px 0">$0.05 / VRDX</div>\n      <div class="cat-body" style="font-size:12px">2.0B VRDX allocation. No minimum. 40% at TGE, 1-month cliff, 6-month vest. First-come, first-served.</div>\n      <div class="cat-grid">\n        <div><strong>Allocation</strong>2.0B VRDX</div>\n        <div><strong>Hard Cap</strong>$100M</div>\n      </div>\n    </div>\n  </div>'
)

# Fix remaining "3 IDO phases" references
html = html.replace(
    "12B allocated to investors across 3 IDO phases.",
    "12B allocated to investors across 4 IDO phases."
)
html = html.replace(
    '<div class="sub">3 IDO phases</div>',
    '<div class="sub">4 IDO phases</div>'
)
html = html.replace(
    "<strong>Distribution:</strong> 3 IDO phases \u2014 Phase 1 (Private, 3.6B at $0.010), Phase 2 (Presale, 6.0B at $0.025), Phase 3 (Public, 2.4B at $0.05).",
    "<strong>Distribution:</strong> 4 IDO phases \u2014 Phase 1 (Seed, 2.4B at $0.005), Phase 2 (Private, 3.6B at $0.010), Phase 3 (Presale, 4.0B at $0.025), Phase 4 (Public, 2.0B at $0.05)."
)

# Fix floating card values
html = html.replace(
    '<span class="l">Phase 1 (Seed)</span><span class="v">3.6B</span>',
    '<span class="l">Phase 1 (Seed)</span><span class="v">2.4B</span>'
)
html = html.replace(
    '<span class="l">Phase 2 (Private)</span><span class="v">6.0B</span>',
    '<span class="l">Phase 2 (Private)</span><span class="v">3.6B</span>'
)
html = html.replace(
    '<span class="l">Phase 3 (Presale)</span><span class="v">2.4B</span>',
    '<span class="l">Phase 3 (Presale)</span><span class="v">4.0B</span>'
)

# Add Phase 4 to floating card
html = html.replace(
    '<div class="mini-row"><span class="l">Phase 3 (Presale)</span><span class="v">4.0B</span></div>\n    </div>',
    '<div class="mini-row"><span class="l">Phase 3 (Presale)</span><span class="v">4.0B</span></div>\n      <div class="mini-row"><span class="l">Phase 4 (Public)</span><span class="v">2.0B</span></div>\n    </div>'
)

# Add responsive CSS for 4-column IDO grid
html = html.replace(
    '@media(max-width:768px){.metrics-grid{grid-template-columns:repeat(2,1fr)}}',
    '@media(max-width:1024px){#ido-grid{grid-template-columns:repeat(2,1fr)!important}}@media(max-width:768px){#ido-grid{grid-template-columns:1fr!important}.metrics-grid{grid-template-columns:repeat(2,1fr)}}'
)

with open("/var/www/verdiscan/tokenomics/index.html", "w") as f:
    f.write(html)

# Verify
checks = [
    ("Phase 1 \u2014 Seed Sale", "seed phase"),
    ("Phase 2 \u2014 Private Sale", "private"),
    ("Phase 3 \u2014 Presale", "presale"),
    ("Phase 4 \u2014 Public Sale", "public"),
    ("$0.005", "seed price"),
    ("4 IDO phases", "4 phases"),
    ("repeat(4,1fr)", "4-col grid"),
    ("ido-grid", "responsive id"),
]
for text, label in checks:
    if text in html:
        print(f"  \u2713 {label}")
    else:
        print(f"  \u2717 {label}: NOT FOUND")

print("Tokenomics page updated with Seed Sale")
