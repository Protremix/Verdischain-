#!/usr/bin/env python3
"""Add Seed Sale phase to the Sale page and update all references."""

with open("/var/www/verdiscan/sale/index.html") as f:
    html = f.read()

# 1. Update hero badge
html = html.replace(
    "IDO Live Now — Phase 1 Active",
    "IDO Live Now — Seed Sale Active"
)

# 2. Update hero sale price
html = html.replace(
    '<div class="hero-stat"><div class="label">Sale Price</div><div class="value">$0.010</div></div>',
    '<div class="hero-stat"><div class="label">Sale Price</div><div class="value">$0.005</div></div>'
)

# 3. Update hero bonus
html = html.replace(
    '<div class="hero-stat"><div class="label">Bonus</div><div class="value">+20%</div></div>',
    '<div class="hero-stat"><div class="label">Bonus</div><div class="value">+30%</div></div>'
)

# 4. Update float card price
html = html.replace(
    '<div class="price-big">$0.010</div>',
    '<div class="price-big">$0.005</div>'
)

# 5. Update "900% at listing" → "1900% at listing"
html = html.replace(
    '↑ 900% at listing',
    '↑ 1900% at listing'
)

# 6. Update phases description from "three" to "four"
html = html.replace(
    "VRDX IDO runs in three phases. Each phase offers different pricing and allocations.",
    "VRDX IDO runs in four phases. Each phase offers different pricing and allocations."
)

# 7. Update phases grid CSS from 3 to 4 columns
html = html.replace(
    ".phases-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:24px; }",
    ".phases-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; }"
)

# Also add responsive rule for 4 columns
html = html.replace(
    "@media(max-width:768px) { .alloc-grid { grid-template-columns:1fr; } }",
    "@media(max-width:1024px) { .phases-grid { grid-template-columns:repeat(2,1fr); } } @media(max-width:768px) { .phases-grid { grid-template-columns:1fr; } .alloc-grid { grid-template-columns:1fr; } }"
)

# 8. Replace the entire phases grid section
old_phases = """    <!-- Phase 1 -->
    <div class="phase-card active">
      <div class="phase-badge active">Live Now</div>
      <h3>Phase 1 — Private Sale</h3>
      <div class="phase-price">$0.010 <span class="old">$0.10</span></div>
      <div class="phase-info">Early investors and strategic partners. Minimum $25,000 commitment.</div>
      <div class="phase-progress">
        <div class="prog-label"><span class="l">Sold</span><span class="v">0 / 3.6B</span></div>
        <div class="prog-bar"><div class="prog-fill" style="width:0%"></div></div>
      </div>
      <div class="phase-meta">
        <div class="phase-meta-item"><div class="l">Allocation</div><div class="v">3.6B VRDX</div></div>
        <div class="phase-meta-item"><div class="l">Vesting</div><div class="v">12mo cliff</div></div>
      </div>
      <button class="btn btn-sale" onclick="document.getElementById('buySection').scrollIntoView({behavior:'smooth'})">Buy Now</button>
    </div>

    <!-- Phase 2 (Active) -->
    <div class="phase-card">
      <div class="phase-badge upcoming">Upcoming</div>
      <h3>Phase 2 — Presale</h3>
      <div class="phase-price">$0.025 <span class="old">$0.10</span></div>
      <div class="phase-info">Public presale. Minimum $100. 20% bonus tokens included. Whitelist recommended.</div>
      <div class="phase-progress">
        <div class="prog-label"><span class="l">Sold</span><span class="v">0 / 6B</span></div>
        <div class="prog-bar"><div class="prog-fill" style="width:0%"></div></div>
      </div>
      <div class="phase-meta">
        <div class="phase-meta-item"><div class="l">Allocation</div><div class="v">6B VRDX</div></div>
        <div class="phase-meta-item"><div class="l">Vesting</div><div class="v">25% TGE</div></div>
      </div>
      <button class="btn btn-notify" onclick="notifyMe()">Notify Me</button>
    </div>

    <!-- Phase 3 -->
    <div class="phase-card">
      <div class="phase-badge upcoming">Upcoming</div>
      <h3>Phase 3 — Public Sale</h3>
      <div class="phase-price">$0.05 <span class="old">$0.10</span></div>
      <div class="phase-info">Public token sale. No minimum. First-come, first-served until hard cap reached.</div>
      <div class="phase-progress">
        <div class="prog-label"><span class="l">Reserved</span><span class="v">0 / 2.4B</span></div>
        <div class="prog-bar"><div class="prog-fill" style="width:0%"></div></div>
      </div>
      <div class="phase-meta">
        <div class="phase-meta-item"><div class="l">Allocation</div><div class="v">2.4B VRDX</div></div>
        <div class="phase-meta-item"><div class="l">Starts</div><div class="v">Sep 1, 2026</div></div>
      </div>
      <button class="btn btn-notify" onclick="notifyMe()">Notify Me</button>
    </div>"""

