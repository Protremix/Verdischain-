import re

with open('/tmp/whitepaper_correct.html', 'r') as f:
    html = f.read()

# Also read the team-fixed version from the server
with open('/var/www/verdiscan/whitepaper/index.html', 'r') as f:
    html = f.read()

# Define new sections using existing CSS classes
# Each section uses .section-block, .section-header, .section-tag, .section-title, .section-desc, .card-panel, etc.

new_css = """
/* Additional whitepaper content styles */
.wp-abstract{background:linear-gradient(135deg,rgba(22,163,74,0.04),rgba(0,168,107,0.02));border:1px solid var(--accent-border);border-radius:var(--radius-lg);padding:40px;margin-bottom:48px}
.wp-abstract p{font-size:15px;color:var(--text-2);line-height:1.8;margin-bottom:16px}
.wp-abstract p:last-child{margin-bottom:0}
.wp-abstract strong{color:var(--text)}
.problem-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px}
.problem-card{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:24px;transition:all .3s}.problem-card:hover{border-color:var(--accent);box-shadow:0 0 20px var(--accent-glow)}
.problem-icon{width:44px;height:44px;border-radius:12px;background:rgba(239,68,68,0.08);display:flex;align-items:center;justify-content:center;margin-bottom:14px;font-size:20px}
.problem-title{font-family:'Space Grotesk';font-size:14px;font-weight:700;color:var(--text);margin-bottom:8px}
.problem-desc{font-size:13px;color:var(--text-2);line-height:1.6}
.solution-list{display:flex;flex-direction:column;gap:12px}
.solution-item{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:20px 24px;display:flex;gap:16px;align-items:flex-start;transition:all .3s}
.solution-item:hover{border-color:var(--accent);background:rgba(22,163,74,0.02)}
.solution-check{width:28px;height:28px;border-radius:50%;background:var(--accent);color:#fff;display:flex;align-items:center;justify-content:center;font-size:14px;flex-shrink:0;margin-top:2px}
.solution-content h4{font-family:'Space Grotesk';font-size:14px;font-weight:700;color:var(--text);margin-bottom:6px}
.solution-content p{font-size:13px;color:var(--text-2);line-height:1.6}
.feature-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}
.feature-card{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:24px;transition:all .3s}
.feature-card:hover{border-color:var(--accent);box-shadow:0 0 20px var(--accent-glow)}
.feature-icon{width:40px;height:40px;border-radius:10px;background:var(--accent-light);display:flex;align-items:center;justify-content:center;margin-bottom:12px;font-size:18px}
.feature-title{font-family:'Space Grotesk';font-size:14px;font-weight:700;color:var(--text);margin-bottom:8px}
.feature-desc{font-size:13px;color:var(--text-2);line-height:1.6}
.feature-list{list-style:none;padding:0;margin-top:12px}
.feature-list li{font-size:12px;color:var(--text-2);padding:4px 0;padding-left:18px;position:relative}
.feature-list li::before{content:'✓';color:var(--accent);font-weight:700;position:absolute;left:0}
.spec-table{width:100%;border-collapse:collapse;margin-top:16px}
.spec-table th{text-align:left;font-family:'JetBrains Mono';font-size:12px;font-weight:600;color:var(--text-3);text-transform:uppercase;letter-spacing:1px;padding:12px 16px;border-bottom:2px solid var(--border)}
.spec-table td{padding:12px 16px;font-size:13px;color:var(--text-2);border-bottom:1px solid var(--border)}
.spec-table td strong{color:var(--text)}
.spec-table td.mono{font-family:'JetBrains Mono';color:var(--accent);font-weight:600}
.phase-timeline{position:relative;padding-left:32px}
.phase-timeline::before{content:'';position:absolute;left:12px;top:0;bottom:0;width:2px;background:linear-gradient(180deg,var(--accent),transparent)}
.phase-item{position:relative;margin-bottom:24px}
.phase-dot{position:absolute;left:-26px;top:4px;width:12px;height:12px;border-radius:50%;background:var(--accent);box-shadow:0 0 8px var(--accent-glow-strong)}
.phase-dot.done{background:#4ade80;box-shadow:0 0 8px rgba(74,222,128,0.4)}
.phase-quarter{font-size:12px;font-weight:600;color:var(--accent);font-family:'JetBrains Mono';margin-bottom:4px}
.phase-title{font-size:14px;font-weight:600;color:var(--text);margin-bottom:4px}
.phase-desc{font-size:13px;color:var(--text-2);line-height:1.6}
.usecase-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px}
.usecase-card{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:24px;transition:all .3s}
.usecase-card:hover{border-color:var(--accent);transform:translateY(-2px);box-shadow:0 8px 24px rgba(0,0,0,0.06)}
.usecase-icon{width:44px;height:44px;border-radius:12px;background:var(--accent-light);display:flex;align-items:center;justify-content:center;margin-bottom:14px;font-size:20px}
.usecase-title{font-family:'Space Grotesk';font-size:14px;font-weight:700;color:var(--text);margin-bottom:8px}
.usecase-desc{font-size:13px;color:var(--text-2);line-height:1.6}
.conclusion-box{background:linear-gradient(135deg,rgba(22,163,74,0.06),rgba(0,168,107,0.03));border:1px solid var(--accent-border);border-radius:var(--radius-lg);padding:40px;text-align:center;margin-bottom:48px}
.conclusion-box h2{font-family:'Space Grotesk';font-size:18px;font-weight:700;color:var(--text);margin-bottom:16px}
.conclusion-box p{font-size:14px;color:var(--text-2);line-height:1.8;max-width:720px;margin:0 auto 16px}
"""

