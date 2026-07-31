"use strict";
/**
 * Ethereum JSON-RPC Compatibility Layer for Trust Wallet
 *
 * Implements standard Ethereum JSON-RPC methods so that Trust Wallet
 * (and MetaMask, etc.) can connect to Verdis as a custom network.
 *
 * Network config for Trust Wallet:
 *   Network Name: Verdis
 *   RPC URL: http://localhost:3200/rpc
 *   Chain ID: 909
 *   Symbol: VRS
 *   Explorer: http://localhost:3200
 */
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
exports.VERDIS_CHAIN_ID = void 0;
exports.getEvmAddress = getEvmAddress;
exports.toChecksumAddress = toChecksumAddress;
exports.setupJsonRpc = setupJsonRpc;
const sha3_1 = require("@noble/hashes/sha3");
const secp256k1 = __importStar(require("@noble/secp256k1"));
const sha256_1 = require("@noble/hashes/sha256");
const hmac_1 = require("@noble/hashes/hmac");
// Required for sync signing in @noble/secp256k1 v2.x
secp256k1.etc.hmacSha256Sync = (key, ...msgs) => {
    const concat = secp256k1.etc.concatBytes;
    return (0, hmac_1.hmac)(sha256_1.sha256, key, concat(...msgs));
};
exports.VERDIS_CHAIN_ID = 909;
// VRS has 18 decimals like ETH (1 VRS = 10^18 wei)
const DECIMALS = 18;
/**
 * Derives an Ethereum-compatible address from a public key using keccak256.
 * Takes the uncompressed public key (64 bytes without prefix), keccak256 hashes it,
 * and takes the last 20 bytes.
 */
function getEvmAddress(publicKey) {
    const pubBytes = Buffer.from(publicKey, 'hex');
    // If compressed (33 bytes), decompress
    let uncompressed;
    if (pubBytes.length === 33) {
        uncompressed = secp256k1.getPublicKey(pubBytes.slice(1), false); // false = uncompressed
        // Remove the 0x04 prefix byte
        uncompressed = uncompressed.slice(1);
    }
    else if (pubBytes.length === 65 && pubBytes[0] === 0x04) {
        uncompressed = pubBytes.slice(1);
    }
    else {
        uncompressed = pubBytes;
    }
    const hash = (0, sha3_1.keccak_256)(uncompressed);
    const address = Buffer.from(hash).subarray(12).toString('hex');
    return toChecksumAddress('0x' + address);
}
/**
 * Converts an address to EIP-55 checksum format.
 */
function toChecksumAddress(address) {
    const addr = address.toLowerCase().replace('0x', '');
    const hash = Buffer.from((0, sha3_1.keccak_256)(Buffer.from(addr, 'utf-8'))).toString('hex');
    let result = '0x';
    for (let i = 0; i < addr.length; i++) {
        if (parseInt(hash[i], 16) >= 8) {
            result += addr[i].toUpperCase();
        }
        else {
            result += addr[i];
        }
    }
    return result;
}
/**
 * Converts VRS amount to wei (hex string).
 * 1 VRS = 10^18 wei
 */
function vrsToHexWei(vrs) {
    // Use string math to avoid floating point precision loss
    const [intPart, decPart] = vrs.toString().split('.');
    const intWei = BigInt(intPart) * BigInt(10 ** DECIMALS);
    let decWei = BigInt(0);
    if (decPart) {
        const padded = decPart.slice(0, DECIMALS).padEnd(DECIMALS, '0');
        decWei = BigInt(padded);
    }
    return '0x' + (intWei + decWei).toString(16);
}
/**
 * Converts hex wei string to VRS number.
 */
function hexWeiToVrs(hex) {
    if (!hex || hex === '0x')
        return 0;
    const wei = BigInt(hex);
    return Number(wei) / 10 ** DECIMALS;
}
/**
 * Simple RLP decoder for Ethereum transactions.
 */
