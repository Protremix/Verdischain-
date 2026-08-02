#!/usr/bin/env python3
"""Fix dashboard EVM badges and update AI chat answers."""

with open('/opt/verdis/app/dist/web/dashboard.html', 'r') as f:
    c = f.read()

# Fix the actual dashboard header
old = '<div class="explore-header"><h2>Smart Contracts</h2><p>Deploy and execute smart contracts on the Verdis Virtual Machine. Choose a template or write your own.</p></div>'
new = '<div class="explore-header"><h2>Smart Contracts \u2014 EVM Compatible</h2><p>Deploy and execute smart contracts on the EVM-compatible Verdis Virtual Machine. 69 opcodes, 256-bit arithmetic, REVERT with state rollback, reentrancy guards, and SHA3 (Keccak256).</p></div>'

if old in c:
    c = c.replace(old, new)
    print('Updated dashboard Smart Contracts header')
else:
    print('Header not found')

# Update AI chat answers about smart contracts
c = c.replace('Stack-based VM with 22 opcodes', 'EVM-compatible VM with 69 opcodes (256-bit arithmetic, REVERT, SHA3, reentrancy guards)')
c = c.replace('stack-based Virtual Machine with 22 opcodes', 'EVM-compatible Virtual Machine with 69 opcodes including 256-bit arithmetic, REVERT with state rollback, reentrancy guards, SHA3 (Keccak256), and EIP-150 gas forwarding')

# Add EVM security badges after the header
badges = '''
<div style="display:flex;flex-wrap:wrap;gap:6px;margin:12px 0">
  <span class="badge" style="font-size:10px;background:rgba(63,185,80,.15);color:#3fb950">256-bit Arithmetic</span>
  <span class="badge" style="font-size:10px;background:rgba(63,185,80,.15);color:#3fb950">Stack Limit 1024</span>
  <span class="badge" style="font-size:10px;background:rgba(63,185,80,.15);color:#3fb950">REVERT + Rollback</span>
  <span class="badge" style="font-size:10px;background:rgba(63,185,80,.15);color:#3fb950">Reentrancy Guard</span>
  <span class="badge" style="font-size:10px;background:rgba(63,185,80,.15);color:#3fb950">SHA3 Keccak256</span>
  <span class="badge" style="font-size:10px;background:rgba(63,185,80,.15);color:#3fb950">EIP-150 Gas</span>
  <span class="badge" style="font-size:10px;background:rgba(63,185,80,.15);color:#3fb950">CALL/STATICCALL</span>
</div>'''

# Find the contract section and add badges
c = c.replace(new, new + badges)

with open('/opt/verdis/app/dist/web/dashboard.html', 'w') as f:
    f.write(c)

print('Dashboard fully patched with EVM info')
