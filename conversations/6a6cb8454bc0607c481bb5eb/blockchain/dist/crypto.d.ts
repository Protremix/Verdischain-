import { Transaction } from './types';
/**
 * Computes SHA-256 hash of given data and returns hex string.
 */
export declare function sha256(data: string | Uint8Array | Buffer): string;
/**
 * Calculates deterministic hash for a transaction object.
 * Hash excludes 'id', 'signature', and 'recovery'.
 */
export declare function hashTransaction(tx: Omit<Transaction, 'id' | 'signature' | 'recovery'> | Transaction): string;
/**
 * Signs a transaction hash with a private key using secp256k1.
 */
export declare function signTransaction(hash: string, privateKey: string): {
    signature: string;
    recovery: number;
};
/**
 * Verifies a signature against a transaction hash and public key using secp256k1.
 */
export declare function verifySignature(hash: string, signature: string, publicKey: string, recovery?: number): boolean;
/**
 * Derives an address from a public key string.
 */
export declare function getAddressFromPublicKey(publicKey: string): string;