function rlpDecode(data) {
    let offset = 0;
    function decodeItem() {
        if (offset >= data.length)
            throw new Error('RLP: unexpected end of data');
        const prefix = data[offset];
        // Single byte (0x00-0x7f)
        if (prefix <= 0x7f) {
            offset++;
            return Buffer.from([prefix]);
        }
        // String (0x80-0xb7)
        if (prefix <= 0xb7) {
            const len = prefix - 0x80;
            offset++;
            const item = data.slice(offset, offset + len);
            offset += len;
            return Buffer.from(item);
        }
        // Long string (0xb8-0xbf)
        if (prefix <= 0xbf) {
            const lenBytes = prefix - 0xb7;
            offset++;
            const len = parseInt(Buffer.from(data.slice(offset, offset + lenBytes)).toString('hex'), 16);
            offset += lenBytes;
            const item = data.slice(offset, offset + len);
            offset += len;
            return Buffer.from(item);
        }
        // List (0xc0-0xf7)
        if (prefix <= 0xf7) {
            const len = prefix - 0xc0;
            offset++;
            const end = offset + len;
            const items = [];
            while (offset < end) {
                items.push(decodeItem());
            }
            return items;
        }
        // Long list (0xf8-0xff)
        const lenBytes = prefix - 0xf7;
        offset++;
        const len = parseInt(Buffer.from(data.slice(offset, offset + lenBytes)).toString('hex'), 16);
        offset += lenBytes;
        const end = offset + len;
        const items = [];
        while (offset < end) {
            items.push(decodeItem());
        }
        return items;
    }
    return decodeItem();
}
/**
 * Parses a raw Ethereum transaction (hex string) and extracts fields.
 */
function parseEthereumTransaction(rawTx) {
    try {
        let raw = rawTx;
        if (raw.startsWith('0x'))
            raw = raw.slice(2);
        const bytes = Buffer.from(raw, 'hex');
        // Check transaction type
        let txType = 0; // legacy
        let payload = bytes;
        if (bytes[0] <= 0x7f) {
            // Typed transaction
            txType = bytes[0];
            payload = bytes.slice(1);
        }
        const decoded = rlpDecode(payload);
        if (!Array.isArray(decoded))
            return null;
        let nonce, gasPrice, gasLimit, to, value, data, v, r, s;
        let chainId = exports.VERDIS_CHAIN_ID;
        if (txType === 0) {
            // Legacy: [nonce, gasPrice, gasLimit, to, value, data, v, r, s]
            nonce = parseInt(Buffer.from(decoded[0]).toString('hex') || '0', 16);
            gasPrice = BigInt('0x' + Buffer.from(decoded[1]).toString('hex') || '0');
            gasLimit = BigInt('0x' + Buffer.from(decoded[2]).toString('hex') || '0');
            to = '0x' + Buffer.from(decoded[3]).toString('hex');
            value = BigInt('0x' + Buffer.from(decoded[4]).toString('hex') || '0');
            data = '0x' + Buffer.from(decoded[5]).toString('hex');
            const vHex = '0x' + Buffer.from(decoded[6]).toString('hex');
            v = parseInt(vHex || '0', 16);
            r = '0x' + Buffer.from(decoded[7]).toString('hex');
            s = '0x' + Buffer.from(decoded[8]).toString('hex');
            // Extract chain ID from v (EIP-155)
            if (v >= 35) {
                chainId = Math.floor((v - 35) / 2);
            }
        }
        else if (txType === 2) {
            // EIP-1559: [chainId, nonce, maxPriorityFee, maxFee, gasLimit, to, value, data, accessList, v, r, s]
            chainId = parseInt(Buffer.from(decoded[0]).toString('hex') || '0', 16);
            nonce = parseInt(Buffer.from(decoded[1]).toString('hex') || '0', 16);
            gasPrice = BigInt('0x' + Buffer.from(decoded[2]).toString('hex') || '0');
            gasLimit = BigInt('0x' + Buffer.from(decoded[4]).toString('hex') || '0');
            to = '0x' + Buffer.from(decoded[5]).toString('hex');
            value = BigInt('0x' + Buffer.from(decoded[6]).toString('hex') || '0');
            data = '0x' + Buffer.from(decoded[7]).toString('hex');
            v = parseInt('0x' + Buffer.from(decoded[9]).toString('hex') || '0', 16);
            r = '0x' + Buffer.from(decoded[10]).toString('hex');
            s = '0x' + Buffer.from(decoded[11]).toString('hex');
        }
        else if (txType === 1) {
            // EIP-2930: [chainId, nonce, gasPrice, gasLimit, to, value, data, accessList, v, r, s]
            chainId = parseInt(Buffer.from(decoded[0]).toString('hex') || '0', 16);
            nonce = parseInt(Buffer.from(decoded[1]).toString('hex') || '0', 16);
            gasPrice = BigInt('0x' + Buffer.from(decoded[2]).toString('hex') || '0');
            gasLimit = BigInt('0x' + Buffer.from(decoded[3]).toString('hex') || '0');
            to = '0x' + Buffer.from(decoded[4]).toString('hex');
            value = BigInt('0x' + Buffer.from(decoded[5]).toString('hex') || '0');
            data = '0x' + Buffer.from(decoded[6]).toString('hex');
            v = parseInt('0x' + Buffer.from(decoded[8]).toString('hex') || '0', 16);
            r = '0x' + Buffer.from(decoded[9]).toString('hex');
            s = '0x' + Buffer.from(decoded[10]).toString('hex');
        }
        else {
            return null;
        }
        // Recover sender address from signature
        // For this we need to sign the transaction hash and recover the public key
        // This requires implementing the signing scheme for Ethereum transactions
        // For now, we'll extract the recovery parameter and use secp256k1.recover
        // Build the unsigned transaction hash for recovery
        const unsignedPayload = buildUnsignedPayload(txType, decoded, chainId);
        const txHash = (0, sha3_1.keccak_256)(unsignedPayload);
        const recovery = txType === 0 ? (v >= 35 ? (v - 35) % 2 : v - 27) : v;
        const sigRS = Buffer.concat([
            Buffer.from(r.replace('0x', ''), 'hex'),
            Buffer.from(s.replace('0x', ''), 'hex'),
        ]);
        let senderAddress = '';
        try {
            const rBig = BigInt(r || '0');
            const sBig = BigInt(s || '0');
            const sig = new secp256k1.Signature(rBig, sBig).addRecoveryBit(recovery);
            const recovered = sig.recoverPublicKey(Buffer.from(txHash));
            const pubHex = recovered.toHex(false); // uncompressed
            senderAddress = getEvmAddress(pubHex);
        }
        catch (e) {
            // If recovery fails, we can't determine the sender
            return null;
        }
        return { nonce, gasPrice, gasLimit, to, value, data, v, r, s, senderAddress, chainId };
    }
    catch (e) {
        return null;
    }
}
/**
 * Builds the unsigned payload for signature recovery.
 */
