import { Transaction } from '../types';
/**
 * Builder class for creating, hashing, and signing RojsChain transactions.
 */
export declare class TransactionBuilder {
    private privateKey;
    private from;
    private to;
    private amount;
    private fee;
    private data;
    private nonce;
    private timestamp?;
    constructor(privateKey: string);
    /**
     * Sets the sender's public key.
     */
    setFrom(publicKey: string): this;
    /**
     * Sets the recipient address or public key.
     */
    setTo(address: string): this;
    /**
     * Sets the amount to transfer.
     */
    setAmount(amount: number): this;
    /**
     * Sets the transaction fee for block inclusion.
     */
    setFee(fee: number): this;
    /**
     * Sets optional smart contract data or payload.
     */
    setData(data: string | null): this;
    /**
     * Sets the transaction nonce to prevent replay attacks.
     */
    setNonce(nonce: number): this;
    /**
     * Sets an explicit timestamp (defaults to current time if unset).
     */
    setTimestamp(timestamp: number): this;
    /**
     * Constructs the transaction object, calculates its unique ID/hash,
     * signs it using the private key, and returns the complete signed Transaction.
     */
    build(): Transaction;
}
/**
 * Validates a transaction against system rules and account balances.
 *
 * Checks:
 * 1. Sender (from) and recipient (to) are non-empty string addresses.
 * 2. Amount is strictly positive (> 0).
 * 3. Fee is non-negative (>= 0).
 * 4. Sender has sufficient balance (amount + fee).
 * 5. Recomputed hash matches transaction ID (tamper resistance).
 * 6. Cryptographic signature is valid for transaction hash and sender public key.
 */
export declare function validateTransaction(tx: Transaction, balances: Map<string, number>): {
    valid: boolean;
    error?: string;
};
/**
 * Mempool class for managing pending transactions before block inclusion.
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
     * Returns all pending transactions in the mempool.
     */
    getTransactions(): Transaction[];
    /**
     * Returns a specific transaction by ID if present.
     */
    getTransaction(id: string): Transaction | undefined;
    /**
     * Removes a transaction from the mempool (e.g. after inclusion in a block).
     */
    removeTransaction(id: string): void;
    /**
     * Gets up to `limit` pending transactions sorted by fee descending (highest fee first) for block inclusion.
     */
    getPendingTransactions(limit: number): Transaction[];
    /**
     * Returns the number of pending transactions in the mempool.
     */
    size(): number;
    /**
     * Clears all pending transactions from the mempool.
     */
    clear(): void;
}
