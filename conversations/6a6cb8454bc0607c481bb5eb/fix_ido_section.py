#!/usr/bin/env python3
"""Fix tokenomics page: replace old IDO DETAILS section with new fundraising rounds."""

with open('/opt/verdis-repo/dist/web/tokenomics/index.html', 'r') as f:
    content = f.read()

# Find and replace the old IDO DETAILS section
import re

old_section = re.search(r'<!-- IDO DETAILS -->.*?<!-- FOOTER -->', content, re.DOTALL)
if old_section:
    new_section = """<!-- FUNDRAISING ROUNDS -->
<div class="section">
  <span class="section-eyebrow">Fundraising</span>
  <h2 class="section-title">Fundraising Rounds</h2>
  <p class="section-sub">6.5B VERDIS allocated across 4 rounds: Seed, Community, Public Presale, and TGE/IDO. Total raised: $18,000,000. FDV at TGE: $500,000,000.</p>
  <div id="ido-grid">
    <div class="cat-card" style="border-color:var(--accent);box-shadow:0 0 24px var(--accent-glow)">
      <div class="cat-header">
        <div class="cat-title">Round 1 — Seed / Strategic</div>
        <span class="badge badge-info">Active</span>
      </div>
      <div class="cat-pct" style="margin:8px 0">$0.0015 / VRDX</div>
      <div class="cat-body" style="font-size:12px">3B VRDX. $4.5M raised. FDV: $150M. 70% discount to TGE. 12-month cliff + 24-month linear. 0% TGE unlock.</div>
      <div class="cat-grid">
        <div><strong>Allocation</strong>3B VRDX</div>
        <div><strong>Capital</strong>$4.5M</div>
      </div>
    </div>
    <div class="cat-card">
      <div class="cat-header">
        <div class="cat-title">Round 2 — Community</div>
        <span class="badge badge-locked">Upcoming</span>
      </div>
      <div class="cat-pct" style="margin:8px 0">$0.003 / VRDX</div>
      <div class="cat-body" style="font-size:12px">1B VRDX. $3M raised. FDV: $300M. 40% discount. 20% TGE unlock + 3-month cliff + 15-month linear. KYC required.</div>
      <div class="cat-grid">
        <div><strong>Allocation</strong>1B VRDX</div>
        <div><strong>Capital</strong>$3M</div>
      </div>
    </div>
    <div class="cat-card">
      <div class="cat-header">
        <div class="cat-title">Round 3 — Public Presale</div>
        <span class="badge badge-locked">Upcoming</span>
      </div>
      <div class="cat-pct" style="margin:8px 0">$0.004 / VRDX</div>
      <div class="cat-body" style="font-size:12px">2B VRDX. $8M raised. FDV: $400M. 20% discount. 25% TGE + 6-month linear. Min $100, max $25,000. KYC + whitelist.</div>
      <div class="cat-grid">
        <div><strong>Allocation</strong>2B VRDX</div>
        <div><strong>Capital</strong>$8M</div>
      </div>
    </div>
    <div class="cat-card">
      <div class="cat-header">
        <div class="cat-title">Round 4 — TGE / IDO</div>
        <span class="badge badge-locked">Upcoming</span>
      </div>
      <div class="cat-pct" style="margin:8px 0">$0.005 / VRDX</div>
      <div class="cat-body" style="font-size:12px">0.5B VRDX. $2.5M raised. FDV: $500M. 0% discount. 100% liquid at TGE. Initial MCap: $40M (8B circulating).</div>
      <div class="cat-grid">
        <div><strong>Allocation</strong>0.5B VRDX</div>
        <div><strong>Capital</strong>$2.5M</div>
      </div>
    </div>
  </div>
</div>

<!-- UNLOCK SCHEDULE -->
<div class="section">
  <span class="section-eyebrow">10-Year Projection</span>
  <h2 class="section-title">Circulating Supply Unlock Schedule</h2>
  <p class="section-sub">Cumulative circulating supply over 10 years. Controlled release ensures manageable sell pressure.</p>
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
    content = content[:old_section.start()] + new_section + content[old_section.end():]
    print("IDO DETAILS section replaced with new fundraising rounds!")
else:
    print("ERROR: Could not find IDO DETAILS section!")

with open('/opt/verdis-repo/dist/web/tokenomics/index.html', 'w') as f:
    f.write(content)
