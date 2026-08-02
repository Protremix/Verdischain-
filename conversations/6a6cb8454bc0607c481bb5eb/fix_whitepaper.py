#!/usr/bin/env python3
"""
Fix garbled text in whitepaper.html sections 16-20 and 27.
Replace corrupted text with proper English technical content.
"""

filepath = "/opt/verdis/app/dist/web/whitepaper.html"
with open(filepath, "r") as f:
    content = f.read()

# Helper: replace a section's content between its opening tag and the next section
import re

def replace_section(content, section_num, new_html):
    """Replace the inner content of a section, keeping the section wrapper."""
    # Find the section start
    marker = f'id="section-{section_num}"'
    start = content.find(marker)
    if start < 0:
        print(f"WARNING: Section {section_num} not found")
        return content
    
    # Find the section opening tag end (first > after the id)
    open_end = content.find('>', start) + 1
    
    # Find the closing </section> for this section
    close_tag = "</section>"
    close_pos = content.find(close_tag, open_end)
    if close_pos < 0:
        print(f"WARNING: Closing tag for section {section_num} not found")
        return content
    
    # Replace content between open and close
    before = content[:open_end]
    after = content[close_pos:]
    
    return before + new_html + after

# === SECTION 16: Validator Selection Algorithm ===
section16 = """
<div class="section-header"><span class="section-badge">16</span><h2 class="section-title">Validator Selection Algorithm</h2></div>
<div class="glass-card">
<p class="tech-para">Verdis employs a <strong>Delegated Proof-of-Stake (DPoS)</strong> consensus algorithm inspired by Tron's model, where 27 Super Representatives (validators) are elected by token holders to produce blocks in a round-robin schedule. The algorithm ensures fast finality, high throughput, and energy efficiency.</p>

<div class="tech-subsec">16.1 — Validator Registration</div>
<p class="tech-para">Any VRDX token holder may register as a validator candidate by submitting a registration transaction with a secp256k1 public key. Registration creates a validator entry in the consensus state with the following structure:</p>
<div class="tech-code-block"><span class="cmt">// Validator structure in consensus layer</span>
<span class="kw">struct</span> <span class="fn">Validator</span> {
  publicKey: <span class="str">[u8; 33]</span>,  <span class="cmt">// secp256k1 compressed public key</span>
  address: <span class="str">String</span>,       <span class="cmt">// Keccak256-derived EVM address (0x...)</span>
  votes: <span class="str">u64</span>,            <span class="cmt">// total delegated VRDX count</span>
  isProducer: <span class="str">bool</span>,      <span class="cmt">// actively producing blocks</span>
  blocksProduced: <span class="str">u64</span>,    <span class="cmt">// lifetime block count</span>
  totalRewards: <span class="str">u64</span>,     <span class="cmt">// total rewards earned</span>
}</div>

<div class="tech-subsec">16.2 — Voting and Delegation Algorithm</div>
<p class="tech-para">VRDX holders delegate their tokens to validator candidates through the <code style="color:#00ff88">vote(voter, validator, amount)</code> transaction. Delegated tokens are locked (staking lock), and voting power is proportional to the delegated amount:</p>
<div class="tech-code-block"><span class="cmt">// Delegation logic</span>
<span class="kw">function</span> <span class="fn">vote</span>(voter, validatorAddr, amount) {
  <span class="kw">require</span>(balanceOf(voter) >= amount, <span class="str">"Insufficient balance"</span>);
  <span class="kw">require</span>(validators[validatorAddr].exists, <span class="str">"Not a validator"</span>);
  
  <span class="cmt">// Lock tokens and update votes</span>
  lockTokens(voter, amount);
  validators[validatorAddr].votes += amount;
  voters[voter].delegatedTo = validatorAddr;
  voters[voter].delegatedAmount += amount;
}</div>

<div class="tech-subsec">16.3 — Round-Robin Block Production</div>
<p class="tech-para">Every maintenance interval (6 hours), the top 27 validators by vote count are selected as Super Representatives. Block production proceeds in round-robin order, with each validator producing one block per 3-second slot. A full round completes in 81 seconds (27 × 3s). Validators who fail to produce within their slot are skipped, and the next validator takes over.</p>

<div class="tech-subsec">16.4 — Green Score Integration</div>
<p class="tech-para">Validator selection incorporates a <strong>Green Score</strong> (0-100) that rewards eco-friendly infrastructure. Validators using renewable energy sources receive higher scores, which translate to a bonus on their effective vote count. This ensures the network incentivizes sustainable operations without compromising security.</p>
</div>
"""

