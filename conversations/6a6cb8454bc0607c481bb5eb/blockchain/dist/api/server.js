"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.BlockchainAPI = void 0;
const express_1 = __importDefault(require("express"));
const cors_1 = __importDefault(require("cors"));
const fs_1 = __importDefault(require("fs"));
const path_1 = __importDefault(require("path"));
const vm_1 = require("../core/vm");
const crypto_1 = require("../crypto");
class BlockchainAPI {
    constructor(blockchain, walletManager, contractManager) {
        this.dex = null;
        this.eco = null;
        this.blockchain = blockchain;
        this.walletManager = walletManager;
        this.contractManager = contractManager;
        this.app = (0, express_1.default)();
        this.setupMiddleware();
        this.setupRoutes();
    }
    setDEX(dex) {
        this.dex = dex;
    }
    setEco(eco) {
        this.eco = eco;
    }
    serveDashboard(filePath) {
        if (filePath && fs_1.default.existsSync(filePath)) {
            this.dashboardHtmlPath = filePath;
        }
    }
    setupMiddleware() {
        this.app.use((0, cors_1.default)());
        this.app.use(express_1.default.json({ limit: '10mb' }));
    }
    setupRoutes() {
        // ===== Dashboard =====
        this.app.get('/', (req, res) => {
            if (this.dashboardHtmlPath && fs_1.default.existsSync(this.dashboardHtmlPath)) {
                res.sendFile(this.dashboardHtmlPath);
                return;
            }
            const defaultPath = path_1.default.resolve(__dirname, '../web/dashboard.html');
            if (fs_1.default.existsSync(defaultPath)) {
                res.sendFile(defaultPath);
                return;
            }
            res.send(`<html><body style="background:#0a0e1a;color:#00ff88;font-family:sans-serif;padding:2rem"><h1>🌿 Verdis Node Running</h1><p>Height: ${this.blockchain.getChainHeight()}</p></body></html>`);
        });
        // ===== Blockchain Info =====
        this.app.get('/api/blockchain/info', (req, res) => {
            const state = this.blockchain.getState();
            res.json({
                height: state.currentHeight,
                totalSupply: state.totalSupply,
                maxSupply: state.maxSupply,
                validatorCount: state.validatorCount,
                blockReward: state.blockReward,
                mempoolSize: this.blockchain.getMempool().size(),
                chainValid: this.blockchain.isChainValid(),
            });
        });
        this.app.get('/api/blockchain/blocks', (req, res) => {
            const limit = parseInt(req.query.limit) || 20;
            const offset = parseInt(req.query.offset) || 0;
            const chain = this.blockchain.getChain();
            const blocks = chain.slice().reverse().slice(offset, offset + limit);
            res.json(blocks);
        });
        this.app.get('/api/blockchain/block/:index', (req, res) => {
            const index = parseInt(req.params.index);
            const block = this.blockchain.getBlockByIndex(index);
            if (!block) {
                res.status(404).json({ error: 'Block not found' });
                return;
            }
            res.json(block);
        });
        this.app.get('/api/blockchain/block/hash/:hash', (req, res) => {
            const block = this.blockchain.getBlockByHash(req.params.hash);
            if (!block) {
                res.status(404).json({ error: 'Block not found' });
                return;
            }
            res.json(block);
        });
        // ===== Wallet =====
        this.app.post('/api/wallet/create', (req, res) => {
            const wallet = this.walletManager.createWallet();
            const balance = this.blockchain.getTokenSystem().getBalance(wallet.address);
            res.json({
                privateKey: wallet.privateKey,
                publicKey: wallet.publicKey,
                address: wallet.address,
                balance,
                staked: this.blockchain.getTokenSystem().getStaked(wallet.address),
            });
        });
        this.app.get('/api/wallet/:address/balance', (req, res) => {
            const balance = this.blockchain.getTokenSystem().getBalance(req.params.address);
            res.json({ address: req.params.address, balance });
        });
        this.app.get('/api/wallet/:address/staked', (req, res) => {
            const staked = this.blockchain.getTokenSystem().getStaked(req.params.address);
            res.json({ address: req.params.address, staked });
        });
        // ===== Transactions =====
        this.app.post('/api/transaction/send', (req, res) => {
            const { privateKey, from, to, amount, fee, data } = req.body;
            let wallet = this.walletManager.getAllWallets().find(w => w.address === from || w.publicKey === from);
            if (!wallet && privateKey) {
                wallet = this.walletManager.importWallet(privateKey);
            }
            if (!wallet) {
                // Sign directly with the private key
                const publicKey = privateKey ? (0, crypto_1.getPublicKeyFromPrivateKey)(privateKey) : from;
                const senderAddress = (0, crypto_1.getAddressFromPublicKey)(publicKey);
                const nonce = Date.now();
                const { signTransaction } = require('../crypto');
                const tx = signTransaction(privateKey, to, amount, fee || 1, nonce, data || null, publicKey);
                const result = this.blockchain.submitTransaction(tx);
                if (!result.success) {
                    res.status(400).json({ error: result.error });
                    return;
                }
                res.json({ txId: tx.id, transaction: tx });
                return;
            }
            const tx = this.walletManager.signTransaction(wallet, to, amount, fee || 1, Date.now(), data);
            const result = this.blockchain.submitTransaction(tx);
            if (!result.success) {
                res.status(400).json({ error: result.error });
                return;
            }
            res.json({ txId: tx.id, transaction: tx });
        });
        this.app.get('/api/transaction/:txId', (req, res) => {
            const receipt = this.blockchain.getTransactionReceipt(req.params.txId);
            res.json(receipt);
        });
        this.app.get('/api/mempool', (req, res) => {
            res.json(this.blockchain.getMempool().getTransactions());
        });
        this.app.get('/api/mempool/size', (req, res) => {
            res.json({ size: this.blockchain.getMempool().size() });
        });
        // ===== Validators & Staking =====
        this.app.get('/api/validators', (req, res) => {
            res.json(this.blockchain.getConsensus().getAllValidatorsList());
        });
        this.app.get('/api/validators/top', (req, res) => {
            res.json(this.blockchain.getConsensus().getTopValidators());
        });
        this.app.post('/api/validators/register', (req, res) => {
            const { publicKey, address } = req.body;
            const validator = this.blockchain.getConsensus().registerValidator(publicKey, address);
            res.json({ success: true, validator });
        });
        this.app.post('/api/validators/vote', (req, res) => {
            const { voterAddress, validatorAddress, amount } = req.body;
            const result = this.blockchain.getConsensus().vote(voterAddress, validatorAddress, amount, this.blockchain.getTokenSystem());
            res.json({ success: result });
        });
        this.app.post('/api/stake', (req, res) => {
            const { address, amount, action } = req.body;
            if (action === 'stake') {
                const result = this.blockchain.getTokenSystem().stake(address, amount);
                res.json({ success: result });
            }
            else if (action === 'unstake') {
                const result = this.blockchain.getTokenSystem().unstake(address, amount);
                res.json({ success: result });
            }
            else {
                res.status(400).json({ error: 'Invalid action' });
            }
        });
        // ===== Block Production =====
        this.app.post('/api/blockchain/produce', (req, res) => {
            const { privateKey, publicKey, address } = req.body;
            const block = this.blockchain.produceBlock(privateKey, publicKey, address);
            if (!block) {
                res.status(400).json({ error: 'Not your turn to produce a block, or no pending transactions' });
                return;
            }
            res.json({ success: true, block });
        });
        // ===== Smart Contracts =====
        this.app.post('/api/contract/deploy', (req, res) => {
            const { owner, name, source } = req.body;
            const bytecode = (0, vm_1.compileContract)(source);
            const contract = this.contractManager.deploy(owner, name, bytecode);
            res.json({ success: true, contractId: contract.id, name: contract.name });
        });
        this.app.post('/api/contract/:id/execute', (req, res) => {
            const { input } = req.body;
            const result = this.contractManager.execute(req.params.id, input);
            res.json(result);
        });
        this.app.get('/api/contract/:id', (req, res) => {
            const contract = this.contractManager.getContract(req.params.id);
            if (!contract) {
                res.status(404).json({ error: 'Contract not found' });
                return;
            }
            res.json({
                id: contract.id,
                name: contract.name,
                owner: contract.owner,
                deployedAt: contract.deployedAt,
                bytecode: contract.bytecode,
            });
        });
        this.app.get('/api/contracts', (req, res) => {
            res.json(this.contractManager.getAllContracts().map(c => ({
                id: c.id,
                name: c.name,
                owner: c.owner,
                deployedAt: c.deployedAt,
            })));
        });
        this.app.get('/api/contract/:id/state', (req, res) => {
            const state = this.contractManager.getContract(req.params.id)?.state;
            if (!state) {
                res.status(404).json({ error: 'Contract not found' });
                return;
            }
            res.json(Object.fromEntries(state));
        });
        // ===== DEX =====
        if (this.dex) {
            this.app.get('/api/dex/pools', (req, res) => {
                res.json(this.dex.getAllPools());
            });
            this.app.post('/api/dex/pool/create', (req, res) => {
                const { tokenA, tokenB } = req.body;
                const pool = this.dex.createPool(tokenA, tokenB);
                res.json({ success: true, pool });
            });
            this.app.post('/api/dex/liquidity/add', (req, res) => {
                const { provider, tokenA, tokenB, amountA, amountB } = req.body;
                const result = this.dex.addLiquidity(provider, tokenA, tokenB, amountA, amountB);
                res.json(result);
            });
            this.app.post('/api/dex/liquidity/remove', (req, res) => {
                const { provider, poolId, lpAmount } = req.body;
                const result = this.dex.removeLiquidity(provider, poolId, lpAmount);
                res.json(result);
            });
            this.app.post('/api/dex/swap', (req, res) => {
                const { trader, tokenIn, tokenOut, amountIn, minAmountOut } = req.body;
                const result = this.dex.swap(trader, tokenIn, tokenOut, amountIn, minAmountOut || 0);
                if (result.error) {
                    res.status(400).json(result);
                    return;
                }
                res.json(result);
            });
            this.app.get('/api/dex/quote', (req, res) => {
                const { tokenIn, tokenOut, amountIn } = req.query;
                const result = this.dex.quoteSwap(tokenIn, tokenOut, parseFloat(amountIn));
                res.json(result);
            });
            this.app.get('/api/dex/pool/:id/stats', (req, res) => {
                const stats = this.dex.getPoolStats(req.params.id);
                res.json(stats);
            });
        }
        // ===== Eco Features =====
        if (this.eco) {
            this.app.get('/api/eco/impact', (req, res) => {
                res.json(this.eco.getNetworkImpact());
            });
            // Carbon Credits
            this.app.post('/api/eco/carbon/mint', (req, res) => {
                const { seller, projectType, amount, price, location, metadata } = req.body;
                const credit = this.eco.mintCarbonCredit(seller, projectType, amount, price, location, metadata);
                res.json({ success: true, credit });
            });
            this.app.post('/api/eco/carbon/verify', (req, res) => {
                const { creditId, verifier } = req.body;
                const result = this.eco.verifyCarbonCredit(creditId, verifier);
                res.json(result);
            });
            this.app.post('/api/eco/carbon/buy', (req, res) => {
                const { creditId, buyer, amount } = req.body;
                const result = this.eco.buyCarbonCredit(creditId, buyer, amount);
                res.json(result);
            });
            this.app.post('/api/eco/carbon/retire', (req, res) => {
                const { creditId, by } = req.body;
                const result = this.eco.retireCarbonCredit(creditId, by);
                res.json(result);
            });
            this.app.get('/api/eco/carbon/credits', (req, res) => {
                const filter = {};
                if (req.query.status)
                    filter.status = req.query.status;
                if (req.query.projectType)
                    filter.projectType = req.query.projectType;
                res.json(this.eco.getCarbonCredits(Object.keys(filter).length ? filter : undefined));
            });
            // Green Validators
            this.app.post('/api/eco/green/register', (req, res) => {
                const { address, energySource } = req.body;
                const score = this.eco.registerGreenValidator(address, energySource);
                res.json({ success: true, score });
            });
            this.app.get('/api/eco/green/top', (req, res) => {
                const n = parseInt(req.query.n) || 10;
                res.json(this.eco.getTopGreenValidators(n));
            });
            this.app.get('/api/eco/green/:address', (req, res) => {
                const score = this.eco.getGreenScore(req.params.address);
                res.json(score || { error: 'No green score found' });
            });
            // Reforestation
            this.app.post('/api/eco/reforest/create', (req, res) => {
                const { owner, name, location, area, treesTarget, species } = req.body;
                const project = this.eco.createReforestationProject(owner, name, location, area, treesTarget, species);
                res.json({ success: true, project });
            });
            this.app.post('/api/eco/reforest/update', (req, res) => {
                const { projectId, treesPlanted } = req.body;
                const project = this.eco.updateReforestationProject(projectId, treesPlanted);
                res.json({ success: !!project, project });
            });
            this.app.post('/api/eco/reforest/verify', (req, res) => {
                const { projectId, verifier } = req.body;
                const result = this.eco.verifyReforestationProject(projectId, verifier);
                res.json(result);
            });
            this.app.get('/api/eco/reforest/projects', (req, res) => {
                const status = req.query.status;
                res.json(this.eco.getReforestationProjects(status));
            });
            // Carbon Offset Pool
            this.app.get('/api/eco/offset-pool', (req, res) => {
                res.json(this.eco.getCarbonOffsetPool());
            });
        }
        // ===== Legacy compatibility =====
        this.app.get('/api/chain', (req, res) => {
            res.json(this.blockchain.getState());
        });
        this.app.get('/api/wallets', (req, res) => {
            res.json(this.walletManager.getAllWallets());
        });
    }
    start(port) {
        this.app.listen(port, () => {
            console.log(`📡 API server listening on port ${port}`);
        });
    }
    getApp() {
        return this.app;
    }
}
exports.BlockchainAPI = BlockchainAPI;
//# sourceMappingURL=server.js.map