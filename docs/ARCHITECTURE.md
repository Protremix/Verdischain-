# Verdis Blockchain Architecture Overview

This document provides a comprehensive technical breakdown of the **Verdis Chain v2.0.0** system architecture. Verdis Chain is an eco-friendly, enterprise-grade Layer-1 blockchain built with Rust and the Substrate framework. It delivers high throughput, deterministic finality, native eco-metrics tracking, WASM smart contract execution, and integrated decentralized financial primitive tools.

---

## 1. Executive System Summary

| Parameter / Feature | Specification |
| :--- | :--- |
| **Blockchain Version** | Verdis Chain v2.0.0 |
| **Core Framework** | Rust + Substrate SDK |
| **Consensus Engine** | BABE (Block Authoring) + GRANDPA (Finality Gadget) |
| **Native Token** | VRS (9 decimals, SS58 Format Prefix `909`) |
| **Total Supply** | 100,000,000,000 VRS (100 Billion) |
| **Chain ID** | `909` |
| **Target Block Time** | 6 seconds |
| **Epoch Duration** | 600 slots (1 hour target block time duration) |
| **Session Period** | 600 blocks |
| **Validator Count** | Up to 101 active validators (DPoS mechanism) |
| **Smart Contract VM** | WASM via `pallet-contracts` |
| **P2P Networking** | `libp2p` (Default Port: `30333`) |
| **RPC Interface** | JSON-RPC over HTTP (`/rpc`) & WebSockets (`/ws`) via Nginx (Port `9944` backend) |
| **Explorer** | Verdiscan (`https://verdischain.com`) |
| **Web Wallet** | `https://verdischain.com/wallet.html` |
| **Android Wallet** | Release APK served at `/verdis-wallet-release.apk` |

---

## 2. High-Level Architecture Diagram

```
+-----------------------------------------------------------------------------------+
|                                  CLIENT LAYER                                     |
|  +---------------------------+  +--------------------------+  +----------------+  |
|  | Verdiscan Web Explorer    |  | Web Wallet               |  | Android Wallet |  |
|  | (https://verdischain.com) |  | (.../wallet.html)        |  | (Native APK)   |  |
|  +---------------------------+  +--------------------------+  +----------------+  |
+---------------------------------------+-------------------------------------------+
                                        | HTTPS / WSS (Port 443 / SSL)
                                        v
+-----------------------------------------------------------------------------------+
|                             EDGE & SECURITY LAYER                                 |
|  +-----------------------------------------------------------------------------+  |
|  | Nginx Reverse Proxy (Server IP: 91.98.160.145)                             |  |
|  |  - Rate Limiting: 30 req/sec per IP                                        |  |
|  |  - TLS / SSL Termination (Let's Encrypt / HSTS enabled)                   |  |
|  |  - Strict CORS Policy: Whitelisted to verdischain.com                       |  |
|  |  - Endpoints: /rpc -> 127.0.0.1:9944, /ws -> 127.0.0.1:9944                 |  |
|  +-----------------------------------------------------------------------------+  |
|  +-----------------------------------------------------------------------------+  |
|  | UFW Firewall Enforcement                                                    |  |
|  |  - Open Ports: 22 (SSH), 80 (HTTP), 443 (HTTPS), 30333 (P2P Libp2p)          |  |
|  |  - Blocked: Direct external access to 9944 (RPC bound to localhost)         |  |
|  +-----------------------------------------------------------------------------+  |
+---------------------------------------+-------------------------------------------+
                                        | Localhost JSON-RPC / WS (Port 9944)
                                        v
+-----------------------------------------------------------------------------------+
|                            VERDIS NODE HOST ENGINE                                |
|  +----------------------------+  +---------------------+  +--------------------+  |
|  | Transaction Pool Engine    |  | JSON-RPC Server     |  | Offchain Workers   |  |
|  | (Prioritization / Queue)   |  | (Safe RPC Filter)   |  | (Async Tasks/HTTP) |  |
|  +----------------------------+  +---------------------+  +--------------------+  |
|  +-----------------------------------------------------------------------------+  |
|  | Consensus Engine: BABE Slot Clock & GRANDPA Finality Voter                 |  |
|  +-----------------------------------------------------------------------------+  |
|  +-----------------------------------------------------------------------------+  |
|  | P2P Networking Engine: libp2p (Port 30333, Kademlia DHT, Peer Discovery)   |  |
|  +-----------------------------------------------------------------------------+  |
+---------------------------------------+-------------------------------------------+
                                        | Execution Engine Calls (WASM Runtime API)
                                        v
+-----------------------------------------------------------------------------------+
|                             VERDIS RUNTIME (WASM)                                 |
|  +-----------------------------------------------------------------------------+  |
|  | Runtime Executive & Pallet Dispatcher                                       |  |
|  +-----------------------------------------------------------------------------+  |
|  | 17 CORE PALLETS:                                                            |  |
|  | [System] [Timestamp] [BABE] [GRANDPA] [Session] [Balances]                   |  |
|  | [TransactionPayment] [Sudo] [Scheduler] [Preimage] [Contracts]              |  |
|  | [DPoS] [AMM-DEX] [Eco] [Tokenomics] [Vesting] [Storage]                     |  |
|  +-----------------------------------------------------------------------------+  |
+---------------------------------------+-------------------------------------------+
                                        | State Reads & Key-Value Writes
                                        v
+-----------------------------------------------------------------------------------+
|                              STORAGE LAYER                                        |
|  +---------------------------------------+  +----------------------------------+  |
|  | RocksDB / ParityDB Trie Storage       |  | Keystore Engine                  |  |
|  | (Merkle Patricia State Trie + Data)   |  | (BABE, GRANDPA, Session Keys)    |  |
|  +---------------------------------------+  +----------------------------------+  |
+-----------------------------------------------------------------------------------+
```