# Insert new CSS before </style>
html = html.replace('</style>', new_css + '\n</style>', 1)

# 1. Executive Summary — insert right after the hero section, before "Our Story"
exec_summary = """
<!-- Executive Summary -->
<div class="section-block reveal" id="abstract">
<div class="wp-abstract">
<h3 style="font-family:'Space Grotesk';font-size:16px;font-weight:700;color:var(--text);margin-bottom:20px">Executive Summary</h3>
<p><strong>Verdis Chain</strong> is a carbon-negative Layer-1 blockchain built on Substrate, powered by native Delegated Proof-of-Stake (DPoS) consensus, an integrated AMM decentralized exchange (DEX), ink! smart contracts, and on-chain carbon credit tracking. The protocol is designed to prove that blockchain infrastructure can be environmentally regenerative rather than destructive.</p>
<p>The native token, <strong>VRDX</strong>, has a fixed supply of <strong>100 billion</strong> with <strong>9 decimals</strong>, serving as the gas token, staking asset, governance instrument, and medium of exchange across the ecosystem. VRDX is not an ERC-20 wrapper — it is woven into the consensus layer itself.</p>
<p>Verdis Chain connects to <strong>EvolvixOS</strong>, an AI Engineering Operating System that provides smart contract auditing, AI-powered development tools, and a plugin marketplace. Together, they form a complete green technology stack: blockchain provides trust and value transfer, AI provides intelligence and automation.</p>
<p>The protocol features <strong>30+ custom Substrate pallets</strong>, including DPoS consensus with 21 target validators, an AMM DEX with 6 liquidity pools, carbon credit minting and retirement, green validator scoring, reforestation logging, governance, IBC cross-chain communication, and Solana-inspired innovations (Gulf Stream, Turbine, Sealevel execution, ZK compression).</p>
</div>
</div>
"""

# Insert before "Our Story" section
story_marker = '<!-- Our Story -->'
if story_marker not in html:
    story_marker = '<div class="section-block reveal" id="story">'
html = html.replace(story_marker, exec_summary + '\n' + story_marker, 1)

# 2. Problem Statement — insert after Executive Summary, before Our Story
problem_section = """
<!-- Problem Statement -->
<div class="section-block reveal" id="problem">
<div class="section-header"><span class="section-tag">The Challenge</span><h2 class="section-title">The Problem We're Solving</h2><p class="section-desc">The blockchain industry faces three fundamental crises: environmental destruction, economic centralization, and technical fragmentation. Verdis Chain was built to address all three.</p></div>
<div class="problem-grid">
<div class="problem-card">
<div class="problem-icon">⚡</div>
<div class="problem-title">Energy Consumption Crisis</div>
<div class="problem-desc">Bitcoin and Ethereum combined consume more electricity than entire nations. Proof-of-Work mining produces 50+ million tonnes of CO2 annually, making blockchain one of the most environmentally destructive technologies ever created. No major chain has a credible path to carbon negativity.</div>
</div>
<div class="problem-card">
<div class="problem-icon">🔧</div>
<div class="problem-title">Validator Centralization</div>
<div class="problem-desc">Most DPoS and PoS networks concentrate power among a small number of institutional validators. Lisk had 101, EOS had 21 block producers. Without green energy incentives and decentralization mandates, networks become oligarchies that prioritize profit over security and sustainability.</div>
</div>
<div class="problem-card">
<div class="problem-icon">⛓️</div>
<div class="problem-title">Fragmented Ecosystems</div>
<div class="problem-desc">Blockchain, AI, and traditional fintech operate in silos. Developers must stitch together multiple chains, bridges, AI APIs, and payment systems with no unified standard. This creates friction, security risks, and poor developer experience.</div>
</div>
<div class="problem-card">
<div class="problem-icon">📊</div>
<div class="problem-title">Opaque Carbon Markets</div>
<div class="problem-desc">Voluntary carbon credit markets suffer from double-counting, lack of transparency, and no real-time verification. Projects cannot prove their environmental impact. Buyers cannot trust that credits represent genuine carbon offsets.</div>
</div>
<div class="problem-card">
<div class="problem-icon">🏦</div>
<div class="problem-title">DEX Security Vulnerabilities</div>
<div class="problem-desc">Existing AMM DEX implementations have suffered from reentrancy attacks, overflow/underflow exploits, and LP token manipulation. Many DEX protocols are built as smart contracts on top of chains rather than as native pallets, adding layers of risk.</div>
</div>
<div class="problem-card">
<div class="problem-icon">🤝</div>
<div class="problem-title">Lack of Green Incentives</div>
<div class="problem-desc">No major blockchain rewards validators for using renewable energy. There is no on-chain mechanism to verify, score, or incentivize green operations. The industry talks about sustainability but has no economic model to enforce it.</div>
</div>
</div>
</div>
"""

