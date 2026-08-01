"use strict";
/**
 * Verdis Blockchain SDK
 * 
 * JavaScript/TypeScript SDK for interacting with the Verdis blockchain.
 * Full-featured: wallet, transactions, DEX, contracts, governance, eco, AI agents.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.VerdisSDK = void 0;
const crypto_2 = require("../crypto");
class VerdisSDK {
    constructor(rpcUrl = 'https://rpc.verdischain.com', options = {}) {
        this.rpcUrl = rpcUrl;
        this.apiBase = options.apiBase || rpcUrl.replace('/rpc', '');
        this.timeout = options.timeout || 30000;
        this.wallet = null;
        this.apiKey = options.apiKey || null;
    }
    // === HTTP Helper ===
    async request(method, path, body) {
        const headers = { 'Content-Type': 'application/json' };
        if (this.apiKey) headers['X-API-Key'] = this.apiKey;
        const url = path.startsWith('/rpc') ? this.rpcUrl : `${this.apiBase}${path}`;
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), this.timeout);
        try {
            const res = await fetch(url, {
                method,
                headers,
                body: body ? JSON.stringify(body) : undefined,
                signal: controller.signal,
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
            return data;
        } finally {
            clearTimeout(timeout);
        }
    }
    // === Wallet ===
    createWallet() {
        const { privateKey, publicKey, address } = (0, crypto_2.generateKeyPair)();
        this.wallet = { privateKey, publicKey, address };
        return this.wallet;
    }
    importWallet(privateKey) {
        const publicKey = (0, crypto_2.getPublicKeyFromPrivate)(privateKey);
        const address = (0, crypto_2.getAddressFromPublicKey)(publicKey);
        this.wallet = { privateKey, publicKey, address };
        return this.wallet;
    }
    getWallet() {
        return this.wallet;
    }
    // === Blockchain ===
    async getBlockHeight() {
        const info = await this.request('GET', '/api/blockchain/info');
        return info.height;
    }
    async getBlockchainInfo() {
        return this.request('GET', '/api/blockchain/info');
    }
    async getBlock(height) {
        return this.request('GET', `/api/blockchain/block/${height}`);
    }
    async getTransaction(txHash) {
        return this.request('GET', `/api/blockchain/tx/${txHash}`);
    }
    async getMempool() {
        return this.request('GET', '/api/blockchain/mempool');
    }
    // === Transactions ===
    async sendTransaction(to, amount, fee = 1) {
        if (!this.wallet) throw new Error('No wallet loaded. Call createWallet() or importWallet().');
        const tx = {
            from: this.wallet.address,
            to,
            amount,
            fee,
            nonce: Date.now(),
            timestamp: Date.now(),
        };
        // Sign transaction
        const { sign } = require('../crypto');
        const hash = (0, crypto_2.hashTransaction)(tx);
        tx.signature = sign(hash, this.wallet.privateKey);
        tx.publicKey = this.wallet.publicKey;
        return this.request('POST', '/api/blockchain/transaction', tx);
    }
    async getBalance(address) {
        const addr = address || this.wallet?.address;
        if (!addr) throw new Error('No address provided and no wallet loaded');
        return this.request('GET', `/api/wallet/balance/${addr}`);
    }
    async getWalletInfo(address) {
        const addr = address || this.wallet?.address;
        return this.request('GET', `/api/wallet/${addr}`);
    }
    // === DEX ===
    async getDexPools() {
        return this.request('GET', '/api/dex/pools');
    }
    async getPool(tokenA, tokenB) {
        return this.request('GET', `/api/dex/pool/${tokenA}/${tokenB}`);
    }
    async swap(tokenIn, tokenOut, amountIn, minAmountOut = 0) {
        if (!this.wallet) throw new Error('No wallet loaded');
        return this.request('POST', '/api/dex/swap', {
            trader: this.wallet.address,
            tokenIn, tokenOut, amountIn, minAmountOut,
        });
    }
    async addLiquidity(tokenA, tokenB, amountA, amountB) {
        if (!this.wallet) throw new Error('No wallet loaded');
        return this.request('POST', '/api/dex/liquidity/add', {
            provider: this.wallet.address,
            tokenA, tokenB, amountA, amountB,
        });
    }
    async getTokenPrice(token) {
        return this.request('GET', `/api/dex/price/${token}`);
    }
    async getMarketData() {
        return this.request('GET', '/api/token/market');
    }
    // === Smart Contracts ===
    async deployContract(name, bytecode, gasLimit = 500000) {
        if (!this.wallet) throw new Error('No wallet loaded');
        return this.request('POST', '/api/contracts/deploy', {
            deployer: this.wallet.address,
            name, bytecode, gasLimit,
        });
    }
    async executeContract(contractId, method, args, value = 0) {
        if (!this.wallet) throw new Error('No wallet loaded');
        return this.request('POST', '/api/contracts/execute', {
            caller: this.wallet.address,
            contractId, method, args, value,
        });
    }
    async getContract(id) {
        return this.request('GET', `/api/contracts/${id}`);
    }
    async listContracts() {
        return this.request('GET', '/api/contracts');
    }
    // === Governance ===
    async createProposal(title, description, type, actions) {
        if (!this.wallet) throw new Error('No wallet loaded');
        return this.request('POST', '/api/governance/proposal/create', {
            proposer: this.wallet.address,
            title, description, proposalType: type, actions,
        });
    }
    async voteOnProposal(proposalId, vote) {
        if (!this.wallet) throw new Error('No wallet loaded');
        return this.request('POST', '/api/governance/vote', {
            voter: this.wallet.address,
            proposalId, vote,
        });
    }
    async getProposals() {
        return this.request('GET', '/api/governance/proposals');
    }
    async getProposal(id) {
        return this.request('GET', `/api/governance/proposal/${id}`);
    }
    async executeProposal(id) {
        if (!this.wallet) throw new Error('No wallet loaded');
        return this.request('POST', '/api/governance/execute', {
            proposalId: id,
            callerAddress: this.wallet.address,
        });
    }
    // === Name Service ===
    async registerName(name) {
        if (!this.wallet) throw new Error('No wallet loaded');
        return this.request('POST', '/api/vns/register', {
            name, ownerAddress: this.wallet.address,
        });
    }
    async resolveName(name) {
        return this.request('GET', `/api/vns/resolve/${name}`);
    }
    // === AI Agents ===
    async registerAgent(agentId, metadata) {
        if (!this.wallet) throw new Error('No wallet loaded');
        return this.request('POST', '/api/ai/agent/register', {
            agentId, ownerAddress: this.wallet.address,
            walletAddress: this.wallet.address, metadata,
        });
    }
    async getAIStats() {
        return this.request('GET', '/api/ai/stats');
    }
    // === Eco ===
    async getEcoStats() {
        return this.request('GET', '/api/eco/stats');
    }
    async mintCarbonCredits(amount, source, certificateId) {
        if (!this.wallet) throw new Error('No wallet loaded');
        return this.request('POST', '/api/eco/carbon/mint', {
            address: this.wallet.address, amount, source, certificateId,
        });
    }
    async logReforestation(treesPlanted, location, species) {
        if (!this.wallet) throw new Error('No wallet loaded');
        return this.request('POST', '/api/eco/reforestation', {
            address: this.wallet.address, treesPlanted, location, species,
        });
    }
    // === Tokenomics ===
    async getTokenomics() {
        return this.request('GET', '/api/tokenomics/info');
    }
    // === Account Abstraction ===
    async createSmartWallet(config) {
        if (!this.wallet) throw new Error('No wallet loaded');
        return this.request('POST', '/api/aa/wallet/create', {
            ownerAddress: this.wallet.address, config,
        });
    }
    async createSessionKey(dappContract, permissions, expiryMinutes) {
        if (!this.wallet) throw new Error('No wallet loaded');
        return this.request('POST', '/api/aa/session/create', {
            walletAddress: this.wallet.address,
            ownerAddress: this.wallet.address,
            dappContract, permissions, expiryMinutes,
        });
    }
    // === Fraud Detection ===
    async getFraudAlerts() {
        return this.request('GET', '/api/fraud/alerts');
    }
    async getFraudStats() {
        return this.request('GET', '/api/fraud/stats');
    }
    // === JSON-RPC ===
    async rpc(method, params = []) {
        return this.request('POST', '/rpc', {
            jsonrpc: '2.0', method, params, id: 1,
        });
    }
    async getChainId() {
        const res = await this.rpc('eth_chainId');
        return parseInt(res.result, 16);
    }
    async getGasPrice() {
        const res = await this.rpc('eth_gasPrice');
        return parseInt(res.result, 16);
    }
}
exports.VerdisSDK = VerdisSDK;
// Default export
exports.default = VerdisSDK;
