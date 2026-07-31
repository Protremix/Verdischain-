import { Transaction } from './types';
export interface KeyPair {
    privateKey: string;
    publicKey: string;
}
/**
 * Computes single SHA-256 hash returned as hex string.
 */
export declare function sha256(data: string | Uint8Array): string;
/**
 * Computes double SHA-256 hash (SHA-256 of SHA-256) returned as hex string.
 */
export declare function doubleSha256(data: string | Uint8Array): string;
/**
 * Generates a new secp256k1 key pair.
 */
export declare function generateKeyPair(): KeyPair;
/**
 * Derives public key hex string from a private key hex string.
 */
export declare function getPublicKeyFromPrivateKey(privateKey: string): string;
/**
 * Derives a blockchain address from a public key using SHA-256 hash.
 */
export declare function getAddressFromPublicKey(publicKey: string): string;
/**
 * Signs data using secp256k1 private key.
 */
export declare function sign(data: string, privateKey: string): {
    signature: string;
    recovery: number;
};
/**
 * Verifies a signature using public key.
 */
export declare function verify(data: string, signature: string, publicKey: string): boolean;
/**
 * Signs a transaction with a private key and constructs a Transaction object.
 */
export declare function signTransaction(privateKey: string, to: string, amount: number, fee: number, nonce: number, data?: string | null, publicKeyOverride?: string): Transaction;