---

## 3. Node & Execution Architecture

Verdis Chain splits system execution into two primary components:
1. **Substrate Host (Outer Node Executable):** Compiled native binary responsible for disk I/O, database interactions, P2P networking, transaction pool management, and consensus scheduling.
2. **Runtime Engine (WASM Core):** Compiled WebAssembly blob stored on-chain that defines state transition logic, balance updates, governance rules, smart contracts, and pallet logic.

```
                  +-----------------------------------+
                  |        Extrinsic / Tx Request     |
                  +-----------------+-----------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
| Substrate Host Outer Node                                             |
|                                                                       |
|   +---------------------+        +--------------------------------+   |
|   |  Transaction Pool   |------->|  TaggedTransactionQueue API   |   |
|   +---------------------+        +---------------+----------------+   |
|                                                  |                    |
|                                                  v                    |
|   +---------------------------------------------------------------+   |
|   |                      WASM Execution Environment               |   |
|   |  +---------------------------------------------------------+  |   |
|   |  | Executable Runtime (WASM Blob in On-Chain State Trie)  |  |   |
|   |  |                                                         |  |   |
|   |  |  Executive Module -> Frame Pallet Dispatcher            |  |   |
|   |  |   |---> System               |---> Contracts (WASM)    |  |   |
|   |  |   |---> Balances             |---> DPoS Staking        |  |   |
|   |  |   |---> TransactionPayment   |---> AMM-DEX             |  |   |
|   |  |   |---> BABE / GRANDPA       |---> Eco Pallet          |  |   |
|   |  +---------------------------------------------------------+  |   |
|   +------------------------------+--------------------------------+   |
|                                  |                                    |
+----------------------------------|------------------------------------+
                                   v
             +--------------------------------------------+
             | State Changes Written to RocksDB / Trie DB |
             +--------------------------------------------+
```

### Key Execution Benefits
* **Forkless Runtime Upgrades:** The entire runtime logic can be upgraded dynamically by submitting a `system.setCode` extrinsic authorized via governance or `sudo`. Nodes execute the new WASM code immediately upon block enactment without hard-forking the underlying P2P host binary.
* **Deterministic Sandboxing:** The WASM environment ensures that execution cannot access host operating system resources directly, enforcing zero non-determinism across node operators globally.

---

## 4. Consensus & Finality Engine

Verdis Chain uses a hybrid consensus model separating block production from finality guarantees:

```
                       BABE Block Production (Probabilistic)
      +--------+        +--------+        +--------+        +--------+
      | Block1 |------->| Block2 |------->| Block3 |------->| Block4 |
      +--------+        +--------+        +--------+        +--------+
          |                                   |
          +-----------------------------------+
                            |
                            v
              GRANDPA Finality Gadget (Deterministic)
          [Validates Chain Branch -> Finalizes Block 3]
```

### BABE (Blind Assignment for Blockchain Extensions)
* **Role:** Primary block authoring mechanism.
* **Mechanism:** Uses a Verifiable Random Function (VRF) to assign block authoring slots to validators deterministically but secretly in advance.
* **Slot Duration:** 6 seconds per block slot.
* **Epoch Period:** 600 slots (~1 hour). At the start of each epoch, BABE calculates the active validator set and slot assignments based on DPoS stake weights.

