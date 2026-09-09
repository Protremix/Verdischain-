# Verdis Substrate Blockchain: Comprehensive Storage Migration Strategy

**Document Version:** 1.0.0  
**Target Runtime:** Verdis Spec v10  
**Network Domain:** verdischain.com  
**Native Token:** VRDX (100,000,000,000 Total Supply | SS58 Prefix: 909)  
**Infrastructure Context:** 10 Active Validator Nodes, 15 Full Nodes | Server: `root@91.98.160.145`  
**Repository Path:** `/opt/verdis-chain-rust/`  

---

## Table of Contents
1. [Overview](#1-overview)
2. [Pre-Upgrade Checklist](#2-pre-upgrade-checklist)
3. [Migration Types](#3-migration-types)
4. [Implementation Pattern](#4-implementation-pattern)
5. [Versioning & StorageVersion Trait](#5-versioning--storageversion-trait)
6. [Testing Migrations (`try-runtime` & Unit Tests)](#6-testing-migrations-try-runtime--unit-tests)
7. [Rollback Strategy](#7-rollback-strategy)
8. [Current Pallet Inventory](#8-current-pallet-inventory)
9. [Migration Log Template](#9-migration-log-template)
10. [Emergency Procedures](#10-emergency-procedures)

---

## 1. Overview

In Substrate-based Layer-1 blockchains like **Verdis**, runtime logic is stored directly on-chain and updated via forkless runtime upgrades. While the WebAssembly (Wasm) blob defining executable logic can be replaced in a single block, the underlying key-value database (`RocksDB`/`ParityDB`) containing the chain state remains persistent across upgrades.

### Why Storage Migrations Are Required
1. **Runtime Schema Changes:** Modifying existing Rust data structures (e.g., converting a single balance `u64` into a struct containing locked and free balances `BalanceStruct { free: u128, reserved: u128 }`).
2. **Pallet Additions & Initializations:** Introducing new custom or upstream pallets that require default on-chain state initialization.
3. **Storage Prefix & Key Restructuring:** Renaming storage items, altering map keys (`Blake2_128Concat` to `Twox64Concat`), or restructuring double/N-maps.
4. **Pallet Deprecation & Removal:** Safely purging obsolete storage prefixes to reclaim database disk space and maintain optimal node performance.

### Risks of Unchecked Upgrades
Executing a runtime upgrade without a matching storage migration strategy causes **state corruption** or **runtime panics**. When the newly compiled Wasm runtime attempts to decode existing raw bytes using a modified struct layout, `SCALE` deserialization fails. In severe cases, this triggers validator node crashes, consensus halts, or non-recoverable state drift across the Verdis 10-validator set.

---

## 2. Pre-Upgrade Checklist

Before submitting any `system.setCode` governance proposal or enacting a runtime upgrade (e.g., from Spec v10 to Spec v11), the release engineering team must execute the following protocol:

| Step | Action Item | Verification Command / Target | Responsible Party |
| :--- | :--- | :--- | :--- |
| **2.1** | **Full Database Snapshot** | Execute cold/warm snapshots across all 15 nodes (`/var/lib/verdis/db`). | Lead DevOps |
| **2.2** | **DevNet / Staging Execution** | Deploy candidate Wasm on isolated 3-node DevNet; verify 100 blocks produced post-upgrade. | Core Runtime Team |
| **2.3** | **`try-runtime` Static & Dynamic Audit** | Run `try-runtime` against a fresh mainnet state fork to verify state transitions and storage integrity. | Lead Security Auditor |
| **2.4** | **Weight Limit Verification** | Calculate execution weight of `on_runtime_upgrade`. Ensure total weight strictly fits within block maximum (`max_extrinsic` weight budget). | Core Runtime Team |
| **2.5** | **Storage Version Validation** | Verify `on_chain_storage_version()` matches expected pre-migration version for all 13 pallets. | Release Manager |
| **2.6** | **Governance Timings & TC Approval** | Secure Technical Committee fast-track authorization or schedule 7-day referendum window. | Governance Lead |
| **2.7** | **Emergency Rollback Plan Active** | Verify SSH key access to `root@91.98.160.145` and ensure backup node binaries are staged in `/opt/verdis-chain-rust/backup/`. | DevOps / SRE |

---

## 3. Migration Types

Verdis categorizes storage migrations into three distinct patterns depending on the state modification scope:

```
                          ┌────────────────────────┐
                          │ Migration Type Selection│
                          └───────────┬────────────┘
                                      │
         ┌────────────────────────────┼────────────────────────────┐
         ▼                            ▼                            ▼
┌─────────────────┐        ┌─────────────────────┐       ┌────────────────────┐
│ 1. New Pallet   │        │ 2. Storage Version  │       │ 3. Deprecated      │
│    Addition     │        │    Schema Change    │       │    Pallet Removal  │
└────────┬────────┘        └──────────┬──────────┘       └─────────┬──────────┘
         │                            │                            │
         ▼                            ▼                            ▼
Init default storage       Transform struct/map          Purge storage keys
Set initial version        In-place or multi-block       Clear prefix from DB
```

### 3.1 Pallet Addition (New Pallet)
When adding a new pallet to the runtime (e.g., adding `pallet_nfts`), the on-chain storage version is uninitialized (`v0` or `NoStorageVersion`).
* **Objective:** Initialize genesis-like default values and write the initial `StorageVersion` into storage.
* **Mechanism:** The pallet's initial `StorageVersion` is set in code via `#[pallet::storage_version(STORAGE_VERSION)]`. The `on_runtime_upgrade` hook populates necessary initial state parameters and explicitly stores the version on-chain.

### 3.2 Storage Version Migration (Existing Schema Change)
When altering existing data structures within custom pallets (such as `pallet-dpos`, `pallet-amm-dex`, or `pallet-vesting`).
* **Single-Block (In-Place) Migration:** Used when the total record count is bounded and can be safely transformed within a single block's weight limit.
* **Multi-Block Migration (MBM):** Required when transforming unbounded collections (e.g., millions of token balance records). Migration progress is persisted across consecutive block initialization hooks (`on_initialize`) until completion.

### 3.3 Deprecated Pallet Removal
When stripping an legacy or obsolete pallet from the Verdis runtime.
* **Objective:** Completely erase all key-value pairs stored under the target pallet's storage prefix to prevent state bloat.
* **Mechanism:** Use `frame_support::storage::migration::clear_prefix` or `frame_support::traits::KillStorageResult`.

---

## 4. Implementation Pattern

Substrate FRAME v2 provides high-level primitives for structuring safe, weight-metered storage migrations.

### 4.1 Implementing `OnRuntimeUpgrade` for Custom Pallets

Below is a production-grade Rust implementation demonstrating a schema upgrade for the `pallet-dpos` custom pallet (migrating validator metadata from `v1::ValidatorInfoV1` to `v2::ValidatorInfoV2`).

```rust
// File: /opt/verdis-chain-rust/pallets/dpos/src/migrations/v2.rs

use super::*;
use frame_support::{
    pallet_prelude::*,
    traits::OnRuntimeUpgrade,
    weights::Weight,
    storage::migration,
};
use sp_std::marker::PhantomData;

/// Storage version 1 structure definition (Legacy)
#[derive(Decode, Encode, Sized)]
pub struct ValidatorInfoV1 {
    pub total_stake: u128,
    pub delegators_count: u32,
    pub is_active: bool,
}

/// Storage version 2 structure definition (Current)
#[derive(Decode, Encode, TypeInfo, MaxEncodedLen, RuntimeDebug, PartialEq, Eq)]
pub struct ValidatorInfoV2<AccountId> {
    pub total_stake: u128,
    pub self_stake: u128,
    pub delegators_count: u32,
    pub is_active: bool,
    pub reward_destination: AccountId,
}

pub struct MigrateV1ToV2<T>(PhantomData<T>);

impl<T: Config> OnRuntimeUpgrade for MigrateV1ToV2<T> {
    fn on_runtime_upgrade() -> Weight {
        let on_chain_version = Pallet::<T>::on_chain_storage_version();
        let current_version = Pallet::<T>::current_storage_version();

        // 1. Version Check: Only run if on-chain version is v1
        if on_chain_version == 1 {
            log::info!(
                target: "runtime::dpos",
                "Migrating Dpos storage from v1 to v2..."
            );

            let mut reads: u64 = 0;
            let mut writes: u64 = 0;

            // 2. Storage Key Prefix Extraction
            let storage_prefix = Pallet::<T>::name().as_bytes();
            let item_prefix = b"Validators";

            // Translate old storage records to new storage format
            migration::translate_storage::<T::AccountId, ValidatorInfoV1, ValidatorInfoV2<T::AccountId>, _>(
                storage_prefix,
                item_prefix,
                |key, old_val| {
                    reads += 1;
                    writes += 1;

                    // Synthesize default fields for new struct elements
                    Some(ValidatorInfoV2 {
                        total_stake: old_val.total_stake,
                        self_stake: old_val.total_stake / 10, // 10% self-bond assumption
                        delegators_count: old_val.delegators_count,
                        is_active: old_val.is_active,
                        reward_destination: key, // Default reward dest to validator AccountId
                    })
                },
            );

            // 3. Update the on-chain storage version to v2
            current_version.put::<Pallet<T>>();
            writes += 1;

            log::info!(
                target: "runtime::dpos",
                "Dpos storage migration completed successfully. Reads: {}, Writes: {}",
                reads,
                writes
            );

            // Return calculated DB execution weight
            T::DbWeight::get().reads_writes(reads, writes)
        } else {
            log::warn!(
                target: "runtime::dpos",
                "Dpos migration skipped: On-chain version {:?} != expected 1",
                on_chain_version
            );
            T::DbWeight::get().reads(1)
        }
    }

    #[cfg(feature = "try-runtime")]
    fn pre_upgrade() -> Result<Vec<u8>, TryRuntimeError> {
        let count = migration::storage_key_iter::<T::AccountId, ValidatorInfoV1, _>(
            Pallet::<T>::name().as_bytes(),
            b"Validators",
        ).count() as u32;

        log::info!(target: "runtime::dpos", "Pre-migration validator count: {}", count);
        Ok(count.encode())
    }

    #[cfg(feature = "try-runtime")]
    fn post_upgrade(state: Vec<u8>) -> Result<(), TryRuntimeError> {
        let prev_count: u32 = Decode::decode(&mut &state[..])
            .map_err(|_| "Failed to decode pre-upgrade state")?;

        let current_version = Pallet::<T>::on_chain_storage_version();
        ensure!(current_version == 2, "Storage version must be 2 after migration");

        let post_count = Validators::<T>::iter().count() as u32;
        ensure!(prev_count == post_count, "Validator record count mismatch post-migration");

        log::info!(target: "runtime::dpos", "Post-migration check verified: {} records migrated", post_count);
        Ok(())
    }
}
```

### 4.2 Standard Migration Composition with `frame_support::migrations::VersionedMigration`

To eliminate boilerplate version checks, Verdis uses the standardized `VersionedMigration` struct wrapper inside `runtime/src/lib.rs`:

```rust
// File: /opt/verdis-chain-rust/runtime/src/lib.rs

pub type DposMigrationV1ToV2 = frame_support::migrations::VersionedMigration<
    1, // From StorageVersion
    2, // To StorageVersion
    pallet_dpos::migrations::v2::MigrateV1ToV2<Runtime>,
    pallet_dpos::Pallet<Runtime>,
    <Runtime as frame_system::Config>::DbWeight,
>;

// Combine all runtime migrations into a single tuple for Executive
pub type RuntimeMigrations = (
    DposMigrationV1ToV2,
    pallet_vesting::migrations::v2::MigrateV1ToV2<Runtime>,
);

// Executed inside Executive config
pub type Executive = frame_executive::Executive<
    Runtime,
    Block,
    frame_system::ChainContext<Runtime>,
    Runtime,
    AllPalletsWithSystem,
    RuntimeMigrations, // Injected here
>;
```

---

## 5. Versioning & StorageVersion Trait

Substrate manages pallet versions using the `StorageVersion` primitive.

### 5.1 Declaring Pallet Storage Version
Every pallet in Verdis explicitly specifies its current in-code version via the `#[pallet::storage_version]` attribute:

```rust
#[frame_support::pallet]
pub mod pallet {
    use frame_support::pallet_prelude::*;

    /// Current in-code storage version for pallet-amm-dex
    const STORAGE_VERSION: StorageVersion = StorageVersion::new(1);

    #[pallet::pallet]
    #[pallet::storage_version(STORAGE_VERSION)]
    pub struct Pallet<T>(_);
    
    // ...
}
```

### 5.2 Version Inspection Primitives
Within runtime code and migration logic, two distinct version inspection methods exist:

1. **`Pallet::<T>::current_storage_version()`**: Returns the hardcoded version declared in the Rust Wasm binary compiled into the runtime.
2. **`Pallet::<T>::on_chain_storage_version()`**: Reads the stored version from the actual on-chain database storage under the pallet's prefix.

```rust
// Version Guard Pattern
let on_chain = Pallet::<T>::on_chain_storage_version();
let in_code  = Pallet::<T>::current_storage_version();

if on_chain < in_code {
    log::info!("Executing storage migration from {:?} to {:?}", on_chain, in_code);
    // Execute transformation...
    in_code.put::<Pallet<T>>(); // Persist new version to DB
}
```

---

## 6. Testing Migrations (`try-runtime` & Unit Tests)

Migrations **must never** be executed directly on mainnet without passing static verification, unit test simulations, and live-fork testing.

### 6.1 Unit Testing Migrations with `TestState`
Create mock runtime tests using the `sp_io::TestExternalities` builder:

```rust
// File: /opt/verdis-chain-rust/pallets/dpos/src/tests/migration_tests.rs

#[test]
fn test_dpos_v1_to_v2_migration_works() {
    TestExternalities::default().execute_with(|| {
        // 1. Manually insert legacy V1 storage records directly into raw DB
        let account_id = 1u64;
        let v1_data = ValidatorInfoV1 {
            total_stake: 1_000_000_000_000,
            delegators_count: 50,
            is_active: true,
        };
        
        // Write raw legacy bytes to simulate pre-upgrade state
        let key = storage_key(b"Dpos", b"Validators", &account_id.encode());
        sp_io::storage::set(&key, &v1_data.encode());

        // Set on-chain version to 1
        StorageVersion::new(1).put::<DposPallet>();

        // 2. Execute migration
        let weight = MigrateV1ToV2::<TestRuntime>::on_runtime_upgrade();
        assert!(weight > Weight::zero());

        // 3. Assert on-chain version updated to 2
        assert_eq!(DposPallet::on_chain_storage_version(), 2);

        // 4. Read migrated data and verify decoded structure
        let v2_data = DposPallet::validators(account_id).unwrap();
        assert_eq!(v2_data.total_stake, 1_000_000_000_000);
        assert_eq!(v2_data.self_stake, 100_000_000_000);
        assert_eq!(v2_data.reward_destination, account_id);
    });
}
```

### 6.2 Full Verification with `try-runtime` CLI

Substrate's `try-runtime` tool executes the exact migration logic against a real, live state snapshot downloaded from the production mainnet node without modifying the actual state.

#### Command Execution Sequence
```bash
# 1. Build runtime binary with try-runtime feature enabled
cd /opt/verdis-chain-rust
cargo build --release --features try-runtime

# 2. Run try-runtime against Verdis Mainnet RPC endpoint
try-runtime \
  --runtime ./target/release/wbuild/verdis-runtime/verdis_runtime.wasm \
  on-runtime-upgrade \
  live \
  --uri wss://verdischain.com:9944
```

#### Expected Output Audit Log
```text
[INFO try-runtime] 🚀 Executing runtime upgrade tests for Verdis Spec v11...
[INFO runtime::dpos] Pre-migration validator count: 10
[INFO runtime::dpos] Migrating Dpos storage from v1 to v2...
[INFO runtime::dpos] Dpos storage migration completed successfully. Reads: 10, Writes: 11
[INFO runtime::dpos] Post-migration check verified: 10 records migrated
[INFO try-runtime] ✔ All pre-upgrade and post-upgrade hooks passed successfully. Zero state corruption detected.
```

---

## 7. Rollback Strategy

If a runtime upgrade fails during or immediately after execution, a fast, structured rollback strategy must be initiated.

```
                          ┌────────────────────────┐
                          │ Migration Failure Event │
                          └───────────┬────────────┘
                                      │
         ┌────────────────────────────┴────────────────────────────┐
         ▼                                                         ▼
┌─────────────────────────────────┐               ┌────────────────────────────────┐
│ Scenario A: Block Import Panic  │               │ Scenario B: Post-Upgrade State │
│ Consensus Halted Mid-Upgrade    │               │ Corruption Detected            │
└────────────────┬────────────────┘               └────────────────┬───────────────┘
                 │                                                 │
                 ▼                                                 ▼
1. Stop all node services                         1. Submit Emergency Governance Extrinsic
2. Restore RocksDB snapshot                        2. Revert Wasm binary spec version
3. Re-launch previous Wasm binary                 3. Execute storage fix / state patch
```

### 7.1 Automated Snapshot Restoration Procedure
All 10 validator nodes run automated pre-upgrade snapshots. If consensus fails post-upgrade, execute the following script across nodes:

```bash
#!/usr/bin/env bash
# Execute on server: root@91.98.160.145

set -e

echo "=== EMERGENCY ROLLBACK INITIATED ==="

# 1. Stop Verdis Node Services
systemctl stop verdis-validator.service

# 2. Revert Database to Pre-Upgrade Snapshot
rm -rf /var/lib/verdis/data/chains/verdis_mainnet/db
cp -r /var/lib/verdis/backups/db_pre_spec10_snap /var/lib/verdis/data/chains/verdis_mainnet/db

# 3. Swap Binary Back to Previous Spec Release
cp /opt/verdis-chain-rust/backup/verdis-node-v9.0.0 /usr/local/bin/verdis-node

# 4. Restart Validator Service
systemctl start verdis-validator.service

echo "=== EMERGENCY ROLLBACK COMPLETE. CHECKING NODE STATUS ==="
verdis-node --version
systemctl status verdis-validator.service
```

---

## 8. Current Pallet Inventory

Verdis Runtime Spec v10 consists of **13 total pallets** (7 custom pallets and 6 core upstream FRAME pallets).

| # | Pallet Name | Type | Storage Version | Storage Prefix | Purpose & Description |
| :-: | :--- | :--- | :-: | :--- | :--- |
| **1** | `pallet-dpos` | Custom | `v2` | `Dpos` | Delegated Proof-of-Stake consensus management, validator set election, self-bonding, and reward distribution. |
| **2** | `pallet-amm-dex` | Custom | `v1` | `AmmDex` | Automated Market Maker decentralized exchange for VRDX and liquidity pool token swaps. |
| **3** | `pallet-eco` | Custom | `v1` | `Eco` | Ecosystem development fund allocation, grant management, and project tracking. |
| **4** | `pallet-tokenomics` | Custom | `v1` | `Tokenomics` | Protocol inflation controls, dynamic fee burning mechanisms, and validator yield curves. |
| **5** | `pallet-vesting` | Custom | `v2` | `Vesting` | Schedule-based token vesting schedules for genesis contributors, team allocations, and strategic partners. |
| **6** | `pallet-fungible-tokens` | Custom | `v1` | `FungibleTokens` | Multi-asset creation and lifecycle management (fungible asset standards on Verdis). |
| **7** | `pallet-storage` | Custom | `v1` | `Storage` | On-chain file metadata storage, proofs of storage capacity, and archival references. |
| **8** | `pallet-contracts` | Upstream | `v16` | `Contracts` | Wasm smart contract execution engine (`pallet_contracts`). |
| **9** | `pallet-nfts` | Upstream | `v1` | `Nfts` | Non-Fungible Token standard for collection creation, minting, trading, and attribute storage. |
| **10**| `pallet-multisig` | Upstream | `v1` | `Multisig` | Multi-signature wallet accounts requiring N-of-M approvals for execution. |
| **11**| `pallet-proxy` | Upstream | `v1` | `Proxy` | Account permissioning, key delegation, and execution proxying. |
| **12**| `pallet-treasury` | Upstream | `v1` | `Treasury` | On-chain community treasury vault holding unallocated VRDX funds. |
| **13**| `pallet-governance` | Upstream | `v1` | `Council`/`Democracy`/`Utility` | Collective decision-making, referendum voting, fast-track proposals, and batch call dispatching. |

---

## 9. Migration Log Template

Every runtime migration executed on Verdis Mainnet or TestNet must be formally documented using the template below and committed to `/opt/verdis-chain-rust/docs/migrations/`.

```markdown
# Verdis Storage Migration Log: [MIGRATION-ID]

## General Metadata
- **Migration ID:** VMR-2026-08-01
- **Target Spec Version:** Spec v11
- **Target Pallet:** `pallet-dpos`
- **Execution Date:** 2026-08-04 21:30 UTC
- **Author / Lead Engineer:** Verdis Core Dev Team
- **Reviewer / Auditor:** Security Audit Team

## Version Transition
- **Pre-Migration Version:** `v1`
- **Post-Migration Version:** `v2`

## Migration Scope & Schema Changes
- **Description:** Updated `ValidatorInfo` struct to include `self_stake` and `reward_destination` fields.
- **Affected Storage Maps:** `Validators` (`StorageMap<AccountId, ValidatorInfoV2>`)
- **Estimated Storage Keys Transformed:** 10 Validator Records

## Benchmarking & Weight Analysis
- **Execution Weight:** `15,420,000` Weight Units
- **Max Permissible Block Weight:** `2,000,000,000,000` Weight Units
- **Weight Usage Ratio:** 0.00077% of block capacity

## Audit & Test Verification
- [x] Rust Unit Tests Passed (`cargo test -p pallet-dpos`)
- [x] `try-runtime` executed against Mainnet fork with zero errors
- [x] Pre-upgrade and post-upgrade storage invariant checks verified
- [x] Database snapshot created across all 10 validator nodes

## Execution Log & Verification Sign-off
- **Governance Referendum Index:** #14
- **Fast-Track Approved:** Yes (Technical Committee)
- **Extrinsic Hash:** `0x9a8f...3c1e`
- **Result Status:** SUCCESS
```

---

## 10. Emergency Procedures

In the event of an unhandled runtime error, panic during block import, or storage corruption on **Verdis Mainnet** (`verdischain.com`), follow this incident response runbook.

### Tiered Severity Classification

* **P1 - Critical (Chain Halt / Block Production Stopped):** Migration caused a runtime panic during `on_initialize` or block execution.
* **P2 - Major (Storage Corruption / State Inconsistency):** Chain is producing blocks, but pallet storage returns invalid/corrupted data.
* **P3 - Minor (Weight Overrun / Slow Block Import):** Migration weight exceeded benchmarks, causing slow block processing but consensus holds.

---

### Incident Response Protocol for P1 (Chain Halt)

#### Step 1: Immediate Operator Alert & Communication
1. Notify all 10 active validator operators via the Emergency Discord/Telegram Validator Channel.
2. Freeze all incoming bridge transactions (`VerdisBridge.sol` on BSC / Ethereum).

#### Step 2: Access Production Server
Connect to the primary coordination host:
```bash
ssh root@91.98.160.145
cd /opt/verdis-chain-rust
```

#### Step 3: Stop Validator Nodes & Isolate State
Broadcast stop command across validator orchestration layer:
```bash
ansible-playbook -i /opt/verdis-chain-rust/deploy/hosts /opt/verdis-chain-rust/deploy/stop_validators.yml
```

#### Step 4: Restore Pre-Upgrade DB Snapshot
Revert the key-value database across all validator instances to the snapshot captured in **Pre-Upgrade Checklist Step 2.1**:
```bash
ansible-playbook -i /opt/verdis-chain-rust/deploy/hosts /opt/verdis-chain-rust/deploy/restore_snapshot.yml
```

#### Step 5: Downgrade Node Binary & Restart Chain
Roll back node binary to Spec v10 release and restart services:
```bash
ansible-playbook -i /opt/verdis-chain-rust/deploy/hosts /opt/verdis-chain-rust/deploy/start_validators.yml
```

#### Step 6: Post-Mortem & Patch Execution
1. Isolate the panicking storage key using `try-runtime --uri ...`.
2. Apply missing decode logic or storage default in `/opt/verdis-chain-rust/pallets/`.
3. Submit a corrected patch Wasm binary for emergency Technical Committee approval.

---

**Approved by Verdis Blockchain Core Engineering Team**  
*Document maintained in workspace: `verdis-storage-migration-strategy.md`*
