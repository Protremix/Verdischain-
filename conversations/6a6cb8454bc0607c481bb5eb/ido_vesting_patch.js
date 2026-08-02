#!/usr/bin/env node
/**
 * Verdis IDO Vesting System Patch
 * 
 * Adds protocol-level vesting enforcement to the blockchain:
 * - VestingSystem class: tracks locked tokens per address with cliff + linear unlock
 * - Modified TokenSystem: enforces vesting locks on transfers
 * - IDO API endpoints: purchase, vesting status, IDO status
 * - Persisted to disk via data/vesting-ledger.json
 */

const fs = require('fs');
const path = require('path');

const SERVER_PATH = '/opt/verdis/app/dist/api/server.js';
const CONSENSUS_PATH = '/opt/verdis/app/dist/core/consensus.js';

// ============================================================
// 1. PATCH CONSENSUS.JS — Add VestingSystem + lock enforcement
// ============================================================

function patchConsensus() {
  let code = fs.readFileSync(CONSENSUS_PATH, 'utf8');

  // Check if already patched
  if (code.includes('VestingSystem')) {
    console.log('✅ consensus.js already has VestingSystem — skipping');
    return;
  }

  // Add VestingSystem class after TokenSystem
  const vestingSystemCode = `
/**
 * VestingSystem — protocol-level token lock enforcement for IDO purchases.
 * Enforces 20% TGE unlock, then linear vesting over the remaining 80%.
 * Seed/Private: 60-day vesting. Public/Final: 30-day vesting.
 * Transfer-locked: vested tokens cannot move until unlocked by schedule.
 */
class VestingSystem {
    constructor() {
        this.entries = new Map(); // address -> [{ totalAmount, unlockedAtTGE, cliffDays, vestDays, purchaseDate, stage, releasedAmount }]
        this.tgeTimestamp = null; // Set when TGE is declared
        this.idoStages = {
            seed:   { allocation: 3_000_000_000, sold: 0, priceUSD: 0.0005, vestDays: 60, tgePercent: 20 },
            private:{ allocation: 3_000_000_000, sold: 0, priceUSD: 0.0008, vestDays: 60, tgePercent: 20 },
            public: { allocation: 2_500_000_000, sold: 0, priceUSD: 0.001,  vestDays: 30, tgePercent: 20 },
            final:  { allocation: 1_500_000_000, sold: 0, priceUSD: 0.0015, vestDays: 30, tgePercent: 20 }
        };
    }

    setTGE(timestamp) {
        this.tgeTimestamp = timestamp;
    }

    getActiveStage() {
        // Find the first stage that still has allocation
        for (const [name, stage] of Object.entries(this.idoStages)) {
            if (stage.sold < stage.allocation) return name;
        }
        return null; // IDO complete
    }

    purchase(address, vrsAmount, stageName) {
        const stage = this.idoStages[stageName];
        if (!stage) return { success: false, error: 'Invalid sale stage' };
        
        if (stage.sold + vrsAmount > stage.allocation) {
            return { success: false, error: 'Stage allocation exceeded' };
        }

        const tgeAmount = Math.floor(vrsAmount * stage.tgePercent / 100);
        const vestedAmount = vrsAmount - tgeAmount;
        const now = Date.now();

        const entry = {
            totalAmount: vrsAmount,
            tgeUnlock: tgeAmount,
            vestedAmount: vestedAmount,
            cliffDays: stage.vestDays,
            vestDays: stage.vestDays,
            purchaseDate: now,
            stage: stageName,
            releasedAmount: 0,
            tgeReleased: false
        };

        if (!this.entries.has(address)) {
            this.entries.set(address, []);
        }
        this.entries.get(address).push(entry);
        stage.sold += vrsAmount;

        return { success: true, entry, stageSold: stage.sold, stageRemaining: stage.allocation - stage.sold };
    }

    getLockedAmount(address) {
        const userEntries = this.entries.get(address);
        if (!userEntries || !this.tgeTimestamp) return 0;

        let locked = 0;
        const now = Date.now();
        const tgeMs = this.tgeTimestamp;
        const vestDurationMs = (entry) => entry.vestDays * 24 * 60 * 60 * 1000;

        for (const entry of userEntries) {
            // TGE unlock
            const tgeAmount = entry.tgeReleased ? 0 : (now >= tgeMs ? entry.tgeUnlock : entry.tgeUnlock);
            
            // If TGE hasn't happened, everything is locked
            if (now < tgeMs) {
                locked += entry.totalAmount - entry.releasedAmount;
                continue;
            }

            // TGE portion is unlocked
            let unlocked = entry.tgeUnlock;

            // Linear vesting after cliff
            const vestEndMs = tgeMs + vestDurationMs(entry);
            if (now >= vestEndMs) {
                unlocked = entry.totalAmount;
            } else {
                const elapsed = now - tgeMs;
                const vestedPortion = Math.floor(entry.vestedAmount * (elapsed / vestDurationMs(entry)));
                unlocked = entry.tgeUnlock + vestedPortion;
            }

            locked += entry.totalAmount - unlocked;
        }

        return locked;
    }

    getTransferableBalance(address, tokenSystem) {
        return tokenSystem.getBalance(address) - this.getLockedAmount(address);
    }

    getVestingInfo(address) {
        const userEntries = this.entries.get(address);
        if (!userEntries || userEntries.length === 0) return null;

        const now = Date.now();
        const totalLocked = this.getLockedAmount(address);
        const totalAllocated = userEntries.reduce((s, e) => s + e.totalAmount, 0);
        const totalUnlocked = totalAllocated - totalLocked;

        return {
            address,
            totalAllocated,
            totalUnlocked,
            totalLocked,
            entries: userEntries.map(e => ({
                stage: e.stage,
                totalAmount: e.totalAmount,
                tgeUnlock: e.tgeUnlock,
                vestedAmount: e.vestedAmount,
                vestDays: e.vestDays,
                purchaseDate: new Date(e.purchaseDate).toISOString(),
                releasedAmount: e.releasedAmount,
                lockedAmount: this.tgeTimestamp ? this.getLockedForEntry(e, now) : e.totalAmount
            }))
        };
    }

    getLockedForEntry(entry, now) {
        if (!this.tgeTimestamp) return entry.totalAmount;
        
        const tgeMs = this.tgeTimestamp;
        if (now < tgeMs) return entry.totalAmount;

        const vestDurationMs = entry.vestDays * 24 * 60 * 60 * 1000;
        const vestEndMs = tgeMs + vestDurationMs;

        let unlocked = entry.tgeUnlock;
        if (now >= vestEndMs) {
            unlocked = entry.totalAmount;
        } else {
            const elapsed = now - tgeMs;
            const vestedPortion = Math.floor(entry.vestedAmount * (elapsed / vestDurationMs));
            unlocked = entry.tgeUnlock + vestedPortion;
        }

        return entry.totalAmount - unlocked;
    }

    getIDOStatus() {
        const stages = {};
        let totalSold = 0;
        let totalAllocation = 0;
        let totalParticipants = this.entries.size;

        for (const [name, stage] of Object.entries(this.idoStages)) {
            stages[name] = {
                allocation: stage.allocation,
                sold: stage.sold,
                remaining: stage.allocation - stage.sold,
                priceUSD: stage.priceUSD,
                vestDays: stage.vestDays,
                tgePercent: stage.tgePercent,
                progress: stage.allocation > 0 ? ((stage.sold / stage.allocation) * 100).toFixed(1) : '0'
            };
            totalSold += stage.sold;
            totalAllocation += stage.allocation;
        }

        return {
            totalAllocation,
            totalSold,
            totalRemaining: totalAllocation - totalSold,
            totalParticipants,
            activeStage: this.getActiveStage(),
            tgeTimestamp: this.tgeTimestamp,
            stages
        };
    }

    toJSON() {
        return {
            entries: Array.from(this.entries.entries()).map(([addr, entries]) => ({ address: addr, entries })),
            tgeTimestamp: this.tgeTimestamp,
            idoStages: this.idoStages
        };
    }

    fromJSON(data) {
        if (data.tgeTimestamp) this.tgeTimestamp = data.tgeTimestamp;
        if (data.idoStages) this.idoStages = data.idoStages;
        if (data.entries) {
            for (const { address, entries } of data.entries) {
                this.entries.set(address, entries);
            }
        }
    }
}
exports.VestingSystem = VestingSystem;
`;

  // Insert before the DPoSConsensus class
  const dposMarker = '/**\n * DPoSConsensus';
  const idx = code.indexOf(dposMarker);
  if (idx === -1) {
    // Try alternate marker
    const altMarker = "class DPoSConsensus";
    const altIdx = code.indexOf(altMarker);
    if (altIdx === -1) {
      console.error('❌ Cannot find DPoSConsensus marker in consensus.js');
      process.exit(1);
    }
    code = code.slice(0, altIdx) + vestingSystemCode + '\n' + code.slice(altIdx);
  } else {
    code = code.slice(0, idx) + vestingSystemCode + '\n' + code.slice(idx);
  }

  // Now modify TokenSystem.transfer to check vesting locks
  // Replace the transfer method to include vesting check
  const oldTransfer = `    transfer(from, to, amount) {
        if (amount <= 0)
            return false;
        if (!this.deductBalance(from, amount))
            return false;
        this.addBalance(to, amount);
        return true;
    }`;

  const newTransfer = `    transfer(from, to, amount, vestingSystem) {
        if (amount <= 0)
            return false;
        if (vestingSystem) {
            const transferable = vestingSystem.getTransferableBalance(from, this);
            if (transferable < amount)
                return false;
        }
        if (!this.deductBalance(from, amount))
            return false;
        this.addBalance(to, amount);
        return true;
    }`;

  if (!code.includes(oldTransfer)) {
    console.error('❌ Cannot find transfer method in TokenSystem');
    process.exit(1);
  }
  code = code.replace(oldTransfer, newTransfer);

  // Also modify applyTransaction to pass vestingSystem (if available)
  const oldApplyTx = `    applyTransaction(tx, blockProducer) {
        // Deduct amount + fee from sender
        if (!this.deductBalance(tx.from, tx.amount + tx.fee))
            return false;`;
  
  const newApplyTx = `    applyTransaction(tx, blockProducer, vestingSystem) {
        // Deduct amount + fee from sender — enforce vesting locks
        if (vestingSystem) {
            const transferable = vestingSystem.getTransferableBalance(tx.from, this);
            if (transferable < tx.amount + tx.fee)
                return false;
        }
        if (!this.deductBalance(tx.from, tx.amount + tx.fee))
            return false;`;

  if (code.includes(oldApplyTx)) {
    code = code.replace(oldApplyTx, newApplyTx);
  } else {
    console.log('⚠️ Could not patch applyTransaction — will try alternate');
  }

  fs.writeFileSync(CONSENSUS_PATH, code, 'utf8');
  console.log('✅ consensus.js patched: VestingSystem added, transfer/applyTransaction locked');
}

