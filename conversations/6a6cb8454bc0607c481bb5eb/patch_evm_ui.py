#!/usr/bin/env python3
"""Add EVM security badges to dashboard and update audit report."""

# Patch dashboard
with open('/opt/verdis/app/dist/web/dashboard.html', 'r') as f:
    c = f.read()

old = '<h3 class="title-medium" style="margin-bottom: 12px;">Smart Contracts</h3>'
new = '<h3 class="title-medium" style="margin-bottom: 12px;">Smart Contracts \xe2\x80\x94 EVM Compatible</h3>\n        <div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px">\n          <span class="badge" style="font-size:10px;background:rgba(63,185,80,.15);color:#3fb950">256-bit Arithmetic</span>\n          <span class="badge" style="font-size:10px;background:rgba(63,185,80,.15);color:#3fb950">Stack Limit 1024</span>\n          <span class="badge" style="font-size:10px;background:rgba(63,185,80,.15);color:#3fb950">REVERT + Rollback</span>\n          <span class="badge" style="font-size:10px;background:rgba(63,185,80,.15);color:#3fb950">Reentrancy Guard</span>\n          <span class="badge" style="font-size:10px;background:rgba(63,185,80,.15);color:#3fb950">SHA3 (Keccak256)</span>\n          <span class="badge" style="font-size:10px;background:rgba(63,185,80,.15);color:#3fb950">EIP-150 Gas</span>\n          <span class="badge" style="font-size:10px;background:rgba(63,185,80,.15);color:#3fb950">CALL/STATICCALL</span>\n        </div>'.encode('utf-8').decode('utf-8')

if old in c:
    c = c.replace(old, new, 1)
    print('Added EVM badges to dashboard')

with open('/opt/verdis/app/dist/web/dashboard.html', 'w') as f:
    f.write(c)

# Patch audit report
with open('/opt/verdis/app/dist/web/audit-report.html', 'r') as f:
    c = f.read()

# Update title
c = c.replace('<h2>5. Smart Contract Virtual Machine</h2>', '<h2>5. Smart Contract Virtual Machine \xe2\x80\x94 EVM Compatible</h2>')

# Update opcode count
c = c.replace('Stack-based VM (22 opcodes)', 'EVM-compatible stack VM (69 opcodes)')

# Add EVM features after gas limit line
old_gas = '<div class="stat-row"><span class="key">Gas Limit</span><span class="val">1,000,000 per execution</span></div>'
evm_features = old_gas + """
<div class="stat-row"><span class="key">256-bit Arithmetic</span><span class="val">BigInt modular (mod 2^256) \xe2\x80\x94 overflow-safe</span></div>
<div class="stat-row"><span class="key">Stack Depth</span><span class="val">1024 max (EVM standard)</span></div>
<div class="stat-row"><span class="key">REVERT</span><span class="val">Full state rollback (snapshot/restore)</span></div>
<div class="stat-row"><span class="key">Reentrancy Guard</span><span class="val">Lock-based + call depth tracking</span></div>
<div class="stat-row"><span class="key">SHA3</span><span class="val">Keccak256 (@noble/hashes/sha3)</span></div>
<div class="stat-row"><span class="key">Gas Forwarding</span><span class="val">EIP-150 (63/64 rule)</span></div>
<div class="stat-row"><span class="key">Memory</span><span class="val">Expandable with gas costs</span></div>
<div class="stat-row"><span class="key">Context Opcodes</span><span class="val">CALLER, CALLVALUE, ORIGIN, ADDRESS, BALANCE</span></div>
<div class="stat-row"><span class="key">Block Context</span><span class="val">BLOCKNUMBER, TIMESTAMP, BLOCKHASH, CHAINID</span></div>
<div class="stat-row"><span class="key">Call Types</span><span class="val">CALL, STATICCALL, DELEGATECALL</span></div>"""

c = c.replace(old_gas, evm_features)

with open('/opt/verdis/app/dist/web/audit-report.html', 'w') as f:
    f.write(c)

print('Updated audit report with EVM features')
print('Done!')
