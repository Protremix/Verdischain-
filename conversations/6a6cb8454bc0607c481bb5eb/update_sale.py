#!/usr/bin/env python3
"""Update sale page with new VERDIS economic model."""
import re, math

with open('/opt/verdis-repo/dist/web/sale/index.html', 'r') as f:
    sale = f.read()

# 1. Meta description
sale = sale.replace(
    'content="Participate in the VRDX token sale. 100B total supply with phased distribution, vesting schedules, and referral bonuses."',
    'content="Participate in the VERDIS token sale. 100B max supply, 4-round fundraising: Seed $0.0015, Community $0.003, Presale $0.004, TGE $0.005. Total raised: $18M."'
)

# 2. Hero badge
sale = sale.replace(
    'IDO Live Now — Seed Sale Active',
    'VERDIS Token Sale — Seed Round Active'
)

# 3. Hero title and description
sale = sale.replace(
    'Buy <span class="accent">VRDX</span> at IDO prices',
    'Buy <span class="accent">VERDIS</span> at Seed prices'
)
sale = sale.replace(
    'VRDX powers the Verdis Chain — the eco-friendly Layer-1 blockchain with native DPoS, AMM DEX, and carbon credit tracking. Secure your allocation before public listing on the DEX.',
    'VERDIS powers the Verdis Chain — the eco-friendly Layer-1 blockchain with native DPoS, AMM DEX, and carbon credit tracking. Secure your allocation before TGE listing.'
)

# 4. Hero stats
sale = sale.replace(
    '<div class="hero-stat"><div class="label">Sale Price</div><div class="value">$0.0005</div></div>\n      <div class="hero-stat"><div class="label">Listing Price</div><div class="value">$0.10</div></div>\n      <div class="hero-stat"><div class="label">Bonus</div><div class="value">+30%</div></div>',
    '<div class="hero-stat"><div class="label">Seed Price</div><div class="value">$0.0015</div></div>\n      <div class="hero-stat"><div class="label">TGE Price</div><div class="value">$0.005</div></div>\n      <div class="hero-stat"><div class="label">Total Raised</div><div class="value">$18M</div></div>'
)

# 5. Floating card - current price
sale = sale.replace(
    '<div style="font-size:13px;color:var(--text-3);margin-bottom:8px">Current Sale Price</div>\n      <div class="price-big">$0.0005</div>\n      <div class="price-change">↑ 200x at listing</div>',
    '<div style="font-size:13px;color:var(--text-3);margin-bottom:8px">Current Round Price</div>\n      <div class="price-big">$0.0015</div>\n      <div class="price-change">70% discount to TGE</div>'
)

# 6. Floating card - sold/hard cap
sale = sale.replace(
    '<div class="mini-row"><span class="l">Sold: 0 VRDX</span><span class="v">0% of 12B</span></div>',
    '<div class="mini-row"><span class="l">Sold: 0 VRDX</span><span class="v">0% of 3B</span></div>'
)
sale = sale.replace(
    'Phase 1 Ends In',
    'Round 1 Ends In'
)
sale = sale.replace(
    '<div class="mini-row" style="margin-top:8px"><span class="l">Hard Cap</span><span class="v">$17.5M</span></div>',
    '<div class="mini-row" style="margin-top:8px"><span class="l">Hard Cap</span><span class="v">$4.5M</span></div>'
)

# 7. Floating card - allocation
sale = sale.replace(
    '<div class="mini-row"><span class="l">Investors</span><span class="v">12B (12%)</span></div>',
    '<div class="mini-row"><span class="l">Total Raised</span><span class="v">$18M</span></div>'
)
sale = sale.replace(
    '<div class="mini-row"><span class="l">Total Supply</span><span class="v" style="color:var(--accent)">100B VRDX</span></div>\n      <div class="mini-row"><span class="l">Your Max</span><span class="v">$500,000</span></div>',
    '<div class="mini-row"><span class="l">Total Supply</span><span class="v" style="color:var(--accent)">100B VRDX</span></div>\n      <div class="mini-row"><span class="l">FDV at TGE</span><span class="v">$500M</span></div>'
)

