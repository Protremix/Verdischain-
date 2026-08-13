# Verdiscan Explorer User & Developer Guide

This document provides a comprehensive operational guide for **Verdiscan** (`https://verdischain.com`), the native block explorer for the Verdis Chain ecosystem.

---

## 1. Explorer Overview & Interface Design

Verdiscan is a dark-themed, Solscan-style block explorer designed for real-time visibility into the Verdis Chain ledger state, transactions, consensus performance, smart contracts, decentralized finance pools, and ecological metric logs.

```
+-----------------------------------------------------------------------------------+
| VERDISCAN DASHBOARD - https://verdischain.com                                     |
+-----------------------------------------------------------------------------------+
|  [Search Bar: Address (SS58 / 0x), Tx Hash, Block #, Contract Address]           |
+-----------------------------------------------------------------------------------+
|  TPS: 1,200 | Block Height: #4,820 | Finalized: #4,818 | Active Validators: 101 |
+-----------------------------------------------------------------------------------+
| TABS: [Overview] [Blocks] [Transactions] [Validators] [DEX] [Eco] [Contracts] [Tokenomics] |
+-----------------------------------------------------------------------------------+
```

### Main Visual Elements
* **Theme:** Dark Mode (solscan-style deep charcoal `#0d1117` & forest green `#10b981` accents).
* **Live Network Stats Bar:** Real-time block height, finalized height, TPS (transactions per second), epoch slot, total VRDX circulating supply, active validators.
* **Global Search Bar:** Supports lookup by:
  * Block Number (e.g., `4820`)
  * Block Hash (32-byte hex e.g., `0x9c3d4f...`)
  * Transaction / Extrinsic Hash (`0x7a8b9c...`)
  * Account SS58 Address (Prefix `909` e.g., `5GrwvaEF...`)
  * Smart Contract Address (`0x...`)

---

## 2. Explorer Navigation Tabs & Feature Breakdown

### 2.1. Overview Tab (Dashboard)
* **Summary Cards:** Total Supply (100B VRDX), Market Cap, Active Accounts, Network Hashrate / VRF Slot execution, Eco Carbon Offsets total.
* **Recent Blocks Feed:** Real-time stream of newly authored BABE blocks with slot index, author validator name, transaction count, and age.
* **Recent Transactions Feed:** Real-time list of extrinsics, sender, recipient, method name (`balances.transfer`, `ammDex.swap`, `eco.logReforestation`), and transfer amounts.

### 2.2. Blocks Tab
* **Block Table:** Lists block height, hash, parent hash, author validator, transaction count, block size (KB), state root, and block finality status.
* **Block Detail View:**
  * **Header Details:** Timestamp, Epoch, Slot Number, State Root Hash, Extrinsics Root Hash.
  * **Consensus Digest:** BABE VRF proof logs and GRANDPA commit vote justifications.
  * **Extrinsics List:** Expandable view of all extrinsics in the block with parameters and events emitted.

### 2.3. Transactions Tab
* **Transaction Table:** Displays Tx Hash, Status (`Success` / `Failed`), Block Number, Origin SS58 Address, Target Address, Value in VRDX, and Transaction Fee.
* **Transaction Detail View:**
  * **Extrinsic Call Data:** Module/Pallet name and Method dispatch call.
  * **Raw Parameters:** Decoded JSON payload arguments.
  * **Event Logs:** List of system events triggered (e.g., `balances.Transfer`, `transactionPayment.TransactionFeePaid`).
  * **Execution Weight & Fee:** Total weight consumed and fee breakdown (base fee + byte fee + tip).

### 2.4. Validators / DPoS Staking Tab
* **Active Validator Roster:** Roster of active validators (up to 101 max) for the current 600-block session.
* **Validator Metrics:**
  * **Validator Address & Name/Identity**
  * **Total Stake:** Self-stake + Nominated stake in VRDX.
  * **Commission Rate (%)**
  * **Green Score:** Sustainability score derived from `pallet_eco` metrics.
  * **Blocks Authored in Current Epoch**
  * **Uptime Performance (%) & Equivocation History**

