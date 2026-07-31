import { Block, Transaction, Validator, BlockchainState } from '../types';
export declare class TokenSystem {
    private balances;
    private stakes;
    getBalance(address: string): number;
    setBalance(address: string, amount: number): void;
    addBalance(address: string, amount: number): void;
    getStaked(address: string): number;
    stake(address: string, amount: number): void;
    getBalancesMap(): Map<string, number>;
}
export declare class Consensus {
    private validators;
    private stakes;
    registerValidator(publicKey: string, address?: string): Validator;
    vote(voterAddress: string, validatorAddressOrKey: string, amount: number, tokenSystem?: TokenSystem): void;
    getValidators(): Map<string, Validator>;
    getAllValidatorsList(): Validator[];
}
export declare class Mempool {
    private pendingTransactions;
    addTransaction(tx: Transaction): boolean;
    getPendingTransactions(): Transaction[];
    clear(): void;
}
export declare class Blockchain {
    private chain;
    private consensus;
    private tokenSystem;
    private mempool;
    private maxSupply;
    private totalSupply;
    constructor();
    private createGenesisBlock;
    addGenesisAllocation(address: string, amount: number): void;
    getConsensus(): Consensus;
    getTokenSystem(): TokenSystem;
    getMempool(): Mempool;
    getChain(): Block[];
    getLatestBlock(): Block;
    getState(): BlockchainState;
}
