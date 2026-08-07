# Verdis Chain JSON-RPC & WebSocket API Specification

This document provides a full technical reference for the **Verdis Chain v2.0.0** JSON-RPC and WebSocket API endpoints.

---

## 1. Network Endpoint Details & Connection Parameters

| Parameter | Value | Notes |
| :--- | :--- | :--- |
| **HTTP JSON-RPC Endpoint** | `https://verdischain.com/rpc` | Proxied via Nginx to local port `9944` |
| **Dedicated RPC Domain** | `https://rpc.verdischain.com` | Directly routes to JSON-RPC interface |
| **WebSocket Endpoint** | `wss://verdischain.com/ws` | Full duplex real-time event streaming |
| **Direct Host Backend** | `http://127.0.0.1:9944` | Bound strictly to `localhost` on the node server |
| **Rate Limit** | `30 requests/sec` per IP | Enforced by Nginx `limit_req` directive |
| **RPC Method Filter** | `--rpc-methods Safe` | Unsafe administrative RPCs disabled on public proxy |
| **CORS Restriction** | `verdischain.com` | Strict origin controls applied |

---

## 2. Security & Policy Rules

### CORS Configuration
Nginx enforces strict CORS controls for browser clients:
```nginx
add_header Access-Control-Allow-Origin "https://verdischain.com" always;
add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
add_header Access-Control-Allow-Headers "Content-Type, Authorization" always;
if ($request_method = OPTIONS) { return 204; }
```

### Rate Limiting Enforcement
All incoming API traffic is subjected to Nginx rate limiting rules:
```nginx
limit_req_zone $binary_remote_addr zone=rpc_limit:10m rate=30r/s;
limit_req zone=rpc_limit burst=20 nodelay;
```

### Safe RPC Method Policy
When starting the node with `--rpc-methods Safe`, administrative RPC calls capable of mutating node state, local keys, or peer tables over remote HTTP are restricted.
* **Blocked/Forbidden Unsafe RPC Methods over Public Proxy:**
  * `author_insertKey` (Disabled over public HTTP/WS; only accessible via local SSH socket)
  * `system_addReservedPeer` / `system_removeReservedPeer`
  * `system_nodeRoles`
  * `offchain_localStorageSet` / `offchain_localStorageGet`

---

## 3. JSON-RPC API Reference

### 3.1. Chain Namespace (`chain_*`)

Provides access to blocks, block headers, hash pointers, and state roots.

#### `chain_getBlock`
Returns the full block structure for a given block hash (or latest if omitted).
* **Parameters:** `[blockHash?: string]`
* **Request Example:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "chain_getBlock",
  "params": ["0x9c3d4f1e5a8b7c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d"]
}
```
* **Response Example:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "block": {
      "header": {
        "parentHash": "0x1111111111111111111111111111111111111111111111111111111111111111",
        "number": "0x12d4",
        "stateRoot": "0xaabbccdd11223344556677889900aabbccdd11223344556677889900aabbccdd",
        "extrinsicsRoot": "0x9988776655443322110099887766554433221100998877665544332211009988",
        "digest": {
          "logs": ["0x06616263..."]
        }
      },
      "extrinsics": [
        "0x280403000b9049758f01"
      ]
    },
    "justifications": null
  }
}
```

#### `chain_getHeader`
Retrieves header metadata for a specific block.
* **Parameters:** `[blockHash?: string]`

#### `chain_getBlockHash`
Returns the block hash for a specified block height.
* **Parameters:** `[blockNumber: number]`
* **Request Example:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "chain_getBlockHash",
  "params": [4820]
}
```

#### `chain_getFinalizedHead`
Returns the hash of the latest finalized block verified by GRANDPA.
* **Parameters:** `[]`
* **Response Example:**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": "0x8f2a9b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a"
}
```

---

### 3.2. State Namespace (`state_*`)

Provides access to storage keys, runtime metadata, and state queries.

#### `state_getStorage`
Reads raw storage values from the Merkle trie at a specific storage key.
* **Parameters:** `[storageKey: string, blockHash?: string]`

#### `state_getRuntimeVersion`
Returns runtime version details (`specName`, `specVersion`, `authoringVersion`).
* **Parameters:** `[]`
* **Response Example:**
```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "result": {
    "specName": "verdis-runtime",
    "implName": "verdis-node",
    "authoringVersion": 1,
    "specVersion": 200,
    "implVersion": 1,
    "apis": [
      ["0xdf6acb6899dd0ed9", 3],
      ["0x37e39704e09f120e", 1]
    ],
    "transactionVersion": 1,
    "stateVersion": 1
  }
}
```

#### `state_getMetadata`
Retrieves compiled scale-encoded metadata blob defining all 17 pallets.
* **Parameters:** `[]`

