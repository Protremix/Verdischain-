import { Transaction } from '../types';
import { sha256, sign } from '../crypto';

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

  public from(sender: string): this {
    this.sender = sender;
    return this;
  }

  public setFrom(sender: string): this {
    this.sender = sender;
    return this;
  }

  public to(recipient: string): this {
    this.recipient = recipient;
    return this;
  }

  public setTo(recipient: string): this {
    this.recipient = recipient;
    return this;
  }

  public amount(amount: number): this {
    this.txAmount = amount;
    return this;
  }

  public setAmount(amount: number): this {
    this.txAmount = amount;
    return this;
  }

  public fee(fee: number): this {
    this.txFee = fee;
    return this;
  }

  public setFee(fee: number): this {
    this.txFee = fee;
    return this;
  }

  public data(data: string | null): this {
    this.txData = data;
    return this;
  }

  public setData(data: string | null): this {
    this.txData = data;
    return this;
  }

  public nonce(nonce: number): this {
    this.txNonce = nonce;
    return this;
  }

  public setNonce(nonce: number): this {
    this.txNonce = nonce;
    return this;
  }

  public sign(privateKey: string): this {
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
