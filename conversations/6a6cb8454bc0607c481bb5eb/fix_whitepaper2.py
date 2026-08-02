#!/usr/bin/env python3
"""Fix garbled text in whitepaper sections 21-26."""

filepath = "/opt/verdis/app/dist/web/whitepaper.html"
with open(filepath, "r") as f:
    content = f.read()

def replace_section(content, section_num, new_html):
    marker = f'id="section-{section_num}"'
    start = content.find(marker)
    if start < 0:
        print(f"WARNING: Section {section_num} not found")
        return content
    open_end = content.find('>', start) + 1
    close_tag = "</section>"
    close_pos = content.find(close_tag, open_end)
    if close_pos < 0:
        print(f"WARNING: Closing tag for section {section_num} not found")
        return content
    before = content[:open_end]
    after = content[close_pos:]
    return before + new_html + after

# Section 21
section21 = """
<div class="section-header"><span class="section-badge">21</span><h2 class="section-title">Network Architecture Diagram</h2></div>
<div class="glass-card">
<p class="tech-para">Verdis operates as an autonomous Layer-1 blockchain deployed on a Hetzner VPS with Nginx reverse proxy, SSL/TLS encryption via Let's Encrypt, and systemd auto-restart. The architecture consists of 4 isolated layers: API Gateway, Consensus, Execution, and Persistence.</p>

<div class="tech-subsec">21.1 — Full Network Architecture</div>
<div class="tech-diagram">┌────────────────────────────────────────────────────────────────────┐
│ CLIENT LAYER                                                        │
│ Browser · MetaMask · Verdis Wallet · curl · Web3 SDK · Mobile      │
└───────────────────────────────┬────────────────────────────────────┘
                                │ HTTPS (TLS 1.3)
                                ▼
┌────────────────────────────────────────────────────────────────────┐
│ NGINX REVERSE PROXY :443                                           │
│ ┌─────────┐ ┌──────────┐ ┌───────────┐ ┌─────────────────────┐     │
│ │ SSL/TLS │ │ gzip     │ │ CORS      │ │ Static files (HTML) │     │
│ │ Let's   │ │ compress │ │ headers   │ │ landing/dashboard/  │     │
│ │ Encrypt │ │          │ │          │ │ whitepaper/explorer │     │
│ └─────────┘ └──────────┘ └───────────┘ └─────────────────────┘     │
└───────────────────────────────┬────────────────────────────────────┘
                                │ proxy_pass http://localhost:3200
                                ▼
┌────────────────────────────────────────────────────────────────────┐
│ VERDIS NODE :3200 (Express.js)                                    │
│                                                                    │
│ ┌──────────────────────────────────────────────────────────────┐   │
│ │ API GATEWAY LAYER                                            │   │
│ ├──┬──────────────┬──────────────┬──────────────┬──────────────┤   │
│ │ │ REST API     │ JSON-RPC     │ WebSocket    │ Security     │   │
│ │ │ (40+ routes) │ (25+ methods)│ (live feeds)  │ (13 checks)  │   │
│ │ │ /api/*       │ /rpc         │ /ws           │ /api/sec/*   │   │
│ ├──┴──────────────┴──────────────┴──────────────┴──────────────┤   │
│ │ CONSENSUS LAYER                                             │   │
│ ├──┬──────────────┬──────────────┬──────────────┬──────────────┤   │
│ │ │ DPoS Engine   │ Validator    │ Block        │ Eco/Green   │   │
│ │ │ (27 SR)      │ Registry     │ Producer     │ Score Mgr   │   │
│ │ │ Round-robin  │ (register,   │ (every 5s)   │ (24h cycle) │   │
│ │ │              │ vote, slash) │              │              │   │
│ ├──┴──────────────┴──────────────┴──────────────┴──────────────┤   │
│ │ EXECUTION LAYER                                             │   │
│ ├──┬──────────────┬──────────────┬──────────────┬──────────────┤   │
│ │ │ Verdis VM    │ VerdisSwap   │ Token System  │ Carbon      │   │
│ │ │ (101 opcodes)│ AMM DEX      │ (balances,   │ Credits &   │   │
│ │ │ Smart        │ (7 pools,    │ transfers,   │ Reforestation│   │
│ │ │ Contracts    │ swaps)       │ staking)      │ Logging     │   │
│ ├──┴──────────────┴──────────────┴──────────────┴──────────────┤   │
│ │ PERSISTENCE LAYER                                           │   │
│ ├──┬──────────────┬──────────────┬──────────────┬──────────────┤   │
│ │ │ Blockchain    │ verdis-state │ Faucet       │ Vesting     │   │
│ │ │ (in-memory    │ .json (disk) │ claims.json  │ Ledger      │   │
│ │ │ chain[])      │ (auto-save)  │ (disk)       │ (disk)      │   │
│ └──┴──────────────┴──────────────┴──────────────┴──────────────┘   │
└───────────────────────────────┬────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────────┐
│ SYSTEMD SERVICE (verdis.service)                                   │
│ Auto-restart on crash · Health check · Log rotation · JIT compile │
└────────────────────────────────────────────────────────────────────┘</div>

<div class="tech-subsec">21.2 — Data Flow</div>
<table class="tech-spec-table">
<tr><th>Flow</th><th>From → To</th><th>Protocol</th><th>Frequency</th></tr>
<tr><td>RPC requests</td><td>Client → Nginx → Node</td><td>HTTPS/JSON-RPC</td><td>On-demand</td></tr>
<tr><td>Blocks</td><td>Block Producer → Chain</td><td>In-memory</td><td>Every 5 seconds</td></tr>
<tr><td>State save</td><td>Node → Disk (verdis-state.json)</td><td>fs.writeFileSync</td><td>Every 100 blocks</td></tr>
<tr><td>Auto-trade bot</td><td>DEX → Pools</td><td>In-memory</td><td>Every 10 seconds</td></tr>
<tr><td>Green Score update</td><td>Eco Manager → Validators</td><td>In-memory</td><td>Every 24 hours</td></tr>
<tr><td>Health check</td><td>systemd → Node</td><td>HTTP GET /api/health</td><td>Every 30 seconds</td></tr>
</table>

<div class="tech-subsec">21.3 — Performance Metrics</div>
<table class="tech-spec-table">
<tr><th>Metric</th><th>Value</th><th>Method</th></tr>
<tr><td>Block time</td><td>5s</td><td>setInterval(produceBlock, 5000)</td></tr>
<tr><td>TPS (theoretical max)</td><td>100 (500 TX × 5s)</td><td>MAX_BLOCK_SIZE / blockTime</td></tr>
<tr><td>API latency</td><td>&lt; 50ms</td><td>Nginx → Express → JSON</td></tr>
<tr><td>State file size</td><td>~715KB</td><td>verdis-state.json</td></tr>
<tr><td>Memory usage</td><td>~150MB</td><td>Node.js process</td></tr>
<tr><td>Uptime</td><td>99.9%+</td><td>systemd auto-restart</td></tr>
</table>
</div>
"""

