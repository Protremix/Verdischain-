import { generateKeyPair, getAddressFromPublicKey, signTransaction as cryptoSignTransaction, getPublicKeyFromPrivateKey } from '../crypto';
import { Wallet, Transaction } from '../types';

/**
 * Manages blockchain wallets, key generation, persistence, and transaction signing.
 */
export class WalletManager {
  private wallets: Map<string, Wallet>;

  constructor() {
    this.wallets = new Map<string, Wallet>();
  }

  /**
   * Creates a new wallet with a generated key pair, derived address, and 0 initial balance.
   */
  public createWallet(): Wallet {
    const { privateKey, publicKey } = generateKeyPair();
    const address = getAddressFromPublicKey(publicKey);

    const wallet: Wallet = {
      privateKey,
      publicKey,
      address,
      balance: 0,
      staked: 0,
    };

    this.wallets.set(address, wallet);
    return wallet;
  }

  /**
   * Imports an existing wallet using its private key, deriving public key and address.
   */
  public importWallet(privateKey: string): Wallet {
    const publicKey = getPublicKeyFromPrivateKey(privateKey);
    const address = getAddressFromPublicKey(publicKey);

    const existingWallet = this.wallets.get(address);
    if (existingWallet) {
      return existingWallet;
    }

    const wallet: Wallet = {
      privateKey,
      publicKey,
      address,
      balance: 0,
      staked: 0,
    };

    this.wallets.set(address, wallet);
    return wallet;
  }

  /**
   * Retrieves a wallet by its address.
   */
  public getWallet(address: string): Wallet | undefined {
    return this.wallets.get(address);
  }

  /**
   * Returns all managed wallets as an array.
   */
  public getAllWallets(): Wallet[] {
    return Array.from(this.wallets.values());
  }

  /**
   * Serializes all managed wallets into a JSON string for persistence.
   */
  public saveWallets(): string {
    return JSON.stringify(this.getAllWallets(), null, 2);
  }

  /**
   * Loads wallets from a serialized JSON string into the wallet manager.
   */
  public loadWallets(json: string): void {
    if (!json || json.trim() === '') {
      return;
    }

    try {
      const walletArray: Wallet[] = JSON.parse(json);
      if (Array.isArray(walletArray)) {
        for (const wallet of walletArray) {
          if (wallet && wallet.address) {
            this.wallets.set(wallet.address, wallet);
          }
        }
      }
    } catch (error) {
      throw new Error(`Failed to load wallets from JSON: ${(error as Error).message}`);
    }
  }

  /**
   * Exports all managed wallets as an array.
   */
  public exportState(): Wallet[] {
    return this.getAllWallets();
  }

  /**
   * Restores wallets into the manager.
   */
  public importState(wallets: Wallet[]): void {
    if (Array.isArray(wallets)) {
      for (const wallet of wallets) {
        if (wallet && wallet.address) {
          this.wallets.set(wallet.address, wallet);
        }
      }
    }
  }

  /**
   * Builds and signs a transaction from the specified wallet.
   */
  public signTransaction(
    wallet: Wallet,
    to: string,
    amount: number,
    fee: number,
    nonce: number,
    data?: string
  ): Transaction {
    return cryptoSignTransaction(
      wallet.privateKey,
      to,
      amount,
      fee,
      nonce,
      data ?? null,
      wallet.publicKey
    );
  }
}
