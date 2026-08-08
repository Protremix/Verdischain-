#!/usr/bin/env python3
"""Update tokenomics and whitepaper pages with new VERDIS economic model."""

import re

# ============================================================================
# TOKENOMICS PAGE UPDATES
# ============================================================================
with open('/opt/verdis-repo/dist/web/tokenomics/index.html', 'r') as f:
    tokenomics = f.read()

# 1. Meta description
tokenomics = tokenomics.replace(
    'content="VRDX token economics: 100B total supply, 12B investor allocation, 6-category distribution model, vesting schedules, and ecosystem incentives."',
    'content="VERDIS token economics: 100B max supply, 9-category allocation, 4-round fundraising, 10-year vesting, staking economics, and economic simulation."'
)
tokenomics = tokenomics.replace(
    'content="100B total supply distributed across 6 categories for long-term decentralization and sustainability."',
    'content="100B max supply distributed across 9 categories with 4-round fundraising for long-term utility, security, and sustainability."'
)

# 2. Hero stats
tokenomics = tokenomics.replace(
    '<div class="hero-stat"><div class="label">Investor Alloc.</div><div class="value">12,000,000,000</div></div>',
    '<div class="hero-stat"><div class="label">Total Raised</div><div class="value">$18,000,000</div></div>'
)
tokenomics = tokenomics.replace(
    '<div class="hero-stat"><div class="label">Categories</div><div class="value">6</div></div>',
    '<div class="hero-stat"><div class="label">TGE Price</div><div class="value">$0.005</div></div>'
)

# 3. Hero floating card - max supply stays 100B
# Update investor allocation card
tokenomics = tokenomics.replace(
    '<div style="font-size:12px;color:var(--text-3);margin-bottom:6px">Investor Allocation</div>',
    '<div style="font-size:12px;color:var(--text-3);margin-bottom:6px">Total Raised</div>'
)
# Replace the IDO phase rows in floating card
tokenomics = tokenomics.replace(
    '<div class="mini-row" style="margin-top:8px"><span class="l">Phase 1 (Seed)</span><span class="v">3B</span></div>',
    '<div class="mini-row" style="margin-top:8px"><span class="l">Seed (3B)</span><span class="v">$4.5M</span></div>'
)
tokenomics = tokenomics.replace(
    '<div class="mini-row"><span class="l">Phase 3 (Presale)</span><span class="v">4B</span></div>',
    '<div class="mini-row"><span class="l">Presale (2B)</span><span class="v">$8M</span></div>'
)

# 4. Metric cards
tokenomics = tokenomics.replace(
    '<div class="metric-card"><div class="label">Investor Allocation</div><div class="value">12B (12%)</div><div class="sub">4 IDO phases</div></div>',
    '<div class="metric-card"><div class="label">Total Raised</div><div class="value">$18M</div><div class="sub">4 fundraising rounds</div></div>'
)
tokenomics = tokenomics.replace(
    '<div class="metric-card"><div class="label">Community & Staking</div><div class="value">25B (25%)</div><div class="sub">Validator rewards</div></div>',
    '<div class="metric-card"><div class="label">Staking Pool</div><div class="value">20B (20%)</div><div class="sub">10-year emissions</div></div>'
)
tokenomics = tokenomics.replace(
    '<div class="metric-card"><div class="label">Eco Fund</div><div class="value">18B (18%)</div><div class="sub">Carbon credits</div></div>',
    '<div class="metric-card"><div class="label">TGE Circulating</div><div class="value">8B (8%)</div><div class="sub">At mainnet launch</div></div>'
)

# 5. Distribution section title and subtitle
tokenomics = tokenomics.replace(
    '6-Category Token Allocation',
    '9-Category Token Allocation'
)
tokenomics = tokenomics.replace(
    'The VRDX supply is distributed across 6 dedicated categories to maintain network security, incentivize validators, fund ecosystem growth, and ensure liquidity.',
    'The VERDIS supply is distributed across 9 dedicated categories to maintain network security, incentivize validators, fund ecosystem growth, ensure liquidity, and support long-term sustainability.'
)

