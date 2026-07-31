"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Blockchain = exports.DPoSConsensus = exports.TokenSystem = void 0;
const crypto_1 = require("../crypto");
const block_1 = require("./block");
const transaction_1 = require("./transaction");
/**
 * TokenSystem — manages native VRS token balances, staking, and transfers.
 */
class TokenSystem {
    constructor() {
        this.balances = new Map();
        this.stakes = new Map();
        this.maxSupply = 100000000000; // 100 billion
        this.totalSupply = 0;
        this.blockReward = 16; // VRS per block (like Tron)
    }
    getBalance(address) {
        return this.balances.get(address) || 0;
    }
    setBalance(address, amount) {
        this.balances.set(address, amount);
    }
    addBalance(address, amount) {
        this.balances.set(address, this.getBalance(address) + amount);
    }
    deductBalance(address, amount) {
        const current = this.getBalance(address);
        if (current < amount)
            return false;
        this.balances.set(address, current - amount);
        return true;
    }
    transfer(from, to, amount) {
        if (amount <= 0)
            return false;
        if (!this.deductBalance(from, amount))
            return false;
        this.addBalance(to, amount);
        return true;
    }
    mint(address, amount) {
        if (this.totalSupply + amount > this.maxSupply) {
            amount = this.maxSupply - this.totalSupply;
        }
        this.addBalance(address, amount);
        this.totalSupply += amount;
    }
    getStaked(address) {
        return this.stakes.get(address) || 0;
    }
    stake(address, amount) {
        if (!this.deductBalance(address, amount))
            return false;
        this.stakes.set(address, this.getStaked(address) + amount);
        return true;
    }
    unstake(address, amount) {
        const currentStaked = this.getStaked(address);
        if (currentStaked < amount)
            return false;
        this.stakes.set(address, currentStaked - amount);
        this.addBalance(address, amount);
        return true;
    }
    applyTransaction(tx, blockProducer) {
        // Deduct amount + fee from sender
        if (!this.deductBalance(tx.from, tx.amount + tx.fee))
            return false;
        // Add amount to receiver
        this.addBalance(tx.to, tx.amount);
        // Fee goes to block producer
        if (tx.fee > 0) {
            this.addBalance(blockProducer, tx.fee);
        }
        return true;
    }
    getBalancesMap() {
        return this.balances;
    }
    getTotalSupply() {
        return this.totalSupply;
    }
    getMaxSupply() {
        return this.maxSupply;
    }
    getBlockReward() {
        return this.blockReward;
    }
    setTotalSupply(amount) {
        this.totalSupply = amount;
    }
}
exports.TokenSystem = TokenSystem;
/**
 * DPoSConsensus — Tron-style delegated proof of stake with 27 super representatives.
 */
