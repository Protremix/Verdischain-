"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Mempool = exports.TransactionBuilder = void 0;
exports.validateTransaction = validateTransaction;
const crypto_1 = require("../crypto");
/**
 * TransactionBuilder - fluent builder for creating and signing transactions.
 */
class TransactionBuilder {
    constructor() {
        this.sender = '';
        this.recipient = '';
        this.txAmount = 0;
        this.txFee = 0;
        this.txData = null;
        this.txNonce = Date.now();
        this.txSignature = '';
        this.txRecovery = 0;
    }
    setFrom(sender) {
        this.sender = sender;
        return this;
    }
    setTo(recipient) {
        this.recipient = recipient;
        return this;
    }
    setAmount(amount) {
        this.txAmount = amount;
        return this;
    }
    setFee(fee) {
        this.txFee = fee;
        return this;
    }
    setData(data) {
        this.txData = data;
        return this;
    }
    setNonce(nonce) {
        this.txNonce = nonce;
        return this;
    }
    signWith(privateKey) {
        const payload = `${this.sender}:${this.recipient}:${this.txAmount}:${this.txFee}:${this.txNonce}:${this.txData || ''}`;
        const sigResult = (0, crypto_1.sign)(payload, privateKey);
        this.txSignature = sigResult.signature;
        this.txRecovery = sigResult.recovery;
        return this;
    }
    build() {
        if (!this.sender)
            throw new Error('Transaction sender is required');
        if (!this.recipient)
            throw new Error('Transaction recipient is required');
        if (this.txAmount <= 0)
            throw new Error('Transaction amount must be greater than zero');
        if (this.txFee < 0)
            throw new Error('Transaction fee cannot be negative');
        const payload = `${this.sender}:${this.recipient}:${this.txAmount}:${this.txFee}:${this.txNonce}:${this.txData || ''}`;
        const id = (0, crypto_1.sha256)(payload);
        return {
            id,
            from: this.sender,
            to: this.recipient,
            amount: this.txAmount,
            fee: this.txFee,
            timestamp: Date.now(),
            nonce: this.txNonce,
            data: this.txData,
            signature: this.txSignature || 'unsigned',
            recovery: this.txRecovery,
        };
    }
}
exports.TransactionBuilder = TransactionBuilder;
/**
 * Validates a transaction against current balances.
 */
function validateTransaction(tx, balances) {
    if (!tx.from || !tx.to) {
        return { valid: false, error: 'Sender and recipient are required' };
    }
    if (tx.amount <= 0) {
        return { valid: false, error: 'Amount must be greater than zero' };
    }
    if (tx.fee < 0) {
        return { valid: false, error: 'Fee cannot be negative' };
    }
    // Check sender balance (amount + fee)
    const senderBalance = balances.get(tx.from) || 0;
    if (senderBalance < tx.amount + tx.fee) {
        return { valid: false, error: `Insufficient balance: has ${senderBalance}, needs ${tx.amount + tx.fee}` };
    }
    // Verify transaction hash matches recomputed hash
    const payload = `${tx.from}:${tx.to}:${tx.amount}:${tx.fee}:${tx.nonce}:${tx.data || ''}`;
    const recomputedId = (0, crypto_1.sha256)(payload);
    if (recomputedId !== tx.id) {
        return { valid: false, error: 'Transaction hash mismatch — data may have been tampered with' };
    }
    // Verify signature (skip for genesis/unsigned transactions)
    if (tx.signature && tx.signature !== 'unsigned') {
        const valid = (0, crypto_1.verify)(payload, tx.signature, tx.from);
        if (!valid) {
            return { valid: false, error: 'Invalid transaction signature' };
        }
    }
    return { valid: true };
}
/**
 * Mempool - holds pending transactions before they're included in a block.
 */
class Mempool {
    constructor() {
        this.transactions = new Map();
    }
    /**
     * Validates and adds a transaction to the mempool.
     */
    addTransaction(tx, balances) {
        // Check for duplicate
        if (this.transactions.has(tx.id)) {
            return { success: false, error: 'Transaction already in mempool' };
        }
        const validation = validateTransaction(tx, balances);
        if (!validation.valid) {
            return { success: false, error: validation.error };
        }
        this.transactions.set(tx.id, tx);
        return { success: true };
    }
    /**
     * Returns all pending transactions.
     */
    getTransactions() {
        return Array.from(this.transactions.values());
    }
    /**
     * Get a specific transaction by id.
     */
    getTransaction(id) {
        return this.transactions.get(id);
    }
    /**
     * Remove a transaction after it's been included in a block.
     */
    removeTransaction(id) {
        this.transactions.delete(id);
    }
    /**
     * Get up to `limit` transactions sorted by fee (highest first) for block inclusion.
     */
    getPendingTransactions(limit) {
        const all = Array.from(this.transactions.values());
        all.sort((a, b) => b.fee - a.fee);
        return all.slice(0, limit);
    }
    /**
     * Returns the number of pending transactions.
     */
    size() {
        return this.transactions.size;
    }
    /**
     * Clear all transactions from the mempool.
     */
    clear() {
        this.transactions.clear();
    }
}
exports.Mempool = Mempool;
//# sourceMappingURL=transaction.js.map