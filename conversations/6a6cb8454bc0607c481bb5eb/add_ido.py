import sys

with open("/opt/verdis/app/dist/api/server.js", "r") as f:
    lines = f.readlines()

# Find the line with api/wallets
insert_after = None
for i, line in enumerate(lines):
    if "this.app.get('/api/wallets'" in line:
        insert_after = i
        break

if insert_after is None:
    print("ERROR: Could not find insertion point")
    sys.exit(1)

IDO_CODE = r"""
        // === IDO / TOKEN SALE ===
        const IDO_CONFIG = {
            priceUSD: 0.001,
            totalAllocation: 10000000000,
            sold: 0,
            purchasers: new Set(),
            minPurchase: 100,
            maxPurchase: 1000000,
            startTime: Date.now(),
            endTime: Date.now() + (365 * 24 * 60 * 60 * 1000),
            paused: false
        };

        this.app.get('/api/ido/info', (req, res) => {
            const remaining = IDO_CONFIG.totalAllocation - IDO_CONFIG.sold;
            res.json({
                priceUSD: IDO_CONFIG.priceUSD,
                totalAllocation: IDO_CONFIG.totalAllocation,
                sold: IDO_CONFIG.sold,
                remaining: remaining,
                progressPct: ((IDO_CONFIG.sold / IDO_CONFIG.totalAllocation) * 100).toFixed(2),
                purchasers: IDO_CONFIG.purchasers.size,
                minPurchase: IDO_CONFIG.minPurchase,
                maxPurchase: IDO_CONFIG.maxPurchase,
                active: !IDO_CONFIG.paused && remaining > 0,
                acceptedPayments: ['VCO-native', 'ETH', 'BNB', 'USDT', 'USDC'],
                tokenSymbol: 'VCO',
                tokenName: 'Verdis Coin',
                chainId: 909
            });
        });

        this.app.post('/api/ido/purchase', this.strictRateLimit.bind(this), (req, res) => {
            try {
                if (IDO_CONFIG.paused) {
                    res.status(400).json({ success: false, error: 'Token sale is paused' });
                    return;
                }
                const { address, amountVCO, signature, publicKey } = req.body;
                if (!address) {
                    res.status(400).json({ success: false, error: 'Wallet address required' });
                    return;
                }
                const amount = parseFloat(amountVCO);
                if (isNaN(amount) || amount <= 0) {
                    res.status(400).json({ success: false, error: 'Invalid amount' });
                    return;
                }
                if (amount < IDO_CONFIG.minPurchase) {
                    res.status(400).json({ success: false, error: 'Minimum purchase is ' + IDO_CONFIG.minPurchase + ' VCO' });
                    return;
                }
                if (amount > IDO_CONFIG.maxPurchase) {
                    res.status(400).json({ success: false, error: 'Maximum purchase is ' + IDO_CONFIG.maxPurchase + ' VCO per wallet' });
                    return;
                }
                const remaining = IDO_CONFIG.totalAllocation - IDO_CONFIG.sold;
                if (amount > remaining) {
                    res.status(400).json({ success: false, error: 'Only ' + remaining + ' VCO remaining' });
                    return;
                }
                this.blockchain.getTokenSystem().mint(address, amount);
                IDO_CONFIG.sold += amount;
                IDO_CONFIG.purchasers.add(address);
                const txId = require('crypto').randomUUID();
                res.json({
                    success: true,
                    txId: txId,
                    address: address,
                    amountVCO: amount,
                    priceUSD: IDO_CONFIG.priceUSD,
                    totalCostUSD: (amount * IDO_CONFIG.priceUSD).toFixed(6),
                    newBalance: this.blockchain.getTokenSystem().getBalance(address),
                    remaining: IDO_CONFIG.totalAllocation - IDO_CONFIG.sold
                });
            } catch (error) {
                res.status(500).json({ success: false, error: error.message });
            }
        });

        this.app.get('/api/ido/purchasers', (req, res) => {
            res.json({
                count: IDO_CONFIG.purchasers.size,
                addresses: Array.from(IDO_CONFIG.purchasers)
            });
        });

        this.app.post('/api/ido/claim', this.strictRateLimit.bind(this), (req, res) => {
            const { address } = req.body;
            if (!address) {
                res.status(400).json({ success: false, error: 'Address required' });
                return;
            }
            const balance = this.blockchain.getTokenSystem().getBalance(address);
            res.json({
                success: true,
                address: address,
                balance: balance,
                message: 'Tokens already credited to wallet'
            });
        });
"""

lines.insert(insert_after + 1, IDO_CODE + "\n")

with open("/opt/verdis/app/dist/api/server.js", "w") as f:
    f.writelines(lines)

print("IDO endpoints added successfully after line " + str(insert_after + 1))