html = html.replace(exec_summary + '\n' + story_marker, exec_summary + '\n' + problem_section + '\n' + story_marker, 1)

# 3. Solution Overview — insert after Problem Statement
solution_section = """
<!-- Solution Overview -->
<div class="section-block reveal" id="solution">
<div class="section-header"><span class="section-tag">Our Answer</span><h2 class="section-title">The Verdis Solution</h2><p class="section-desc">Verdis Chain addresses each problem with a purpose-built, native-layer solution — not a patch or a smart contract overlay.</p></div>
<div class="solution-list">
<div class="solution-item">
<div class="solution-check">✓</div>
<div class="solution-content">
<h4>Carbon-Native Blockchain Architecture</h4>
<p>Carbon credit minting, retirement, and verification are built directly into the protocol as native pallets — not as ERC-20 tokens or external oracles. Every transaction contributes to carbon offsetting through a 20% fee auto-retire mechanism. The chain is designed to be carbon-negative by architecture, not by offset purchases.</p>
</div>
</div>
<div class="solution-item">
<div class="solution-check">✓</div>
<div class="solution-content">
<h4>DPoS with Green Validator Scoring</h4>
<p>Validators are incentivized to operate on 100% renewable energy through on-chain green scoring. Green validators earn a +2.5% APY bonus yield. The protocol targets 21 active validators with geographic diversity, preventing the centralization seen in networks with fewer, larger validators.</p>
</div>
</div>
<div class="solution-item">
<div class="solution-check">✓</div>
<div class="solution-content">
<h4>Native AMM DEX (Not a Smart Contract)</h4>
<p>The DEX is implemented as a Substrate pallet, not an ink!/Solidity contract. This eliminates reentrancy risks, reduces gas costs, and provides overflow-safe arithmetic with checked_mul/checked_add operations. 6 liquidity pools are seeded and operational on testnet.</p>
</div>
</div>
<div class="solution-item">
<div class="solution-check">✓</div>
<div class="solution-content">
<h4>Unified Ecosystem with EvolvixOS</h4>
<p>Verdis Chain and EvolvixOS are designed as a single ecosystem. Blockchain provides trust and value transfer; AI provides intelligence, smart contract auditing, and development tools. Developers build once and deploy across both platforms.</p>
</div>
</div>
<div class="solution-item">
<div class="solution-check">✓</div>
<div class="solution-content">
<h4>Transparent On-Chain Carbon Credits</h4>
<p>Every carbon credit is minted on-chain with verifiable provenance. Retirements are public and immutable. 1 tCO2e = 100 Eco-Credits. Double-counting is impossible by protocol design. Reforestation projects are logged with GPS coordinates and verification metadata.</p>
</div>
</div>
<div class="solution-item">
<div class="solution-check">✓</div>
<div class="solution-content">
<h4>Solana-Inspired Performance Innovations</h4>
<p>Gulf Stream transaction forwarding, Turbine block propagation, Sealevel parallel execution, ZK compression, and Account Lookup Tables (ALT) are implemented as native pallets — bringing high-throughput architecture to the Substrate ecosystem without compromising on decentralization.</p>
</div>
</div>
</div>
</div>
"""

html = html.replace(problem_section + '\n' + story_marker, problem_section + '\n' + solution_section + '\n' + story_marker, 1)

# 4. Consensus Mechanism — insert after Technical Architecture section
# Find the "Connection to EvolvixOS" section and insert before it
evo_marker = '<div class="section-block reveal" id="evo">'
if evo_marker not in html:
    evo_marker = '<!-- EvolvixOS -->'
