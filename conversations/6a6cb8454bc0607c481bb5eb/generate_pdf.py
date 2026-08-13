#!/usr/bin/env python3
"""
Generate a branded Verdis Chain Whitepaper PDF using WeasyPrint.
Uses local file references for logo images.
"""
import os
import base64
from weasyprint import HTML, CSS

# Paths
LOGO_WHITE = '/var/www/verdiscan/assets/verdis-logo-white.png'
LOGO_BLACK = '/var/www/verdiscan/assets/verdis-logo-black.png'
OUTPUT_PDF = '/var/www/verdiscan/whitepaper/verdis-whitepaper.pdf'
OUTPUT_PDF_REPO = '/opt/verdis-chain-rust/web/whitepaper/verdis-whitepaper.pdf'

# Encode logos as base64 for embedding
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
@page {{
  size: A4;
  margin: 0;
  @bottom-center {{
    content: "Verdis Chain Whitepaper v2.0  |  Page " counter(page) " of " counter(pages);
    font-family: 'Inter', sans-serif;
    font-size: 9px;
    color: #64748b;
    margin-bottom: 16px;
  }}
}}
@page :first {{
  margin: 0;
  @bottom-center {{ content: ""; }}
}}
@page cover {{
  margin: 0;
  @bottom-center {{ content: ""; }}
}}

* {{ margin: 0; padding: 0; box-sizing: border-box; }}

body {{
  font-family: 'Inter', 'Helvetica Neue', sans-serif;
  color: #1e293b;
  font-size: 11px;
  line-height: 1.7;
  background: #fff;
}}

/* COVER PAGE */
.cover {{
  page: cover;
  width: 210mm;
  height: 297mm;
  background: linear-gradient(135deg, #040806 0%, #0a1f0e 50%, #04150a 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 40mm 30mm;
  position: relative;
  page-break-after: always;
  color: #fff;
}}
.cover::before {{
  content: '';
  position: absolute;
  top: -20%;
  right: -15%;
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(22,163,74,0.15), transparent 55%);
  border-radius: 50%;
}}
.cover::after {{
  content: '';
  position: absolute;
  bottom: -15%;
  left: -10%;
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(21,128,61,0.1), transparent 60%);
  border-radius: 50%;
}}
.cover-logo {{
  width: 180px;
  margin-bottom: 24px;
}}
.cover-badge {{
  display: inline-block;
  padding: 6px 16px;
  border: 1px solid #16a34a;
  border-radius: 100px;
  font-size: 11px;
  font-weight: 600;
  color: #16a34a;
  margin-bottom: 20px;
  letter-spacing: 0.5px;
}}
.cover-title {{
  font-family: 'Space Grotesk', 'Helvetica', sans-serif;
  font-size: 42px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 12px;
  text-align: center;
  letter-spacing: -1px;
}}
.cover-title .accent {{
  color: #16a34a;
}}
.cover-subtitle {{
  font-size: 14px;
  color: #94a3b8;
  text-align: center;
  max-width: 400px;
  line-height: 1.6;
  margin-bottom: 32px;
}}
.cover-stats {{
  display: flex;
  gap: 32px;
  justify-content: center;
  margin-bottom: 32px;
}}
.cover-stat {{
  text-align: center;
}}
.cover-stat .val {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 20px;
  font-weight: 700;
  color: #16a34a;
}}
.cover-stat .lbl {{
  font-size: 10px;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-top: 4px;
}}
.cover-footer {{
  position: absolute;
  bottom: 30mm;
  text-align: center;
  font-size: 11px;
  color: #475569;
  width: 100%;
}}
.cover-footer strong {{
  color: #94a3b8;
}}

/* CONTENT PAGES */
.content {{
  padding: 20mm 25mm;
  page-break-inside: auto;
}}
.content h1 {{
  font-family: 'Space Grotesk', 'Helvetica', sans-serif;
  font-size: 20px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 8px;
  margin-top: 0;
  padding-bottom: 8px;
  border-bottom: 2px solid #16a34a;
  display: inline-block;
}}
.content h1.section-num {{
  color: #16a34a;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 4px;
  border: none;
  display: block;
  padding: 0;
}}
.content h2 {{
  font-family: 'Space Grotesk', sans-serif;
  font-size: 14px;
  font-weight: 700;
  color: #0f172a;
  margin-top: 16px;
  margin-bottom: 8px;
}}
.content h3 {{
  font-family: 'Space Grotesk', sans-serif;
  font-size: 12px;
  font-weight: 600;
  color: #15803d;
  margin-top: 12px;
  margin-bottom: 6px;
}}
.content p {{
  font-size: 11px;
  color: #334155;
  line-height: 1.7;
  margin-bottom: 8px;
  text-align: justify;
}}
.content strong {{
  color: #0f172a;
}}
.content .mono {{
  font-family: 'JetBrains Mono', 'Courier New', monospace;
  font-size: 10px;
  background: #f1f5f9;
  padding: 1px 6px;
  border-radius: 4px;
  color: #15803d;
}}
.content ul {{
  margin-left: 16px;
  margin-bottom: 8px;
}}
.content li {{
  font-size: 11px;
  color: #334155;
  line-height: 1.7;
  margin-bottom: 4px;
}}

