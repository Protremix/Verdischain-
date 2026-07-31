import crypto from 'crypto';
import { Block, Transaction, Validator, Stake, BlockchainState } from '../types';

export class TokenSystem {
  private balances: Map<string, number> = new Map();
  private stakes: Map<string, number> = new Map();

  public getBalance(address: string): number {
    return this.balances.get(address) || 0;
  }

  public setBalance(address: string, amount: number): void {
    this.balances.set(address, amount);
  }

  public addBalance(address: string, amount: number): void {
    const current = this.getBalance(address);
    this.balances.set(address, current + amount);
  }

  public getStaked(address: string): number {
    return this.stakes.get(address) || 0;
  }

  public stake(address: string, amount: number): void {
    const currentBal = this.getBalance(address);
    if (currentBal >= amount) {
      this.balances.set(address, currentBal - amount);
    }
    const currentStaked = this.getStaked(address);
    this.stakes.set(address, currentStaked + amount);
  }

  public getBalancesMap(): Map<string, number> {
    return this.balances;
  }
}

export class Consensus {
  private validators: Map<string, Validator> = new Map();
  private stakes: Stake[] = [];

  public registerValidator(publicKey: string, address?: string): Validator {
    const valAddress = address || publicKey;
    const existing = this.validators.get(publicKey) || this.validators.get(valAddress);
    if (existing) {
      return existing;
    }

    const validator: Validator = {
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

  public vote(
    voterAddress: string,
    validatorAddressOrKey: string,
    amount: number,
    tokenSystem?: TokenSystem
  ): void {
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

  public getValidators(): Map<string, Validator> {
    return this.validators;
  }

  public getAllValidatorsList(): Validator[] {
    const uniqueValidators = new Set<Validator>();
    for (const validator of this.validators.values()) {
      uniqueValidators.add(validator);
    }
    return Array.from(uniqueValidators);
  }
}

export class Mempool {
  private pendingTransactions: Transaction[] = [];

  public addTransaction(tx: Transaction): boolean {
    this.pendingTransactions.push(tx);
    return true;
  }

  public getPendingTransactions(): Transaction[] {
    return [...this.pendingTransactions];
  }

  public clear(): void {
    this.pendingTransactions = [];
  }
}

export class Blockchain {
  private chain: Block[] = [];
  private consensus: Consensus = new Consensus();
  private tokenSystem: TokenSystem = new TokenSystem();
  private mempool: Mempool = new Mempool();
  private maxSupply: number = 100_000_000_000; // 100 Billion
  private totalSupply: number = 0;

  constructor() {
    this.createGenesisBlock();
  }

  private createGenesisBlock(): void {
    const genesisBlock: Block = {
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
      hash: crypto.createHash('sha256').update('GENESIS_BLOCK').digest('hex'),
    };
    this.chain.push(genesisBlock);
  }

  public addGenesisAllocation(address: string, amount: number): void {
    if (this.totalSupply + amount > this.maxSupply) {
      throw new Error('Genesis allocation exceeds maximum supply limit');
    }
    this.tokenSystem.addBalance(address, amount);
    this.totalSupply += amount;
  }

  public getConsensus(): Consensus {
    return this.consensus;
  }

  public getTokenSystem(): TokenSystem {
    return this.tokenSystem;
  }

  public getMempool(): Mempool {
    return this.mempool;
  }

  public getChain(): Block[] {
    return this.chain;
  }

  public getLatestBlock(): Block {
    return this.chain[this.chain.length - 1];
  }

  public getState(): BlockchainState {
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
