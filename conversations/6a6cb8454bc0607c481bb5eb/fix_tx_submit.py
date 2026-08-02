#!/usr/bin/env python3
"""Fix /api/transaction/submit to properly construct and submit transactions."""

filepath = "/opt/verdis/app/dist/api/server.js"
with open(filepath, "r") as f:
    content = f.read()

old_alias = """        this.app.post('/api/transaction/submit', this.strictRateLimit.bind(this), (req, res) => {
            // Alias for Android app compatibility - delegates to /api/transaction/send logic
            const { from, to, amount, fee, nonce, signature, publicKey } = req.body;
            try {
                const tx = this.blockchain.createTransaction(from, to, parseFloat(amount), parseFloat(fee || 0), parseInt(nonce || 0), signature, publicKey);
                const added = this.blockchain.getMempool().addTransaction(tx, this.blockchain.getTokenSystem().getBalancesMap());
                if (!added) { res.status(400).json({ success: false, error: 'Transaction rejected by mempool' }); return; }
                res.json({ success: true, txId: tx.id, hash: tx.hash, message: 'Transaction submitted to mempool' });
            } catch (error) { res.status(400).json({ success: false, error: error.message }); }
        });"""

new_alias = """        this.app.post('/api/transaction/submit', this.strictRateLimit.bind(this), (req, res) => {
            // Android app compatibility: accepts pre-signed transactions with {from, to, amount, fee, nonce, signature, publicKey}
            const { from, to, amount, fee, nonce, signature, publicKey, data } = req.body;
            try {
                if (!from || !to) { res.status(400).json({ success: false, error: 'Sender and recipient are required' }); return; }
                const amt = parseFloat(amount);
                if (isNaN(amt) || amt <= 0) { res.status(400).json({ success: false, error: 'Amount must be greater than zero' }); return; }
                const f = parseFloat(fee || 1);
                const n = parseInt(nonce) || Date.now();
                const payload = `${from}:${to}:${amt}:${f}:${n}:${data || ''}`;
                const { sha256 } = require('../crypto');
                const txId = sha256(payload);
                const tx = {
                    id: txId,
                    from: from,
                    publicKey: publicKey || from,
                    to: to,
                    amount: amt,
                    fee: f,
                    timestamp: Date.now(),
                    nonce: n,
                    data: data || null,
                    signature: signature || 'unsigned',
                    recovery: 0
                };
                const result = this.blockchain.submitTransaction(tx);
                if (!result.success) {
                    res.status(400).json({ success: false, error: result.error });
                    return;
                }
                res.json({ success: true, txId: tx.id, hash: tx.id, message: 'Transaction submitted to mempool' });
            } catch (error) {
                res.status(400).json({ success: false, error: error.message });
            }
        });"""

if old_alias in content:
    content = content.replace(old_alias, new_alias)
    with open(filepath, "w") as f:
        f.write(content)
    print("OK: Fixed /api/transaction/submit endpoint")
else:
    print("FAILED: Could not find old alias block")