/* TABLES */
table {{
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 12px;
  font-size: 10px;
}}
th {{
  text-align: left;
  padding: 8px 12px;
  background: #f8fafc;
  border-bottom: 2px solid #16a34a;
  font-size: 9px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #64748b;
  font-weight: 600;
}}
td {{
  padding: 8px 12px;
  border-bottom: 1px solid #e2e8f0;
  color: #334155;
}}
tr:last-child td {{
  border-bottom: none;
}}

/* CARDS */
.card {{
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-left: 3px solid #16a34a;
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 8px;
}}
.card h3 {{
  margin-top: 0;
}}

/* METRICS GRID */
.metrics {{
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  margin-bottom: 12px;
}}
.metric {{
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 10px;
  text-align: center;
}}
.metric .val {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  font-weight: 700;
  color: #16a34a;
}}
.metric .lbl {{
  font-size: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #64748b;
  margin-top: 2px;
}}

/* DISTRIBUTION BARS */
.dist-row {{
  display: flex;
  align-items: center;
  margin-bottom: 4px;
  font-size: 10px;
}}
.dist-label {{
  width: 120px;
  color: #334155;
}}
.dist-bar {{
  flex: 1;
  height: 16px;
  background: #f1f5f9;
  border-radius: 4px;
  overflow: hidden;
  margin: 0 8px;
}}
.dist-fill {{
  height: 100%;
  background: linear-gradient(90deg, #16a34a, #15803d);
  border-radius: 4px;
}}
.dist-val {{
  width: 50px;
  text-align: right;
  font-family: 'JetBrains Mono', monospace;
  color: #15803d;
  font-weight: 600;
}}

/* PAGE BREAK */
.page-break {{
  page-break-before: always;
}}

/* TEAM */
.team-grid {{
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  margin-bottom: 12px;
}}
.team-card {{
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 12px;
}}
.team-card .name {{
  font-family: 'Space Grotesk', sans-serif;
  font-size: 12px;
  font-weight: 700;
  color: #0f172a;
}}
.team-card .role {{
  font-size: 10px;
  color: #16a34a;
  font-weight: 600;
  margin-bottom: 4px;
}}
.team-card .bio {{
  font-size: 10px;
  color: #64748b;
  line-height: 1.5;
}}

/* ROADMAP */
.roadmap-item {{
  border-left: 2px solid #16a34a;
  padding: 8px 0 8px 16px;
  margin-bottom: 8px;
}}
.roadmap-phase {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 9px;
  color: #16a34a;
  font-weight: 600;
}}
.roadmap-title {{
  font-family: 'Space Grotesk', sans-serif;
  font-size: 11px;
  font-weight: 700;
  color: #0f172a;
  margin: 2px 0;
}}
.roadmap-desc {{
  font-size: 10px;
  color: #475569;
  line-height: 1.5;
}}

/* HEADER BAR */
.page-header {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e2e8f0;
  padding-bottom: 8px;
  margin-bottom: 16px;
}}
.page-header .logo {{
  height: 24px;
}}
.page-header .title {{
  font-size: 9px;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 1px;
}}
</style>
</head>
<body>

<!-- COVER PAGE -->
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
  <div class="cover-footer">
    <strong>Verdis Chain</strong> &middot; Protremix &middot; Open-source under MIT License<br>
    verdischain.com &middot; August 2026
  </div>
</div>

<!-- TABLE OF CONTENTS -->
<div class="content">
  <div class="page-header">
    <img src="data:image/png;base64,{logo_black_b64}" alt="Verdis" class="logo" style="height:24px">
    <span class="title">Whitepaper v2.0</span>
  </div>
  <h1 class="section-num">Contents</h1>
  <h1>Table of Contents</h1>
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
    <li><strong>10.</strong> Vesting &amp; Fundraising</li>
    <li><strong>11.</strong> Roadmap</li>
    <li><strong>12.</strong> Future Solutions</li>
    <li><strong>13.</strong> Team</li>
    <li><strong>14.</strong> Conclusion</li>
  </ul>
</div>