if evo_marker not in html:
    # Try to find it by section tag
    evo_marker = '<div class="section-header"><span class="section-tag">Ecosystem</span>'

consensus_section = """
<!-- Consensus Mechanism -->
<div class="section-block reveal" id="consensus">
<div class="section-header"><span class="section-tag">Consensus</span><h2 class="section-title">DPoS Consensus & Block Production</h2><p class="section-desc">Verdis Chain uses Delegated Proof-of-Stake (DPoS) with BABE/GRANDPA finality — combining fast block production with provable deterministic finality.</p></div>
<div class="card-panel">
<h3 style="font-family:'Space Grotesk';font-size:14px;font-weight:700;color:#0f172a;margin-bottom:16px">How DPoS Works on Verdis Chain</h3>
<p style="font-size:14px;color:var(--text-2);line-height:1.8;margin-bottom:16px">VRDX holders delegate their tokens to validators. The top 21 validators by delegated stake are selected as active block producers each epoch. Validators produce blocks using BABE (Blind Assignment for Blockchain Extension), while GRANDPA provides deterministic finality — once a block is finalized by GRANDPA, it cannot be reverted.</p>
<table class="spec-table">
<tr><th>Parameter</th><th>Value</th><th>Description</th></tr>
<tr><td><strong>Consensus Engine</strong></td><td class="mono">BABE + GRANDPA</td><td>Block production + finality gadget</td></tr>
<tr><td><strong>Active Validators</strong></td><td class="mono">21</td><td>Target validator set size</td></tr>
<tr><td><strong>Epoch Duration</strong></td><td class="mono">1,200 blocks</td><td>Validator set rotation period</td></tr>
<tr><td><strong>Session Period</strong></td><td class="mono">50 blocks</td><td>Session key rotation interval</td></tr>
<tr><td><strong>Finality</strong></td><td class="mono">Deterministic</td><td>GRANDPA BFT finality gadget</td></tr>
<tr><td><strong>Block Time</strong></td><td class="mono">~6 seconds</td><td>Target block production interval</td></tr>
<tr><td><strong>Slashing</strong></td><td class="mono">Enabled</td><td>Penalties for equivocation and downtime</td></tr>
<tr><td><strong>Green Validator Bonus</strong></td><td class="mono">+2.5% APY</td><td>Additional yield for renewable energy validators</td></tr>
</table>
</div>
<div class="feature-grid" style="margin-top:16px">
<div class="feature-card">
<div class="feature-icon">🔄</div>
<div class="feature-title">BABE Block Production</div>
<div class="feature-desc">VRF-based slot assignment ensures fair, unpredictable block production. Each validator gets assigned slots based on their stake ratio, with a randomness beacon preventing predictability.</div>
</div>
<div class="feature-card">
<div class="feature-icon">⚡</div>
<div class="feature-title">GRANDPA Finality</div>
<div class="feature-desc">BFT finality gadget that finalizes blocks in batches rather than one-by-one. Provides sub-second finality under normal conditions and survives network partitions.</div>
</div>
<div class="feature-card">
<div class="feature-icon">🌱</div>
<div class="feature-title">Green Scoring</div>
<div class="feature-desc">On-chain green score (0-5) assigned to validators based on verified renewable energy usage. Higher scores earn additional staking yield and priority for ecosystem grants.</div>
</div>
<div class="feature-card">
<div class="feature-icon">⚔️</div>
<div class="feature-title">Slashing</div>
<div class="feature-desc">Validators who equivocate (double-sign) or go offline are slashed. Slashed amounts are proportional to severity, with the slashed tokens burned or sent to treasury.</div>
</div>
</div>
</div>
"""

html = html.replace(evo_marker, consensus_section + '\n' + evo_marker, 1)