# 6. Distribution table - replace 6 rows with 9 rows
old_table = """<tr><td><span class="cat-dot" style="background:#16a34a"></span>Community Rewards</td><td>25%</td><td class="mono">25,000,000,000</td></tr>
          <tr><td><span class="cat-dot" style="background:#26a17b"></span>Eco Fund</td><td>18%</td><td class="mono">18,000,000,000</td></tr>
          <tr><td><span class="cat-dot" style="background:#627eea"></span>Team &amp; Advisors</td><td>15%</td><td class="mono">15,000,000,000</td></tr>
          <tr><td><span class="cat-dot" style="background:#fbbf24"></span>DEX Liquidity</td><td>15%</td><td class="mono">15,000,000,000</td></tr>
          <tr><td><span class="cat-dot" style="background:#a855f7"></span>Treasury Reserve</td><td>15%</td><td class="mono">15,000,000,000</td></tr>
          <tr><td><span class="cat-dot" style="background:#4ade80"></span>Investors (IDO)</td><td>12%</td><td class="mono">12,000,000,000</td></tr>"""

new_table = """<tr><td><span class="cat-dot" style="background:#16a34a"></span>Ecosystem &amp; Developer Grants</td><td>25%</td><td class="mono">25,000,000,000</td></tr>
          <tr><td><span class="cat-dot" style="background:#26a17b"></span>PoS Staking Rewards</td><td>20%</td><td class="mono">20,000,000,000</td></tr>
          <tr><td><span class="cat-dot" style="background:#a855f7"></span>Treasury</td><td>15%</td><td class="mono">15,000,000,000</td></tr>
          <tr><td><span class="cat-dot" style="background:#627eea"></span>Development</td><td>10%</td><td class="mono">10,000,000,000</td></tr>
          <tr><td><span class="cat-dot" style="background:#fbbf24"></span>Liquidity</td><td>10%</td><td class="mono">10,000,000,000</td></tr>
          <tr><td><span class="cat-dot" style="background:#4ade80"></span>Community</td><td>5%</td><td class="mono">5,000,000,000</td></tr>
          <tr><td><span class="cat-dot" style="background:#3b82f6"></span>Seed / Strategic</td><td>3%</td><td class="mono">3,000,000,000</td></tr>
          <tr><td><span class="cat-dot" style="background:#ec4899"></span>Public Presale</td><td>2%</td><td class="mono">2,000,000,000</td></tr>
          <tr><td><span class="cat-dot" style="background:#f97316"></span>Team &amp; Advisors</td><td>5%</td><td class="mono">5,000,000,000</td></tr>"""

tokenomics = tokenomics.replace(old_table, new_table)