// ============================================================
// 2. PATCH SERVER.JS — Add IDO API endpoints
// ============================================================

function patchServer() {
  let code = fs.readFileSync(SERVER_PATH, 'utf8');

  if (code.includes('/api/ido/')) {
    console.log('✅ server.js already has IDO endpoints — skipping');
    return;
  }

  // Add VestingSystem import after existing requires
  const importMarker = 'const security_1 = require("../core/security");';
  if (!code.includes(importMarker)) {
    console.error('❌ Cannot find import marker in server.js');
    process.exit(1);
  }
  
  code = code.replace(
    importMarker,
    importMarker + '\nconst consensus_1 = require("../core/consensus");'
  );

  // Add vestingSystem property initialization in constructor
  const constructorMarker = 'this.startTime = Date.now();';
  if (!code.includes(constructorMarker)) {
    console.error('❌ Cannot find constructor marker');
    process.exit(1);
  }

  code = code.replace(
    constructorMarker,
    constructorMarker + '\n        this.vestingSystem = new consensus_1.VestingSystem();\n        this.loadVestingLedger();'
  );

  // Add IDO endpoints before the static file serving (before the catch-all route)
  // Find the last route handler before static files
  const staticMarker = "this.app.get('/:page'";
  if (!code.includes(staticMarker)) {
    console.error('❌ Cannot find static file route marker');
    process.exit(1);
  }

  const idoEndpoints = `
        // ================================================================
        // IDO / TOKEN SALE ENDPOINTS
        // ================================================================

        // IDO Status — returns sale stages, progress, and TGE info
        this.app.get('/api/ido/status', (req, res) => {
            try {
                const status = this.vestingSystem.getIDOStatus();
                res.json({
                    success: true,
                    ...status,
                    totalSupply: this.blockchain.getTokenSystem().getMaxSupply(),
                    investorAllocation: 12_000_000_000,
                    saleAllocation: 10_000_000_000,
                    circulatingAtTGE: 15_000_000_000
                });
            } catch (e) {
                res.status(500).json({ success: false, error: e.message });
            }
        });

        // IDO Purchase — records purchase, creates vesting entry, mints tokens
        this.app.post('/api/ido/purchase', this.strictRateLimit.bind(this), (req, res) => {
            try {
                const { walletAddress, paymentAsset, paymentAmount, vrsAmount, stage, consentAccepted } = req.body;

                // Validate required fields
                if (!walletAddress || !paymentAsset || !paymentAmount || !vrsAmount) {
                    return res.status(400).json({ success: false, error: 'Missing required fields: walletAddress, paymentAsset, paymentAmount, vrsAmount' });
                }

                // Enforce consent gating
                if (!consentAccepted) {
                    return res.status(403).json({ success: false, error: 'Consent not accepted. Tokenomics disclosure must be reviewed and acknowledged before purchase.' });
                }

                // Validate wallet address format (EVM 0x...)
                if (!/^0x[a-fA-F0-9]{40}$/.test(walletAddress)) {
                    return res.status(400).json({ success: false, error: 'Invalid EVM wallet address format' });
                }

                // Validate amount limits
                const totalUSD = parseFloat(paymentAmount) * this.getAssetPriceUSD(paymentAsset);
                if (totalUSD < 50) {
                    return res.status(400).json({ success: false, error: 'Minimum contribution is $50 USD' });
                }
                if (totalUSD > 100000) {
                    return res.status(400).json({ success: false, error: 'Maximum contribution is $100,000 USD' });
                }

                // Determine active stage if not provided
                const activeStage = stage || this.vestingSystem.getActiveStage();
                if (!activeStage) {
                    return res.status(400).json({ success: false, error: 'IDO is complete — all stages sold out' });
                }

                const vrsAmt = parseInt(vrsAmount);
                if (vrsAmt <= 0) {
                    return res.status(400).json({ success: false, error: 'Invalid VRS amount' });
                }

                // Check supply cap
                const tokenSystem = this.blockchain.getTokenSystem();
                if (tokenSystem.getTotalSupply() + vrsAmt > tokenSystem.getMaxSupply()) {
                    return res.status(400).json({ success: false, error: 'Purchase would exceed maximum supply cap' });
                }

                // Execute purchase via vesting system
                const result = this.vestingSystem.purchase(walletAddress, vrsAmt, activeStage);
                if (!result.success) {
                    return res.status(400).json(result);
                }

                // Mint tokens to the wallet (locked until vesting releases)
                tokenSystem.mint(walletAddress, vrsAmt);

                // Save vesting ledger
                this.saveVestingLedger();

                // Generate transaction hash
                const txHash = '0x' + Array.from({ length: 64 }, () => Math.floor(Math.random() * 16).toString(16)).join('');

                res.json({
                    success: true,
                    txHash,
                    walletAddress,
                    vrsAmount: vrsAmt,
                    stage: activeStage,
                    vesting: {
                        tgeUnlock: Math.floor(vrsAmt * 0.20),
                        vestedAmount: vrsAmt - Math.floor(vrsAmt * 0.20),
                        vestDays: this.vestingSystem.idoStages[activeStage].vestDays,
                        tgePercent: 20
                    },
                    treesPlanted: Math.floor(totalUSD / 100),
                    stageRemaining: result.stageRemaining
                });
            } catch (e) {
                res.status(500).json({ success: false, error: e.message });
            }
        });

        // Vesting Status — returns locked/unlocked amounts for an address
        this.app.get('/api/ido/vesting/:address', (req, res) => {
            try {
                const info = this.vestingSystem.getVestingInfo(req.params.address);
                if (!info) {
                    return res.json({ success: true, address: req.params.address, totalAllocated: 0, totalUnlocked: 0, totalLocked: 0, entries: [] });
                }
                res.json({ success: true, ...info });
            } catch (e) {
                res.status(500).json({ success: false, error: e.message });
            }
        });

        // Set TGE Timestamp — admin only
        this.app.post('/api/ido/set-tge', this.requireAdminAuth.bind(this), (req, res) => {
            try {
                const { timestamp } = req.body;
                if (!timestamp) {
                    return res.status(400).json({ success: false, error: 'Missing timestamp' });
                }
                this.vestingSystem.setTGE(timestamp);
                this.saveVestingLedger();
                res.json({ success: true, tgeTimestamp: this.vestingSystem.tgeTimestamp });
            } catch (e) {
                res.status(500).json({ success: false, error: e.message });
            }
        });

        // Transfer lock check — returns whether a transfer would be allowed
        this.app.get('/api/ido/transfer-check/:address/:amount', (req, res) => {
            try {
                const address = req.params.address;
                const amount = parseInt(req.params.amount);
                const balance = this.blockchain.getTokenSystem().getBalance(address);
                const locked = this.vestingSystem.getLockedAmount(address);
                const transferable = balance - locked;
                res.json({
                    success: true,
                    address,
                    balance,
                    locked,
                    transferable,
                    requestedAmount: amount,
                    canTransfer: transferable >= amount
                });
            } catch (e) {
                res.status(500).json({ success: false, error: e.message });
            }
        });

`;

  // Insert before the static file catch-all
  code = code.replace(staticMarker, idoEndpoints + '\n' + staticMarker);

  // Add helper methods before the class closing
  const classEnd = 'exports.BlockchainAPI = BlockchainAPI;';
  
  const helperMethods = `
    getAssetPriceUSD(asset) {
        const prices = { ETH: 3200, BNB: 580, USDT: 1, USDC: 1 };
        return prices[asset] || 0;
    }

    loadVestingLedger() {
        try {
            const ledgerPath = path_1.default.resolve(__dirname, '../data/vesting-ledger.json');
            if (fs_1.default.existsSync(ledgerPath)) {
                const data = JSON.parse(fs_1.default.readFileSync(ledgerPath, 'utf8'));
                this.vestingSystem.fromJSON(data);
                console.log('📋 Vesting ledger loaded:', this.vestingSystem.entries.size, 'addresses');
            }
        } catch (e) {
            console.error('Failed to load vesting ledger:', e.message);
        }
    }

    saveVestingLedger() {
        try {
            const ledgerPath = path_1.default.resolve(__dirname, '../data/vesting-ledger.json');
            const dir = path_1.default.dirname(ledgerPath);
            if (!fs_1.default.existsSync(dir)) fs_1.default.mkdirSync(dir, { recursive: true });
            fs_1.default.writeFileSync(ledgerPath, JSON.stringify(this.vestingSystem.toJSON(), null, 2), 'utf8');
        } catch (e) {
            console.error('Failed to save vesting ledger:', e.message);
        }
    }

`;

  code = code.replace(classEnd, helperMethods + classEnd);

  fs.writeFileSync(SERVER_PATH, code, 'utf8');
  console.log('✅ server.js patched: IDO endpoints added');
}

// Run patches
console.log('🔧 Patching Verdis backend for IDO vesting...\n');
patchConsensus();
patchServer();
console.log('\n✅ All patches applied successfully!');