class DPoSConsensus {
    constructor() {
        this.validators = new Map();
        this.stakes = [];
        this.validatorCount = 27;
        this.blockReward = 16;
        this.roundTurn = 0;
    }
    registerValidator(publicKey, address) {
        const valAddress = address || publicKey;
        const lookupKey = address || publicKey;
        const existing = this.validators.get(lookupKey);
        if (existing)
            return existing;
        const validator = {
            publicKey,
            address: valAddress,
            votes: 0,
            isProducer: true,
            blocksProduced: 0,
            totalRewards: 0,
        };
        this.validators.set(valAddress, validator);
        return validator;
    }
    vote(voterAddress, validatorAddress, amount, tokenSystem) {
        const validator = this.validators.get(validatorAddress);
        if (!validator)
            return false;
        validator.votes += amount;
        this.stakes.push({
            voter: voterAddress,
            validator: validatorAddress,
            amount,
            timestamp: Date.now(),
        });
        return true;
    }
    getTopValidators() {
        const all = this.getAllValidatorsList();
        all.sort((a, b) => b.votes - a.votes);
        return all.slice(0, this.validatorCount);
    }
    getCurrentProducer() {
        const top = this.getTopValidators();
        if (top.length === 0)
            return null;
        return top[this.roundTurn % top.length];
    }
    rotateProducer() {
        this.roundTurn++;
    }
    distributeRewards(producer, tokenSystem) {
        const reward = tokenSystem.getBlockReward();
        // 80% to producer
        const producerReward = Math.floor(reward * 0.8);
        tokenSystem.addBalance(producer.address, producerReward);
        producer.totalRewards += producerReward;
        // 20% to voters proportional to stake
        const voterStakes = this.stakes.filter(s => s.validator === producer.address);
        const totalVoterStake = voterStakes.reduce((sum, s) => sum + s.amount, 0);
        if (totalVoterStake > 0) {
            const voterRewardPool = reward - producerReward;
            for (const stakeEntry of voterStakes) {
                const share = Math.floor(voterRewardPool * (stakeEntry.amount / totalVoterStake));
                if (share > 0) {
                    tokenSystem.addBalance(stakeEntry.voter, share);
                }
            }
        }
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
    getStakes() {
        return this.stakes;
    }
    getValidatorCount() {
        return this.validatorCount;
    }
    incrementBlocksProduced(validatorAddress) {
        const validator = this.validators.get(validatorAddress);
        if (validator) {
            validator.blocksProduced++;
        }
    }
}
exports.DPoSConsensus = DPoSConsensus;
/**
 * Blockchain — the main chain manager. Handles block production, validation, and queries.
 */
class Blockchain {
    constructor() {
        this.chain = [];
        this.mempool = new transaction_1.Mempool();
        this.consensus = new DPoSConsensus();
        this.tokenSystem = new TokenSystem();
        this.chain.push((0, block_1.createGenesisBlock)());
    }
    /**
     * Allocates genesis tokens to an address (only before block 1).
     */
    addGenesisAllocation(address, amount) {
        if (this.chain.length > 1) {
            throw new Error('Genesis allocations can only be made before block 1 is produced');
        }
        this.tokenSystem.addBalance(address, amount);
        this.tokenSystem.setTotalSupply(this.tokenSystem.getTotalSupply() + amount);
    }
    /**
     * Produces a new block. Must be the current producer's turn.
     */
    produceBlock(validatorPrivateKey, validatorPublicKey, validatorAddress) {
        const currentProducer = this.consensus.getCurrentProducer();
        if (!currentProducer)
            return null;
        if (currentProducer.address !== validatorAddress && currentProducer.publicKey !== validatorPublicKey) {
            return null; // Not this validator's turn
        }
        const latestBlock = this.getLatestBlock();
        const pendingTxs = this.mempool.getPendingTransactions(100); // Max 100 txs per block
        // Sign the block header
        const blockPayload = `${latestBlock.hash}:${pendingTxs.length}:${Date.now()}`;
        const sigResult = (0, crypto_1.sign)(blockPayload, validatorPrivateKey);
        const newBlock = (0, block_1.createBlock)(latestBlock.header.index + 1, latestBlock.hash, pendingTxs, validatorPublicKey, sigResult.signature, 0, // difficulty (DPoS doesn't use PoW)
        0 // nonce
        );
        // Validate the new block
        if (!(0, block_1.validateBlock)(newBlock, latestBlock)) {
            return null;
        }
        // Apply all transactions
        for (const tx of pendingTxs) {
            this.tokenSystem.applyTransaction(tx, validatorAddress);
            this.mempool.removeTransaction(tx.id);
        }
        // Distribute block reward
        this.tokenSystem.mint(validatorAddress, 0); // Rewards handled by distributeRewards
        this.consensus.distributeRewards(currentProducer, this.tokenSystem);
        this.consensus.incrementBlocksProduced(validatorAddress);
        // Add block to chain
        this.chain.push(newBlock);
        // Rotate to next producer
        this.consensus.rotateProducer();
        return newBlock;
    }
    /**
     * Submits a transaction to the mempool.
     */
    submitTransaction(tx) {
        return this.mempool.addTransaction(tx, this.tokenSystem.getBalancesMap());
    }
    /**
     * Finds a transaction in the chain and returns its block.
     */
    getTransactionReceipt(txId) {
        for (const block of this.chain) {
            for (const tx of block.transactions) {
                if (tx.id === txId) {
                    return { block, tx };
                }
            }
        }
        return { block: null, tx: null };
    }
    getChain() {
        return this.chain;
    }
    getLatestBlock() {
        return this.chain[this.chain.length - 1];
    }
    getBlockByIndex(index) {
        return this.chain.find(b => b.header.index === index);
    }
    getBlockByHash(hash) {
        return this.chain.find(b => b.hash === hash);
    }
    getChainHeight() {
        return this.chain.length - 1;
    }
    isChainValid() {
        return (0, block_1.isChainValid)(this.chain);
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
    getState() {
        return {
            chain: this.chain,
            mempool: this.mempool.getTransactions(),
            validators: this.consensus.getValidators(),
            stakes: this.consensus.getStakes(),
            balances: this.tokenSystem.getBalancesMap(),
            contracts: new Map(),
            totalSupply: this.tokenSystem.getTotalSupply(),
            maxSupply: this.tokenSystem.getMaxSupply(),
            blockReward: this.tokenSystem.getBlockReward(),
            validatorCount: this.consensus.getValidatorCount(),
            currentHeight: this.getChainHeight(),
        };
    }
}
exports.Blockchain = Blockchain;
//# sourceMappingURL=consensus.js.map