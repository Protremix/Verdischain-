import sys

with open("/opt/verdis/app/dist/api/server.js", "r") as f:
    content = f.read()

# === 1. ENHANCE DEX POOLS ENDPOINT ===
old_pools = """        this.app.get('/api/dex/pools', (req, res) => {
            const pools = this.dex.getAllPools().map(p => ({
                ...p,
                pair: `${p.tokenA === 'VRDX' ? 'VRDX' : p.tokenA}/${p.tokenB === 'VRDX' ? 'VRDX' : p.tokenB}`
            }));
            res.json(pools);
        });"""

new_pools = """        this.app.get('/api/dex/pools', (req, res) => {
            const swapHistory = this.marketTracker ? (this.marketTracker.getSwapHistory(10000) || []) : [];
            const pools = this.dex.getAllPools().map(p => {
                const price = p.reserveA > 0 ? p.reserveB / p.reserveA : 0;
                const tvl = p.reserveA + p.reserveB;
                const poolSwaps = swapHistory.filter(s => s.poolId === p.id);
                const swapCount = poolSwaps.length;
                const volume24h = poolSwaps.reduce((sum, s) => sum + (s.amountInUSD || s.amountIn || 0), 0);
                return {
                    ...p,
                    pair: p.tokenA + '/' + p.tokenB,
                    price: price,
                    tvl: tvl,
                    swapCount: swapCount,
                    volume24h: volume24h,
                    priceFormatted: price.toFixed(6),
                    tvlFormatted: tvl.toLocaleString(),
                };
            });
            res.json(pools);
        });"""

if old_pools in content:
    content = content.replace(old_pools, new_pools)
    print("DEX pools endpoint enhanced")
else:
    print("WARNING: DEX pools pattern not found")

# === 2. ENHANCE VALIDATORS ENDPOINT ===
old_validators = """        this.app.get('/api/validators', (req, res) => {
            res.json(this.blockchain.getConsensus().getAllValidatorsList());
        });"""

new_validators = """        this.app.get('/api/validators', (req, res) => {
            const validators = this.blockchain.getConsensus().getAllValidatorsList();
            const greenScores = this.eco.getAllGreenScores();
            const greenMap = new Map();
            for (const gs of greenScores) {
                greenMap.set(gs.address, gs);
            }
            const enriched = validators.map(v => {
                const gs = greenMap.get(v.address) || {};
                return {
                    ...v,
                    active: v.isProducer || false,
                    greenScore: gs.score || 0,
                    energySource: gs.energySource || 'Unknown',
                    renewableEnergy: gs.renewableEnergy || false,
                    carbonOffset: gs.carbonOffset || 0,
                    treesPlanted: gs.treesPlanted || 0,
                };
            });
            res.json(enriched);
        });"""

if old_validators in content:
    content = content.replace(old_validators, new_validators)
    print("Validators endpoint enhanced")
else:
    print("WARNING: Validators pattern not found")

# === 3. ADD ECO STATS ENDPOINT ===
old_eco = "        this.app.get('/api/eco/impact', (req, res) => { res.json(this.eco.getNetworkImpact()); });"

new_eco = """        this.app.get('/api/eco/impact', (req, res) => { res.json(this.eco.getNetworkImpact()); });
        this.app.get('/api/eco/stats', (req, res) => {
            const impact = this.eco.getNetworkImpact();
            const carbonCredits = this.eco.getCarbonCredits();
            const reforestationProjects = this.eco.getReforestationProjects();
            const greenScores = this.eco.getAllGreenScores();
            const totalCredits = carbonCredits.reduce((s, c) => s + c.amount, 0);
            const retiredCredits = carbonCredits.filter(c => c.status === 'retired').length;
            const activeCredits = carbonCredits.filter(c => c.status === 'active' || c.status === 'verified').length;
            const totalTrees = reforestationProjects.reduce((s, p) => s + (p.treesPlanted || 0), 0);
            const totalCO2 = reforestationProjects.reduce((s, p) => s + (p.co2Sequestered || 0), 0);
            const totalArea = reforestationProjects.reduce((s, p) => s + (p.area || 0), 0);
            res.json({
                totalCO2Offset: impact.totalCO2Offset || totalCO2,
                totalTrees: impact.totalTrees || totalTrees,
                totalArea: impact.totalArea || totalArea,
                greenValidators: impact.greenValidators || greenScores.length,
                creditsRetired: impact.creditsRetired || retiredCredits,
                creditsActive: activeCredits,
                creditsTotal: carbonCredits.length,
                totalCreditAmount: totalCredits,
                reforestationProjects: reforestationProjects.length,
                greenScores: greenScores,
                carbonCredits: carbonCredits,
                reforestationData: reforestationProjects,
            });
        });"""