---

### 3.3. System Namespace (`system_*`)

Provides node identity, health, peer status, and system properties.

#### `system_name`
Returns node soft client name (e.g., `"Verdis Node"`).

#### `system_version`
Returns host binary version string (e.g., `"2.0.0-a8c1f9e"`).

#### `system_chain`
Returns chain specification name (e.g., `"Verdis Mainnet"`).

#### `system_health`
Returns node health metrics (isSyncing, peers, shouldHavePeers).
* **Parameters:** `[]`
* **Response Example:**
```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "result": {
    "peers": 42,
    "isSyncing": false,
    "shouldHavePeers": true
  }
}
```

#### `system_properties`
Returns chain symbol, decimals, and SS58 network prefix.
* **Response Example:**
```json
{
  "jsonrpc": "2.0",
  "id": 6,
  "result": {
    "ss58Format": 909,
    "tokenDecimals": 9,
    "tokenSymbol": "VRDX"
  }
}
```

---

### 3.4. Author Namespace (`author_*`)

Handles submitting extrinsics and local validator key operations.

#### `author_submitExtrinsic`
Submits a hex-encoded signed extrinsic transaction to the tx pool.
* **Parameters:** `[extrinsicHex: string]`
* **Request Example:**
```json
{
  "jsonrpc": "2.0",
  "id": 7,
  "method": "author_submitExtrinsic",
  "params": ["0x450284005d45..."]
}
```
* **Response Example:**
```json
{
  "jsonrpc": "2.0",
  "id": 7,
  "result": "0x7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b"
}
```

#### `author_pendingExtrinsics`
Lists pending unbaked transactions in the transaction pool.

#### `author_rotateKeys`
Generates a new session key tuple in the node local keystore and returns the concatenated hex payload. Used during validator onboarding.
* **Parameters:** `[]` *(Requires localhost access or local admin RPC)*
* **Response Example:**
```json
{
  "jsonrpc": "2.0",
  "id": 8,
  "result": "0x9c3d4f1e5a8b7c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d"
}
```

#### `author_hasSessionKeys`
Verifies whether the node possesses private key material for a given session key tuple.
* **Parameters:** `[sessionKeysHex: string]`

---

### 3.5. RPC Namespace (`rpc_*`)

#### `rpc_methods`
Returns list of all available JSON-RPC methods enabled on the target node.
* **Response Example:**
```json
{
  "jsonrpc": "2.0",
  "id": 9,
  "result": {
    "methods": [
      "author_pendingExtrinsics",
      "author_submitAndWatchExtrinsic",
      "author_submitExtrinsic",
      "babe_epochAuthorship",
      "chain_getBlock",
      "chain_getBlockHash",
      "chain_getFinalizedHead",
      "chain_getHeader",
      "chain_subscribeFinalizedHeads",
      "chain_subscribeNewHeads",
      "grandpa_proveFinality",
      "rpc_methods",
      "state_getMetadata",
      "state_getRuntimeVersion",
      "state_getStorage",
      "system_chain",
      "system_health",
      "system_name",
      "system_properties",
      "system_version"
    ]
  }
}
```

---

### 3.6. Consensus Namespaces (`babe_*` & `grandpa_*`)

#### `babe_epochAuthorship`
Retrieves slot assignments and expected block authoring slots for active validators during the current epoch.

#### `grandpa_proveFinality`
Returns cryptographic justification proofs verifying block finality under GRANDPA.

---

## 4. WebSocket Subscriptions

Client applications establish subscriptions over `wss://verdischain.com/ws`.

### Subscription Workflow Example: `chain_subscribeNewHeads`

1. **Client Sends Subscription Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 10,
  "method": "chain_subscribeNewHeads",
  "params": []
}
```

2. **Server Responds with Subscription ID:**
```json
{
  "jsonrpc": "2.0",
  "id": 10,
  "result": "sub_abc123xyz"
}
```

3. **Server Streams Real-Time Header Notifications:**
```json
{
  "jsonrpc": "2.0",
  "method": "chain_newHead",
  "params": {
    "subscription": "sub_abc123xyz",
    "result": {
      "parentHash": "0x8f2a9b...",
      "number": "0x12d5",
      "stateRoot": "0x3c4d5e...",
      "extrinsicsRoot": "0x1a2b3c..."
    }
  }
}
```

### Supported WebSockets Subscriptions List
* `chain_subscribeNewHeads` / `chain_unsubscribeNewHeads`
* `chain_subscribeFinalizedHeads` / `chain_unsubscribeFinalizedHeads`
* `author_submitAndWatchExtrinsic` (Streams transaction status: `ready` -> `inBlock` -> `finalized`)
* `state_subscribeStorage` (Streams state updates for selected trie keys)