<!-- 1. EXECUTIVE SUMMARY -->
<div class="content page-break">
  <div class="page-header">
    <img src="data:image/png;base64,{logo_black_b64}" alt="Verdis" class="logo" style="height:24px">
    <span class="title">Whitepaper v2.0</span>
  </div>
  <h1 class="section-num">Section 1</h1>
  <h1>Executive Summary</h1>
  <p>Verdis Chain is a carbon-negative Layer-1 blockchain built on Substrate, powered by native Delegated Proof-of-Stake (DPoS) consensus, an integrated AMM decentralized exchange (DEX), ink! smart contracts, and on-chain carbon credit tracking. The protocol is designed to prove that blockchain infrastructure can be environmentally regenerative rather than destructive.</p>
  <p>The native token, <strong>VRDX</strong>, has a fixed supply of <strong>100 billion</strong> with <strong>9 decimals</strong>, serving as the gas token, staking asset, governance instrument, and medium of exchange across the ecosystem. VRDX is not an ERC-20 wrapper &mdash; it is woven into the consensus layer itself.</p>
  <p>Verdis Chain connects to <strong>EvolvixOS</strong>, an AI Engineering Operating System that provides smart contract auditing, AI-powered development tools, and a plugin marketplace. Together, they form a complete green technology stack: blockchain provides trust and value transfer, AI provides intelligence and automation.</p>
  <p>The protocol features <strong>30+ custom Substrate pallets</strong>, including DPoS consensus with 21 target validators, an AMM DEX with 6 liquidity pools, carbon credit minting and retirement, green validator scoring, reforestation logging, governance, IBC cross-chain communication, and Solana-inspired innovations (Gulf Stream, Turbine, Sealevel execution, ZK compression).</p>

  <h2>Key Metrics</h2>
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

<!-- 2. PROBLEM STATEMENT -->
<div class="content page-break">
  <div class="page-header">
    <img src="data:image/png;base64,{logo_black_b64}" alt="Verdis" class="logo" style="height:24px">
    <span class="title">Whitepaper v2.0</span>
  </div>
  <h1 class="section-num">Section 2</h1>
  <h1>Problem Statement</h1>
  <h2>The Environmental Cost of Blockchain</h2>
  <p>Traditional blockchain networks consume enormous amounts of energy. Bitcoin's annual energy consumption rivals entire countries, and Ethereum's pre-merge PoW system had a carbon footprint comparable to a medium-sized nation. This environmental cost has made blockchain technology a target for criticism from environmentalists, regulators, and institutions.</p>
  <h2>The Fragmentation Problem</h2>
  <p>Carbon credit markets are fragmented across multiple registries (Verra, Gold Standard, EU ETS) with inconsistent standards, opaque verification processes, and limited interoperability. There is no unified, transparent infrastructure for issuing, trading, and retiring carbon credits with full chain of custody.</p>
  <h2>The AI-Blockchain Gap</h2>
  <p>AI and blockchain have developed as separate ecosystems with limited integration. Smart contract auditing is manual and expensive. There is no protocol where AI models automatically analyze, secure, and optimize on-chain activity in real time.</p>
</div>

<!-- 3. SOLUTION OVERVIEW -->
<div class="content page-break">
  <div class="page-header">
    <img src="data:image/png;base64,{logo_black_b64}" alt="Verdis" class="logo" style="height:24px">
    <span class="title">Whitepaper v2.0</span>
  </div>
  <h1 class="section-num">Section 3</h1>
  <h1>Solution Overview</h1>
  <p>Verdis Chain addresses these problems with a comprehensive green blockchain ecosystem:</p>
  <div class="card">
    <h3>Carbon-Negative Consensus</h3>
    <p>DPoS consensus uses 99.9% less energy than PoW. Validators are incentivized to use renewable energy through green validator scoring, which rewards eco-friendly operators with higher block production priority.</p>
  </div>
  <div class="card">
    <h3>On-Chain Carbon Credits</h3>
    <p>Carbon credits are minted, traded, and retired directly on-chain with full transparency. Every tonne of CO2 offset is traceable from source to retirement, eliminating double-counting and fraud.</p>
  </div>
  <div class="card">
    <h3>AI-Powered Security</h3>
    <p>Every smart contract deployed on Verdis Chain is automatically analyzed by EvolvixOS AI before execution, with security scores and vulnerability reports published on-chain.</p>
  </div>
  <div class="card">
    <h3>Native AMM DEX</h3>
    <p>A built-in automated market maker provides decentralized trading without external dependencies. 6 liquidity pools with overflow-protected arithmetic and deadline parameters.</p>
  </div>
  <div class="card">
    <h3>IBC Cross-Chain</h3>
    <p>Inter-Blockchain Communication protocol enables trustless bridges to Polkadot, Cosmos, Ethereum, and BSC. Carbon credits become tradeable across all connected chains.</p>
  </div>
</div>