# 7. Category breakdown - replace 6 cards with 9 cards
old_cats = re.search(r'<!-- CATEGORY BREAKDOWN -->.*?<!-- VESTING SCHEDULE -->', tokenomics, re.DOTALL)
if old_cats:
    new_cats = """<!-- CATEGORY BREAKDOWN -->
<div class="section">
  <span class="section-eyebrow">Category Breakdown</span>
  <h2 class="section-title">Detailed Category Analysis</h2>
  <p class="section-sub">Each allocation serves a specific purpose in the Verdis ecosystem. Built for long-term utility, security, and sustainability.</p>

  <div class="cat-card">
    <div class="cat-header"><div class="cat-title">1. Ecosystem &amp; Developer Grants</div><div class="cat-pct">25% (25B VRDX)</div></div>
    <div class="cat-body"><strong>Purpose:</strong> Developer grants, AI developers, plugin developers, dApps, smart contracts, research, education, hackathons, partnerships.<br><strong>Distribution:</strong> 4% (1B) at TGE for initial grants. Remaining 24B linear over 10 years. Governance-controlled with milestone-based releases.<br><strong>Economic Reasoning:</strong> Largest allocation ensures 10+ years of ecosystem funding for thousands of projects.</div>
    <div class="cat-grid"><div><strong>Vesting</strong>4% TGE + 10yr linear</div><div><strong>Governance</strong>Milestone-based</div></div>
  </div>

  <div class="cat-card">
    <div class="cat-header"><div class="cat-title">2. PoS Staking Rewards</div><div class="cat-pct">20% (20B VRDX)</div></div>
    <div class="cat-body"><strong>Purpose:</strong> Rewards for DPoS validators, delegators, and network security participants.<br><strong>Distribution:</strong> 2.5% (0.5B) at TGE. 2B/year emission for 10 years. Distributed per epoch via Substrate runtime.<br><strong>Economic Reasoning:</strong> Sustains network cryptoeconomic security for a decade. Target APR: 5-6.67% at 30-40% staking ratio.</div>
    <div class="cat-grid"><div><strong>Vesting</strong>2.5% TGE + 10yr emission</div><div><strong>Governance</strong>Validator rewards</div></div>
  </div>

  <div class="cat-card">
    <div class="cat-header"><div class="cat-title">3. Treasury</div><div class="cat-pct">15% (15B VRDX)</div></div>
    <div class="cat-body"><strong>Purpose:</strong> Infrastructure, security, ecosystem expansion, research, strategic development, emergency reserves.<br><strong>Distribution:</strong> 3.33% (0.5B) at TGE. Multisig (5-of-7). Max 10% spending/month. Public dashboard with audit logs.<br><strong>Economic Reasoning:</strong> Long-term capital runway with full transparency. Community controls allocation through governance.</div>
    <div class="cat-grid"><div><strong>Vesting</strong>3.33% TGE + 10yr governance</div><div><strong>Governance</strong>Multisig 5-of-7</div></div>
  </div>

  <div class="cat-card">
    <div class="cat-header"><div class="cat-title">4. Development</div><div class="cat-pct">10% (10B VRDX)</div></div>
    <div class="cat-body"><strong>Purpose:</strong> EvolvixOS, Verdis blockchain, AI infrastructure, SDK, developer tools, cloud infrastructure, security research.<br><strong>Distribution:</strong> 5% (0.5B) at TGE. 6-month cliff + 42-month linear vesting.<br><strong>Economic Reasoning:</strong> Ensures continuous development of core platform over 4+ years.</div>
    <div class="cat-grid"><div><strong>Vesting</strong>5% TGE + 6mo cliff + 42mo</div><div><strong>Governance</strong>Core development</div></div>
  </div>

  <div class="cat-card">
    <div class="cat-header"><div class="cat-title">5. Liquidity</div><div class="cat-pct">10% (10B VRDX)</div></div>
    <div class="cat-body"><strong>Purpose:</strong> DEX liquidity pools (VRDX/USDC, VRDX/ETH), CEX market making, managed liquidity reserve.<br><strong>Distribution:</strong> 40% (4B) at TGE for DEX pools. 2B for CEX partnerships. 4B managed reserve over 5 years.<br><strong>Economic Reasoning:</strong> NOT all deployed at once. Initial 4B ensures adequate market depth (40% of circulating supply).</div>
    <div class="cat-grid"><div><strong>Vesting</strong>40% TGE + 5yr managed</div><div><strong>Governance</strong>Reserve policy</div></div>
  </div>

  <div class="cat-card">
    <div class="cat-header"><div class="cat-title">6. Community</div><div class="cat-pct">5% (5B VRDX)</div></div>
    <div class="cat-body"><strong>Purpose:</strong> Contributors, bug bounty, education, hackathons, ecosystem participation, developer initiatives.<br><strong>Distribution:</strong> 20% (1B) at TGE. 3-month cliff + 15-month linear. Anti-sybil: KYC verification, 1 allocation per identity.<br><strong>Economic Reasoning:</strong> Controlled distribution prevents abuse while incentivizing genuine community contribution.</div>
    <div class="cat-grid"><div><strong>Vesting</strong>20% TGE + 3mo cliff + 15mo</div><div><strong>Governance</strong>Contribution-based</div></div>
  </div>

  <div class="cat-card">
    <div class="cat-header"><div class="cat-title">7. Seed / Strategic</div><div class="cat-pct">3% (3B VRDX)</div></div>
    <div class="cat-body"><strong>Purpose:</strong> Strategic investors with long vesting — minimal dilution, maximum strategic value.<br><strong>Distribution:</strong> $0.0015/VRDX. $4.5M raised. 12-month cliff + 24-month linear (36 months total). 0% TGE unlock.<br><strong>Economic Reasoning:</strong> 70% discount to TGE justified by 3-year vesting commitment. 125M/month unlock post-cliff (1.56% of circulating).</div>
    <div class="cat-grid"><div><strong>Vesting</strong>0% TGE + 12mo cliff + 24mo</div><div><strong>Governance</strong>Standard voting</div></div>
  </div>

  <div class="cat-card">
    <div class="cat-header"><div class="cat-title">8. Public Presale</div><div class="cat-pct">2% (2B VRDX)</div></div>
    <div class="cat-body"><strong>Purpose:</strong> Public community allocation with purchase limits to prevent concentration.<br><strong>Distribution:</strong> $0.004/VRDX. $8M raised. 25% (0.5B) at TGE + 6-month linear. Min $100, max $25,000. KYC + whitelist required.<br><strong>Economic Reasoning:</strong> 20% discount to TGE. Anti-concentration: max 0.1% of presale per wallet, 1 allocation per identity.</div>
    <div class="cat-grid"><div><strong>Vesting</strong>25% TGE + 6mo linear</div><div><strong>Governance</strong>Standard voting</div></div>
  </div>

  <div class="cat-card">
    <div class="cat-header"><div class="cat-title">9. Team &amp; Advisors</div><div class="cat-pct">5% (5B VRDX)</div></div>
    <div class="cat-body"><strong>Purpose:</strong> Aligns founding engineers, developers, advisors, and contributors with long-term network success.<br><strong>Distribution:</strong> 12-month cliff, then linear monthly vesting over 36 months (48 months total). 0% TGE unlock.<br><strong>Economic Reasoning:</strong> Extended 4-year lockup prevents founder dump risk and ensures long-term commitment.</div>
    <div class="cat-grid"><div><strong>Vesting</strong>0% TGE + 12mo cliff + 36mo</div><div><strong>Governance</strong>Standard voting</div></div>
  </div>
</div>

<!-- VESTING SCHEDULE -->"""
    tokenomics = tokenomics[:old_cats.start()] + new_cats + tokenomics[old_cats.end():]