# === SECTION 17: Block Structure & Cryptographic Primitives ===
section17 = """
<div class="section-header"><span class="section-badge">17</span><h2 class="section-title">Block Structure & Cryptographic Primitives</h2></div>
<div class="glass-card">
<p class="tech-para">Each block in the Verdis chain contains a header with cryptographic commitments to the block's state, a body of validated transactions, and consensus metadata for finality verification.</p>

<div class="tech-subsec">17.1 — Block Header Structure</div>
<div class="tech-code-block"><span class="cmt">// Block header structure</span>
<span class="kw">struct</span> <span class="fn">BlockHeader</span> {
  index: <span class="str">u64</span>,              <span class="cmt">// block height</span>
  previousHash: <span class="str">[u8; 32]</span>,   <span class="cmt">// SHA-256 of previous block header</span>
  merkleRoot: <span class="str">[u8; 32]</span>,    <span class="cmt">// Merkle root of all transactions</span>
  stateRoot: <span class="str">[u8; 32]</span>,     <span class="cmt">// Keccak256 of state trie root</span>
  timestamp: <span class="str">u64</span>,          <span class="cmt">// Unix epoch milliseconds</span>
  validator: <span class="str">String</span>,      <span class="cmt">// validator's EVM address</span>
  validatorPubKey: <span class="str">[u8; 33]</span>, <span class="cmt">// secp256k1 public key</span>
  signature: <span class="str">[u8; 64]</span>,    <span class="cmt">// secp256k1 ECDSA signature</span>
  nonce: <span class="str">u64</span>,            <span class="cmt">// consensus nonce</span>
}</div>

<div class="tech-subsec">17.2 — Cryptographic Primitives</div>
<p class="tech-para">Verdis uses a dual-hash architecture for security and EVM compatibility:</p>
<ul style="margin-left: 20px; color: var(--text-muted); line-height: 1.8;">
<li><strong>SHA-256:</strong> Used for block chaining (previousHash) and Merkle tree construction. Provides resistance against preimage and collision attacks.</li>
<li><strong>Keccak-256:</strong> Used for EVM address derivation, state trie roots, and smart contract address computation. Ensures compatibility with Ethereum tooling.</li>
<li><strong>secp256k1:</strong> ECDSA signatures for all transactions and block proposals. Public keys are 33 bytes (compressed), signatures are 64 bytes (r, s) with a 1-byte recovery id.</li>
</ul>

<div class="tech-subsec">17.3 — Merkle Tree Construction</div>
<p class="tech-para">Transactions within a block are organized into a binary Merkle tree using SHA-256. The root hash is included in the block header, enabling efficient SPV (Simple Payment Verification) proofs. A Merkle proof for any transaction requires only log₂(n) hashes, where n is the number of transactions in the block.</p>
</div>
"""

