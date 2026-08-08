# Verdis Chain SDK Developer Guide: Building Eco-Friendly Decentralized Applications

Welcome to the official developer guide for the **Verdis Chain JavaScript SDK** (`verdis-sdk.js`). This guide provides end-to-end tutorials, architectural patterns, and practical code walkthroughs for software engineers building decentralized applications (dApps), trading bots, indexers, and sustainability tracking tools on the Verdis Chain ecosystem.

---

## Table of Contents

1. [Architectural Overview](#1-architectural-overview)
2. [Chapter 1: Quickstart & Project Setup](#chapter-1-quickstart--project-setup)
3. [Chapter 2: Managing Node Connections & Resiliency](#chapter-2-managing-node-connections--resiliency)
4. [Chapter 3: Working with Accounts, Nonces & SS58 Addresses](#chapter-3-working-with-accounts-nonces--ss58-addresses)
5. [Chapter 4: DPoS Consensus & Validator Monitoring](#chapter-4-dpos-consensus--validator-monitoring)
6. [Chapter 5: Liquidity & Trading on Verdis AMM DEX](#chapter-5-liquidity--trading-on-verdis-amm-dex)
7. [Chapter 6: Sustainable dApps with the Eco Pallet](#chapter-6-sustainable-dapps-with-the-eco-pallet)
8. [Chapter 7: Real-Time Applications & Block Subscriptions](#chapter-7-real-time-applications--block-subscriptions)
9. [Chapter 8: Transaction Submission & Extrinsic Lifecycle](#chapter-8-transaction-submission--extrinsic-lifecycle)
10. [Chapter 9: Raw Storage Queries & SCALE Serialization](#chapter-9-raw-storage-queries--scale-serialization)
11. [Chapter 10: Production Best Practices & Failover Architecture](#chapter-10-production-best-practices--failover-architecture)

---

## 1. Architectural Overview

**Verdis Chain** is a high-performance Substrate-based layer-1 blockchain designed specifically for green finance, decentralized trading, and carbon offset verification. It features:
- **Delegated Proof of Stake (DPoS)** for high-throughput, low-energy consensus.
- **Eco Pallet** for on-chain verification of carbon credits, tree planting, and green validator scoring.
- **AMM DEX Pallet** for automated token swaps and liquidity provision.
- **SS58 Network Prefix 909** for address safety and chain isolation.

### Why `verdis-sdk.js`?
Standard Substrate developer libraries like `@polkadot/api` carry heavy dependencies and large bundle sizes. The **Verdis Chain SDK** was architected as a single-file, zero-dependency JavaScript module that communicates directly via JSON-RPC 2.0 over native WebSockets.

#### Architectural Highlights:
- **Size**: Lightweight single file (~13 KB).
- **Environment**: Compatible with Node.js, Web Browsers, Cloudflare Workers, and React Native.
- **Transport**: Native WebSocket streaming with automatic RPC request ID mapping.
- **Low Overhead**: Direct binary double-map key generation using built-in Twox128 hashing algorithms.

---

## Chapter 1: Quickstart & Project Setup

### Environment Requirements
- **Node.js**: Version 18.0.0 or higher (provides global `WebSocket` support natively).
- **Browsers**: Any modern evergreen browser (Chrome, Firefox, Safari, Edge).

### Step 1: Incorporating the SDK into Your Project

Place `verdis-sdk.js` in your project's source directory (e.g., `./lib/verdis-sdk.js`).

**In Node.js / CommonJS:**
```javascript
const { VerdisSDK } = require('./lib/verdis-sdk');
```

**In ES Modules / React / Vue / Next.js:**
```javascript
import { VerdisSDK } from './lib/verdis-sdk.js';
```

### Step 2: Hello, Verdis Chain!

Create `index.js` and run your first query to fetch chain info:

```javascript
const { VerdisSDK } = require('./verdis-sdk');

async function main() {
  // Connect to local dev node or remote RPC
  const sdk = new VerdisSDK('ws://localhost:9944');
  
  await sdk.connect();
  console.log('Connected successfully!');

  const chainName = await sdk.getChainName();
  const height = await sdk.getBlockHeight();

  console.log(`Node Name: ${chainName}`);
  console.log(`Current Block Height: #${height}`);

  sdk.disconnect();
}

main().catch(console.error);
```

---

## Chapter 2: Managing Node Connections & Resiliency

When operating production dApps, network blips or node restarts shouldn't crash your application. The `VerdisSDK` class handles connection lifecycle state transitions gracefully.

### Configuring Connection Options

```javascript
const sdk = new VerdisSDK('wss://verdischain.com/ws', {
  timeout: 12000,        // 12-second RPC call timeout
  autoReconnect: true    // Auto-reconnect on disconnect
});
```

### Reconnection Mechanism Explained
1. If the socket closes unexpectedly, `sdk.onclose` is triggered.
2. Active pending promises are immediately rejected so caller code doesn't hang indefinitely.
3. The SDK executes an exponential backoff reconnect attempt:
   $$\text{Delay} = \min(1000 \times 2^{\text{attempts}}, 30000) \text{ ms}$$
4. Upon re-establishing the connection, the attempt counter is reset.

### Graceful Shutdown Pattern
Always disconnect the SDK when shutting down background workers or unmounting UI components:

```javascript
process.on('SIGINT', () => {
  console.log('Shutting down server...');
  sdk.disconnect();
  process.exit(0);
});
```

---

## Chapter 3: Working with Accounts, Nonces & SS58 Addresses

Verdis Chain uses **SS58 Network Prefix 909**. This ensures account addresses begin with network-specific identifiers, guarding against accidental cross-chain transactions.

### Reading Account State

Account balances in Substrate are stored under the `System.Account` double-map. You can read an account's state using `getBalance(address)` or `getAccountInfo(address)`:

```javascript
const { VerdisSDK } = require('./verdis-sdk');

async function inspectAccount(address) {
  const sdk = new VerdisSDK('ws://localhost:9944');
  await sdk.connect();

  const accountInfo = await sdk.getAccountInfo(address);
  console.log(`Account details for ${address}:`, accountInfo);

  const nonce = await sdk.getNonce(address);
  console.log(`Next valid transaction nonce: ${nonce}`);

  sdk.disconnect();
}

inspectAccount('5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY');
```

---

## Chapter 4: DPoS Consensus & Validator Monitoring

Verdis Chain uses Delegated Proof of Stake (DPoS) for energy-efficient consensus. The SDK provides dedicated methods to monitor active validator nodes, total staked capital, and epoch progression.

### Building a Validator Dashboard Monitor

```javascript
const { VerdisSDK } = require('./verdis-sdk');

async function monitorValidators() {
  const sdk = new VerdisSDK('ws://localhost:9944');
  await sdk.connect();

  console.log('=== Verdis Chain DPoS Status ===');
  
  const currentEpoch = await sdk.getCurrentEpoch();
  const activeValidators = await sdk.getActiveValidators();
  const totalStaked = await sdk.getTotalStaked();
  const totalValidatorCount = await sdk.getValidatorCount();

  console.log(`Current Epoch         : ${currentEpoch}`);
  console.log(`Total Staked Tokens   : ${totalStaked} VRD`);
  console.log(`Total Registered Nodes: ${totalValidatorCount}`);
  console.log(`Active Validator Set  :`, activeValidators);

  sdk.disconnect();
}

monitorValidators();
```

---

## Chapter 5: Liquidity & Trading on Verdis AMM DEX

The Verdis runtime features an automated market maker (AMM) DEX pallet for decentralized token exchanges.

### Exploring Pools and Reserves

```javascript
const { VerdisSDK } = require('./verdis-sdk');

async function inspectDex() {
  const sdk = new VerdisSDK('ws://localhost:9944');
  await sdk.connect();

  const poolCount = await sdk.getPoolCount();
  const volume = await sdk.getTotalVolume();
  const totalSwaps = await sdk.getTotalSwaps();

  console.log(`AMM DEX Overview:`);
  console.log(`- Total Liquidity Pools: ${poolCount}`);
  console.log(`- Cumulative Volume    : ${volume} VRD`);
  console.log(`- Total Swaps Executed : ${totalSwaps}`);

  if (poolCount > 0) {
    const pools = await sdk.getPools(5);
    pools.forEach((pool, index) => {
      console.log(`
Pool #${index}:`, pool);
    });
  }

  sdk.disconnect();
}

inspectDex();
```

---

## Chapter 6: Sustainable dApps with the Eco Pallet

Verdis Chain incorporates an **Eco Pallet** that indexes eco-friendly metrics directly into state storage. Developers can build carbon offset dashboards, green validator badges, and tree-planting tracker dApps.

### Building an On-Chain Sustainability Audit Tool

```javascript
const { VerdisSDK } = require('./verdis-sdk');

async function auditEcoMetrics() {
  const sdk = new VerdisSDK('ws://localhost:9944');
  await sdk.connect();

  console.log('🌱 --- Verdis Chain Sustainability Impact Report --- 🌱');

  const trees = await sdk.getTotalTreesPlanted();
  const co2Offset = await sdk.getTotalCo2Offset();
  const creditsRetired = await sdk.getTotalCreditsRetired();
  const greenValidators = await sdk.getGreenValidators();
  const carbonCredits = await sdk.getCarbonCredits();

  console.log(`Total Trees Planted       : ${trees || 0}`);
  console.log(`Total CO2 Offset (Tons)   : ${co2Offset || 0}`);
  console.log(`Carbon Credits Retired    : ${creditsRetired || 0}`);
  console.log(`Green Certified Validators:`, greenValidators);
  console.log(`Carbon Credit Records     :`, carbonCredits);

  sdk.disconnect();
}

auditEcoMetrics();
```

---

## Chapter 7: Real-Time Applications & Block Subscriptions

To build reactive dApps, live dashboards, or notification bots, you need real-time block streaming. `verdis-sdk.js` provides WebSocket subscriptions that trigger user callbacks when new blocks are produced.

### Live Block Header Listener

```javascript
const { VerdisSDK } = require('./verdis-sdk');

async function startBlockWatcher() {
  const sdk = new VerdisSDK('ws://localhost:9944');
  await sdk.connect();

  console.log('Listening for live block headers...');

  // Subscribe to new heads
  const subId = await sdk.subscribeNewHeads((header) => {
    const blockNumber = parseInt(header.number, 16);
    console.log(`
[New Block #${blockNumber}]`);
    console.log(` Parent Hash: ${header.parentHash}`);
    console.log(` State Root : ${header.stateRoot}`);
  });

  console.log(`Subscription active with ID: ${subId}`);

  // Listen for 30 seconds, then clean up
  setTimeout(async () => {
    console.log('
Unsubscribing...');
    await sdk.unsubscribe(subId);
    sdk.disconnect();
    console.log('Watcher closed.');
  }, 30000);
}

startBlockWatcher();
```

---

## Chapter 8: Transaction Submission & Extrinsic Lifecycle

All state mutations on Verdis Chain (transferring VRD, swapping tokens, planting trees) require submitting signed extrinsics to the transaction pool.

### Submitting Transactions & Checking Mempool

```javascript
const { VerdisSDK } = require('./verdis-sdk');

async function handleTransactions() {
  const sdk = new VerdisSDK('ws://localhost:9944');
  await sdk.connect();

  // 1. Fetch pending extrinsics in node mempool
  const pendingBefore = await sdk.pendingExtrinsics();
  console.log('Current pending transactions:', pendingBefore.length);

  // 2. Example: Submit a signed extrinsic byte payload (0x...)
  const signedExtrinsicHex = '0x...'; // Construct using your keypair/signer
  
  try {
    const txHash = await sdk.submitExtrinsic(signedExtrinsicHex);
    console.log(`Extrinsic submitted! Transaction Hash: ${txHash}`);
  } catch (error) {
    console.error(`Submission failed: ${error.message}`);
  }

  sdk.disconnect();
}

handleTransactions();
```

---

## Chapter 9: Raw Storage Queries & SCALE Serialization

For custom pallet state storage or low-level queries, `verdis-sdk.js` includes storage helper routines and SCALE codec encoders.

### How Substrate Storage Keys Are Generated

Substrate stores module data under 32-byte storage keys constructed as:
$$\text{Key} = \text{Twox128}(\text{ModuleName}) + \text{Twox128}(\text{StorageItemName}) + \text{SCALE}(\text{KeyParams})$$

### Querying Custom Pallet Storage Key Directly

```javascript
const { VerdisSDK } = require('./verdis-sdk');

async function directStorageQuery() {
  const sdk = new VerdisSDK('ws://localhost:9944');
  await sdk.connect();

  // Compute raw storage key for System.Events
  const key = sdk._storageKey('System', 'Events');
  console.log('Calculated Storage Key for System.Events:', key);

  // Query state storage at current best head
  const rawEvents = await sdk.rpc('state_getStorage', [key]);
  console.log('Raw State Events Payload:', rawEvents);

  sdk.disconnect();
}

directStorageQuery();
```

### Using Built-in SCALE Encoders

```javascript
const { VerdisSDK } = require('./verdis-sdk');
const sdkModule = require('./verdis-sdk');

// standalone SCALE utilities
const { encodeU32, encodeU128, bytesToHex, hexToBytes } = sdkModule;

// Encode a u32 integer (e.g., pool ID 42)
const poolIdBytes = encodeU32(42);
console.log('Encoded Pool ID 42 (hex):', bytesToHex(poolIdBytes)); // 0x2a000000

// Encode a u128 token balance
const balanceBytes = encodeU128(1000000000000000000n);
console.log('Encoded 1 VRD Balance (hex):', bytesToHex(balanceBytes));
```

---

## Chapter 10: Production Best Practices & Failover Architecture

When running application infrastructure at scale, follow these production guidelines:

### 1. Endpoint Pooling & Failover
Maintain a list of RPC endpoints and attempt failover if a primary connection drops:

```javascript
const ENDPOINTS = [
  'wss://rpc1.verdischain.com/ws',
  'wss://rpc2.verdischain.com/ws',
  'ws://localhost:9944'
];

async function connectToCluster() {
  for (const url of ENDPOINTS) {
    try {
      console.log(`Attempting connection to ${url}...`);
      const sdk = new VerdisSDK(url, { timeout: 5000 });
      await sdk.connect();
      console.log(`Connected to cluster node: ${url}`);
      return sdk;
    } catch (e) {
      console.warn(`Failed to connect to ${url}, trying next endpoint...`);
    }
  }
  throw new Error('All RPC endpoints failed.');
}
```

### 2. Error Boundary Patterns
Wrap async RPC calls in try-catch blocks or higher-order retry helpers:

```javascript
async function retryOperation(fn, retries = 3, delayMs = 1000) {
  for (let i = 0; i < retries; i++) {
    try {
      return await fn();
    } catch (err) {
      if (i === retries - 1) throw err;
      await new Promise((r) => setTimeout(r, delayMs));
    }
  }
}
```

### Summary & Next Steps
You are now equipped to build production-grade, eco-friendly dApps on Verdis Chain using `verdis-sdk.js`.

For additional resources:
- SDK Source Code: `/tmp/verdis-repo/sdk/verdis-sdk.js`
- API Reference: `/tmp/verdis-repo/sdk/README.md`
