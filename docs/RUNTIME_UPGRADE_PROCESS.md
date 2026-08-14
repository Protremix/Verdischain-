# Runtime Upgrade Process (ARCH-029)

**Status:** Must be tested with try-runtime before mainnet

---

## 1. Overview

Runtime upgrades on Verdis Chain follow the Substrate storage migration pattern. Upgrades are high-risk operations that can brick the chain if done incorrectly.

## 2. Pre-Upgrade Checklist

- [ ] All tests pass on the new runtime (`cargo test --workspace`)
- [ ] `try-runtime` migration tested on a fork of live state
- [ ] Genesis config changes verified for consistency (`scripts/check_genesis_consistency.py`)
- [ ] Storage version incremented if migrations are needed
- [ ] Weight calculations updated for any modified dispatchables
- [ ] No pallet removed without storage migration (or deliberate storage clear)
- [ ] No pallet added without genesis config
- [ ] CI release gates pass (fmt, clippy, test, tokenomics, release build, WASM build, hygiene)

## 3. Upgrade Process

### 3.1 Development
1. Create new runtime version in `runtime/src/lib.rs` (increment `spec_version`)
2. Implement any storage migrations in the pallet's `on_runtime_upgrade` hook
3. Update tests
4. Run `cargo test --workspace`

### 3.2 Testing
1. Build new WASM runtime: `cargo build --release --target wasm32-unknown-unknown -p verdis-runtime`
2. Use `try-runtime` to test migration on live state:
   ```
   try-runtime --runtime target/wasm32-unknown-unknown/release/verdis_runtime.wasm \
     on-runtime-upgrade live --uri ws://localhost:9944
   ```
3. Verify all storage migrations succeed
4. Verify no panics in `on_runtime_upgrade`

### 3.3 Deployment
1. Submit `set_code` extrinsic via governance (council motion + referendum)
2. Monitor block production after upgrade
3. Verify all pallets functional post-upgrade
4. If failure: emergency rollback via previous WASM (if available)

### 3.4 Post-Upgrade
1. Verify block production continues
2. Run health checks (RPC, DEX, staking, vesting)
3. Update documentation with new spec_version
4. Publish upgrade summary

## 4. Emergency Rollback

If a runtime upgrade causes a chain halt:
1. Validators coordinate to revert to previous runtime WASM
2. Use `set_code` with the previous WASM blob
3. Requires 2/3+ council approval (or emergency root if available)
4. Document the failure in post-mortem

## 5. Governance

- Mainnet: Runtime upgrades require council motion + referendum
- No sudo on mainnet (removed)
- Emergency upgrades require supermajority council approval
- No single party can unilaterally upgrade the runtime
