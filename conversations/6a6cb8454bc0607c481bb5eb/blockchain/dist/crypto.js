"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.sha256 = sha256;
exports.hashTransaction = hashTransaction;
exports.signTransaction = signTransaction;
exports.verifySignature = verifySignature;
exports.getAddressFromPublicKey = getAddressFromPublicKey;
const crypto_1 = require("crypto");
const hmac_1 = require("@noble/hashes/hmac");
const sha256_1 = require("@noble/hashes/sha256");
const secp = __importStar(require("@noble/secp256k1"));
// Configure secp256k1 HMAC SHA-256 for synchronous signing
secp.etc.hmacSha256Sync = (key, ...msgs) => (0, hmac_1.hmac)(sha256_1.sha256, key, secp.etc.concatBytes(...msgs));
/**
 * Computes SHA-256 hash of given data and returns hex string.
 */
function sha256(data) {
    return (0, crypto_1.createHash)('sha256').update(data).digest('hex');
}
/**
 * Calculates deterministic hash for a transaction object.
 * Hash excludes 'id', 'signature', and 'recovery'.
 */
function hashTransaction(tx) {
    const payload = JSON.stringify({
        from: tx.from,
        to: tx.to,
        amount: tx.amount,
        fee: tx.fee,
        timestamp: tx.timestamp,
        nonce: tx.nonce,
        data: tx.data ?? null,
    });
    return sha256(payload);
}
/**
 * Signs a transaction hash with a private key using secp256k1.
 */
function signTransaction(hash, privateKey) {
    const sig = secp.sign(hash, privateKey);
    return {
        signature: sig.toCompactHex(),
        recovery: sig.recovery,
    };
}
/**
 * Verifies a signature against a transaction hash and public key using secp256k1.
 */
function verifySignature(hash, signature, publicKey, recovery) {
    try {
        return secp.verify(signature, hash, publicKey);
    }
    catch {
        return false;
    }
}
/**
 * Derives an address from a public key string.
 */
function getAddressFromPublicKey(publicKey) {
    if (!publicKey)
        return '';
    if (publicKey.startsWith('RJ') && publicKey.length === 42) {
        return publicKey;
    }
    const hash = sha256(publicKey);
    return 'RJ' + hash.substring(0, 40);
}
//# sourceMappingURL=crypto.js.map