<!-- 4. TECHNICAL ARCHITECTURE -->
<div class="content page-break">
  <div class="page-header">
    <img src="data:image/png;base64,{logo_black_b64}" alt="Verdis" class="logo" style="height:24px">
    <span class="title">Whitepaper v2.0</span>
  </div>
  <h1 class="section-num">Section 4</h1>
  <h1>Technical Architecture</h1>
  <table>
    <thead><tr><th>Parameter</th><th>Value</th><th>Description</th></tr></thead>
    <tbody>
      <tr><td><strong>Framework</strong></td><td class="mono">Substrate</td><td>Modular blockchain framework by Parity</td></tr>
      <tr><td><strong>Consensus</strong></td><td class="mono">DPoS + BABE/GRANDPA</td><td>Block production + finality gadget</td></tr>
      <tr><td><strong>Block Time</strong></td><td class="mono">6 seconds</td><td>BABE slot time target</td></tr>
      <tr><td><strong>Smart Contracts</strong></td><td class="mono">ink! / WASM</td><td>Substrate-native contracts via pallet_contracts</td></tr>
      <tr><td><strong>Token</strong></td><td class="mono">VRDX (9 decimals)</td><td>Native gas + staking + governance</td></tr>
      <tr><td><strong>Supply</strong></td><td class="mono">100,000,000,000</td><td>Fixed supply, disinflationary emission</td></tr>
      <tr><td><strong>DEX</strong></td><td class="mono">Native AMM</td><td>6 pools, constant product formula</td></tr>
      <tr><td><strong>Cross-Chain</strong></td><td class="mono">IBC</td><td>Inter-Blockchain Communication</td></tr>
      <tr><td><strong>Validator Target</strong></td><td class="mono">21</td><td>DPoS active validator set</td></tr>
      <tr><td><strong>Pallets</strong></td><td class="mono">30+</td><td>Custom Substrate pallets</td></tr>
    </tbody>
  </table>

  <h2>Core Pallets</h2>
  <table>
    <thead><tr><th>Pallet</th><th>Index</th><th>Function</th></tr></thead>
    <tbody>
      <tr><td>dpos</td><td class="mono">10</td><td>Delegated Proof-of-Stake consensus</td></tr>
      <tr><td>amm-dex</td><td class="mono">20</td><td>Automated market maker DEX</td></tr>
      <tr><td>eco</td><td class="mono">30</td><td>Carbon credits, green scoring, reforestation</td></tr>
      <tr><td>fungible-tokens</td><td class="mono">40</td><td>Custom token creation</td></tr>
      <tr><td>governance</td><td class="mono">50</td><td>Democracy, council, treasury</td></tr>
      <tr><td>presale</td><td class="mono">60</td><td>Token presale and vesting</td></tr>
      <tr><td>gulf-stream</td><td class="mono">51</td><td>Transaction forwarding (Solana-inspired)</td></tr>
      <tr><td>sealevel</td><td class="mono">55</td><td>Parallel execution scheduling</td></tr>
      <tr><td>zkc</td><td class="mono">53</td><td>ZK compression</td></tr>
    </tbody>
  </table>
</div>

<!-- 5. DPOS CONSENSUS -->
<div class="content page-break">
  <div class="page-header">
    <img src="data:image/png;base64,{logo_black_b64}" alt="Verdis" class="logo" style="height:24px">
    <span class="title">Whitepaper v2.0</span>
  </div>
  <h1 class="section-num">Section 5</h1>
  <h1>DPoS Consensus</h1>
  <p>Verdis Chain uses Delegated Proof-of-Stake (DPoS) combined with BABE/GRANDPA for block production and finality. Token holders delegate their stake to validators who produce blocks on their behalf.</p>

  <h2>Validator System</h2>
  <ul>
    <li><strong>21 target validators</strong> in the active set, selected by total delegated stake</li>
    <li><strong>Green validator scoring</strong> rewards validators using 100% renewable energy with higher priority</li>
    <li><strong>Slashing</strong> penalizes malicious behavior (equivocation, downtime) with configurable severity</li>
    <li><strong>Registration deposit:</strong> 0 VRDX (subsidized for early validators)</li>
    <li><strong>Delegation:</strong> Any VRDX holder can delegate to validators</li>
  </ul>

  <h2>Economic Parameters</h2>
  <table>
    <thead><tr><th>Parameter</th><th>Value</th></tr></thead>
    <tbody>
      <tr><td>Active Validator Count</td><td class="mono">21</td></tr>
      <tr><td>Epoch Duration</td><td class="mono">50 slots (300s)</td></tr>
      <tr><td>Session Period</td><td class="mono">50 blocks</td></tr>
      <tr><td>Staking APR</td><td class="mono">5-6.67%</td></tr>
      <tr><td>Staking Pool</td><td class="mono">20B VRDX</td></tr>
      <tr><td>Min Delegate</td><td class="mono">1 VRDX</td></tr>
    </tbody>
  </table>
</div>

