#!/usr/bin/env python3
"""Fix persistence: restore tokenSystem stakes Map from saved state"""

with open('/opt/verdis/app/dist/core/persistence.js') as f:
    content = f.read()

# Add stake restoration after balance restoration
old = """    for (const [addr, bal] of Object.entries(state.balances)) {
        tokenSystem.setBalance(addr, bal);
    }
    // Restore max supply
    tokenSystem.maxSupply = state.maxSupply;"""

new = """    for (const [addr, bal] of Object.entries(state.balances)) {
        tokenSystem.setBalance(addr, bal);
    }
    // Restore stakes (tokenSystem staking positions)
    if (state.stakes) {
        for (const [addr, staked] of Object.entries(state.stakes)) {
            if (staked > 0) {
                tokenSystem.stakes.set(addr, staked);
            }
        }
    }
    // Restore max supply
    tokenSystem.maxSupply = state.maxSupply;"""

if old in content:
    content = content.replace(old, new)
    print("1. Added tokenSystem stakes restoration")
else:
    print("1. ERROR: balance restore not found")

# Also add getStaked method check — does TokenSystem already have it?
# Yes, it does (we confirmed earlier). Let's also add a getStaked helper to wallet
# Actually, let's also make sure the stakes are saved for all addresses, not just wallet addresses

# Fix the export to also save stakes from the stakes Map directly
old_export = """    // Export stakes (staking positions)
    const stakes = {};
    // TokenSystem doesn't expose stakes map directly, but we can get them from wallets
    for (const w of walletManager.getAllWallets()) {
        stakes[w.address] = tokenSystem.getStaked(w.address);
    }"""

new_export = """    // Export stakes (staking positions)
    const stakes = {};
    // Export from tokenSystem stakes Map directly
    if (tokenSystem.stakes && tokenSystem.stakes instanceof Map) {
        for (const [addr, amount] of tokenSystem.stakes.entries()) {
            stakes[addr] = amount;
        }
    }
    // Also check wallet staked fields for any not in the Map
    for (const w of walletManager.getAllWallets()) {
        if (stakes[w.address] === undefined) {
            stakes[w.address] = tokenSystem.getStaked(w.address);
        }
    }"""

if old_export in content:
    content = content.replace(old_export, new_export)
    print("2. Fixed stakes export to use tokenSystem.stakes Map directly")
else:
    print("2. ERROR: stakes export not found")

with open('/opt/verdis/app/dist/core/persistence.js', 'w') as f:
    f.write(content)
print("Persistence fixed!")
