import { Transaction } from '../types';
import { sha256, sign, verify, getAddressFromPublicKey } from '../crypto';

/**
 * TransactionBuilder - fluent builder for creating and signing transactions.
 */
export class TransactionBuilder {
  private sender: string = '';
  private recipient: string = '';
  private txAmount: number = 0;
  private txFee: number = 0;
  private txData: string | null = null;
  private txNonce: number = Date.now();
  private txSignature: string = '';
  private txRecovery: number = 0;

  constructor() {}

  public setFrom(sender: string): this {
    this.sender = sender;
    return this;
  }

  public setTo(recipient: string): this {
    this.recipient = recipient;
    return this;
  }

  public setAmount(amount: number): this {
    this.txAmount = amount;
    return this;
  }

  public setFee(fee: number): this {
    this.txFee = fee;
    return this;
  }

  public setData(data: string | null): this {
    this.txData = data;
    return this;
  }

  public setNonce(nonce: number): this {
    this.txNonce = nonce;
    return this;
  }

  public signWith(privateKey: string): this {
    const payload = `${this.sender}:${this.recipient}:${this.txAmount}:${this.txFee}:${this.txNonce}:${this.txData || ''}`;
    const sigResult = sign(payload, privateKey);
    this.txSignature = sigResult.signature;
    this.txRecovery = sigResult.recovery;
    return this;
  }

  public build(): Transaction {
    if (!this.sender) throw new Error('Transaction sender is required');
    if (!this.recipient) throw new Error('Transaction recipient is required');
    if (this.txAmount <= 0) throw new Error('Transaction amount must be greater than zero');
    if (this.txFee < 0) throw new Error('Transaction fee cannot be negative');

    const payload = `${this.sender}:${this.recipient}:${this.txAmount}:${this.txFee}:${this.txNonce}:${this.txData || ''}`;
    const id = sha256(payload);

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

/**
 * Validates a transaction against current balances.
 */
export function validateTransaction(tx: Transaction, balances: Map<string, number>): { valid: boolean; error?: string } {
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
  const recomputedId = sha256(payload);
  if (recomputedId !== tx.id) {
    return { valid: false, error: 'Transaction hash mismatch — data may have been tampered with' };
  }

  // Verify signature (skip for genesis/unsigned transactions)
  if (tx.signature && tx.signature !== 'unsigned') {
    const valid = verify(payload, tx.signature, tx.from);
    if (!valid) {
      return { valid: false, error: 'Invalid transaction signature' };
    }
  }

  return { valid: true };
}

/**
 * Mempool - holds pending transactions before they're included in a block.
 */
export class Mempool {
  private transactions: Map<string, Transaction> = new Map();

  /**
   * Validates and adds a transaction to the mempool.
   */
  addTransaction(tx: Transaction, balances: Map<string, number>): { success: boolean; error?: string } {
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
  getTransactions(): Transaction[] {
    return Array.from(this.transactions.values());
  }

  /**
   * Get a specific transaction by id.
   */
  getTransaction(id: string): Transaction | undefined {
    return this.transactions.get(id);
  }

  /**
   * Remove a transaction after it's been included in a block.
   */
  removeTransaction(id: string): void {
    this.transactions.delete(id);
  }

  /**
   * Get up to `limit` transactions sorted by fee (highest first) for block inclusion.
   */
  getPendingTransactions(limit: number): Transaction[] {
    const all = Array.from(this.transactions.values());
    all.sort((a, b) => b.fee - a.fee);
    return all.slice(0, limit);
  }

  /**
   * Returns the number of pending transactions.
   */
  size(): number {
    return this.transactions.size;
  }

  /**
   * Clear all transactions from the mempool.
   */
  clear(): void {
    this.transactions.clear();
  }
}