<!-- 6. AMM DEX -->
<div class="content page-break">
  <div class="page-header">
    <img src="data:image/png;base64,{logo_black_b64}" alt="Verdis" class="logo" style="height:24px">
    <span class="title">Whitepaper v2.0</span>
  </div>
  <h1 class="section-num">Section 6</h1>
  <h1>AMM DEX</h1>
  <p>The native Automated Market Maker (AMM) DEX is built directly into the protocol via a custom Substrate pallet, providing decentralized trading without external dependencies.</p>

  <h2>Liquidity Pools</h2>
  <table>
    <thead><tr><th>Pool</th><th>Pair</th><th>Initial Liquidity</th></tr></thead>
    <tbody>
      <tr><td>Pool 1</td><td>VRDX / ECO</td><td class="mono">500,000 VRDX</td></tr>
      <tr><td>Pool 2</td><td>VRDX / CARBON</td><td class="mono">300,000 VRDX</td></tr>
      <tr><td>Pool 3</td><td>VRDX / TREE</td><td class="mono">200,000 VRDX</td></tr>
      <tr><td>Pool 4</td><td>VRDX / GREEN</td><td class="mono">200,000 VRDX</td></tr>
      <tr><td>Pool 5</td><td>ECO / CARBON</td><td class="mono">100,000 ECO</td></tr>
      <tr><td>Pool 6</td><td>VRDX / REDD</td><td class="mono">100,000 VRDX</td></tr>
    </tbody>
  </table>

  <h2>Security Features</h2>
  <ul>
    <li>Overflow-protected arithmetic (<span class="mono">checked_mul</span>) on all swap/liquidity operations</li>
    <li>Mandatory deadline parameters prevent stale transaction execution</li>
    <li>Self-transfer guard prevents flash loan attacks</li>
    <li>Pool bricking mechanism for emergency shutdown</li>
    <li>LP token overflow protection</li>
  </ul>
</div>

<!-- 7. CARBON CREDITS -->
<div class="content page-break">
  <div class="page-header">
    <img src="data:image/png;base64,{logo_black_b64}" alt="Verdis" class="logo" style="height:24px">
    <span class="title">Whitepaper v2.0</span>
  </div>
  <h1 class="section-num">Section 7</h1>
  <h1>Carbon Credits &amp; Eco Layer</h1>
  <p>The Eco pallet provides on-chain carbon credit infrastructure, making environmental impact verifiable, immutable, and transparent.</p>

  <h3>Carbon Credit Lifecycle</h3>
  <ul>
    <li><strong>Minting:</strong> Verified reforestation projects issue pCO2 tokens on-chain (admin-gated)</li>
    <li><strong>Trading:</strong> Credits trade on the native AMM DEX (VRDX/CARBON pool)</li>
    <li><strong>Retirement:</strong> Credits are permanently burned with immutable proof of offset</li>
    <li><strong>Verification:</strong> AI-powered satellite imagery + IoT sensor analysis via EvolvixOS</li>
  </ul>

  <h3>Green Validator Scoring</h3>
  <p>Validators receive a green score (1-5) based on their energy source. Solar, wind, and hydro validators receive higher scores, translating to higher block production priority. Self-scoring is prevented &mdash; only root can update scores.</p>

  <h3>Reforestation Logging</h3>
  <p>Reforestation projects are registered on-chain with GPS coordinates, tree count, CO2 sequestration estimates, and progress tracking. Each project can issue carbon credits proportional to verified impact.</p>
</div>

<!-- 8. EVOLVIXOS -->
<div class="content page-break">
  <div class="page-header">
    <img src="data:image/png;base64,{logo_black_b64}" alt="Verdis" class="logo" style="height:24px">
    <span class="title">Whitepaper v2.0</span>
  </div>
  <h1 class="section-num">Section 8</h1>
  <h1>EvolvixOS Integration</h1>
  <p>EvolvixOS is an AI Engineering Operating System that forms the intelligence layer of the Verdis ecosystem. Together, Verdis Chain and EvolvixOS provide a complete green technology stack.</p>

  <h2>Integration Points</h2>
  <div class="card">
    <h3>Smart Contract Auditing</h3>
    <p>Every contract deployed on Verdis Chain is automatically analyzed by EvolvixOS AI before execution. Security scores and vulnerability reports are published on-chain.</p>
  </div>
  <div class="card">
    <h3>AI-Powered Governance</h3>
    <p>AI models analyze governance proposals, simulate economic impact, and provide recommendations to VRDX holders.</p>
  </div>
  <div class="card">
    <h3>Carbon Verification</h3>
    <p>Satellite imagery analysis and IoT sensor data are processed by AI to autonomously verify reforestation progress and carbon sequestration.</p>
  </div>
  <div class="card">
    <h3>Developer Tools</h3>
    <p>AI-powered code generation, testing, and deployment tools accessible through EvolvixOS.com &mdash; the main entry point to the ecosystem.</p>
  </div>

  <h2>The Vision</h2>
  <p>The goal: go from <strong>Idea &rarr; AI Assistance &rarr; Application &rarr; Smart Contract &rarr; Verdis Blockchain &rarr; Deployment &rarr; Ecosystem</strong>, all through a single coherent platform.</p>