# Section 22
section22 = """
<div class="section-header"><span class="section-badge">22</span><h2 class="section-title">Transaction Lifecycle Flow</h2></div>
<div class="glass-card">
<p class="tech-para">Every VRDX transaction goes through 8 stages from creation to final confirmation on the blockchain. This ensures security, immutability, and verifiability at each step.</p>

<div class="tech-subsec">22.1 — Transaction Lifecycle</div>
<div class="tech-diagram">Step 1: CREATION
┌─────────────────────────────────────────┐
│ User creates transaction:             │
│ • from: 0x72cd...b312                  │
│ • to: 0xdead...beef                     │
│ • amount: 100 VRDX                      │
│ • fee: 1 VRDX                           │
│ • nonce: 42                             │
└───────────────────┬─────────────────────┘
                    │
                    ▼
Step 2: SIGNING (secp256k1 ECDSA)
┌─────────────────────────────────────────┐
│ payload = SHA256(from + to + amount    │
│ + fee + nonce)                          │
│ signature = secp256k1.sign(payload,     │
│ privateKey)                             │
│ tx.id = SHA256(payload + signature)    │
└───────────────────┬─────────────────────┘
                    │
                    ▼
Step 3: SUBMISSION (POST /api/transaction/send)
┌─────────────────────────────────────────┐
│ HTTP POST → Nginx → Express             │
│ Body: {privateKey, from, to,            │
│ amount, fee, nonce}                     │
│ → SecurityManager.checkRateLimit(ip)    │
└───────────────────┬─────────────────────┘
                    │
                    ▼
Step 4: VALIDATION (Security Checks)
┌─────────────────────────────────────────┐
│ ✓ Rate limit (30/min standard)         │
│ ✓ Address validation (0x prefix)        │
│ ✓ Amount validation (>0, ≤ 1B VRDX)     │
│ ✓ Nonce replay check                    │
│ ✓ Signature verification (secp256k1)    │
│ ✓ Balance check (amount + fee ≤ balance)│
└───────────────────┬─────────────────────┘
                    │ Pass
                    ▼
Step 5: MEMPOOL
┌─────────────────────────────────────────┐
│ Transaction added to mempool            │
│ MAX_MEMPOOL_SIZE = 1000                  │
│ Pending until next block                │
└───────────────────┬─────────────────────┘
                    │
                    ▼
Step 6: BLOCK PRODUCTION (every 5s)
┌─────────────────────────────────────────┐
│ DPoS: getCurrentProducer() → Top-27 SR  │
│ Takes TX from mempool (≤ 500 per block) │
│ Builds Merkle Tree of transactions      │
│ Creates BlockHeader + signs with key    │
│ blockHash = doubleSHA256(header)        │
└───────────────────┬─────────────────────┘
                    │
                    ▼
Step 7: STATE EXECUTION
┌─────────────────────────────────────────┐
│ TokenSystem.applyTransaction(tx, prod)  │
│ • deductBalance(from, amount + fee)    │
│ • addBalance(to, amount)                │
│ • addBalance(producer, fee)             │
│ • consumeNonce(nonce)                    │
│ • distributeRewards(producer, 16 VRDX)  │
│   → 80% producer, 20% voters             │
└───────────────────┬─────────────────────┘
                    │
                    ▼
Step 8: PERSISTENCE & BROADCAST
┌─────────────────────────────────────────┐
│ Block added to chain[]                  │
│ State saved → verdis-state.json         │
│ WebSocket broadcast → Dashboard         │
│ Explorer updates in real-time           │
│                                         │
│ ✓ Transaction confirmed                 │
│ ✓ Immutable in blockchain               │
│ ✓ Verifiable through Merkle proof       │
└─────────────────────────────────────────┘</div>

<div class="tech-subsec">22.2 — Processing Time</div>
<table class="tech-spec-table">
<tr><th>Stage</th><th>Time</th><th>Description</th></tr>
<tr><td>Creation + signing</td><td>&lt; 10ms</td><td>Client-side (secp256k1.sign)</td></tr>
<tr><td>Network latency</td><td>20-50ms</td><td>HTTPS to server</td></tr>
<tr><td>Validation</td><td>&lt; 5ms</td><td>SecurityManager checks</td></tr>
<tr><td>Mempool wait</td><td>0-5s</td><td>Until next block</td></tr>
<tr><td>Block production</td><td>&lt; 50ms</td><td>Merkle Tree + hash + sign</td></tr>
<tr><td>State execution</td><td>&lt; 5ms</td><td>Balance updates</td></tr>
<tr><td>Persistence</td><td>&lt; 100ms</td><td>writeFileSync (sync)</td></tr>
<tr><td><strong>Total</strong></td><td><strong>~5-6s</strong></td><td><strong>From creation to confirmation</strong></td></tr>
</table>

<div class="tech-subsec">22.3 — Transaction Types</div>
<table class="tech-spec-table">
<tr><th>Type</th><th>Endpoint</th><th>Checks</th></tr>
<tr><td>Transfer</td><td>/api/transaction/send</td><td>Balance, nonce, signature</td></tr>
<tr><td>Stake</td><td>/api/staking/stake</td><td>Balance ≥ amount, min 1,000 VRDX</td></tr>
<tr><td>Unstake</td><td>/api/staking/unstake</td><td>Staked ≥ amount</td></tr>
<tr><td>Vote</td><td>/api/consensus/vote</td><td>Validator exists, balance</td></tr>
<tr><td>DEX Swap</td><td>/api/dex/swap</td><td>Pool liquidity, slippage</td></tr>
<tr><td>Contract Deploy</td><td>/api/contract/deploy</td><td>Bytecode validation</td></tr>
<tr><td>Contract Execute</td><td>/api/contract/:id/execute</td><td>Contract exists, gas</td></tr>
<tr><td>Carbon Credit</td><td>/api/eco/carbon/mint</td><td>Admin key, project exists</td></tr>
</table>
</div>
"""

