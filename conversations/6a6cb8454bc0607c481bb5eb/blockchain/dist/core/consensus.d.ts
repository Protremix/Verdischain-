import { Block, Transaction, Validator, Stake } from '../types';
export interface ChainInfo {
    height: number;
    totalSupply: number;
    maxSupply: number;
    validatorCount: number;
    blockReward: number;
}
export interface TransactionReceipt {
    transaction: Transaction;
    blockIndex: number;
    blockHash: string;
    confirmations: number;
    status: 'confirmed' | 'pending';
}
export declare class TokenSystem {
    private totalSupply;
    private maxSupply;
    getTotalSupply(): number;
    getMaxSupply(): number;
}
export declare class DPoSConsensus {
    private activeValidators;
    getValidators(): Validator[];
}
export declare class Blockchain {
    private chain;
    private mempool;
    private validators;
    private stakes;
    private balances;
    private totalSupply;
    private maxSupply;
    private blockReward;
    constructor();
    private createGenesisBlock;
    getBalance(address: string): number;
    getStakedAmount(address: string): number;
    submitTransaction(tx: Transaction): string;
    getTransactionReceipt(txId: string): TransactionReceipt | null;
    getMempool(): Transaction[];
    getMempoolSize(): number;
    getChainInfo(): ChainInfo;
    getChainHeight(): number;
    getBlocks(limit?: number, offset?: number): Block[];
    getBlockByIndex(index: number): Block | null;
    getBlockByHash(hash: string): Block | null;
    getValidators(): Validator[];
    getTopValidators(limit?: number): Validator[];
    registerValidator(publicKey: string): Validator;
    voteForValidator(voterAddress: string, validatorAddress: string, amount: number, privateKey: string): Stake;
    stake(address: string, amount: number): boolean;
    unstake(address: string, amount: number): boolean;
    produceBlock(publicKey: string, privateKey: string): Block;
    allocateGenesis(address: string, amount: number): boolean;
}
