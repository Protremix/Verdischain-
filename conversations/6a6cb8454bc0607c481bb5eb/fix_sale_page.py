#!/usr/bin/env python3
"""Fix the VRDX Sale page: IDO from zero, correct calculations."""

import re

with open("/var/www/verdiscan/sale/index.html") as f:
    html = f.read()

# 1. Hero badge: "Presale Live Now — Phase 2 Active" → "IDO Live Now — Phase 1 Active"
html = html.replace(
    "Presale Live Now \u2014 Phase 2 Active",
    "IDO Live Now \u2014 Phase 1 Active"
)

# 2. Hero heading
html = html.replace(
    'at presale prices',
    'at IDO prices'
)

# 3. Hero description
html = html.replace(
    'Secure your allocation before public listing.',
    'Secure your allocation before public listing on the DEX.'
)

# 4. Hero stats: Sale Price $0.025 → $0.010
html = html.replace(
    '<div class="hero-stat"><div class="label">Sale Price</div><div class="value">$0.025</div></div>',
    '<div class="hero-stat"><div class="label">Sale Price</div><div class="value">$0.010</div></div>'
)

# 5. Float card main: price $0.025 → $0.010, allocation bar 67% → 0%
html = html.replace('<div class="price-big">$0.025</div>', '<div class="price-big">$0.010</div>')
html = html.replace('\u2191 300% at listing', '\u2191 900% at listing')
html = html.replace('<div class="alloc-fill" style="width:67%"></div>', '<div class="alloc-fill" style="width:0%"></div>')
html = html.replace(
    '<span class="l">Sold: 8.04B VRDX</span><span class="v">67% of 12B</span>',
    '<span class="l">Sold: 0 VRDX</span><span class="v">0% of 12B</span>'
)

# 6. Float card price: "Phase 2 Ends In" → "Phase 1 Ends In"
html = html.replace('Phase 2 Ends In', 'Phase 1 Ends In')
html = html.replace('id="heroCountdown">14d 06h 32m', 'id="heroCountdown">21d 06h 32m')

# 7. Raised: $201M → $0
html = html.replace(
    '<span class="l">Raised</span><span class="v" style="color:var(--accent)">$201M</span>',
    '<span class="l">Raised</span><span class="v" style="color:var(--accent)">$0</span>'
)

# 8. Phase 1 — from "Sold Out" to "Live Now" with 0 sold
old_p1 = """    <div class="phase-card past">
      <div class="phase-badge sold">Sold Out</div>
      <h3>Phase 1 \u2014 Private Sale</h3>
      <div class="phase-price">$0.010 <span class="old">$0.10</span></div>
      <div class="phase-info">Early investors and strategic partners. Minimum $25,000 commitment.</div>
      <div class="phase-progress">
        <div class="prog-label"><span class="l">Sold</span><span class="v">3.6B / 3.6B</span></div>
        <div class="prog-bar"><div class="prog-fill" style="width:100%"></div></div>
      </div>
      <div class="phase-meta">
        <div class="phase-meta-item"><div class="l">Allocation</div><div class="v">3.6B VRDX</div></div>
        <div class="phase-meta-item"><div class="l">Vesting</div><div class="v">12mo cliff</div></div>
      </div>
      <button class="btn btn-sale" disabled>Sold Out</button>
    </div>"""

new_p1 = """    <div class="phase-card active">
      <div class="phase-badge active">Live Now</div>
      <h3>Phase 1 \u2014 Private Sale</h3>
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
    </div>"""

html = html.replace(old_p1, new_p1)