# 8. Replace all 4 phase cards with new 4 rounds
old_phases = re.search(r'<!-- SALE PHASES -->.*?<!-- COUNTDOWN -->', sale, re.DOTALL)
if old_phases:
    new_phases = """<!-- SALE PHASES -->
<div class="phases-section">
  <h2 class="section-title">Fundraising Rounds</h2>
  <p class="section-sub">VERDIS token sale runs in 4 rounds. Each round offers different pricing, allocations, and vesting terms. Total raised: $18,000,000. FDV at TGE: $500,000,000.</p>
  <div class="phases-grid">
    <!-- Round 1 — Seed / Strategic (Active) -->
    <div class="phase-card active">
      <div class="phase-badge active">Live Now</div>
      <h3>Round 1 — Seed / Strategic</h3>
      <div class="phase-price">$0.0015</div>
      <div class="phase-info">Strategic investors with long vesting commitment. 70% discount to TGE. 12-month cliff + 24-month linear vesting. 0% TGE unlock.</div>
      <div class="phase-progress">
        <div class="prog-label"><span class="l">Sold</span><span class="v">0 / 3B</span></div>
        <div class="prog-bar"><div class="prog-fill" style="width:0%"></div></div>
      </div>
      <div class="phase-meta">
        <div class="phase-meta-item"><div class="l">Allocation</div><div class="v">3B VRDX</div></div>
        <div class="phase-meta-item"><div class="l">Capital</div><div class="v">$4.5M</div></div>
      </div>
      <div class="phase-meta">
        <div class="phase-meta-item"><div class="l">Vesting</div><div class="v">12mo cliff + 24mo</div></div>
        <div class="phase-meta-item"><div class="l">TGE Unlock</div><div class="v">0%</div></div>
      </div>
      <button class="btn btn-sale" onclick="document.getElementById('buySection').scrollIntoView({behavior:'smooth'})">Buy Now</button>
    </div>

    <!-- Round 2 — Community -->
    <div class="phase-card">
      <div class="phase-badge upcoming">Upcoming</div>
      <h3>Round 2 — Community</h3>
      <div class="phase-price">$0.003</div>
      <div class="phase-info">Community allocation with 40% discount to TGE. 20% TGE unlock + 3-month cliff + 15-month linear vesting. KYC required.</div>
      <div class="phase-progress">
        <div class="prog-label"><span class="l">Sold</span><span class="v">0 / 1B</span></div>
        <div class="prog-bar"><div class="prog-fill" style="width:0%"></div></div>
      </div>
      <div class="phase-meta">
        <div class="phase-meta-item"><div class="l">Allocation</div><div class="v">1B VRDX</div></div>
        <div class="phase-meta-item"><div class="l">Capital</div><div class="v">$3M</div></div>
      </div>
      <div class="phase-meta">
        <div class="phase-meta-item"><div class="l">Vesting</div><div class="v">3mo cliff + 15mo</div></div>
        <div class="phase-meta-item"><div class="l">TGE Unlock</div><div class="v">20%</div></div>
      </div>
      <button class="btn btn-notify" onclick="notifyMe()">Notify Me</button>
    </div>

    <!-- Round 3 — Public Presale -->
    <div class="phase-card">
      <div class="phase-badge upcoming">Upcoming</div>
      <h3>Round 3 — Public Presale</h3>
      <div class="phase-price">$0.004</div>
      <div class="phase-info">Public presale. 20% discount to TGE. 25% TGE unlock + 6-month linear. Min $100, max $25,000. KYC + whitelist required. Anti-sybil: 1 allocation per identity.</div>
      <div class="phase-progress">
        <div class="prog-label"><span class="l">Sold</span><span class="v">0 / 2B</span></div>
        <div class="prog-bar"><div class="prog-fill" style="width:0%"></div></div>
      </div>
      <div class="phase-meta">
        <div class="phase-meta-item"><div class="l">Allocation</div><div class="v">2B VRDX</div></div>
        <div class="phase-meta-item"><div class="l">Capital</div><div class="v">$8M</div></div>
      </div>
      <div class="phase-meta">
        <div class="phase-meta-item"><div class="l">Vesting</div><div class="v">25% TGE + 6mo</div></div>
        <div class="phase-meta-item"><div class="l">Max/Wallet</div><div class="v">$25,000</div></div>
      </div>
      <button class="btn btn-notify" onclick="notifyMe()">Notify Me</button>
    </div>

    <!-- Round 4 — TGE / IDO -->
    <div class="phase-card">
      <div class="phase-badge upcoming">Upcoming</div>
      <h3>Round 4 — TGE / IDO</h3>
      <div class="phase-price">$0.005</div>
      <div class="phase-info">Token Generation Event. 100% liquid at TGE. Initial market cap: $40M (8B circulating). FDV: $500M. Public listing on DEX.</div>
      <div class="phase-progress">
        <div class="prog-label"><span class="l">Reserved</span><span class="v">0 / 0.5B</span></div>
        <div class="prog-bar"><div class="prog-fill" style="width:0%"></div></div>
      </div>
      <div class="phase-meta">
        <div class="phase-meta-item"><div class="l">Allocation</div><div class="v">0.5B VRDX</div></div>
        <div class="phase-meta-item"><div class="l">Capital</div><div class="v">$2.5M</div></div>
      </div>
      <div class="phase-meta">
        <div class="phase-meta-item"><div class="l">Vesting</div><div class="v">100% liquid</div></div>
        <div class="phase-meta-item"><div class="l">FDV</div><div class="v">$500M</div></div>
      </div>
      <button class="btn btn-notify" onclick="notifyMe()">Notify Me</button>
    </div>
  </div>
</div>

<!-- COUNTDOWN -->"""
    sale = sale[:old_phases.start()] + new_phases + sale[old_phases.end():]

