#!/usr/bin/env python3
"""Wire ZK proof system into the server with API endpoints"""

with open('/opt/verdis/app/dist/api/server.js') as f:
    server = f.read()

# 1. Add ZK proof endpoints
zk_endpoints = '''
        // === ZK PROOFS ===
        this.zkSystem = new (require("../core/zk-proofs")).ZKProofSystem();
        
        this.app.get("/api/zk/stats", (req, res) => {
            res.json(this.zkSystem.getStats());
        });
        
        this.app.post("/api/zk/range-proof", (req, res) => {
            try {
                const { value, max, blinding } = req.body;
                if (value === undefined || max === undefined) 
                    return res.status(400).json({ error: "value and max required" });
                const blindingFactor = blinding || '0'.repeat(64);
                const proof = this.zkSystem.generateRangeProof(value, max, blindingFactor);
                res.json({ success: true, proof });
            } catch (e) { res.status(500).json({ error: e.message }); }
        });
        
        this.app.post("/api/zk/verify-range", (req, res) => {
            try {
                const { proof } = req.body;
                const valid = this.zkSystem.verifyRangeProof(proof);
                res.json({ success: true, valid });
            } catch (e) { res.status(500).json({ error: e.message }); }
        });
        
        this.app.post("/api/zk/private-transfer", (req, res) => {
            try {
                const { senderAddress, recipientAddress, amount, senderBalance, blinding } = req.body;
                if (!senderAddress || !recipientAddress || amount === undefined)
                    return res.status(400).json({ error: "senderAddress, recipientAddress, amount required" });
                const balance = senderBalance || 999999999;
                const blindingFactor = blinding || '0'.repeat(64);
                const proof = this.zkSystem.createPrivateTransferProof(
                    senderAddress, recipientAddress, amount, balance, blindingFactor
                );
                res.json({ success: true, proof });
            } catch (e) { res.status(500).json({ error: e.message }); }
        });
        
        this.app.post("/api/zk/verify-transfer", (req, res) => {
            try {
                const { proof } = req.body;
                const valid = this.zkSystem.verifyPrivateTransferProof(proof);
                res.json({ success: true, valid });
            } catch (e) { res.status(500).json({ error: e.message }); }
        });
        
        this.app.post("/api/zk/state-proof", (req, res) => {
            try {
                const { address } = req.body;
                if (!address) return res.status(400).json({ error: "address required" });
                const balance = this.blockchain.getTokenSystem().getBalance(address);
                const nonce = 0;
                const proof = this.zkSystem.createStateProof(address, balance, nonce);
                res.json({ success: true, proof, committedBalance: balance });
            } catch (e) { res.status(500).json({ error: e.message }); }
        });
        
        this.app.post("/api/zk/verify-state", (req, res) => {
            try {
                const { proof } = req.body;
                const valid = this.zkSystem.verifyStateProof(proof, this.blockchain.getTokenSystem());
                res.json({ success: true, valid });
            } catch (e) { res.status(500).json({ error: e.message }); }
        }
        
'''

# Insert before the parallel exec stats endpoint
marker = 'this.app.get("/api/parallel-exec/stats"'
if marker in server:
    server = server.replace(marker, zk_endpoints + '\n        ' + marker, 1)
    print("1. Added ZK proof API endpoints")
else:
    # Try network/tps
    marker2 = 'this.app.get("/api/network/tps"'
    if marker2 in server:
        server = server.replace(marker2, zk_endpoints + '\n        ' + marker2, 1)
        print("1. Added ZK proof API endpoints (before network/tps)")
    else:
        print("1. ERROR: insertion point not found")

with open('/opt/verdis/app/dist/api/server.js', 'w') as f:
    f.write(server)
print("ZK proof system wired!")
