import { Wallet, Transaction } from '../types';
/**
 * Manages blockchain wallets, key generation, persistence, and transaction signing.
 */
export declare class WalletManager {
    private wallets;
    constructor();
    /**
     * Creates a new wallet with a generated key pair, derived address, and 0 initial balance.
     */
    createWallet(): Wallet;
    /**
     * Imports an existing wallet using its private key, deriving public key and address.
     */
    importWallet(privateKey: string): Wallet;
    /**
     * Retrieves a wallet by its address.
     */
    getWallet(address: string): Wallet | undefined;
    /**
     * Returns all managed wallets as an array.
     */
    getAllWallets(): Wallet[];
    /**
     * Serializes all managed wallets into a JSON string for persistence.
     */
    saveWallets(): string;
    /**
     * Loads wallets from a serialized JSON string into the wallet manager.
     */
    loadWallets(json: string): void;
    /**
     * Builds and signs a transaction from the specified wallet.
     */
    signTransaction(wallet: Wallet, to: string, amount: number, fee: number, nonce: number, data?: string): Transaction;
}
