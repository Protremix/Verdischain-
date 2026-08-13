#!/usr/bin/env python3
"""
Regenerate the branded PDF whitepaper to include the new TGE vesting roadmap section.
"""
import os, base64
from weasyprint import HTML

LOGO_WHITE = '/var/www/verdiscan/assets/verdis-logo-white.png'
LOGO_BLACK = '/var/www/verdiscan/assets/verdis-logo-black.png'
OUTPUT_PDF = '/var/www/verdiscan/whitepaper/verdis-whitepaper.pdf'
OUTPUT_PDF_REPO = '/opt/verdis-chain-rust/web/whitepaper/verdis-whitepaper.pdf'

def img_b64(path):
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode()

logo_white_b64 = img_b64(LOGO_WHITE)
logo_black_b64 = img_b64(LOGO_BLACK)

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
@page {{ size: A4; margin: 0; @bottom-center {{ content: "Verdis Chain Whitepaper v2.0  |  Page " counter(page) " of " counter(pages); font-family: 'Inter', sans-serif; font-size: 9px; color: #64748b; margin-bottom: 16px; }} }}
@page :first {{ margin: 0; @bottom-center {{ content: ""; }} }}
@page cover {{ margin: 0; @bottom-center {{ content: ""; }} }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: 'Inter', 'Helvetica Neue', sans-serif; color: #1e293b; font-size: 11px; line-height: 1.7; background: #fff; }}

/* COVER */
.cover {{ page: cover; width: 210mm; height: 297mm; background: linear-gradient(135deg, #040806 0%, #0a1f0e 50%, #04150a 100%); display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 40mm 30mm; position: relative; page-break-after: always; color: #fff; }}
.cover::before {{ content: ''; position: absolute; top: -20%; right: -15%; width: 600px; height: 600px; background: radial-gradient(circle, rgba(22,163,74,0.15), transparent 55%); border-radius: 50%; }}
.cover-logo {{ width: 180px; margin-bottom: 24px; }}
.cover-badge {{ display: inline-block; padding: 6px 16px; border: 1px solid #16a34a; border-radius: 100px; font-size: 11px; font-weight: 600; color: #16a34a; margin-bottom: 20px; letter-spacing: 0.5px; }}
.cover-title {{ font-family: 'Space Grotesk', 'Helvetica', sans-serif; font-size: 42px; font-weight: 700; color: #fff; margin-bottom: 12px; text-align: center; letter-spacing: -1px; }}
.cover-title .accent {{ color: #16a34a; }}
.cover-subtitle {{ font-size: 14px; color: #94a3b8; text-align: center; max-width: 400px; line-height: 1.6; margin-bottom: 32px; }}
.cover-stats {{ display: flex; gap: 32px; justify-content: center; margin-bottom: 32px; }}
.cover-stat {{ text-align: center; }}
.cover-stat .val {{ font-family: 'JetBrains Mono', monospace; font-size: 20px; font-weight: 700; color: #16a34a; }}
.cover-stat .lbl {{ font-size: 10px; color: #64748b; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }}
.cover-footer {{ position: absolute; bottom: 30mm; text-align: center; font-size: 11px; color: #475569; width: 100%; }}
.cover-footer strong {{ color: #94a3b8; }}

/* CONTENT */
.content {{ padding: 20mm 25mm; page-break-inside: auto; }}
.content h1 {{ font-family: 'Space Grotesk', 'Helvetica', sans-serif; font-size: 20px; font-weight: 700; color: #0f172a; margin-bottom: 8px; margin-top: 0; padding-bottom: 8px; border-bottom: 2px solid #16a34a; display: inline-block; }}
.content h1.section-num {{ color: #16a34a; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px; border: none; display: block; padding: 0; }}
.content h2 {{ font-family: 'Space Grotesk', sans-serif; font-size: 14px; font-weight: 700; color: #0f172a; margin-top: 16px; margin-bottom: 8px; }}
.content h3 {{ font-family: 'Space Grotesk', sans-serif; font-size: 12px; font-weight: 600; color: #15803d; margin-top: 12px; margin-bottom: 6px; }}
.content p {{ font-size: 11px; color: #334155; line-height: 1.7; margin-bottom: 8px; text-align: justify; }}
.content strong {{ color: #0f172a; }}
.content .mono {{ font-family: 'JetBrains Mono', 'Courier New', monospace; font-size: 10px; background: #f1f5f9; padding: 1px 6px; border-radius: 4px; color: #15803d; }}
.content ul {{ margin-left: 16px; margin-bottom: 8px; }}
.content li {{ font-size: 11px; color: #334155; line-height: 1.7; margin-bottom: 4px; }}

table {{ width: 100%; border-collapse: collapse; margin-bottom: 12px; font-size: 10px; }}
th {{ text-align: left; padding: 8px 12px; background: #f8fafc; border-bottom: 2px solid #16a34a; font-size: 9px; text-transform: uppercase; letter-spacing: 0.5px; color: #64748b; font-weight: 600; }}
td {{ padding: 8px 12px; border-bottom: 1px solid #e2e8f0; color: #334155; }}
tr:last-child td {{ border-bottom: none; }}
.unlocked {{ color: #16a34a; font-weight: 600; }}
.partial {{ color: #d97706; font-weight: 600; }}
.locked {{ color: #ef4444; font-weight: 600; }}

.card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-left: 3px solid #16a34a; border-radius: 8px; padding: 12px 16px; margin-bottom: 8px; }}
.card h3 {{ margin-top: 0; }}
.card.warn {{ border-left-color: #f59e0b; }}
.card.success {{ border-left-color: #4ade80; }}

.metrics {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 12px; }}
.metric {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px; text-align: center; }}
.metric .val {{ font-family: 'JetBrains Mono', monospace; font-size: 13px; font-weight: 700; color: #16a34a; }}
.metric .lbl {{ font-size: 8px; text-transform: uppercase; letter-spacing: 0.5px; color: #64748b; margin-top: 2px; }}

.dist-row {{ display: flex; align-items: center; margin-bottom: 4px; font-size: 10px; }}
.dist-label {{ width: 120px; color: #334155; }}
.dist-bar {{ flex: 1; height: 16px; background: #f1f5f9; border-radius: 4px; overflow: hidden; margin: 0 8px; }}
.dist-fill {{ height: 100%; background: linear-gradient(90deg, #16a34a, #15803d); border-radius: 4px; }}
.dist-val {{ width: 50px; text-align: right; font-family: 'JetBrains Mono', monospace; color: #15803d; font-weight: 600; }}

.supply-row {{ display: flex; align-items: center; gap: 8px; margin-bottom: 4px; font-size: 10px; }}
.sr-when {{ width: 70px; font-weight: 600; color: #475569; }}
.sr-bar {{ flex: 1; height: 20px; background: #f1f5f9; border-radius: 4px; overflow: hidden; position: relative; }}
.sr-fill {{ height: 100%; background: linear-gradient(90deg, #16a34a, #22c55e); border-radius: 4px; }}
.sr-val {{ position: absolute; right: 6px; top: 50%; transform: translateY(-50%); font-family: 'JetBrains Mono'; font-size: 9px; font-weight: 700; color: #fff; }}
.sr-pct {{ width: 40px; text-align: right; font-family: 'JetBrains Mono'; font-size: 10px; font-weight: 600; color: #16a34a; }}

.page-break {{ page-break-before: always; }}
.page-header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #e2e8f0; padding-bottom: 8px; margin-bottom: 16px; }}
.page-header .logo {{ height: 24px; }}
.page-header .title {{ font-size: 9px; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; }}

.insight-box {{ background: rgba(22,163,74,0.08); border: 1px solid #16a34a; border-radius: 8px; padding: 12px 16px; margin: 12px 0; }}
.insight-box .it-title {{ font-size: 12px; font-weight: 700; color: #16a34a; margin-bottom: 4px; }}
.insight-box .it-body {{ font-size: 10px; color: #334155; line-height: 1.6; }}
</style>
</head>
<body>

<!-- COVER -->
<div class="cover">
  <img src="data:image/png;base64,{logo_white_b64}" alt="Verdis Chain" class="cover-logo">
  <div class="cover-badge">Whitepaper v2.0 &bull; Green Layer-1 Protocol</div>
  <h1 class="cover-title">VERDIS <span class="accent">CHAIN</span></h1>
  <p class="cover-subtitle">The world's first carbon-negative Layer-1 blockchain. Built with Substrate, powered by native DPoS consensus, AMM DEX, ink! smart contracts, and on-chain carbon credit tracking.</p>
  <div class="cover-stats">
    <div class="cover-stat"><div class="val">100B</div><div class="lbl">Total Supply</div></div>
    <div class="cover-stat"><div class="val">DPoS</div><div class="lbl">Consensus</div></div>
    <div class="cover-stat"><div class="val">30+</div><div class="lbl">Pallets</div></div>
    <div class="cover-stat"><div class="val">$500M</div><div class="lbl">FDV</div></div>
  </div>
  <div class="cover-footer"><strong>Verdis Chain</strong> &middot; Protremix &middot; Open-source under MIT License<br>verdischain.com &middot; August 2026</div>
</div>

<!-- TOC -->
<div class="content">
  <div class="page-header"><img src="data:image/png;base64,{logo_black_b64}" alt="Verdis" class="logo" style="height:24px"><span class="title">Whitepaper v2.0</span></div>
  <h1 class="section-num">Contents</h1><h1>Table of Contents</h1>
  <ul style="font-size:11px;line-height:2;color:#334155;list-style:none">
    <li><strong>1.</strong> Executive Summary</li>
    <li><strong>2.</strong> Problem Statement</li>
    <li><strong>3.</strong> Solution Overview</li>
    <li><strong>4.</strong> Technical Architecture</li>
    <li><strong>5.</strong> DPoS Consensus</li>
    <li><strong>6.</strong> AMM DEX</li>
    <li><strong>7.</strong> Carbon Credits &amp; Eco Layer</li>
    <li><strong>8.</strong> EvolvixOS Integration</li>
    <li><strong>9.</strong> Tokenomics &amp; Distribution</li>
    <li><strong>10.</strong> Vesting &amp; Cliff Roadmap (From TGE Day)</li>
    <li><strong>11.</strong> Fundraising &amp; Staking</li>
    <li><strong>12.</strong> Roadmap</li>
    <li><strong>13.</strong> Team</li>
    <li><strong>14.</strong> Conclusion</li>
  </ul>
</div>

<!-- 1. EXEC SUMMARY -->
<div class="content page-break">
  <div class="page-header"><img src="data:image/png;base64,{logo_black_b64}" alt="Verdis" class="logo" style="height:24px"><span class="title">Whitepaper v2.0</span></div>
  <h1 class="section-num">Section 1</h1><h1>Executive Summary</h1>
  <p>Verdis Chain is a carbon-negative Layer-1 blockchain built on Substrate, powered by native Delegated Proof-of-Stake (DPoS) consensus, an integrated AMM decentralized exchange (DEX), ink! smart contracts, and on-chain carbon credit tracking.</p>
  <p>The native token, <strong>VRDX</strong>, has a fixed supply of <strong>100 billion</strong> with <strong>9 decimals</strong>, serving as gas, staking asset, governance instrument, and medium of exchange.</p>
  <p>Verdis Chain connects to <strong>EvolvixOS</strong>, an AI Engineering Operating System providing smart contract auditing, AI-powered development tools, and a plugin marketplace.</p>
  <div class="metrics">
    <div class="metric"><div class="val">100B</div><div class="lbl">Total Supply</div></div>
    <div class="metric"><div class="val">6s</div><div class="lbl">Block Time</div></div>
    <div class="metric"><div class="val">21</div><div class="lbl">Validators</div></div>
    <div class="metric"><div class="val">6</div><div class="lbl">DEX Pools</div></div>
    <div class="metric"><div class="val">30+</div><div class="lbl">Pallets</div></div>
    <div class="metric"><div class="val">$500M</div><div class="lbl">FDV</div></div>
    <div class="metric"><div class="val">$18M</div><div class="lbl">Raised</div></div>
    <div class="metric"><div class="val">8B</div><div class="lbl">TGE Circ.</div></div>
  </div>
</div>

<!-- 2-3. PROBLEM + SOLUTION -->
<div class="content page-break">
  <div class="page-header"><img src="data:image/png;base64,{logo_black_b64}" alt="Verdis" class="logo" style="height:24px"><span class="title">Whitepaper v2.0</span></div>
  <h1 class="section-num">Section 2</h1><h1>Problem Statement</h1>
  <p>Traditional blockchains consume enormous energy. Carbon markets are fragmented. AI and blockchain operate in isolation. Verdis Chain addresses all three.</p>
  <h1 class="section-num" style="margin-top:16px">Section 3</h1><h1>Solution Overview</h1>
  <div class="card"><h3>Carbon-Negative Consensus</h3><p>DPoS uses 99.9% less energy than PoW. Green validator scoring rewards renewable energy.</p></div>
  <div class="card"><h3>On-Chain Carbon Credits</h3><p>Full transparency from source to retirement. No double-counting.</p></div>
  <div class="card"><h3>AI-Powered Security</h3><p>Every contract analyzed by EvolvixOS AI before deployment.</p></div>
  <div class="card"><h3>Native AMM DEX</h3><p>6 liquidity pools, overflow-protected arithmetic.</p></div>
</div>

<!-- 4. ARCHITECTURE -->
<div class="content page-break">
  <div class="page-header"><img src="data:image/png;base64,{logo_black_b64}" alt="Verdis" class="logo" style="height:24px"><span class="title">Whitepaper v2.0</span></div>
  <h1 class="section-num">Section 4</h1><h1>Technical Architecture</h1>
  <table>
    <thead><tr><th>Parameter</th><th>Value</th><th>Description</th></tr></thead>
    <tbody>
      <tr><td><strong>Framework</strong></td><td class="mono">Substrate</td><td>Modular blockchain framework</td></tr>
      <tr><td><strong>Consensus</strong></td><td class="mono">DPoS + BABE/GRANDPA</td><td>Block production + finality</td></tr>
      <tr><td><strong>Block Time</strong></td><td class="mono">6 seconds</td><td>BABE slot time</td></tr>
      <tr><td><strong>Smart Contracts</strong></td><td class="mono">ink! / WASM</td><td>Substrate-native</td></tr>
      <tr><td><strong>Token</strong></td><td class="mono">VRDX (9 decimals)</td><td>Native gas + staking</td></tr>
      <tr><td><strong>Supply</strong></td><td class="mono">100,000,000,000</td><td>Fixed supply</td></tr>
      <tr><td><strong>DEX</strong></td><td class="mono">Native AMM</td><td>6 pools</td></tr>
      <tr><td><strong>Cross-Chain</strong></td><td class="mono">IBC</td><td>Inter-Blockchain Communication</td></tr>
      <tr><td><strong>Validator Target</strong></td><td class="mono">21</td><td>DPoS active set</td></tr>
    </tbody>
  </table>
</div>

<!-- 5-6. DPOS + DEX -->
<div class="content page-break">
  <div class="page-header"><img src="data:image/png;base64,{logo_black_b64}" alt="Verdis" class="logo" style="height:24px"><span class="title">Whitepaper v2.0</span></div>
  <h1 class="section-num">Section 5</h1><h1>DPoS Consensus</h1>
  <p>21 target validators selected by delegated stake. Green scoring rewards renewable energy. Slashing penalizes malicious behavior. Staking APR: 5-6.67% at 30-40% stake rate. 20B VRDX staking pool.</p>
  <h1 class="section-num" style="margin-top:16px">Section 6</h1><h1>AMM DEX</h1>
  <table>
    <thead><tr><th>Pool</th><th>Pair</th><th>Initial Liquidity</th></tr></thead>
    <tbody>
      <tr><td>Pool 1</td><td>VRDX/ECO</td><td class="mono">500,000 VRDX</td></tr>
      <tr><td>Pool 2</td><td>VRDX/CARBON</td><td class="mono">300,000 VRDX</td></tr>
      <tr><td>Pool 3</td><td>VRDX/TREE</td><td class="mono">200,000 VRDX</td></tr>
      <tr><td>Pool 4</td><td>VRDX/GREEN</td><td class="mono">200,000 VRDX</td></tr>
      <tr><td>Pool 5</td><td>ECO/CARBON</td><td class="mono">100,000 ECO</td></tr>
      <tr><td>Pool 6</td><td>VRDX/REDD</td><td class="mono">100,000 VRDX</td></tr>
    </tbody>
  </table>
</div>

<!-- 7-8. CARBON + EVOLVIXOS -->
<div class="content page-break">
  <div class="page-header"><img src="data:image/png;base64,{logo_black_b64}" alt="Verdis" class="logo" style="height:24px"><span class="title">Whitepaper v2.0</span></div>
  <h1 class="section-num">Section 7</h1><h1>Carbon Credits &amp; Eco Layer</h1>
  <p>Carbon credits minted, traded, and retired on-chain. Green validator scoring (1-5). Reforestation projects logged with GPS, tree count, CO2 estimates. AI verification via EvolvixOS.</p>
  <h1 class="section-num" style="margin-top:16px">Section 8</h1><h1>EvolvixOS Integration</h1>
  <div class="card"><h3>Smart Contract Auditing</h3><p>AI analyzes every contract before deployment. Security scores published on-chain.</p></div>
  <div class="card"><h3>AI Governance</h3><p>AI simulates economic impact of proposals, provides recommendations.</p></div>
  <div class="card"><h3>Carbon Verification</h3><p>Satellite imagery + IoT + AI for autonomous reforestation verification.</p></div>
</div>

<!-- 9. TOKENOMICS -->
<div class="content page-break">
  <div class="page-header"><img src="data:image/png;base64,{logo_black_b64}" alt="Verdis" class="logo" style="height:24px"><span class="title">Whitepaper v2.0</span></div>
  <h1 class="section-num">Section 9</h1><h1>Tokenomics &amp; Distribution</h1>
  <table>
    <thead><tr><th>Category</th><th>Allocation</th><th>%</th><th>Purpose</th></tr></thead>
    <tbody>
      <tr><td>Ecosystem &amp; Grants</td><td class="mono">25B</td><td class="mono">25%</td><td>Grants, partnerships</td></tr>
      <tr><td>PoS Staking</td><td class="mono">20B</td><td class="mono">20%</td><td>Validator rewards</td></tr>
      <tr><td>Treasury</td><td class="mono">15B</td><td class="mono">15%</td><td>DAO-governed</td></tr>
      <tr><td>Development</td><td class="mono">10B</td><td class="mono">10%</td><td>Core development</td></tr>
      <tr><td>Liquidity</td><td class="mono">10B</td><td class="mono">10%</td><td>DEX liquidity</td></tr>
      <tr><td>Community</td><td class="mono">5B</td><td class="mono">5%</td><td>Rewards, airdrops</td></tr>
      <tr><td>Team &amp; Advisors</td><td class="mono">5B</td><td class="mono">5%</td><td>12-mo cliff vesting</td></tr>
      <tr><td>Seed / Strategic</td><td class="mono">3B</td><td class="mono">3%</td><td>12-mo cliff</td></tr>
      <tr><td>Public Presale</td><td class="mono">2B</td><td class="mono">2%</td><td>6-mo cliff</td></tr>
    </tbody>
  </table>
  <div class="dist-row"><span class="dist-label">Ecosystem</span><div class="dist-bar"><div class="dist-fill" style="width:100%"></div></div><span class="dist-val">25%</span></div>
  <div class="dist-row"><span class="dist-label">Staking</span><div class="dist-bar"><div class="dist-fill" style="width:80%"></div></div><span class="dist-val">20%</span></div>
  <div class="dist-row"><span class="dist-label">Treasury</span><div class="dist-bar"><div class="dist-fill" style="width:60%"></div></div><span class="dist-val">15%</span></div>
  <div class="dist-row"><span class="dist-label">Development</span><div class="dist-bar"><div class="dist-fill" style="width:40%"></div></div><span class="dist-val">10%</span></div>
  <div class="dist-row"><span class="dist-label">Liquidity</span><div class="dist-bar"><div class="dist-fill" style="width:40%"></div></div><span class="dist-val">10%</span></div>
  <div class="dist-row"><span class="dist-label">Community</span><div class="dist-bar"><div class="dist-fill" style="width:20%"></div></div><span class="dist-val">5%</span></div>
  <div class="dist-row"><span class="dist-label">Team</span><div class="dist-bar"><div class="dist-fill" style="width:20%"></div></div><span class="dist-val">5%</span></div>
  <div class="dist-row"><span class="dist-label">Seed</span><div class="dist-bar"><div class="dist-fill" style="width:12%"></div></div><span class="dist-val">3%</span></div>
  <div class="dist-row"><span class="dist-label">Presale</span><div class="dist-bar"><div class="dist-fill" style="width:8%"></div></div><span class="dist-val">2%</span></div>
</div>

<!-- 10. VESTING & CLIFF ROADMAP (FROM TGE DAY) -->
<div class="content page-break">
  <div class="page-header"><img src="data:image/png;base64,{logo_black_b64}" alt="Verdis" class="logo" style="height:24px"><span class="title">Whitepaper v2.0</span></div>
  <h1 class="section-num">Section 10</h1>
  <h1>Vesting &amp; Cliff Roadmap (From TGE Day)</h1>
  <p>Every unlock event is measured from <strong>Day 0 (TGE &mdash; Token Generation Event)</strong>. This is the day tokens are sold and released to the market. All cliffs, vesting periods, and circulating supply milestones are calculated from this date.</p>

  <h2>Unlock Events</h2>
  <div class="card"><h3>Day 0 &mdash; TGE</h3><p>Initial circulating: <strong>8B VRDX (8%)</strong>. All investor tokens locked (0% unlocked). Liquidity seeded, DEX active, staking begins.</p></div>
  <div class="card warn"><h3>Month 3 &mdash; Community Cliff Ends</h3><p>Community round (1B at $0.003) 3-month cliff completes. 20% TGE release. Linear vesting: <span class="mono">53.3M/month</span> over 15 months.</p></div>
  <div class="card warn"><h3>Month 6 &mdash; Presale Cliff Ends</h3><p>Presale (2B at $0.004) 6-month cliff completes. 25% TGE release. Linear vesting: <span class="mono">250M/month</span> over 6 months.</p></div>
  <div class="card"><h3>Month 12 &mdash; Seed &amp; Team Cliff Ends</h3><p>Seed/Private (3B) and Team (5B) 12-month cliffs complete. 0% unlocked at TGE. Seed: <span class="mono">125M/month</span> over 24 months. Team: <span class="mono">138.9M/month</span> over 36 months.</p></div>
  <div class="card success"><h3>Month 36 &mdash; Seed Fully Vested</h3><p>All 3B Seed/Private tokens unlocked. 24 months of linear vesting complete.</p></div>
  <div class="card success"><h3>Month 48 &mdash; Team Fully Vested</h3><p>All 5B Team &amp; Advisor tokens unlocked. All investor and team tokens now circulating.</p></div>
  <div class="card success"><h3>Year 10 &mdash; Full Ecosystem Unlock</h3><p>Ecosystem (25B) and Staking (20B) fully released. <strong>95B+ VRDX circulating (95%+)</strong>.</p></div>

  <h2>Unlock Schedule (From TGE Day)</h2>
  <table>
    <thead><tr><th>Time from TGE</th><th>Event</th><th>Unlocked</th><th>Circulating</th><th>%</th></tr></thead>
    <tbody>
      <tr><td><strong>Day 0</strong></td><td>TGE &mdash; tokens sold</td><td class="unlocked">8B</td><td class="mono">8,000,000,000</td><td class="mono">8.0%</td></tr>
      <tr><td>Month 3</td><td>Community cliff ends</td><td class="partial">+53.3M/mo</td><td class="mono">~8,360,000,000</td><td class="mono">~8.4%</td></tr>
      <tr><td>Month 6</td><td>Presale cliff ends</td><td class="partial">+250M/mo</td><td class="mono">~9,500,000,000</td><td class="mono">~9.5%</td></tr>
      <tr><td>Month 12</td><td>Seed + Team cliff ends</td><td class="partial">+263.9M/mo</td><td class="mono">~11,500,000,000</td><td class="mono">~11.5%</td></tr>
      <tr><td>Month 24</td><td>Community + Presale vested</td><td class="partial">~263.9M/mo</td><td class="mono">~24,300,000,000</td><td class="mono">~24.3%</td></tr>
      <tr><td>Month 36</td><td>Seed fully vested</td><td class="partial">~138.9M/mo</td><td class="mono">~39,300,000,000</td><td class="mono">~39.3%</td></tr>
      <tr><td>Month 48</td><td>Team fully vested</td><td class="partial">~140M/mo</td><td class="mono">~56,900,000,000</td><td class="mono">~56.9%</td></tr>
      <tr><td>Year 5</td><td>Ecosystem emission</td><td class="partial">~2B/yr</td><td class="mono">~65,000,000,000</td><td class="mono">~65.0%</td></tr>
      <tr><td>Year 10</td><td>Full unlock</td><td class="unlocked">95B+</td><td class="mono">~95,000,000,000</td><td class="mono">~95.0%</td></tr>
    </tbody>
  </table>

  <h2>Circulating Supply Growth (From TGE Day)</h2>
  <div class="supply-row"><span class="sr-when">Day 0</span><div class="sr-bar"><div class="sr-fill" style="width:8%"><span class="sr-val">8B</span></div></div><span class="sr-pct">8%</span></div>
  <div class="supply-row"><span class="sr-when">Month 3</span><div class="sr-bar"><div class="sr-fill" style="width:8.4%"><span class="sr-val">8.4B</span></div></div><span class="sr-pct">8.4%</span></div>
  <div class="supply-row"><span class="sr-when">Month 6</span><div class="sr-bar"><div class="sr-fill" style="width:9.5%"><span class="sr-val">9.5B</span></div></div><span class="sr-pct">9.5%</span></div>
  <div class="supply-row"><span class="sr-when">Month 12</span><div class="sr-bar"><div class="sr-fill" style="width:11.5%"><span class="sr-val">11.5B</span></div></div><span class="sr-pct">11.5%</span></div>
  <div class="supply-row"><span class="sr-when">Month 24</span><div class="sr-bar"><div class="sr-fill" style="width:24%"><span class="sr-val">~24B</span></div></div><span class="sr-pct">24%</span></div>
  <div class="supply-row"><span class="sr-when">Month 36</span><div class="sr-bar"><div class="sr-fill" style="width:39%"><span class="sr-val">~39B</span></div></div><span class="sr-pct">39%</span></div>
  <div class="supply-row"><span class="sr-when">Month 48</span><div class="sr-bar"><div class="sr-fill" style="width:57%"><span class="sr-val">~57B</span></div></div><span class="sr-pct">57%</span></div>
  <div class="supply-row"><span class="sr-when">Year 5</span><div class="sr-bar"><div class="sr-fill" style="width:65%"><span class="sr-val">~65B</span></div></div><span class="sr-pct">65%</span></div>
  <div class="supply-row"><span class="sr-when">Year 10</span><div class="sr-bar"><div class="sr-fill" style="width:95%"><span class="sr-val">~95B</span></div></div><span class="sr-pct">95%</span></div>

  <div class="insight-box">
    <div class="it-title">&#9888; Key Insight</div>
    <div class="it-body">From TGE day, only 8% of tokens are circulating. Investor tokens are fully locked with 3-12 month cliffs. The first unlock is at Month 3 (Community). The largest wave starts at Month 12 (Seed + Team). This design prevents dump pressure and ensures long-term price stability.</div>
  </div>
</div>

<!-- 11. FUNDRAISING -->
<div class="content page-break">
  <div class="page-header"><img src="data:image/png;base64,{logo_black_b64}" alt="Verdis" class="logo" style="height:24px"><span class="title">Whitepaper v2.0</span></div>
  <h1 class="section-num">Section 11</h1><h1>Fundraising &amp; Staking</h1>
  <table>
    <thead><tr><th>Round</th><th>Price</th><th>Tokens</th><th>Raised</th><th>Cliff</th></tr></thead>
    <tbody>
      <tr><td>Seed</td><td class="mono">$0.0015</td><td class="mono">3B</td><td class="mono">$4.5M</td><td>12 months</td></tr>
      <tr><td>Community</td><td class="mono">$0.003</td><td class="mono">1B</td><td class="mono">$3M</td><td>3 months</td></tr>
      <tr><td>Presale</td><td class="mono">$0.004</td><td class="mono">2B</td><td class="mono">$8M</td><td>6 months</td></tr>
      <tr><td>TGE/IDO</td><td class="mono">$0.005</td><td class="mono">0.5B</td><td class="mono">$2.5M</td><td>None</td></tr>
      <tr style="border-top:2px solid #16a34a"><td><strong>Total</strong></td><td></td><td class="mono"><strong>6.5B</strong></td><td class="mono"><strong>$18M</strong></td><td></td></tr>
    </tbody>
  </table>
  <p>Staking: 20B pool, 5-6.67% APR at 30-40% stake. Validators earn block rewards + DEX fees.</p>
</div>

<!-- 12. ROADMAP -->
<div class="content page-break">
  <div class="page-header"><img src="data:image/png;base64,{logo_black_b64}" alt="Verdis" class="logo" style="height:24px"><span class="title">Whitepaper v2.0</span></div>
  <h1 class="section-num">Section 12</h1><h1>Roadmap</h1>
  <p><strong>Phase 1 (Q1 2026):</strong> Genesis &amp; TGE &mdash; 8B VRDX circulating, all investor tokens locked.</p>
  <p><strong>Phase 2 (Q2 2026):</strong> DPoS staking &amp; DEX activation &mdash; 21 validators, 8.2B bonded.</p>
  <p><strong>Phase 3 (Q3 2026):</strong> Eco precompiles &amp; presale unlock &mdash; carbon credits active.</p>
  <p><strong>Phase 4 (Q1 2027):</strong> Seed + Team cliff end &mdash; all vesting active, DAO governance.</p>
  <p><strong>Phase 5 (2027-2030):</strong> Global carbon offset scaling &mdash; 10M+ tCO2e retired.</p>
  <p><strong>Phase 6 (2030-2032):</strong> AI-powered governance &mdash; hybrid human-AI DAO.</p>
  <p><strong>Phase 7 (2030-2033):</strong> Cross-chain carbon credits &mdash; IBC, 100M+ tCO2e/yr.</p>
  <p><strong>Phase 8 (2031-2034):</strong> ZK rollup &mdash; 10,000+ TPS, sub-cent fees.</p>
</div>

<!-- 13. TEAM -->
<div class="content page-break">
  <div class="page-header"><img src="data:image/png;base64,{logo_black_b64}" alt="Verdis" class="logo" style="height:24px"><span class="title">Whitepaper v2.0</span></div>
  <h1 class="section-num">Section 13</h1><h1>Team</h1>
  <table>
    <tbody>
      <tr><td><strong>Dorian Jean</strong></td><td>CEO &amp; Founder</td></tr>
      <tr><td><strong>Mark Jamestown</strong></td><td>CTO</td></tr>
      <tr><td><strong>Elizabeth Jefferson</strong></td><td>Head of Product</td></tr>
      <tr><td><strong>Rojs Gordons</strong></td><td>Co-Founder &amp; Community</td></tr>
      <tr><td><strong>Mar&iacute;a Dolores M&aacute;rquez de Prado</strong></td><td>Legal Counsel</td></tr>
      <tr><td><strong>Ignacio Mart&iacute;nez-Arrieta</strong></td><td>Legal &amp; Compliance</td></tr>
    </tbody>
  </table>
</div>

<!-- 14. CONCLUSION -->
<div class="content page-break">
  <div class="page-header"><img src="data:image/png;base64,{logo_black_b64}" alt="Verdis" class="logo" style="height:24px"><span class="title">Whitepaper v2.0</span></div>
  <h1 class="section-num">Section 14</h1><h1>Conclusion</h1>
  <p>Verdis Chain proves blockchain can be environmentally regenerative. By embedding carbon credits, green scoring, and reforestation into consensus, sustainability becomes a protocol-level feature.</p>
  <p>With 30+ pallets, native AMM DEX, ink! contracts, DPoS, IBC, and EvolvixOS AI integration, Verdis provides a complete green technology stack.</p>
  <p>The 100B VRDX economy incentivizes decentralization, security, and environmental impact &mdash; with structured vesting from TGE day preventing dump pressure.</p>
  <p style="margin-top:16px;text-align:center;font-size:14px;font-weight:700;color:#16a34a;font-family:'Space Grotesk',sans-serif">This is not a promise. This is architecture.</p>
  <div style="margin-top:32px;text-align:center;border-top:1px solid #e2e8f0;padding-top:16px">
    <img src="data:image/png;base64,{logo_black_b64}" alt="Verdis Chain" style="height:32px;margin-bottom:8px">
    <p style="font-size:10px;color:#64748b;text-align:center">verdischain.com &middot; &copy; 2026 Verdis Chain &middot; Protremix &middot; MIT License</p>
  </div>
</div>

</body>
</html>"""

with open('/tmp/whitepaper_pdf_v2.html', 'w') as f:
    f.write(html_content)

print("Generating PDF with WeasyPrint...")
doc = HTML(string=html_content, base_url='/var/www/verdiscan/')
doc.write_pdf(OUTPUT_PDF)

import shutil
shutil.copy(OUTPUT_PDF, OUTPUT_PDF_REPO)
size = os.path.getsize(OUTPUT_PDF)
print(f"PDF generated: {OUTPUT_PDF} ({size / 1024:.1f} KB)")