# 8. Vesting schedule table
old_vesting = re.search(r'<div class="vesting-table-wrap">.*?</table></div>', tokenomics, re.DOTALL)
if old_vesting:
    new_vesting = """<div class="vesting-table-wrap"><div style="overflow-x:auto;width:100%"><table class="vesting-table">
    <thead>
      <tr><th>Category</th><th>TGE Unlock</th><th>Cliff</th><th>Vesting Period</th><th>Monthly Release</th><th>Status</th></tr>
    </thead>
    <tbody>
      <tr><td><strong>Seed / Strategic</strong></td><td>0%</td><td>12 months</td><td>36 months</td><td class="mono">125M / month</td><td><span class="badge badge-info">Round Active</span></td></tr>
      <tr><td><strong>Community</strong></td><td>20% (1B)</td><td>3 months</td><td>18 months</td><td class="mono">300M / month</td><td><span class="badge badge-locked">Upcoming</span></td></tr>
      <tr><td><strong>Public Presale</strong></td><td>25% (0.5B)</td><td>None</td><td>6 months</td><td class="mono">250M / month</td><td><span class="badge badge-locked">Upcoming</span></td></tr>
      <tr><td><strong>IDO / TGE</strong></td><td>100%</td><td>None</td><td>Liquid</td><td class="mono">At TGE</td><td><span class="badge badge-locked">Upcoming</span></td></tr>
      <tr><td><strong>Team &amp; Advisors</strong></td><td>0%</td><td>12 months</td><td>48 months</td><td class="mono">138.9M / month</td><td><span class="badge badge-locked">Locked</span></td></tr>
      <tr><td><strong>Ecosystem Grants</strong></td><td>4% (1B)</td><td>None</td><td>120 months</td><td class="mono">200M / month</td><td><span class="badge badge-success">Active</span></td></tr>
      <tr><td><strong>PoS Staking</strong></td><td>2.5% (0.5B)</td><td>None</td><td>120 months</td><td class="mono">162.5M / month</td><td><span class="badge badge-success">Active</span></td></tr>
      <tr><td><strong>Treasury</strong></td><td>3.33% (0.5B)</td><td>None</td><td>120 months</td><td class="mono">120M / month</td><td><span class="badge badge-locked">Governance</span></td></tr>
      <tr><td><strong>Development</strong></td><td>5% (0.5B)</td><td>6 months</td><td>48 months</td><td class="mono">223.8M / month</td><td><span class="badge badge-locked">Locked</span></td></tr>
      <tr><td><strong>Liquidity</strong></td><td>40% (4B)</td><td>None</td><td>60 months</td><td class="mono">120M / month</td><td><span class="badge badge-warning">At Launch</span></td></tr>
    </tbody>
  </table></div>"""
    tokenomics = tokenomics[:old_vesting.start()] + new_vesting + tokenomics[old_vesting.end():]