# 5. Smart Contracts — insert after Consensus
smart_contracts = """
<!-- Smart Contracts -->
<div class="section-block reveal" id="smart-contracts">
<div class="section-header"><span class="section-tag">Programmability</span><h2 class="section-title">Smart Contracts & Developer Platform</h2><p class="section-desc">Verdis Chain supports ink! smart contracts — Rust-based, WebAssembly-compiled contracts that inherit the safety guarantees of the Rust type system.</p></div>
<div class="card-panel">
<h3 style="font-family:'Space Grotesk';font-size:14px;font-weight:700;color:#0f172a;margin-bottom:16px">ink! Smart Contract Platform</h3>
<p style="font-size:14px;color:var(--text-2);line-height:1.8;margin-bottom:16px">Smart contracts on Verdis Chain are written in <strong>ink!</strong>, a Rust-based embedded domain language. Unlike Solidity, ink! leverages Rust's ownership model and type safety to prevent entire classes of vulnerabilities — reentrancy, integer overflow, and memory safety issues are caught at compile time.</p>
<ul class="feature-list" style="margin-bottom:0">
<li>Compiled to WebAssembly — portable, efficient, and sandboxed</li>
<li>Rust type safety prevents buffer overflows and null pointer dereferences</li>
<li>Contract storage is automatically managed with type-safe mapping</li>
<li>Events and errors are first-class citizens with strongly-typed definitions</li>
<li>Cross-contract calls are type-checked at compile time</li>
<li>Integrated with the EvolvixOS AI auditing platform for automated security review</li>
</ul>
</div>
<div class="feature-grid" style="margin-top:16px">
<div class="feature-card">
<div class="feature-icon">🦀</div>
<div class="feature-title">Rust + WASM</div>
<div class="feature-desc">Contracts compile to WebAssembly, providing near-native execution speed and cross-platform portability. Rust's zero-cost abstractions keep gas costs minimal.</div>
</div>
<div class="feature-card">
<div class="feature-icon">🔐</div>
<div class="feature-title">AI-Powered Auditing</div>
<div class="feature-desc">EvolvixOS provides automated smart contract auditing. AI models analyze contract code for common vulnerability patterns, gas optimization opportunities, and best practice violations.</div>
</div>
<div class="feature-card">
<div class="feature-icon">📦</div>
<div class="feature-title">Developer SDK</div>
<div class="feature-desc">JavaScript SDK with 51 methods, native WebSocket support, and zero external dependencies. Deploy contracts, query state, and sign transactions programmatically.</div>
</div>
<div class="feature-card">
<div class="feature-icon">🧪</div>
<div class="feature-title">Testnet Environment</div>
<div class="feature-desc">Full testnet with faucet, block explorer, and documentation. Deploy and test contracts before mainnet launch with real consensus and real DEX pools.</div>
</div>
</div>
</div>
"""

html = html.replace(evo_marker, smart_contracts + '\n' + evo_marker, 1)

# 6. AMM DEX — insert after Smart Contracts
dex_section = """
<!-- AMM DEX -->
<div class="section-block reveal" id="dex">
<div class="section-header"><span class="section-tag">Decentralized Exchange</span><h2 class="section-title">Native AMM DEX Architecture</h2><p class="section-desc">The Verdis DEX is a native Substrate pallet — not a smart contract. This eliminates reentrancy risks, reduces execution overhead, and provides overflow-safe arithmetic at the protocol level.</p></div>
<div class="card-panel">
<h3 style="font-family:'Space Grotesk';font-size:14px;font-weight:700;color:#0f172a;margin-bottom:16px">How the Native DEX Works</h3>
<p style="font-size:14px;color:var(--text-2);line-height:1.8;margin-bottom:16px">The DEX uses the constant product formula (x × y = k) popularized by Uniswap, but implemented as a native pallet with checked arithmetic. Every swap, liquidity addition, and removal uses <strong>checked_mul</strong> and <strong>checked_add</strong> operations — if any calculation would overflow, the transaction reverts with an error rather than wrapping around.</p>
<table class="spec-table">
<tr><th>Feature</th><th>Implementation</th><th>Security</th></tr>
<tr><td><strong>AMM Formula</strong></td><td class="mono">x × y = k</td><td>Constant product invariant</td></tr>
<tr><td><strong>Swap Fee</strong></td><td class="mono">0.3%</td><td>Standard AMM fee tier</td></tr>
<tr><td><strong>Arithmetic</strong></td><td class="mono">checked_mul / checked_add</td><td>No overflow/underflow possible</td></tr>
<tr><td><strong>Self-Transfer Guard</strong></td><td class="mono">Prevented</td><td>Cannot swap token for itself</td></tr>
<tr><td><strong>Pool Bricking</strong></td><td class="mono">Prevented</td><td>Zero-reserve pools are rejected</td></tr>
<tr><td><strong>Deadline Protection</strong></td><td class="mono">Mandatory</td><td>All swaps include deadline parameter</td></tr>
<tr><td><strong>Active Pools</strong></td><td class="mono">6 (testnet)</td><td>VRDX/ECO, VRDX/CARBON, VRDX/TREE, VRDX/GREEN, ECO/CARBON, VRDX/REDD</td></tr>
</table>
</div>
<div class="feature-grid" style="margin-top:16px">
<div class="feature-card">
<div class="feature-icon">💧</div>
<div class="feature-title">Liquidity Provision</div>
<div class="feature-desc">Anyone can create a liquidity pool by providing equal-value deposits of two tokens. LP tokens represent proportional ownership of the pool and can be withdrawn at any time.</div>
</div>
<div class="feature-card">
<div class="feature-icon">🔄</div>
<div class="feature-title">Token Swaps</div>
<div class="feature-desc">Instant token swaps with 0.3% fee distributed to liquidity providers. Slippage protection via deadline parameters. All swaps execute atomically — partial fills are not possible.</div>
</div>
<div class="feature-card">
<div class="feature-icon">🛡️</div>
<div class="feature-title">Overflow Protection</div>
<div class="feature-desc">Every arithmetic operation uses checked math. If a swap result would exceed u128 maximum, the transaction fails cleanly rather than wrapping to a tiny number.</div>
</div>
<div class="feature-card">
<div class="feature-icon">📊</div>
<div class="feature-title">On-Chain Pricing</div>
<div class="feature-desc">Pool reserves serve as a decentralized price oracle. The DEX can be queried by other pallets for token pricing, enabling collateralized lending and other DeFi applications.</div>
</div>
</div>
</div>
"""