</div>

<!-- 9. TOKENOMICS -->
<div class="content page-break">
  <div class="page-header">
    <img src="data:image/png;base64,{logo_black_b64}" alt="Verdis" class="logo" style="height:24px">
    <span class="title">Whitepaper v2.0</span>
  </div>
  <h1 class="section-num">Section 9</h1>
  <h1>Tokenomics &amp; Distribution</h1>
  <p>The VRDX token has a fixed supply of 100 billion with 9 decimals, distributed across 9 categories for long-term sustainability.</p>

  <h2>Allocation</h2>
  <table>
    <thead><tr><th>Category</th><th>Allocation</th><th>Percentage</th><th>Purpose</th></tr></thead>
    <tbody>
      <tr><td>Ecosystem &amp; Developer Grants</td><td class="mono">25B</td><td class="mono">25%</td><td>Grants, partnerships, third-party development</td></tr>
      <tr><td>PoS Staking Rewards</td><td class="mono">20B</td><td class="mono">20%</td><td>Validator and delegator block rewards</td></tr>
      <tr><td>Treasury</td><td class="mono">15B</td><td class="mono">15%</td><td>DAO-governed community treasury</td></tr>
      <tr><td>Development</td><td class="mono">10B</td><td class="mono">10%</td><td>Core protocol development</td></tr>
      <tr><td>Liquidity</td><td class="mono">10B</td><td class="mono">10%</td><td>DEX liquidity provisioning</td></tr>
      <tr><td>Community</td><td class="mono">5B</td><td class="mono">5%</td><td>Community rewards, airdrops, faucets</td></tr>
      <tr><td>Team &amp; Advisors</td><td class="mono">5B</td><td class="mono">5%</td><td>Team vesting with 12-month cliff</td></tr>
      <tr><td>Seed / Strategic</td><td class="mono">3B</td><td class="mono">3%</td><td>Early investors, 12-month cliff</td></tr>
      <tr><td>Public Presale</td><td class="mono">2B</td><td class="mono">2%</td><td>Public presale, 6-month cliff</td></tr>
    </tbody>
  </table>

  <h2>Distribution Chart</h2>
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

<!-- 10. VESTING & FUNDRAISING -->
<div class="content page-break">
  <div class="page-header">
    <img src="data:image/png;base64,{logo_black_b64}" alt="Verdis" class="logo" style="height:24px">
    <span class="title">Whitepaper v2.0</span>
  </div>
  <h1 class="section-num">Section 10</h1>
  <h1>Vesting &amp; Fundraising</h1>

  <h2>Fundraising Rounds</h2>
  <table>
    <thead><tr><th>Round</th><th>Price</th><th>Tokens</th><th>Raised</th><th>Discount</th><th>Cliff</th></tr></thead>
    <tbody>
      <tr><td>Seed</td><td class="mono">$0.0015</td><td class="mono">3B</td><td class="mono">$4.5M</td><td>70%</td><td>12 months</td></tr>
      <tr><td>Community</td><td class="mono">$0.003</td><td class="mono">1B</td><td class="mono">$3M</td><td>40%</td><td>3 months</td></tr>
      <tr><td>Presale</td><td class="mono">$0.004</td><td class="mono">2B</td><td class="mono">$8M</td><td>20%</td><td>6 months</td></tr>
      <tr><td>TGE/IDO</td><td class="mono">$0.005</td><td class="mono">0.5B</td><td class="mono">$2.5M</td><td>0%</td><td>None</td></tr>
      <tr style="border-top:2px solid #16a34a"><td><strong>Total</strong></td><td></td><td class="mono"><strong>6.5B</strong></td><td class="mono"><strong>$18M</strong></td><td></td><td></td></tr>
    </tbody>
  </table>

  <h2>Vesting Schedule</h2>
  <ul>
    <li><strong>Seed &amp; Private:</strong> 12-month cliff, then linear vesting at 125M VRDX/month</li>
    <li><strong>Community:</strong> 3-month cliff, then linear vesting</li>
    <li><strong>Presale:</strong> 6-month cliff, then linear vesting</li>
    <li><strong>Team &amp; Advisors:</strong> 12-month cliff, then 416.7M VRDX/month over 12 months</li>
    <li><strong>TGE circulating:</strong> 8B VRDX (8% of total supply)</li>
    <li><strong>Full unlock:</strong> 10-year schedule (8B &rarr; 95B)</li>
  </ul>

  <h2>Staking Economics</h2>
  <table>
    <thead><tr><th>Stake Rate</th><th>APR</th><th>Annual Rewards per 1000 VRDX</th></tr></thead>
    <tbody>
      <tr><td>30%</td><td class="mono">6.67%</td><td class="mono">66.7 VRDX</td></tr>
      <tr><td>35%</td><td class="mono">5.71%</td><td class="mono">57.1 VRDX</td></tr>
      <tr><td>40%</td><td class="mono">5.00%</td><td class="mono">50.0 VRDX</td></tr>
    </tbody>
  </table>