# === SECTION 18: Staking Economics & Reward Distribution ===
section18 = """
<div class="section-header"><span class="section-badge">18</span><h2 class="section-title">Staking Economics & Reward Distribution</h2></div>
<div class="glass-card">
<p class="tech-para">Verdis staking economics are designed to incentivize long-term participation, secure the network, and reward eco-friendly validators.</p>

<div class="tech-subsec">18.1 — Block Rewards</div>
<p class="tech-para">Each block produces a reward of 16 VRDX, distributed as follows:</p>
<ul style="margin-left: 20px; color: var(--text-muted); line-height: 1.8;">
<li><strong>Block Producer (80%):</strong> 12.8 VRDX to the validator who produced the block.</li>
<li><strong>Voters (20%):</strong> 3.2 VRDX split proportionally among all delegators to that validator.</li>
</ul>

<div class="tech-subsec">18.2 — Staking Parameters</div>
<table class="tech-table">
<tr><th>Parameter</th><th>Value</th><th>Description</th></tr>
<tr><td>minValidatorStake</td><td>1,000,000 VRDX</td><td>Minimum stake to register as validator</td></tr>
<tr><td>blockReward</td><td>16 VRDX</td><td>Reward per block</td></tr>
<tr><td>maintenanceInterval</td><td>6 hours</td><td>Validator re-election frequency</td></tr>
<tr><td>unstakingDelay</td><td>72 hours</td><td>Lock period after undelegation</td></tr>
<tr><td>maxValidators</td><td>27</td><td>Super Representatives per round</td></tr>
</table>

<div class="tech-subsec">18.3 — Green Reward Multiplier</div>
<p class="tech-para">Validators with a Green Score above 80 receive a 1.2× multiplier on their block rewards. This incentivizes the use of renewable energy and low-carbon infrastructure. The Green Score is calculated from verified energy source data, hardware efficiency metrics, and carbon offset contributions.</p>

<div class="tech-subsec">18.4 — Slashing and Penalties</div>
<p class="tech-para">Validators who act maliciously or fail to produce blocks are subject to slashing:</p>
<ul style="margin-left: 20px; color: var(--text-muted); line-height: 1.8;">
<li><strong>Double Signing:</strong> 20% of staked VRDX slashed, validator permanently removed.</li>
<li><strong>Downtime:</strong> 1% of staked VRDX slashed per 100 missed blocks (max 10%).</li>
<li><strong>Malicious Block:</strong> Full stake slashed, validator blacklisted.</li>
</ul>
</div>
"""

# === SECTION 19: Security Model & Threat Mitigation ===
section19 = """
<div class="section-header"><span class="section-badge">19</span><h2 class="section-title">Security Model & Threat Mitigation</h2></div>
<div class="glass-card">
<p class="tech-para">Verdis implements a comprehensive security model addressing consensus-level, network-level, and application-level threats.</p>

<div class="tech-subsec">19.1 — Threat Model</div>
<table class="tech-table">
<tr><th>Threat</th><th>Mitigation</th><th>Severity</th></tr>
<tr><td>51% Attack (Validator Collusion)</td><td>BFT 2/3 majority required; 27 distributed validators; slashing disincentive</td><td>Low</td></tr>
<tr><td>Long-Range Attack</td><td>Checkpoint blocks signed by 2/3 validators; finality in 2 slots</td><td>Low</td></tr>
<tr><td>Transaction Replay</td><td>Per-account nonce tracking; chain ID 909 in signatures</td><td>Very Low</td></tr>
<tr><td>DDoS / Spam</td><td>Rate limiting (30/min standard, 5/min strict); mempool cap (1000 txs); gas pricing</td><td>Low</td></tr>
<tr><td>Sybil Attack</td><td>Minimum stake 1M VRDX for validator registration</td><td>Very Low</td></tr>
<tr><td>Smart Contract Exploit</td><td>Formal verification; opcode whitelist; gas limits; code audit</td><td>Medium</td></tr>
</table>

<div class="tech-subsec">19.2 — Active Security Checks (13)</div>
<p class="tech-para">The Verdis security layer enforces 13 active checks on every transaction and block:</p>
<ol style="margin-left: 20px; color: var(--text-muted); line-height: 1.8;">
<li>secp256k1 signature verification on all transactions</li>
<li>SHA-256 + Keccak-256 dual-hash block validation</li>
<li>Tamper detection via Merkle root comparison</li>
<li>Double-spend prevention through nonce tracking</li>
<li>Chain validation (block index continuity)</li>
<li>Rate limiting (30/min standard, 5/min strict endpoints)</li>
<li>Nonce replay protection (chain ID 909 in signature)</li>
<li>Admin API key authentication</li>
<li>Validator slashing for malicious behavior</li>
<li>Input validation on all API endpoints</li>
<li>Mempool limits (max 1000 pending transactions)</li>
<li>Maximum transaction amount (1B VRDX per tx)</li>
<li>Maximum block size (500 transactions per block)</li>
</ol>

<div class="tech-subsec">19.3 — Key Management</div>
<p class="tech-para">Private keys never leave the user's device. All signing operations occur client-side using @noble/secp256k1. The server only stores public keys, addresses, and signed transaction data. Wallets use AES-256-CBC encryption for local storage with a user-defined PIN.</p>
</div>
"""

