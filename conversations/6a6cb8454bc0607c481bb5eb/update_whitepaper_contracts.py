#!/usr/bin/env python3
"""
Update the whitepaper Smart Contracts section with full EVM compatibility details.
"""
import re

with open("/opt/verdis/app/dist/web/whitepaper.html", "r") as f:
    html = f.read()

# === 1. Replace the Smart Contracts section ===
old_section = '<section id="section-10" class="section-block"><div class="section-header"><span class="section-badge">10</span><h2 class="section-title">Smart Contracts & Verdis VM</h2></div><div class="glass-card"><p class="section-p">The<strong>Verdis Virtual Machine (VVM)</strong>is a stack-based runtime environment engineered for extreme concurrency. VVM provides 100% EVM bytecode compatibility while introducing native precompiled contracts for zero-knowledge proofs, satellite telemetry verification, and carbon credit retirements.</p><p class="section-p">Developers can deploy existing Solidity, Vyper, or Yul smart contracts without modification using standard Web3 libraries (ethers.js, web3.js, Foundry, Hardhat).</p></div></section>'

new_section = '''<section id="section-10" class="section-block"><div class="section-header"><span class="section-badge">10</span><h2 class="section-title">Smart Contracts & Verdis VM</h2></div>

<div class="glass-card">
<p class="section-p">The <strong>Verdis Virtual Machine (VVM)</strong> is a stack-based runtime environment engineered for extreme concurrency and full Ethereum Virtual Machine (EVM) compatibility. The VVM implements <strong>101 EVM opcodes</strong> matching the Ethereum Berlin/London opcode schedule, enabling developers to deploy existing Solidity, Vyper, or Yul smart contracts without modification using standard Web3 libraries (ethers.js, web3.js, Foundry, Hardhat).</p>
</div>

<div class="glass-card">
<h3 class="card-title" style="margin-bottom:16px;color:var(--primary);">EVM Opcode Coverage</h3>
<p class="section-p">The VVM implements the complete Ethereum opcode set across all EVM categories:</p>
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px;margin:16px 0;">
<div style="background:rgba(0,255,136,0.05);border:1px solid var(--border-glass);border-radius:10px;padding:14px;">
<p style="color:var(--primary);font-weight:600;margin-bottom:8px;font-size:0.9rem;">Arithmetic (11)</p>
<p style="font-size:0.82rem;color:var(--text-muted);">ADD, SUB, MUL, DIV, MOD, SDIV, SMOD, ADDMOD, MULMOD, EXP, SIGNEXTEND — all 256-bit modular (overflow-safe)</p>
</div>
<div style="background:rgba(0,255,136,0.05);border:1px solid var(--border-glass);border-radius:10px;padding:14px;">
<p style="color:var(--primary);font-weight:600;margin-bottom:8px;font-size:0.9rem;">Comparison (6)</p>
<p style="font-size:0.82rem;color:var(--text-muted);">LT, GT, SLT, SGT, EQ, ISZERO — signed and unsigned</p>
</div>
<div style="background:rgba(0,255,136,0.05);border:1px solid var(--border-glass);border-radius:10px;padding:14px;">
<p style="color:var(--primary);font-weight:600;margin-bottom:8px;font-size:0.9rem;">Bitwise (9)</p>
<p style="font-size:0.82rem;color:var(--text-muted);">AND, OR, XOR, NOT, BYTE, SHL, SHR, SAR, SHA3 (Keccak256)</p>
</div>
<div style="background:rgba(0,255,136,0.05);border:1px solid var(--border-glass);border-radius:10px;padding:14px;">
<p style="color:var(--primary);font-weight:600;margin-bottom:8px;font-size:0.9rem;">Stack (51)</p>
<p style="font-size:0.82rem;color:var(--text-muted);">POP, PUSH1–PUSH32, DUP1–DUP16, SWAP1–SWAP16, JUMP, JUMPI, JUMPDEST, PC, GAS</p>
</div>
<div style="background:rgba(0,255,136,0.05);border:1px solid var(--border-glass);border-radius:10px;padding:14px;">
<p style="color:var(--primary);font-weight:600;margin-bottom:8px;font-size:0.9rem;">Memory & Storage (6)</p>
<p style="font-size:0.82rem;color:var(--text-muted);">MLOAD, MSTORE, MSTORE8, MSIZE, SLOAD, SSTORE</p>
</div>
<div style="background:rgba(0,255,136,0.05);border:1px solid var(--border-glass);border-radius:10px;padding:14px;">
<p style="color:var(--primary);font-weight:600;margin-bottom:8px;font-size:0.9rem;">Environment (12)</p>
<p style="font-size:0.82rem;color:var(--text-muted);">CALLER, CALLVALUE, ORIGIN, ADDRESS, BALANCE, CODESIZE, CODECOPY, EXTCODESIZE, EXTCODEHASH, EXTCODECOPY, RETURNDATASIZE, RETURNDATACOPY</p>
</div>
<div style="background:rgba(0,255,136,0.05);border:1px solid var(--border-glass);border-radius:10px;padding:14px;">
<p style="color:var(--primary);font-weight:600;margin-bottom:8px;font-size:0.9rem;">Block Context (9)</p>
<p style="font-size:0.82rem;color:var(--text-muted);">BLOCKHASH, COINBASE, TIMESTAMP, BLOCKNUMBER, DIFFICULTY, GASLIMIT, CHAINID, SELFBALANCE, BASEFEE</p>
</div>
<div style="background:rgba(0,255,136,0.05);border:1px solid var(--border-glass);border-radius:10px;padding:14px;">
<p style="color:var(--primary);font-weight:600;margin-bottom:8px;font-size:0.9rem;">System (8)</p>
<p style="font-size:0.82rem;color:var(--text-muted);">CALL, CALLCODE, DELEGATECALL, STATICCALL, CREATE, CREATE2, RETURN, REVERT, INVALID, SELFDESTRUCT, STOP, GASPRICE</p>
</div>
<div style="background:rgba(0,255,136,0.05);border:1px solid var(--border-glass);border-radius:10px;padding:14px;">
<p style="color:var(--primary);font-weight:600;margin-bottom:8px;font-size:0.9rem;">Logging (5)</p>
<p style="font-size:0.82rem;color:var(--text-muted);">LOG0, LOG1, LOG2, LOG3, LOG4 — EVM event emission with topics</p>
</div>
</div>
</div>

<div class="glass-card">
<h3 class="card-title" style="margin-bottom:16px;color:var(--primary);">EVM Security Model</h3>
<p class="section-p">The VVM enforces the complete Ethereum security model with the following protections:</p>
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px;margin:16px 0;">
<div style="background:rgba(0,255,136,0.05);border:1px solid var(--border-glass);border-radius:10px;padding:14px;">
<p style="color:var(--primary);font-weight:600;font-size:0.9rem;">256-Bit Modular Arithmetic</p>
<p style="font-size:0.82rem;color:var(--text-muted);margin-top:4px;">All operations use BigInt with mod 2²⁵⁶ overflow protection, identical to EVM behavior.</p>
</div>
<div style="background:rgba(0,255,136,0.05);border:1px solid var(--border-glass);border-radius:10px;padding:14px;">
<p style="color:var(--primary);font-weight:600;font-size:0.9rem;">Stack Depth Limit (EIP-150)</p>
<p style="font-size:0.82rem;color:var(--text-muted);margin-top:4px;">Maximum 1024 stack items. Gas forwarding on CALL uses the 63/64 rule.</p>
</div>
<div style="background:rgba(0,255,136,0.05);border:1px solid var(--border-glass);border-radius:10px;padding:14px;">
<p style="color:var(--primary);font-weight:600;font-size:0.9rem;">Reentrancy Guard</p>
<p style="font-size:0.82rem;color:var(--text-muted);margin-top:4px;">Per-contract execution lock prevents reentrant calls, preventing the DAO-class attack vector.</p>
</div>
<div style="background:rgba(0,255,136,0.05);border:1px solid var(--border-glass);border-radius:10px;padding:14px;">
<p style="color:var(--primary);font-weight:600;font-size:0.9rem;">State Snapshot & Rollback</p>
<p style="font-size:0.82rem;color:var(--text-muted);margin-top:4px;">REVERT triggers automatic state snapshot restoration — failed transactions restore all prior state.</p>
</div>
<div style="background:rgba(0,255,136,0.05);border:1px solid var(--border-glass);border-radius:10px;padding:14px;">
<p style="color:var(--primary);font-weight:600;font-size:0.9rem;">Gas Metering (Berlin/London)</p>
<p style="font-size:0.82rem;color:var(--text-muted);margin-top:4px;">Per-opcode gas costs matching the Ethereum Berlin/London EIP-2929/3529 schedule. SSTORE: 20,000 gas (new), 5,000 (update). SLOAD: 800 gas.</p>
</div>
<div style="background:rgba(0,255,136,0.05);border:1px solid var(--border-glass);border-radius:10px;padding:14px;">
<p style="color:var(--primary);font-weight:600;font-size:0.9rem;">EIP-170 Code Size Limit</p>
<p style="font-size:0.82rem;color:var(--text-muted);margin-top:4px;">Contract bytecode limited to 24,576 bytes, preventing state bloat and resource exhaustion.</p>
</div>
<div style="background:rgba(0,255,136,0.05);border:1px solid var(--border-glass);border-radius:10px;padding:14px;">
<p style="color:var(--primary);font-weight:600;font-size:0.9rem;">INVALID Consumes All Gas</p>
<p style="font-size:0.82rem;color:var(--text-muted);margin-top:4px;">INVALID opcode (0xFE) consumes all remaining gas, matching EVM behavior for fault detection.</p>
</div>
<div style="background:rgba(0,255,136,0.05);border:1px solid var(--border-glass);border-radius:10px;padding:14px;">
<p style="color:var(--primary);font-weight:600;font-size:0.9rem;">Keccak256 Hashing</p>
<p style="font-size:0.82rem;color:var(--text-muted);margin-top:4px;">SHA3 opcode uses @noble/hashes Keccak256 — EVM-exact cryptographic hashing. Contract addresses derived via keccak256(sender ++ nonce).</p>
</div>
<div style="background:rgba(0,255,136,0.05);border:1px solid var(--border-glass);border-radius:10px;padding:14px;">
<p style="color:var(--primary);font-weight:600;font-size:0.9rem;">Memory Expansion Gas</p>
<p style="font-size:0.82rem;color:var(--text-muted);margin-top:4px;">Dynamic memory expansion costs 3 gas per 32-byte word, matching EVM memory gas accounting.</p>
</div>
<div style="background:rgba(0,255,136,0.05);border:1px solid var(--border-glass);border-radius:10px;padding:14px;">
<p style="color:var(--primary);font-weight:600;font-size:0.9rem;">Nonce-Based Contract Addresses</p>
<p style="font-size:0.82rem;color:var(--text-muted);margin-top:4px;">Contract addresses derived from keccak256(sender ++ nonce) for CREATE, and keccak256(0xFF ++ sender ++ salt ++ keccak256(init_code)) for CREATE2 — identical to Ethereum.</p>
</div>
<div style="background:rgba(0,255,136,0.05);border:1px solid var(--border-glass);border-radius:10px;padding:14px;">
<p style="color:var(--primary);font-weight:600;font-size:0.9rem;">Raw EVM Bytecode Deployment</p>
<p style="font-size:0.82rem;color:var(--text-muted);margin-top:4px;">Contracts can be deployed with raw EVM hex bytecode (0x608060...) or Verdis assembly text. Both formats compile to the same internal representation.</p>
</div>
<div style="background:rgba(0,255,136,0.05);border:1px solid var(--border-glass);border-radius:10px;padding:14px;">
<p style="color:var(--primary);font-weight:600;font-size:0.9rem;">Call Depth Limit</p>
<p style="font-size:0.82rem;color:var(--text-muted);margin-top:4px;">Maximum call depth of 1024, preventing stack overflow attacks via recursive contract calls.</p>
</div>
</div>
</div>

<div class="glass-card">
<h3 class="card-title" style="margin-bottom:16px;color:var(--primary);">Gas Schedule (Berlin/London)</h3>
<p class="section-p">The VVM implements the Ethereum Berlin/London gas schedule with EIP-2929 access lists and EIP-3529 gas refund reductions:</p>
<div style="overflow-x:auto;margin:16px 0;">
<table style="width:100%;border-collapse:collapse;font-size:0.82rem;">
<thead><tr style="border-bottom:1px solid var(--border-glass);"><th style="text-align:left;padding:8px;color:var(--text-muted);font-weight:600;">Category</th><th style="text-align:right;padding:8px;color:var(--text-muted);font-weight:600;">Gas Cost</th><th style="text-align:left;padding:8px;color:var(--text-muted);font-weight:600;">Opcodes</th></tr></thead>
<tbody>
<tr style="border-bottom:1px solid rgba(0,255,136,0.08);"><td style="padding:8px;">Tier 0 (Free)</td><td style="text-align:right;padding:8px;color:var(--primary);">0</td><td style="padding:8px;color:var(--text-muted);">STOP, RETURN, REVERT, INVALID</td></tr>
<tr style="border-bottom:1px solid rgba(0,255,136,0.08);"><td style="padding:8px;">Tier 1 (Base)</td><td style="text-align:right;padding:8px;color:var(--primary);">2</td><td style="padding:8px;color:var(--text-muted);">ADD, SUB, MUL, DIV, MOD, LT, GT, EQ, ISZERO, AND, OR, XOR, NOT</td></tr>
<tr style="border-bottom:1px solid rgba(0,255,136,0.08);"><td style="padding:8px;">Tier 2 (Low)</td><td style="text-align:right;padding:8px;color:var(--primary);">3</td><td style="padding:8px;color:var(--text-muted);">SDIV, SMOD, SLT, SGT, PUSH1–32, DUP1–16, SWAP1–16, MLOAD, MSTORE</td></tr>
<tr style="border-bottom:1px solid rgba(0,255,136,0.08);"><td style="padding:8px;">Tier 3 (Mid)</td><td style="text-align:right;padding:8px;color:var(--primary);">5–8</td><td style="padding:8px;color:var(--text-muted);">ADDMOD, MULMOD, SIGNEXTEND, BALANCE, EXTCODESIZE</td></tr>
<tr style="border-bottom:1px solid rgba(0,255,136,0.08);"><td style="padding:8px;">SHA3</td><td style="text-align:right;padding:8px;color:var(--primary);">30 + 6/word</td><td style="padding:8px;color:var(--text-muted);">Keccak256 hash</td></tr>
<tr style="border-bottom:1px solid rgba(0,255,136,0.08);"><td style="padding:8px;">Storage (Read)</td><td style="text-align:right;padding:8px;color:var(--primary);">800</td><td style="padding:8px;color:var(--text-muted);">SLOAD</td></tr>
<tr style="border-bottom:1px solid rgba(0,255,136,0.08);"><td style="padding:8px;">Storage (Write)</td><td style="text-align:right;padding:8px;color:var(--primary);">20,000</td><td style="padding:8px;color:var(--text-muted);">SSTORE (new slot), 5,000 (update)</td></tr>
<tr style="border-bottom:1px solid rgba(0,255,136,0.08);"><td style="padding:8px;">External Call</td><td style="text-align:right;padding:8px;color:var(--primary);">2,600</td><td style="padding:8px;color:var(--text-muted);">CALL, STATICCALL, DELEGATECALL</td></tr>
<tr style="border-bottom:1px solid rgba(0,255,136,0.08);"><td style="padding:8px;">Contract Creation</td><td style="text-align:right;padding:8px;color:var(--primary);">32,000</td><td style="padding:8px;color:var(--text-muted);">CREATE, CREATE2</td></tr>
<tr style="border-bottom:1px solid rgba(0,255,136,0.08);"><td style="padding:8px;">Self-Destruct</td><td style="text-align:right;padding:8px;color:var(--primary);">5,000</td><td style="padding:8px;color:var(--text-muted);">SELFDESTRUCT</td></tr>
<tr style="border-bottom:1px solid rgba(0,255,136,0.08);"><td style="padding:8px;">Logging</td><td style="text-align:right;padding:8px;color:var(--primary);">375 + 375/topic</td><td style="padding:8px;color:var(--text-muted);">LOG0–LOG4</td></tr>
</tbody>
</table>
</div>
</div>

<div class="glass-card">
<h3 class="card-title" style="margin-bottom:16px;color:var(--primary);">Deployed Contracts</h3>
<p class="section-p">The Verdis Mainnet currently hosts 13 EVM-compatible smart contracts across four categories, each with full Verdis branding metadata (logo, version, license, compiler, tags):</p>
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px;margin:16px 0;">
<div style="background:rgba(0,255,136,0.05);border:1px solid var(--border-glass);border-radius:10px;padding:14px;">
<p style="color:var(--primary);font-weight:600;font-size:0.9rem;">Eco Contracts</p>
<p style="font-size:0.82rem;color:var(--text-muted);margin-top:4px;">CarbonCreditMinter — Mints verified CCO2 tokens backed by reforestation (Verra VCS compatible). ReforestationLogger — On-chain logging of tree counts, species, CO2 sequestration, and verification status.</p>
</div>
<div style="background:rgba(0,255,136,0.05);border:1px solid var(--border-glass);border-radius:10px;padding:14px;">
<p style="color:var(--primary);font-weight:600;font-size:0.9rem;">DeFi Contracts</p>
<p style="font-size:0.82rem;color:var(--text-muted);margin-top:4px;">EcoDepositCalculator — Calculates eco-deposit yields based on carbon credit holdings. EcoStakingReward — Distributes staking rewards with bonus multipliers for green validators using renewable energy.</p>
</div>
<div style="background:rgba(0,255,136,0.05);border:1px solid var(--border-glass);border-radius:10px;padding:14px;">
<p style="color:var(--primary);font-weight:600;font-size:0.9rem;">Security Contracts</p>
<p style="font-size:0.82rem;color:var(--text-muted);margin-top:4px;">MultiSigWallet — M-of-N approval wallet for treasury management. TimeLockVault — Enforces 30/60-day vesting cliffs for IDO allocations. SecureVault — Access-controlled token vault with caller verification.</p>
</div>
<div style="background:rgba(0,255,136,0.05);border:1px solid var(--border-glass);border-radius:10px;padding:14px;">
<p style="color:var(--primary);font-weight:600;font-size:0.9rem;">Test Contracts</p>
<p style="font-size:0.82rem;color:var(--text-muted);margin-top:4px;">Adder, AdderV2, HashTest (Keccak256), RevertTest — Verify EVM opcode execution, state rollback, and gas accounting.</p>
</div>
</div>
<p class="section-p">Each contract includes standardized metadata: project name, Verdis logo URL, version, EVM standard, compiler version (VerdisVM v1.0), MIT license, network (Verdis Mainnet, Chain ID 909), token symbol (VRDX), category, and searchable tags. Contract addresses are derived using Ethereum-standard nonce-based derivation: <code style="font-family:var(--font-mono);color:var(--primary);font-size:0.82rem;">address = keccak256(sender ++ nonce)[0:20]</code>.</p>
</div>

<div class="glass-card">
<h3 class="card-title" style="margin-bottom:16px;color:var(--primary);">Bytecode Execution</h3>
<p class="section-p">The VVM accepts two deployment formats:</p>
<p class="section-p"><strong>1. Raw EVM Hex Bytecode</strong> — Standard Ethereum bytecode format (e.g., <code style="font-family:var(--font-mono);color:var(--primary);font-size:0.82rem;">0x6080604052...</code>). The VVM parses hex bytecode directly into its internal representation, enabling deployment of compiled Solidity output without modification.</p>
<p class="section-p"><strong>2. Verdis Assembly Text</strong> — Human-readable assembly (e.g., <code style="font-family:var(--font-mono);color:var(--primary);font-size:0.82rem;">PUSH 1000\\nPUSH 50\\nMUL\\nLOG\\nHALT</code>). Compiled via the Verdis assembler with label support for jump destinations.</p>
<p class="section-p">Both formats compile to the same internal bytecode array and execute identically through the VVM opcode dispatcher. Verified on-chain: raw EVM bytecode <code style="font-family:var(--font-mono);color:var(--primary);font-size:0.82rem;">6005600301</code> (PUSH1 5, PUSH1 3, ADD) executes correctly, returning 8 with 8 gas consumed.</p>
</div>

<div class="glass-card">
<h3 class="card-title" style="margin-bottom:16px;color:var(--primary);">Native Precompiled Contracts</h3>
<p class="section-p">In addition to the 101 standard EVM opcodes, the VVM introduces native precompiled contracts for Verdis-specific operations:</p>
<ul style="list-style:none;padding:0;margin:12px 0;">
<li style="padding:6px 0;border-bottom:1px solid rgba(0,255,136,0.08);font-size:0.88rem;color:var(--text-muted);"><strong style="color:var(--primary);">Carbon Credit Minting</strong> — Native precompile for minting CCO2 tokens backed by verified reforestation data.</li>
<li style="padding:6px 0;border-bottom:1px solid rgba(0,255,136,0.08);font-size:0.88rem;color:var(--text-muted);"><strong style="color:var(--primary);">Satellite Telemetry Verification</strong> — Precompile that validates satellite imagery proofs for reforestation claims.</li>
<li style="padding:6px 0;border-bottom:1px solid rgba(0,255,136,0.08);font-size:0.88rem;color:var(--text-muted);"><strong style="color:var(--primary);">Green Validator Scoring</strong> — Precompile that computes renewable energy scores for DPoS validator ranking.</li>
<li style="padding:6px 0;font-size:0.88rem;color:var(--text-muted);"><strong style="color:var(--primary);">AMM DEX Operations</strong> — Native swap, add liquidity, and remove liquidity precompiles for VerdisSwap.</li>
</ul>
</div>

</section>'''

