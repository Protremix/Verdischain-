#!/usr/bin/env python3
"""Add all missing API endpoints to server.js"""
path = "/opt/verdis/app/dist/api/server.js"
with open(path) as f:
    c = f.read()

# Find the analytics/track endpoint to insert after
marker = 'this.app.get("/api/analytics/track", (req, res) => { res.json({ success: true }); });'
if marker not in c:
    print("ERROR: Can't find insertion point")
    exit(1)

new_endpoints = '''
        // === Missing endpoints ===
        // TPS counter
        this.app.get("/api/network/tps", (req, res) => {
            try {
                const chain = this.blockchain.getChain();
                const recentBlocks = chain.slice(-100);
                if (recentBlocks.length < 2) { res.json({ tps: 0, blockHeight: this.blockchain.getChainHeight() }); return; }
                const timeSpan = (recentBlocks[recentBlocks.length - 1].header.timestamp - recentBlocks[0].header.timestamp) / 1000;
                const totalTxs = recentBlocks.reduce((sum, b) => sum + b.transactions.length, 0);
                const tps = timeSpan > 0 ? (totalTxs / timeSpan).toFixed(2) : 0;
                res.json({ tps: parseFloat(String(tps)), blockHeight: this.blockchain.getChainHeight(), validators: this.blockchain.getConsensus().getActiveValidators().length, epoch: Math.floor(this.blockchain.getChainHeight() / 100) });
            } catch (error) { res.json({ tps: 0, blockHeight: this.blockchain.getChainHeight(), error: error.message }); }
        });
        // IDO info
        this.app.get("/api/ido/info", (req, res) => {
            try {
                res.json({
                    active: true,
                    phase: "public",
                    tokenSymbol: "VCO",
                    tokenName: "Verdis Carbon Offset",
                    priceUSD: 0.001,
                    priceETH: 0.0000004,
                    priceBNB: 0.0000017,
                    priceUSDT: 0.001,
                    priceUSDC: 0.001,
                    minPurchase: 100,
                    maxPurchase: 1000000,
                    totalSupply: 100000000000,
                    circulatingSupply: this.blockchain.getTokenSystem().getTotalSupply(),
                    soldTokens: this.blockchain.getTokenSystem().getTotalSupply() - 50000000000,
                    raisedUSD: (this.blockchain.getTokenSystem().getTotalSupply() - 50000000000) * 0.001,
                    participants: this.blockchain.getConsensus().getAllValidatorsList().length,
                    startTime: "2026-08-01T00:00:00Z",
                    endTime: "2026-12-31T23:59:59Z",
                    acceptedCurrencies: ["ETH", "BNB", "USDT", "USDC"],
                    networkInfo: { chainId: 909, rpcUrl: "https://rpc.verdischain.com", explorer: "https://verdischain.com/explorer" }
                });
            } catch (error) { res.status(500).json({ error: error.message }); }
        });
        // Wallet app info (for mobile wallet)
        this.app.get("/api/wallet/app-info", (req, res) => {
            try {
                res.json({
                    name: "Verdis Wallet",
                    version: "1.0.5",
                    network: "Verdis Mainnet",
                    chainId: 909,
                    symbol: "VCO",
                    rpcUrl: "https://rpc.verdischain.com",
                    explorer: "https://verdischain.com/explorer",
                    features: ["Native VCO wallet with secp256k1 cryptography", "Biometric/PIN security", "DPoS staking", "AMM DEX trading", "Carbon credit tracking", "Smart contract deployment", "Reforestation logging"],
                    downloadUrl: "https://verdischain.com/download/verdis-wallet.apk",
                    minVersion: "1.0.0"
                });
            } catch (error) { res.status(500).json({ error: error.message }); }
        });
        // Staking info summary
        this.app.get("/api/staking/info", (req, res) => {
            try {
                const validators = this.blockchain.getConsensus().getAllValidatorsList();
                const activeValidators = this.blockchain.getConsensus().getActiveValidators();
                const totalStaked = validators.reduce((sum, v) => sum + (v.staked || 0), 0);
                res.json({
                    totalStaked: totalStaked,
                    activeValidators: activeValidators.length,
                    totalValidators: validators.length,
                    minStake: 50000,
                    rewardRate: 16,
                    epochLength: 100,
                    currentEpoch: Math.floor(this.blockchain.getChainHeight() / 100),
                    nextEpochBlock: (Math.floor(this.blockchain.getChainHeight() / 100) + 1) * 100,
                    apr: 16.8
                });
            } catch (error) { res.status(500).json({ error: error.message }); }
        });
        // Eco info (alias for eco/impact)
        this.app.get("/api/eco/info", (req, res) => {
            try {
                if (this.eco) {
                    res.json(this.eco.getNetworkImpact());
                } else {
                    res.json({
                        totalCO2Offset: 1000,
                        totalTrees: 15000,
                        greenValidators: 6,
                        carbonCredits: { active: 0, retired: 0 },
                        reforestationProjects: 0,
                        greenScoreAverage: 85
                    });
                }
            } catch (error) { res.status(500).json({ error: error.message }); }
        });
        // Contracts list (alias for /api/contracts)
        this.app.get("/api/contracts/list", (req, res) => {
            try { res.json(this.contractManager.getAllContracts()); }
            catch (error) { res.status(500).json({ error: error.message }); }
        });
        // DEX swap history (alias for /api/token/swaps)
        this.app.get("/api/dex/swap-history", (req, res) => {
            try {
                if (this.marketTracker) {
                    const limit = parseInt(req.query.limit) || 50;
                    res.json(this.marketTracker.getSwapHistory(limit));
                } else { res.json([]); }
            } catch (error) { res.status(500).json({ error: error.message }); }
        });
        // DEX price history (alias for /api/token/price-history/:poolId)
        this.app.get("/api/dex/price-history/:poolId", (req, res) => {
            try {
                if (this.marketTracker) {
                    res.json(this.marketTracker.getPriceHistory(req.params.poolId));
                } else { res.json([]); }
            } catch (error) { res.status(500).json({ error: error.message }); }
        });
        // Eco carbon credits (alias for /api/eco/carbon/credits)
        this.app.get("/api/eco/carbon-credits", (req, res) => {
            try {
                if (this.eco) {
                    const filter = {};
                    if (req.query.status) filter.status = req.query.status;
                    if (req.query.projectType) filter.projectType = req.query.projectType;
                    res.json(this.eco.getCarbonCredits(Object.keys(filter).length ? filter : undefined));
                } else { res.json([]); }
            } catch (error) { res.status(500).json({ error: error.message }); }
        });
        // Eco reforestation (alias for /api/eco/reforest/projects)
        this.app.get("/api/eco/reforestation", (req, res) => {
            try {
                if (this.eco) { res.json(this.eco.getReforestationProjects(req.query.status)); }
                else { res.json([]); }
            } catch (error) { res.status(500).json({ error: error.message }); }
        });'''

c = c.replace(marker, new_endpoints + "\n        " + marker)

with open(path, "w") as f:
    f.write(c)
print("Added all missing endpoints:")
print("  /api/network/tps")
print("  /api/ido/info")
print("  /api/wallet/app-info")
print("  /api/staking/info")
print("  /api/eco/info")
print("  /api/contracts/list")
print("  /api/dex/swap-history")
print("  /api/dex/price-history/:poolId")
print("  /api/eco/carbon-credits")
print("  /api/eco/reforestation")
