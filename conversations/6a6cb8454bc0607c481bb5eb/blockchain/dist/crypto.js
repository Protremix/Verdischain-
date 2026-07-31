"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.sha256 = sha256;
exports.doubleSha256 = doubleSha256;
exports.generateKeyPair = generateKeyPair;
exports.getPublicKeyFromPrivateKey = getPublicKeyFromPrivateKey;
exports.getAddressFromPublicKey = getAddressFromPublicKey;
exports.signTransaction = signTransaction;
const crypto_1 = require("crypto");
const secp = require("@noble/secp256k1");
const hmac_1 = require("@noble/hashes/hmac");
const sha256_1 = require("@noble/hashes/sha256");
// Configure secp256k1 sync HMAC for @noble/secp256k1 v2
secp.etc.hmacSha256Sync = (key, ...msgs) => (0, hmac_1.hmac)(sha256_1.sha256, key, secp.etc.concatBytes(...msgs));
/**
 * Computes SHA-256 hash of input data and returns a hex string.
 */
function sha256(data) {
    if (typeof data === 'string') {
        return crypto_1.default.createHash('sha256').update(data, 'utf-8').digest('hex');
    }
    return crypto_1.default.createHash('sha256').update(data).digest('hex');
}
/**
 * Computes double SHA-256 hash of input data and returns a hex string.
 */
function doubleSha256(data) {
    const first = typeof data === 'string'
        ? crypto_1.default.createHash('sha256').update(data, 'utf-8').digest()
        : crypto_1.default.createHash('sha256').update(data).digest();
    return crypto_1.default.createHash('sha256').update(first).digest('hex');
}
/**
 * Generates a real secp256k1 keypair.
 * Returns private key and compressed public key as hex strings.
 */
function generateKeyPair() {
    const privKeyBytes = secp.utils.randomPrivateKey();
    const privateKey = Buffer.from(privKeyBytes).toString('hex');
    const pubKeyBytes = secp.getPublicKey(privKeyBytes, true); // compressed 33-byte
    const publicKey = Buffer.from(pubKeyBytes).toString('hex');
    return { privateKey, publicKey };
}
/**
 * Derives the public key from a given private key string.
 */
function getPublicKeyFromPrivateKey(privateKey) {
    const privKeyBytes = Buffer.from(privateKey, 'hex');
    const pubKeyBytes = secp.getPublicKey(privKeyBytes, true);
    return Buffer.from(pubKeyBytes).toString('hex');
}
/**
 * Derives a standard 20-byte hex address (0x...) from a public key string.
 */
function getAddressFromPublicKey(publicKey) {
    const hash = crypto_1.default.createHash('sha256').update(publicKey, 'hex').digest('hex');
    return '0x' + hash.slice(0, 40);
}
/**
 * Builds and signs a transaction using the sender's private key.
 */
function signTransaction(privateKeyOrWallet, to, amount, fee, nonce, data, publicKeyParam) {
    let privateKey;
    let publicKey;
    if (typeof privateKeyOrWallet === 'object' && privateKeyOrWallet !== null) {
        privateKey = privateKeyOrWallet.privateKey;
        publicKey = privateKeyOrWallet.publicKey;
    }
    else {
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
    const hashHex = crypto_1.default.createHash('sha256').update(txString).digest('hex');
    const sigObj = secp.sign(hashHex, privateKey);
    const sigHex = Buffer.from(sigObj.toCompactRawBytes ? sigObj.toCompactRawBytes() : sigObj).toString('hex');
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
