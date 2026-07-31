"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Mempool = exports.TransactionBuilder = void 0;
exports.validateTransaction = validateTransaction;
const crypto_1 = require("../crypto");
/**
 * Builder class for creating, hashing, and signing RojsChain transactions.
 */
class TransactionBuilder {
    constructor(privateKey) {
        this.from = '';
        this.to = '';
        this.amount = 0;
        this.fee = 0;
        this.data = null;
        this.nonce = 0;
        if (!privateKey) {
            throw new Error('Private key is required to create a TransactionBuilder');
        }
        this.privateKey = privateKey;
    }
    /**
     * Sets the sender's public key.
     */
    setFrom(publicKey) {
        this.from = publicKey;
        return this;
    }
    /**
     * Sets the recipient address or public key.
     */
    setTo(address) {
        this.to = address;
        return this;
    }
    /**
     * Sets the amount to transfer.
     */
    setAmount(amount) {
        this.amount = amount;
        return this;
    }
    /**
     * Sets the transaction fee for block inclusion.
     */
    setFee(fee) {
        this.fee = fee;
        return this;
    }
    /**
     * Sets optional smart contract data or payload.
     */
    setData(data) {
        this.data = data;
        return this;
    }
    /**
     * Sets the transaction nonce to prevent replay attacks.
     */
    setNonce(nonce) {
        this.nonce = nonce;
        return this;
    }
    /**
     * Sets an explicit timestamp (defaults to current time if unset).
     */
    setTimestamp(timestamp) {
        this.timestamp = timestamp;
        return this;
    }
    /**
     * Constructs the transaction object, calculates its unique ID/hash,
     * signs it using the private key, and returns the complete signed Transaction.
     */
    build() {
        if (!this.from) {
            throw new Error('Sender public key (from) is required');
        }
        if (!this.to) {
            throw new Error('Recipient address (to) is required');
        }
        if (this.amount <= 0) {
            throw new Error('Amount must be greater than 0');
        }
        if (this.fee < 0) {
            throw new Error('Fee cannot be negative');
        }
        if (this.nonce < 0) {
            throw new Error('Nonce cannot be negative');
        }
        const txTimestamp = this.timestamp ?? Date.now();
        const unsignedData = {
            from: this.from,
            to: this.to,
            amount: this.amount,
            fee: this.fee,
            timestamp: txTimestamp,
            nonce: this.nonce,
            data: this.data ?? null,
        };
        // Calculate transaction hash / ID
        const id = (0, crypto_1.hashTransaction)(unsignedData);
        // Sign transaction hash with private key
        const { signature, recovery } = (0, crypto_1.signTransaction)(id, this.privateKey);
        const transaction = {
            id,
            from: this.from,
            to: this.to,
            amount: this.amount,
            fee: this.fee,
            timestamp: txTimestamp,
            nonce: this.nonce,
            data: this.data ?? null,
            signature,
            recovery,
        };
        return transaction;
    }
}
exports.TransactionBuilder = TransactionBuilder;
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
function validateTransaction(tx, balances) {
    if (!tx || typeof tx !== 'object') {
        return { valid: false, error: 'Transaction must be a valid object' };
    }
    // 1. Non-empty from and to
    if (!tx.from || typeof tx.from !== 'string' || tx.from.trim().length === 0) {
        return { valid: false, error: 'Sender public key (from) is required and cannot be empty' };
    }
    if (!tx.to || typeof tx.to !== 'string' || tx.to.trim().length === 0) {
        return { valid: false, error: 'Recipient address (to) is required and cannot be empty' };
    }
    // 2. Amount > 0
    if (typeof tx.amount !== 'number' || !Number.isFinite(tx.amount) || tx.amount <= 0) {
        return { valid: false, error: 'Transaction amount must be a finite number greater than 0' };
    }
    // 3. Fee >= 0
    if (typeof tx.fee !== 'number' || !Number.isFinite(tx.fee) || tx.fee < 0) {
        return { valid: false, error: 'Transaction fee must be a finite non-negative number' };
    }
    // Check nonce and timestamp validity
    if (typeof tx.nonce !== 'number' || !Number.isFinite(tx.nonce) || tx.nonce < 0) {
        return { valid: false, error: 'Transaction nonce must be a non-negative number' };
    }
    // 4. Sufficient balance check
    const senderBalance = balances.get(tx.from) ?? balances.get((0, crypto_1.getAddressFromPublicKey)(tx.from)) ?? 0;
    const totalRequired = tx.amount + tx.fee;
    if (senderBalance < totalRequired) {
        return {
            valid: false,
            error: `Insufficient sender balance: available ${senderBalance}, required ${totalRequired} (amount ${tx.amount} + fee ${tx.fee})`,
        };
    }
    // 5. Tx hash matches recomputed hash
    const computedHash = (0, crypto_1.hashTransaction)(tx);
    if (tx.id !== computedHash) {
        return { valid: false, error: `Transaction ID mismatch: expected ${computedHash}, got ${tx.id}` };
    }
    // 6. Signature validation
    const isValidSig = (0, crypto_1.verifySignature)(tx.id, tx.signature, tx.from, tx.recovery);
    if (!isValidSig) {
        return { valid: false, error: 'Invalid transaction signature' };
    }
    return { valid: true };
}
/**
 * Mempool class for managing pending transactions before block inclusion.
 */