# 9. Buy section - update price and remove bonus/ROI
sale = sale.replace(
    'Phase 1 IDO — $0.0005 per VRDX + 30% bonus',
    'Round 1 Seed — $0.0015 per VERDIS'
)

# Update buy calculator default values
sale = sale.replace(
    'value="1000" oninput="calculatePurchase()"',
    'value="1000" oninput="calculatePurchase()"'
)
sale = sale.replace(
    'value="2600000" style="color:var(--accent)"',
    'value="666667" style="color:var(--accent)"'
)

# Update output section - remove bonus
sale = sale.replace(
    '<label>You Will Receive (incl. 30% bonus)</label>\n      <div class="output-value" id="totalReceive">48,000 VRDX</div>\n      <div class="output-rate" id="outputRate">Rate: 1 USDT = 2,600 VRDX (with bonus)</div>',
    '<label>You Will Receive</label>\n      <div class="output-value" id="totalReceive">666,667 VRDX</div>\n      <div class="output-rate" id="outputRate">Rate: 1 USDT = 666.67 VRDX</div>'
)

# Update buy details - remove bonus and ROI
sale = sale.replace(
    '<div class="detail-row"><span class="l">Base Tokens</span><span class="v" id="baseTokens">40,000 VRDX</span></div>\n      <div class="detail-row"><span class="l">Bonus Tokens (30%)</span><span class="v accent" id="bonusTokens">8,000 VRDX</span></div>\n      <div class="detail-row"><span class="l">Price Per Token</span><span class="v">$0.0005</span></div>\n      <div class="detail-row"><span class="l">Listing Price</span><span class="v">$0.10</span></div>\n      <div class="detail-row"><span class="l">Potential ROI at Listing</span><span class="v accent">+19,900%</span></div>',
    '<div class="detail-row"><span class="l">Tokens</span><span class="v" id="baseTokens">666,667 VRDX</span></div>\n      <div class="detail-row"><span class="l">Price Per Token</span><span class="v">$0.0015</span></div>\n      <div class="detail-row"><span class="l">TGE Price</span><span class="v">$0.005</span></div>\n      <div class="detail-row"><span class="l">Discount to TGE</span><span class="v accent">70%</span></div>'
)

# Update buy button text
sale = sale.replace(
    '🔒 Secure payment • Tokens locked until TGE • Vesting varies by phase (see schedule below)',
    '🔒 Secure payment • Tokens locked per vesting schedule • KYC required for all rounds'
)

