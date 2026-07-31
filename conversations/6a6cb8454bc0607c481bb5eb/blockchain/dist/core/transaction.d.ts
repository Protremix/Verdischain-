import { Transaction } from '../types';
/**
 * TransactionBuilder - fluent builder for creating and signing transactions.
 */
export declare class TransactionBuilder {
    private sender;
    private recipient;
    private txAmount;
    private txFee;
    private txData;
    private txNonce;
    private txSignature;
    private senderPublicKey;
    private txRecovery;
    constructor();
    setFrom(sender: string): this;
    setPublicKey(pubKey: string): this;
    setTo(recipient: string): this;
    setAmount(amount: number): this;
    setFee(fee: number): this;
    setData(data: string | null): this;
    setNonce(nonce: number): this;
    signWith(privateKey: string): this;
    build(): Transaction;
}
/**
 * Validates a transaction against current balances.
 */
export declare function validateTransaction(tx: Transaction, balances: Map<string, number>): {
    valid: boolean;
    error?: string;
};
/**
 * Mempool - holds pending transactions before they're included in a block.
 */
export declare class Mempool {
    private transactions;
    /**
     * Validates and adds a transaction to the mempool.
     */
    addTransaction(tx: Transaction, balances: Map<string, number>): {
        success: boolean;
        error?: string;
    };
    /**
     * Returns all pending transactions.
     */
    getTransactions(): Transaction[];
    /**
     * Get a specific transaction by id.
     */
    getTransaction(id: string): Transaction | undefined;
    /**
     * Remove a transaction after it's been included in a block.
     */
    removeTransaction(id: string): void;
    /**
     * Get up to `limit` transactions sorted by fee (highest first) for block inclusion.
     */
    getPendingTransactions(limit: number): Transaction[];
    /**
     * Returns the number of pending transactions.
     */
    size(): number;
    /**
     * Clear all transactions from the mempool.
     */
    clear(): void;
}