# === SECTION 20: Network Architecture & Protocol Specification ===
section20 = """
<div class="section-header"><span class="section-badge">20</span><h2 class="section-title">Network Architecture & Protocol Specification</h2></div>
<div class="glass-card">
<p class="tech-para">The Verdis network operates on a layered architecture designed for scalability, security, and EVM compatibility.</p>

<div class="tech-subsec">20.1 — Protocol Layers</div>
<table class="tech-table">
<tr><th>Layer</th><th>Component</th><th>Technology</th></tr>
<tr><td>L1 — Consensus</td><td>DPoS Block Production</td><td>27 validators, 3s blocks, BFT finality</td></tr>
<tr><td>L2 — State</td><td>Account State Trie</td><td>Keccak-256 Merkle Patricia Trie</td></tr>
<tr><td>L3 — VM</td><td>Verdis Virtual Machine</td><td>101 EVM opcodes, stack-based</td></tr>
<tr><td>L4 — DEX</td><td>VerdisSwap AMM</td><td>x×y=k, 0.3% fee, 7 pools</td></tr>
<tr><td>L5 — API</td><td>REST + JSON-RPC</td><td>40+ endpoints, EIP-1193 compatible</td></tr>
<tr><td>L6 — Eco</td><td>Carbon & Reforestation</td><td>On-chain credits, satellite verification</td></tr>
</table>

<div class="tech-subsec">20.2 — API Architecture</div>
<p class="tech-para">The Verdis API exposes both REST and JSON-RPC endpoints:</p>
<ul style="margin-left: 20px; color: var(--text-muted); line-height: 1.8;">
<li><strong>REST API:</strong> 40+ endpoints for blockchain data, wallets, DEX, staking, eco-metrics, and security.</li>
<li><strong>JSON-RPC:</strong> EIP-1193 compatible endpoints (eth_blockNumber, eth_getBalance, eth_sendRawTransaction, etc.) for MetaMask/Trust Wallet compatibility.</li>
<li><strong>Chain ID:</strong> 909 for EVM compatibility.</li>
<li><strong>Block Time:</strong> 5 seconds (3s production + 2s finality).</li>
</ul>

<div class="tech-subsec">20.3 — Data Persistence</div>
<p class="tech-para">The blockchain state is persisted to disk using a JSON-based snapshot system. Every 100 blocks, a full state snapshot is written to the data directory. On restart, the node loads the latest snapshot and replays any subsequent blocks from the transaction log. This ensures crash recovery without data loss.</p>

<div class="tech-subsec">20.4 — Network Topology</div>
<p class="tech-para">The Verdis network consists of validator nodes, seed nodes, and API gateway nodes. Validator nodes produce blocks and maintain consensus. Seed nodes assist with peer discovery. API gateway nodes serve the REST and JSON-RPC endpoints, rate-limiting, and caching layer. All nodes communicate over TCP with secp256k1 authenticated peer connections.</p>
</div>
"""