### 2.5. DEX Pools / AMM Tab
* **Liquidity Pools Overview:** Lists native automated market maker trading pairs (e.g., `VRDX/vUSDT`, `VRDX/vCARBON`).
* **Pool Metrics:**
  * **Total Value Locked (TVL)**
  * **24h Trading Volume**
  * **Pool Reserves:** Liquidity reserve balance of Token A and Token B.
  * **Swap Fee:** 0.30% (30 bps).
* **Recent Swaps & Liquidity Events:** Real-time log of `Swap`, `AddLiquidity`, and `RemoveLiquidity` transactions.

### 2.6. Eco Data Tab (Carbon & Sustainability Verification)
Verdis Chain incorporates native ecological tracking features directly into the consensus and runtime via `pallet_eco`.

```
+-----------------------------------------------------------------------------------+
| ECO DATA METRICS DASHBOARD                                                        |
+-----------------------------------------------------------------------------------+
| Total Carbon Offsets: 142,500 Tons CO2e | Verified Reforestation Trees: 1,250,000 |
+-----------------------------------------------------------------------------------+
| REFORESTATION LOGS TABLE:                                                         |
| Project ID | Region / Geo-Coordinates | Trees Planted | Verifier | Proof Hash |
| REF-8091   | Amazon Basin (-3.12,-60.0)| 50,000        | EcoCert  | 0x3a4b5c...|
+-----------------------------------------------------------------------------------+
```

* **Metrics Log Breakdown:**
  * **Carbon Offset Registry:** Certificate serial numbers, issued offset tons CO2e, retirement status.
  * **Reforestation Telemetry:** Geolocation tagged reforestation entries, tree species, planting density, and cryptographic audit proofs.
  * **Green Validator Scoring Engine:** Computes validator green multipliers based on renewable energy usage, carbon offset purchases, and hardware efficiency.

### 2.7. Smart Contracts Tab
* **WASM Contract Registry:** Directory of smart contracts deployed via `pallet_contracts`.
* **Contract Detail Page:**
  * **Contract Code Hash & Bytecode Verification**
  * **Read/Write Storage Interfaces (ink! ABI)**
  * **Contract Balance & Execution History**

### 2.8. Tokenomics & Holders Tab
* **Distribution Graph:** Displays the 100B VRDX token distribution.
* **Rich List / Top Holders Table:** Ranks account addresses by VRDX balance, percentage of total supply, and account label (e.g., Treasury, Team Vesting, AMM Pool).

---

## 3. Underlying API Endpoints Used by Verdiscan

Verdiscan queries the node backend via REST and JSON-RPC endpoints:

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/blockchain/info` | `GET` | Fetches latest block height, finalized head, and TPS |
| `/api/monitoring/health` | `GET` | Node sync health and active peer count |
| `/api/blocks/latest` | `GET` | Paginated list of recent blocks |
| `/api/blocks/:hash_or_num` | `GET` | Detailed block header, digest, and extrinsics |
| `/api/tx/:hash` | `GET` | Transaction status, event logs, and decoded call parameters |
| `/api/validators` | `GET` | Active 101 DPoS validator set, stakes, and green scores |
| `/api/dex/pools` | `GET` | AMM liquidity pool reserve balances, TVL, and volumes |
| `/api/eco/telemetry` | `GET` | Carbon offsets, reforestation logs, and verifier proofs |
| `/rpc` | `POST` | Direct JSON-RPC proxy fallback for state reads (`state_getStorage`) |

---

## 4. How to Read Data on Verdiscan

### How to Inspect a Block
1. Navigate to `https://verdischain.com/blocks` or enter the block number in the search bar.
2. Review the **Header Card** to confirm block slot index and finalized status.
3. Inspect **Extrinsics:** Each extrinsic displays the index (e.g., `4820-0`, `4820-1`). Click to expand parameters.

### How to Verify an Eco Reforestation Proof
1. Navigate to the **Eco Tab**.
2. Locate the project entry under **Reforestation Logs**.
3. Click the **Proof Hash**. Verdiscan displays the on-chain IPFS / Storage hash committed by accredited verifiers in `pallet_eco`.
