import sys

readme_content = """# Verdis Chain JavaScript SDK

> Native JavaScript / TypeScript SDK for Verdis Chain — lightweight, dependency-free, with built-in WebSocket support, DPoS staking, AMM DEX interaction, and Eco Pallet tracking.

---

## Table of Contents

- [Overview](#overview)
- [Getting Started](#getting-started)
  - [Installation](#installation)
  - [Connecting to Verdis Chain](#connecting-to-verdis-chain)
  - [Basic Usage Example](#basic-usage-example)
- [API Reference](#api-reference)
  - [Constructor & Connection Management](#constructor--connection-management)
  - [Chain Information](#chain-information)
  - [Account & Balance](#account--balance)
  - [Validators & DPoS Pallet](#validators--dpos-pallet)
  - [DEX / AMM Pallet](#dex--amm-pallet)
  - [Eco Pallet](#eco-pallet)
  - [Tokenomics & Vesting](#tokenomics--vesting)
  - [Extrinsics & Transactions](#extrinsics--transactions)
  - [Storage, Events & Constants](#storage-events--constants)
  - [WebSocket Subscriptions](#websocket-subscriptions)
  - [Internal Storage & Hashing Helpers](#internal-storage--hashing-helpers)
  - [SCALE Codec & Utility Functions](#scale-codec--utility-functions)
- [WebSocket Subscriptions Architecture](#websocket-subscriptions-architecture)
- [Extrinsic Submission Guide](#extrinsic-submission-guide)
- [Error Handling & Resiliency](#error-handling--resiliency)
- [Complete Working Example App](#complete-working-example-app)
- [SS58 Address Format (Prefix 909)](#ss58-address-format-prefix-909)
- [Node RPC Methods Reference](#node-rpc-methods-reference)
- [License](#license)

---

## Overview

The **Verdis Chain JavaScript SDK** (`verdis-sdk.js`) provides a lightweight, asynchronous interface to communicate with Substrate-based Verdis Chain nodes. It operates using native WebSockets without relying on external npm dependencies (such as `@polkadot/api`), making it ideal for browser environments, lightweight backend services, edge workers, and mobile webviews.

### Key Features
- **Zero External Dependencies**: Operates natively in Node.js (v18+) and modern web browsers.
- **WebSocket Native**: Persistent connection with JSON-RPC 2.0 streaming.
- **Auto-Reconnection**: Configurable automatic reconnect with exponential backoff.
- **Built-in Pallet Support**: High-level methods for DPoS Staking, AMM DEX, Carbon Credits (Eco), Tokenomics, and Storage.
- **SCALE Codec Helpers**: Built-in utilities for encoding/decoding primitive Substrate types (u8, u16, u32, u64, u128, bool, vec, bytes).

---

## Getting Started

### Installation

No external package installation is required. Simply include or require `verdis-sdk.js` in your JavaScript/TypeScript project:

**CommonJS (Node.js):**
```javascript
const { VerdisSDK } = require('./verdis-sdk');
```

**ES Modules / Browser:**
```javascript
import { VerdisSDK } from './verdis-sdk.js';

// Or via global window object when included via <script src="verdis-sdk.js"></script>:
const sdk = new window.VerdisSDK();
```

### Connecting to Verdis Chain

You can connect to a local development node or a public remote endpoint.

- **Local Development Node**: `ws://localhost:9944` (or HTTP `http://localhost:9944`)
- **Mainnet / Public RPC**: `wss://verdischain.com/ws`

```javascript
const { VerdisSDK } = require('./verdis-sdk');

async function main() {
  // Initialize SDK with node WebSocket URL and custom options
  const sdk = new VerdisSDK('ws://localhost:9944', {
    timeout: 10000,      // RPC response timeout in milliseconds (default: 10000ms)
    autoReconnect: true  // Automatically attempt reconnection on drop (default: true)
  });

  // Connect to node
  await sdk.connect();
  console.log('Connected status:', sdk.isConnected());

  // Gracefully disconnect when finished
  // sdk.disconnect();
}

main().catch(console.error);
```

### Basic Usage Example

```javascript
const { VerdisSDK } = require('./verdis-sdk');

async function run() {
  const sdk = new VerdisSDK('wss://verdischain.com/ws');
  await sdk.connect();

  // Query block height and chain name
  const chainName = await sdk.getChainName();
  const height = await sdk.getBlockHeight();
  console.log(`Connected to ${chainName} at block #${height}`);

  // Query account balance
  const aliceAddress = '5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY';
  const balance = await sdk.getBalance(aliceAddress);
  console.log('Alice Account Info:', balance);

  sdk.disconnect();
}

run();
```

---

## API Reference

This section documents all **51 prototype methods** of the `VerdisSDK` class, grouped by functional category, as well as the standalone SCALE codec utility functions.

---

### Constructor & Connection Management

#### `constructor(wsUrl?, options?)`
Creates a new `VerdisSDK` instance.

- **Parameters**:
  - `wsUrl` (`string`, optional, default: `'ws://localhost:9944'`): WebSocket RPC endpoint URL.
  - `options` (`object`, optional):
    - `options.timeout` (`number`, default: `10000`): Request timeout in milliseconds.
    - `options.autoReconnect` (`boolean`, default: `true`): Whether to automatically reconnect upon socket termination.
- **Returns**: `VerdisSDK` instance.
- **Example**:
  ```javascript
  const sdk = new VerdisSDK('wss://verdischain.com/ws', { timeout: 15000, autoReconnect: true });
  ```

#### `async connect()`
Establishes a WebSocket connection to the configured `wsUrl`.

- **Parameters**: None.
- **Returns**: `Promise<VerdisSDK>` - Resolves to the SDK instance upon successful connection.
- **Throws**: `Error` if connection fails or fails to open before timeout.
- **Example**:
  ```javascript
  await sdk.connect();
  console.log('Connected to Verdis node!');
  ```

#### `disconnect()`
Terminates the active WebSocket connection and disables automatic reconnection.

- **Parameters**: None.
- **Returns**: `void`.
- **Example**:
  ```javascript
  sdk.disconnect();
  console.log('Disconnected.');
  ```

#### `isConnected()`
Checks whether the SDK currently maintains an active WebSocket connection.

- **Parameters**: None.
- **Returns**: `boolean` - `true` if connected, `false` otherwise.
- **Example**:
  ```javascript
  if (sdk.isConnected()) {
    console.log('Socket is active');
  }
  ```

#### `async rpc(method, params?)`
Sends a raw JSON-RPC 2.0 request over the WebSocket connection.

- **Parameters**:
  - `method` (`string`): The JSON-RPC method name (e.g. `'chain_getHeader'`).
  - `params` (`Array<any>`, optional, default: `[]`): Parameters array for the RPC call.
- **Returns**: `Promise<any>` - Resolves with the `result` property of the JSON-RPC response.
- **Throws**: `Error` if disconnected, on RPC timeout, or if node returns an RPC error response.
- **Example**:
  ```javascript
  const header = await sdk.rpc('chain_getHeader', []);
  console.log('Header:', header);
  ```

---

### Chain Information

#### `async getBlockHeight()`
Queries the current block height (latest best block number) of the chain.

- **Parameters**: None.
- **Returns**: `Promise<number>` - The current block number as an integer.
- **Example**:
  ```javascript
  const height = await sdk.getBlockHeight();
  console.log('Current block height:', height); // e.g. 142050
  ```

#### `async getBlock(hash?)`
Fetches block details for a given block hash or the latest block if hash is omitted.

- **Parameters**:
  - `hash` (`string`, optional): Hex block hash (e.g. `'0x1234...'`).
- **Returns**: `Promise<object>` - SignedBlock JSON object containing block header and extrinsics.
- **Example**:
  ```javascript
  const block = await sdk.getBlock('0x8f2a...');
  console.log('Block extrinsics count:', block.block.extrinsics.length);
  ```

#### `async getBlockHash(blockNum)`
Gets the block hash for a specific block height.

- **Parameters**:
  - `blockNum` (`number`): The block height number.
- **Returns**: `Promise<string>` - Hex-encoded block hash string.
- **Example**:
  ```javascript
  const hash = await sdk.getBlockHash(1000);
  console.log('Hash of block 1000:', hash);
  ```

#### `async getFinalizedHead()`
Retrieves the hash of the latest finalized block on the chain.

- **Parameters**: None.
- **Returns**: `Promise<string>` - Hex block hash of finalized head.
- **Example**:
  ```javascript
  const finalizedHash = await sdk.getFinalizedHead();
  console.log('Finalized head:', finalizedHash);
  ```

#### `async getChainName()`
Retrieves the human-readable name of the blockchain.

- **Parameters**: None.
- **Returns**: `Promise<string>` - Chain name (e.g., `'Verdis Chain'`).
- **Example**:
  ```javascript
  const chainName = await sdk.getChainName();
  console.log('Chain:', chainName);
  ```

#### `async getChainType()`
Gets the chain classification type.

- **Parameters**: None.
- **Returns**: `Promise<string>` - Chain type (e.g., `'Development'`, `'Local'`, `'Live'`).
- **Example**:
  ```javascript
  const type = await sdk.getChainType();
  console.log('Chain type:', type);
  ```

#### `async getNodeVersion()`
Gets the version string of the running node software.

- **Parameters**: None.
- **Returns**: `Promise<string>` - Node version (e.g. `'1.0.0-a8f3b'`).
- **Example**:
  ```javascript
  const version = await sdk.getNodeVersion();
  console.log('Node version:', version);
  ```

#### `async getNodeName()`
Gets the client implementation name of the node.

- **Parameters**: None.
- **Returns**: `Promise<string>` - Client name (e.g. `'Verdis Substrate Node'`).
- **Example**:
  ```javascript
  const name = await sdk.getNodeName();
  console.log('Node implementation name:', name);
  ```

#### `async getSystemHealth()`
Gets the current operational status and health metrics of the node.

- **Parameters**: None.
- **Returns**: `Promise<object>` - Health status object (`{ peers: number, isSyncing: boolean, ... }`).
- **Example**:
  ```javascript
  const health = await sdk.getSystemHealth();
  console.log(`Connected peers: ${health.peers}, Syncing: ${health.isSyncing}`);
  ```

#### `async getSystemProperties()`
Gets configured chain properties such as SS58 prefix, token decimals, and token symbol.

- **Parameters**: None.
- **Returns**: `Promise<object>` - Properties map (`{ ss58Format: 909, tokenDecimals: 18, tokenSymbol: 'VRD' }`).
- **Example**:
  ```javascript
  const props = await sdk.getSystemProperties();
  console.log('Symbol:', props.tokenSymbol, 'SS58 Prefix:', props.ss58Format);
  ```

#### `async getRuntimeVersion()`
Gets the specification and implementation version of the active Substrate runtime.

- **Parameters**: None.
- **Returns**: `Promise<object>` - Spec name, spec version, authoring version, etc.
- **Example**:
  ```javascript
  const runtime = await sdk.getRuntimeVersion();
  console.log('Runtime Spec Version:', runtime.specVersion);
  ```

---

### Account & Balance

#### `async getAccountInfo(address)`
Reads raw account storage data for the specified address from the `System.Account` storage map.

- **Parameters**:
  - `address` (`string`): Account SS58 address or raw public key hex.
- **Returns**: `Promise<any>` - Raw account data structure containing nonce, consumers, providers, and balance fields (`free`, `reserved`, `miscFrozen`, `feeFrozen`).
- **Example**:
  ```javascript
  const info = await sdk.getAccountInfo('5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY');
  console.log('Account Info:', info);
  ```

#### `async getBalance(address)`
Queries account balance details (alias for `getAccountInfo`).

- **Parameters**:
  - `address` (`string`): Account SS58 address.
- **Returns**: `Promise<any>` - Account balance data object.
- **Example**:
  ```javascript
  const balance = await sdk.getBalance('5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY');
  console.log('Balance:', balance);
  ```

#### `async getNonce(address)`
Queries the current transaction nonce for an account from `System.AccountNonce`.

- **Parameters**:
  - `address` (`string`): Account SS58 address.
- **Returns**: `Promise<number>` - Integer nonce value (defaults to 0 if account not initialized).
- **Example**:
  ```javascript
  const nonce = await sdk.getNonce('5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY');
  console.log('Next nonce:', nonce);
  ```

---

### Validators & DPoS Pallet

#### `async getValidators()`
Queries the total set of validator candidates or bonded validator entries in the DPoS pallet.

- **Parameters**: None.
- **Returns**: `Promise<any>` - Storage data for `DPoS.Validators`.
- **Example**:
  ```javascript
  const validators = await sdk.getValidators();
  console.log('Registered validators:', validators);
  ```

#### `async getValidatorCount()`
Queries the total count of registered validator nodes.

- **Parameters**: None.
- **Returns**: `Promise<any>` - Value stored in `DPoS.ValidatorList`.
- **Example**:
  ```javascript
  const count = await sdk.getValidatorCount();
  console.log('Validator count:', count);
  ```

#### `async getActiveValidators()`
Queries the current active set of block-producing validators for the active epoch.

- **Parameters**: None.
- **Returns**: `Promise<any>` - Array of active validator account IDs from `DPoS.ActiveValidators`.
- **Example**:
  ```javascript
  const active = await sdk.getActiveValidators();
  console.log('Active validator set:', active);
  ```

#### `async getTotalStaked()`
Queries the total amount of VRD tokens currently staked across all delegators and validators.

- **Parameters**: None.
- **Returns**: `Promise<any>` - Total staked token amount from `DPoS.TotalStaked`.
- **Example**:
  ```javascript
  const staked = await sdk.getTotalStaked();
  console.log('Total network stake:', staked);
  ```

#### `async getCurrentEpoch()`
Queries the current DPoS consensus epoch index.

- **Parameters**: None.
- **Returns**: `Promise<number>` - Integer epoch number from `DPoS.CurrentEpoch` (defaults to 0).
- **Example**:
  ```javascript
  const epoch = await sdk.getCurrentEpoch();
  console.log('Current epoch:', epoch);
  ```

---

### DEX / AMM Pallet

#### `async getPoolCount()`
Gets the total number of liquidity pools created in the AMM DEX pallet.

- **Parameters**: None.
- **Returns**: `Promise<number>` - Integer pool count from `AmmDex.PoolCount`.
- **Example**:
  ```javascript
  const count = await sdk.getPoolCount();
  console.log('Total AMM pools:', count);
  ```

#### `async getPool(poolId)`
Queries storage details for a specific liquidity pool by its numeric ID.

- **Parameters**:
  - `poolId` (`number`): The pool ID index (0-based integer).
- **Returns**: `Promise<any>` - Pool storage data object (token pair, reserve A, reserve B, total LP tokens).
- **Example**:
  ```javascript
  const pool = await sdk.getPool(0);
  console.log('Pool 0 data:', pool);
  ```

#### `async getPools(limit?)`
Queries multiple liquidity pools up to a specified limit.

- **Parameters**:
  - `limit` (`number`, optional, default: `10`): Maximum number of pools to fetch.
- **Returns**: `Promise<Array<any>>` - Array of pool objects.
- **Example**:
  ```javascript
  const pools = await sdk.getPools(5);
  console.log(`Fetched ${pools.length} DEX pools`);
  ```

#### `async getTotalVolume()`
Queries total cumulative trading volume recorded on the AMM DEX.

- **Parameters**: None.
- **Returns**: `Promise<any>` - Total volume metric from `AmmDex.TotalVolume`.
- **Example**:
  ```javascript
  const volume = await sdk.getTotalVolume();
  console.log('Total DEX Volume:', volume);
  ```

#### `async getTotalSwaps()`
Queries the total count of executed token swaps on the DEX.

- **Parameters**: None.
- **Returns**: `Promise<number>` - Total swaps executed from `AmmDex.TotalSwaps`.
- **Example**:
  ```javascript
  const swaps = await sdk.getTotalSwaps();
  console.log('Total DEX Swaps executed:', swaps);
  ```

---

### Eco Pallet

#### `async getCarbonCredits()`
Queries registered carbon credit records from `Eco.CarbonCredits`.

- **Parameters**: None.
- **Returns**: `Promise<any>` - Carbon credit registry entries.
- **Example**:
  ```javascript
  const credits = await sdk.getCarbonCredits();
  console.log('Carbon Credit registry:', credits);
  ```

#### `async getGreenValidators()`
Queries list of validators classified as green nodes (powered by renewable energy).

- **Parameters**: None.
- **Returns**: `Promise<any>` - Green validator accounts from `Eco.GreenValidators`.
- **Example**:
  ```javascript
  const greenNodes = await sdk.getGreenValidators();
  console.log('Green Validators:', greenNodes);
  ```

#### `async getTotalCo2Offset()`
Queries total metric tons of CO2 offset tracked on-chain.

- **Parameters**: None.
- **Returns**: `Promise<any>` - CO2 offset total from `Eco.TotalCo2Offset`.
- **Example**:
  ```javascript
  const co2 = await sdk.getTotalCo2Offset();
  console.log('Total CO2 Offset (tons):', co2);
  ```

#### `async getTotalTreesPlanted()`
Queries cumulative number of trees planted verified by the Eco pallet.

- **Parameters**: None.
- **Returns**: `Promise<any>` - Tree count total from `Eco.TotalTreesPlanted`.
- **Example**:
  ```javascript
  const trees = await sdk.getTotalTreesPlanted();
  console.log('Total Trees Planted:', trees);
  ```

#### `async getTotalCreditsRetired()`
Queries total carbon credits permanently retired / burned for environmental offsets.

- **Parameters**: None.
- **Returns**: `Promise<any>` - Total retired credits from `Eco.TotalCreditsRetired`.
- **Example**:
  ```javascript
  const retired = await sdk.getTotalCreditsRetired();
  console.log('Retired Carbon Credits:', retired);
  ```

---

### Tokenomics & Vesting

#### `async getTotalSupply()`
Queries the total circulating supply of VRD tokens.

- **Parameters**: None.
- **Returns**: `Promise<any>` - Total token supply from `Tokenomics.TotalSupply`.
- **Example**:
  ```javascript
  const supply = await sdk.getTotalSupply();
  console.log('Total VRD Supply:', supply);
  ```

#### `async getPresalePrice()`
Queries configured token price for presale rounds.

- **Parameters**: None.
- **Returns**: `Promise<any>` - Presale price value from `Tokenomics.PresalePrice`.
- **Example**:
  ```javascript
  const price = await sdk.getPresalePrice();
  console.log('Presale Price:', price);
  ```

#### `async getVestingSchedules()`
Queries vesting schedule parameters from `Vesting.VestingSchedules`.

- **Parameters**: None.
- **Returns**: `Promise<any>` - Vesting schedules list.
- **Example**:
  ```javascript
  const schedules = await sdk.getVestingSchedules();
  console.log('Vesting Schedules:', schedules);
  ```

---

### Extrinsics & Transactions

#### `async submitExtrinsic(extrinsic)`
Submits a SCALE-encoded signed transaction / extrinsic to the node transaction pool.

- **Parameters**:
  - `extrinsic` (`string`): Hex-encoded signed extrinsic string (e.g. `'0x...'`).
- **Returns**: `Promise<string>` - The transaction hash assigned by the author RPC module.
- **Throws**: `Error` if submission is rejected by transaction pool validation.
- **Example**:
  ```javascript
  const txHash = await sdk.submitExtrinsic('0x4904...00');
  console.log('Submitted extrinsic hash:', txHash);
  ```

#### `async pendingExtrinsics()`
Fetches all currently pending extrinsics waiting in the node's mempool.

- **Parameters**: None.
- **Returns**: `Promise<Array<string>>` - Array of hex-encoded pending extrinsic strings.
- **Example**:
  ```javascript
  const pending = await sdk.pendingExtrinsics();
  console.log('Pending transactions in mempool:', pending.length);
  ```

---

### Storage, Events & Constants

#### `async getPinnedData()`
Queries pinned IPFS or decentralised storage metadata from `Storage.PinnedData`.

- **Parameters**: None.
- **Returns**: `Promise<any>` - Storage data object.
- **Example**:
  ```javascript
  const pinned = await sdk.getPinnedData();
  console.log('Pinned storage metadata:', pinned);
  ```

#### `async queryStorage(module, key, blockHash?)`
Helper method to calculate module storage key and query `state_getStorage`.

- **Parameters**:
  - `module` (`string`): Pallet name (e.g., `'System'`, `'Balances'`, `'DPoS'`).
  - `key` (`string`): Storage item name (e.g., `'Account'`, `'TotalIssuance'`).
  - `blockHash` (`string`, optional): Hash of specific block to query historical state.
- **Returns**: `Promise<any>` - Raw hex or decoded storage value.
- **Example**:
  ```javascript
  const data = await sdk.queryStorage('System', 'Events');
  console.log('Current events raw data:', data);
  ```

#### `async queryStorageAt(keys, blockHash?)`
Queries state storage for multiple storage keys at a given block.

- **Parameters**:
  - `keys` (`Array<string>`): Array of hex-encoded storage keys.
  - `blockHash` (`string`, optional): Block hash to query at.
- **Returns**: `Promise<any>` - Array of storage values corresponding to the keys.
- **Example**:
  ```javascript
  const keys = ['0x1234...', '0x5678...'];
  const res = await sdk.queryStorageAt(keys);
  console.log('Storage query results:', res);
  ```

#### `async getKeys(prefix, blockHash?)`
Fetches state storage keys matching a given prefix string/key.

- **Parameters**:
  - `prefix` (`string`): Storage key hex prefix.
  - `blockHash` (`string`, optional): Optional block hash.
- **Returns**: `Promise<Array<string>>` - Array of matching storage key hex strings.
- **Example**:
  ```javascript
  const keys = await sdk.getKeys('0x26aa394bea01e74dbace168582103f6f');
  console.log('Found matching keys:', keys.length);
  ```

#### `async getEvents(blockHash?)`
Queries system events recorded in storage for a specific block or the current head.

- **Parameters**:
  - `blockHash` (`string`, optional): Block hash.
- **Returns**: `Promise<any>` - Raw event record bytes or decoded event entries from `System.Events`.
- **Example**:
  ```javascript
  const events = await sdk.getEvents();
  console.log('Block events:', events);
  ```

#### `async getConstant(module, constant)`
Queries a pallet runtime constant metadata entry.

- **Parameters**:
  - `module` (`string`): Pallet module name.
  - `constant` (`string`): Constant name.
- **Returns**: `Promise<any>` - Constant value stored at pallet prefix.
- **Example**:
  ```javascript
  const existDeposit = await sdk.getConstant('Balances', 'ExistentialDeposit');
  console.log('Existential Deposit:', existDeposit);
  ```

---

### WebSocket Subscriptions

#### `async subscribeNewHeads(callback)`
Subscribes to live new block headers as they are imported by the node.

- **Parameters**:
  - `callback` (`function(header)`): Callback function called with block header object on every new block.
- **Returns**: `Promise<string>` - Subscription ID string.
- **Example**:
  ```javascript
  const subId = await sdk.subscribeNewHeads((header) => {
    console.log('New Block Header #', parseInt(header.number, 16));
  });
  console.log('Active Subscription ID:', subId);
  ```

#### `async subscribeFinalizedHeads(callback)`
Subscribes to live finalized block headers as blocks achieve finality.

- **Parameters**:
  - `callback` (`function(header)`): Callback function invoked with finalized block header.
- **Returns**: `Promise<string>` - Subscription ID string.
- **Example**:
  ```javascript
  const subId = await sdk.subscribeFinalizedHeads((header) => {
    console.log('Finalized Block #', parseInt(header.number, 16));
  });
  ```

#### `async unsubscribe(subId)`
Unsubscribes an active block header subscription.

- **Parameters**:
  - `subId` (`string`): Subscription ID returned by `subscribeNewHeads` or `subscribeFinalizedHeads`.
- **Returns**: `Promise<boolean>` - `true` if successfully unsubscribed.
- **Example**:
  ```javascript
  const ok = await sdk.unsubscribe(subId);
  console.log('Unsubscribed:', ok);
  ```

---

### Internal Storage & Hashing Helpers

These private helper methods are used internally by the SDK to construct Substrate double-map storage keys and compute hashes.

#### `_storageKey(module, item, ...params)`
Constructs a standard Substrate storage key hex string by concatenating `Twox128(module) + Twox128(item) + SCALE(params)`.

- **Parameters**:
  - `module` (`string`): Pallet module name.
  - `item` (`string`): Storage item name.
  - `...params` (`Buffer | string | number`): Key parameters (e.g. account public key or numeric ID).
- **Returns**: `string` - Hex storage key string starting with `'0x'`.
- **Example**:
  ```javascript
  const key = sdk._storageKey('System', 'Account', '5GrwvaEF...');
  console.log('Storage Key:', key);
  ```

#### `_hashModule(name)`
Computes Twox128 hash of pallet module name string.

- **Parameters**:
  - `name` (`string`): Module name.
- **Returns**: `string` - 32-character (16-byte) hex hash.
- **Example**:
  ```javascript
  const hash = sdk._hashModule('System');
  ```

#### `_hashItem(name)`
Computes Twox128 hash of storage item name string.

- **Parameters**:
  - `name` (`string`): Item name.
- **Returns**: `string` - 32-character (16-byte) hex hash.
- **Example**:
  ```javascript
  const hash = sdk._hashItem('Account');
  ```

#### `_twox128(data)`
Implements 128-bit Twox hash algorithm over raw string or Buffer data.

- **Parameters**:
  - `data` (`string | Buffer`): Input payload to hash.
- **Returns**: `string` - 32 hex character hash string.
- **Example**:
  ```javascript
  const hash = sdk._twox128('Balances');
  ```

---

### SCALE Codec & Utility Functions

The SDK exports standalone SCALE encoding/decoding primitive utility functions used for binary serialization of Substrate types:

| Utility Function | Parameters | Return Type | Description |
|---|---|---|---|
| `encodeU8(n)` | `n: number` | `Buffer` | Encodes unsigned 8-bit integer into 1-byte Buffer. |
| `encodeU16(n)` | `n: number` | `Buffer` | Encodes unsigned 16-bit integer into 2-byte little-endian Buffer. |
| `encodeU32(n)` | `n: number` | `Buffer` | Encodes unsigned 32-bit integer into 4-byte little-endian Buffer. |
| `encodeU64(n)` | `n: number \| bigint` | `Buffer` | Encodes unsigned 64-bit integer into 8-byte little-endian Buffer. |
| `encodeU128(n)` | `n: number \| bigint` | `Buffer` | Encodes unsigned 128-bit integer into 16-byte little-endian Buffer. |
| `encodeBool(b)` | `b: boolean` | `Buffer` | Encodes boolean as 1-byte Buffer (`0x01` or `0x00`). |
| `encodeVec(arr)` | `arr: Buffer[]` | `Buffer` | Encodes vector of buffers with length prefix. |
| `encodeBytes(b)` | `b: Buffer` | `Buffer` | Encodes single buffer wrapped in vector SCALE prefix. |
| `decodeU32(b, offset?)` | `b: Buffer, offset?: number` | `number` | Decodes 32-bit little-endian integer from Buffer offset. |
| `decodeU64(b, offset?)` | `b: Buffer, offset?: number` | `bigint` | Decodes 64-bit little-endian BigInt from Buffer offset. |
| `hexToBytes(hex)` | `hex: string` | `Buffer` | Converts hex string (with or without `'0x'`) to Buffer. |
| `bytesToHex(b)` | `b: Buffer` | `string` | Converts Buffer to `'0x'` prefixed hex string. |
| `truncateHash(hash, len?)` | `hash: string, len?: number` | `string` | Formats long hex hash into truncated display representation (`0x1234...5678`). |

---

## WebSocket Subscriptions Architecture

The `VerdisSDK` provides a native JSON-RPC pub/sub event mechanism over a single persistent WebSocket connection.

### How Subscriptions Work

1. **Registration**: When calling `subscribeNewHeads(callback)` or `subscribeFinalizedHeads(callback)`, the SDK sends an RPC request (`chain_subscribeNewHeads` or `chain_subscribeFinalizedHeads`) to the node.
2. **Subscription Handler**: The SDK registers the callback inside an internal `subscriptions` Map keyed by the notification event name (`chain_newHead` or `chain_finalizedHead`).
3. **Event Dispatching**: When the node emits push notification frames matching the registered method name:
   ```json
   {
     "jsonrpc": "2.0",
     "method": "chain_newHead",
     "params": {
       "subscription": "sub_xyz123",
       "result": {
         "parentHash": "0x...",
         "number": "0x1a4",
         "stateRoot": "0x...",
         "extrinsicsRoot": "0x..."
       }
     }
   }
   ```
   The WebSocket `onmessage` handler matches `msg.method` against `this.subscriptions` and executes `callback(msg.params.result)`.

4. **Unsubscribing**: Calling `sdk.unsubscribe(subId)` issues the `chain_unsubscribeNewHeads` RPC call, stopping push notifications from the node and cleaning up client resources.

---

## Extrinsic Submission Guide

In Substrate networks, state changes (token transfers, liquidity additions, governance votes, validator bonding) are submitted via **Extrinsics**.

### Submitting a Signed Extrinsic

```javascript
const { VerdisSDK } = require('./verdis-sdk');

async function submitTx() {
  const sdk = new VerdisSDK('ws://localhost:9944');
  await sdk.connect();

  // 1. Fetch sender account nonce
  const senderAddress = '5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY';
  const nonce = await sdk.getNonce(senderAddress);
  console.log('Current sender nonce:', nonce);

  // 2. Prepare hex-encoded signed extrinsic string (constructed using Keyring / transaction builder)
  const signedExtrinsicHex = '0x49040300005gr...';

  try {
    // 3. Submit extrinsic to node pool
    const txHash = await sdk.submitExtrinsic(signedExtrinsicHex);
    console.log('Transaction submitted successfully! Hash:', txHash);

    // 4. Inspect pending extrinsics mempool
    const pending = await sdk.pendingExtrinsics();
    console.log('Transactions pending in mempool:', pending);
  } catch (err) {
    console.error('Extrinsic submission failed:', err.message);
  } finally {
    sdk.disconnect();
  }
}

submitTx();
```

---

## Error Handling & Resiliency

The SDK includes robust built-in error handling and recovery mechanisms to maintain stability across network drops or node maintenance.

### 1. RPC Request Timeouts
Each outgoing RPC request registers a timeout timer (configurable via `options.timeout`, default 10,000ms). If the node fails to return a result within the timeout window, the SDK:
- Cleans up the request from the internal `pending` Map.
- Rejects the request Promise with `Error: RPC timeout: <method_name>`.

### 2. Auto-Reconnection & Exponential Backoff
When the WebSocket connection is closed unexpectedly (`onclose`), the SDK automatically triggers reconnection logic if `autoReconnect` is enabled:
- **Pending Requests Cleanup**: Rejects all active pending RPC promises with `Error: Connection closed`.
- **Exponential Backoff**: Delay increases exponentially starting at `1000ms` up to `maxReconnectDelay = 30000ms` (30 seconds):
  $$\\text{delay} = \\min(1000 \\times 2^{\\text{reconnectAttempts}}, 30000)$$
- **Attempt Reset**: Upon successful connection (`onopen`), `reconnectAttempts` resets back to `0`.

```javascript
const sdk = new VerdisSDK('ws://localhost:9944', {
  timeout: 5000,        // Timeout fast if node responds slowly
  autoReconnect: true   // Maintain persistent connection automatically
});

sdk.connect().catch((err) => {
  console.error('Initial connection failed:', err);
});
```

---

## Complete Working Example App

Below is a self-contained, fully working JavaScript application using `verdis-sdk.js` that connects to Verdis Chain, queries chain metrics, validator information, AMM liquidity pools, Eco metrics, and subscribes to block headers for 30 seconds.

```javascript
const { VerdisSDK } = require('./verdis-sdk');

async function main() {
  console.log('====================================================');
  console.log('   Verdis Chain JavaScript SDK Comprehensive Test');
  console.log('====================================================\n');

  // Initialize SDK
  const sdk = new VerdisSDK('ws://localhost:9944', {
    timeout: 10000,
    autoReconnect: true
  });

  try {
    // 1. Connect
    console.log('[1/6] Connecting to Verdis Chain Node...');
    await sdk.connect();
    console.log(' Successfully connected to node!\n');

    // 2. Fetch System & Chain Info
    console.log('[2/6] Querying Chain System Metrics...');
    const chainName = await sdk.getChainName();
    const chainType = await sdk.getChainType();
    const nodeVersion = await sdk.getNodeVersion();
    const height = await sdk.getBlockHeight();
    const finalized = await sdk.getFinalizedHead();
    const properties = await sdk.getSystemProperties();

    console.log(`  - Chain Name       : ${chainName}`);
    console.log(`  - Chain Type       : ${chainType}`);
    console.log(`  - Node Version     : ${nodeVersion}`);
    console.log(`  - Block Height     : #${height}`);
    console.log(`  - Finalized Head   : ${finalized}`);
    console.log(`  - SS58 Prefix      : ${properties.ss58Format}`);
    console.log(`  - Token Symbol     : ${properties.tokenSymbol}`);
    console.log(`  - Token Decimals   : ${properties.tokenDecimals}\n`);

    // 3. Query DPoS Validator Ecosystem
    console.log('[3/6] Querying DPoS Pallet Staking Data...');
    const epoch = await sdk.getCurrentEpoch();
    const activeValidators = await sdk.getActiveValidators();
    const totalStaked = await sdk.getTotalStaked();

    console.log(`  - Current Epoch    : ${epoch}`);
    console.log(`  - Total Stake      : ${totalStaked || '0'} VRD`);
    console.log(`  - Active Validators: ${JSON.stringify(activeValidators)}\n`);

    // 4. Query AMM DEX Liquidity Pools
    console.log('[4/6] Querying AMM DEX Pallet...');
    const poolCount = await sdk.getPoolCount();
    const totalVolume = await sdk.getTotalVolume();
    const totalSwaps = await sdk.getTotalSwaps();

    console.log(`  - Total Pools      : ${poolCount}`);
    console.log(`  - Cumulative Volume: ${totalVolume || '0'} VRD`);
    console.log(`  - Executed Swaps   : ${totalSwaps}`);
    if (poolCount > 0) {
      const pools = await sdk.getPools(3);
      console.log('  - Sample Pools     :', pools);
    }
    console.log('');

    // 5. Query Eco Pallet Metrics
    console.log('[5/6] Querying Eco Pallet Sustainability Metrics...');
    const trees = await sdk.getTotalTreesPlanted();
    const co2Offset = await sdk.getTotalCo2Offset();
    const creditsRetired = await sdk.getTotalCreditsRetired();
    const greenNodes = await sdk.getGreenValidators();

    console.log(`  - Trees Planted    : ${trees || 0}`);
    console.log(`  - CO2 Offset (tons): ${co2Offset || 0}`);
    console.log(`  - Credits Retired  : ${creditsRetired || 0}`);
    console.log(`  - Green Validators : ${JSON.stringify(greenNodes)}\n`);

    // 6. WebSocket Block Header Subscription
    console.log('[6/6] Subscribing to New Block Headers (Listening for 20 seconds)...');
    let blockCount = 0;
    const subId = await sdk.subscribeNewHeads((header) => {
      blockCount++;
      const blockNum = parseInt(header.number, 16);
      console.log(`  [Block #${blockNum}] Hash: ${header.parentHash || 'N/A'}`);
    });

    console.log(` Subscription created with ID: ${subId}`);
    console.log(' Waiting for incoming blocks...');

    await new Promise((resolve) => setTimeout(resolve, 20000));

    // Unsubscribe
    console.log('\n Unsubscribing block headers...');
    await sdk.unsubscribe(subId);
    console.log(` Received ${blockCount} new blocks during subscription period.`);

  } catch (err) {
    console.error('Error during SDK execution:', err);
  } finally {
    console.log('\nClosing SDK connection...');
    sdk.disconnect();
    console.log('====================================================');
    console.log('   Test Complete');
    console.log('====================================================');
  }
}

main();
```

---

## SS58 Address Format (Prefix 909)

Verdis Chain uses the standard **SS58 Address Format** with a dedicated network prefix identifier:

- **SS58 Prefix**: `909` (`0x038D`)
- **Token Symbol**: `VRD`
- **Decimals**: `18`

### SS58 Structure
SS58 addresses are Base58-check encoded representations of 32-byte public key hashes (Sr25519 or Ed25519). An SS58 formatted address consists of:
1. **Prefix Bytes**: Identifies the specific chain network ID (909 for Verdis).
2. **Account Public Key**: 32-byte public key bytes.
3. **BLAKE2 Checksum**: 2-byte verification checksum ensuring address integrity against typos.

Address prefix 909 ensures that address strings generated for Verdis Chain are uniquely formatted and prevent accidental cross-chain token transfers to incompatible Substrate chains.

---

## Node RPC Methods Reference

The SDK methods map directly to standard and custom Substrate JSON-RPC methods provided by the Verdis node:

| SDK Method | JSON-RPC Method | Description |
|---|---|---|
| `getBlockHeight()` | `chain_getHeader` | Fetches latest block header and parses block number hex. |
| `getBlock(hash)` | `chain_getBlock` | Fetches signed block JSON for hash. |
| `getBlockHash(blockNum)` | `chain_getBlockHash` | Fetches block hash for block number. |
| `getFinalizedHead()` | `chain_getFinalizedHead` | Fetches hash of current finalized block. |
| `getChainName()` | `system_chain` | Queries system chain name. |
| `getChainType()` | `system_chainType` | Queries chain environment type. |
| `getNodeVersion()` | `system_version` | Queries node binary version. |
| `getNodeName()` | `system_name` | Queries node implementation name. |
| `getSystemHealth()` | `system_health` | Queries peer count and sync status. |
| `getSystemProperties()` | `system_properties` | Queries SS58 prefix, decimals, and token symbol. |
| `getRuntimeVersion()` | `state_getRuntimeVersion` | Queries Substrate runtime specification. |
| `getAccountInfo(addr)` | `state_getStorage` | Storage query on `System.Account`. |
| `getBalance(addr)` | `state_getStorage` | Storage query on `System.Account`. |
| `getNonce(addr)` | `state_getStorage` | Storage query on `System.AccountNonce`. |
| `getValidators()` | `state_getStorage` | Storage query on `DPoS.Validators`. |
| `getValidatorCount()` | `state_getStorage` | Storage query on `DPoS.ValidatorList`. |
| `getActiveValidators()` | `state_getStorage` | Storage query on `DPoS.ActiveValidators`. |
| `getTotalStaked()` | `state_getStorage` | Storage query on `DPoS.TotalStaked`. |
| `getCurrentEpoch()` | `state_getStorage` | Storage query on `DPoS.CurrentEpoch`. |
| `getPoolCount()` | `state_getStorage` | Storage query on `AmmDex.PoolCount`. |
| `getPool(id)` | `state_getStorage` | Storage query on `AmmDex.Pools`. |
| `getTotalVolume()` | `state_getStorage` | Storage query on `AmmDex.TotalVolume`. |
| `getTotalSwaps()` | `state_getStorage` | Storage query on `AmmDex.TotalSwaps`. |
| `getCarbonCredits()` | `state_getStorage` | Storage query on `Eco.CarbonCredits`. |
| `getGreenValidators()` | `state_getStorage` | Storage query on `Eco.GreenValidators`. |
| `getTotalCo2Offset()` | `state_getStorage` | Storage query on `Eco.TotalCo2Offset`. |
| `getTotalTreesPlanted()` | `state_getStorage` | Storage query on `Eco.TotalTreesPlanted`. |
| `getTotalCreditsRetired()` | `state_getStorage` | Storage query on `Eco.TotalCreditsRetired`. |
| `getTotalSupply()` | `state_getStorage` | Storage query on `Tokenomics.TotalSupply`. |
| `getPresalePrice()` | `state_getStorage` | Storage query on `Tokenomics.PresalePrice`. |
| `getVestingSchedules()` | `state_getStorage` | Storage query on `Vesting.VestingSchedules`. |
| `getPinnedData()` | `state_getStorage` | Storage query on `Storage.PinnedData`. |
| `submitExtrinsic(tx)` | `author_submitExtrinsic` | Submits signed extrinsic hex to transaction pool. |
| `pendingExtrinsics()` | `author_pendingExtrinsics` | Returns array of pending transactions in mempool. |
| `subscribeNewHeads(cb)` | `chain_subscribeNewHeads` | Subscribes to live new block headers stream. |
| `subscribeFinalizedHeads(cb)` | `chain_subscribeFinalizedHeads` | Subscribes to finalized block headers stream. |
| `unsubscribe(id)` | `chain_unsubscribeNewHeads` | Unsubscribes header subscription stream. |

---

## License

This SDK is released under the open-source **MIT License**.
Copyright (c) Protremix / Verdis Chain.
"""

with open("/tmp/verdis-repo/sdk/README.md", "w") as f:
    f.write(readme_content)

print("Successfully generated /tmp/verdis-repo/sdk/README.md")