# 9. Investor allocation section - replace 4 IDO phases with new 4 rounds
old_investor = re.search(r'<!-- INVESTOR ALLOCATION -->.*?</div>\s*</div>\s*<!-- FOOTER -->', tokenomics, re.DOTALL)
if old_investor:
    new_investor = """<!-- INVESTOR ALLOCATION -->
<div class="section">
  <span class="section-eyebrow">Fundraising</span>
  <h2 class="section-title">Fundraising Rounds</h2>
  <p class="section-sub">6.5B VRDX allocated across 4 rounds: Seed, Community, Public Presale, and TGE/IDO. Total raised: $18,000,000. FDV at TGE: $500,000,000.</p>
  <div id="ido-grid">
    <div class="cat-card" style="border-color:var(--accent);box-shadow:0 0 24px var(--accent-glow)">
      <div class="cat-header"><div class="cat-title">Round 1 — Seed / Strategic</div><span class="badge badge-info">Active</span></div>
      <div class="cat-pct" style="margin:8px 0">$0.0015 / VRDX</div>
      <div class="cat-body" style="font-size:12px">3B VRDX allocation. Capital raised: $4.5M. FDV: $150M. 70% discount to TGE. 12-month cliff + 24-month linear vesting. 0% TGE unlock.</div>
      <div class="cat-grid"><div><strong>Allocation</strong>3B VRDX</div><div><strong>Capital</strong>$4.5M</div></div>
    </div>
    <div class="cat-card">
      <div class="cat-header"><div class="cat-title">Round 2 — Community</div><span class="badge badge-locked">Upcoming</span></div>
      <div class="cat-pct" style="margin:8px 0">$0.003 / VRDX</div>
      <div class="cat-body" style="font-size:12px">1B VRDX allocation. Capital raised: $3M. FDV: $300M. 40% discount to TGE. 20% TGE unlock + 3-month cliff + 15-month linear.</div>
      <div class="cat-grid"><div><strong>Allocation</strong>1B VRDX</div><div><strong>Capital</strong>$3M</div></div>
    </div>
    <div class="cat-card">
      <div class="cat-header"><div class="cat-title">Round 3 — Public Presale</div><span class="badge badge-locked">Upcoming</span></div>
      <div class="cat-pct" style="margin:8px 0">$0.004 / VRDX</div>
      <div class="cat-body" style="font-size:12px">2B VRDX allocation. Capital raised: $8M. FDV: $400M. 20% discount to TGE. 25% TGE unlock + 6-month linear. Min $100, max $25,000. KYC + whitelist.</div>
      <div class="cat-grid"><div><strong>Allocation</strong>2B VRDX</div><div><strong>Capital</strong>$8M</div></div>
    </div>
    <div class="cat-card">
      <div class="cat-header"><div class="cat-title">Round 4 — TGE / IDO</div><span class="badge badge-locked">Upcoming</span></div>
      <div class="cat-pct" style="margin:8px 0">$0.005 / VRDX</div>
      <div class="cat-body" style="font-size:12px">0.5B VRDX allocation. Capital raised: $2.5M. FDV: $500M. 0% discount. 100% liquid at TGE. Initial market cap: $40M (8B circulating).</div>
      <div class="cat-grid"><div><strong>Allocation</strong>0.5B VRDX</div><div><strong>Capital</strong>$2.5M</div></div>
    </div>
  </div>
</div>

<!-- UNLOCK SCHEDULE -->
<div class="section">
  <span class="section-eyebrow">10-Year Projection</span>
  <h2 class="section-title">Circulating Supply Unlock Schedule</h2>
  <p class="section-sub">Month-by-month cumulative circulating supply over 10 years. Targets ensure controlled release without excessive sell pressure.</p>
  <div style="overflow-x:auto;width:100%"><table class="dist-table">
    <thead><tr><th>Year</th><th>Cumulative Supply</th><th>% of Max</th><th>Target</th></tr></thead>
    <tbody>
      <tr><td>TGE (Year 0)</td><td class="mono">8,000,000,000</td><td class="mono">8.0%</td><td>8B</td></tr>
      <tr><td>Year 1</td><td class="mono">20,260,000,000</td><td class="mono">20.3%</td><td>18B</td></tr>
      <tr><td>Year 2</td><td class="mono">34,740,000,000</td><td class="mono">34.7%</td><td>29B</td></tr>
      <tr><td>Year 3</td><td class="mono">47,620,000,000</td><td class="mono">47.6%</td><td>40B</td></tr>
      <tr><td>Year 5</td><td class="mono">66,000,000,000</td><td class="mono">66.0%</td><td>62B</td></tr>
      <tr><td>Year 7</td><td class="mono">77,600,000,000</td><td class="mono">77.6%</td><td>81B</td></tr>
      <tr><td>Year 10</td><td class="mono">95,000,000,000</td><td class="mono">95.0%</td><td>100B</td></tr>
    </tbody>
  </table></div>
</div>

<!-- STAKING ECONOMICS -->
<div class="section">
  <span class="section-eyebrow">Staking</span>
  <h2 class="section-title">PoS Staking Economics</h2>
  <p class="section-sub">20B VERDIS staking pool with 10-year emission at 2B/year. Target staking ratio: 30-40% (5-6.67% APR).</p>
  <div style="overflow-x:auto;width:100%"><table class="dist-table">
    <thead><tr><th>Staking Ratio</th><th>APR</th><th>Inflation (Y1)</th><th>Assessment</th></tr></thead>
    <tbody>
      <tr><td class="mono">10%</td><td class="mono">20.00%</td><td class="mono">25.0%</td><td>High incentive, low security</td></tr>
      <tr><td class="mono">20%</td><td class="mono">10.00%</td><td class="mono">25.0%</td><td>Adequate</td></tr>
      <tr style="background:var(--accent-glow)"><td class="mono"><strong>30%</strong></td><td class="mono"><strong>6.67%</strong></td><td class="mono"><strong>25.0%</strong></td><td><strong>Target — optimal balance</strong></td></tr>
      <tr style="background:var(--accent-glow)"><td class="mono"><strong>40%</strong></td><td class="mono"><strong>5.00%</strong></td><td class="mono"><strong>25.0%</strong></td><td><strong>Target — optimal balance</strong></td></tr>
      <tr><td class="mono">50%</td><td class="mono">4.00%</td><td class="mono">25.0%</td><td>Good security, less liquidity</td></tr>
      <tr><td class="mono">60%</td><td class="mono">3.33%</td><td class="mono">25.0%</td><td>High security, liquidity concern</td></tr>
      <tr><td class="mono">80%</td><td class="mono">2.50%</td><td class="mono">25.0%</td><td>Low liquidity risk</td></tr>
    </tbody>
  </table></div>
</div>

<!-- FOOTER -->"""
    tokenomics = tokenomics[:old_investor.start()] + new_investor + tokenomics[old_investor.end():]