if old_eco in content:
    content = content.replace(old_eco, new_eco)
    print("Eco stats endpoint added")
else:
    print("WARNING: Eco impact pattern not found")

# === 4. ENHANCE EXPLORER STATS ===
old_explorer = """        this.app.get('/api/explorer/stats', (req, res) => {
            const chain = this.blockchain.getChain();
            let totalTx = 0;
            for (const b of chain)
                totalTx += b.transactions.length;
            res.json({
                blockHeight: this.blockchain.getChainHeight(),
                totalBlocks: chain.length,
                totalTransactions: totalTx,
                totalSupply: this.blockchain.getTokenSystem().getTotalSupply(),
                maxSupply: this.blockchain.getTokenSystem().getMaxSupply(),
                validators: this.blockchain.getConsensus().getAllValidatorsList().length,
                mempoolSize: this.blockchain.getMempool().size(),
                activeWallets: this.walletManager.getAllWallets().length,
                dexPools: this.dex.getAllPools().length,
                contracts: this.contractManager.getAllContracts().length,
                chainValid: this.blockchain.isChainValid(),
            });
        });"""

new_explorer = """        this.app.get('/api/explorer/stats', (req, res) => {
            const chain = this.blockchain.getChain();
            let totalTx = 0;
            for (const b of chain)
                totalTx += b.transactions.length;
            const ecoImpact = this.eco.getNetworkImpact();
            const swapHistory = this.marketTracker ? (this.marketTracker.getSwapHistory(10000) || []) : [];
            const totalDexVolume = swapHistory.reduce((s, sw) => s + (sw.amountInUSD || sw.amountIn || 0), 0);
            const totalDexTvl = this.dex.getAllPools().reduce((s, p) => s + p.reserveA + p.reserveB, 0);
            res.json({
                blockHeight: this.blockchain.getChainHeight(),
                totalBlocks: chain.length,
                totalTransactions: totalTx,
                totalSupply: this.blockchain.getTokenSystem().getTotalSupply(),
                maxSupply: this.blockchain.getTokenSystem().getMaxSupply(),
                validators: this.blockchain.getConsensus().getAllValidatorsList().length,
                mempoolSize: this.blockchain.getMempool().size(),
                activeWallets: this.walletManager.getAllWallets().length,
                dexPools: this.dex.getAllPools().length,
                dexTvl: totalDexTvl,
                dexVolume: totalDexVolume,
                dexSwaps: swapHistory.length,
                contracts: this.contractManager.getAllContracts().length,
                chainValid: this.blockchain.isChainValid(),
                co2Offset: ecoImpact.totalCO2Offset || 0,
                treesPlanted: ecoImpact.totalTrees || 0,
                greenValidators: ecoImpact.greenValidators || 0,
                carbonCredits: ecoImpact.creditsRetired || 0,
            });
        });"""

if old_explorer in content:
    content = content.replace(old_explorer, new_explorer)
    print("Explorer stats enhanced")
else:
    print("WARNING: Explorer stats pattern not found")

with open("/opt/verdis/app/dist/api/server.js", "w") as f:
    f.write(content)

print("All API endpoints enhanced successfully")