# 9. Phase 2 — from "Live Now" to "Upcoming" with 0 sold
old_p2 = """    <div class="phase-card active">
      <div class="phase-badge active">Live Now</div>
      <h3>Phase 2 \u2014 Presale</h3>
      <div class="phase-price">$0.025 <span class="old">$0.10</span></div>
      <div class="phase-info">Public presale. Minimum $100. 20% bonus tokens included. Whitelist recommended.</div>
      <div class="phase-progress">
        <div class="prog-label"><span class="l">Sold</span><span class="v">4.44B / 6B</span></div>
        <div class="prog-bar"><div class="prog-fill" style="width:74%"></div></div>
      </div>
      <div class="phase-meta">
        <div class="phase-meta-item"><div class="l">Allocation</div><div class="v">6B VRDX</div></div>
        <div class="phase-meta-item"><div class="l">Vesting</div><div class="v">25% TGE</div></div>
      </div>
      <button class="btn btn-sale" onclick="document.getElementById('buySection').scrollIntoView({behavior:'smooth'})">Buy Now</button>
    </div>"""

new_p2 = """    <div class="phase-card">
      <div class="phase-badge upcoming">Upcoming</div>
      <h3>Phase 2 \u2014 Presale</h3>
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
    </div>"""

html = html.replace(old_p2, new_p2)

# 10. Buy interface header
html = html.replace(
    "Phase 2 Presale \u2014 $0.025 per VRDX + 20% bonus",
    "Phase 1 IDO \u2014 $0.010 per VRDX + 20% bonus"
)

# 11. Buy details: Price Per Token $0.025 → $0.010
html = html.replace(
    '<span class="l">Price Per Token</span><span class="v">$0.025</span>',
    '<span class="l">Price Per Token</span><span class="v">$0.010</span>'
)

# 12. Potential ROI at Listing: +300% → +900%
html = html.replace(
    '<span class="l">Potential ROI at Listing</span><span class="v accent">+300%</span>',
    '<span class="l">Potential ROI at Listing</span><span class="v accent">+900%</span>'
)

# 13. Whitelist count: 8,247 → 0
html = html.replace(
    'id="wlCount">8,247<',
    'id="wlCount">0<'
)

# 14. Sale config in JS
old_config = """  phase: 2,
  pricePerToken: 0.025,
  listingPrice: 0.10,
  bonus: 0.20, // 20%
  hardCap: 300000000, // $300M
  raised: 201000000, // $201M
  sold: 4440000000, // 4.44B VRDX
  totalAllocation: 6000000000, // 6B for phase 2
  endDate: new Date('2026-08-21T23:59:59').getTime(),"""

new_config = """  phase: 1,
  pricePerToken: 0.010,
  listingPrice: 0.10,
  bonus: 0.20, // 20%
  hardCap: 300000000, // $300M
  raised: 0, // $0 - IDO not started
  sold: 0, // 0 VRDX sold
  totalAllocation: 3600000000, // 3.6B for Phase 1
  endDate: new Date('2026-08-29T23:59:59').getTime(),"""

html = html.replace(old_config, new_config)

# 15. Countdown default values: 14 → 21
html = html.replace('id="cd-days">14<', 'id="cd-days">21<')

# 16. Vesting table: Phase 1 Private Sale from "Locked" to "Active"
old_vest1 = """          <td><strong>Private Sale</strong></td>
          <td>0%</td><td>12 months</td><td>24 months</td><td class="mono">1.5B / month</td>
          <td><span class="vesting-badge locked">Locked</span></td>"""

new_vest1 = """          <td><strong>Private Sale</strong></td>
          <td>0%</td><td>12 months</td><td>24 months</td><td class="mono">1.5B / month</td>
          <td><span class="vesting-badge active">Active</span></td>"""

html = html.replace(old_vest1, new_vest1)

# 17. Vesting table: Presale from "Active" to "Upcoming"
old_vest2 = """          <td><strong>Presale (Phase 2)</strong></td>
          <td>25%</td><td>3 months</td><td>12 months</td><td class="mono">6.25% / month</td>
          <td><span class="vesting-badge active">Active</span><div class="vesting-progress"><div class="vp-fill" style="width:0%"></div></div></td>"""

