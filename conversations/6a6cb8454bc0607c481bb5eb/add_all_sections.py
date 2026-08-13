import re

with open('/var/www/verdiscan/whitepaper/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Additional CSS
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
.feature-list li::before{content:'\\2713';color:var(--accent);font-weight:700;position:absolute;left:0}
.spec-table{width:100%;border-collapse:collapse;margin-top:16px}
.spec-table th{text-align:left;font-family:'JetBrains Mono';font-size:12px;font-weight:600;color:var(--text-3);text-transform:uppercase;letter-spacing:1px;padding:12px 16px;border-bottom:2px solid var(--border)}
.spec-table td{padding:12px 16px;font-size:13px;color:var(--text-2);border-bottom:1px solid var(--border)}
.spec-table td strong{color:var(--text)}
.spec-table td.mono{font-family:'JetBrains Mono';color:var(--accent);font-weight:600}
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

# Insert CSS before </style>
html = html.replace('</style>', new_css + '\n</style>', 1)

# Find insertion points
# Consensus/Smart Contracts/DEX go before the EvolvixOS section
evo_pos = html.find('id="evo"')
if evo_pos == -1:
    evo_pos = html.find('Ecosystem</span>')
if evo_pos == -1:
    evo_pos = html.find('Connection to EvolvixOS')
evo_pos = html.rfind('<section', 0, evo_pos) if evo_pos > 0 else -1
# Try another marker
if evo_pos == -1:
    evo_pos = html.find('class="evo-grid"')
    if evo_pos > 0:
        evo_pos = html.rfind('<section', 0, evo_pos)

print(f'Evo section at: {evo_pos}')

# Governance/Security/UseCases go before the improvement section
improve_pos = html.find('id="improve"')
if improve_pos == -1:
    improve_pos = html.find('How We Will Improve')
if improve_pos > 0:
    improve_pos = html.rfind('<section', 0, improve_pos)
else:
    improve_pos = html.find('class="improve-list"')
    if improve_pos > 0:
        improve_pos = html.rfind('<section', 0, improve_pos)

print(f'Improve section at: {improve_pos}')

# CTA/conclusion goes before footer or CTA
footer_pos = html.find('<footer')
if footer_pos == -1:
    footer_pos = html.find('Join the Green Blockchain Revolution')
    if footer_pos > 0:
        footer_pos = html.rfind('<section', 0, footer_pos)

print(f'Footer/CTA at: {footer_pos}')

# Build sections using HTML entities for emojis
consensus_section = """
<!-- Consensus Mechanism -->
<section class="section-block reveal" id="consensus">
<div class="section-header"><span class="section-tag">Consensus</span><h2 class="section-title">DPoS Consensus &amp; Block Production</h2><p class="section-desc">Verdis Chain uses Delegated Proof-of-Stake (DPoS) with BABE/GRANDPA finality &mdash; combining fast block production with provable deterministic finality.</p></div>
<div class="card-panel">
<h3 style="font-family:'Space Grotesk';font-size:14px;font-weight:700;color:#0f172a;margin-bottom:16px">How DPoS Works on Verdis Chain</h3>
<p style="font-size:14px;color:var(--text-2);line-height:1.8;margin-bottom:16px">VRDX holders delegate their tokens to validators. The top 21 validators by delegated stake are selected as active block producers each epoch. Validators produce blocks using BABE (Blind Assignment for Blockchain Extension), while GRANDPA provides deterministic finality &mdash; once a block is finalized by GRANDPA, it cannot be reverted.</p>
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
<div class="feature-card"><div class="feature-icon">&#9851;</div><div class="feature-title">BABE Block Production</div><div class="feature-desc">VRF-based slot assignment ensures fair, unpredictable block production. Each validator gets assigned slots based on their stake ratio, with a randomness beacon preventing predictability.</div></div>
<div class="feature-card"><div class="feature-icon">&#9889;</div><div class="feature-title">GRANDPA Finality</div><div class="feature-desc">BFT finality gadget that finalizes blocks in batches rather than one-by-one. Provides sub-second finality under normal conditions and survives network partitions.</div></div>
<div class="feature-card"><div class="feature-icon">&#127793;</div><div class="feature-title">Green Scoring</div><div class="feature-desc">On-chain green score (0-5) assigned to validators based on verified renewable energy usage. Higher scores earn additional staking yield and priority for ecosystem grants.</div></div>
<div class="feature-card"><div class="feature-icon">&#9876;</div><div class="feature-title">Slashing</div><div class="feature-desc">Validators who equivocate (double-sign) or go offline are slashed. Slashed amounts are proportional to severity, with the slashed tokens burned or sent to treasury.</div></div>
</div>
</section>

<!-- Smart Contracts -->
<section class="section-block reveal" id="smart-contracts">
<div class="section-header"><span class="section-tag">Programmability</span><h2 class="section-title">Smart Contracts &amp; Developer Platform</h2><p class="section-desc">Verdis Chain supports ink! smart contracts &mdash; Rust-based, WebAssembly-compiled contracts that inherit the safety guarantees of the Rust type system.</p></div>
<div class="card-panel">
<h3 style="font-family:'Space Grotesk';font-size:14px;font-weight:700;color:#0f172a;margin-bottom:16px">ink! Smart Contract Platform</h3>
<p style="font-size:14px;color:var(--text-2);line-height:1.8;margin-bottom:16px">Smart contracts on Verdis Chain are written in <strong>ink!</strong>, a Rust-based embedded domain language. Unlike Solidity, ink! leverages Rust's ownership model and type safety to prevent entire classes of vulnerabilities &mdash; reentrancy, integer overflow, and memory safety issues are caught at compile time.</p>
<ul class="feature-list" style="margin-bottom:0">
<li>Compiled to WebAssembly &mdash; portable, efficient, and sandboxed</li>
<li>Rust type safety prevents buffer overflows and null pointer dereferences</li>
<li>Contract storage is automatically managed with type-safe mapping</li>
<li>Events and errors are first-class citizens with strongly-typed definitions</li>
<li>Cross-contract calls are type-checked at compile time</li>
<li>Integrated with the EvolvixOS AI auditing platform for automated security review</li>
</ul>
</div>
<div class="feature-grid" style="margin-top:16px">
<div class="feature-card"><div class="feature-icon">&#128013;</div><div class="feature-title">Rust + WASM</div><div class="feature-desc">Contracts compile to WebAssembly, providing near-native execution speed and cross-platform portability. Rust's zero-cost abstractions keep gas costs minimal.</div></div>
<div class="feature-card"><div class="feature-icon">&#128274;</div><div class="feature-title">AI-Powered Auditing</div><div class="feature-desc">EvolvixOS provides automated smart contract auditing. AI models analyze contract code for common vulnerability patterns, gas optimization opportunities, and best practice violations.</div></div>
<div class="feature-card"><div class="feature-icon">&#128230;</div><div class="feature-title">Developer SDK</div><div class="feature-desc">JavaScript SDK with 51 methods, native WebSocket support, and zero external dependencies. Deploy contracts, query state, and sign transactions programmatically.</div></div>
<div class="feature-card"><div class="feature-icon">&#129514;</div><div class="feature-title">Testnet Environment</div><div class="feature-desc">Full testnet with faucet, block explorer, and documentation. Deploy and test contracts before mainnet launch with real consensus and real DEX pools.</div></div>
</div>
</section>

<!-- AMM DEX -->
<section class="section-block reveal" id="dex">
<div class="section-header"><span class="section-tag">Decentralized Exchange</span><h2 class="section-title">Native AMM DEX Architecture</h2><p class="section-desc">The Verdis DEX is a native Substrate pallet &mdash; not a smart contract. This eliminates reentrancy risks, reduces execution overhead, and provides overflow-safe arithmetic at the protocol level.</p></div>
<div class="card-panel">
<h3 style="font-family:'Space Grotesk';font-size:14px;font-weight:700;color:#0f172a;margin-bottom:16px">How the Native DEX Works</h3>
<p style="font-size:14px;color:var(--text-2);line-height:1.8;margin-bottom:16px">The DEX uses the constant product formula (x &times; y = k) popularized by Uniswap, but implemented as a native pallet with checked arithmetic. Every swap, liquidity addition, and removal uses <strong>checked_mul</strong> and <strong>checked_add</strong> operations &mdash; if any calculation would overflow, the transaction reverts with an error rather than wrapping around.</p>
<table class="spec-table">
<tr><th>Feature</th><th>Implementation</th><th>Security</th></tr>
<tr><td><strong>AMM Formula</strong></td><td class="mono">x &times; y = k</td><td>Constant product invariant</td></tr>
<tr><td><strong>Swap Fee</strong></td><td class="mono">0.3%</td><td>Standard AMM fee tier</td></tr>
<tr><td><strong>Arithmetic</strong></td><td class="mono">checked_mul / checked_add</td><td>No overflow/underflow possible</td></tr>
<tr><td><strong>Self-Transfer Guard</strong></td><td class="mono">Prevented</td><td>Cannot swap token for itself</td></tr>
<tr><td><strong>Pool Bricking</strong></td><td class="mono">Prevented</td><td>Zero-reserve pools are rejected</td></tr>
<tr><td><strong>Deadline Protection</strong></td><td class="mono">Mandatory</td><td>All swaps include deadline parameter</td></tr>
<tr><td><strong>Active Pools</strong></td><td class="mono">6 (testnet)</td><td>VRDX/ECO, VRDX/CARBON, VRDX/TREE, VRDX/GREEN, ECO/CARBON, VRDX/REDD</td></tr>
</table>
</div>
<div class="feature-grid" style="margin-top:16px">
<div class="feature-card"><div class="feature-icon">&#128167;</div><div class="feature-title">Liquidity Provision</div><div class="feature-desc">Anyone can create a liquidity pool by providing equal-value deposits of two tokens. LP tokens represent proportional ownership of the pool and can be withdrawn at any time.</div></div>
<div class="feature-card"><div class="feature-icon">&#9851;</div><div class="feature-title">Token Swaps</div><div class="feature-desc">Instant token swaps with 0.3% fee distributed to liquidity providers. Slippage protection via deadline parameters. All swaps execute atomically &mdash; partial fills are not possible.</div></div>
<div class="feature-card"><div class="feature-icon">&#128737;</div><div class="feature-title">Overflow Protection</div><div class="feature-desc">Every arithmetic operation uses checked math. If a swap result would exceed u128 maximum, the transaction fails cleanly rather than wrapping to a tiny number.</div></div>
<div class="feature-card"><div class="feature-icon">&#128202;</div><div class="feature-title">On-Chain Pricing</div><div class="feature-desc">Pool reserves serve as a decentralized price oracle. The DEX can be queried by other pallets for token pricing, enabling collateralized lending and other DeFi applications.</div></div>
</div>
</section>

"""

governance_section = """
<!-- Governance -->
<section class="section-block reveal" id="governance">
<div class="section-header"><span class="section-tag">Governance</span><h2 class="section-title">Decentralized Governance Model</h2><p class="section-desc">VRDX holders govern the protocol through on-chain democracy. The governance system manages treasury allocations, runtime upgrades, and protocol parameters.</p></div>
<div class="feature-grid">
<div class="feature-card"><div class="feature-icon">&#128499;</div><div class="feature-title">Democracy</div><div class="feature-desc">Any VRDX holder can propose a referendum. Proposals are voted on by token-weighted quadratic voting. Approved proposals are automatically executed after an enactment delay.</div>
<ul class="feature-list"><li>Proposal submission requires token lock</li><li>Quadratic voting reduces whale influence</li><li>Enactment delay for safety review</li></ul>
</div>
<div class="feature-card"><div class="feature-icon">&#127963;</div><div class="feature-title">Council</div><div class="feature-desc">An elected council of 8 members fast-tracks proposals and manages emergency actions. Council members are elected by VRDX holders and can be removed via no-confidence vote.</div>
<ul class="feature-list"><li>8 council members (expandable)</li><li>Fast-track for urgent protocol fixes</li><li>Removable via no-confidence vote</li></ul>
</div>
<div class="feature-card"><div class="feature-icon">&#128176;</div><div class="feature-title">Treasury</div><div class="feature-desc">15B VRDX is allocated to the treasury, controlled by governance. Funds are spent on ecosystem grants, developer bounties, infrastructure, and carbon offset initiatives.</div>
<ul class="feature-list"><li>15,000,000,000 VRDX allocated</li><li>DAO-governed spending</li><li>Transparent on-chain accounting</li></ul>
</div>
<div class="feature-card"><div class="feature-icon">&#128274;</div><div class="feature-title">Technical Committee</div><div class="feature-desc">A technical committee of core developers can veto emergency proposals that would harm the protocol. This provides a safety net against malicious governance attacks.</div>
<ul class="feature-list"><li>Emergency veto power</li><li>Composed of core protocol developers</li><li>Prevents harmful governance captures</li></ul>
</div>
</div>
</section>

<!-- Security Model -->
<section class="section-block reveal" id="security">
<div class="section-header"><span class="section-tag">Security</span><h2 class="section-title">Security Architecture</h2><p class="section-desc">Security is the foundational design principle of Verdis Chain. Every pallet, every extrinsic, and every storage item is built with defense-in-depth.</p></div>
<div class="card-panel">
<h3 style="font-family:'Space Grotesk';font-size:14px;font-weight:700;color:#0f172a;margin-bottom:16px">Security Principles</h3>
<div class="solution-list">
<div class="solution-item"><div class="solution-check">&#128274;</div><div class="solution-content"><h4>No Custodial Keys</h4><p>The protocol never stores user private keys. All transactions are signed on the user's device (wallet). The TX Relay service only relays pre-signed extrinsics &mdash; it cannot sign on behalf of users.</p></div></div>
<div class="solution-item"><div class="solution-check">&#128737;</div><div class="solution-content"><h4>Bounded Inputs</h4><p>All extrinsic parameters use bounded Vec&lt;u8&gt; with length checks (32-128 bytes). This prevents storage DoS attacks where an attacker could submit unbounded data to exhaust chain storage.</p></div></div>
<div class="solution-item"><div class="solution-check">&#9889;</div><div class="solution-content"><h4>Safe Integer Casts</h4><p>All integer conversions use try_from instead of unsafe as casts. This prevents silent truncation bugs that could corrupt balances or staking calculations.</p></div></div>
<div class="solution-item"><div class="solution-check">&#128272;</div><div class="solution-content"><h4>Checked Arithmetic</h4><p>The DEX uses checked_mul and checked_add for all swap calculations. Overflow/underflow is impossible &mdash; transactions fail cleanly rather than wrapping around to incorrect values.</p></div></div>
<div class="solution-item"><div class="solution-check">&#128100;</div><div class="solution-content"><h4>Authorization Checks</h4><p>Green score updates require root authorization (validators cannot self-score). Carbon credit minting requires verified authority. Reforestation project creation requires admin approval.</p></div></div>
<div class="solution-item"><div class="solution-check">&#128273;</div><div class="solution-content"><h4>Air-Gapped Key Generation</h4><p>Production validator keys must be generated on air-gapped machines. No hardcoded private keys, no server-side custody, no hidden privileged backdoors, no undocumented founder controls.</p></div></div>
</div>
</div>
</section>

<!-- Use Cases -->
<section class="section-block reveal" id="use-cases">
<div class="section-header"><span class="section-tag">Applications</span><h2 class="section-title">Real-World Use Cases</h2><p class="section-desc">Verdis Chain is designed for real-world environmental, financial, and developer applications &mdash; not just speculation.</p></div>
<div class="usecase-grid">
<div class="usecase-card"><div class="usecase-icon">&#127793;</div><div class="usecase-title">Carbon Credit Trading</div><div class="usecase-desc">Companies buy and retire on-chain carbon credits with full provenance tracking. Each credit represents 1 tCO2e of verified offset. Retirements are public, immutable, and auditable.</div></div>
<div class="usecase-card"><div class="usecase-icon">&#127797;</div><div class="usecase-title">Reforestation Funding</div><div class="usecase-desc">Reforestation projects register on-chain with GPS coordinates and verification metadata. Donors fund projects directly. Progress is tracked transparently with milestone-based fund releases.</div></div>
<div class="usecase-card"><div class="usecase-icon">&#9889;</div><div class="usecase-title">Green Energy Certification</div><div class="usecase-desc">Validators prove renewable energy usage and earn green scores. Energy providers can certify green energy production on-chain, creating a verifiable renewable energy certificate (REC) market.</div></div>
<div class="usecase-card"><div class="usecase-icon">&#9851;</div><div class="usecase-title">Decentralized Trading</div><div class="usecase-desc">The native AMM DEX enables permissionless token trading. Projects can create liquidity pools for their ecosystem tokens, providing instant liquidity without centralized exchanges.</div></div>
<div class="usecase-card"><div class="usecase-icon">&#129302;</div><div class="usecase-title">AI-Powered Development</div><div class="usecase-desc">Through EvolvixOS, developers use AI to audit smart contracts, generate boilerplate, and optimize gas. AI tools analyze on-chain data for security insights and protocol health monitoring.</div></div>
<div class="usecase-card"><div class="usecase-icon">&#127974;</div><div class="usecase-title">DeFi Applications</div><div class="usecase-desc">The DEX serves as a price oracle for lending protocols. Staking derivatives, yield aggregation, and carbon-backed stablecoins can be built on top of the native pallet infrastructure.</div></div>
<div class="usecase-card"><div class="usecase-icon">&#128225;</div><div class="usecase-title">Cross-Chain Bridges</div><div class="usecase-desc">IBC protocol enables trust-minimized bridges to other chains. VRDX can be transferred to Polkadot parachains, Ethereum, and other IBC-enabled networks.</div></div>
<div class="usecase-card"><div class="usecase-icon">&#128203;</div><div class="usecase-title">Supply Chain Tracking</div><div class="usecase-desc">Green supply chains track products from origin to consumer. Each step is recorded on-chain with timestamp, location, and certification data &mdash; preventing greenwashing and fraud.</div></div>
</div>
</section>

"""

conclusion_section = """
<!-- Conclusion -->
<section class="section-block reveal" id="conclusion">
<div class="conclusion-box">
<h2>Conclusion: Building the Green Standard</h2>
<p>Verdis Chain proves that blockchain technology can be environmentally regenerative. By embedding carbon credits, green validator scoring, and reforestation tracking directly into the consensus layer, we make sustainability a protocol-level feature rather than an afterthought.</p>
<p>With 30+ custom pallets, native AMM DEX, ink! smart contracts, DPoS consensus, IBC cross-chain communication, and integration with the EvolvixOS AI ecosystem, Verdis Chain provides a complete platform for the next generation of green decentralized applications.</p>
<p>The 100B VRDX token economy is designed for long-term sustainability &mdash; with 45% allocated to ecosystem and staking, 12% to investors with structured vesting, and a DAO-governed treasury ensuring community control. Every economic parameter is designed to incentivize decentralization, security, and environmental impact.</p>
<p><strong>This is not a promise. This is architecture.</strong></p>
</div>
</section>

"""

# Insert sections
if evo_pos > 0:
    html = html[:evo_pos] + consensus_section + html[evo_pos:]
    print('Inserted Consensus/Smart Contracts/DEX sections')
else:
    print('WARN: Could not find EvolvixOS section for Consensus insertion')

# Recalculate improve_pos after insertion
improve_pos = html.find('id="improve"')
if improve_pos == -1:
    improve_pos = html.find('How We Will Improve')
if improve_pos > 0:
    improve_pos = html.rfind('<section', 0, improve_pos)
else:
    improve_pos = html.find('class="improve-list"')
    if improve_pos > 0:
        improve_pos = html.rfind('<section', 0, improve_pos)

if improve_pos > 0:
    html = html[:improve_pos] + governance_section + html[improve_pos:]
    print('Inserted Governance/Security/UseCases sections')
else:
    print('WARN: Could not find improvement section')

# Insert conclusion before footer/CTA
footer_pos = html.find('<footer')
if footer_pos == -1:
    footer_pos = html.find('Join the Green Blockchain Revolution')
    if footer_pos > 0:
        footer_pos = html.rfind('<section', 0, footer_pos)

if footer_pos > 0:
    html = html[:footer_pos] + conclusion_section + html[footer_pos:]
    print('Inserted Conclusion section')
else:
    print('WARN: Could not find footer/CTA for conclusion')

# Write files
with open('/var/www/verdiscan/whitepaper/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
with open('/opt/verdis-chain-rust/web/whitepaper/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

# Verify
with open('/var/www/verdiscan/whitepaper/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

checks = [
    ('Executive Summary' in content, 'Executive Summary'),
    ('The Problem We' in content, 'Problem Statement'),
    ('The Verdis Solution' in content, 'Solution Overview'),
    ('DPoS Consensus' in content, 'Consensus Mechanism'),
    ('ink! Smart Contract' in content, 'Smart Contracts'),
    ('Native AMM DEX' in content, 'DEX Architecture'),
    ('Decentralized Governance' in content, 'Governance'),
    ('Security Architecture' in content, 'Security Model'),
    ('Real-World Use Cases' in content, 'Use Cases'),
    ('Building the Green Standard' in content, 'Conclusion'),
    ('Dorian Jean' in content, 'Dorian Jean team'),
    ('Rojs Gordons' in content, 'Rojs Gordons team'),
    ('Inter' in content, 'Inter font'),
    ('#16a34a' in content, 'Correct green'),
    ('caff33' not in content, 'No neon green'),
    ('100B' in content, '100B supply'),
    ('Decimals' in content, 'Decimals section'),
]
for ok, label in checks:
    print('OK' if ok else 'FAIL', ':', label)

print(f'\nTotal: {len(content)} bytes, {content.count(chr(10))} lines')
print(f'Sections: {content.count("section-block")}')