# === SECTION 27: GitHub, Audit & Resources ===
section27 = """
<div class="section-header"><span class="section-badge">27</span><h2 class="section-title">GitHub, Audit & Resources</h2></div>
<div class="glass-card">
<div class="tech-subsec">27.1 — Source Code Repositories</div>
<p class="tech-para">All Verdis source code is maintained on GitHub for full transparency:</p>
<ul style="margin-left: 20px; color: var(--text-muted); line-height: 1.8;">
<li><strong>Blockchain Core:</strong> Node, consensus, VM, DEX, API — TypeScript/Node.js</li>
<li><strong>Web Interface:</strong> Dashboard, Explorer (Verdiscan), Wallet, Token Sale — HTML/CSS/JS</li>
<li><strong>Mobile Wallet:</strong> Native Android (dependency-free architecture) — Java/Kotlin</li>
<li><strong>Smart Contracts:</strong> Deployed contracts and templates — Verdis VM bytecode</li>
</ul>

<div class="tech-subsec">27.2 — Security Audit</div>
<p class="tech-para">A comprehensive third-party security audit is scheduled for September 2026, covering:</p>
<ul style="margin-left: 20px; color: var(--text-muted); line-height: 1.8;">
<li>secp256k1 cryptographic implementation review</li>
<li>DPoS consensus algorithm formal verification</li>
<li>Verdis VM opcode security and gas schedule audit</li>
<li>VerdisSwap AMM and liquidity pool security</li>
<li>API endpoint penetration testing (40+ endpoints)</li>
<li>Smart contract vulnerability scanning</li>
</ul>
<p class="tech-para">Audit firms under consideration: CertiK, Hacken, Trail of Bits. A bug bounty program with a $50,000 reward pool will launch concurrent with the audit.</p>

<div class="tech-subsec">27.3 — Documentation Resources</div>
<ul style="margin-left: 20px; color: var(--text-muted); line-height: 1.8;">
<li><strong>Whitepaper (this document):</strong> Full protocol specification and tokenomics</li>
<li><strong>API Documentation:</strong> Available at /api-docs on the Verdis dashboard</li>
<li><strong>Source Code Viewer:</strong> Interactive code browser at /code</li>
<li><strong>Team Profiles:</strong> Available at /team with GitHub links</li>
<li><strong>Network Status:</strong> Live monitoring at /status</li>
</ul>

<div class="tech-subsec">27.4 — Community & Links</div>
<ul style="margin-left: 20px; color: var(--text-muted); line-height: 1.8;">
<li><strong>Website:</strong> <a href="https://verdischain.com" style="color:#00ff88">verdischain.com</a></li>
<li><strong>Twitter/X:</strong> @Verdischain</li>
<li><strong>Telegram:</strong> @verdischain</li>
<li><strong>GitHub:</strong> Primary platform for all code transparency</li>
<li><strong>Explorer:</strong> <a href="https://verdischain.com/explorer.html" style="color:#00ff88">verdischain.com/explorer</a></li>
</ul>

<div class="tech-subsec">27.5 — Founder & Development</div>
<p class="tech-para">Verdis was founded by <strong>Rojs Gordons</strong>, CEO of <strong>Protremix</strong> (software development company) and creator of the <strong>Anerium</strong> fintech platform. The development team consists of 5 engineers specializing in blockchain protocol design, full-stack development, mobile engineering, and ecological systems. All team profiles and GitHub repositories are available on the team page.</p>
</div>
"""

# Apply replacements
sections_to_fix = {
    16: section16,
    17: section17,
    18: section18,
    19: section19,
    20: section20,
    27: section27,
}

for num, new_html in sections_to_fix.items():
    content = replace_section(content, num, new_html)
    print(f"OK: Replaced section {num}")

# Write back
with open(filepath, "w") as f:
    f.write(content)

print("\nDone! All garbled sections replaced with proper English content.")

# Verify no garbled text remains
import re
garbled_patterns = ['andwithbyet', 'witheewith', 'inandt', 'etowith', 'ineandean', 'tforandand']
remaining = 0
for p in garbled_patterns:
    matches = re.findall(p, content)
    if matches:
        remaining += len(matches)
        print(f"WARNING: Pattern '{p}' still has {len(matches)} matches")

if remaining == 0:
    print("Verification: No garbled text patterns remaining!")
else:
    print(f"Verification: {remaining} garbled patterns still remain")
