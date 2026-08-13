with open('/var/www/verdiscan/whitepaper/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

story_start = html.find('<section id="story"')
if story_start == -1:
    story_start = html.find('id="story"')
    if story_start > 0:
        story_start = html.rfind('<', 0, story_start)

print(f'Story section found at: {story_start}')

insert_html = """<!-- Executive Summary -->
<section class="section-block reveal" id="abstract">
<div class="wp-abstract">
<h3 style="font-family:'Space Grotesk';font-size:16px;font-weight:700;color:var(--text);margin-bottom:20px">Executive Summary</h3>
<p><strong>Verdis Chain</strong> is a carbon-negative Layer-1 blockchain built on Substrate, powered by native Delegated Proof-of-Stake (DPoS) consensus, an integrated AMM decentralized exchange (DEX), ink! smart contracts, and on-chain carbon credit tracking. The protocol is designed to prove that blockchain infrastructure can be environmentally regenerative rather than destructive.</p>
<p>The native token, <strong>VRDX</strong>, has a fixed supply of <strong>100 billion</strong> with <strong>9 decimals</strong>, serving as the gas token, staking asset, governance instrument, and medium of exchange across the ecosystem. VRDX is not an ERC-20 wrapper &mdash; it is woven into the consensus layer itself.</p>
<p>Verdis Chain connects to <strong>EvolvixOS</strong>, an AI Engineering Operating System that provides smart contract auditing, AI-powered development tools, and a plugin marketplace. Together, they form a complete green technology stack: blockchain provides trust and value transfer, AI provides intelligence and automation.</p>
<p>The protocol features <strong>30+ custom Substrate pallets</strong>, including DPoS consensus with 21 target validators, an AMM DEX with 6 liquidity pools, carbon credit minting and retirement, green validator scoring, reforestation logging, governance, IBC cross-chain communication, and Solana-inspired innovations (Gulf Stream, Turbine, Sealevel execution, ZK compression).</p>
</div>
</section>

<!-- Problem Statement -->
<section class="section-block reveal" id="problem">
<div class="section-header"><span class="section-tag">The Challenge</span><h2 class="section-title">The Problem We're Solving</h2><p class="section-desc">The blockchain industry faces three fundamental crises: environmental destruction, economic centralization, and technical fragmentation. Verdis Chain was built to address all three.</p></div>
<div class="problem-grid">
<div class="problem-card">
<div class="problem-icon">&#9889;</div>
<div class="problem-title">Energy Consumption Crisis</div>
<div class="problem-desc">Bitcoin and Ethereum combined consume more electricity than entire nations. Proof-of-Work mining produces 50+ million tonnes of CO2 annually, making blockchain one of the most environmentally destructive technologies ever created. No major chain has a credible path to carbon negativity.</div>
</div>
<div class="problem-card">
<div class="problem-icon">&#128736;</div>
<div class="problem-title">Validator Centralization</div>
<div class="problem-desc">Most DPoS and PoS networks concentrate power among a small number of institutional validators. Without green energy incentives and decentralization mandates, networks become oligarchies that prioritize profit over security and sustainability.</div>
</div>
<div class="problem-card">
<div class="problem-icon">&#128277;</div>
<div class="problem-title">Fragmented Ecosystems</div>
<div class="problem-desc">Blockchain, AI, and traditional fintech operate in silos. Developers must stitch together multiple chains, bridges, AI APIs, and payment systems with no unified standard. This creates friction, security risks, and poor developer experience.</div>
</div>
<div class="problem-card">
<div class="problem-icon">&#128202;</div>
<div class="problem-title">Opaque Carbon Markets</div>
<div class="problem-desc">Voluntary carbon credit markets suffer from double-counting, lack of transparency, and no real-time verification. Projects cannot prove their environmental impact. Buyers cannot trust that credits represent genuine carbon offsets.</div>
</div>
<div class="problem-card">
<div class="problem-icon">&#127976;</div>
<div class="problem-title">DEX Security Vulnerabilities</div>
<div class="problem-desc">Existing AMM DEX implementations have suffered from reentrancy attacks, overflow/underflow exploits, and LP token manipulation. Many DEX protocols are built as smart contracts on top of chains rather than as native pallets, adding layers of risk.</div>
</div>
<div class="problem-card">
<div class="problem-icon">&#129309;</div>
<div class="problem-title">Lack of Green Incentives</div>
<div class="problem-desc">No major blockchain rewards validators for using renewable energy. There is no on-chain mechanism to verify, score, or incentivize green operations. The industry talks about sustainability but has no economic model to enforce it.</div>
</div>
</div>
</section>

<!-- Solution Overview -->
<section class="section-block reveal" id="solution">
<div class="section-header"><span class="section-tag">Our Answer</span><h2 class="section-title">The Verdis Solution</h2><p class="section-desc">Verdis Chain addresses each problem with a purpose-built, native-layer solution &mdash; not a patch or a smart contract overlay.</p></div>
<div class="solution-list">
<div class="solution-item">
<div class="solution-check">&#10003;</div>
<div class="solution-content">
<h4>Carbon-Native Blockchain Architecture</h4>
<p>Carbon credit minting, retirement, and verification are built directly into the protocol as native pallets &mdash; not as ERC-20 tokens or external oracles. Every transaction contributes to carbon offsetting through a 20% fee auto-retire mechanism. The chain is designed to be carbon-negative by architecture, not by offset purchases.</p>
</div>
</div>
<div class="solution-item">
<div class="solution-check">&#10003;</div>
<div class="solution-content">
<h4>DPoS with Green Validator Scoring</h4>
<p>Validators are incentivized to operate on 100% renewable energy through on-chain green scoring. Green validators earn a +2.5% APY bonus yield. The protocol targets 21 active validators with geographic diversity, preventing the centralization seen in networks with fewer, larger validators.</p>
</div>
</div>
<div class="solution-item">
<div class="solution-check">&#10003;</div>
<div class="solution-content">
<h4>Native AMM DEX (Not a Smart Contract)</h4>
<p>The DEX is implemented as a Substrate pallet, not an ink!/Solidity contract. This eliminates reentrancy risks, reduces gas costs, and provides overflow-safe arithmetic with checked_mul/checked_add operations. 6 liquidity pools are seeded and operational on testnet.</p>
</div>
</div>
<div class="solution-item">
<div class="solution-check">&#10003;</div>
<div class="solution-content">
<h4>Unified Ecosystem with EvolvixOS</h4>
<p>Verdis Chain and EvolvixOS are designed as a single ecosystem. Blockchain provides trust and value transfer; AI provides intelligence, smart contract auditing, and development tools. Developers build once and deploy across both platforms.</p>
</div>
</div>
<div class="solution-item">
<div class="solution-check">&#10003;</div>
<div class="solution-content">
<h4>Transparent On-Chain Carbon Credits</h4>
<p>Every carbon credit is minted on-chain with verifiable provenance. Retirements are public and immutable. 1 tCO2e = 100 Eco-Credits. Double-counting is impossible by protocol design. Reforestation projects are logged with GPS coordinates and verification metadata.</p>
</div>
</div>
<div class="solution-item">
<div class="solution-check">&#10003;</div>
<div class="solution-content">
<h4>Solana-Inspired Performance Innovations</h4>
<p>Gulf Stream transaction forwarding, Turbine block propagation, Sealevel parallel execution, ZK compression, and Account Lookup Tables (ALT) are implemented as native pallets &mdash; bringing high-throughput architecture to the Substrate ecosystem without compromising on decentralization.</p>
</div>
</div>
</div>
</section>

"""

if story_start >= 0:
    html = html[:story_start] + insert_html + html[story_start:]
    print('Inserted 3 sections before story section')
else:
    print('ERROR: Could not find story section')

with open('/var/www/verdiscan/whitepaper/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
with open('/opt/verdis-chain-rust/web/whitepaper/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

with open('/var/www/verdiscan/whitepaper/index.html', 'r', encoding='utf-8') as f:
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
    ('100B' in content, '100B supply'),
    ('Decimals' in content, 'Decimals section'),
]
for ok, label in checks:
    print('OK' if ok else 'FAIL', ':', label)

print(f'\nTotal: {len(content)} bytes, {content.count(chr(10))} lines')
print(f'Sections: {content.count("section-block")}')