new_vest2 = """          <td><strong>Presale (Phase 2)</strong></td>
          <td>25%</td><td>3 months</td><td>12 months</td><td class="mono">6.25% / month</td>
          <td><span class="vesting-badge locked">Upcoming</span></td>"""

html = html.replace(old_vest2, new_vest2)

# 18. Section subtitle
html = html.replace(
    "VRDX token sale runs in three phases.",
    "VRDX IDO runs in three phases."
)

# 19. FAQ: min investment
html = html.replace(
    "The minimum investment for Phase 2 (Presale) is $100 in USDT or ETH.",
    "The minimum investment for Phase 1 (Private Sale) is $25,000 in USDT or ETH."
)

# 20. FAQ: bonus question
html = html.replace(
    "During Phase 2 presale, every purchase includes a 20% bonus in VRDX tokens. For example, if you buy 40,000 VRDX for $1,000, you receive 48,000 VRDX total. This bonus is in addition to the already discounted presale price of $0.025 (vs $0.10 listing price).",
    "During Phase 1 IDO, every purchase includes a 20% bonus in VRDX tokens. For example, if you buy 100,000 VRDX for $1,000, you receive 120,000 VRDX total. This bonus is in addition to the already discounted IDO price of $0.010 (vs $0.10 listing price)."
)

# 21. FAQ: lock-up period
html = html.replace(
    "Yes. Presale tokens have a 3-month cliff",
    "Yes. IDO tokens have a 12-month cliff"
)
html = html.replace(
    "then monthly unlocks. 25% unlocks at TGE, then 6.25% per month for 12 months.",
    "then monthly unlocks over 24 months after a 12-month cliff."
)

# 22. Buy button confirmation
html = html.replace(
    "2. Tokens will be locked until TGE (September 2026)\\n3. 25% unlocks at TGE, rest vests over 12 months",
    "2. Tokens will be locked until TGE\\n3. 12-month cliff, then monthly vesting over 24 months"
)

# 23. Secure payment footer text
html = html.replace(
    "\U0001f512 Secure payment \u2022 Tokens locked until TGE \u2022 25% unlocked at listing",
    "\U0001f512 Secure payment \u2022 Tokens locked until TGE \u2022 12-month cliff, then monthly vesting"
)

# 24. Buy sub text
html = html.replace(
    "Phase 1 IDO \u2014 $0.010 per VRDX + 20% bonus",
    "Phase 1 IDO \u2014 $0.010 per VRDX + 20% bonus"
)

# 25. FAQ: "When will tokens be distributed?" answer
html = html.replace(
    "Tokens are distributed at the Token Generation Event (TGE). Presale buyers receive 25% at TGE, with the remaining 75% vested over 12 months after a 3-month cliff.",
    "Tokens are distributed at the Token Generation Event (TGE). Private Sale buyers have a 12-month cliff, then monthly vesting over 24 months."
)

# 26. Vesting table: Public Sale row stays "Upcoming" (already correct)

with open("/var/www/verdiscan/sale/index.html", "w") as f:
    f.write(html)

print("All changes applied successfully")

# Verify key changes
checks = [
    ("IDO Live Now", "hero badge"),
    ("IDO prices", "hero heading"),
    ("$0.010", "sale price"),
    ("0 / 3.6B", "phase 1 progress"),
    ("0 / 6B", "phase 2 progress"),
    ("Sold: 0 VRDX", "hero sold"),
    ("phase: 1", "config phase"),
    ("pricePerToken: 0.010", "config price"),
    ("raised: 0", "config raised"),
    ("sold: 0", "config sold"),
    ("wlCount\">0<", "whitelist count"),
    ("Phase 1 IDO", "buy header"),
    ("+900%", "ROI"),
]
for text, label in checks:
    if text in html:
        print(f"  \u2713 {label}: found")
    else:
        print(f"  \u2717 {label}: NOT FOUND")