new_phases = """    <!-- Phase 1 — Seed Sale (Active) -->
    <div class="phase-card active">
      <div class="phase-badge active">Live Now</div>
      <h3>Phase 1 — Seed Sale</h3>
      <div class="phase-price">$0.005 <span class="old">$0.10</span></div>
      <div class="phase-info">Earliest investors and strategic partners. Minimum $50,000 commitment. 30% bonus tokens.</div>
      <div class="phase-progress">
        <div class="prog-label"><span class="l">Sold</span><span class="v">0 / 2.4B</span></div>
        <div class="prog-bar"><div class="prog-fill" style="width:0%"></div></div>
      </div>
      <div class="phase-meta">
        <div class="phase-meta-item"><div class="l">Allocation</div><div class="v">2.4B VRDX</div></div>
        <div class="phase-meta-item"><div class="l">Vesting</div><div class="v">12mo cliff</div></div>
      </div>
      <button class="btn btn-sale" onclick="document.getElementById('buySection').scrollIntoView({behavior:'smooth'})">Buy Now</button>
    </div>

    <!-- Phase 2 — Private Sale -->
    <div class="phase-card">
      <div class="phase-badge upcoming">Upcoming</div>
      <h3>Phase 2 — Private Sale</h3>
      <div class="phase-price">$0.010 <span class="old">$0.10</span></div>
      <div class="phase-info">Early investors and strategic partners. Minimum $25,000 commitment. 20% bonus tokens.</div>
      <div class="phase-progress">
        <div class="prog-label"><span class="l">Sold</span><span class="v">0 / 3.6B</span></div>
        <div class="prog-bar"><div class="prog-fill" style="width:0%"></div></div>
      </div>
      <div class="phase-meta">
        <div class="phase-meta-item"><div class="l">Allocation</div><div class="v">3.6B VRDX</div></div>
        <div class="phase-meta-item"><div class="l">Vesting</div><div class="v">12mo cliff</div></div>
      </div>
      <button class="btn btn-notify" onclick="notifyMe()">Notify Me</button>
    </div>

    <!-- Phase 3 — Presale -->
    <div class="phase-card">
      <div class="phase-badge upcoming">Upcoming</div>
      <h3>Phase 3 — Presale</h3>
      <div class="phase-price">$0.025 <span class="old">$0.10</span></div>
      <div class="phase-info">Public presale. Minimum $100. 20% bonus tokens included. Whitelist recommended.</div>
      <div class="phase-progress">
        <div class="prog-label"><span class="l">Sold</span><span class="v">0 / 4B</span></div>
        <div class="prog-bar"><div class="prog-fill" style="width:0%"></div></div>
      </div>
      <div class="phase-meta">
        <div class="phase-meta-item"><div class="l">Allocation</div><div class="v">4B VRDX</div></div>
        <div class="phase-meta-item"><div class="l">Vesting</div><div class="v">25% TGE</div></div>
      </div>
      <button class="btn btn-notify" onclick="notifyMe()">Notify Me</button>
    </div>

    <!-- Phase 4 — Public Sale -->
    <div class="phase-card">
      <div class="phase-badge upcoming">Upcoming</div>
      <h3>Phase 4 — Public Sale</h3>
      <div class="phase-price">$0.05 <span class="old">$0.10</span></div>
      <div class="phase-info">Public token sale. No minimum. First-come, first-served until hard cap reached.</div>
      <div class="phase-progress">
        <div class="prog-label"><span class="l">Reserved</span><span class="v">0 / 2B</span></div>
        <div class="prog-bar"><div class="prog-fill" style="width:0%"></div></div>
      </div>
      <div class="phase-meta">
        <div class="phase-meta-item"><div class="l">Allocation</div><div class="v">2B VRDX</div></div>
        <div class="phase-meta-item"><div class="l">Starts</div><div class="v">Sep 1, 2026</div></div>
      </div>
      <button class="btn btn-notify" onclick="notifyMe()">Notify Me</button>
    </div>"""

html = html.replace(old_phases, new_phases)

# 9. Update vesting schedule table
old_vesting = """        <tr>
          <td><strong>Private Sale</strong></td>
          <td>0%</td><td>12 months</td><td>24 months</td><td class="mono">1.5B / month</td>
          <td><span class="vesting-badge active">Active</span></td>
        </tr>
        <tr>
          <td><strong>Presale (Phase 2)</strong></td>
          <td>25%</td><td>3 months</td><td>12 months</td><td class="mono">6.25% / month</td>
          <td><span class="vesting-badge locked">Upcoming</span></td>
        </tr>
        <tr>
          <td><strong>Public Sale</strong></td>
          <td>40%</td><td>1 month</td><td>6 months</td><td class="mono">10% / month</td>
          <td><span class="vesting-badge locked">Upcoming</span></td>
        </tr>"""

