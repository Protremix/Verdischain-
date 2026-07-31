import crypto from 'crypto';
import { Block, Transaction, Validator, Stake, BlockchainState } from '../types';
import { sha256, sign, getPublicKeyFromPrivateKey, getAddressFromPublicKey } from '../crypto';
import { createBlock, createGenesisBlock, validateBlock, isChainValid as validateChain, MerkleTree } from './block';
import { Mempool, validateTransaction } from './transaction';

/**
 * TokenSystem — manages native VRS token balances, staking, and transfers.
 */
export class TokenSystem {
  private balances: Map<string, number> = new Map();
  private stakes: Map<string, number> = new Map();
  private maxSupply: number = 100_000_000_000; // 100 billion
  private totalSupply: number = 0;
  private blockReward: number = 16; // VRS per block (like Tron)

  getBalance(address: string): number {
    return this.balances.get(address) || 0;
  }

  setBalance(address: string, amount: number): void {
    this.balances.set(address, amount);
  }

  addBalance(address: string, amount: number): void {
    this.balances.set(address, this.getBalance(address) + amount);
  }

  deductBalance(address: string, amount: number): boolean {
    const current = this.getBalance(address);
    if (current < amount) return false;
    this.balances.set(address, current - amount);
    return true;
  }

  transfer(from: string, to: string, amount: number): boolean {
    if (amount <= 0) return false;
    if (!this.deductBalance(from, amount)) return false;
    this.addBalance(to, amount);
    return true;
  }

  mint(address: string, amount: number): void {
    if (this.totalSupply + amount > this.maxSupply) {
      amount = this.maxSupply - this.totalSupply;
    }
    this.addBalance(address, amount);
    this.totalSupply += amount;
  }

  getStaked(address: string): number {
    return this.stakes.get(address) || 0;
  }

  stake(address: string, amount: number): boolean {
    if (!this.deductBalance(address, amount)) return false;
    this.stakes.set(address, this.getStaked(address) + amount);
    return true;
  }

  unstake(address: string, amount: number): boolean {
    const currentStaked = this.getStaked(address);
    if (currentStaked < amount) return false;
    this.stakes.set(address, currentStaked - amount);
    this.addBalance(address, amount);
    return true;
  }

  applyTransaction(tx: Transaction, blockProducer: string): boolean {
    // Deduct amount + fee from sender
    if (!this.deductBalance(tx.from, tx.amount + tx.fee)) return false;
    // Add amount to receiver
    this.addBalance(tx.to, tx.amount);
    // Fee goes to block producer
    if (tx.fee > 0) {
      this.addBalance(blockProducer, tx.fee);
    }
    return true;
  }

  getBalancesMap(): Map<string, number> {
    return this.balances;
  }

  getTotalSupply(): number {
    return this.totalSupply;
  }

  getMaxSupply(): number {
    return this.maxSupply;
  }

  getBlockReward(): number {
    return this.blockReward;
  }

  setTotalSupply(amount: number): void {
    this.totalSupply = amount;
  }
}

/**
 * DPoSConsensus — Tron-style delegated proof of stake with 27 super representatives.
 */
export class DPoSConsensus {
  private validators: Map<string, Validator> = new Map();
  private stakes: Stake[] = [];
  private validatorCount: number = 27;
  private blockReward: number = 16;
  private roundTurn: number = 0;