html = html.replace(evo_marker, dex_section + '\n' + evo_marker, 1)

# 7. Governance — insert after "What Our Ecosystem Means"
ecosystem_marker = '<div class="section-block reveal" id="improve">'
if ecosystem_marker not in html:
    ecosystem_marker = '<!-- Improvement -->'
if ecosystem_marker not in html:
    ecosystem_marker = '<div class="section-header"><span class="section-tag">Roadmap</span><h2 class="section-title">How We Will Improve'

governance_section = """
<!-- Governance -->
<div class="section-block reveal" id="governance">
<div class="section-header"><span class="section-tag">Governance</span><h2 class="section-title">Decentralized Governance Model</h2><p class="section-desc">VRDX holders govern the protocol through on-chain democracy. The governance system manages treasury allocations, runtime upgrades, and protocol parameters.</p></div>
<div class="feature-grid">
<div class="feature-card">
<div class="feature-icon">🗳️</div>
<div class="feature-title">Democracy</div>
<div class="feature-desc">Any VRDX holder can propose a referendum. Proposals are voted on by token-weighted quadratic voting. Approved proposals are automatically executed after an enactment delay.</div>
<ul class="feature-list">
<li>Proposal submission requires token lock</li>
<li>Quadratic voting reduces whale influence</li>
<li>Enactment delay for safety review</li>
</ul>
</div>
<div class="feature-card">
<div class="feature-icon">🏛️</div>
<div class="feature-title">Council</div>
<div class="feature-desc">An elected council of 8 members fast-tracks proposals and manages emergency actions. Council members are elected by VRDX holders and can be removed via no-confidence vote.</div>
<ul class="feature-list">
<li>8 council members (expandable)</li>
<li>Fast-track for urgent protocol fixes</li>
<li>Removable via no-confidence vote</li>
</ul>
</div>
<div class="feature-card">
<div class="feature-icon">💰</div>
<div class="feature-title">Treasury</div>
<div class="feature-desc">15B VRDX is allocated to the treasury, controlled by governance. Funds are spent on ecosystem grants, developer bounties, infrastructure, and carbon offset initiatives.</div>
<ul class="feature-list">
<li>15,000,000,000 VRDX allocated</li>
<li>DAO-governed spending</li>
<li>Transparent on-chain accounting</li>
</ul>
</div>
<div class="feature-card">
<div class="feature-icon">🔒</div>
<div class="feature-title">Technical Committee</div>
<div class="feature-desc">A technical committee of core developers can veto emergency proposals that would harm the protocol. This provides a safety net against malicious governance attacks.</div>
<ul class="feature-list">
<li>Emergency veto power</li>
<li>Composed of core protocol developers</li>
<li>Prevents harmful governance captures</li>
</ul>
</div>
</div>
</div>
"""

html = html.replace(ecosystem_marker, governance_section + '\n' + ecosystem_marker, 1)