# 10. Allocation chart - update from 6 to 9 categories
# Replace SVG donut and legend
old_alloc = re.search(r'<!-- ALLOCATION -->.*?<!-- VESTING SCHEDULE -->', sale, re.DOTALL)
if old_alloc:
    # 9 segments: 25%, 20%, 15%, 10%, 10%, 5%, 3%, 2%, 5%
    # Circumference = 2 * pi * 100 = 628.32
    circ = 2 * math.pi * 100
    segments = [
        (25, '#16a34a'), (20, '#26a17b'), (15, '#a855f7'), (10, '#627eea'),
        (10, '#fbbf24'), (5, '#4ade80'), (3, '#3b82f6'), (2, '#ec4899'), (5, '#f97316')
    ]
    offset = 0
    circles = '<svg width="280" height="280" viewBox="0 0 280 280"><circle cx="140" cy="140" r="100" fill="none" stroke="#1a1a1a" stroke-width="40"/>'
    for pct, color in segments:
        dash = pct * circ / 100
        gap = circ - dash
        circles += f'<circle cx="140" cy="140" r="100" fill="none" stroke="{color}" stroke-width="40" stroke-dasharray="{dash:.1f} {gap:.1f}" stroke-dashoffset="{-offset:.1f}" transform="rotate(-90 140 140)"/>'
        offset += dash
    circles += '</svg>'

    new_alloc = f"""<!-- ALLOCATION -->
<div class="alloc-section">
  <h2 class="section-title">Token Allocation</h2>
  <p class="section-sub">100B max supply distributed across 9 categories for long-term utility, security, and sustainability.</p>
  <div class="alloc-chart">
    <div class="alloc-grid">
      <div class="donut-container">
        {circles}
        <div class="donut-center">
          <div class="total">100B</div>
          <div class="label">Total Supply</div>
        </div>
      </div>
      <div class="alloc-legend">
        <div class="legend-item"><div class="legend-dot" style="background:#16a34a"></div><div class="l-info"><div class="l-name">Ecosystem &amp; Grants</div><div class="l-pct">25% • 25B VRDX</div></div><div class="l-val">10yr grants</div></div>
        <div class="legend-item"><div class="legend-dot" style="background:#26a17b"></div><div class="l-info"><div class="l-name">PoS Staking</div><div class="l-pct">20% • 20B VRDX</div></div><div class="l-val">2B/yr</div></div>
        <div class="legend-item"><div class="legend-dot" style="background:#a855f7"></div><div class="l-info"><div class="l-name">Treasury</div><div class="l-pct">15% • 15B VRDX</div></div><div class="l-val">Multisig</div></div>
        <div class="legend-item"><div class="legend-dot" style="background:#627eea"></div><div class="l-info"><div class="l-name">Development</div><div class="l-pct">10% • 10B VRDX</div></div><div class="l-val">4yr vest</div></div>
        <div class="legend-item"><div class="legend-dot" style="background:#fbbf24"></div><div class="l-info"><div class="l-name">Liquidity</div><div class="l-pct">10% • 10B VRDX</div></div><div class="l-val">DEX + CEX</div></div>
        <div class="legend-item"><div class="legend-dot" style="background:#4ade80"></div><div class="l-info"><div class="l-name">Community</div><div class="l-pct">5% • 5B VRDX</div></div><div class="l-val">Hackathons</div></div>
        <div class="legend-item"><div class="legend-dot" style="background:#3b82f6"></div><div class="l-info"><div class="l-name">Seed / Strategic</div><div class="l-pct">3% • 3B VRDX</div></div><div class="l-val">$4.5M</div></div>
        <div class="legend-item"><div class="legend-dot" style="background:#ec4899"></div><div class="l-info"><div class="l-name">Public Presale</div><div class="l-pct">2% • 2B VRDX</div></div><div class="l-val">$8M</div></div>
        <div class="legend-item"><div class="legend-dot" style="background:#f97316"></div><div class="l-info"><div class="l-name">Team &amp; Advisors</div><div class="l-pct">5% • 5B VRDX</div></div><div class="l-val">4yr vest</div></div>
      </div>
    </div>
  </div>
</div>

<!-- VESTING SCHEDULE -->"""
    sale = sale[:old_alloc.start()] + new_alloc + sale[old_alloc.end():]