# Section 23
section23 = """
<div class="section-header"><span class="section-badge">23</span><h2 class="section-title">Token Flow & VRDX Demand Sources</h2></div>
<div class="glass-card">
<p class="tech-para">Demand for VRDX is driven by 7 key streams. Each creates buying pressure on the token through independent economic mechanisms.</p>

<div class="tech-subsec">23.1 — Demand Sources</div>
<table class="tech-spec-table">
<tr><th>#</th><th>Source</th><th>Mechanism</th><th>Impact</th></tr>
<tr><td>1</td><td>IDO Token Sale</td><td>Direct purchase at $0.0005/VRDX</td><td>Initial demand, price discovery</td></tr>
<tr><td>2</td><td>DEX Trading</td><td>AMM swaps across 7 pools (VRDX pairs)</td><td>Continuous trading volume</td></tr>
<tr><td>3</td><td>Staking</td><td>Lock VRDX for validator delegation</td><td>Reduces circulating supply</td></tr>
<tr><td>4</td><td>Validator Registration</td><td>Minimum 1M VRDX stake required</td><td>Long-term lock-up</td></tr>
<tr><td>5</td><td>Carbon Credits</td><td>VRDX used to mint/retire carbon credits</td><td>Utility-driven demand</td></tr>
<tr><td>6</td><td>Governance</td><td>Staking VRDX for VerdisDAO voting rights</td><td>Locks tokens for participation</td></tr>
<tr><td>7</td><td>Protocol Fee Burn</td><td>20% of all DEX fees permanently burned</td><td>Deflationary pressure</td></tr>
</table>

<div class="tech-subsec">23.2 — Token Lock-up Summary</div>
<table class="tech-spec-table">
<tr><th>Category</th><th>Amount</th><th>Lock Duration</th></tr>
<tr><td>Staking lock</td><td>10B VRDX (Staking allocation)</td><td>Continuous (per-block emission)</td></tr>
<tr><td>Vesting lock</td><td>Team/Investors/Advisors (20B)</td><td>6-48 months per schedule</td></tr>
<tr><td>Liquidity lock</td><td>5B VRDX</td><td>24 months</td></tr>
<tr><td>Treasury lock</td><td>20B VRDX</td><td>DAO governance only</td></tr>
<tr><td>Community distribution</td><td>34B VRDX</td><td>8-10 year release</td></tr>
</table>

<div class="tech-subsec">23.3 — Deflationary Mechanics</div>
<p class="tech-para">Verdis implements deflationary pressure through a 20% protocol fee burn on all DEX transactions. As trading volume increases, more VRDX is permanently removed from circulation, creating a supply squeeze that benefits long-term holders. The maximum supply of 100B VRDX is fixed and can never be increased.</p>
</div>
"""

