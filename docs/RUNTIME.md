# Verdis Chain Runtime Specification

This document provides a comprehensive technical specification of the **Verdis Chain v2.0.0** WebAssembly (WASM) runtime environment.

---

## 1. Overview & Chain Identity Parameters

Verdis Chain runtime is constructed using Substrate's FRAME framework and compiled to WebAssembly for deterministic forkless execution.

| Parameter | Value | Description |
| :--- | :--- | :--- |
| **Runtime Version** | `2.0.0` | Verdis Runtime Spec Version |
| **Token Symbol** | `VRS` | Native Verdis Utility & Governance Token |
| **Token Decimals** | `9` | 1 VRS = 1,000,000,000 Planck (Base Unit) |
| **SS58 Address Format** | `909` | Address prefix format for SS58 encoding |
| **Chain ID** | `909` | Network identifier |
| **Total Token Supply** | `100,000,000,000 VRS` | 100 Billion VRS hard supply cap |
| **Target Block Time** | `6 seconds` | Slot time duration |
| **Slots Per Epoch** | `600 slots` | BABE Epoch duration (~1 hour) |
| **Session Period** | `600 blocks` | Rotation interval for DPoS validator elections |
| **Max Active Validators**| `101` | Maximum consensus active validators |

---

## 2. Pallet Composition (17 Pallets)

The Verdis runtime incorporates 17 FRAME pallets handling identity, consensus, system operations, smart contracts, decentralized finance, token economics, and ecological verification.

```
+-----------------------------------------------------------------------------------+
|                            VERDIS RUNTIME (17 PALLETS)                            |
+-----------------------------------------------------------------------------------+
|  1. System                 2. Timestamp               3. BABE                     |
|  4. GRANDPA                5. Session                 6. Balances                 |
|  7. TransactionPayment     8. Sudo                    9. Scheduler                |
| 10. Preimage              11. Contracts              12. DPoS Staking             |
| 13. AMM-DEX               14. Eco Verification       15. Tokenomics               |
| 16. Vesting               17. Decentralized Storage                               |
+-----------------------------------------------------------------------------------+
```

### Detailed Pallet Index & Configurations

#### 1. System (`pallet_system`)
* **Index:** `0`
* **Purpose:** Core low-level abstraction layer defining basic state types, headers, extrinsics, accounts, block limits, and hash functions.
* **Config Parameters:**
  * `BlockWeights`: Maximum block weight capacity (2,000,000,000,000 picoseconds).
  * `BlockLength`: Maximum block length limit (5 MB).
  * `SS58Prefix`: Configured to `909`.
  * `AccountData`: Configured with `pallet_balances::AccountData<Balance>`.
  * `Hashing`: Blake2b 256-bit hash algorithm (`sp_core::H256`).

#### 2. Timestamp (`pallet_timestamp`)
* **Index:** `1`
* **Purpose:** Provides on-chain wall-clock time tracking set at the start of every block.
* **Config Parameters:**
  * `MinimumPeriod`: `3,000 milliseconds` (half of the 6-second target block time).
  * `WeightInfo`: Benchmark-derived execution weight costs.

#### 3. BABE (`pallet_babe`)
* **Index:** `2`
* **Purpose:** Block authoring consensus engine based on slot clock and VRF randomness.
* **Config Parameters:**
  * `EpochDuration`: `600 slots`.
  * `ExpectedBlockTime`: `6,000 ms`.
  * `KeyOwnerProof`: Enforces proof verification for bad slot authoring or equivocations.

#### 4. GRANDPA (`pallet_grandpa`)
* **Index:** `3`
* **Purpose:** Deterministic finality gadget managing validator authority set votes.
* **Config Parameters:**
  * `MaxAuthorities`: `101` validators.
  * `MaxSetIdSessionEntries`: Configured for multi-session authority set storage.

#### 5. Session (`pallet_session`)
* **Index:** `4`
* **Purpose:** Coordinates validator key changes and ties validator identities to consensus engine session keys (`BABE` VRF key + `GRANDPA` Ed25519 key).
* **Config Parameters:**
  * `SessionHandler`: Configured with `OpaqueKeys` tuple `(Babe, Grandpa)`.
  * `ValidatorId`: `AccountId` (32 bytes).

#### 6. Balances (`pallet_balances`)
* **Index:** `5`
* **Purpose:** Native currency ledger management for VRS balances, account locks, holds, free vs reserved balances, and transfer dispatches.
* **Config Parameters:**
  * `ExistentialDeposit`: `10,000,000 Planck` (0.01 VRS). Prevents state bloat by pruning accounts falling below this limit.
  * `MaxLocks`: `50`.
  * `MaxReserves`: `50`.