function buildUnsignedPayload(txType, decoded, chainId) {
    // For legacy transactions: RLP([nonce, gasPrice, gasLimit, to, value, data, chainId, 0, 0])
    if (txType === 0) {
        const unsignedFields = [
            decoded[0], // nonce
            decoded[1], // gasPrice
            decoded[2], // gasLimit
            decoded[3], // to
            decoded[4], // value
            decoded[5], // data
            Buffer.from([chainId]), // chainId
            Buffer.alloc(0), // 0
            Buffer.alloc(0), // 0
        ];
        return Buffer.from(rlpEncode(unsignedFields));
    }
    // For typed transactions, the prefix is included in the hash
    // EIP-1559: 0x02 || RLP([chainId, nonce, maxPriorityFee, maxFee, gasLimit, to, value, data, accessList])
    if (txType === 2) {
        const unsignedFields = decoded.slice(0, 9); // chainId through accessList
        const rlpData = Buffer.from(rlpEncode(unsignedFields));
        return Buffer.concat([Buffer.from([0x02]), rlpData]);
    }
    // EIP-2930: 0x01 || RLP([chainId, nonce, gasPrice, gasLimit, to, value, data, accessList])
    if (txType === 1) {
        const unsignedFields = decoded.slice(0, 8);
        const rlpData = Buffer.from(rlpEncode(unsignedFields));
        return Buffer.concat([Buffer.from([0x01]), rlpData]);
    }
    return Buffer.alloc(0);
}
/**
 * Minimal RLP encoder for building unsigned transaction payloads.
 */