# Section 24
section24 = """
<div class="section-header"><span class="section-badge">24</span><h2 class="section-title">Ecosystem Revenue Model</h2></div>
<div class="glass-card">
<p class="tech-para">The Verdis ecosystem generates revenue through multiple streams, ensuring sustainability and continuous development funding.</p>

<div class="tech-subsec">24.1 — Revenue Streams</div>
<table class="tech-spec-table">
<tr><th>Stream</th><th>Source</th><th>Rate</th><th>Distribution</th></tr>
<tr><td>DEX Trading Fees</td><td>0.3% per swap on VerdisSwap</td><td>0.3% of trade volume</td><td>80% LP providers, 20% burn</td></tr>
<tr><td>Staking Fees</td><td>Validator commission on rewards</td><td>Variable (set by validator)</td><td>Validator + delegators</td></tr>
<tr><td>Carbon Credit Issuance</td><td>Corporate carbon offset purchases</td><td>$5-50/credit</td><td>70% treasury, 30% validator</td></tr>
<tr><td>Enterprise ESG API</td><td>Corporate API access for ESG reporting</td><td>$500-5000/month</td><td>Treasury</td></tr>
<tr><td>Carbon Credit Retirement</td><td>Fee for retiring credits on-chain</td><td>0.1 VRDX per credit</td><td>Burned</td></tr>
<tr><td>Green Validator Subsidies</td><td>Subsidies for running on 100% renewable energy</td><td>20% of fees</td><td>Validators</td></tr>
</table>

<div class="tech-subsec">24.2 — Projected Annual Revenue</div>
<table class="tech-spec-table">
<tr><th>Year</th><th>DEX Volume</th><th>Carbon Credits</th><th>Enterprise API</th><th>Total</th></tr>
<tr><td>2026 (H2)</td><td>$110K</td><td>$25K</td><td>$0</td><td>$135K</td></tr>
<tr><td>2027</td><td>$2M</td><td>$500K</td><td>$200K</td><td>$2.7M</td></tr>
<tr><td>2028</td><td>$10M</td><td>$2M</td><td>$1M</td><td>$13M</td></tr>
</table>

<div class="tech-subsec">24.3 — Burn Rate</div>
<p class="tech-para">With 20% of all DEX fees permanently burned, the annual VRDX burn rate is projected to reach 500M VRDX by 2027 and 2B VRDX by 2028. This creates a deflationary spiral that increases token scarcity over time, benefiting all holders.</p>
</div>
"""