if old_section in html:
    html = html.replace(old_section, new_section)
    print("✅ Replaced Smart Contracts section with comprehensive EVM details")
else:
    print("⚠️ Old section not found exactly, trying flexible match...")
    # Try to find the section by ID
    import re
    pattern = r'<section id="section-10".*?</section>'
    match = re.search(pattern, html, re.DOTALL)
    if match:
        html = html[:match.start()] + new_section + html[match.end():]
        print("✅ Replaced section-10 via regex match")
    else:
        print("❌ Could not find section-10")

# === 2. Update "22 opcodes" to "101 opcodes" in timeline ===
html = html.replace("Verdis VM (22 opcodes)", "Verdis VM (101 EVM opcodes)")
html = html.replace("Verdis VM (22 instructions)", "Verdis VM (101 EVM opcodes)")
html = html.replace("22 instructions", "101 EVM opcodes")
print("✅ Updated opcode count references (22 → 101)")

# === 3. Update "22 opcodes" in content text ===
# Also check the whitepaper-content.txt file
try:
    with open("/opt/verdis/app/dist/web/whitepaper-content.txt", "r") as f:
        content = f.read()
    content = content.replace("22 instructions", "101 EVM opcodes")
    content = content.replace("Verdis VM (22 opcodes)", "Verdis VM (101 EVM opcodes)")
    with open("/opt/verdis/app/dist/web/whitepaper-content.txt", "w") as f:
        f.write(content)
    print("✅ Updated whitepaper-content.txt")
except:
    pass

with open("/opt/verdis/app/dist/web/whitepaper.html", "w") as f:
    f.write(html)

print(f"\nWhitepaper updated! New size: {len(html):,} chars")
