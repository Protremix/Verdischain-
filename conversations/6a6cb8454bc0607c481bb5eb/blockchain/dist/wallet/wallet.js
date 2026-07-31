"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.WalletManager = void 0;
const crypto_1 = require("../crypto");
/**
 * Manages blockchain wallets, key generation, persistence, and transaction signing.
 */
class WalletManager {
    constructor() {
        this.wallets = new Map();
    }
    /**
     * Creates a new wallet with a generated key pair, derived address, and 0 initial balance.
     */
    createWallet() {
        const { privateKey, publicKey } = (0, crypto_1.generateKeyPair)();
        const address = (0, crypto_1.getAddressFromPublicKey)(publicKey);
        const wallet = {
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
    importWallet(privateKey) {
        const publicKey = (0, crypto_1.getPublicKeyFromPrivateKey)(privateKey);
        const address = (0, crypto_1.getAddressFromPublicKey)(publicKey);
        const existingWallet = this.wallets.get(address);
        if (existingWallet) {
            return existingWallet;
        }
        const wallet = {
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
    getWallet(address) {
        return this.wallets.get(address);
    }
    /**
     * Returns all managed wallets as an array.
     */
    getAllWallets() {
        return Array.from(this.wallets.values());
    }
    /**
     * Serializes all managed wallets into a JSON string for persistence.
     */
    saveWallets() {
        return JSON.stringify(this.getAllWallets(), null, 2);
    }
    /**
     * Loads wallets from a serialized JSON string into the wallet manager.
     */
    loadWallets(json) {
        if (!json || json.trim() === '') {
            return;
        }
        try {
            const walletArray = JSON.parse(json);
            if (Array.isArray(walletArray)) {
                for (const wallet of walletArray) {
                    if (wallet && wallet.address) {
                        this.wallets.set(wallet.address, wallet);
                    }
                }
            }
        }
        catch (error) {
            throw new Error(`Failed to load wallets from JSON: ${error.message}`);
        }
    }
    /**
     * Builds and signs a transaction from the specified wallet.
     */
    signTransaction(wallet, to, amount, fee, nonce, data) {
        return (0, crypto_1.signTransaction)(wallet.privateKey, to, amount, fee, nonce, data ?? null, wallet.publicKey);
    }
}
exports.WalletManager = WalletManager;
//# sourceMappingURL=wallet.js.map