# Section 25
section25 = """
<div class="section-header"><span class="section-badge">25</span><h2 class="section-title">Team & Advisory</h2></div>
<div class="glass-card">
<div class="tech-subsec">25.1 — Core Team</div>
<p class="tech-para">The Verdis team consists of 5 experienced engineers and a growth manager, each with expertise in distributed systems, blockchain protocol design, climate technology, and mobile engineering. All team profiles and GitHub contributions are publicly available on the team page.</p>

<table class="tech-spec-table">
<tr><th>Role</th><th>Responsibilities</th><th>Background</th></tr>
<tr><td>Founder & CEO</td><td>Vision, strategy, protocol design</td><td>Protremix CEO, Anerium fintech platform creator</td></tr>
<tr><td>Lead Architect & Protocol Engineer</td><td>Consensus, VM, cryptography</td><td>Blockchain protocol design, secp256k1 implementation</td></tr>
<tr><td>Full-Stack Engineer</td><td>Web dashboard, explorer, API</td><td>Web3 development, real-time data systems</td></tr>
<tr><td>Mobile Engineer</td><td>Android wallet, native UI</td><td>Native Android development, security-first design</td></tr>
<tr><td>Eco Systems Engineer</td><td>Carbon credits, reforestation tracking</td><td>Climate tech, satellite data integration</td></tr>
<tr><td>Community & Growth Manager</td><td>Telegram, Twitter, partnerships</td><td>Community building, Web3 marketing</td></tr>
</table>

<div class="tech-subsec">25.2 — Advisors</div>
<table class="tech-spec-table">
<tr><th>Role</th><th>Expertise</th></tr>
<tr><td>Cryptographic Audit Advisor</td><td>Security auditing, formal verification, secp256k1 review</td></tr>
<tr><td>Climate Science Advisor</td><td>Carbon credit standards (VCS, Gold Standard), NDVI satellite verification</td></tr>
<tr><td>Legal & Compliance Advisor</td><td>Regulatory framework, token sale compliance, ESG reporting standards</td></tr>
</table>

<div class="tech-subsec">25.3 — Founder Background</div>
<p class="tech-para"><strong>Rojs Gordons</strong> is the Founder and CEO of Verdis. He is the CEO of <strong>Protremix</strong>, a software development company with a track record of building production fintech platforms. His prior work includes the <strong>Anerium</strong> fintech platform and multiple payment systems. His vision for Verdis combines production-grade financial infrastructure with on-chain ecological impact tracking.</p>
</div>
"""