# 10. Chart data - update from 6 to 9 categories
old_chart = """labels: [
                'Community Rewards (25%)',
                'Eco Fund (18%)',
                'Team & Advisors (15%)',
                'DEX Liquidity (15%)',
                'Treasury Reserve (15%)',
                'Investors / IDO (12%)'
            ],
            datasets: [{
                data: [25, 18, 15, 15, 15, 12],
                backgroundColor: [
                    '#16a34a',
                    '#26a17b',
                    '#627eea',
                    '#fbbf24',
                    '#a855f7',
                    '#4ade80'
                ],"""

new_chart = """labels: [
                'Ecosystem & Grants (25%)',
                'PoS Staking (20%)',
                'Treasury (15%)',
                'Development (10%)',
                'Liquidity (10%)',
                'Community (5%)',
                'Seed / Strategic (3%)',
                'Public Presale (2%)',
                'Team & Advisors (5%)'
            ],
            datasets: [{
                data: [25, 20, 15, 10, 10, 5, 3, 2, 5],
                backgroundColor: [
                    '#16a34a',
                    '#26a17b',
                    '#a855f7',
                    '#627eea',
                    '#fbbf24',
                    '#4ade80',
                    '#3b82f6',
                    '#ec4899',
                    '#f97316'
                ],"""

tokenomics = tokenomics.replace(old_chart, new_chart)

# Save updated tokenomics
with open('/opt/verdis-repo/dist/web/tokenomics/index.html', 'w') as f:
    f.write(tokenomics)
print("Tokenomics page updated")