function rlpEncode(item) {
    const parts = [];
    function encodeLength(len, offset) {
        if (len < 56) {
            return Buffer.from([offset + len]);
        }
        const lenBytes = Buffer.from(len.toString(16).padStart(2, '0'), 'hex');
        return Buffer.concat([Buffer.from([offset + 55 + lenBytes.length]), lenBytes]);
    }
    function encode(item) {
        if (Buffer.isBuffer(item)) {
            if (item.length === 1 && item[0] < 0x80) {
                return item;
            }
            return Buffer.concat([encodeLength(item.length, 0x80), item]);
        }
        if (Array.isArray(item)) {
            const encoded = item.map(encode);
            const totalLen = encoded.reduce((sum, buf) => sum + buf.length, 0);
            return Buffer.concat([encodeLength(totalLen, 0xc0), ...encoded]);
        }
        if (typeof item === 'number') {
            if (item === 0)
                return Buffer.from([0x80]);
            const hex = item.toString(16);
            return encode(Buffer.from(hex.length % 2 ? '0' + hex : hex, 'hex'));
        }
        return encode(Buffer.from(item.toString(), 'utf-8'));
    }
    return encode(item);
}
/**
 * Formats a block in Ethereum JSON-RPC format.
 */
function formatBlock(block, includeTxs = false) {
    if (!block)
        return null;
    return {
        number: '0x' + block.header.index.toString(16),
        hash: '0x' + (block.hash || ''),
        parentHash: '0x' + (block.header.previousHash || ''),
        nonce: '0x' + (block.header.nonce || 0).toString(16).padStart(16, '0'),
        sha3Uncles: '0x' + '0'.repeat(64),
        logsBloom: '0x' + '0'.repeat(512),
        transactionsRoot: '0x' + (block.header.merkleRoot || ''),
        stateRoot: '0x' + '0'.repeat(64),
        receiptsRoot: '0x' + '0'.repeat(64),
        miner: block.header.validator ? getEvmAddress(block.header.validator) : '0x' + '0'.repeat(40),
        difficulty: '0x0',
        totalDifficulty: '0x0',
        extraData: '0x',
        size: '0x' + (JSON.stringify(block).length).toString(16),
        gasLimit: '0x' + (8000000).toString(16),
        gasUsed: '0x' + (block.transactions?.length * 21000 || 0).toString(16),
        timestamp: '0x' + Math.floor(block.header.timestamp / 1000).toString(16),
        transactions: includeTxs
            ? (block.transactions || []).map(formatTransaction)
            : (block.transactions || []).map((t) => '0x' + (t.id || '')),
        uncles: [],
    };
}
/**
 * Formats a transaction in Ethereum JSON-RPC format.
 */
function formatTransaction(tx, blockInfo) {
    return {
        blockHash: blockInfo ? '0x' + (blockInfo.hash || '') : null,
        blockNumber: blockInfo ? '0x' + blockInfo.header.index.toString(16) : null,
        from: tx.from || '',
        gas: '0x' + (21000).toString(16),
        gasPrice: '0x' + (tx.fee || 1).toString(16),
        hash: '0x' + (tx.id || ''),
        input: tx.data ? '0x' + tx.data : '0x',
        nonce: '0x' + (tx.nonce || 0).toString(16),
        to: tx.to || '',
        transactionIndex: '0x0',
        value: vrsToHexWei(tx.amount || 0),
        type: '0x0',
        chainId: '0x' + exports.VERDIS_CHAIN_ID.toString(16),
    };
}
/**
 * Sets up JSON-RPC endpoints on the Express app.
 */
