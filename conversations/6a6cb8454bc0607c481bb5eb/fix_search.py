#!/usr/bin/env python3
"""Patch explorer search to support partial address matching."""

filepath = "/opt/verdis/app/dist/api/server.js"
with open(filepath, "r") as f:
    content = f.read()

old_search_end = """            res.status(404).json({ error: 'Not found' });
        });
        // Explorer stats"""

new_search_end = """            // Partial address matching (prefix search)
            if (q.startsWith('0x') && q.length >= 4) {
                const allWallets = this.walletManager.getAllWallets();
                const allValidators = this.blockchain.getConsensus().getAllValidatorsList();
                const allAddrs = [
                    ...allWallets.map(w => w.address),
                    ...allValidators.map(v => v.address)
                ].filter(a => a && a.toLowerCase().startsWith(q.toLowerCase()));
                if (allAddrs.length === 1) {
                    const addr = allAddrs[0];
                    const bal = this.blockchain.getTokenSystem().getBalance(addr);
                    const chain = this.blockchain.getChain();
                    const txs = [];
                    for (const block of chain) {
                        for (const tx of block.transactions) {
                            if (tx.from === addr || tx.to === addr) {
                                txs.push({ ...tx, blockIndex: block.header.index, blockHash: block.hash });
                            }
                        }
                    }
                    const val = this.blockchain.getConsensus().getAllValidatorsList().find(v => v.address === addr);
                    res.json({
                        type: 'address',
                        data: {
                            address: addr,
                            balance: bal,
                            isValidator: !!val,
                            validatorInfo: val || null,
                            transactionCount: txs.length,
                            transactions: txs.slice(-20).reverse()
                        }
                    });
                    return;
                }
                if (allAddrs.length > 1) {
                    res.json({ type: 'addresses', data: allAddrs, count: allAddrs.length });
                    return;
                }
            }
            res.status(404).json({ error: 'Not found', query: q });
        });
        // Explorer stats"""

if old_search_end in content:
    content = content.replace(old_search_end, new_search_end)
    with open(filepath, "w") as f:
        f.write(content)
    print("OK: Explorer search patched with partial address matching")
else:
    print("FAILED: Could not find search endpoint end marker")
