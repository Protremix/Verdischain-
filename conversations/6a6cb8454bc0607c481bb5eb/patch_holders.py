#!/usr/bin/env python3
"""Patch the server to add contract holders endpoint."""

with open("/opt/verdis/app/dist/api/server.js", "r") as f:
    c = f.read()

# 1. Add holders endpoint after the contract state endpoint
holders_endpoint = """        this.app.get('/api/contract/:id/holders', (req, res) => {
            const contract = this.contractManager.getContract(req.params.id);
            if (!contract) {
                res.status(404).json({ error: 'Contract not found' });
                return;
            }
            const holders = [];
            holders.push({
                address: contract.owner,
                balance: 0,
                role: 'owner',
                since: contract.deployedAt
            });
            if (contract.state && contract.state.size > 0) {
                for (const [key, value] of contract.state.entries()) {
                    if (typeof key === 'string' && key.startsWith('0x')) {
                        holders.push({
                            address: key,
                            balance: typeof value === 'number' ? value : 0,
                            role: 'holder',
                            since: contract.deployedAt
                        });
                    }
                }
            }
            const allWallets = this.walletManager.getAllWallets ? this.walletManager.getAllWallets() : [];
            for (const w of allWallets) {
                const addr = w.address || w.id;
                const bal = w.balance || 0;
                if (addr && !holders.find(h => h.address === addr) && bal > 0) {
                    holders.push({
                        address: addr,
                        balance: bal,
                        role: 'ecosystem',
                        since: contract.deployedAt
                    });
                }
            }
            res.json({
                contractId: contract.id,
                contractName: contract.name,
                holderCount: holders.length,
                holders: holders
            });
        });
"""

# Find the contract state endpoint and add holders after it
marker = "this.app.get('/api/contract/:id/state'"
idx = c.find(marker)
if idx != -1:
    next_endpoint = c.find("this.app.get(", idx + len(marker))
    if next_endpoint != -1:
        c = c[:next_endpoint] + holders_endpoint + "        " + c[next_endpoint:]
        print("Added /api/contract/:id/holders endpoint")
    else:
        print("ERROR: Could not find insertion point")
else:
    print("ERROR: Could not find state endpoint")

with open("/opt/verdis/app/dist/api/server.js", "w") as f:
    f.write(c)

print("Server patched successfully!")
