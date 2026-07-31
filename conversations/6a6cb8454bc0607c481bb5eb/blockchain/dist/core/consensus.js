"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.Blockchain = exports.Mempool = exports.Consensus = exports.TokenSystem = void 0;
const crypto_1 = __importDefault(require("crypto"));
class TokenSystem {
    constructor() {
        this.balances = new Map();
        this.stakes = new Map();
    }
    getBalance(address) {
        return this.balances.get(address) || 0;
    }
    setBalance(address, amount) {
        this.balances.set(address, amount);
    }
    addBalance(address, amount) {
        const current = this.getBalance(address);
        this.balances.set(address, current + amount);
    }
    getStaked(address) {
        return this.stakes.get(address) || 0;
    }
    stake(address, amount) {
        const currentBal = this.getBalance(address);
        if (currentBal >= amount) {
            this.balances.set(address, currentBal - amount);
        }
        const currentStaked = this.getStaked(address);
        this.stakes.set(address, currentStaked + amount);
    }
    getBalancesMap() {
        return this.balances;
    }
}
exports.TokenSystem = TokenSystem;
class Consensus {
    constructor() {
        this.validators = new Map();
        this.stakes = [];
    }
    registerValidator(publicKey, address) {
        const valAddress = address || publicKey;
        const existing = this.validators.get(publicKey) || this.validators.get(valAddress);
        if (existing) {
            return existing;
        }
        const validator = {
            publicKey,
            address: valAddress,
            votes: 0,
            isProducer: true,
            blocksProduced: 0,
            totalRewards: 0,
        };
        this.validators.set(publicKey, validator);
        this.validators.set(valAddress, validator);
        return validator;
    }
    vote(voterAddress, validatorAddressOrKey, amount, tokenSystem) {
        const validator = this.validators.get(validatorAddressOrKey);
        if (validator) {
            validator.votes += amount;
        }
        this.stakes.push({
            voter: voterAddress,
            validator: validatorAddressOrKey,
            amount,
            timestamp: Date.now(),
        });
    }
    getValidators() {
        return this.validators;
    }
    getAllValidatorsList() {
        const uniqueValidators = new Set();
        for (const validator of this.validators.values()) {
            uniqueValidators.add(validator);
        }
        return Array.from(uniqueValidators);
    }
}
exports.Consensus = Consensus;
class Mempool {
    constructor() {
        this.pendingTransactions = [];
    }
    addTransaction(tx) {
        this.pendingTransactions.push(tx);
        return true;
    }
    getPendingTransactions() {
        return [...this.pendingTransactions];
    }
    clear() {
        this.pendingTransactions = [];
    }
}
exports.Mempool = Mempool;
class Blockchain {
    constructor() {
        this.chain = [];
        this.consensus = new Consensus();
        this.tokenSystem = new TokenSystem();
        this.mempool = new Mempool();
        this.maxSupply = 100000000000; // 100 Billion
        this.totalSupply = 0;
        this.createGenesisBlock();
    }
    createGenesisBlock() {
        const genesisBlock = {
            header: {
                index: 0,
                previousHash: '0'.repeat(64),
                timestamp: Date.now(),
                merkleRoot: '0'.repeat(64),
                validator: 'GENESIS',
                validatorSignature: '',
                difficulty: 1,
                nonce: 0,
            },
            transactions: [],
            hash: crypto_1.default.createHash('sha256').update('GENESIS_BLOCK').digest('hex'),
        };
        this.chain.push(genesisBlock);
    }
    addGenesisAllocation(address, amount) {
        if (this.totalSupply + amount > this.maxSupply) {
            throw new Error('Genesis allocation exceeds maximum supply limit');
        }
        this.tokenSystem.addBalance(address, amount);
        this.totalSupply += amount;
    }
    getConsensus() {
        return this.consensus;
    }
    getTokenSystem() {
        return this.tokenSystem;
    }
    getMempool() {
        return this.mempool;
    }
    getChain() {
        return this.chain;
    }
    getLatestBlock() {
        return this.chain[this.chain.length - 1];
    }
    getState() {
        return {
            chain: this.chain,
            mempool: this.mempool.getPendingTransactions(),
            validators: this.consensus.getValidators(),
            stakes: [],
            balances: this.tokenSystem.getBalancesMap(),
            contracts: new Map(),
            totalSupply: this.totalSupply,
            maxSupply: this.maxSupply,
            blockReward: 50,
            validatorCount: this.consensus.getAllValidatorsList().length,
            currentHeight: this.chain.length - 1,
        };
    }
}
exports.Blockchain = Blockchain;
//# sourceMappingURL=consensus.js.map