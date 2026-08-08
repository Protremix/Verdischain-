"use strict";

/**
 * Verdis Chain SDK — JavaScript/TypeScript
 *
 * A lightweight SDK for interacting with the Verdis Chain Substrate node.
 * Uses native WebSocket — no external dependencies.
 *
 * @example
 * const { VerdisSDK } = require('./verdis-sdk');
 * const sdk = new VerdisSDK('ws://localhost:9944');
 * await sdk.connect();
 * const height = await sdk.getBlockHeight();
 * console.log('Block height:', height);
 *
 * // Subscribe to new blocks
 * sdk.subscribeNewHeads((header) => {
 *   console.log('New block:', header.number);
 * });
 *
 * @license MIT
 * @author Protremix
 */

// === SCALE Codec Utilities ===
function encodeU8(n) { const b = Buffer.alloc(1); b.writeUInt8(n & 0xFF); return b; }
function encodeU16(n) { const b = Buffer.alloc(2); b.writeUInt16LE(n & 0xFFFF); return b; }
function encodeU32(n) { const b = Buffer.alloc(4); b.writeUInt32LE(n >>> 0); return b; }
function encodeU64(n) { const b = Buffer.alloc(8); b.writeBigUInt64LE(BigInt(n)); return b; }
function encodeU128(n) {
  const b = Buffer.alloc(16);
  const v = BigInt(n);
  for (let i = 0; i < 16; i++) b[i] = Number((v >> BigInt(i * 8)) & 0xFFn);
  return b;
}
function encodeBool(b) { return Buffer.from([b ? 1 : 0]); }
function encodeVec(arr) {
  const len = encodeU32(arr.length);
  return Buffer.concat([len, ...arr]);
}
function encodeBytes(b) { return encodeVec([b]); }
function decodeU32(b, offset = 0) { return b.readUInt32LE(offset); }
function decodeU64(b, offset = 0) { return b.readBigUInt64LE(offset); }
function hexToBytes(hex) {
  hex = hex.replace('0x', '');
  return Buffer.from(hex, 'hex');
}
function bytesToHex(b) { return '0x' + Buffer.from(b).toString('hex'); }
function truncateHash(hash, len = 16) {
  if (!hash || hash.length < len) return hash || '';
  return hash.slice(0, len) + '...' + hash.slice(-8);
}

// === VerdisSDK ===
class VerdisSDK {
  /**
   * Create a new Verdis Chain SDK instance
   * @param {string} wsUrl - WebSocket RPC URL (default: ws://localhost:9944)
   * @param {object} options - SDK options
   * @param {number} options.timeout - RPC timeout in ms (default: 10000)
   * @param {boolean} options.autoReconnect - Auto-reconnect on disconnect (default: true)
   */
  constructor(wsUrl = 'ws://localhost:9944', options = {}) {
    this.wsUrl = wsUrl;
    this.httpUrl = wsUrl.replace('ws://', 'http://').replace('wss://', 'https://');
    this.timeout = options.timeout || 10000;
    this.autoReconnect = options.autoReconnect !== false;
    this.ws = null;
    this.reqId = 1;
    this.pending = new Map();
    this.subscriptions = new Map();
    this.connected = false;
    this.reconnectAttempts = 0;
    this.maxReconnectDelay = 30000;
  }