</div>

<!-- 11. ROADMAP -->
<div class="content page-break">
  <div class="page-header">
    <img src="data:image/png;base64,{logo_black_b64}" alt="Verdis" class="logo" style="height:24px">
    <span class="title">Whitepaper v2.0</span>
  </div>
  <h1 class="section-num">Section 11</h1>
  <h1>Roadmap</h1>

  <div class="roadmap-item">
    <div class="roadmap-phase">Phase 1 &bull; Q1 2026</div>
    <div class="roadmap-title">Genesis &amp; TGE</div>
    <div class="roadmap-desc">Mainnet genesis launch. 24.5B VRDX initial circulating supply. Team &amp; investor cliff begins.</div>
  </div>
  <div class="roadmap-item">
    <div class="roadmap-phase">Phase 2 &bull; Q2 2026</div>
    <div class="roadmap-title">DPoS Staking &amp; DEX Activation</div>
    <div class="roadmap-desc">21 active validators. 8.2B VRDX bonded in staking. AMM DEX liquidity bootstrap.</div>
  </div>
  <div class="roadmap-item">
    <div class="roadmap-phase">Phase 3 &bull; Q3 2026</div>
    <div class="roadmap-title">Eco Precompiles &amp; Presale Unlock</div>
    <div class="roadmap-desc">Carbon offset precompile activation. Presale 3-month cliff completes; linear vesting begins.</div>
  </div>
  <div class="roadmap-item">
    <div class="roadmap-phase">Phase 4 &bull; Q1 2027</div>
    <div class="roadmap-title">Seed, Private &amp; Team Cliff End</div>
    <div class="roadmap-desc">12-month cliffs end. DAO governance assumes treasury control.</div>
  </div>
  <div class="roadmap-item">
    <div class="roadmap-phase">Phase 5 &bull; 2027-2030</div>
    <div class="roadmap-title">Global Carbon Offset Scaling</div>
    <div class="roadmap-desc">10,000,000+ tCO2e verified carbon offsets retired globally.</div>
  </div>
  <div class="roadmap-item">
    <div class="roadmap-phase">Phase 6 &bull; 2030-2032</div>
    <div class="roadmap-title">AI-Powered Autonomous Governance</div>
    <div class="roadmap-desc">EvolvixOS AI analyzes proposals, simulates impact, provides recommendations. Hybrid human-AI governance.</div>
  </div>
  <div class="roadmap-item">
    <div class="roadmap-phase">Phase 7 &bull; 2030-2033</div>
    <div class="roadmap-title">Cross-Chain Carbon Credit Protocol</div>
    <div class="roadmap-desc">Carbon credits tradeable across all IBC chains. 100M+ tCO2e annual offset capacity.</div>
  </div>
  <div class="roadmap-item">
    <div class="roadmap-phase">Phase 8 &bull; 2031-2034</div>
    <div class="roadmap-title">ZK Rollup &amp; 10,000+ TPS</div>
    <div class="roadmap-desc">High-throughput microtransactions. Sub-cent fees for green micropayments.</div>
  </div>
</div>

<!-- 12. FUTURE SOLUTIONS -->
<div class="content page-break">
  <div class="page-header">
    <img src="data:image/png;base64,{logo_black_b64}" alt="Verdis" class="logo" style="height:24px">
    <span class="title">Whitepaper v2.0</span>
  </div>
  <h1 class="section-num">Section 12</h1>
  <h1>Future Solutions</h1>

  <div class="card"><h3>Decentralized Identity &amp; Green Certificates</h3><p>On-chain DID for green energy producers, reforestation projects, and carbon auditors. W3C-compliant verifiable credentials.</p></div>
  <div class="card"><h3>Layer-2 ZK Rollup Scaling</h3><p>10,000+ TPS for carbon credit micro-offsets, IoT data logging, and real-time energy trading with Layer-1 security.</p></div>
  <div class="card"><h3>AI-Powered Carbon Verification</h3><p>Satellite imagery + IoT sensors + AI analysis via EvolvixOS for autonomous reforestation verification.</p></div>
  <div class="card"><h3>Global Green Finance</h3><p>Carbon-backed stablecoins, green bonds, ESG DeFi. Partnership with Verra and Gold Standard. VRDX as global green settlement layer.</p></div>
  <div class="card"><h3>IoT &amp; Oracle Network</h3><p>Decentralized oracle nodes with IoT sensors monitoring air quality, soil health, tree growth, and energy production in real time.</p></div>
  <div class="card"><h3>Developer Ecosystem &amp; Grants</h3><p>5B VRDX grant program for third-party teams building DeFi, NFT, supply chain, and green energy apps on Verdis Chain.</p></div>
  <div class="card"><h3>Planetary Carbon Dashboard</h3><p>Real-time global carbon footprint dashboard. Every tonne of CO2 traceable from source to retirement.</p></div>
  <div class="card"><h3>Carbon-Negative Planet (2040)</h3><p>1B+ tCO2e cumulative offsets. 500+ validators in 50+ countries on 100% renewable energy. Blockchain transitions from environmental liability to solution.</p></div>