new_vesting = """        <tr>
          <td><strong>Seed Sale (Phase 1)</strong></td>
          <td>0%</td><td>12 months</td><td>24 months</td><td class="mono">100M / month</td>
          <td><span class="vesting-badge active">Active</span></td>
        </tr>
        <tr>
          <td><strong>Private Sale (Phase 2)</strong></td>
          <td>0%</td><td>12 months</td><td>24 months</td><td class="mono">150M / month</td>
          <td><span class="vesting-badge locked">Upcoming</span></td>
        </tr>
        <tr>
          <td><strong>Presale (Phase 3)</strong></td>
          <td>25%</td><td>3 months</td><td>12 months</td><td class="mono">6.25% / month</td>
          <td><span class="vesting-badge locked">Upcoming</span></td>
        </tr>
        <tr>
          <td><strong>Public Sale (Phase 4)</strong></td>
          <td>40%</td><td>1 month</td><td>6 months</td><td class="mono">10% / month</td>
          <td><span class="vesting-badge locked">Upcoming</span></td>
        </tr>"""

html = html.replace(old_vesting, new_vesting)

# 10. Update SALE_CONFIG
old_config = """const SALE_CONFIG = {
  phase: 1,
  pricePerToken: 0.010,
  listingPrice: 0.10,
  bonus: 0.20, // 20%
  hardCap: 300000000, // $300M
  raised: 0, // $0 - IDO not started
  sold: 0, // 0 VRDX sold
  totalAllocation: 3600000000, // 3.6B for Phase 1
  endDate: new Date('2026-08-29T23:59:59').getTime(),
};"""

new_config = """const SALE_CONFIG = {
  phase: 1,
  pricePerToken: 0.005,
  listingPrice: 0.10,
  bonus: 0.30, // 30%
  hardCap: 250000000, // $250M total across all phases
  raised: 0, // $0 - IDO not started
  sold: 0, // 0 VRDX sold
  totalAllocation: 2400000000, // 2.4B for Seed Sale (Phase 1)
  endDate: new Date('2026-08-29T23:59:59').getTime(),
};"""

html = html.replace(old_config, new_config)

# 11. Update minimum investment check from $100 to $50,000 for Seed Sale
html = html.replace(
    "if (usdValue < 100) { alert('Minimum investment is $100'); return; }",
    "if (usdValue < 50000) { alert('Minimum investment for Seed Sale is $50,000'); return; }"
)

# 12. Update max investment per wallet
html = html.replace(
    "if (usdValue > 50000) { alert('Maximum investment per wallet is $50,000'); return; }",
    "if (usdValue > 500000) { alert('Maximum investment per wallet is $500,000'); return; }"
)

# 13. Update "Your Max" in float card
html = html.replace(
    '<span class="l">Your Max</span><span class="v">$50,000</span>',
    '<span class="l">Your Max</span><span class="v">$500,000</span>'
)

# 14. Update hard cap from $300M to $250M
html = html.replace(
    '<span class="l">Hard Cap</span><span class="v">$300M</span>',
    '<span class="l">Hard Cap</span><span class="v">$250M</span>'
)

# 15. Update whitelist allocation cap
html = html.replace(
    "Higher allocation cap ($75,000 vs $50,000)",
    "Higher allocation cap ($750,000 vs $500,000)"
)

# 16. Update Phase 3 notify to Phase 4
html = html.replace(
    "when Phase 3 opens",
    "when Phase 4 opens"
)

html = html.replace(
    "when Phase 3 opens on September 1, 2026",
    "when Phase 4 opens on September 1, 2026"
)

# 17. Update allocation legend investors value
html = html.replace(
    '<div class="l-val">$300M</div>',
    '<div class="l-val">$250M</div>'
)

with open("/var/www/verdiscan/sale/index.html", "w") as f:
    f.write(html)

# Verify
checks = [
    ("Phase 1 — Seed Sale", "seed phase added"),
    ("Phase 2 — Private Sale", "private renumbered"),
    ("Phase 3 — Presale", "presale renumbered"),
    ("Phase 4 — Public Sale", "public renumbered"),
    ("$0.005", "seed price"),
    ("+30%", "seed bonus"),
    ("2.4B VRDX", "seed allocation"),
    ("four phases", "description updated"),
    ("250M", "hard cap updated"),
    ("50000", "min investment"),
]
for text, label in checks:
    if text in html:
        print(f"  \u2713 {label}")
    else:
        print(f"  \u2717 {label}: NOT FOUND")

print("Sale page updated with Seed Sale phase")