### GRANDPA (GHOST-based Recursive Ancestor Deriving Prefix Agreement)
* **Role:** Finality gadget providing instant, deterministic, non-revertible finality.
* **Mechanism:** Operates independently from block authoring. GRANDPA validators vote on chain heads rather than individual blocks, allowing the engine to finalize hundreds of blocks simultaneously when a 2/3+ Supermajority consensus is reached.

---

## 5. Storage Architecture

Verdis state storage utilizes an optimized key-value database schema built over a **Merkle Patricia Trie**:

```
                              State Root Hash
                                    /  \
                                   /    \
                              Node A    Node B
                               / \        / \
                            P1   P2     P3   P4
                            |    |      |    |
                      Balances  DPoS   Eco  Contracts
```

### Key Components
1. **Key-Value Store:** RocksDB or ParityDB engines store raw key-value state entries.
2. **State Pruning:** 
   * **Archive Mode:** Retains state tries for all historical blocks (used for Verdiscan explorer indexed RPC nodes).
   * **Full / Pruned Mode:** Retains state tries only for recent blocks (default 256 blocks) + state trie root for finalized blocks to conserve disk space.
3. **Keystore:** Local node keystore storing hot keys:
   * BABE Key (`sr25519`)
   * GRANDPA Key (`ed25519`)
   * ImOnline Key (`sr25519`)

---

## 6. Networking & P2P Protocols

Network communications run on **libp2p** on port `30333`.

```
                  +----------------------------------------+
                  |           libp2p Transport             |
                  |          TCP / Noise Encryption        |
                  +-------------------+--------------------+
                                      |
       +------------------------------+------------------------------+
       |                              |                              |
       v                              v                              v
+------------------+        +------------------+        +------------------+
| Kademlia DHT     |        | Block Syncing    |        | Gossip Protocol  |
| Peer Discovery   |        | Header & Body    |        | Extrinsic & Consensus|
| & Address Table  |        | Download Engine  |        | Propagation      |
+------------------+        +------------------+        +------------------+
```

### Protocols Supported
* **Peer Discovery:** Kademlia Distributed Hash Table (DHT) & Bootstrap nodes list.
* **Security & Transport:** Encrypted Noise streams over TCP/IP.
* **Gossip Subsystems:**
  * Substrate Block Announcements.
  * Transaction propagation (`author_submitExtrinsic`).
  * GRANDPA voting & finality round messages.

---

## 7. Security, Ingress & Gateway Layer

All external public traffic interacts through a hardened edge layer running on IP `91.98.160.145`:

```
Public Request (Client / Browser / Android Wallet)
                      |
                      v
            [ UFW Firewall ]
   Allows: 22, 80, 443, 30333
                      |
                      v
      [ Nginx Edge Proxy (verdischain.com) ]
   - Rate limit: 30 requests/sec per IP
   - CORS restriction: Whitelisted domains
   - SSL/TLS Termination (Let's Encrypt / HSTS)
   - Forwarding Rules:
       https://verdischain.com/rpc -> http://127.0.0.1:9944
       wss://verdischain.com/ws   -> ws://127.0.0.1:9944
                      |
                      v
  [ Substrate JSON-RPC Engine (localhost:9944) ]
   - Substrate RPC methods running with `--rpc-methods Safe`
```

---

## 8. Data Flow Diagrams

### Extrinsic Life Cycle
```
[User Wallet]
      |  1. Construct & sign transaction payload using private key
      v
[HTTP/WS POST] ---> [Nginx Proxy (30 r/s limit)]
                          |  2. Forward request
                          v
               [Verdis Node JSON-RPC]
                          |  3. Call author_submitExtrinsic
                          v
               [Transaction Pool Engine]
                          |  4. Validate via TaggedTransactionQueue API
                          v
            [Peer-to-Peer Gossip Network]
                          |  5. Broadcast transaction to peer nodes
                          v
              [BABE Block Producer]
                          |  6. Pack extrinsic into candidate block
                          v
                [Block Execution / WASM]
                          |  7. Apply state transitions via Pallets
                          v
               [GRANDPA Finality Engine]
                          |  8. Validator 2/3+ voting agreement
                          v
                  [Finalized State Trie]
```

---

## 9. System Repositories & Build Outputs

* **Core Repository:** Rust / Substrate Node Workspace
* **Build Target:** `cargo build --release` (Generates native binary `verdis` and WebAssembly runtime blob `verdis_runtime.compact.compressed.wasm`).
* **Deployment Artifacts:**
  * Service Script: `/etc/systemd/system/verdis.service`
  * Gateway Configuration: `/etc/nginx/sites-available/verdischain`
  * Android Release Build: `verdis-wallet-release.apk`
