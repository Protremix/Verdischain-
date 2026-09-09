# Verdis Blockchain Developer Documentation Update

**Runtime Version:** Spec v10 (Runtime 2.0.0)  
**Chain ID:** 909  
**SS58 Address Prefix:** 909  
**Native Token:** VRDX (9 Decimals)  
**Network Architecture:** Green DPoS (Delegated Proof of Stake) Substrate-based Layer-1  

---

## Table of Contents
1. [Quick Start](#1-quick-start)
   - [Network Parameters & Connection Details](#network-parameters--connection-details)
   - [Connecting via Polkadot.js API](#connecting-via-polkadotjs-api)
   - [Connecting via Web3.js / Raw JSON-RPC](#connecting-via-web3js--raw-json-rpc)
   - [Connecting via WebSockets](#connecting-via-websockets)
2. [RPC API Reference](#2-rpc-api-reference)
   - [Chain RPCs](#chain-rpcs)
   - [State RPCs](#state-rpcs)
   - [System RPCs](#system-rpcs)
   - [DPoS Staking RPCs](#dpos-staking-rpcs)
   - [AMM DEX RPCs](#amm-dex-rpcs)
   - [Smart Contracts RPCs](#smart-contracts-rpcs)
3. [Smart Contracts](#3-smart-contracts)
   - [Overview of ink! WASM Smart Contracts](#overview-of-ink-wasm-smart-contracts)
   - [Writing & Compiling ink! Contracts](#writing--compiling-ink-contracts)
   - [Deploying WASM Contracts](#deploying-wasm-contracts)
   - [Interacting with Deployed Contracts](#interacting-with-deployed-contracts)
   - [Gas Estimation & Storage Deposit](#gas-estimation--storage-deposit)
4. [Token Standards](#4-token-standards)
   - [Fungible Tokens Pallet](#fungible-tokens-pallet)
   - [NFTs Pallet](#nfts-pallet)
5. [DEX Integration](#5-dex-integration)
   - [AMM DEX Architecture](#amm-dex-architecture)
   - [Adding Liquidity](#adding-liquidity)
   - [Removing Liquidity](#removing-liquidity)
   - [Swapping Tokens](#swapping-tokens)
   - [Fetching Prices & Reserves](#fetching-prices--reserves)
6. [Governance](#6-governance)
   - [Council Proposals](#council-proposals)
   - [Democracy Referenda](#democracy-referenda)
   - [Treasury Proposals & Green Grants](#treasury-proposals--green-grants)
7. [Staking](#7-staking)
   - [Registering as a Validator](#registering-as-a-validator)
   - [Delegating & Staking Tokens](#delegating--staking-tokens)
   - [Unstaking & Unbonding](#unstaking--unbonding)
   - [Claiming Staking Rewards](#claiming-staking-rewards)
8. [SDK Examples](#8-sdk-examples)
   - [1. Connect & Read Network Info](#1-connect--read-network-info)
   - [2. Transfer VRDX Native Tokens](#2-transfer-vrdx-native-tokens)
   - [3. DEX Swap & Liquidity Integration](#3-dex-swap--liquidity-integration)
   - [4. Dry-Run Contract Call](#4-dry-run-contract-call)
   - [5. Query Eco Carbon Offsets](#5-query-eco-carbon-offsets)
   - [6. Subscribe to Live Events](#6-subscribe-to-live-events)
9. [Eco Protocol](#9-eco-protocol)
   - [Carbon Credit Tokenization & Retirement](#carbon-credit-tokenization--retirement)
   - [Green Validator Scoring Index (EEI)](#green-validator-scoring-index-eei)
   - [Satellite-Verified Reforestation Logging](#satellite-verified-reforestation-logging)
   - [Micro-Gas Fee Offset Routing](#micro-gas-fee-offset-routing)
10. [Network Information](#10-network-information)
    - [Current Network State](#current-network-state)
    - [Official Endpoints & Resources Summary](#official-endpoints--resources-summary)

---

## 1. Quick Start

Verdis is a high-performance, carbon-negative Substrate Layer-1 blockchain operating under a Green Delegated Proof of Stake (Green DPoS) consensus protocol.

### Network Parameters & Connection Details

| Parameter | Primary Value | Fallback / Alternative | Notes |
| :--- | :--- | :--- | :--- |
| **HTTP JSON-RPC** | `https://verdischain.com/rpc` | `https://rpc.verdischain.com` | Primary HTTP JSON-RPC 2.0 interface |
| **WebSocket RPC** | `wss://ws.verdischain.com` | `wss://verdischain.com/ws` | Real-time event streaming & subscriptions |
| **Chain ID** | `909` | `0x038d` | Network identifier |
| **SS58 Address Format** | `909` | N/A | Verdis native SS58 address prefix |
| **Native Token Symbol** | `VRDX` | `VRS` (legacy) | Native gas and governance asset |
| **Token Decimals** | `9` | N/A | 1 VRDX = 1,000,000,000 Planck (base units) |
| **Block Time** | `6 seconds` | N/A | Target BABE slot time |
| **Runtime Version** | `Spec v10` | Runtime 2.0.0 | Latest mainnet runtime specification |

---

### Connecting via Polkadot.js API

The `@polkadot/api` library provides a type-safe JavaScript/TypeScript interface for interacting with Verdis node RPCs, submitting extrinsics, and querying storage.

#### Installation
```bash
npm install @polkadot/api @polkadot/keyring @polkadot/util-crypto
```

#### TypeScript Connection Example
```typescript
import { ApiPromise, WsProvider } from '@polkadot/api';

async function connectToVerdis() {
  // Initialize WebSocket provider
  const wsProvider = new WsProvider('wss://ws.verdischain.com');

  // Connect to the node
  const api = await ApiPromise.create({ 
    provider: wsProvider,
    // Custom SS58 prefix for Verdis addresses
    userExtensions: {}
  });

  await api.isReady;

  // Retrieve basic chain metadata
  const [chain, nodeName, nodeVersion, runtimeVersion] = await Promise.all([
    api.rpc.system.chain(),
    api.rpc.system.name(),
    api.rpc.system.version(),
    api.rpc.state.getRuntimeVersion()
  ]);

  console.log(`Connected to chain: ${chain} using ${nodeName} v${nodeVersion}`);
  console.log(`Spec Version: ${runtimeVersion.specVersion.toNumber()}`);

  return api;
}

connectToVerdis().catch(console.error);
```

---

### Connecting via Web3.js / Raw JSON-RPC

Verdis nodes accept standard JSON-RPC 2.0 HTTP POST requests on `https://verdischain.com/rpc` or `https://rpc.verdischain.com`.

#### cURL Request Example
```bash
curl -X POST https://verdischain.com/rpc \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "system_properties",
    "params": [],
    "id": 1
  }'
```

#### Expected JSON Response
```json
{
  "jsonrpc": "2.0",
  "result": {
    "ss58Format": 909,
    "tokenDecimals": 9,
    "tokenSymbol": "VRDX"
  },
  "id": 1
}
```

#### JavaScript `fetch` Example
```javascript
async function callVerdisRpc(method, params = []) {
  const response = await fetch('https://verdischain.com/rpc', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      jsonrpc: '2.0',
      id: Date.now(),
      method,
      params
    })
  });

  const data = await response.json();
  if (data.error) {
    throw new Error(`RPC Error (${data.error.code}): ${data.error.message}`);
  }
  return data.result;
}

// Example usage
callVerdisRpc('chain_getBlockHash', [0]).then(genesisHash => {
  console.log('Genesis Block Hash:', genesisHash);
});
```

---

### Connecting via WebSockets

Use raw WebSockets to listen to new block headers and state notifications in real-time.

```javascript
const WebSocket = require('ws');

const ws = new WebSocket('wss://ws.verdischain.com');

ws.on('open', () => {
  console.log('Connected to Verdis WebSocket endpoint');
  
  // Subscribe to new block headers
  ws.send(JSON.stringify({
    jsonrpc: '2.0',
    id: 1,
    method: 'chain_subscribeNewHeads',
    params: []
  }));
});

ws.on('message', (data) => {
  const response = JSON.parse(data);
  if (response.method === 'chain_newHead') {
    const header = response.params.result;
    console.log(`New Block #${parseInt(header.number, 16)} Hash: ${header.stateRoot}`);
  }
});
```

---

## 2. RPC API Reference

Verdis exposes 121 JSON-RPC methods categorized by runtime system responsibility. Below are the key methods grouped by core category.

### Chain RPCs

Handles block queries, block hashes, and finality status.

#### 1. `chain_getBlock`
- **Description:** Returns the header and extrinsics array for a specified block hash.
- **Parameters:** `[blockHash?: string]` (Optional. If omitted, returns current head block).
- **Return Type:** `Object` (`{ block: { header: {...}, extrinsics: [...] }, justifications: [...] }`)
- **Example Call:**
  ```json
  {
    "jsonrpc": "2.0",
    "method": "chain_getBlock",
    "params": ["0x9f28d..."],
    "id": 1
  }
  ```

#### 2. `chain_getBlockHash`
- **Description:** Get block hash for a given block height number.
- **Parameters:** `[blockNumber?: number]` (Optional. Height integer).
- **Return Type:** `String` (32-byte hex string representing block hash).
- **Example Call:**
  ```json
  {
    "jsonrpc": "2.0",
    "method": "chain_getBlockHash",
    "params": [104500],
    "id": 1
  }
  ```

#### 3. `chain_getFinalizedHead`
- **Description:** Get block hash of the latest finalized block header agreed upon by GRANDPA consensus.
- **Parameters:** `[]`
- **Return Type:** `String` (Block hash string).
- **Example Call:**
  ```json
  {
    "jsonrpc": "2.0",
    "method": "chain_getFinalizedHead",
    "params": [],
    "id": 1
  }
  ```

---

### State RPCs

Reads state storage items, storage hashes, and full runtime metadata.

#### 1. `state_getStorage`
- **Description:** Returns raw hex-encoded value stored under a specific state storage key.
- **Parameters:** `[key: string, blockHash?: string]`
- **Return Type:** `String` (HEX encoded storage data or `null`).
- **Example Call:**
  ```json
  {
    "jsonrpc": "2.0",
    "method": "state_getStorage",
    "params": ["0x26aa394bea01e72be357804854025432..."],
    "id": 1
  }
  ```

#### 2. `state_getStorageHash`
- **Description:** Returns the Blake2b 256-bit hash of a storage value at a given storage key.
- **Parameters:** `[key: string, blockHash?: string]`
- **Return Type:** `String` (Hex string of storage hash).
- **Example Call:**
  ```json
  {
    "jsonrpc": "2.0",
    "method": "state_getStorageHash",
    "params": ["0x26aa394bea01e..."],
    "id": 1
  }
  ```

#### 3. `state_getMetadata`
- **Description:** Returns the SCALE-encoded runtime metadata containing all pallets, calls, events, storage definitions, and types.
- **Parameters:** `[blockHash?: string]`
- **Return Type:** `String` (HEX string of SCALE metadata).
- **Example Call:**
  ```json
  {
    "jsonrpc": "2.0",
    "method": "state_getMetadata",
    "params": [],
    "id": 1
  }
  ```

---

### System RPCs

Inspects node synchronization status, network properties, and software build specs.

#### 1. `system_health`
- **Description:** Returns health statistics of the node including connected peer count and syncing status.
- **Parameters:** `[]`
- **Return Type:** `Object` (`{ isSyncing: boolean, peers: number, shouldHavePeers: boolean }`)
- **Example Result:**
  ```json
  {
    "jsonrpc": "2.0",
    "result": { "isSyncing": false, "peers": 32, "shouldHavePeers": true },
    "id": 1
  }
  ```

#### 2. `system_properties`
- **Description:** Retrieves chain properties configured in the chain spec.
- **Parameters:** `[]`
- **Return Type:** `Object` (`{ ss58Format: 909, tokenDecimals: 9, tokenSymbol: "VRDX" }`)

#### 3. `system_runtimeVersion`
- **Description:** Returns current WASM runtime version information.
- **Parameters:** `[blockHash?: string]`
- **Return Type:** `Object` (`{ specName: "verdis", specVersion: 10, implVersion: 2, authoringVersion: 1 }`)

---

### DPoS Staking RPCs

Custom RPC methods for querying Green DPoS validator candidates, stake allocations, and active election epochs.

#### 1. `dpos_activeValidators`
- **Description:** Returns the list of SS58 account addresses of currently active consensus block producers.
- **Parameters:** `[]`
- **Return Type:** `Array<string>`
- **Example Result:**
  ```json
  {
    "jsonrpc": "2.0",
    "result": [
      "5GrwvaEF5zXb26Fz9rcQpDWS5CTERHpNehXCPcNoHGKutQY",
      "5FHneW46xGXzc5m2b5W7NqsZF8T4C9ni4a2hKw6J55256657"
    ],
    "id": 1
  }
  ```

#### 2. `dpos_allValidators`
- **Description:** Returns all registered validator candidates eligible for selection in the next epoch.
- **Parameters:** `[]`
- **Return Type:** `Array<Object>` (`[{ accountId: string, commission: number, greenScore: number }]`)

#### 3. `dpos_validatorStake`
- **Description:** Returns detailed breakdown of self-staked tokens, delegated tokens, and total backing for a validator address.
- **Parameters:** `[validatorAccountId: string]`
- **Return Type:** `Object` (`{ selfStake: string, delegatedStake: string, totalStake: string, delegatorsCount: number }`)

#### 4. `dpos_currentEpoch`
- **Description:** Query current DPoS epoch index, starting block, slot index, and blocks remaining in current session.
- **Parameters:** `[]`
- **Return Type:** `Object` (`{ epochIndex: number, startBlock: number, currentSlot: number, blocksRemaining: number }`)

---

### AMM DEX RPCs

Methods for interacting with the native automated market maker liquidity pools and asset prices.

#### 1. `amm_dex_getAllPools`
- **Description:** Lists all deployed liquidity pools on the native AMM DEX.
- **Parameters:** `[]`
- **Return Type:** `Array<Object>` (`[{ poolId: string, tokenA: string, tokenB: string, reserveA: string, reserveB: string, totalLpSupply: string }]`)

#### 2. `amm_dex_getPool`
- **Description:** Retrieve liquidity reserves, fee tiers, and token metadata for a specific asset pair.
- **Parameters:** `[assetA: number|string, assetB: number|string]`
- **Return Type:** `Object` (`{ poolId: string, reserveA: string, reserveB: string, feeBps: number, treeFeeBps: number }`)

#### 3. `amm_dex_getPrice`
- **Description:** Returns the estimated output amount and price impact for swapping `amountIn` of `assetA` into `assetB`.
- **Parameters:** `[assetA: number|string, assetB: number|string, amountIn: string]`
- **Return Type:** `Object` (`{ amountOut: string, priceImpactPct: number, treeOffsetContribution: string }`)

#### 4. `amm_dex_getLiquidity`
- **Description:** Query LP token balance and share percentage for an account address in a specified liquidity pool.
- **Parameters:** `[poolId: string, accountId: string]`
- **Return Type:** `Object` (`{ lpBalance: string, sharePct: number, tokenAAmount: string, tokenBAmount: string }`)

---

### Smart Contracts RPCs

Methods for WASM contract dry-running, gas calculation, and state queries.

#### 1. `contracts_call`
- **Description:** Dry-runs a WASM smart contract execution without persisting state changes. Used for state reads and gas estimation.
- **Parameters:** `[callRequest: Object, blockHash?: string]`
  - `callRequest`: `{ origin: string, dest: string, value: string, gasLimit: { refTime: string, proofSize: string }, storageDepositLimit: string|null, inputData: string }`
- **Return Type:** `Object` (`{ gasConsumed: {...}, gasRequired: {...}, storageDeposit: {...}, result: { Ok: { flags: number, data: string } } }`)

#### 2. `contracts_getStorage`
- **Description:** Directly fetches hex-encoded value stored at a contract's internal key slot.
- **Parameters:** `[contractAddress: string, storageKey: string]`
- **Return Type:** `String` (HEX storage bytes).

#### 3. `contracts_instantiate`
- **Description:** Dry-runs contract instantiation from uploaded WASM code hash to estimate required deployment weight and deposit.
- **Parameters:** `[instantiateRequest: Object]`
  - `instantiateRequest`: `{ origin: string, value: string, gasLimit: {...}, storageDepositLimit: string|null, codeHash: string, data: string, salt: string }`
- **Return Type:** `Object` (`{ result: {...}, gasConsumed: {...}, gasRequired: {...}, storageDeposit: {...} }`)

---

## 3. Smart Contracts

Verdis supports high-performance WebAssembly (WASM) smart contracts powered by `pallet_contracts`. Developers can write contracts in Rust using parity **ink!**.

### Overview of ink! WASM Smart Contracts

- **Execution Engine:** `pallet_contracts` sandbox.
- **Gas Model:** Two-dimensional Weight system consisting of:
  - `ref_time`: Computation CPU execution time in picoseconds.
  - `proof_size`: Memory and trie proof footprint in bytes.
- **Storage Deposit:** Rent model where accounts lock tokens based on state bytes consumed. Tokens are refunded when storage is freed.

---

### Writing & Compiling ink! Contracts

#### Example ink! Token Vault Contract (`lib.rs`)
```rust
#![cfg_attr(not(feature = "std"), no_std, no_main)]

#[ink::contract]
mod eco_vault {
    use ink::storage::Mapping;

    #[ink(storage)]
    pub struct EcoVault {
        owner: AccountId,
        balances: Mapping<AccountId, Balance>,
        total_staked: Balance,
    }

    #[ink(event)]
    pub meow_deposit {
        #[ink(topic)]
        from: AccountId,
        amount: Balance,
    }

    impl EcoVault {
        #[ink(constructor)]
        pub fn new() -> Self {
            Self {
                owner: Self::env().caller(),
                balances: Mapping::default(),
                total_staked: 0,
            }
        }

        #[ink(message, payable)]
        pub fn deposit(&mut self) {
            let caller = self.env().caller();
            let amount = self.env().transferred_value();
            let current = self.balances.get(caller).unwrap_or(0);
            
            self.balances.insert(caller, &(current + amount));
            self.total_staked += amount;

            self.env().emit_event(meow_deposit { from: caller, amount });
        }

        #[ink(message)]
        pub fn get_balance(&self, account: AccountId) -> Balance {
            self.balances.get(account).unwrap_or(0)
        }
    }
}
```

#### Compilation Process
```bash
# Install cargo-contract CLI
cargo install --force --locked cargo-contract

# Build WASM binary and metadata
cargo contract build --release
```
This produces three files in `target/ink/`:
1. `eco_vault.wasm` (Compiled WebAssembly code)
2. `metadata.json` (ABI definition)
3. `eco_vault.contract` (Combined bundle used for deployment)

---

### Deploying WASM Contracts

Deploying an ink! contract consists of two steps:
1. **Upload WASM Code (`contracts.uploadCode`):** Uploads the byte code to chain storage. Returns a unique 32-byte `codeHash`.
2. **Instantiate Contract (`contracts.instantiate` / `contracts.instantiateWithCode`):** Executes constructor and creates a unique contract SS58 address.

#### Deployment via Polkadot.js API
```typescript
import { ApiPromise, WsProvider, Keyring } from '@polkadot/api';
import { CodePromise } from '@polkadot/api-contract';
import * as fs from 'fs';

async function deployContract() {
  const wsProvider = new WsProvider('wss://ws.verdischain.com');
  const api = await ApiPromise.create({ provider: wsProvider });
  const keyring = new Keyring({ type: 'sr25519', ss58Format: 909 });
  const deployer = keyring.addFromUri('//Alice');

  const contractAbi = JSON.parse(fs.readFileSync('./target/ink/eco_vault.json', 'utf8'));
  const wasm = fs.readFileSync('./target/ink/eco_vault.wasm');

  const code = new CodePromise(api, contractAbi, wasm);

  // Set maximum gas limits (refTime & proofSize)
  const gasLimit = api.registry.createType('WeightV2', {
    refTime: 300000000000,
    proofSize: 1000000,
  });

  const tx = code.tx.new({ gasLimit, storageDepositLimit: null });

  const unsub = await tx.signAndSend(deployer, ({ status, contract }) => {
    if (status.isInBlock) {
      console.log(`Contract deployed at address: ${contract.address.toString()}`);
      unsub();
    }
  });
}
```

---

### Interacting with Deployed Contracts

#### 1. State Queries (Read-Only via `contracts_call`)
```typescript
import { ContractPromise } from '@polkadot/api-contract';

async function queryContract(api: ApiPromise, contractAddress: string, abi: any, userAccount: string) {
  const contract = new ContractPromise(api, abi, contractAddress);
  
  // Dry run read-only call
  const { result, output } = await contract.query.getBalance(
    userAccount,
    { gasLimit: -1, storageDepositLimit: null },
    userAccount
  );

  if (result.isOk) {
    console.log('User Vault Balance:', output?.toHuman());
  }
}
```

#### 2. Executing Transactions (State Mutation)
```typescript
async function executeDeposit(api: ApiPromise, contractAddress: string, abi: any, signer: any, amountPlanck: string) {
  const contract = new ContractPromise(api, abi, contractAddress);

  const gasLimit = api.registry.createType('WeightV2', {
    refTime: 100000000000,
    proofSize: 50000,
  });

  const tx = contract.tx.deposit({
    gasLimit,
    value: amountPlanck,
  });

  await tx.signAndSend(signer, ({ status, events }) => {
    if (status.isInBlock) {
      console.log(`Deposit tx included in block ${status.asInBlock.toHex()}`);
    }
  });
}
```

---

### Gas Estimation & Storage Deposit

To calculate accurate gas limits before transaction dispatch, invoke `contracts_call` RPC:

```typescript
async function estimateGas(api: ApiPromise, origin: string, dest: string, inputData: string) {
  const response = await api.rpc.contracts.call({
    origin,
    dest,
    value: 0,
    gasLimit: null,
    storageDepositLimit: null,
    inputData
  });

  console.log('Required RefTime:', response.gasRequired.refTime.toString());
  console.log('Required ProofSize:', response.gasRequired.proofSize.toString());
  console.log('Storage Deposit Needed:', response.storageDeposit.asCharge.toString());
}
```

---

## 4. Token Standards

Verdis provides two high-performance native token pallets: `pallet_fungible_tokens` (for custom fungible tokens) and `pallet_nfts` (for non-fungible collections).

### Fungible Tokens Pallet

Operates directly at the runtime layer with sub-millisecond execution fees.

#### Core Extrinsics Overview

| Extrinsic Method | Parameters | Description |
| :--- | :--- | :--- |
| `fungible_tokens.create` | `id: u32, admin: MultiAddress, min_balance: Balance` | Registers a new fungible token asset class |
| `fungible_tokens.mint` | `id: u32, beneficiary: MultiAddress, amount: Balance` | Mints new tokens (admin signature required) |
| `fungible_tokens.burn` | `id: u32, target: MultiAddress, amount: Balance` | Destroys tokens from an account balance |
| `fungible_tokens.transfer` | `id: u32, target: MultiAddress, amount: Balance` | Transfers token balance between accounts |
| `fungible_tokens.approve` | `id: u32, delegate: MultiAddress, amount: Balance` | Grants approval allowance for a delegate |

#### Example: Creating & Minting a Fungible Token
```typescript
// 1. Create Asset (ID: 100)
const createTx = api.tx.fungibleTokens.create(
  100, // Asset ID
  alice.address, // Admin
  1000000 // Minimum balance (existential deposit)
);
await createTx.signAndSend(alice);

// 2. Mint 1,000,000 Tokens to Bob
const mintTx = api.tx.fungibleTokens.mint(
  100,
  bob.address,
  "1000000000000000" // 1,000,000 tokens (with 9 decimals)
);
await mintTx.signAndSend(alice);
```

---

### NFTs Pallet

Designed for high-throughput digital assets, eco-credentials, and satellite reforestation certificates.

#### Core Extrinsics Overview

| Extrinsic Method | Parameters | Description |
| :--- | :--- | :--- |
| `nfts.create_collection` | `collection_id: u32, admin: MultiAddress, config: CollectionConfig` | Creates an NFT collection container |
| `nfts.mint_nft` | `collection_id: u32, item_id: u32, owner: MultiAddress, metadata: Vec<u8>` | Mints an individual NFT item |
| `nfts.transfer` | `collection_id: u32, item_id: u32, recipient: MultiAddress` | Transfers NFT ownership |

#### Example: Minting a Reforestation Certificate NFT
```typescript
const collectionId = 1;
const itemId = 42;
const metadataUrl = "https://ipfs.io/ipfs/QmEcoCertificateExampleHash";

const mintNftTx = api.tx.nfts.mintNft(
  collectionId,
  itemId,
  bob.address,
  Array.from(Buffer.from(metadataUrl))
);

await mintNftTx.signAndSend(alice);
```

---

## 5. DEX Integration

The Verdis AMM DEX (`pallet_amm_dex`) is an on-chain automated market maker utilizing constant product liquidity pools ($x \cdot y = k$).

### AMM DEX Architecture
- **Micro-Carbon Fee Model:** Every swap allocates a 0.3% total fee:
  - `0.25%`: Distributed directly to Liquidity Providers (LPs).
  - `0.05%`: Routed automatically to the **Green Treasury** smart contract to purchase verified carbon offsets and fund tree planting.

---

### Adding Liquidity

To provide liquidity to an active pair, call `amm_dex.add_liquidity`:

```typescript
async function addLiquidity(
  api: ApiPromise,
  signer: any,
  assetA: number, // 0 for VRDX
  assetB: number, // Token Asset ID
  amountADesired: string,
  amountBDesired: string
) {
  const tx = api.tx.ammDex.addLiquidity(
    assetA,
    assetB,
    amountADesired,
    amountBDesired,
    "0", // amountAMin (slippage bound)
    "0"  // amountBMin (slippage bound)
  );

  await tx.signAndSend(signer, ({ status }) => {
    if (status.isInBlock) {
      console.log('Liquidity added successfully');
    }
  });
}
```

---

### Removing Liquidity

Burn LP tokens to withdraw underlying pool reserves:

```typescript
const removeTx = api.tx.ammDex.removeLiquidity(
  assetA,
  assetB,
  lpTokenAmount, // Amount of LP tokens to burn
  amountAMin,    // Minimum Asset A expected
  amountBMin     // Minimum Asset B expected
);
await removeTx.signAndSend(signer);
```

---

### Swapping Tokens

Perform an instant automated token swap:

```typescript
async function swapExactTokens(
  api: ApiPromise,
  signer: any,
  assetIn: number,
  assetOut: number,
  amountIn: string,
  minAmountOut: string
) {
  const tx = api.tx.ammDex.swapExactTokensForTokens(
    amountIn,
    minAmountOut,
    [assetIn, assetOut], // Asset route path
    signer.address,
    Math.floor(Date.now() / 1000) + 600 // Deadline (10 mins)
  );

  await tx.signAndSend(signer, ({ status }) => {
    if (status.isInBlock) {
      console.log('Token swap confirmed in block');
    }
  });
}
```

---

### Fetching Prices & Reserves

Query live prices directly using custom RPC methods:

```typescript
// Fetch Pool Reserves
const pool = await callVerdisRpc('amm_dex_getPool', [0, 1]); // VRDX / CARBON
console.log('VRDX Reserve:', pool.reserveA);
console.log('CARBON Reserve:', pool.reserveB);

// Fetch Spot Price Quote for 100 VRDX
const priceQuote = await callVerdisRpc('amm_dex_getPrice', [0, 1, "100000000000"]);
console.log('Output CARBON Amount:', priceQuote.amountOut);
console.log('Estimated Price Impact:', `${priceQuote.priceImpactPct}%`);
```

---

## 6. Governance

Verdis features on-chain governance enabling VRDX token holders to propose upgrades, vote on referenda, and manage the Green Treasury.

### Governance Components Overview

```
+-------------------------------------------------------------------------+
|                       VERDIS ON-CHAIN GOVERNANCE                        |
+-------------------------------------------------------------------------+
|  1. Council            | 13 elected members governing fast-track motions|
|  2. Democracy          | Token-weighted public referenda & proposals    |
|  3. Green Treasury     | Autonomous fund financing ecological projects  |
+-------------------------------------------------------------------------+
```

---

### Council Proposals

The elected Verdis Council votes on administrative operations, runtime upgrades, and fast-track emergency proposals.

```typescript
// Propose a council motion
const motionTx = api.tx.council.propose(
  3, // Threshold of positive votes required
  proposalCall, // Encoded call frame
  proposalLength
);
await motionTx.signAndSend(councilMember);
```

---

### Democracy Referenda

Public proposals are submitted by locking VRDX tokens. Every 28 days, the most endorsed proposal turns into a public referendum.

1. **Submit Proposal Preimage:**
   ```typescript
   const notePreimageTx = api.tx.preimage.notePreimage(encodedProposalByteCode);
   await notePreimageTx.signAndSend(signer);
   ```
2. **Submit Public Proposal:**
   ```typescript
   const proposeTx = api.tx.democracy.propose(preimageHash, lockedValue);
   await proposeTx.signAndSend(signer);
   ```
3. **Vote on Active Referendum:**
   ```typescript
   const voteTx = api.tx.democracy.vote(
     refIndex,
     {
       Standard: {
         vote: { aye: true, conviction: 'Locked1x' },
         balance: "1000000000000" // 1,000 VRDX
       }
     }
   );
   await voteTx.signAndSend(signer);
   ```

---

### Treasury Proposals & Green Grants

Projects building eco-friendly protocols, satellite trackers, or green DApps can apply for VRDX funding from the Green Treasury.

```typescript
const treasuryProposalTx = api.tx.treasury.proposeSpend(
  requestedValue, // Requested VRDX amount in Planck
  beneficiaryAddress // Receiver account address
);
await treasuryProposalTx.signAndSend(applicantKeypair);
```

---

## 7. Staking

Verdis uses Green DPoS (Delegated Proof of Stake) consensus. Network security is maintained by active consensus validators supported by delegators.

### Staking Overview
- **Validator Capacity:** Maximum 101 active validators (currently 10 mainnet consensus nodes).
- **Session Duration:** 600 slots (~1 hour).
- **Unbonding Period:** 28 eras (~28 days).

---

### Registering as a Validator

To operate a validator node:
1. Spin up a full node with `--validator` flag.
2. Generate BABE and GRANDPA keys via `author_rotateKeys` RPC.
3. Bind session keys to account via `session.setKeys`.
4. Register candidate via `dpos_staking.register_validator`.

```typescript
// Set Session Keys
const setKeysTx = api.tx.session.setKeys(
  generatedRotateKeysHex, 
  "0x00" // Proof
);
await setKeysTx.signAndSend(validatorKeypair);

// Register Validator Candidate
const registerTx = api.tx.dposStaking.registerValidator(
  "1000000000000000", // Self stake (1,000,000 VRDX)
  500 // Commission in Basis Points (5.00%)
);
await registerTx.signAndSend(validatorKeypair);
```

---

### Delegating & Staking Tokens

VRDX holders can delegate stake to active validators to earn continuous epoch yields:

```typescript
const delegateTx = api.tx.dposStaking.delegateStake(
  targetValidatorAddress,
  "5000000000000" // Stake 5,000 VRDX
);
await delegateTx.signAndSend(delegatorKeypair);
```

---

### Unstaking & Unbonding

To initiate stake withdrawal:

```typescript
// Step 1: Initiate unbond request
const unbondTx = api.tx.dposStaking.unbond("5000000000000");
await unbondTx.signAndSend(delegatorKeypair);

// Step 2: After unbonding duration expires, withdraw unbonded funds
const withdrawTx = api.tx.dposStaking.withdrawUnbonded();
await withdrawTx.signAndSend(delegatorKeypair);
```

---

### Claiming Staking Rewards

Staking rewards are distributed at epoch boundaries. Claim rewards manually using `payout_stakers`:

```typescript
const payoutTx = api.tx.dposStaking.payoutStakers(
  validatorAddress,
  eraIndex
);
await payoutTx.signAndSend(anyUserKeypair);
```

---

## 8. SDK Examples

Complete JavaScript / TypeScript examples for common operations on Verdis.

### 1. Connect & Read Network Info

```typescript
import { ApiPromise, WsProvider } from '@polkadot/api';

async function main() {
  const provider = new WsProvider('wss://ws.verdischain.com');
  const api = await ApiPromise.create({ provider });

  const [header, activeVals, epoch] = await Promise.all([
    api.rpc.chain.getHeader(),
    api.rpc.dpos?.activeValidators ? api.rpc.dpos.activeValidators() : Promise.resolve([]),
    api.rpc.dpos?.currentEpoch ? api.rpc.dpos.currentEpoch() : Promise.resolve({})
  ]);

  console.log('Latest Block Number:', header.number.toNumber());
  console.log('Active Validators Count:', activeVals.length);
  console.log('Epoch Info:', epoch);

  await api.disconnect();
}

main().catch(console.error);
```

---

### 2. Transfer VRDX Native Tokens

```typescript
import { ApiPromise, WsProvider, Keyring } from '@polkadot/api';

async function transferVrdx() {
  const api = await ApiPromise.create({ provider: new WsProvider('wss://ws.verdischain.com') });
  const keyring = new Keyring({ type: 'sr25519', ss58Format: 909 });
  
  // Replace with secret seed
  const sender = keyring.addFromUri('//Alice');
  const recipient = '5FHneW46xGXzc5m2b5W7NqsZF8T4C9ni4a2hKw6J55256657';
  
  // Transfer 10.5 VRDX (10.5 * 10^9 Planck)
  const amountPlanck = "10500000000";

  const tx = api.tx.balances.transferKeepAlive(recipient, amountPlanck);

  // Estimate transaction fee
  const info = await tx.paymentInfo(sender);
  console.log(`Estimated Tx Fee: ${info.partialFee.toHuman()}`);

  // Send transaction
  const hash = await tx.signAndSend(sender);
  console.log(`Submitted Tx Hash: ${hash.toHex()}`);
}

transferVrdx().catch(console.error);
```

---

### 3. DEX Swap & Liquidity Integration

```typescript
import { ApiPromise, WsProvider, Keyring } from '@polkadot/api';

async function executeDexSwap() {
  const api = await ApiPromise.create({ provider: new WsProvider('wss://ws.verdischain.com') });
  const keyring = new Keyring({ type: 'sr25519', ss58Format: 909 });
  const trader = keyring.addFromUri('//Alice');

  const assetIn = 0; // VRDX
  const assetOut = 1; // CARBON Token
  const amountIn = "5000000000"; // 5 VRDX
  const minAmountOut = "4800000000"; // Minimum 4.8 CARBON

  const swapTx = api.tx.ammDex.swapExactTokensForTokens(
    amountIn,
    minAmountOut,
    [assetIn, assetOut],
    trader.address,
    Math.floor(Date.now() / 1000) + 300
  );

  const unsub = await swapTx.signAndSend(trader, ({ status, events }) => {
    if (status.isInBlock) {
      console.log(`Swap executed in block: ${status.asInBlock.toHex()}`);
      events.forEach(({ event: { method, section, data } }) => {
        console.log(`Event emitted: ${section}.${method} -> ${data.toString()}`);
      });
      unsub();
    }
  });
}

executeDexSwap().catch(console.error);
```

---

### 4. Dry-Run Contract Call

```typescript
async function dryRunContractCall() {
  const response = await fetch('https://verdischain.com/rpc', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      jsonrpc: '2.0',
      id: 1,
      method: 'contracts_call',
      params: [{
        origin: '5GrwvaEF5zXb26Fz9rcQpDWS5CTERHpNehXCPcNoHGKutQY',
        dest: '5C4hrfjw9DjXZTzV3MwzrrAr9P1MJhSrvWGWqi1YN8Cq3380',
        value: '0',
        gasLimit: { refTime: '10000000000', proofSize: '100000' },
        storageDepositLimit: null,
        inputData: '0x2f865bd9' // Encoded message selector
      }]
    })
  });

  const data = await response.json();
  console.log('Dry Run Result:', data.result);
}

dryRunContractCall();
```

---

### 5. Query Eco Carbon Offsets

```typescript
async function getEcoMetrics() {
  const response = await fetch('https://verdischain.com/rpc', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      jsonrpc: '2.0',
      id: 1,
      method: 'state_getStorage',
      params: ['0xEcoVerificationStorageKeyBytes']
    })
  });

  const result = await response.json();
  console.log('Raw Eco State Data:', result.result);
}

getEcoMetrics();
```

---

### 6. Subscribe to Live Events

```typescript
import { ApiPromise, WsProvider } from '@polkadot/api';

async function listenToEvents() {
  const api = await ApiPromise.create({ provider: new WsProvider('wss://ws.verdischain.com') });

  api.query.system.events((events) => {
    events.forEach((record) => {
      const { event, phase } = record;
      console.log(`\t${event.section}:${event.method}:: ${event.data}`);
    });
  });
}

listenToEvents().catch(console.error);
```

---

## 9. Eco Protocol

Verdis is built around a native **Proof of Eco** architecture that enforces carbon neutrality and integrates satellite-based environmental monitoring directly into the consensus layer.

```
+-----------------------------------------------------------------------------------+
|                            VERDIS ECO PROTOCOL MATRIX                             |
+-----------------------------------------------------------------------------------+
|  1. Energy Score (EEI)   | Real-time node energy efficiency scoring               |
|  2. Carbon Tokenization  | Verra & Gold Standard verified carbon credits         |
|  3. Satellite Reforest   | Earth Observation (Sentinel-2) canopy verification    |
|  4. Micro-Gas Offset     | 1% auto-deduction into Green Treasury smart contracts |
+-----------------------------------------------------------------------------------+
```

---

### Carbon Credit Tokenization & Retirement

Verdis natively tokenizes carbon credits directly via `pallet_eco_verification`.
- **Standards Supported:** Verra VCS and Gold Standard offset certificates.
- **On-Chain Retirement:** Carbon credit tokens can be permanently burned on-chain to generate non-transferable **Proof-of-Carbon-Offset Certificates** (issued as NFTs via `pallet_nfts`).

---

### Green Validator Scoring Index (EEI)

Validators operating on Verdis are continuously scored according to their **Energy Efficiency Index (EEI)**.
- **Metrics Tracked:**
  - Hardware PUE (Power Usage Effectiveness).
  - Energy Source Verification (100% Solar, Wind, or Hydro energy certificates).
  - On-chain Carbon Offset ratio.
- **Consensus Impact:** Validators with higher EEI scores receive up to a **15% bonus multiplier** on block reward distributions, incentivizing zero-carbon infrastructure.

---

### Satellite-Verified Reforestation Logging

The Verdis Eco Protocol ingests satellite telemetry feeds from Copernicus Sentinel-2 and NASA Landsat.
- **Canopy Verification:** Oracles transmit multispectral NDVI (Normalized Difference Vegetation Index) calculations directly on-chain.
- **Automated Disbursement:** Reforestation grants are automatically unlocked from the Green Treasury when satellite feeds confirm positive tree canopy expansion in designated reforestation zones.

---

### Micro-Gas Fee Offset Routing

Every transaction processed on the Verdis network contributes to carbon offsetting:
- **Automatic Split:** 1% of the gas fee for every transaction is routed directly into the **Green Treasury** smart contract (`5GreenTreasuryContractAddress...`).
- **Autonomous Offset Purchasing:** When accumulated funds reach preset thresholds, the contract automatically executes offset retirements via verified liquidity pools.

---

## 10. Network Information

### Current Network State

| Parameter | Value |
| :--- | :--- |
| **Runtime Specification** | Spec v10 (Runtime 2.0.0) |
| **Active FRAME Pallets** | 13 Pallets (`pallet_system`, `pallet_timestamp`, `pallet_babe`, `pallet_grandpa`, `pallet_balances`, `pallet_transaction_payment`, `pallet_contracts`, `pallet_dpos_staking`, `pallet_amm_dex`, `pallet_eco_verification`, `pallet_tokenomics`, `pallet_vesting`, `pallet_decentralized_storage`) |
| **Total RPC Methods** | 121 JSON-RPC & WebSocket methods |
| **Active Consensus Validators** | 10 Validators |
| **Active DEX Liquidity Pools** | 6 Pools (`VRDX/CARBON`, `VRDX/USDC`, `VRDX/ETH`, `CARBON/USDC`, `VRDX/ECO`, `REFOREST/VRDX`) |
| **Target Block Duration** | 6 Seconds |
| **Finality Time** | Sub-second GRANDPA determinism |
| **Consensus Mechanism** | Green DPoS (BABE + GRANDPA) |

---

### Official Endpoints & Resources Summary

| Resource | URL / Details |
| :--- | :--- |
| **HTTP RPC Endpoint (Primary)** | `https://verdischain.com/rpc` |
| **HTTP RPC Endpoint (Alternate)** | `https://rpc.verdischain.com` |
| **WebSocket RPC Endpoint** | `wss://ws.verdischain.com` |
| **Block Explorer** | `https://verdischain.com/explorer` |
| **Developer Portal** | `https://verdischain.com/developers` |
| **Native Faucet** | `https://verdischain.com/faucet` |
| **AMM DEX Interface** | `https://verdischain.com/dex` |
| **Chain ID** | `909` |
| **SS58 Address Format** | `909` |
| **Token Identifier** | `VRDX` (9 Decimals) |

---
