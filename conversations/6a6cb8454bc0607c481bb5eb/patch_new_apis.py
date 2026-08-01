#!/usr/bin/env python3
"""Add Name Service, Fraud Detection, and Account Abstraction API endpoints"""

with open('/opt/verdis/app/dist/api/server.js') as f:
    content = f.read()

marker = '// === TOKENOMICS & GAS ABSTRACTION ==='

new_endpoints = '''// === NAME SERVICE (Human-Readable Addresses) ===
        this.app.post("/api/vns/register", this.strictRateLimit.bind(this), (req, res) => {
            try {
                const { name, ownerAddress } = req.body;
                const result = this.nameService.register(name, ownerAddress);
                if (!result.success) return res.status(400).json({ error: result.error });
                res.json({ success: true, record: result.record });
            } catch (e) { res.status(500).json({ error: e.message }); }
        });
        this.app.get("/api/vns/resolve/:name", (req, res) => {
            const address = this.nameService.resolve(req.params.name);
            if (!address) return res.status(404).json({ error: "Name not found" });
            res.json({ name: req.params.name, address });
        });
        this.app.get("/api/vns/reverse/:address", (req, res) => {
            const name = this.nameService.reverseResolve(req.params.address);
            res.json({ address: req.params.address, name });
        });
        this.app.post("/api/vns/transfer", this.strictRateLimit.bind(this), (req, res) => {
            try {
                const { name, currentOwner, newOwner } = req.body;
                const result = this.nameService.transfer(name, currentOwner, newOwner);
                if (!result.success) return res.status(400).json({ error: result.error });
                res.json({ success: true });
            } catch (e) { res.status(500).json({ error: e.message }); }
        });
        this.app.post("/api/vns/text-record", this.strictRateLimit.bind(this), (req, res) => {
            try {
                const { name, ownerAddress, key, value } = req.body;
                const result = this.nameService.setTextRecord(name, ownerAddress, key, value);
                if (!result.success) return res.status(400).json({ error: result.error });
                res.json({ success: true });
            } catch (e) { res.status(500).json({ error: e.message }); }
        });
        this.app.post("/api/vns/renew", this.strictRateLimit.bind(this), (req, res) => {
            try {
                const { name, ownerAddress } = req.body;
                const result = this.nameService.renew(name, ownerAddress);
                if (!result.success) return res.status(400).json({ error: result.error });
                res.json({ success: true, expiresAt: result.expiresAt });
            } catch (e) { res.status(500).json({ error: e.message }); }
        });
        this.app.get("/api/vns/names", (req, res) => {
            res.json(this.nameService.getAllNames());
        });
        this.app.get("/api/vns/names/:address", (req, res) => {
            res.json(this.nameService.getNamesByOwner(req.params.address));
        });
        this.app.get("/api/vns/stats", (req, res) => {
            res.json(this.nameService.getStats());
        });

        // === FRAUD DETECTION ===
        this.app.post("/api/fraud/analyze", (req, res) => {
            try {
                const tx = req.body;
                const risk = this.fraudDetection.analyzeTransaction(tx);
                res.json(risk);
            } catch (e) { res.status(500).json({ error: e.message }); }
        });
        this.app.get("/api/fraud/alerts", (req, res) => {
            const limit = parseInt(req.query.limit) || 50;
            res.json(this.fraudDetection.getAlerts(limit));
        });
        this.app.get("/api/fraud/stats", (req, res) => {
            res.json(this.fraudDetection.getStats());
        });
        this.app.post("/api/fraud/blacklist", this.requireAdminAuth.bind(this), (req, res) => {
            try {
                const { address, reason } = req.body;
                this.fraudDetection.blacklist(address, reason);
                res.json({ success: true });
            } catch (e) { res.status(500).json({ error: e.message }); }
        });
        this.app.post("/api/fraud/whitelist", this.requireAdminAuth.bind(this), (req, res) => {
            try {
                const { address } = req.body;
                this.fraudDetection.whitelist(address);
                res.json({ success: true });
            } catch (e) { res.status(500).json({ error: e.message }); }
        });
        this.app.get("/api/fraud/check/:address", (req, res) => {
            res.json({ address: req.params.address, blacklisted: this.fraudDetection.isBlacklisted(req.params.address) });
        });

        // === ACCOUNT ABSTRACTION (Smart Wallets) ===
        this.app.post("/api/aa/wallet/create", this.strictRateLimit.bind(this), (req, res) => {
            try {
                const { ownerAddress, config } = req.body;
                const result = this.accountAbstraction.createSmartWallet(ownerAddress, config);
                if (!result.success) return res.status(400).json({ error: "Failed to create smart wallet" });
                res.json(result);
            } catch (e) { res.status(500).json({ error: e.message }); }
        });
        this.app.get("/api/aa/wallet/:address", (req, res) => {
            const wallet = this.accountAbstraction.getSmartWallet(req.params.address);
            if (!wallet) return res.status(404).json({ error: "Smart wallet not found" });
            res.json(wallet);
        });
        this.app.post("/api/aa/guardian/add", this.strictRateLimit.bind(this), (req, res) => {
            try {
                const { walletAddress, ownerAddress, guardianAddress } = req.body;
                const result = this.accountAbstraction.addGuardian(walletAddress, ownerAddress, guardianAddress);
                if (!result.success) return res.status(400).json({ error: result.error });
                res.json(result);
            } catch (e) { res.status(500).json({ error: e.message }); }
        });
        this.app.post("/api/aa/recovery/initiate", this.strictRateLimit.bind(this), (req, res) => {
            try {
                const { walletAddress, newOwnerAddress } = req.body;
                const result = this.accountAbstraction.initiateRecovery(walletAddress, newOwnerAddress);
                if (!result.success) return res.status(400).json({ error: result.error });
                res.json(result);
            } catch (e) { res.status(500).json({ error: e.message }); }
        });
        this.app.post("/api/aa/recovery/approve", this.strictRateLimit.bind(this), (req, res) => {
            try {
                const { walletAddress, guardianAddress } = req.body;
                const result = this.accountAbstraction.approveRecovery(walletAddress, guardianAddress);
                if (!result.success) return res.status(400).json({ error: result.error });
                res.json(result);
            } catch (e) { res.status(500).json({ error: e.message }); }
        });
        this.app.post("/api/aa/session/create", this.strictRateLimit.bind(this), (req, res) => {
            try {
                const { walletAddress, ownerAddress, dappContract, permissions, expiryMinutes } = req.body;
                const result = this.accountAbstraction.createSessionKey(walletAddress, ownerAddress, dappContract, permissions, expiryMinutes);
                if (!result.success) return res.status(400).json({ error: result.error });
                res.json(result);
            } catch (e) { res.status(500).json({ error: e.message }); }
        });
        this.app.post("/api/aa/session/validate", (req, res) => {
            try {
                const { sessionAddress, contractId, operation, amount } = req.body;
                const result = this.accountAbstraction.validateSessionAction(sessionAddress, contractId, operation, amount || 0);
                res.json(result);
            } catch (e) { res.status(500).json({ error: e.message }); }
        });
        this.app.post("/api/aa/session/revoke", this.strictRateLimit.bind(this), (req, res) => {
            try {
                const { sessionAddress, ownerAddress } = req.body;
                const result = this.accountAbstraction.revokeSessionKey(sessionAddress, ownerAddress);
                if (!result.success) return res.status(400).json({ error: result.error });
                res.json(result);
            } catch (e) { res.status(500).json({ error: e.message }); }
        });
        this.app.get("/api/aa/sessions", (req, res) => {
            res.json(this.accountAbstraction.getActiveSessions());
        });
        this.app.post("/api/aa/spend-check", (req, res) => {
            try {
                const { walletAddress, amount } = req.body;
                const result = this.accountAbstraction.checkSpendLimit(walletAddress, amount);
                res.json(result);
            } catch (e) { res.status(500).json({ error: e.message }); }
        });
        this.app.get("/api/aa/stats", (req, res) => {
            res.json(this.accountAbstraction.getStats());
        });

'''

if marker in content:
    content = content.replace(marker, new_endpoints + marker, 1)
    print("Added Name Service, Fraud Detection, and Account Abstraction endpoints")
else:
    print("ERROR: marker not found")

with open('/opt/verdis/app/dist/api/server.js', 'w') as f:
    f.write(content)
print("Done!")
