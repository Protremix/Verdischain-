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
const jsonrpc_1 = require("./jsonrpc");
const security_1 = require("../core/security");
class BlockchainAPI {
    constructor(blockchain, walletManager, contractManager) {
        this.dex = null;
        this.marketTracker = null;
        this.eco = null;
        this.startTime = Date.now();
        this.blockchain = blockchain;
        this.walletManager = walletManager;
        this.contractManager = contractManager;
        this.app = (0, express_1.default)();
        this.app.use((0, cors_1.default)());
        this.app.use(express_1.default.json({ limit: '10mb' }));
        this.security = new security_1.SecurityManager();
        // Rate limiting middleware
        this.app.use((req, res, next) => {
            const ip = req.headers['x-forwarded-for'] || req.connection?.remoteAddress || req.socket?.remoteAddress || 'unknown';
            const rateLimit = this.security.checkRateLimit(ip);
            res.setHeader('X-RateLimit-Remaining', rateLimit.remaining);
            res.setHeader('X-RateLimit-Reset', rateLimit.resetIn);
            if (!rateLimit.allowed) {
                res.status(429).json({ error: 'Rate limit exceeded', retryAfter: rateLimit.resetIn });
                return;
            }
            next();
        });
        this.setupCoreRoutes();
        // Trust Wallet / EVM JSON-RPC compatibility
        (0, jsonrpc_1.setupJsonRpc)(this.app, this.blockchain, this.walletManager);
    }
    // Admin authentication middleware
    requireAdminAuth(req, res, next) {
        const apiKey = req.headers['x-api-key'] || req.query.apiKey;
        if (!apiKey || !this.security.verifyApiKey(apiKey)) {
            this.security.logEvent('auth_failed', 'warning', 'Admin auth failed', req.headers['x-forwarded-for'] || req.ip);
            res.status(401).json({ error: 'Unauthorized — admin API key required', hint: 'Add x-api-key header' });
            return;
        }
        next();
    }
    // Strict rate limit for sensitive endpoints
    strictRateLimit(req, res, next) {
        const ip = req.headers['x-forwarded-for'] || req.ip || 'unknown';
        const rateLimit = this.security.checkRateLimit(ip + ':strict', true);
        if (!rateLimit.allowed) {
            res.status(429).json({ error: 'Rate limit exceeded for sensitive operation', retryAfter: rateLimit.resetIn });
            return;
        }
        next();
    }
    setDEX(dex) {
        this.dex = dex;
        this.setupDEXRoutes();
    }
    setMarketTracker(mt) {
        this.marketTracker = mt;
    }
    setEco(eco) {
        this.eco = eco;
        this.setupEcoRoutes();
    }
    serveDashboard(filePath) {
        if (filePath && fs_1.default.existsSync(filePath)) {
            this.dashboardHtmlPath = filePath;
        }
    }
    setupCoreRoutes() {
        // Dashboard
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
            res.send(`<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🌿 Verdis — The Eco-Friendly Blockchain</title>
<meta name="description" content="Verdis (VRS) is a fully functional L1 blockchain with native DPoS consensus, AMM DEX, carbon credit tracking, and Ethereum-compatible JSON-RPC.">
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { background:#0a0e1a; color:#e0e0e0; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; }
.container { max-width:800px; margin:0 auto; padding:2rem 1rem; }
h1 { color:#00e676; font-size:2.5rem; margin-bottom:0.5rem; }
.tagline { color:#888; font-size:1.2rem; margin-bottom:2rem; }
.stats { display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:1rem; margin:2rem 0; }
.stat { background:#13182a; padding:1.5rem; border-radius:12px; text-align:center; border:1px solid #1e2438; }
.stat-value { font-size:1.8rem; font-weight:700; color:#00e676; }
.stat-label { color:#888; font-size:0.85rem; margin-top:0.25rem; }
.features { margin:2rem 0; }
.feature { display:flex; align-items:center; gap:0.75rem; padding:0.75rem 0; }
.feature-icon { font-size:1.5rem; }
.security-badge { display:inline-block; background:#1a2332; color:#00e676; padding:0.25rem 0.75rem; border-radius:999px; font-size:0.8rem; margin:0.25rem; border:1px solid #00e67633; }
a { color:#00e676; text-decoration:none; }
a:hover { text-decoration:underline; }
.footer { margin-top:3rem; padding-top:2rem; border-top:1px solid #1e2438; color:#666; font-size:0.85rem; }
</style>
</head>
<body>
<div class="container">
  <h1>🌿 Verdis</h1>
  <p class="tagline">The Eco-Friendly Blockchain</p>
  <p>A fully functional L1 blockchain with native DPoS consensus, AMM-based DEX, and integrated carbon credit tracking. Built for sustainability.</p>
  
  <div class="stats">
    <div class="stat"><div class="stat-value">${this.blockchain.getChainHeight()}</div><div class="stat-label">Block Height</div></div>
    <div class="stat"><div class="stat-value">${this.blockchain.getTokenSystem().getTotalSupply().toLocaleString()}</div><div class="stat-label">VRS Supply</div></div>
    <div class="stat"><div class="stat-value">${this.blockchain.getConsensus().getAllValidatorsList().length}</div><div class="stat-label">Validators</div></div>
    <div class="stat"><div class="stat-value">909</div><div class="stat-label">Chain ID</div></div>
  </div>
  
  <h2 style="color:#00e676;margin:1.5rem 0 0.75rem">🔐 Security Features</h2>
  <div>
    <span class="security-badge">✅ secp256k1 Signatures</span>
    <span class="security-badge">✅ SHA-256 + Keccak256</span>
    <span class="security-badge">✅ Transaction Hash Integrity</span>
    <span class="security-badge">✅ Balance Checks</span>
    <span class="security-badge">✅ Chain Validation</span>
    <span class="security-badge">✅ Rate Limiting</span>
    <span class="security-badge">✅ Replay Protection</span>
    <span class="security-badge">✅ Admin Authentication</span>
    <span class="security-badge">✅ Validator Slashing</span>
    <span class="security-badge">✅ Input Validation</span>
    <span class="security-badge">✅ Mempool Limits</span>
    <span class="security-badge">✅ Max TX Amount</span>
  </div>
  
  <h2 style="color:#00e676;margin:1.5rem 0 0.75rem">🚀 Features</h2>
  <div class="features">
    <div class="feature"><span class="feature-icon">💱</span> Native AMM DEX with 6 trading pairs (VRS/CARBON, VRS/ECO, ...)</div>
    <div class="feature"><span class="feature-icon">🌱</span> Carbon credit minting, retirement, and reforestation tracking</div>
    <div class="feature"><span class="feature-icon">🔑</span> Green validator scoring with renewable energy verification</div>
    <div class="feature"><span class="feature-icon">📜</span> Smart contract VM (stack-based bytecode execution)</div>
    <div class="feature"><span class="feature-icon">📱</span> Ethereum JSON-RPC — compatible with MetaMask & Trust Wallet</div>
    <div class="feature"><span class="feature-icon">💾</span> State persistence — survives node restarts</div>
    <div class="feature"><span class="feature-icon">🔍</span> Block explorer — search blocks, transactions, and addresses</div>
    <div class="feature"><span class="feature-icon">📊</span> Live Chart.js visualizations and market data</div>
  </div>
  
  <h2 style="color:#00e676;margin:1.5rem 0 0.75rem">📡 Connect</h2>
  <div style="background:#13182a;padding:1.5rem;border-radius:12px;border:1px solid #1e2438">
    <p style="margin-bottom:0.75rem"><strong>RPC URL:</strong> <code style="color:#00e676">${req.protocol}://${req.get('host')}/rpc</code></p>
    <p style="margin-bottom:0.75rem"><strong>Chain ID:</strong> 909</p>
    <p style="margin-bottom:0.75rem"><strong>Symbol:</strong> VRS</p>
    <p style="margin-bottom:0.75rem"><strong>Explorer:</strong> <a href="/api/explorer/stats">API</a> | <a href="/api/security/audit">Security Audit</a></p>
    <p style="margin-bottom:0.75rem"><strong>Network Info:</strong> <a href="/api/network/info">/api/network/info</a></p>
  </div>
  
  <div class="footer">
    <p>🌿 Verdis Network — Chain ID 909 | DPoS | secp256k1 | Keccak256</p>
    <p style="margin-top:0.5rem">Built with @noble/secp256k1 and @noble/hashes. No mocks. No third-party dependencies.</p>
  </div>
</div>
</body>
</html>`);
        });
        // Public network info (for sharing/marketing)
        this.app.get('/api/network/info', (req, res) => {
            const host = req.get('host') || '';
            const protocol = req.secure || req.get('x-forwarded-proto') === 'https' ? 'https' : 'http';
            const isPublic = !host.includes('localhost') && !host.includes('127.0.0.1');
            const baseUrl = isPublic ? `${protocol}://${host}` : 'http://localhost:3200';
            res.json({
                name: 'Verdis',
                symbol: 'VRS',
                tagline: 'The Eco-Friendly Blockchain',
                description: 'A fully functional L1 blockchain with native DPoS consensus, AMM-based DEX, and integrated carbon credit tracking. Built for sustainability.',
                chainId: 909,
                rpcUrl: baseUrl + '/rpc',
                explorerUrl: baseUrl,
                dashboardUrl: baseUrl,
                blockTime: 5000,
                maxSupply: 100000000000,
                consensus: 'Delegated Proof of Stake (DPoS)',
                validatorCount: 27,
                cryptography: {
                    curve: 'secp256k1',
                    hash: 'SHA-256 + Keccak256',
                    signatures: 'ECDSA with recovery',
                    addressFormat: 'Ethereum-compatible (0x...)',
                },
                features: [
                    'Native AMM DEX with 6 trading pairs',
                    'Carbon credit minting and retirement',
                    'Reforestation tracking',
                    'Green validator scoring',
                    'Smart contract VM (stack-based)',
                    'Ethereum JSON-RPC (MetaMask/Trust Wallet)',
                    'State persistence (survives restarts)',
                    'Block explorer',
                    'Rate limiting & replay protection',
                    'Validator slashing conditions',
                ],
                security: {
                    rateLimiting: true,
                    signatureVerification: true,
                    replayProtection: true,
                    adminAuth: true,
                    validatorSlashing: true,
                    inputValidation: true,
                    chainValidation: true,
                },
                links: {
                    dashboard: baseUrl,
                    rpc: baseUrl + '/rpc',
                    securityAudit: baseUrl + '/api/security/audit',
                    explorer: baseUrl + '#tab-explorer',
                    marketData: baseUrl + '/api/token/market',
                    networkInfo: baseUrl + '/api/network/info',
                },
            });
        });
        // Public URL (auto-detected from request)
        this.app.get('/api/public-url', (req, res) => {
            const host = req.get('host') || '';
            const protocol = req.secure || req.get('x-forwarded-proto') === 'https' ? 'https' : 'http';
            const isPublic = !host.includes('localhost') && !host.includes('127.0.0.1');
            res.json({
                url: isPublic ? `${protocol}://${host}` : null,
                rpcUrl: isPublic ? `${protocol}://${host}/rpc` : 'http://localhost:3200/rpc',
                isPublic,
                host,
            });
        });
        // Unified search (block number, block hash, tx hash, or address)
        this.app.get('/api/explorer/search', (req, res) => {
            const q = (req.query.q || '').trim();
            if (!q) {
                res.status(400).json({ error: 'Query required' });
                return;
            }
            // Try as block number
            if (/^\d+$/.test(q)) {
                const block = this.blockchain.getBlockByIndex(parseInt(q));
                if (block) {
                    res.json({ type: 'block', data: block });
                    return;
                }
            }
            // Try as block hash
            const blockByHash = this.blockchain.getBlockByHash(q);
            if (blockByHash) {
                res.json({ type: 'block', data: blockByHash });
                return;
            }
            // Try as transaction hash
            const receipt = this.blockchain.getTransactionReceipt(q);
            if (receipt && receipt.tx) {
                res.json({ type: 'transaction', data: { ...receipt.tx, blockIndex: receipt.block?.header.index } });
                return;
            }
            // Try as wallet address (0x prefix or public key)
            if (q.startsWith('0x') || q.startsWith('03') || q.startsWith('02')) {
                const balance = this.blockchain.getTokenSystem().getBalance(q);
                const wallet = this.walletManager.getAllWallets().find(w => w.address === q || w.publicKey === q);
                const validator = this.blockchain.getConsensus().getAllValidatorsList().find(v => v.address === q);
                if (wallet || balance > 0 || validator) {
                    // Search transactions in blocks for this address
                    const chain = this.blockchain.getChain();
                    const txs = [];
                    for (const block of chain) {
                        for (const tx of block.transactions) {
                            if (tx.from === q || tx.to === q) {
                                txs.push({ ...tx, blockIndex: block.header.index, blockHash: block.hash });
                            }
                        }
                    }
                    res.json({
                        type: 'address',
                        data: {
                            address: q,
                            balance,
                            wallet: wallet ? { publicKey: wallet.publicKey, address: wallet.address } : null,
                            isValidator: !!validator,
                            validatorInfo: validator || null,
                            transactionCount: txs.length,
                            transactions: txs.slice(-20).reverse()
                        }
                    });
                    return;
                }
            }
            res.status(404).json({ error: 'Not found' });
        });
        // Explorer stats
        this.app.get('/api/explorer/stats', (req, res) => {
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
        });
        // Security audit report (public)
        this.app.get('/api/security/audit', (req, res) => {
            res.json(this.security.getAuditReport());
        });
        // Security events log (admin only)
        this.app.get('/api/security/events', this.requireAdminAuth.bind(this), (req, res) => {
            const limit = parseInt(req.query.limit) || 50;
            res.json(this.security.getSecurityEvents(limit));
        });
        // Get admin API key (only accessible locally)
        this.app.get('/api/security/admin-key', (req, res) => {
            const ip = req.ip || req.socket?.remoteAddress || '';
            if (!ip.includes('127.0.0.1') && !ip.includes('localhost') && !ip.includes('::1')) {
                res.status(403).json({ error: 'Admin key only accessible from localhost' });
                return;
            }
            res.json({ apiKey: this.security.getAdminApiKey() });
        });
        // Monitoring / Health check (public)
        this.app.get('/api/monitoring/health', (req, res) => {
            const now = Date.now();
            const uptime = now - this.startTime;
            const chain = this.blockchain.getChain();
            const lastBlock = chain[chain.length - 1];
            const lastBlockTime = lastBlock ? lastBlock.header.timestamp : 0;
            const blockStaleness = now - lastBlockTime;
            const mempoolSize = this.blockchain.getMempool().size();
            // Determine health status
            const isHealthy = blockStaleness < 30000 && this.blockchain.isChainValid();
            const status = isHealthy ? 'healthy' : 'unhealthy';
            // Calculate TPS (transactions per second over last 100 blocks)
            const recentBlocks = chain.slice(-100);
            const recentTxCount = recentBlocks.reduce((sum, b) => sum + b.transactions.length, 0);
            const timeSpan = recentBlocks.length > 1 ?
                (recentBlocks[recentBlocks.length - 1].header.timestamp - recentBlocks[0].header.timestamp) / 1000 : 1;
            const tps = timeSpan > 0 ? (recentTxCount / timeSpan).toFixed(2) : '0.00';
            res.json({
                status,
                timestamp: now,
                uptime: {
                    seconds: Math.floor(uptime / 1000),
                    human: Math.floor(uptime / 3600000) + 'h ' + Math.floor((uptime % 3600000) / 60000) + 'm ' + Math.floor((uptime % 60000) / 1000) + 's',
                },
                chain: {
                    height: this.blockchain.getChainHeight(),
                    totalBlocks: chain.length,
                    chainValid: this.blockchain.isChainValid(),
                    lastBlockTime,
                    blockStalenessMs: blockStaleness,
                    blockStalenessHuman: blockStaleness < 1000 ? blockStaleness + 'ms' : Math.floor(blockStaleness / 1000) + 's',
                    blockTime: 5000,
                },
                consensus: {
                    validators: this.blockchain.getConsensus().getAllValidatorsList().length,
                    topValidators: this.blockchain.getConsensus().getTopValidators().length,
                },
                mempool: {
                    size: mempoolSize,
                    maxSize: 1000,
                },
                dex: {
                    pools: this.dex ? this.dex.getAllPools().length : 0,
                },
                performance: {
                    tps: parseFloat(tps),
                    avgBlockTx: recentBlocks.length > 0 ? (recentTxCount / recentBlocks.length).toFixed(2) : '0',
                },
                version: '1.0.0',
                network: 'verdis',
                chainId: 909,
            });
        });
        // Uptime badge (simple text for monitoring tools)
        this.app.get('/api/monitoring/uptime', (req, res) => {
            const uptime = Date.now() - this.startTime;
            const isHealthy = this.blockchain.isChainValid();
            res.setHeader('Content-Type', 'text/plain');
            res.send(isHealthy ? 'OK' : 'ERROR');
        });
        // Blockchain Info
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
            res.json(chain.slice().reverse().slice(offset, offset + limit));
        });
        this.app.get('/api/blockchain/block/:index', (req, res) => {
            const block = this.blockchain.getBlockByIndex(parseInt(req.params.index));
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
        // Wallet
        this.app.post('/api/wallet/create', (req, res) => {
            const wallet = this.walletManager.createWallet();
            res.json({
                privateKey: wallet.privateKey,
                publicKey: wallet.publicKey,
                address: wallet.address,
                balance: this.blockchain.getTokenSystem().getBalance(wallet.address),
                staked: this.blockchain.getTokenSystem().getStaked(wallet.address),
            });
        });
        this.app.get('/api/wallet/:address/balance', (req, res) => {
            res.json({ address: req.params.address, balance: this.blockchain.getTokenSystem().getBalance(req.params.address) });
        });
        this.app.get('/api/wallet/:address/staked', (req, res) => {
            res.json({ address: req.params.address, staked: this.blockchain.getTokenSystem().getStaked(req.params.address) });
        });
        // Wallet Transaction History
        this.app.get('/api/wallet/:address/transactions', (req, res) => {
            const address = req.params.address;
            const chain = this.blockchain.getChain();
            const txs = [];
            for (const block of chain) {
                for (const tx of block.transactions) {
                    if (tx.from === address || tx.to === address) {
                        txs.push({
                            ...tx,
                            blockIndex: block.header.index,
                            blockHash: block.hash,
                            timestamp: block.header.timestamp,
                            direction: tx.from === address ? 'sent' : 'received'
                        });
                    }
                }
            }
            // Also check mempool for pending
            const mempoolTxs = this.blockchain.getMempool().getTransactions();
            for (const tx of mempoolTxs) {
                if (tx.from === address || tx.to === address) {
                    txs.push({ ...tx, blockIndex: null, blockHash: null, timestamp: tx.timestamp, direction: tx.from === address ? 'sent' : 'received', pending: true });
                }
            }
            res.json(txs.reverse());
        });
        // Wallet Full Details
        this.app.get('/api/wallet/:address/details', (req, res) => {
            const address = req.params.address;
            const wallet = this.walletManager.getAllWallets().find(w => w.address === address);
            const balance = this.blockchain.getTokenSystem().getBalance(address);
            const staked = this.blockchain.getTokenSystem().getStaked(address);
            const validator = this.blockchain.getConsensus().getAllValidatorsList().find(v => v.address === address);
            const greenVal = this.eco ? this.eco.getGreenScore(address) : null;
            res.json({
                address,
                balance,
                staked,
                isValidator: !!validator,
                validatorInfo: validator || null,
                greenScore: greenVal || null,
                privateKey: wallet ? wallet.privateKey : null,
                publicKey: wallet ? wallet.publicKey : null,
            });
        });
        // Transactions
        this.app.post('/api/transaction/send', this.strictRateLimit.bind(this), (req, res) => {
            // Nonce replay protection
            const { privateKey, from, to, amount, fee, data } = req.body;
            let wallet = this.walletManager.getAllWallets().find(w => w.address === from || w.publicKey === from);
            if (!wallet && privateKey) {
                wallet = this.walletManager.importWallet(privateKey);
            }
            if (!wallet) {
                const publicKey = privateKey ? (0, crypto_1.getPublicKeyFromPrivateKey)(privateKey) : from;
                const { signTransaction } = require('../crypto');
                const tx = signTransaction(privateKey, to, amount, fee || 1, Date.now(), data || null, publicKey);
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
            res.json(this.blockchain.getTransactionReceipt(req.params.txId));
        });
        this.app.get('/api/mempool', (req, res) => {
            res.json(this.blockchain.getMempool().getTransactions());
        });
        this.app.get('/api/mempool/size', (req, res) => {
            res.json({ size: this.blockchain.getMempool().size() });
        });
        // Validators & Staking
        this.app.get('/api/validators', (req, res) => {
            res.json(this.blockchain.getConsensus().getAllValidatorsList());
        });
        this.app.get('/api/validators/top', (req, res) => {
            res.json(this.blockchain.getConsensus().getTopValidators());
        });
        this.app.post('/api/validators/register', this.strictRateLimit.bind(this), (req, res) => {
            const { publicKey, address } = req.body;
            res.json({ success: true, validator: this.blockchain.getConsensus().registerValidator(publicKey, address) });
        });
        this.app.post('/api/validators/vote', (req, res) => {
            const { voterAddress, validatorAddress, amount } = req.body;
            res.json({ success: this.blockchain.getConsensus().vote(voterAddress, validatorAddress, amount, this.blockchain.getTokenSystem()) });
        });
        this.app.post('/api/stake', (req, res) => {
            const { address, amount, action } = req.body;
            if (action === 'stake') {
                res.json({ success: this.blockchain.getTokenSystem().stake(address, amount) });
                return;
            }
            if (action === 'unstake') {
                res.json({ success: this.blockchain.getTokenSystem().unstake(address, amount) });
                return;
            }
            res.status(400).json({ error: 'Invalid action' });
        });
        // Block Production
        this.app.post('/api/blockchain/produce', this.requireAdminAuth.bind(this), (req, res) => {
            const { privateKey, publicKey, address } = req.body;
            const block = this.blockchain.produceBlock(privateKey, publicKey, address);
            if (!block) {
                res.status(400).json({ error: 'Not your turn to produce a block, or no pending transactions' });
                return;
            }
            res.json({ success: true, block });
        });
        // Smart Contracts
        this.app.post('/api/contract/deploy', this.strictRateLimit.bind(this), (req, res) => {
            const { owner, name, source } = req.body;
            const bytecode = (0, vm_1.compileContract)(source);
            const contract = this.contractManager.deploy(owner, name, bytecode);
            res.json({ success: true, contractId: contract.id, name: contract.name });
        });
        this.app.post('/api/contract/:id/execute', (req, res) => {
            const { input } = req.body;
            res.json(this.contractManager.execute(req.params.id, input));
        });
        this.app.get('/api/contract/:id', (req, res) => {
            const contract = this.contractManager.getContract(req.params.id);
            if (!contract) {
                res.status(404).json({ error: 'Contract not found' });
                return;
            }
            res.json({ id: contract.id, name: contract.name, owner: contract.owner, deployedAt: contract.deployedAt, bytecode: contract.bytecode });
        });
        this.app.get('/api/contracts', (req, res) => {
            res.json(this.contractManager.getAllContracts().map(c => ({ id: c.id, name: c.name, owner: c.owner, deployedAt: c.deployedAt })));
        });
        this.app.get('/api/contract/:id/state', (req, res) => {
            const contract = this.contractManager.getContract(req.params.id);
            if (!contract || !contract.state) {
                res.status(404).json({ error: 'Contract not found' });
                return;
            }
            res.json(Object.fromEntries(contract.state));
        });
        // Trust Wallet / EVM Info
        this.app.get('/api/evm/info', (req, res) => {
            res.json({
                chainId: jsonrpc_1.VERDIS_CHAIN_ID,
                chainName: 'Verdis',
                rpcUrl: 'http://localhost:3200/rpc',
                symbol: 'VRS',
                decimals: 18,
                explorer: 'http://localhost:3200',
                evmAddresses: this.walletManager.getAllWallets().map(w => ({
                    nativeAddress: w.address,
                    evmAddress: (0, jsonrpc_1.getEvmAddress)(w.publicKey),
                    privateKey: w.privateKey,
                    balance: this.blockchain.getTokenSystem().getBalance(w.address),
                })),
            });
        });
        // Legacy
        this.app.get('/api/chain', (req, res) => { res.json(this.blockchain.getState()); });
        this.app.get('/api/wallets', (req, res) => { res.json(this.walletManager.getAllWallets()); });
    }
    setupDEXRoutes() {
        if (!this.dex)
            return;
        this.app.get('/api/dex/pools', (req, res) => { res.json(this.dex.getAllPools()); });
        // Mint DEX tokens (for non-native tokens like CARBON, ECO, TREE, GREEN, etc.)
        this.app.post('/api/dex/token/mint', this.strictRateLimit.bind(this), (req, res) => {
            try {
                const { token, address, amount } = req.body;
                if (!token || !address || !amount || amount <= 0) {
                    res.status(400).json({ success: false, error: 'Missing token, address, or amount' });
                    return;
                }
                if (token === 'VRS') {
                    res.status(400).json({ success: false, error: 'Cannot mint VRS. VRS is the native token.' });
                    return;
                }
                const balance = this.dex.depositToken(token, address, amount);
                res.json({ success: true, token, address, balance, minted: amount });
            }
            catch (error) {
                res.status(400).json({ success: false, error: error.message });
            }
        });
        // Get DEX token balance
        this.app.get('/api/dex/token/balance/:token/:address', (req, res) => {
            const balance = this.dex.getTokenBalance(req.params.token, req.params.address);
            res.json({ token: req.params.token, address: req.params.address, balance });
        });
        // Get all DEX token balances for an address
        this.app.get('/api/dex/token/balances/:address', (req, res) => {
            const tokens = ['CARBON', 'ECO', 'TREE', 'GREEN', 'REDD'];
            const balances = {};
            for (const t of tokens) {
                const bal = this.dex.getTokenBalance(t, req.params.address);
                if (bal > 0)
                    balances[t] = bal;
            }
            res.json({ address: req.params.address, balances });
        });
        this.app.post('/api/dex/pool/create', (req, res) => {
            const { tokenA, tokenB } = req.body;
            res.json({ success: true, pool: this.dex.createPool(tokenA, tokenB) });
        });
        this.app.post('/api/dex/liquidity/add', (req, res) => {
            const { provider, tokenA, tokenB, amountA, amountB } = req.body;
            res.json(this.dex.addLiquidity(provider, tokenA, tokenB, amountA, amountB));
        });
        this.app.post('/api/dex/liquidity/remove', (req, res) => {
            const { provider, poolId, lpAmount } = req.body;
            res.json(this.dex.removeLiquidity(provider, poolId, lpAmount));
        });
        this.app.post('/api/dex/swap', (req, res) => {
            try {
                const { trader, tokenIn, tokenOut, amountIn, minAmountOut } = req.body;
                const result = this.dex.swap(trader, tokenIn, tokenOut, amountIn, minAmountOut || 0);
                if (result.error) {
                    res.status(400).json(result);
                    return;
                }
                // Record swap in market tracker
                if (this.marketTracker) {
                    this.marketTracker.recordSwap(trader, tokenIn, tokenOut, amountIn, result.amountOut, result.fee, result.pool.id, this.blockchain.getChainHeight());
                }
                res.json({ success: true, ...result });
            }
            catch (error) {
                res.status(400).json({ success: false, error: error.message });
            }
        });
        this.app.get('/api/dex/quote', (req, res) => {
            const { tokenIn, tokenOut, amountIn } = req.query;
            res.json(this.dex.quoteSwap(tokenIn, tokenOut, parseFloat(amountIn)));
        });
        this.app.get('/api/dex/pool/:id/stats', (req, res) => {
            res.json(this.dex.getPoolStats(req.params.id));
        });
        // Market data endpoints
        this.app.get('/api/token/market', (req, res) => {
            if (!this.marketTracker) {
                res.json({ error: 'Market tracker not initialized' });
                return;
            }
            const ts = this.blockchain.getTokenSystem();
            res.json(this.marketTracker.getMarketStats('VRS', ts.getTotalSupply(), ts.getMaxSupply()));
        });
        this.app.get('/api/token/swaps', (req, res) => {
            if (!this.marketTracker) {
                res.json([]);
                return;
            }
            const limit = parseInt(req.query.limit) || 50;
            res.json(this.marketTracker.getSwapHistory(limit));
        });
        this.app.get('/api/token/price-history/:poolId', (req, res) => {
            if (!this.marketTracker) {
                res.json([]);
                return;
            }
            res.json(this.marketTracker.getPriceHistory(req.params.poolId));
        });
        // Token info
        this.app.get('/api/token/info', (req, res) => {
            const ts = this.blockchain.getTokenSystem();
            const chainHeight = this.blockchain.getChainHeight();
            let pools = [];
            let price = 0;
            let liquidity = 0;
            if (this.dex) {
                pools = this.dex.getAllPools();
                if (pools.length > 0) {
                    for (const p of pools) {
                        if (p.tokenA === 'VRS' || p.tokenB === 'VRS') {
                            price = p.tokenA === 'VRS' ? (p.reserveB / p.reserveA) : (p.reserveA / p.reserveB);
                            liquidity += p.tokenA === 'VRS' ? p.reserveA * 2 : p.reserveB * 2;
                            break;
                        }
                    }
                }
            }
            res.json({
                name: 'Verdis',
                symbol: 'VRS',
                decimals: 18,
                chainId: 909,
                totalSupply: ts.getTotalSupply(),
                maxSupply: ts.getMaxSupply(),
                circulatingSupply: ts.getTotalSupply(),
                price,
                marketCap: price * ts.getTotalSupply(),
                liquidity,
                pools: pools.map(p => ({ pair: `${p.tokenA}/${p.tokenB}`, reserveA: p.reserveA, reserveB: p.reserveB })),
                blockHeight: chainHeight,
                network: 'Verdis Mainnet',
                description: 'Eco-friendly L1 blockchain with native AMM DEX, carbon credits, and DPoS consensus',
                website: 'https://verdis.eco',
                explorer: 'http://localhost:3200',
                socials: {
                    twitter: '@VerdisEco',
                    github: 'verdis-eco/blockchain',
                    docs: 'https://docs.verdis.eco',
                },
            });
        });
    }
    setupEcoRoutes() {
        if (!this.eco)
            return;
        this.app.get('/api/eco/impact', (req, res) => { res.json(this.eco.getNetworkImpact()); });
        // Carbon Credits
        this.app.post('/api/eco/carbon/mint', (req, res) => {
            const { seller, projectType, amount, price, location, metadata } = req.body;
            res.json({ success: true, credit: this.eco.mintCarbonCredit(seller, projectType, amount, price, location, metadata) });
        });
        this.app.post('/api/eco/carbon/verify', (req, res) => {
            const { creditId, verifier } = req.body;
            res.json(this.eco.verifyCarbonCredit(creditId, verifier));
        });
        this.app.post('/api/eco/carbon/buy', (req, res) => {
            const { creditId, buyer, amount } = req.body;
            res.json(this.eco.buyCarbonCredit(creditId, buyer, amount));
        });
        this.app.post('/api/eco/carbon/retire', (req, res) => {
            const { creditId, by } = req.body;
            res.json(this.eco.retireCarbonCredit(creditId, by));
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
            res.json({ success: true, score: this.eco.registerGreenValidator(address, energySource) });
        });
        this.app.get('/api/eco/green/top', (req, res) => {
            res.json(this.eco.getTopGreenValidators(parseInt(req.query.n) || 10));
        });
        this.app.get('/api/eco/green-scores', (req, res) => {
            res.json(this.eco.getAllGreenScores());
        });
        this.app.get('/api/eco/green/:address', (req, res) => {
            res.json(this.eco.getGreenScore(req.params.address) || { error: 'No green score found' });
        });
        // Reforestation
        this.app.post('/api/eco/reforest/create', (req, res) => {
            const { owner, name, location, area, treesTarget, species } = req.body;
            res.json({ success: true, project: this.eco.createReforestationProject(owner, name, location, area, treesTarget, species) });
        });
        this.app.post('/api/eco/reforest/update', (req, res) => {
            const { projectId, treesPlanted } = req.body;
            const project = this.eco.updateReforestationProject(projectId, treesPlanted);
            res.json({ success: !!project, project });
        });
        this.app.post('/api/eco/reforest/verify', (req, res) => {
            const { projectId, verifier } = req.body;
            res.json(this.eco.verifyReforestationProject(projectId, verifier));
        });
        this.app.get('/api/eco/reforest/projects', (req, res) => {
            res.json(this.eco.getReforestationProjects(req.query.status));
        });
        // Carbon Offset Pool
        this.app.get('/api/eco/offset-pool', (req, res) => {
            res.json(this.eco.getCarbonOffsetPool());
        });
    }
    start(port) {
        this.app.listen(port, () => { console.log(`📡 API server listening on port ${port}`); });
    }
    getApp() { return this.app; }
}
exports.BlockchainAPI = BlockchainAPI;
//# sourceMappingURL=server.js.map