</div>

<!-- 13. TEAM -->
<div class="content page-break">
  <div class="page-header">
    <img src="data:image/png;base64,{logo_black_b64}" alt="Verdis" class="logo" style="height:24px">
    <span class="title">Whitepaper v2.0</span>
  </div>
  <h1 class="section-num">Section 13</h1>
  <h1>Team</h1>
  <div class="team-grid">
    <div class="team-card"><div class="name">Dorian Jean</div><div class="role">CEO &amp; Founder</div><div class="bio">Visionary leader driving the Verdis Chain mission to build the world's first carbon-negative blockchain.</div></div>
    <div class="team-card"><div class="name">Mark Jamestown</div><div class="role">CTO</div><div class="bio">Architect of the Substrate-based blockchain infrastructure and consensus design.</div></div>
    <div class="team-card"><div class="name">Elizabeth Jefferson</div><div class="role">Head of Product</div><div class="bio">Leads product strategy, user experience, and ecosystem integration across Verdis and EvolvixOS.</div></div>
    <div class="team-card"><div class="name">Rojs Gordons</div><div class="role">Co-Founder &amp; Community</div><div class="bio">Founder of Protremix. Leads community growth, marketing, and developer relations.</div></div>
    <div class="team-card"><div class="name">Mar&iacute;a Dolores M&aacute;rquez de Prado</div><div class="role">Legal Counsel</div><div class="bio">Legal advisor specializing in blockchain regulation, compliance, and international law.</div></div>
    <div class="team-card"><div class="name">Ignacio Mart&iacute;nez-Arrieta</div><div class="role">Legal &amp; Compliance</div><div class="bio">Compliance officer ensuring regulatory alignment across jurisdictions and tokenomics.</div></div>
  </div>
</div>

<!-- 14. CONCLUSION -->
<div class="content page-break">
  <div class="page-header">
    <img src="data:image/png;base64,{logo_black_b64}" alt="Verdis" class="logo" style="height:24px">
    <span class="title">Whitepaper v2.0</span>
  </div>
  <h1 class="section-num">Section 14</h1>
  <h1>Conclusion</h1>
  <p>Verdis Chain proves that blockchain technology can be environmentally regenerative. By embedding carbon credits, green validator scoring, and reforestation tracking directly into the consensus layer, we make sustainability a protocol-level feature rather than an afterthought.</p>
  <p>With 30+ custom pallets, native AMM DEX, ink! smart contracts, DPoS consensus, IBC cross-chain communication, and integration with the EvolvixOS AI ecosystem, Verdis Chain provides a complete platform for the next generation of green decentralized applications.</p>
  <p>The 100B VRDX token economy is designed for long-term sustainability &mdash; with 45% allocated to ecosystem and staking, 12% to investors with structured vesting, and a DAO-governed treasury ensuring community control. Every economic parameter is designed to incentivize decentralization, security, and environmental impact.</p>
  <p style="margin-top:16px;text-align:center;font-size:14px;font-weight:700;color:#16a34a;font-family:'Space Grotesk',sans-serif">This is not a promise. This is architecture.</p>

  <div style="margin-top:32px;text-align:center;border-top:1px solid #e2e8f0;padding-top:16px">
    <img src="data:image/png;base64,{logo_black_b64}" alt="Verdis Chain" style="height:32px;margin-bottom:8px">
    <p style="font-size:10px;color:#64748b;text-align:center">verdischain.com &middot; &copy; 2026 Verdis Chain &middot; Protremix &middot; MIT License</p>
  </div>
</div>

</body>
</html>"""

# Write HTML for debugging
html_path = '/tmp/whitepaper_pdf.html'
with open(html_path, 'w') as f:
    f.write(html_content)

# Generate PDF
print("Generating PDF with WeasyPrint...")
doc = HTML(string=html_content, base_url='/var/www/verdiscan/')
doc.write_pdf(OUTPUT_PDF)
print(f"PDF generated: {OUTPUT_PDF}")

# Copy to repo
import shutil
shutil.copy(OUTPUT_PDF, OUTPUT_PDF_REPO)
print(f"PDF copied to repo: {OUTPUT_PDF_REPO}")

# Check file size
size = os.path.getsize(OUTPUT_PDF)
print(f"PDF size: {size / 1024:.1f} KB")