# ============================================================================
# WHITEPAPER PAGE UPDATES
# ============================================================================
with open('/opt/verdis-repo/dist/web/whitepaper/index.html', 'r') as f:
    whitepaper = f.read()

# Update distribution items (6 → 9)
old_dist = re.search(r'<div class="dist-list">.*?</div>\s*</div></div>\s*</section>', whitepaper, re.DOTALL)
if old_dist:
    new_dist = """<div class="dist-list">
<div class="dist-item active"><div class="dist-left"><div class="dist-dot" style="background:#00a86b"></div><div><div class="dist-name">Ecosystem &amp; Developer Grants</div><div class="dist-desc">Developer grants, AI, dApps, research, hackathons</div></div></div><div class="dist-right"><div class="dist-pct">25%</div><div class="dist-amt">25,000,000,000 VRDX</div></div></div>
<div class="dist-item"><div class="dist-left"><div class="dist-dot" style="background:#26a17b"></div><div><div class="dist-name">PoS Staking Rewards</div><div class="dist-desc">10-year validator &amp; delegator rewards (2B/yr)</div></div></div><div class="dist-right"><div class="dist-pct">20%</div><div class="dist-amt">20,000,000,000 VRDX</div></div></div>
<div class="dist-item"><div class="dist-left"><div class="dist-dot" style="background:#a855f7"></div><div><div class="dist-name">Treasury</div><div class="dist-desc">Multisig 5-of-7, governance-controlled reserve</div></div></div><div class="dist-right"><div class="dist-pct">15%</div><div class="dist-amt">15,000,000,000 VRDX</div></div></div>
<div class="dist-item"><div class="dist-left"><div class="dist-dot" style="background:#627eea"></div><div><div class="dist-name">Development</div><div class="dist-desc">EvolvixOS, Verdis, AI infrastructure, SDK</div></div></div><div class="dist-right"><div class="dist-pct">10%</div><div class="dist-amt">10,000,000,000 VRDX</div></div></div>
<div class="dist-item"><div class="dist-left"><div class="dist-dot" style="background:#fbbf24"></div><div><div class="dist-name">Liquidity</div><div class="dist-desc">DEX pools, CEX market making, managed reserve</div></div></div><div class="dist-right"><div class="dist-pct">10%</div><div class="dist-amt">10,000,000,000 VRDX</div></div></div>
<div class="dist-item"><div class="dist-left"><div class="dist-dot" style="background:#4ade80"></div><div><div class="dist-name">Community</div><div class="dist-desc">Contributors, bug bounty, education, hackathons</div></div></div><div class="dist-right"><div class="dist-pct">5%</div><div class="dist-amt">5,000,000,000 VRDX</div></div></div>
<div class="dist-item"><div class="dist-left"><div class="dist-dot" style="background:#3b82f6"></div><div><div class="dist-name">Seed / Strategic</div><div class="dist-desc">$0.0015/VRDX, $4.5M raised, 70% discount</div></div></div><div class="dist-right"><div class="dist-pct">3%</div><div class="dist-amt">3,000,000,000 VRDX</div></div></div>
<div class="dist-item"><div class="dist-left"><div class="dist-dot" style="background:#ec4899"></div><div><div class="dist-name">Public Presale</div><div class="dist-desc">$0.004/VRDX, $8M raised, 20% discount</div></div></div><div class="dist-right"><div class="dist-pct">2%</div><div class="dist-amt">2,000,000,000 VRDX</div></div></div>
<div class="dist-item"><div class="dist-left"><div class="dist-dot" style="background:#f97316"></div><div><div class="dist-name">Team &amp; Advisors</div><div class="dist-desc">12-month cliff, 36-month linear vesting</div></div></div><div class="dist-right"><div class="dist-pct">5%</div><div class="dist-amt">5,000,000,000 VRDX</div></div></div>
</div></div></div>
</section>"""
    whitepaper = whitepaper[:old_dist.start()] + new_dist + whitepaper[old_dist.end():]