# 8. Security Model — insert after Governance
security_section = """
<!-- Security Model -->
<div class="section-block reveal" id="security">
<div class="section-header"><span class="section-tag">Security</span><h2 class="section-title">Security Architecture</h2><p class="section-desc">Security is the foundational design principle of Verdis Chain. Every pallet, every extrinsic, and every storage item is built with defense-in-depth.</p></div>
<div class="card-panel">
<h3 style="font-family:'Space Grotesk';font-size:14px;font-weight:700;color:#0f172a;margin-bottom:16px">Security Principles</h3>
<div class="solution-list">
<div class="solution-item">
<div class="solution-check">🔒</div>
<div class="solution-content">
<h4>No Custodial Keys</h4>
<p>The protocol never stores user private keys. All transactions are signed on the user's device (wallet). The TX Relay service only relays pre-signed extrinsics — it cannot sign on behalf of users.</p>
</div>
</div>
<div class="solution-item">
<div class="solution-check">🛡️</div>
<div class="solution-content">
<h4>Bounded Inputs</h4>
<p>All extrinsic parameters use bounded Vec&lt;u8&gt; with length checks (32-128 bytes). This prevents storage DoS attacks where an attacker could submit unbounded data to exhaust chain storage.</p>
</div>
</div>
<div class="solution-item">
<div class="solution-check">⚡</div>
<div class="solution-content">
<h4>Safe Integer Casts</h4>
<p>All integer conversions use try_from instead of unsafe as casts. This prevents silent truncation bugs that could corrupt balances or staking calculations.</p>
</div>
</div>
<div class="solution-item">
<div class="solution-check">🔐</div>
<div class="solution-content">
<h4>Checked Arithmetic</h4>
<p>The DEX uses checked_mul and checked_add for all swap calculations. Overflow/underflow is impossible — transactions fail cleanly rather than wrapping around to incorrect values.</p>
</div>
</div>
<div class="solution-item">
<div class="solution-check">👤</div>
<div class="solution-content">
<h4>Authorization Checks</h4>
<p>Green score updates require root authorization (validators cannot self-score). Carbon credit minting requires verified authority. Reforestation project creation requires admin approval.</p>
</div>
</div>
<div class="solution-item">
<div class="solution-check">🔑</div>
<div class="solution-content">
<h4>Air-Gapped Key Generation</h4>
<p>Production validator keys must be generated on air-gapped machines. No hardcoded private keys, no server-side custody, no hidden privileged backdoors, no undocumented founder controls.</p>
</div>
</div>
</div>
</div>
</div>
"""

html = html.replace(ecosystem_marker, security_section + '\n' + ecosystem_marker, 1)

# 9. Use Cases — insert after Security Model
usecases_section = """
<!-- Use Cases -->
<div class="section-block reveal" id="use-cases">
<div class="section-header"><span class="section-tag">Applications</span><h2 class="section-title">Real-World Use Cases</h2><p class="section-desc">Verdis Chain is designed for real-world environmental, financial, and developer applications — not just speculation.</p></div>
<div class="usecase-grid">
<div class="usecase-card">
<div class="usecase-icon">🌱</div>
<div class="usecase-title">Carbon Credit Trading</div>
<div class="usecase-desc">Companies buy and retire on-chain carbon credits with full provenance tracking. Each credit represents 1 tCO2e of verified offset. Retirements are public, immutable, and auditable.</div>
</div>
<div class="usecase-card">
<div class="usecase-icon">🌳</div>
<div class="usecase-title">Reforestation Funding</div>
<div class="usecase-desc">Reforestation projects register on-chain with GPS coordinates and verification metadata. Donors fund projects directly. Progress is tracked transparently with milestone-based fund releases.</div>
</div>
<div class="usecase-card">
<div class="usecase-icon">⚡</div>
<div class="usecase-title">Green Energy Certification</div>
<div class="usecase-desc">Validators prove renewable energy usage and earn green scores. Energy providers can certify green energy production on-chain, creating a verifiable renewable energy certificate (REC) market.</div>
</div>
<div class="usecase-card">
<div class="usecase-icon">🔄</div>
<div class="usecase-title">Decentralized Trading</div>
<div class="usecase-desc">The native AMM DEX enables permissionless token trading. Projects can create liquidity pools for their ecosystem tokens, providing instant liquidity without centralized exchanges.</div>
</div>
<div class="usecase-card">
<div class="usecase-icon">🤖</div>
<div class="usecase-title">AI-Powered Development</div>
<div class="usecase-desc">Through EvolvixOS, developers use AI to audit smart contracts, generate boilerplate, and optimize gas. AI tools analyze on-chain data for security insights and protocol health monitoring.</div>
</div>
<div class="usecase-card">
<div class="usecase-icon">🏦</div>
<div class="usecase-title">DeFi Applications</div>
<div class="usecase-desc">The DEX serves as a price oracle for lending protocols. Staking derivatives, yield aggregation, and carbon-backed stablecoins can be built on top of the native pallet infrastructure.</div>
</div>
<div class="usecase-card">
<div class="usecase-icon">📡</div>
<div class="usecase-title">Cross-Chain Bridges</div>
<div class="usecase-desc">IBC protocol enables trust-minimized bridges to other chains. VRDX can be transferred to Polkadot parachains, Ethereum, and other IBC-enabled networks.</div>
</div>
<div class="usecase-card">
<div class="usecase-icon">📋</div>
<div class="usecase-title">Supply Chain Tracking</div>
<div class="usecase-desc">Green supply chains track products from origin to consumer. Each step is recorded on-chain with timestamp, location, and certification data — preventing greenwashing and fraud.</div>
</div>
</div>
</div>
"""