# Section 26
section26 = """
<div class="section-header"><span class="section-badge">26</span><h2 class="section-title">Detailed Roadmap with Dates</h2></div>
<div class="glass-card">
<div class="tech-subsec">26.1 — Completed Milestones</div>
<table class="tech-spec-table">
<tr><th>Date</th><th>Milestone</th><th>Status</th></tr>
<tr><td>Jan 15 — Jun 30, 2026</td><td>Genesis, Testnet & IDO Phase 1-2</td><td><span style="color:#00ff88">✓ Completed</span></td></tr>
<tr><td>Aug 1, 2026</td><td>Mainnet V1 & Ecosystem Launch</td><td><span style="color:#00ff88">✓ Completed</span></td></tr>
<tr><td>Aug 2, 2026</td><td>Verdiscan Explorer, Wallet v3, Protocol-level vesting</td><td><span style="color:#00ff88">✓ Completed</span></td></tr>
</table>

<div class="tech-subsec">26.2 — Upcoming Milestones</div>
<table class="tech-spec-table">
<tr><th>Date</th><th>Milestone</th><th>Status</th></tr>
<tr><td>Sep 1 — Sep 30, 2026</td><td>External Security Audit (CertiK/Hacken) + Bug Bounty ($50K)</td><td><span style="color:#ffaa00">In Progress</span></td></tr>
<tr><td>Oct 1 — Oct 31, 2026</td><td>CEX Listings: MEXC, Gate.io, Bitget + DEX Liquidity Bootstrap</td><td><span style="color:#00aaff">Upcoming</span></td></tr>
<tr><td>Nov 1 — Dec 31, 2026</td><td>Tier-1 CEX Listing (Binance/OKX/Bybit) + Enterprise ESG API</td><td><span style="color:#00aaff">Upcoming</span></td></tr>
<tr><td>Q1 2027</td><td>ESA Sentinel-2 Satellite Integration + 1M Trees Verified</td><td><span style="color:#00aaff">Planned</span></td></tr>
<tr><td>Q2 — Q4 2027</td><td>ZK-Rollups Layer-2 + iOS Wallet + 100+ Validators</td><td><span style="color:#00aaff">Planned</span></td></tr>
</table>

<div class="tech-subsec">26.3 — Technical Milestones</div>
<table class="tech-spec-table">
<tr><th>Feature</th><th>Target Date</th><th>Current Status</th></tr>
<tr><td>Block Production (5s)</td><td>Aug 2026</td><td>Live (12,000+ blocks)</td></tr>
<tr><td>DPoS (27 validators)</td><td>Aug 2026</td><td>Live (5 active, 27 registered)</td></tr>
<tr><td>VerdisSwap AMM (7 pools)</td><td>Aug 2026</td><td>Live (5,700+ swaps)</td></tr>
<tr><td>Carbon Credit Tracking</td><td>Aug 2026</td><td>Live (17Kt CO2, 10K trees)</td></tr>
<tr><td>Protocol-level Vesting</td><td>Aug 2026</td><td>Live (6 endpoints enforced)</td></tr>
<tr><td>Verdiscan Explorer</td><td>Aug 2026</td><td>Live (10 tabs, real-time data)</td></tr>
<tr><td>Android Wallet v2.5.2</td><td>Aug 2026</td><td>Live (release-signed)</td></tr>
<tr><td>Cross-chain Bridges</td><td>Oct 2026</td><td>Development</td></tr>
<tr><td>ZK-Rollup Prototype</td><td>Q1 2027</td><td>Research</td></tr>
<tr><td>iOS Wallet</td><td>Q2-Q4 2027</td><td>Planned</td></tr>
</table>
</div>
"""

for num, new_html in [(21, section21), (22, section22), (23, section23), (24, section24), (25, section25), (26, section26)]:
    content = replace_section(content, num, new_html)
    print(f"OK: Replaced section {num}")

with open(filepath, "w") as f:
    f.write(content)

# Verify
import re
patterns = ['andwithbyet', 'witheewith', 'inandt', 'etowith', 'ineandean', 'tforandand',
            'ewitht', 'twitht', 'ewithand', 'andwitht', 'ewithandwith', 'andtandand',
            'withtand', 'withinand', 'teandand', 'andwithewith', 'andandtwith',
            'ewitheandinet', 'eteandandin', 'proportionale', 'foreandwitht']
total = 0
for p in patterns:
    matches = re.findall(p, content)
    if matches:
        total += len(matches)
        print(f"REMAINING: {p} ({len(matches)}x)")

if total == 0:
    print("\nVERIFICATION PASSED: No garbled text remaining!")
else:
    print(f"\n{total} garbled patterns still remain")
