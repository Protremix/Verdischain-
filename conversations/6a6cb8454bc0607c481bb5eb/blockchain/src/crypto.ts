import crypto from 'crypto';
import * as secp from '@noble/secp256k1';
import { hmac } from '@noble/hashes/hmac';
import { sha256 as nobleSha256 } from '@noble/hashes/sha256';
import { Transaction, Wallet } from './types';

// Configure secp256k1 sync HMAC for @noble/secp256k1 v2
secp.etc.hmacSha256Sync = (key: Uint8Array, ...msgs: Uint8Array[]) =>
  hmac(nobleSha256, key, secp.etc.concatBytes(...msgs));

/**
 * Computes SHA-256 hash of input data and returns a hex string.
 */
export function sha256(data: string | Uint8Array): string {
  if (typeof data === 'string') {
    return crypto.createHash('sha256').update(data, 'utf-8').digest('hex');
  }
  return crypto.createHash('sha256').update(data).digest('hex');
}

/**
 * Computes double SHA-256 hash of input data and returns a hex string.
 */
export function doubleSha256(data: string | Uint8Array): string {
  const first = typeof data === 'string'
    ? crypto.createHash('sha256').update(data, 'utf-8').digest()
    : crypto.createHash('sha256').update(data).digest();
  return crypto.createHash('sha256').update(first).digest('hex');
}

/**
 * Generates a real secp256k1 keypair.
 * Returns private key and compressed public key as hex strings.
 */
export function generateKeyPair(): { privateKey: string; publicKey: string } {
  const privKeyBytes = secp.utils.randomPrivateKey();
  const privateKey = Buffer.from(privKeyBytes).toString('hex');
  const pubKeyBytes = secp.getPublicKey(privKeyBytes, true); // compressed 33-byte
  const publicKey = Buffer.from(pubKeyBytes).toString('hex');
  return { privateKey, publicKey };
}

/**
 * Derives the public key from a given private key string.
 */
export function getPublicKeyFromPrivateKey(privateKey: string): string {
  const privKeyBytes = Buffer.from(privateKey, 'hex');
  const pubKeyBytes = secp.getPublicKey(privKeyBytes, true);
  return Buffer.from(pubKeyBytes).toString('hex');
}

/**
 * Derives a standard 20-byte hex address (0x...) from a public key string.
 */
export function getAddressFromPublicKey(publicKey: string): string {
  const hash = crypto.createHash('sha256').update(publicKey, 'hex').digest('hex');
  return '0x' + hash.slice(0, 40);
}

/**
 * Builds and signs a transaction using the sender's private key.
 */
export function signTransaction(
  privateKeyOrWallet: string | Wallet,
  to: string,
  amount: number,
  fee: number,
  nonce: number,
  data?: string | null,
  publicKeyParam?: string
): Transaction {
  let privateKey: string;
  let publicKey: string;

  if (typeof privateKeyOrWallet === 'object' && privateKeyOrWallet !== null) {
    privateKey = privateKeyOrWallet.privateKey;
    publicKey = privateKeyOrWallet.publicKey;
  } else {
    privateKey = privateKeyOrWallet;
    publicKey = publicKeyParam || getPublicKeyFromPrivateKey(privateKey);
  }

  const timestamp = Date.now();
  const txData = {
    from: publicKey,
    to,
    amount,
    fee,
    timestamp,
    nonce,
    data: data ?? null,
  };

  const txString = JSON.stringify(txData);
  const hashHex = crypto.createHash('sha256').update(txString).digest('hex');

  const sigObj = secp.sign(hashHex, privateKey);
  const sigHex = Buffer.from(
    (sigObj as any).toCompactRawBytes ? (sigObj as any).toCompactRawBytes() : (sigObj as any)
  ).toString('hex');
  const recovery = sigObj.recovery ?? 0;

  return {
    id: hashHex,
    from: publicKey,
    to,
    amount,
    fee,
    timestamp,
    nonce,
    data: data ?? null,
    signature: sigHex,
    recovery,
  };
}