html = html.replace(ecosystem_marker, usecases_section + '\n' + ecosystem_marker, 1)

# 10. Conclusion — insert before the CTA/footer section
# Find the CTA section
cta_marker = '<h2>Join the Green Blockchain Revolution</h2>'
if cta_marker not in html:
    cta_marker = '<!-- CTA -->'
if cta_marker not in html:
    # Try to find the section before footer
    cta_marker = '<div class="section-block reveal" id="cta">'
if cta_marker not in html:
    # Try another approach — find the roadmap section end
    cta_marker = '<!-- Token Release Roadmap -->'
    if cta_marker in html:
        # Find end of that section
        pos = html.find(cta_marker)
        # Find the closing </div> of the section-block
        depth = 0
        i = pos
        while i < len(html):
            if html[i:i+5] == '<div ':
                depth += 1
            elif html[i:i+6] == '</div>':
                depth -= 1
                if depth == 0:
                    cta_marker = html[pos:i+6]
                    break
            i += 1

conclusion_section = """
<!-- Conclusion -->
<div class="section-block reveal" id="conclusion">
<div class="conclusion-box">
<h2>Conclusion: Building the Green Standard</h2>
<p>Verdis Chain proves that blockchain technology can be environmentally regenerative. By embedding carbon credits, green validator scoring, and reforestation tracking directly into the consensus layer, we make sustainability a protocol-level feature rather than an afterthought.</p>
<p>With 30+ custom pallets, native AMM DEX, ink! smart contracts, DPoS consensus, IBC cross-chain communication, and integration with the EvolvixOS AI ecosystem, Verdis Chain provides a complete platform for the next generation of green decentralized applications.</p>
<p>The 100B VRDX token economy is designed for long-term sustainability — with 45% allocated to ecosystem and staking, 12% to investors with structured vesting, and a DAO-governed treasury ensuring community control. Every economic parameter is designed to incentivize decentralization, security, and environmental impact.</p>
<p><strong>This is not a promise. This is architecture.</strong></p>
</div>
</div>
"""

# Insert conclusion before CTA
if '<h2>Join the Green Blockchain Revolution</h2>' in html:
    html = html.replace('<h2>Join the Green Blockchain Revolution</h2>', conclusion_section + '\n<h2>Join the Green Blockchain Revolution</h2>', 1)
else:
    # Insert before the roadmap section's closing or before footer
    footer_pos = html.find('<footer')
    if footer_pos > 0:
        html = html[:footer_pos] + conclusion_section + '\n' + html[footer_pos:]

# Write to server and git
with open('/var/www/verdiscan/whitepaper/index.html', 'w') as f:
    f.write(html)
with open('/opt/verdis-chain-rust/web/whitepaper/index.html', 'w') as f:
    f.write(html)

# Verify
with open('/var/www/verdiscan/whitepaper/index.html', 'r') as f:
    content = f.read()

checks = [
    ('Executive Summary' in content, 'Executive Summary'),
    ('The Problem We' in content, 'Problem Statement'),
    ('The Verdis Solution' in content, 'Solution Overview'),
    ('DPoS Consensus & Block Production' in content, 'Consensus Mechanism'),
    ('ink! Smart Contract Platform' in content, 'Smart Contracts'),
    ('Native AMM DEX Architecture' in content, 'DEX Architecture'),
    ('Decentralized Governance Model' in content, 'Governance'),
    ('Security Architecture' in content, 'Security Model'),
    ('Real-World Use Cases' in content, 'Use Cases'),
    ('Building the Green Standard' in content, 'Conclusion'),
    ('Dorian Jean' in content, 'Dorian Jean team'),
    ('Rojs Gordons' in content, 'Rojs Gordons team'),
    ('Inter' in content, 'Inter font'),
    ('#16a34a' in content, 'Correct green'),
    ('caff33' not in content, 'No neon green'),
    ('100,000,000,000' in content or '100B' in content, '100B supply'),
    ('9' in content and 'Decimals' in content, '9 decimals'),
]
for ok, label in checks:
    print(f'{"OK" if ok else "FAIL"}: {label}')

print(f'\nTotal size: {len(content)} bytes ({content.count(chr(10))} lines)')
print(f'Sections found: {content.count("section-block")}')
