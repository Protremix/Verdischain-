#!/usr/bin/env python3
"""Add tokenomics + gas abstraction API endpoints to server.js"""

with open('/opt/verdis/app/dist/api/server.js') as f:
    content = f.read()

# Add endpoints before the AI section
marker = '// === AI AGENT REGISTRY ==='

new_endpoints = '''// === TOKENOMICS & GAS ABSTRACTION ===
        this.app.get("/api/tokenomics/info", (req, res) => {
            const ts = this.blockchain.getTokenSystem();
            res.json({
                maxSupply: ts.getMaxSupply(),
                totalSupply: ts.getTotalSupply(),
                blockReward: ts.getBlockReward(),
                feeBurnRate: ts.feeBurnRate || 0.5,
                totalFeesBurned: ts.totalFeesBurned || 0,
                totalFeesDistributed: ts.totalFeesDistributed || 0,
                treasuryAddress: ts.treasuryAddress,
                treasuryBalance: ts.getTreasuryBalance ? ts.getTreasuryBalance() : 0,
                circulatingSupply: ts.getTotalSupply() - (ts.totalFeesBurned || 0),
                rewardDistribution: { producer: 0.70, voters: 0.20, treasury: 0.10 },
                gasAbstractionEnabled: ts.gasAbstractionEnabled,
            });
        });
        this.app.post("/api/gas/sponsor", this.strictRateLimit.bind(this), (req, res) => {
            try {
                const { sponsor, privateKey, amount } = req.body;
                if (!sponsor || !privateKey || !amount)
                    return res.status(400).json({ error: "sponsor, privateKey, amount required" });
                const ts = this.blockchain.getTokenSystem();
                const wallet = this.walletManager.getAllWallets().find(w => w.address === sponsor);
                if (!wallet) return res.status(404).json({ error: "Wallet not found" });
                const result = ts.depositGasSponsorship(sponsor, amount);
                if (!result) return res.status(400).json({ error: "Insufficient balance" });
                res.json({ success: true, sponsor, amount, balance: ts.getGasSponsorshipBalance(sponsor) });
            } catch (e) { res.status(500).json({ error: e.message }); }
        });
        this.app.get("/api/gas/sponsor/:address", (req, res) => {
            const ts = this.blockchain.getTokenSystem();
            res.json({ sponsor: req.params.address, balance: ts.getGasSponsorshipBalance(req.params.address) });
        });
        this.app.post("/api/gas/sponsor/withdraw", this.strictRateLimit.bind(this), (req, res) => {
            try {
                const { sponsor, amount } = req.body;
                if (!sponsor || !amount) return res.status(400).json({ error: "sponsor, amount required" });
                const ts = this.blockchain.getTokenSystem();
                const result = ts.withdrawGasSponsorship(sponsor, amount);
                if (!result) return res.status(400).json({ error: "Insufficient sponsorship balance" });
                res.json({ success: true, remaining: ts.getGasSponsorshipBalance(sponsor) });
            } catch (e) { res.status(500).json({ error: e.message }); }
        });
        this.app.get("/api/treasury/balance", (req, res) => {
            const ts = this.blockchain.getTokenSystem();
            res.json({ address: ts.treasuryAddress, balance: ts.getTreasuryBalance() });
        });

'''

if marker in content:
    content = content.replace(marker, new_endpoints + marker, 1)
    print("Added tokenomics + gas abstraction endpoints")
else:
    print("ERROR: AI marker not found")

with open('/opt/verdis/app/dist/api/server.js', 'w') as f:
    f.write(content)
print("Done!")
