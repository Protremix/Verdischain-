#!/usr/bin/env python3
"""Update tokenomics page to include Seed Sale phase."""

with open("/var/www/verdiscan/tokenomics/index.html") as f:
    html = f.read()

# Replace the 3 IDO phase cards with 4
old_ido = '''  <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px">
    <div class="cat-card" style="border-color:var(--accent);box-shadow:0 0 24px var(--accent-glow)">
      <div class="cat-header">
        <div class="cat-title">Phase 1 \u2014 Private Sale</div>
        <span class="badge badge-info">Live Now</span>
      </div>
      <div class="cat-pct" style="margin:8px 0">$0.010 / VRDX</div>
      <div class="cat-body" style="font-size:12px">3.6B VRDX allocation. Minimum $25,000. 12-month cliff, 24-month vest. 20% bonus tokens.</div>
      <div class="cat-grid">
        <div><strong>Allocation</strong>3.6B VRDX</div>
        <div><strong>Hard Cap</strong>$36M</div>
      </div>
    </div>
    <div class="cat-card">
      <div class="cat-header">
        <div class="cat-title">Phase 2 \u2014 Presale</div>
        <span class="badge badge-locked">Upcoming</span>
      </div>
      <div class="cat-pct" style="margin:8px 0">$0.025 / VRDX</div>
      <div class="cat-body" style="font-size:12px">6.0B VRDX allocation. Minimum $100. 25% at TGE, 3-month cliff, 12-month vest. 20% bonus.</div>
      <div class="cat-grid">
        <div><strong>Allocation</strong>6.0B VRDX</div>
        <div><strong>Hard Cap</strong>$150M</div>
      </div>
    </div>
    <div class="cat-card">
      <div class="cat-header">
        <div class="cat-title">Phase 3 \u2014 Public Sale</div>
        <span class="badge badge-locked">Upcoming</span>
      </div>
      <div class="cat-pct" style="margin:8px 0">$0.05 / VRDX</div>
      <div class="cat-body" style="font-size:12px">2.4B VRDX allocation. No minimum. 40% at TGE, 1-month cliff, 6-month vest. First-come, first-served.</div>
      <div class="cat-grid">
        <div><strong>Allocation</strong>2.4B VRDX</div>
        <div><strong>Hard Cap</strong>$120M</div>
      </div>
    </div>
  </div>'''

new_ido = '''  <div id="ido-grid" style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px">
    <div class="cat-card" style="border-color:var(--accent);box-shadow:0 0 24px var(--accent-glow)">
      <div class="cat-header">
        <div class="cat-title">Phase 1 \u2014 Seed Sale</div>
        <span class="badge badge-info">Live Now</span>
      </div>
      <div class="cat-pct" style="margin:8px 0">$0.005 / VRDX</div>
      <div class="cat-body" style="font-size:12px">2.4B VRDX allocation. Minimum $50,000. 12-month cliff, 24-month vest. 30% bonus tokens.</div>
      <div class="cat-grid">
        <div><strong>Allocation</strong>2.4B VRDX</div>
        <div><strong>Hard Cap</strong>$12M</div>
      </div>
    </div>
    <div class="cat-card">
      <div class="cat-header">
        <div class="cat-title">Phase 2 \u2014 Private Sale</div>
        <span class="badge badge-locked">Upcoming</span>
      </div>
      <div class="cat-pct" style="margin:8px 0">$0.010 / VRDX</div>
      <div class="cat-body" style="font-size:12px">3.6B VRDX allocation. Minimum $25,000. 12-month cliff, 24-month vest. 20% bonus tokens.</div>
      <div class="cat-grid">
        <div><strong>Allocation</strong>3.6B VRDX</div>
        <div><strong>Hard Cap</strong>$36M</div>
      </div>
    </div>
    <div class="cat-card">
      <div class="cat-header">
        <div class="cat-title">Phase 3 \u2014 Presale</div>
        <span class="badge badge-locked">Upcoming</span>
      </div>
      <div class="cat-pct" style="margin:8px 0">$0.025 / VRDX</div>
      <div class="cat-body" style="font-size:12px">4.0B VRDX allocation. Minimum $100. 25% at TGE, 3-month cliff, 12-month vest. 20% bonus.</div>
      <div class="cat-grid">
        <div><strong>Allocation</strong>4.0B VRDX</div>
        <div><strong>Hard Cap</strong>$100M</div>
      </div>
    </div>
    <div class="cat-card">
      <div class="cat-header">
        <div class="cat-title">Phase 4 \u2014 Public Sale</div>
        <span class="badge badge-locked">Upcoming</span>
      </div>
      <div class="cat-pct" style="margin:8px 0">$0.05 / VRDX</div>
      <div class="cat-body" style="font-size:12px">2.0B VRDX allocation. No minimum. 40% at TGE, 1-month cliff, 6-month vest. First-come, first-served.</div>
      <div class="cat-grid">
        <div><strong>Allocation</strong>2.0B VRDX</div>
        <div><strong>Hard Cap</strong>$100M</div>
      </div>
    </div>
  </div>'''