#### 7. TransactionPayment (`pallet_transaction_payment`)
* **Index:** `6`
* **Purpose:** Calculates gas/fee requirements for incoming extrinsics based on byte size and execution weight.
* **Config Parameters:**
  * `OperationalFeeMultiplier`: `5`.
  * `WeightToFee`: Converts execution weight to VRS tokens dynamically.
  * `FeeMultiplierUpdate`: Dynamic fee adjustment mechanism based on block congestion.

#### 8. Sudo (`pallet_sudo`)
* **Index:** `7`
* **Purpose:** Administrative pallet providing superuser privileges during early network lifecycle and runtime upgrade initializations.
* **Config Parameters:**
  * `Key`: Single root administrator `AccountId`.

#### 9. Scheduler (`pallet_scheduler`)
* **Index:** `8`
* **Purpose:** Provides periodic or delayed extrinsic execution scheduling engine.
* **Config Parameters:**
  * `MaxScheduledPerBlock`: `50`.
  * `MaximumWeight`: Upper bound weight reserved for scheduled calls.

#### 10. Preimage (`pallet_preimage`)
* **Index:** `9`
* **Purpose:** Offloads storage of large proposal calls and runtime upgrade byte arrays by hashing preimages on-chain.
* **Config Parameters:**
  * `BaseDeposit`: `1,000,000,000 Planck` (1 VRS base deposit).
  * `ByteDeposit`: `10,000,000 Planck` per byte stored.

#### 11. Contracts (`pallet_contracts`)
* **Index:** `10`
* **Purpose:** WebAssembly (WASM) smart contract execution engine allowing developers to deploy ink! smart contracts.
* **Config Parameters:**
  * `CallStack`: Maximum depth of nested cross-contract calls (`32`).
  * `DepositPerByte`: Contract code storage fee allocation.
  * `Schedule`: WASM instruction weight pricing table.

#### 12. DPoS Staking (`pallet_dpos`)
* **Index:** `11`
* **Purpose:** Delegated Proof-of-Stake consensus election layer. Selects up to 101 active validators per 600-block session.
* **Config Parameters:**
  * `MaxValidators`: `101`.
  * `MinValidatorStake`: `100,000 VRS` (100,000,000,000,000 Planck).
  * `MinNominatorStake`: `100 VRS` (100,000,000,000 Planck).
  * `UnbondingPeriod`: `28 sessions` (~28 hours).

#### 13. AMM-DEX (`pallet_amm_dex`)
* **Index:** `12`
* **Purpose:** Native automated market maker liquidity pool engine allowing decentralized swapping between VRS and custom eco-tokens.
* **Config Parameters:**
  * `FeeBps`: Liquidity pool trade swap fee set to `30 bps` (0.30%).
  * `MinimumLiquidity`: `1,000,000 Planck` locked on pool initialization.

#### 14. Eco Verification (`pallet_eco`)
* **Index:** `13`
* **Purpose:** Eco-friendly tracking module for recording carbon offset credits, tree planting/reforestation telemetry, and computing validator green sustainability scores.
* **Config Parameters:**
  * `GreenScoreWeight`: Percentage boost applied to green-verified validators during DPoS block reward distribution.
  * `MaxCertifiers`: `20` accredited environmental verification accounts.

#### 15. Tokenomics (`pallet_tokenomics`)
* **Index:** `14`
* **Purpose:** Manages inflation curves, dynamic token burning mechanisms, treasury distribution fractions, and total supply invariants.
* **Config Parameters:**
  * `MaxSupply`: `100,000,000,000 VRS`.
  * `BurnRateBps`: Deflationary fee burn fraction (20% of network transaction fees burned).

#### 16. Vesting (`pallet_vesting`)
* **Index:** `15`
* **Purpose:** Enforces block-by-block linear vesting schedules for team, advisor, and investor token genesis allocations.
* **Config Parameters:**
  * `MinVestedTransfer`: `1,000 VRS` (1,000,000,000,000 Planck).
  * `MaxVestingSchedules`: `28` schedules per individual account.

#### 17. Storage (`pallet_storage`)
* **Index:** `16`
* **Purpose:** On-chain proof and metadata verification registry for decentralized file storage providers.
* **Config Parameters:**
  * `ProofVerificationPeriod`: `1200 blocks`.
  * `StorageFeePerMB`: Base rate for on-chain storage commitment.

---

## 3. Implemented Runtime APIs

The Verdis runtime exposes the standard set of Substrate RPC-facing APIs for node interaction, transaction routing, and consensus coordination:

| API Name | Interface Trait | Purpose / Usage |
| :--- | :--- | :--- |
| **`Core`** | `sp_api::Core` | Initializes blocks, executes extrinsics, extracts version and metadata. |
| **`BlockBuilder`** | `sp_block_builder::BlockBuilder` | Constructs new blocks, applies extrinsics, checks inherited inherent data. |
| **`Metadata`** | `sp_api::Metadata` | Exposes metadata reflection API for client SDKs and Verdiscan. |
| **`TaggedTransactionQueue`**| `sp_transaction_pool::runtime_api::TaggedTransactionQueue` | Validates transaction validity, priority, nonces, and dependencies in tx pool. |
| **`OffchainWorkerApi`** | `sp_offchain::OffchainWorkerApi` | Triggers off-chain worker execution routines at block execution end. |
| **`SessionKeys`** | `sp_session::SessionKeys` | Generates and decodes opaque session key tuples (`author_rotateKeys`). |
| **`BabeApi`** | `sp_consensus_babe::BabeApi` | Interrogates epoch parameters, VRF outputs, slot assignment configs. |
| **`GrandpaApi`** | `sp_consensus_grandpa::GrandpaApi` | Fetches active GRANDPA authority sets, pending set changes, and equivocation proofs. |
| **`TransactionPayment`** | `pallet_transaction_payment_rpc_runtime_api::TransactionPaymentApi` | Queries fee estimates, weight conversions, and dispatch info prior to submission. |
| **`GenesisBuilder`** | `sp_genesis_builder::GenesisBuilder` | Builds and queries genesis state configurations during chain initialization. |

---

## 4. Genesis State & Distribution Breakdown

The total supply of Verdis Chain is **100,000,000,000 VRS** (100 Billion VRS) initialized at genesis across 6 key allocations:

```
+-------------------------------------------------------------------+
|               VERDIS GENESIS DISTRIBUTION (100B VRS)              |
+-------------------------------------------------------------------+
| [Community Allocation]          35,000,000,000 VRS (35.0%)        |
| [Treasury & Staking Rewards]    30,000,000,000 VRS (30.0%)        |
| [Core Team]                     15,000,000,000 VRS (15.0%)        |
| [Strategic Investors]           10,000,000,000 VRS (10.0%)        |
| [Liquidity Pools]                5,000,000,000 VRS  (5.0%)        |
| [Advisors & Ecosystem Airdrop]   5,000,000,000 VRS  (5.0%)        |
+-------------------------------------------------------------------+
```

### Genesis Token Distribution Table

| Bucket | Allocation (VRS) | Allocation (Planck) | Percentage | Vesting Condition / Lockup |
| :--- | :--- | :--- | :--- | :--- |
| **Community** | 35,000,000,000 VRS | 35,000,000,000,000,000,000 | 35.0% | 10% unlocked at TGE, remainder linear 36 months |
| **Treasury + Staking** | 30,000,000,000 VRS | 30,000,000,000,000,000,000 | 30.0% | On-chain governance controlled emission over 10 years |
| **Core Team** | 15,000,000,000 VRS | 15,000,000,000,000,000,000 | 15.0% | 12-month cliff, 36-month linear vesting |
| **Investors** | 10,000,000,000 VRS | 10,000,000,000,000,000,000 | 10.0% | 6-month cliff, 18-month linear vesting |
| **Liquidity Pools** | 5,000,000,000 VRS | 5,000,000,000,000,000,000 | 5.0% | 100% unlocked at TGE for AMM DEX initial liquidity |
| **Advisors + Airdrop**| 5,000,000,000 VRS | 5,000,000,000,000,000,000 | 5.0% | 20% unlocked at TGE, 12-month linear vesting |
| **Total** | **100,000,000,000 VRS**| **100,000,000,000,000,000,000** | **100.0%** | Hard capped total initial supply |

---

## 5. Genesis Spec Config Snippet (`chain_spec.rs`)

```json
{
  "name": "Verdis Mainnet",
  "id": "verdis_mainnet",
  "chainType": "Live",
  "bootNodes": [
    "/ip4/91.98.160.145/tcp/30333/p2p/12D3KooWSvEr...12345"
  ],
  "telemetryEndpoints": null,
  "protocolId": "vrs909",
  "properties": {
    "tokenDecimals": 9,
    "tokenSymbol": "VRS",
    "ss58Format": 909
  },
  "genesis": {
    "runtime": {
      "system": {},
      "balances": {
        "balances": [
          ["5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY", 35000000000000000000],
          ["5GNJqR1F3ZXChB315CkdE53Cg4A2f2222222222222222222", 30000000000000000000]
        ]
      },
      "babe": {
        "epochConfig": {
          "c": [1, 4],
          "allowedSlots": "PrimaryAndSecondaryPlainSlots"
        }
      },
      "grandpa": {
        "authorities": []
      },
      "dpos": {
        "maxValidators": 101,
        "minValidatorStake": 100000000000000
      },
      "sudo": {
        "key": "5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY"
      }
    }
  }
}
```
