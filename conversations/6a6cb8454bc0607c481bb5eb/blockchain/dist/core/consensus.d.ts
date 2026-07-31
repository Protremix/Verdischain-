import { Block, Transaction, Validator, Stake, BlockchainState } from '../types';
import { Mempool } from './transaction';
/**
 * TokenSystem — manages native VRS token balances, staking, and transfers.
 */
export declare class TokenSystem {
    private balances;
    private stakes;
    private maxSupply;
    private totalSupply;
    private blockReward;
    getBalance(address: string): number;
    setBalance(address: string, amount: number): void;
    addBalance(address: string, amount: number): void;
    deductBalance(address: string, amount: number): boolean;
    transfer(from: string, to: string, amount: number): boolean;
    mint(address: string, amount: number): void;
    getStaked(address: string): number;
    stake(address: string, amount: number): boolean;
    unstake(address: string, amount: number): boolean;
    applyTransaction(tx: Transaction, blockProducer: string): boolean;
    getBalancesMap(): Map<string, number>;
    getTotalSupply(): number;
    getMaxSupply(): number;
    getBlockReward(): number;
    setTotalSupply(amount: number): void;
}
/**
 * DPoSConsensus — Tron-style delegated proof of stake with 27 super representatives.
 */
export declare class DPoSConsensus {
    private validators;
    private stakes;
    private validatorCount;
    private blockReward;
    private roundTurn;
    registerValidator(publicKey: string, address?: string): Validator;
    vote(voterAddress: string, validatorAddress: string, amount: number, tokenSystem?: TokenSystem): boolean;
    getTopValidators(): Validator[];
    getCurrentProducer(): Validator | null;
    rotateProducer(): void;
    distributeRewards(producer: Validator, tokenSystem: TokenSystem): void;
    getValidators(): Map<string, Validator>;
    getAllValidatorsList(): Validator[];
    getStakes(): Stake[];
    getValidatorCount(): number;
    incrementBlocksProduced(validatorAddress: string): void;
}
/**
 * Blockchain — the main chain manager. Handles block production, validation, and queries.
 */
export declare class Blockchain {
    private chain;
    private mempool;
    private consensus;
    private tokenSystem;
    constructor();
    /**
     * Allocates genesis tokens to an address (only before block 1).
     */
    addGenesisAllocation(address: string, amount: number): void;
    /**
     * Produces a new block. Must be the current producer's turn.
     */
    produceBlock(validatorPrivateKey: string, validatorPublicKey: string, validatorAddress: string): Block | null;
    /**
     * Submits a transaction to the mempool.
     */
    submitTransaction(tx: Transaction): {
        success: boolean;
        error?: string;
    };
    /**
     * Finds a transaction in the chain and returns its block.
     */
    getTransactionReceipt(txId: string): {
        block: Block | null;
        tx: Transaction | null;
    };
    getChain(): Block[];
    getLatestBlock(): Block;
    getBlockByIndex(index: number): Block | undefined;
    getBlockByHash(hash: string): Block | undefined;
    getChainHeight(): number;
    isChainValid(): boolean;
    getConsensus(): DPoSConsensus;
    getTokenSystem(): TokenSystem;
    getMempool(): Mempool;
    getState(): BlockchainState;
}