function setupJsonRpc(app, blockchain, walletManager) {
    // JSON-RPC endpoint
    app.post('/rpc', (req, res) => {
        handleRpc(req, res, blockchain, walletManager);
    });
    // Also support GET for chainId (some wallets probe)
    app.get('/rpc', (req, res) => {
        res.json({
            jsonrpc: '2.0',
            id: null,
            error: { code: -32600, message: 'Only POST method is supported' }
        });
    });
}
async function handleRpc(req, res, blockchain, walletManager) {
    const { jsonrpc, method, params, id } = req.body;
    // Support batch requests
    if (Array.isArray(req.body)) {
        const results = req.body.map((r) => processMethod(r.method, r.params, r.id, blockchain, walletManager));
        res.json(results);
        return;
    }
    const result = processMethod(method, params, id, blockchain, walletManager);
    res.json(result);
}
function processMethod(method, params, id, blockchain, walletManager) {
    const response = { jsonrpc: '2.0', id };
    try {
        switch (method) {
            case 'eth_chainId':
                return { ...response, result: '0x' + exports.VERDIS_CHAIN_ID.toString(16) };
            case 'net_version':
                return { ...response, result: String(exports.VERDIS_CHAIN_ID) };
            case 'web3_clientVersion':
                return { ...response, result: 'Verdis/v1.0.0' };
            case 'web3_sha3':
                return { ...response, result: '0x' + Buffer.from((0, sha3_1.keccak_256)(Buffer.from(params[0].replace('0x', ''), 'hex'))).toString('hex') };
            case 'net_listening':
                return { ...response, result: true };
            case 'net_peerCount':
                return { ...response, result: '0x0' };
            case 'eth_protocolVersion':
                return { ...response, result: '0x41' };
            case 'eth_syncing':
                return { ...response, result: false };
            case 'eth_mining':
                return { ...response, result: true };
            case 'eth_coinbase':
                return { ...response, result: '0x' + '0'.repeat(40) };
            case 'eth_gasPrice':
                return { ...response, result: '0x' + (10 ** 9).toString(16) }; // 1 Gwei
            case 'eth_blockNumber': {
                const height = blockchain.getChainHeight();
                return { ...response, result: '0x' + height.toString(16) };
            }
            case 'eth_getBalance': {
                const address = params[0].toLowerCase();
                // Map EVM address to native address
                let nativeAddr = address;
                for (const w of walletManager.getAllWallets()) {
                    const evm = getEvmAddress(w.publicKey).toLowerCase();
                    if (evm === address) {
                        nativeAddr = w.address;
                        break;
                    }
                    if (w.address.toLowerCase() === address) {
                        nativeAddr = w.address;
                        break;
                    }
                }
                const balance = blockchain.getTokenSystem().getBalance(nativeAddr);
                return { ...response, result: vrsToHexWei(balance) };
            }
            case 'eth_getTransactionCount': {
                const address = params[0].toLowerCase();
                // Map EVM address to native address
                let nativeAddr = address;
                for (const w of walletManager.getAllWallets()) {
                    const evm = getEvmAddress(w.publicKey).toLowerCase();
                    if (evm === address) {
                        nativeAddr = w.address;
                        break;
                    }
                    if (w.address.toLowerCase() === address) {
                        nativeAddr = w.address;
                        break;
                    }
                }
                let nonce = 0;
                for (const block of blockchain.getChain()) {
                    for (const tx of block.transactions) {
                        if (tx.from.toLowerCase() === nativeAddr.toLowerCase())
                            nonce++;
                    }
                }
                return { ...response, result: '0x' + nonce.toString(16) };
            }
            case 'eth_getCode': {
                // No EVM contracts deployed directly
                return { ...response, result: '0x' };
            }
            case 'eth_getBlockByNumber': {
                const blockNum = params[0] === 'latest'
                    ? blockchain.getChainHeight()
                    : parseInt(params[0], 16);
                const includeTxs = params[1] !== false;
                const block = blockchain.getBlockByIndex(blockNum);
                if (!block)
                    return { ...response, result: null };
                return { ...response, result: formatBlock(block, includeTxs) };
            }
            case 'eth_getBlockByHash': {
                const hash = params[0].replace('0x', '');
                const block = blockchain.getBlockByHash(hash);
                if (!block)
                    return { ...response, result: null };
                return { ...response, result: formatBlock(block, params[1] !== false) };
            }
            case 'eth_getTransactionByHash': {
                const hash = params[0].replace('0x', '');
                const receipt = blockchain.getTransactionReceipt(hash);
                if (!receipt.tx)
                    return { ...response, result: null };
                return { ...response, result: formatTransaction(receipt.tx, receipt.block) };
            }
            case 'eth_getTransactionReceipt': {
                const hash = params[0].replace('0x', '');
                const receipt = blockchain.getTransactionReceipt(hash);
                if (!receipt.tx)
                    return { ...response, result: null };
                return {
                    ...response,
                    result: {
                        transactionHash: '0x' + receipt.tx.id,
                        transactionIndex: '0x0',
                        blockHash: receipt.block ? '0x' + receipt.block.hash : null,
                        blockNumber: receipt.block ? '0x' + receipt.block.header.index.toString(16) : null,
                        from: receipt.tx.from,
                        to: receipt.tx.to,
                        cumulativeGasUsed: '0x' + (21000).toString(16),
                        gasUsed: '0x' + (21000).toString(16),
                        contractAddress: null,
                        logs: [],
                        logsBloom: '0x' + '0'.repeat(512),
                        status: '0x1',
                    }
                };
            }
            case 'eth_sendRawTransaction': {
                const rawTx = params[0];
                const parsed = parseEthereumTransaction(rawTx);
                if (!parsed) {
                    return {
                        ...response,
                        error: { code: -32603, message: 'Failed to parse transaction' }
                    };
                }
                // Convert value from wei to VRS
                const amountVrs = Number(parsed.value) / 10 ** DECIMALS;
                const feeVrs = Number(parsed.gasPrice * parsed.gasLimit) / 10 ** DECIMALS;
                // Find the sender's wallet in our system
                let wallet = walletManager.getAllWallets().find(w => {
                    const evmAddr = getEvmAddress(w.publicKey);
                    return evmAddr.toLowerCase() === parsed.senderAddress.toLowerCase();
                });
                // If not found, try importing the private key (but we don't have it from raw tx)
                // Instead, use the recovered address directly
                if (!wallet) {
                    // Create a wallet entry for this EVM address if we can match it
                    // For now, use the sender address directly
                    const senderAddr = parsed.senderAddress;
                    // Try to find by our SHA-256 address format too
                    wallet = walletManager.getAllWallets().find(w => w.address === senderAddr);
                }
                if (!wallet) {
                    return {
                        ...response,
                        error: { code: -32603, message: 'Sender wallet not found. Import your private key first.' }
                    };
                }
                // Sign and submit the transaction using our system
                const to = parsed.to;
                const tx = walletManager.signTransaction(wallet, to, amountVrs, feeVrs > 0 ? feeVrs : 1, Date.now(), parsed.data !== '0x' ? parsed.data : undefined);
                const result = blockchain.submitTransaction(tx);
                if (!result.success) {
                    return {
                        ...response,
                        error: { code: -32603, message: result.error || 'Transaction failed' }
                    };
                }
                return { ...response, result: '0x' + tx.id };
            }
            case 'eth_call': {
                // For read-only contract calls — return empty for now
                return { ...response, result: '0x' };
            }
            case 'eth_estimateGas': {
                return { ...response, result: '0x' + (21000).toString(16) };
            }
            case 'eth_getLogs': {
                return { ...response, result: [] };
            }
            case 'eth_getStorageAt': {
                return { ...response, result: '0x' + '0'.repeat(64) };
            }
            case 'eth_getBlockTransactionCountByNumber': {
                const blockNum = params[0] === 'latest'
                    ? blockchain.getChainHeight()
                    : parseInt(params[0], 16);
                const block = blockchain.getBlockByIndex(blockNum);
                const count = block ? block.transactions.length : 0;
                return { ...response, result: '0x' + count.toString(16) };
            }
            case 'eth_getBlockTransactionCountByHash': {
                const hash = params[0].replace('0x', '');
                const block = blockchain.getBlockByHash(hash);
                const count = block ? block.transactions.length : 0;
                return { ...response, result: '0x' + count.toString(16) };
            }
            case 'eth_accounts':
                return { ...response, result: walletManager.getAllWallets().map(w => w.address) };
            case 'eth_getTransactionByBlockNumberAndIndex': {
                const blockNum = params[0] === 'latest'
                    ? blockchain.getChainHeight()
                    : parseInt(params[0], 16);
                const idx = parseInt(params[1], 16);
                const block = blockchain.getBlockByIndex(blockNum);
                if (!block || !block.transactions[idx])
                    return { ...response, result: null };
                return { ...response, result: formatTransaction(block.transactions[idx], block) };
            }
            case 'eth_getTransactionByBlockHashAndIndex': {
                const hash = params[0].replace('0x', '');
                const idx = parseInt(params[1], 16);
                const block = blockchain.getBlockByHash(hash);
                if (!block || !block.transactions[idx])
                    return { ...response, result: null };
                return { ...response, result: formatTransaction(block.transactions[idx], block) };
            }
            case 'eth_maxPriorityFeePerGas':
                return { ...response, result: '0x' + (10 ** 9).toString(16) };
            case 'eth_getFeeHistory':
                return {
                    ...response,
                    result: {
                        oldestBlock: '0x0',
                        baseFeePerGas: ['0x' + (10 ** 9).toString(16)],
                        gasUsedRatio: [0.1],
                        reward: [],
                    }
                };
            default:
                return {
                    ...response,
                    error: { code: -32601, message: `Method ${method} not supported` }
                };
        }
    }
    catch (error) {
        return {
            ...response,
            error: { code: -32603, message: error.message || 'Internal error' }
        };
    }
}
//# sourceMappingURL=jsonrpc.js.map