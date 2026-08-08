#!/usr/bin/env python3
"""Update Sale page pricing so 12B total = $17.5M."""

with open("/var/www/verdiscan/sale/index.html") as f:
    html = f.read()

# --- Hero section ---
html = html.replace(
    '<div class="hero-stat"><div class="label">Sale Price</div><div class="value">$0.005</div></div>',
    '<div class="hero-stat"><div class="label">Sale Price</div><div class="value">$0.0005</div></div>'
)
html = html.replace(
    '<div class="hero-stat"><div class="label">Bonus</div><div class="value">+30%</div></div>',
    '<div class="hero-stat"><div class="label">Bonus</div><div class="value">+30%</div></div>'
)

# --- Float card ---
html = html.replace(
    '<div class="price-big">$0.005</div>',
    '<div class="price-big">$0.0005</div>'
)
html = html.replace(
    '↑ 1900% at listing',
    '↑ 200x at listing'
)

# Hard cap in float card
html = html.replace(
    '<span class="l">Hard Cap</span><span class="v">$250M</span>',
    '<span class="l">Hard Cap</span><span class="v">$17.5M</span>'
)

# --- Phase cards ---
# Seed Sale
html = html.replace(
    '<div class="phase-price">$0.005 <span class="old">$0.10</span></div>',
    '<div class="phase-price">$0.0005 <span class="old">$0.10</span></div>'
)
html = html.replace(
    '<div class="phase-info">Earliest investors and strategic partners. Minimum $50,000 commitment. 30% bonus tokens.</div>',
    '<div class="phase-info">Earliest investors and strategic partners. Minimum $50,000 commitment. 30% bonus tokens.</div>'
)
html = html.replace(
    '<div class="prog-label"><span class="l">Sold</span><span class="v">0 / 2.4B</span></div>',
    '<div class="prog-label"><span class="l">Sold</span><span class="v">0 / 3B</span></div>'
)
html = html.replace(
    '<div class="phase-meta-item"><div class="l">Allocation</div><div class="v">2.4B VRDX</div></div>\n      <div class="phase-meta-item"><div class="l">Vesting</div><div class="v">12mo cliff</div></div>\n      </div>\n      <button class="btn btn-sale"',
    '<div class="phase-meta-item"><div class="l">Allocation</div><div class="v">3B VRDX</div></div>\n      <div class="phase-meta-item"><div class="l">Vesting</div><div class="v">12mo cliff</div></div>\n      </div>\n      <button class="btn btn-sale"'
)

# Private Sale
html = html.replace(
    '<div class="phase-price">$0.010 <span class="old">$0.10</span></div>',
    '<div class="phase-price">$0.001 <span class="old">$0.10</span></div>'
)
html = html.replace(
    '<div class="prog-label"><span class="l">Sold</span><span class="v">0 / 3.6B</span></div>',
    '<div class="prog-label"><span class="l">Sold</span><span class="v">0 / 3B</span></div>'
)
html = html.replace(
    '<div class="phase-meta-item"><div class="l">Allocation</div><div class="v">3.6B VRDX</div></div>\n      <div class="phase-meta-item"><div class="l">Vesting</div><div class="v">12mo cliff</div></div>\n      </div>\n      <button class="btn btn-notify"',
    '<div class="phase-meta-item"><div class="l">Allocation</div><div class="v">3B VRDX</div></div>\n      <div class="phase-meta-item"><div class="l">Vesting</div><div class="v">12mo cliff</div></div>\n      </div>\n      <button class="btn btn-notify"'
)

# Presale
html = html.replace(
    '<div class="phase-price">$0.025 <span class="old">$0.10</span></div>',
    '<div class="phase-price">$0.002 <span class="old">$0.10</span></div>'
)
html = html.replace(
    '<div class="prog-label"><span class="l">Sold</span><span class="v">0 / 4B</span></div>',
    '<div class="prog-label"><span class="l">Sold</span><span class="v">0 / 4B</span></div>'
)
# Presale allocation already says 4B — keep it

# Public Sale
html = html.replace(
    '<div class="phase-price">$0.05 <span class="old">$0.10</span></div>',
    '<div class="phase-price">$0.0025 <span class="old">$0.10</span></div>'
)
html = html.replace(
    '<div class="prog-label"><span class="l">Reserved</span><span class="v">0 / 2B</span></div>',
    '<div class="prog-label"><span class="l">Reserved</span><span class="v">0 / 2B</span></div>'
)
# Public allocation already says 2B — keep it

# --- Vesting schedule ---
# Seed: 3B over 24 months = 125M/month
html = html.replace(
    '<td class="mono">100M / month</td>',
    '<td class="mono">125M / month</td>'
)
# Private: 3B over 24 months = 125M/month
html = html.replace(
    '<td class="mono">150M / month</td>',
    '<td class="mono">125M / month</td>'
)

# --- SALE_CONFIG ---
old_config = """const SALE_CONFIG = {
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

new_config = """const SALE_CONFIG = {
  phase: 1,
  pricePerToken: 0.0005,
  listingPrice: 0.10,
  bonus: 0.30, // 30%
  hardCap: 17500000, // $17.5M total across all 4 phases
  raised: 0, // $0 - IDO not started
  sold: 0, // 0 VRDX sold
  totalAllocation: 3000000000, // 3B for Seed Sale (Phase 1)
  endDate: new Date('2026-08-29T23:59:59').getTime(),
};"""

html = html.replace(old_config, new_config)

# --- Allocation legend ---
html = html.replace(
    '<div class="l-val">$250M</div>',
    '<div class="l-val">$17.5M</div>'
)

# --- "0% of 12B" in float card progress ---
html = html.replace(
    '<span class="v">0% of 12B</span>',
    '<span class="v">0% of 12B</span>'
)

with open("/var/www/verdiscan/sale/index.html", "w") as f:
    f.write(html)

# Verify
checks = [
    ("$0.0005", "seed price $0.0005"),
    ("$0.001", "private price $0.001"),
    ("$0.002", "presale price $0.002"),
    ("$0.0025", "public price $0.0025"),
    ("$17.5M", "hard cap $17.5M"),
    ("3B VRDX", "seed 3B alloc"),
    ("200x at listing", "200x gain"),
    ("17500000", "JS config hardCap"),
    ("pricePerToken: 0.0005", "JS config price"),
    ("3000000000", "JS config totalAlloc"),
]
for text, label in checks:
    if text in html:
        print(f"  \u2713 {label}")
    else:
        print(f"  \u2717 {label}: NOT FOUND")

print("Sale page updated - 12B = $17.5M")
