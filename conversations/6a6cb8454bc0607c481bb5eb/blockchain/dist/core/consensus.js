"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Blockchain = exports.DPoSConsensus = exports.TokenSystem = void 0;
const sha256_1 = require("@noble/hashes/sha256");
class TokenSystem {
    constructor() {
        this.totalSupply = 1000000000;
        this.maxSupply = 2000000000;
    }
    getTotalSupply() {
        return this.totalSupply;
    }
    getMaxSupply() {
        return this.maxSupply;
    }
}
exports.TokenSystem = TokenSystem;
class DPoSConsensus {
    constructor() {
        this.activeValidators = new Map();
    }
    getValidators() {
        return Array.from(this.activeValidators.values());
    }
}
exports.DPoSConsensus = DPoSConsensus;
class Blockchain {
    constructor() {
        this.chain = [];
        this.mempool = [];
        this.validators = new Map();
        this.stakes = [];
        this.balances = new Map();
        this.totalSupply = 100000000;
        this.maxSupply = 1000000000;
        this.blockReward = 10;
        this.createGenesisBlock();
    }
    createGenesisBlock() {
        const genesisHeader = {
            index: 0,
            previousHash: '0'.repeat(64),
            timestamp: Date.now(),
            merkleRoot: '0'.repeat(64),
            validator: 'genesis',
            validatorSignature: 'genesis_sig',
            difficulty: 1,
            nonce: 0,
        };
        const genesisBlock = {
            header: genesisHeader,
            transactions: [],
            hash: Buffer.from((0, sha256_1.sha256)(Buffer.from(JSON.stringify(genesisHeader)))).toString('hex'),
        };
        this.chain.push(genesisBlock);
    }
    getBalance(address) {
        return this.balances.get(address) || 0;
    }
    getStakedAmount(address) {
        return this.stakes
            .filter((s) => s.voter === address)
            .reduce((acc, s) => acc + s.amount, 0);
    }
    submitTransaction(tx) {
        if (!tx || !tx.id)
            throw new Error('Invalid transaction');
        this.mempool.push(tx);
        return tx.id;
    }
    getTransactionReceipt(txId) {
        // Check blocks
        for (const block of this.chain) {
            const tx = block.transactions.find((t) => t.id === txId);
            if (tx) {
                return {
                    transaction: tx,
                    blockIndex: block.header.index,
                    blockHash: block.hash,
                    confirmations: this.chain.length - block.header.index,
                    status: 'confirmed',
                };
            }
        }
        // Check mempool
        const pendingTx = this.mempool.find((t) => t.id === txId);
        if (pendingTx) {
            return {
                transaction: pendingTx,
                blockIndex: -1,
                blockHash: '',
                confirmations: 0,
                status: 'pending',
            };
        }
        return null;
    }
    getMempool() {
        return [...this.mempool];
    }
    getMempoolSize() {
        return this.mempool.length;
    }
    getChainInfo() {
        return {
            height: this.chain.length,
            totalSupply: this.totalSupply,
            maxSupply: this.maxSupply,
            validatorCount: this.validators.size,
            blockReward: this.blockReward,
        };
    }
    getChainHeight() {
        return this.chain.length;
    }
    getBlocks(limit = 20, offset = 0) {
        return this.chain.slice(offset, offset + limit);
    }
    getBlockByIndex(index) {
        if (index < 0 || index >= this.chain.length)
            return null;
        return this.chain[index];
    }
    getBlockByHash(hash) {
        return this.chain.find((b) => b.hash === hash) || null;
    }
    getValidators() {
        return Array.from(this.validators.values());
    }
    getTopValidators(limit = 27) {
        const list = Array.from(this.validators.values());
        list.sort((a, b) => b.votes - a.votes);
        return list.slice(0, limit);
    }
    registerValidator(publicKey) {
        if (!publicKey)
            throw new Error('Public key is required to register validator');
        const existing = this.validators.get(publicKey);
        if (existing)
            return existing;
        const validator = {
            publicKey,
            address: `0x${publicKey.slice(0, 20)}`,
            votes: 0,
            isProducer: true,
            blocksProduced: 0,
            totalRewards: 0,
        };
        this.validators.set(publicKey, validator);
        return validator;
    }
    voteForValidator(voterAddress, validatorAddress, amount, privateKey) {
        if (!voterAddress || !validatorAddress || !privateKey)
            throw new Error('Missing required voting fields');
        if (amount <= 0)
            throw new Error('Vote amount must be greater than zero');
        const voterBalance = this.getBalance(voterAddress);
        if (voterBalance < amount) {
            throw new Error('Insufficient balance to vote');
        }
        this.balances.set(voterAddress, voterBalance - amount);
        const stake = {
            voter: voterAddress,
            validator: validatorAddress,
            amount,
            timestamp: Date.now(),
        };
        this.stakes.push(stake);
        // Update validator vote count
        for (const val of this.validators.values()) {
            if (val.address === validatorAddress || val.publicKey === validatorAddress) {
                val.votes += amount;
            }
        }
        return stake;
    }
    stake(address, amount) {
        if (!address)
            throw new Error('Address is required');
        if (amount <= 0)
            throw new Error('Stake amount must be greater than zero');
        const balance = this.getBalance(address);
        if (balance < amount)
            throw new Error('Insufficient balance to stake');
        this.balances.set(address, balance - amount);
        return true;
    }
    unstake(address, amount) {
        if (!address)
            throw new Error('Address is required');
        if (amount <= 0)
            throw new Error('Unstake amount must be greater than zero');
        const currentStaked = this.getStakedAmount(address);
        if (currentStaked < amount)
            throw new Error('Unstake amount exceeds total staked');
        const currentBalance = this.getBalance(address);
        this.balances.set(address, currentBalance + amount);
        return true;
    }
    produceBlock(publicKey, privateKey) {
        if (!publicKey || !privateKey)
            throw new Error('Public key and private key are required to produce block');
        const lastBlock = this.chain[this.chain.length - 1];
        const newIndex = lastBlock.header.index + 1;
        const txsToInclude = [...this.mempool];
        this.mempool = [];
        const header = {
            index: newIndex,
            previousHash: lastBlock.hash,
            timestamp: Date.now(),
            merkleRoot: Buffer.from((0, sha256_1.sha256)(Buffer.from(JSON.stringify(txsToInclude)))).toString('hex'),
            validator: publicKey,
            validatorSignature: `sig_${privateKey.slice(0, 8)}`,
            difficulty: 1,
            nonce: 0,
        };
        const blockHash = Buffer.from((0, sha256_1.sha256)(Buffer.from(JSON.stringify(header)))).toString('hex');
        const block = {
            header,
            transactions: txsToInclude,
            hash: blockHash,
        };
        this.chain.push(block);
        // Award block reward
        const validator = this.validators.get(publicKey);
        if (validator) {
            validator.blocksProduced += 1;
            validator.totalRewards += this.blockReward;
        }
        return block;
    }
    allocateGenesis(address, amount) {
        if (this.chain.length > 1) {
            throw new Error('Genesis allocation is only allowed before any blocks are produced');
        }
        if (!address)
            throw new Error('Address is required');
        if (amount <= 0)
            throw new Error('Allocation amount must be greater than zero');
        const currentBalance = this.getBalance(address);
        this.balances.set(address, currentBalance + amount);
        return true;
    }
}
exports.Blockchain = Blockchain;
//# sourceMappingURL=consensus.js.map