  /** Connect to the Verdis Chain node */
  async connect() {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.wsUrl);
        this.ws.onopen = () => {
          this.connected = true;
          this.reconnectAttempts = 0;
          console.log('[VerdisSDK] Connected to', this.wsUrl);
          resolve(this);
        };
        this.ws.onclose = () => {
          this.connected = false;
          console.log('[VerdisSDK] Disconnected');
          this.pending.forEach(({ reject }) => reject(new Error('Connection closed')));
          this.pending.clear();
          if (this.autoReconnect) {
            const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts++), this.maxReconnectDelay);
            setTimeout(() => this.connect().catch(() => {}), delay);
          }
        };
        this.ws.onerror = (err) => {
          if (!this.connected) reject(err);
        };
        this.ws.onmessage = (e) => {
          const msg = typeof e.data === 'string' ? JSON.parse(e.data) : JSON.parse(e.data.toString());
          if (msg.id !== undefined && this.pending.has(msg.id)) {
            const { resolve, reject } = this.pending.get(msg.id);
            this.pending.delete(msg.id);
            if (msg.error) reject(new Error(msg.error.message || 'RPC error'));
            else resolve(msg.result);
          } else if (msg.method && this.subscriptions.has(msg.method)) {
            const callback = this.subscriptions.get(msg.method);
            callback(msg.params.result);
          }
        };
      } catch (err) {
        reject(err);
      }
    });
  }

  /** Disconnect from the node */
  disconnect() {
    this.autoReconnect = false;
    if (this.ws) this.ws.close();
    this.ws = null;
    this.connected = false;
  }

  /** Check if connected */
  isConnected() { return this.connected; }

  // === Core RPC ===
  async rpc(method, params = []) {
    if (!this.connected) throw new Error('Not connected');
    const id = this.reqId++;
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        this.pending.delete(id);
        reject(new Error(`RPC timeout: ${method}`));
      }, this.timeout);

      this.pending.set(id, {
        resolve: (result) => { clearTimeout(timer); resolve(result); },
        reject: (err) => { clearTimeout(timer); reject(err); }
      });

      this.ws.send(JSON.stringify({ jsonrpc: '2.0', id, method, params }));
    });
  }

  // === Chain Info ===
  async getBlockHeight() {
    const header = await this.rpc('chain_getHeader');
    return parseInt(header.number, 16);
  }

  async getBlock(hash) {
    return this.rpc('chain_getBlock', [hash]);
  }

  async getBlockHash(blockNum) {
    return this.rpc('chain_getBlockHash', [blockNum]);
  }

  async getFinalizedHead() {
    return this.rpc('chain_getFinalizedHead');
  }

  async getChainName() {
    return this.rpc('system_chain');
  }

  async getChainType() {
    return this.rpc('system_chainType');
  }

  async getNodeVersion() {
    return this.rpc('system_version');
  }

  async getNodeName() {
    return this.rpc('system_name');
  }

  async getSystemHealth() {
    return this.rpc('system_health');
  }

  async getSystemProperties() {
    return this.rpc('system_properties');
  }

  async getRuntimeVersion() {
    return this.rpc('state_getRuntimeVersion');
  }

  // === Account ===
  async getAccountInfo(address) {
    const key = this._storageKey('System', 'Account', address);
    const data = await this.rpc('state_getStorage', [key]);
    return data;
  }

  async getBalance(address) {
    const info = await this.getAccountInfo(address);
    return info;
  }

  async getNonce(address) {
    const key = this._storageKey('System', 'AccountNonce', address);
    const data = await this.rpc('state_getStorage', [key]);
    return data ? parseInt(data, 16) : 0;
  }

  // === DPoS ===
  async getValidators() {
    const key = this._storageKey('DPoS', 'Validators');
    const data = await this.rpc('state_getStorage', [key]);
    return data;
  }

  async getValidatorCount() {
    const key = this._storageKey('DPoS', 'ValidatorList');
    const data = await this.rpc('state_getStorage', [key]);
    return data;
  }

  async getActiveValidators() {
    const key = this._storageKey('DPoS', 'ActiveValidators');
    const data = await this.rpc('state_getStorage', [key]);
    return data;
  }

  async getTotalStaked() {
    const key = this._storageKey('DPoS', 'TotalStaked');
    const data = await this.rpc('state_getStorage', [key]);
    return data;
  }

  async getCurrentEpoch() {
    const key = this._storageKey('DPoS', 'CurrentEpoch');
    const data = await this.rpc('state_getStorage', [key]);
    return data ? parseInt(data, 16) : 0;
  }

  // === AMM DEX ===
  async getPoolCount() {
    const key = this._storageKey('AmmDex', 'PoolCount');
    const data = await this.rpc('state_getStorage', [key]);
    return data ? parseInt(data, 16) : 0;
  }

  async getPool(poolId) {
    const key = this._storageKey('AmmDex', 'Pools', encodeU32(poolId));
    const data = await this.rpc('state_getStorage', [key]);
    return data;
  }

  async getPools(limit = 10) {
    const count = await this.getPoolCount();
    const pools = [];
    for (let i = 0; i < Math.min(count, limit); i++) {
      pools.push(await this.getPool(i));
    }
    return pools;
  }

  async getTotalVolume() {
    const key = this._storageKey('AmmDex', 'TotalVolume');
    const data = await this.rpc('state_getStorage', [key]);
    return data;
  }

  async getTotalSwaps() {
    const key = this._storageKey('AmmDex', 'TotalSwaps');
    const data = await this.rpc('state_getStorage', [key]);
    return data ? parseInt(data, 16) : 0;
  }

  // === Eco ===
  async getCarbonCredits() {
    const key = this._storageKey('Eco', 'CarbonCredits');
    return this.rpc('state_getStorage', [key]);
  }

  async getGreenValidators() {
    const key = this._storageKey('Eco', 'GreenValidators');
    return this.rpc('state_getStorage', [key]);
  }

  async getTotalCo2Offset() {
    const key = this._storageKey('Eco', 'TotalCo2Offset');
    return this.rpc('state_getStorage', [key]);
  }

  async getTotalTreesPlanted() {
    const key = this._storageKey('Eco', 'TotalTreesPlanted');
    return this.rpc('state_getStorage', [key]);
  }

  async getTotalCreditsRetired() {
    const key = this._storageKey('Eco', 'TotalCreditsRetired');
    return this.rpc('state_getStorage', [key]);
  }

  // === Tokenomics ===
  async getTotalSupply() {
    const key = this._storageKey('Tokenomics', 'TotalSupply');
    const data = await this.rpc('state_getStorage', [key]);
    return data;
  }

  async getPresalePrice() {
    const key = this._storageKey('Tokenomics', 'PresalePrice');
    const data = await this.rpc('state_getStorage', [key]);
    return data;
  }

  // === Vesting ===
  async getVestingSchedules() {
    const key = this._storageKey('Vesting', 'VestingSchedules');
    return this.rpc('state_getStorage', [key]);
  }

  // === Storage ===
  async getPinnedData() {
    const key = this._storageKey('Storage', 'PinnedData');
    return this.rpc('state_getStorage', [key]);
  }

  // === Transactions ===
  async submitExtrinsic(extrinsic) {
    return this.rpc('author_submitExtrinsic', [extrinsic]);
  }

  async pendingExtrinsics() {
    return this.rpc('author_pendingExtrinsics');
  }

  // === Subscriptions ===
  async subscribeNewHeads(callback) {
    const subId = await this.rpc('chain_subscribeNewHeads');
    this.subscriptions.set('chain_newHead', callback);
    return subId;
  }

  async subscribeFinalizedHeads(callback) {
    const subId = await this.rpc('chain_subscribeFinalizedHeads');
    this.subscriptions.set('chain_finalizedHead', callback);
    return subId;
  }

  async unsubscribe(subId) {
    return this.rpc('chain_unsubscribeNewHeads', [subId]);
  }

  // === Storage Query Helpers ===
  async queryStorage(module, key, blockHash) {
    const storageKey = this._storageKey(module, key);
    return this.rpc('state_getStorage', blockHash ? [storageKey, blockHash] : [storageKey]);
  }

  async queryStorageAt(keys, blockHash) {
    return this.rpc('state_queryStorageAt', [keys, blockHash]);
  }

  async getKeys(prefix, blockHash) {
    return this.rpc('state_getKeys', blockHash ? [prefix, blockHash] : [prefix]);
  }

  // === Events ===
  async getEvents(blockHash) {
    const key = this._storageKey('System', 'Events');
    const data = await this.rpc('state_getStorage', blockHash ? [key, blockHash] : [key]);
    return data;
  }

  // === Constants ===
  async getConstant(module, constant) {
    const key = `0x${Buffer.from(module).toString('hex')}${Buffer.from(constant).toString('hex')}`;
    return this.rpc('state_getStorage', [key]);
  }

  // === Private Helpers ===
  _storageKey(module, item, ...params) {
    const moduleHash = this._hashModule(module);
    const itemHash = this._hashItem(item);
    let key = '0x' + moduleHash + itemHash;
    if (params && params.length > 0) {
      for (const p of params) {
        if (Buffer.isBuffer(p)) key += p.toString('hex');
        else if (typeof p === 'string') key += Buffer.from(p).toString('hex');
        else if (typeof p === 'number') key += encodeU32(p).toString('hex');
      }
    }
    return key;
  }

  _hashModule(name) {
    // Twox128 hash of module name
    return this._twox128(name);
  }

  _hashItem(name) {
    // Twox128 hash of item name
    return this._twox128(name);
  }

  _twox128(data) {
    // Simplified Twox128 — for production, use proper SipHash
    const buf = Buffer.from(data);
    let h1 = 0, h2 = 0;
    for (let i = 0; i < buf.length; i++) {
      h1 = (h1 * 31 + buf[i]) >>> 0;
      h2 = (h2 * 37 + buf[i]) >>> 0;
    }
    const result = Buffer.alloc(16);
    result.writeUInt32LE(h1, 0);
    result.writeUInt32LE(h2, 4);
    result.writeUInt32LE((h1 ^ 0x5bd1e995) >>> 0, 8);
    result.writeUInt32LE((h2 ^ 0x5bd1e995) >>> 0, 12);
    return result.toString('hex');
  }
}

// === Exports ===
module.exports = { VerdisSDK };
module.exports.VerdisSDK = VerdisSDK;
module.exports.default = VerdisSDK;

// ES module export
if (typeof window !== 'undefined') {
  window.VerdisSDK = VerdisSDK;
}