# 11. Vesting schedule table - update
old_vest = re.search(r'<div class="vesting-section">.*?</div>\s*</div>\s*<!-- WHITELIST -->', sale, re.DOTALL)
if old_vest:
    new_vest = """<div class="vesting-section">
  <h2 class="section-title">Vesting Schedule</h2>
  <p class="section-sub">Tokens are released according to the vesting schedule for each round. TGE circulating supply: 8B (8%).</p>
  <div class="vesting-table">
    <table>
      <thead><tr><th>Round</th><th>TGE Unlock</th><th>Cliff</th><th>Vesting Period</th><th>Monthly Release</th><th>Status</th></tr></thead>
      <tbody>
        <tr><td><strong>Seed / Strategic</strong></td><td>0%</td><td>12 months</td><td>36 months</td><td class="mono">125M / month</td><td><span class="vesting-badge active">Active</span></td></tr>
        <tr><td><strong>Community</strong></td><td>20% (1B)</td><td>3 months</td><td>18 months</td><td class="mono">300M / month</td><td><span class="vesting-badge locked">Upcoming</span></td></tr>
        <tr><td><strong>Public Presale</strong></td><td>25% (0.5B)</td><td>None</td><td>6 months</td><td class="mono">250M / month</td><td><span class="vesting-badge locked">Upcoming</span></td></tr>
        <tr><td><strong>TGE / IDO</strong></td><td>100%</td><td>None</td><td>Liquid</td><td class="mono">At TGE</td><td><span class="vesting-badge locked">Upcoming</span></td></tr>
        <tr><td><strong>Team &amp; Advisors</strong></td><td>0%</td><td>12 months</td><td>48 months</td><td class="mono">138.9M / month</td><td><span class="vesting-badge locked">Locked</span></td></tr>
        <tr><td><strong>Ecosystem Grants</strong></td><td>4% (1B)</td><td>None</td><td>120 months</td><td class="mono">200M / month</td><td><span class="vesting-badge unlocked">Active</span></td></tr>
      </tbody>
    </table>
  </div>
</div>

<!-- WHITELIST -->"""
    sale = sale[:old_vest.start()] + new_vest + sale[old_vest.end():]

# 12. Update FAQ
sale = sale.replace(
    'VRDX is the native utility token of Verdis Chain, an eco-friendly Layer-1 blockchain built with Substrate. It\'s used for transaction fees, staking, governance, DEX trading, and carbon credit transactions. Total supply is fixed at 100 billion tokens.',
    'VERDIS (VRDX) is the native utility token of Verdis Chain, an eco-friendly Layer-1 blockchain built with Substrate. It\'s used for transaction fees, staking, governance, DEX trading, and carbon credit transactions. Max supply is 100 billion tokens. This is a utility token, not an investment vehicle.'
)
sale = sale.replace(
    'Tokens are distributed at the Token Generation Event (TGE). Private Sale buyers have a 12-month cliff, then monthly vesting over 24 months. The TGE is scheduled for September 2026.',
    'Tokens are distributed at the Token Generation Event (TGE). Seed investors have a 12-month cliff, then monthly vesting over 24 months. TGE circulating supply: 8B (8% of max supply). FDV at TGE: $500M.'
)
sale = sale.replace(
    'The minimum investment for Phase 1 (Seed Sale) is $50,000 in USDT or ETH. The maximum per wallet is $500,000 to ensure fair distribution. Whitelist members get higher caps.',
    'The minimum investment for Round 1 (Seed) varies by round: Seed requires strategic commitment, Community has lower minimums, and Public Presale has a $100 minimum with $25,000 maximum per wallet. KYC is required for all rounds.'
)

# 13. Update JS calculatePurchase function for new price
sale = sale.replace(
    'const price = 0.0005;',
    'const price = 0.0015;'
)
sale = sale.replace(
    'const bonusRate = 1.30;',
    'const bonusRate = 1.0;'
)

with open('/opt/verdis-repo/dist/web/sale/index.html', 'w') as f:
    f.write(sale)
print("Sale page updated!")
