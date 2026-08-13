# Verdis Chain — Try-Runtime Dry-Run Testing Plan

**Version:** 1.0
**Date:** 2026-08-11
**Status:** Ready for Execution

## Overview

Try-runtime testing verifies that runtime upgrades can be applied safely without breaking state or consensus. This is critical for mainnet readiness — any runtime upgrade must be dry-run tested before deployment.

## Current Status

- Runtime compiles with `try-runtime` feature: ✅ (verified Aug 11 2026)
- Node binary with try-runtime: ❌ (pallet-staking v49 version mismatch — `peek_disabled` trait method missing)
- Workaround: Runtime-level try-runtime tests can be run via `cargo test` with `--features try-runtime`

## Test Categories

### 1. Pre-Upgrade State Snapshot
Create a snapshot of the current chain state before any upgrade:
```bash
# On a running testnet node
curl -X POST http://localhost:9933 -H "Content-Type: application/json" \
  -d id:1
```

### 2. Runtime Upgrade Simulation
Simulate a runtime upgrade by:
1. Build new runtime WASM
2. Compare storage layout between old and new
3. Run `OnRuntimeUpgrade` hook for all pallets
4. Verify no storage corruption

### 3. Fork-Off Testing
Create a fork of the live chain state:
1. Export current chain state
2. Start a new node with the forked state
3. Apply the new runtime
4. Verify the chain continues producing blocks

### 4. Migration Testing
For each pallet that has storage migrations:
1. Run `pre_upgrade()` hook
2. Verify storage state
3. Run `on_runtime_upgrade()`
4. Run `post_upgrade()` hook
5. Verify all storage items are valid

## Execution Plan

### Phase 1: Runtime-Level Tests (Current)
```bash
# Build runtime with try-runtime
cargo build --features try-runtime -p verdis-runtime

# Run try-runtime enabled tests
cargo test --features try-runtime -p verdis-runtime
```

### Phase 2: Node-Level Dry Runs (After Substrate Upgrade)
```bash
# Build node with try-runtime
cargo build --features try-runtime -p verdis-chain

# Create snapshot from live testnet
./verdis try-runtime create-snapshot --uri ws://localhost:9944 --path snapshot.json

# Run pre-upgrade check
./verdis try-runtime pre-upgrade --uri ws://localhost:9944

# Apply runtime upgrade on snapshot
./verdis try-runtime on-runtime-upgrade live --uri ws://localhost:9944 --path snapshot.json

# Run post-upgrade check
./verdis try-runtime post-upgrade --uri ws://localhost:9944
```

### Phase 3: Fork-Off Testing
```bash
# Export live chain state
./verdis export-state --chain testnet --base-path /tmp/chain > state.json

# Fork-off with new runtime
./verdis try-runtime fork-off --chain testnet --base-path /tmp/fork --runtime wasm/new_runtime.wasm

# Verify fork produces blocks
./verdis --chain /tmp/fork/chain-spec.json --alice --validator
```

## Blockers

1. **pallet-staking v49 version mismatch**: The `peek_disabled` trait method is missing from `pallet-session` migration. This requires either:
   - Upgrading `pallet-session` to a compatible version
   - Or removing `pallet-staking` from the try-runtime feature dependencies
   - **Priority:** P2 (try-runtime testing can proceed at runtime level without the full node binary)

## Acceptance Criteria

- [ ] Runtime compiles with `--features try-runtime` ✅
- [ ] All pallets implement `TryRuntime`/`OnRuntimeUpgrade` hooks
- [ ] Pre-upgrade snapshot can be created
- [ ] Runtime upgrade simulation succeeds
- [ ] Post-upgrade state is valid
- [ ] Fork-off test produces blocks
- [ ] No storage corruption detected
