#!/usr/bin/env python3
"""Fix explorer search to include token system addresses and deduplicate."""

filepath = "/opt/verdis/app/dist/api/server.js"
with open(filepath, "r") as f:
    content = f.read()

old = """            // Partial address matching (prefix search)
            if (q.startsWith('0x') && q.length >= 4) {
                const allWallets = this.walletManager.getAllWallets();
                const allValidators = this.blockchain.getConsensus().getAllValidatorsList();
                const allAddrs = [
                    ...allWallets.map(w => w.address),
                    ...allValidators.map(v => v.address)
                ].filter(a => a && a.toLowerCase().startsWith(q.toLowerCase()));
                if (allAddrs.length === 1) {"""

new = """            // Partial address matching (prefix search)
            if (q.startsWith('0x') && q.length >= 4) {
                const allWallets = this.walletManager.getAllWallets();
                const allValidators = this.blockchain.getConsensus().getAllValidatorsList();
                const balancesMap = this.blockchain.getTokenSystem().getBalancesMap();
                const balanceAddrs = balancesMap ? Array.from(balancesMap.keys()) : [];
                const allAddrs = [
                    ...new Set([
                        ...allWallets.map(w => w.address),
                        ...allValidators.map(v => v.address),
                        ...balanceAddrs
                    ])
                ].filter(a => a && a.toLowerCase().startsWith(q.toLowerCase()));
                if (allAddrs.length === 1) {"""

if old in content:
    content = content.replace(old, new)
    with open(filepath, "w") as f:
        f.write(content)
    print("OK: Search patched with token system addresses + dedup")
else:
    print("FAILED: Could not find search pattern")