# Update SVG pie chart segments for 9 categories
old_svg = re.search(r'<svg class="pie-svg".*?</svg>', whitepaper, re.DOTALL)
if old_svg:
    # 9 segments: 25%, 20%, 15%, 10%, 10%, 5%, 3%, 2%, 5%
    # Circumference = 2 * pi * 38 = 238.76
    # Each percentage = 2.3876 per 1%
    import math
    circ = 2 * math.pi * 38
    segments = [
        (25, '#00a86b'), (20, '#26a17b'), (15, '#a855f7'), (10, '#627eea'),
        (10, '#fbbf24'), (5, '#4ade80'), (3, '#3b82f6'), (2, '#ec4899'), (5, '#f97316')
    ]
    offset = 0
    circles = '<svg class="pie-svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="38" fill="none" stroke="#222" stroke-width="16"/>'
    for pct, color in segments:
        dash = pct * circ / 100
        gap = circ - dash
        circles += f'<circle class="pie-seg" cx="50" cy="50" r="38" fill="none" stroke="{color}" stroke-width="16" stroke-dasharray="{dash:.2f} {gap:.2f}" stroke-dashoffset="{-offset:.2f}"/>'
        offset += dash
    circles += '</svg>'
    whitepaper = whitepaper[:old_svg.start()] + circles + whitepaper[old_svg.end():]

# Update vesting section
old_vesting_wp = re.search(r'<section id="vesting".*?</section>', whitepaper, re.DOTALL)
if old_vesting_wp:
    new_vesting_wp = """<section id="vesting" class="section-block reveal">
<div class="section-header"><span class="section-tag">Release Terms</span><h2 class="section-title">3. Vesting Schedule</h2><p class="section-desc">Structured release terms enforcing long-term alignment across team, investors, and ecosystem participants. Total raised: $18M across 4 rounds.</p></div>
<div class="vesting-grid">
<div class="vest-card"><div class="vest-header"><span class="vest-title">Seed / Strategic (3B)</span><span class="vest-badge">$4.5M raised</span></div><div class="vest-cliff">12-Month Cliff (0% unlocked at TGE)</div><div class="vest-details">$0.0015/VRDX. 70% discount to TGE. After month 12, linear release of <span class="mono">125M VRDX / month</span> over 24 months (3 years total).</div><div class="vest-bar"><div class="vest-fill" style="width:25%"></div></div><span class="mono" style="font-size:11px;color:var(--text-3)">Cliff status: Active vesting</span></div>
<div class="vest-card"><div class="vest-header"><span class="vest-title">Community + Presale (3B)</span><span class="vest-badge">$11M raised</span></div><div class="vest-cliff">Phased Cliff (10-25% TGE)</div><div class="vest-details">Community: $0.003/VRDX, 20% TGE, 3mo cliff, 15mo linear. Presale: $0.004/VRDX, 25% TGE, 6mo linear. Min $100, max $25,000. KYC + whitelist.</div><div class="vest-bar"><div class="vest-fill" style="width:15%"></div></div><span class="mono" style="font-size:11px;color:var(--text-3)">Cliff status: Upcoming</span></div>
<div class="vest-card"><div class="vest-header"><span class="vest-title">Team &amp; Advisors (5B)</span><span class="vest-badge">0% TGE</span></div><div class="vest-cliff">12-Month Cliff (0% unlocked)</div><div class="vest-details">100% locked for first 12 months. After month 12, linear release of <span class="mono">138.9M VRDX / month</span> over 36 months (4 years total).</div><div class="vest-bar"><div class="vest-fill" style="width:25%"></div></div><span class="mono" style="font-size:11px;color:var(--text-3)">Cliff status: Locked</span></div>
<div class="vest-card"><div class="vest-header"><span class="vest-title">Ecosystem + Staking (45B)</span><span class="vest-badge">10-year release</span></div><div class="vest-cliff" style="background:rgba(74,222,128,0.1);color:var(--success);border-color:rgba(74,222,128,0.2)">Linear Release</div><div class="vest-details">Ecosystem Grants (25B): 4% TGE + 10yr linear. PoS Staking (20B): 2.5% TGE + 2B/yr emission for 10 years. Governance-controlled.</div><div class="vest-bar"><div class="vest-fill" style="width:30%"></div></div><span class="mono" style="font-size:11px;color:var(--text-3)">Distribution: Grants + staking rewards</span></div>
</div>
</section>"""
    whitepaper = whitepaper[:old_vesting_wp.start()] + new_vesting_wp + whitepaper[old_vesting_wp.end():]

# Save updated whitepaper
with open('/opt/verdis-repo/dist/web/whitepaper/index.html', 'w') as f:
    f.write(whitepaper)
print("Whitepaper page updated")

print("\nBoth pages updated successfully!")