class Mempool {
    constructor() {
        this.transactions = new Map();
    }
    /**
     * Validates and adds a transaction to the mempool.
     */
    addTransaction(tx, balances) {
        // Check if transaction is already in mempool
        if (this.transactions.has(tx.id)) {
            return { success: false, error: `Transaction ${tx.id} already exists in mempool` };
        }
        // Validate transaction against system rules and account balances
        const validation = validateTransaction(tx, balances);
        if (!validation.valid) {
            return { success: false, error: validation.error ?? 'Transaction validation failed' };
        }
        // Cumulative balance check against other pending transactions by the same sender in mempool
        let pendingSpent = 0;
        for (const pendingTx of this.transactions.values()) {
            if (pendingTx.from === tx.from) {
                pendingSpent += pendingTx.amount + pendingTx.fee;
            }
        }
        const senderBalance = balances.get(tx.from) ?? balances.get((0, crypto_1.getAddressFromPublicKey)(tx.from)) ?? 0;
        const totalRequiredWithPending = pendingSpent + tx.amount + tx.fee;
        if (senderBalance < totalRequiredWithPending) {
            return {
                success: false,
                error: `Insufficient sender balance including pending mempool transactions: available ${senderBalance}, pending total required ${totalRequiredWithPending}`,
            };
        }
        this.transactions.set(tx.id, tx);
        return { success: true };
    }
    /**
     * Returns all pending transactions in the mempool.
     */
    getTransactions() {
        return Array.from(this.transactions.values());
    }
    /**
     * Returns a specific transaction by ID if present.
     */
    getTransaction(id) {
        return this.transactions.get(id);
    }
    /**
     * Removes a transaction from the mempool (e.g. after inclusion in a block).
     */
    removeTransaction(id) {
        this.transactions.delete(id);
    }
    /**
     * Gets up to `limit` pending transactions sorted by fee descending (highest fee first) for block inclusion.
     */
    getPendingTransactions(limit) {
        if (limit <= 0) {
            return [];
        }
        const allTransactions = Array.from(this.transactions.values());
        // Sort by fee descending; if fees are equal, sort by timestamp ascending (FCFS)
        allTransactions.sort((a, b) => {
            if (b.fee !== a.fee) {
                return b.fee - a.fee;
            }
            return a.timestamp - b.timestamp;
        });
        return allTransactions.slice(0, limit);
    }
    /**
     * Returns the number of pending transactions in the mempool.
     */
    size() {
        return this.transactions.size;
    }
    /**
     * Clears all pending transactions from the mempool.
     */
    clear() {
        this.transactions.clear();
    }
}
exports.Mempool = Mempool;
//# sourceMappingURL=transaction.js.map