html = html.replace(old_ido, new_ido)

# Update IDO section description
html = html.replace(
    "12B VRDX allocated to investors across 3 IDO phases.",
    "12B VRDX allocated to investors across 4 IDO phases."
)
html = html.replace(
    "12B VRDX allocated to investors across 4 IDO phases. Each phase offers different pricing and vesting terms.",
    "12B VRDX allocated across 4 IDO phases: Seed, Private, Presale, and Public. Each phase offers different pricing and vesting terms."
)

# Update vesting schedule to include Seed Sale
old_vest = """      <tr>
        <td><strong>Private Sale (Phase 1)</strong></td>
        <td>0%</td><td>12 months</td><td>24 months</td><td class="mono">1.5B / month</td>
        <td><span class="badge badge-info">IDO Active</span></td>
      </tr>
      <tr>
        <td><strong>Presale (Phase 2)</strong></td>
        <td>25%</td><td>3 months</td><td>12 months</td><td class="mono">6.25% / month</td>
        <td><span class="badge badge-locked">Upcoming</span></td>
      </tr>
      <tr>
        <td><strong>Public Sale (Phase 3)</strong></td>
        <td>40%</td><td>1 month</td><td>6 months</td><td class="mono">10% / month</td>
        <td><span class="badge badge-locked">Upcoming</span></td>
      </tr>"""

new_vest = """      <tr>
        <td><strong>Seed Sale (Phase 1)</strong></td>
        <td>0%</td><td>12 months</td><td>24 months</td><td class="mono">100M / month</td>
        <td><span class="badge badge-info">IDO Active</span></td>
      </tr>
      <tr>
        <td><strong>Private Sale (Phase 2)</strong></td>
        <td>0%</td><td>12 months</td><td>24 months</td><td class="mono">150M / month</td>
        <td><span class="badge badge-locked">Upcoming</span></td>
      </tr>
      <tr>
        <td><strong>Presale (Phase 3)</strong></td>
        <td>25%</td><td>3 months</td><td>12 months</td><td class="mono">6.25% / month</td>
        <td><span class="badge badge-locked">Upcoming</span></td>
      </tr>
      <tr>
        <td><strong>Public Sale (Phase 4)</strong></td>
        <td>40%</td><td>1 month</td><td>6 months</td><td class="mono">10% / month</td>
        <td><span class="badge badge-locked">Upcoming</span></td>
      </tr>"""

html = html.replace(old_vest, new_vest)

# Update floating card investor allocation breakdown
html = html.replace(
    'Phase 1 (Private)',
    'Phase 1 (Seed)'
)
html = html.replace(
    'Phase 2 (Presale)',
    'Phase 2 (Private)'
)
html = html.replace(
    'Phase 3 (Public)</span><span class="v">2.4B',
    'Phase 3 (Presale)</span><span class="v">4.0B'
)

# Add Phase 4 line
html = html.replace(
    'Phase 3 (Presale)</span><span class="v">4.0B</span></div>\n    </div>',
    'Phase 3 (Presale)</span><span class="v">4.0B</span></div>\n      <div class="mini-row"><span class="l">Phase 4 (Public)</span><span class="v">2.0B</span></div>\n    </div>'
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
    ("Phase 2 \u2014 Private Sale", "private renumbered"),
    ("Phase 3 \u2014 Presale", "presale renumbered"),
    ("Phase 4 \u2014 Public Sale", "public renumbered"),
    ("$0.005", "seed price"),
    ("4 IDO phases", "4 phases desc"),
    ("Seed Sale (Phase 1)", "vesting seed"),
]
for text, label in checks:
    if text in html:
        print(f"  \u2713 {label}")
    else:
        print(f"  \u2717 {label}: NOT FOUND")

print("Tokenomics page updated")