  registerValidator(publicKey: string, address?: string): Validator {
    const valAddress = address || publicKey;
    const lookupKey = address || publicKey;
    const existing = this.validators.get(lookupKey);
    if (existing) return existing;

    const validator: Validator = {
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

  vote(voterAddress: string, validatorAddress: string, amount: number, tokenSystem?: TokenSystem): boolean {
    const validator = this.validators.get(validatorAddress);
    if (!validator) return false;

    validator.votes += amount;
    this.stakes.push({
      voter: voterAddress,
      validator: validatorAddress,
      amount,
      timestamp: Date.now(),
    });
    return true;
  }

  getTopValidators(): Validator[] {
    const all = this.getAllValidatorsList();
    all.sort((a, b) => b.votes - a.votes);
    return all.slice(0, this.validatorCount);
  }

  getCurrentProducer(): Validator | null {
    const top = this.getTopValidators();
    if (top.length === 0) return null;
    return top[this.roundTurn % top.length];
  }

  rotateProducer(): void {
    this.roundTurn++;
  }

  distributeRewards(producer: Validator, tokenSystem: TokenSystem): void {
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

  getValidators(): Map<string, Validator> {
    return this.validators;
  }

  getAllValidatorsList(): Validator[] {
    const uniqueValidators = new Set<Validator>();
    for (const validator of this.validators.values()) {
      uniqueValidators.add(validator);
    }
    return Array.from(uniqueValidators);
  }

  getStakes(): Stake[] {
    return this.stakes;
  }

  getValidatorCount(): number {
    return this.validatorCount;
  }

  incrementBlocksProduced(validatorAddress: string): void {
    const validator = this.validators.get(validatorAddress);
    if (validator) {
      validator.blocksProduced++;
    }
  }
}

/**
 * Blockchain — the main chain manager. Handles block production, validation, and queries.
 */
export class Blockchain {
  private chain: Block[] = [];
  private mempool: Mempool = new Mempool();
  private consensus: DPoSConsensus = new DPoSConsensus();
  private tokenSystem: TokenSystem = new TokenSystem();

  constructor() {
    this.chain.push(createGenesisBlock());
  }

  /**
   * Allocates genesis tokens to an address (only before block 1).
   */
  addGenesisAllocation(address: string, amount: number): void {
    if (this.chain.length > 1) {
      throw new Error('Genesis allocations can only be made before block 1 is produced');
    }
    this.tokenSystem.addBalance(address, amount);
    this.tokenSystem.setTotalSupply(this.tokenSystem.getTotalSupply() + amount);
  }

  /**
   * Produces a new block. Must be the current producer's turn.
   */
  produceBlock(validatorPrivateKey: string, validatorPublicKey: string, validatorAddress: string): Block | null {
    const currentProducer = this.consensus.getCurrentProducer();
    if (!currentProducer) return null;
    if (currentProducer.address !== validatorAddress && currentProducer.publicKey !== validatorPublicKey) {
      return null; // Not this validator's turn
    }

    const latestBlock = this.getLatestBlock();
    const pendingTxs = this.mempool.getPendingTransactions(100); // Max 100 txs per block

    // Sign the block header
    const blockPayload = `${latestBlock.hash}:${pendingTxs.length}:${Date.now()}`;
    const sigResult = sign(blockPayload, validatorPrivateKey);

    const newBlock = createBlock(
      latestBlock.header.index + 1,
      latestBlock.hash,
      pendingTxs,
      validatorPublicKey,
      sigResult.signature,
      0, // difficulty (DPoS doesn't use PoW)
      0  // nonce
    );

    // Validate the new block
    if (!validateBlock(newBlock, latestBlock)) {
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
  submitTransaction(tx: Transaction): { success: boolean; error?: string } {
    return this.mempool.addTransaction(tx, this.tokenSystem.getBalancesMap());
  }

  /**
   * Finds a transaction in the chain and returns its block.
   */
  getTransactionReceipt(txId: string): { block: Block | null; tx: Transaction | null } {
    for (const block of this.chain) {
      for (const tx of block.transactions) {
        if (tx.id === txId) {
          return { block, tx };
        }
      }
    }
    return { block: null, tx: null };
  }

  getChain(): Block[] {
    return this.chain;
  }

  getLatestBlock(): Block {
    return this.chain[this.chain.length - 1];
  }

  getBlockByIndex(index: number): Block | undefined {
    return this.chain.find(b => b.header.index === index);
  }

  getBlockByHash(hash: string): Block | undefined {
    return this.chain.find(b => b.hash === hash);
  }

  getChainHeight(): number {
    return this.chain.length - 1;
  }

  isChainValid(): boolean {
    return validateChain(this.chain);
  }

  getConsensus(): DPoSConsensus {
    return this.consensus;
  }

  getTokenSystem(): TokenSystem {
    return this.tokenSystem;
  }

  getMempool(): Mempool {
    return this.mempool;
  }

  getState(): BlockchainState {
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
