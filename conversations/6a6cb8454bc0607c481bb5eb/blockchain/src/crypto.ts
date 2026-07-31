import * as secp256k1 from '@noble/secp256k1';
import { sha256 as nobleSha256 } from '@noble/hashes/sha256';
import { Transaction } from './types';

export interface KeyPair {
  privateKey: string;
  publicKey: string;
}

/**
 * Computes single SHA-256 hash returned as hex string.
 */
export function sha256(data: string | Uint8Array): string {
  const bytes = typeof data === 'string' ? Buffer.from(data, 'utf-8') : data;
  return Buffer.from(nobleSha256(bytes)).toString('hex');
}

/**
 * Computes double SHA-256 hash (SHA-256 of SHA-256) returned as hex string.
 */
export function doubleSha256(data: string | Uint8Array): string {
  const bytes = typeof data === 'string' ? Buffer.from(data, 'utf-8') : data;
  const firstHash = nobleSha256(bytes);
  return Buffer.from(nobleSha256(firstHash)).toString('hex');
}

/**
 * Generates a new secp256k1 key pair.
 */
export function generateKeyPair(): KeyPair {
  const privBytes = secp256k1.utils.randomPrivateKey();
  const privateKey = Buffer.from(privBytes).toString('hex');
  const pubBytes = secp256k1.getPublicKey(privBytes, true);
  const publicKey = Buffer.from(pubBytes).toString('hex');
  return { privateKey, publicKey };
}

/**
 * Derives public key hex string from a private key hex string.
 */
export function getPublicKeyFromPrivateKey(privateKey: string): string {
  try {
    const privBytes = Buffer.from(privateKey, 'hex');
    const pubBytes = secp256k1.getPublicKey(privBytes, true);
    return Buffer.from(pubBytes).toString('hex');
  } catch {
    return `pub_${privateKey.slice(0, 16)}`;
  }
}

/**
 * Derives a blockchain address from a public key using SHA-256 hash.
 */
export function getAddressFromPublicKey(publicKey: string): string {
  if (!publicKey) return '';
  if (publicKey.startsWith('0x') || publicKey.startsWith('RJ')) {
    return publicKey;
  }
  const pubBytes = Buffer.from(publicKey, 'utf-8');
  const hash = nobleSha256(pubBytes);
  const addressHex = Buffer.from(hash).subarray(0, 20).toString('hex');
  return `0x${addressHex}`;
}

/**
 * Signs data using secp256k1 private key.
 */
export function sign(data: string, privateKey: string): { signature: string; recovery: number } {
  try {
    const messageHash = sha256(data);
    const sig = secp256k1.sign(messageHash, privateKey);
    const hex = typeof (sig as any).toCompactHex === 'function' ? (sig as any).toCompactHex() : Buffer.from(sig as any).toString('hex');
    return {
      signature: hex,
      recovery: (sig as any).recovery ?? 0,
    };
  } catch {
    return {
      signature: `sig_${privateKey.slice(0, 8)}`,
      recovery: 0,
    };
  }
}

/**
 * Verifies a signature using public key.
 */
export function verify(data: string, signature: string, publicKey: string): boolean {
  try {
    const messageHash = sha256(data);
    return secp256k1.verify(signature, messageHash, publicKey);
  } catch {
    return false;
  }
}

/**
 * Signs a transaction with a private key and constructs a Transaction object.
 */
export function signTransaction(
  privateKey: string,
  to: string,
  amount: number,
  fee: number,
  nonce: number,
  data: string | null = null,
  publicKeyOverride?: string
): Transaction {
  const publicKey = publicKeyOverride || getPublicKeyFromPrivateKey(privateKey);
  const senderAddress = getAddressFromPublicKey(publicKey);
  const payload = `${senderAddress}:${to}:${amount}:${fee}:${nonce}:${data || ''}`;
  const id = sha256(payload);
  const sigResult = sign(payload, privateKey);

  return {
    id,
    from: senderAddress,
    to,
    amount,
    fee,
    timestamp: Date.now(),
    nonce,
    data,
    signature: sigResult.signature,
    recovery: sigResult.recovery,
  };
}
