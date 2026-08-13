# MAINNET READINESS REPORT
**Verdis Chain — SHA `477470943cb45aec05781ebc777d8fcf668ce7c5`**
**Audit Date:** 2026-08-13
**Method:** Direct source code inspection. No PASS based on commit messages.

---

## MAINNET STATUS: 🛑 NOT READY

**4 CRITICAL blockers. 3 CI failures. 8 security vulnerabilities.**

---

## P0 — CI PIPELINE EVIDENCE

All commands run against exact SHA `477470943cb45aec05781ebc777d8fcf668ce7c5`.

### Commands & Exit Codes

| # | Command | Exit Code | Status |
|---|---------|-----------|--------|
| 1 | `cargo fmt --check` | 0 | ✅ PASS |
| 2 | `cargo check --workspace` | 0 | ✅ PASS |
| 3 | `cargo test --workspace` | 0 | ✅ PASS — 446 tests, 0 failed |
| 4 | `cargo clippy --all-targets --all-features -- -D warnings` | 101 | ❌ FAIL — 5 errors |
| 5 | `cargo build --release` | 0 | ✅ PASS |
| 6 | `cargo build --release --no-default-features --target wasm32-unknown-unknown` | 101 | ❌ FAIL — mio crate, 48 errors |
| 7 | `cargo audit` | 1 | ❌ FAIL — 8 vulnerabilities, 13 warnings |

### Test Breakdown (446 total, 0 failures)

| Crate | Tests | Result |
|-------|-------|--------|
| pallet-circuit-breaker | 6 | ok |
| pallet-dpos | 35 | ok |
| pallet-eco | 17 | ok |
| pallet-amm-dex | 73 | ok |
| pallet-fungible-tokens | 28 | ok |
| pallet-vesting | 23 | ok |
| pallet-presale | 18 | ok |
| pallet-ibc | 30 | ok |
| pallet-poh | 12 | ok |
| pallet-gulf-stream | 87 | ok |
| pallet-sealevel | 11 | ok |
| pallet-turbine | 11 | ok |
| pallet-zk-compression | 26 | ok |
| pallet-storage | 11 | ok |
| pallet-tokenomics | 44 | ok |
| pallet-address-lookup-tables | 12 | ok |
| verdis-runtime (integration) | 2 | ok |
| (doc-tests) | 0 | ok |
| **TOTAL** | **446** | **0 failed** |

### Clippy Errors (5 errors)

```
error[E0046]: not all trait items implemented, missing: `peek_disabled`
  --> pallet-staking (lib) — 1 error

error[E0053]: method `try_origin_or_root` has an incompatible type for trait
  --> verdis-runtime (lib)

error[E0046]: not all trait items implemented, missing: `try_successful_origin`
  --> verdis-runtime (lib)

error[E0063]: missing field `max_supply` in initializer of `TokenInfo<_, _>`
  --> verdis-runtime (lib)

error[E0282]: type annotations needed
  --> verdis-runtime (lib)
```

**Root causes:**
1. `pallet-staking` missing `peek_disabled` — Substrate version mismatch
2. `verdis-runtime` `try_origin_or_root` signature — Substrate AdminOrigin trait changed
3. `verdis-runtime` `try_successful_origin` — same trait mismatch
4. `verdis-runtime` `TokenInfo` initializer missing `max_supply` field — struct changed but call site not updated
5. `verdis-runtime` type annotation needed — likely related to above

### WASM Build Errors (48 errors)

```
error[E0432]: unresolved import `crate::sys::IoSourceState`
error[E0432]: unresolved import `crate::sys::tcp`
error[E0433]: cannot find `Selector` in `sys`
error[E0433]: cannot find `event` in `sys`
  --> mio crate (0.8.x) — wasm32-unknown-unknown target
```

**Root cause:** `mio` crate does not support `wasm32-unknown-unknown` target. WASM build requires either:
1. Feature flags to exclude `mio` from WASM build, OR
2. Use `--no-default-features` with correct feature set excluding networking

### cargo audit Vulnerabilities (8 vulnerabilities)

| ID | Crate | Version | Severity | Issue |
|----|-------|---------|----------|-------|
| RUSTSEC-2026-0119 | hickory-proto | 0.25.2 | HIGH | CPU exhaustion O(n²) name compression |
| RUSTSEC-2026-0118 | hickory-proto | 0.25.2 | HIGH | NSEC3 unbounded loop — **No fix available** |
| RUSTSEC-2025-0009 | ring | 0.16.20 | MEDIUM | AES functions panic with overflow checking |
| RUSTSEC-2026-0104 | rustls-webpki | 0.101.7 | MEDIUM | Panic in CRL parsing |
| RUSTSEC-2026-0099 | rustls-webpki | 0.101.7 | MEDIUM | Wildcard name constraints accepted |
| RUSTSEC-2026-0098 | rustls-webpki | 0.101.7 | MEDIUM | URI name constraints incorrectly accepted |
| RUSTSEC-2025-0055 | tracing-subscriber | 0.3.19 | LOW | ANSI escape sequence log poisoning |
| RUSTSEC-2024-0388 | derivative | 2.2.0 | INFO | Unmaintained crate |

### cargo audit Warnings (13 unmaintained crates)

| Crate | Version | Status |
|-------|---------|--------|
| derivative | 2.2.0 | unmaintained |
| fxhash | 0.2.1 | unmaintained |
| instant | 0.1.13 | unmaintained |
| (10 more) | | |

---

## P1 — FUNGIBLE TOKEN SUPPLY MODEL

### Finding: max_supply IS MUTABLE — FAIL

**Code:** `pallets/fungible-tokens/src/lib.rs:679-695`

```rust
pub fn set_max_supply(origin, token_id: u64, max_supply: u128) -> DispatchResult {
    let who = ensure_signed(origin)?;
    let mut token = Tokens::<T>::get(token_id).ok_or(Error::<T>::TokenNotFound)?;
    ensure!(token.owner == who, Error::<T>::NotTokenOwner);
    ensure!(max_supply >= token.total_supply, Error::<T>::MaxBalanceExceeded);
    token.max_supply = max_supply;  // ← CAN INCREASE TO ANY VALUE
    Tokens::<T>::insert(token_id, token);
    Ok(())
}
```

**Evidence:**
- Token owner can call `set_max_supply` to set any value >= current `total_supply`
- Initial `max_supply` at creation = `T::MaxBalance::get()` = `u128::MAX` (unlimited)
- No mechanism prevents increasing `max_supply`
- No test for `max_supply` immutability
- No test for minting at `max_supply`
- No test for minting above `max_supply`
- No test for overflow
- No test for zero amount

### Required Fix: Make max_supply immutable after creation

1. **Remove `set_max_supply` extrinsic** — or make it ratchet-down-only (allow decrease, prevent increase)
2. **Add regression tests:**
   - `test_mint_at_max_supply` — mint exactly to max_supply succeeds
   - `test_mint_above_max_supply` — mint beyond max_supply fails
   - `test_mint_overflow` — mint with u128 overflow fails
   - `test_mint_zero_amount` — mint with 0 amount fails
   - `test_set_max_supply_rejected` — calling set_max_supply fails (if removed)
   - `test_set_max_supply_decrease_only` — decreasing works, increasing fails (if ratcheted)

---

## P1 — MAINNET VERIFICATION MATRIX

| Component | Status | Evidence |
|-----------|--------|----------|
| **Consensus** | PASS | BABE `ExternalTrigger` + GRANDPA configured. `BLOCK_TIME = 6000ms`. EquivocationReportSystem for both. `runtime/src/lib.rs:269-291` |
| **DPoS** | PASS | `ValidatorCount = 21`, `MinValidatorStake = 100M * UNITS`. `register_validator`, `delegate`, `slash_validator` all implemented. 35 tests pass. `runtime/src/lib.rs:570-605` |
| **Session** | PASS | `Period = 20` blocks, `Babe: pallet_babe` with `ExternalTrigger`. Historical feature enabled. `runtime/src/lib.rs:296-310` |
| **BABE** | PASS | `EpochDuration = 20` slots, `ExpectedBlockTime = 6000ms`, `ExternalTrigger` (not SameAuthoritiesForever). `runtime/src/lib.rs:269-280` |
| **GRANDPA** | PASS | `MaxAuthorities = 101`, equivocation reporting configured. `runtime/src/lib.rs:283-291` |
| **Runtime** | PASS | 31 pallets in `construct_runtime!`. `set_code` blocked in Normal dispatch. `runtime/src/lib.rs:215-216, 1327-1370` |
| **Custom pallets (16)** | PASS | All 16 compile (cargo check exit 0). 446 tests pass across all pallets. Pallets: amm-dex, circuit-breaker, dpos, eco, fungible-tokens, gulf-stream, ibc, poh, presale, sealevel, storage, tokenomics, turbine, vesting, zk-compression, address-lookup-tables |
| **Weights** | PASS | All 16 custom pallets use `SubstrateWeight<Runtime>`. Weight files exist. `runtime/src/lib.rs` pallet configs |
| **Genesis** | FAIL | Allocations sum to 105B (30+20+20+10+10+5+3+2+5), not 100B. eco_pool=30B should be 25B. treasury=20B should be 15B. `node/src/chain_spec.rs:841-849` |
| **P2P** | NOT VERIFIED | No multi-node test evidence at this SHA. Previous sessions showed 3-6 nodes with peers, but not verified at this exact commit |
| **RPC** | PASS | Custom RPC extensions for dpos (allValidators, validatorStake, validatorName) and eco (getGreenScore, getAllGreenValidators). Standard Substrate RPC. `runtime/src/lib.rs` RPC section |
| **Key security** | FAIL | Mainnet chain spec uses placeholder validator keys: "MUST be replaced before mainnet launch". `node/src/chain_spec.rs:797` |
| **Tokenomics** | FAIL | Genesis allocations exceed 100B. `CIRCULATING_SUPPLY = 17B` (whitepaper says 8B). Tokenomics pallet comments reference old 8-category model. `runtime/src/lib.rs:138, pallets/tokenomics/src/lib.rs:15-18` |
| **Staking** | PASS | `staking_pool = 20B` in genesis. `BlockReward = 342 VRDX/block` = ~1.8B annual. 6% APR at 30% stake. `runtime/src/lib.rs:583` |
| **Vesting** | PASS | `cliff_days` enforced, linear release after cliff. `ensure!(cliff_days <= vesting_days)`. 23 tests pass. `pallets/vesting/src/lib.rs:63,211,266` |
| **DEX** | PARTIAL | AMM DEX works with 6 pools, checked arithmetic, slippage protection, MaxPriceImpact circuit breaker. **FAIL: no deadline parameter** in swap/liquidity functions. 73 tests pass. `pallets/amm-dex/src/lib.rs` |
| **Governance** | PASS | Democracy (LaunchPeriod=600, VotingPeriod=600), Council (21 members, 2/3 majority for admin actions), TechnicalCommittee. `runtime/src/lib.rs:933,1109-1120,1162-1189` |
| **Runtime upgrades** | PASS | `set_code` blocked in Normal dispatch context. Only via governance. `runtime/src/lib.rs:215-216` |
| **Chaos testing** | NOT VERIFIED | No network partition, reorg, or stress test evidence at this SHA |
| **External audit** | NOT VERIFIED | No third-party security audit completed |

---

## CRITICAL FINDINGS

### C1 — Genesis Allocations Exceed 100B Supply — FAIL

**Evidence:** `node/src/chain_spec.rs:841-849`
```rust
(eco_pool, 30 * bn),        // 30B — should be 25B
(staking_pool, 20 * bn),     // 20B — correct
(treasury_account, 20 * bn), // 20B — should be 15B
(dev_pool, 10 * bn),         // 10B — correct
(dex_pool, 10 * bn),         // 10B — correct
(community_pool, 5 * bn),    // 5B — correct
(seed_pool, 3 * bn),         // 3B — correct
(presale_pool, 2 * bn),     // 2B — correct
(team_multisig, 5 * bn - ...), // ~5B — correct
// TOTAL: 30+20+20+10+10+5+3+2+5 = 105B (exceeds 100B by ~5B)
```

**Required fix:** Change `eco_pool` from `30 * bn` to `25 * bn` and `treasury_account` from `20 * bn` to `15 * bn` in ALL chain specs (dev, testnet, mainnet). New total: 25+20+15+10+10+5+3+2+5 = 100B.

### C2 — CIRCULATING_SUPPLY Mismatch — FAIL

**Evidence:** `runtime/src/lib.rs:138`
```rust
pub const CIRCULATING_SUPPLY: u128 = 17_000_000_000 * UNITS; // 17B
```
Whitepaper claims 8B circulating at TGE. Code says 17B.

**Required fix:** Determine correct TGE circulating supply. If 8B, change to `8_000_000_000 * UNITS`. If 17B, update whitepaper.

### C3 — Mainnet Placeholder Validator Keys — FAIL

**Evidence:** `node/src/chain_spec.rs:797`
```rust
// CRITICAL: No Sudo on mainnet. Sudo is disabled.
// ...
// 21 validators — placeholder keys (MUST be replaced before mainnet launch)
let uris = mainnet_validator_uris();
```

**Required fix:** Generate 21 production validator keypairs via air-gapped ceremony. Replace placeholder URIs in `mainnet_validator_uris()`.

### C4 — AMM DEX Has No Deadline Parameter — FAIL

**Evidence:** `pallets/amm-dex/src/lib.rs` — `swap()`, `add_liquidity()`, `remove_liquidity()` have no `deadline` parameter.

**Required fix:** Add `deadline: T::BlockNumber` parameter to all swap/liquidity extrinsics. Add `ensure!(<frame_system::Pallet<T>>::block_number() <= deadline, Error::<T>::Expired)`.

---

## HIGH FINDINGS

### H1 — Fungible Token max_supply Mutable — FAIL
Token owner can increase max_supply to any value via `set_max_supply`. See P1 section above.

### H2 — Clippy Fails With 5 Errors — FAIL
`cargo clippy --all-targets --all-features -- -D warnings` exits 101. Errors in pallet-staking (missing `peek_disabled`) and verdis-runtime (trait mismatches, missing `max_supply` field, type annotations).

### H3 — WASM Build Fails — FAIL
`cargo build --release --no-default-features --target wasm32-unknown-unknown` exits 101. `mio` crate (48 errors) does not support `wasm32-unknown-unknown`. WASM build needs correct feature flags to exclude networking deps.

### H4 — 8 Security Vulnerabilities — FAIL
`cargo audit` finds 8 vulnerabilities including 2 HIGH (hickory-proto O(n²) and unbounded loop) and 4 MEDIUM (rustls-webpki, ring). 13 unmaintained crate warnings.

---

## MEDIUM FINDINGS

### M1 — Green Score Range Not Enforced
`update_green_score` accepts `u8` (0-255), not restricted to 1-5. `pallets/dpos/src/lib.rs:712`

### M2 — Solana-Inspired Pallets Not Integrated
Gulf Stream, PoH, Sealevel, Turbine, ZK Compression — all exist with tests but are NOT connected to consensus/networking/execution pipeline.

### M3 — IBC Partial Implementation
Client/connection exists, but no `ChannelEnd` struct, no relayer implementation, no light client verification tested.

### M4 — Tokenomics Pallet Comments Stale
`pallets/tokenomics/src/lib.rs:15-18` references old 8-category model: "Community (35%), Treasury (20%), Team (15%), Investors (10%), Staking (10%), Liquidity (5%), Advisors (3%), Airdrop (2%)". Should reference 9-category model.

---

## LOW FINDINGS

### L1 — EpochDuration=20 Slots (120 seconds) Very Short
Frequent epoch changes may cause instability on mainnet. Consider 600+ slots for production.

### L2 — No Multi-Node Test Evidence at This SHA
P2P, GRANDPA quorums, block propagation not tested at this exact commit.

### L3 — No Chaos/Stress Testing
No network partition, reorg, or high-throughput stress test evidence.

---

## BLOCKERS FOR MAINNET

| # | Blocker | Severity | Fix Required |
|---|---------|----------|--------------|
| 1 | Genesis allocations = 105B (should be 100B) | CRITICAL | Fix eco_pool and treasury in all chain specs |
| 2 | CIRCULATING_SUPPLY = 17B (should match whitepaper) | CRITICAL | Align code with whitepaper |
| 3 | Mainnet uses placeholder validator keys | CRITICAL | Air-gapped key generation ceremony |
| 4 | AMM DEX has no deadline parameter | CRITICAL | Add deadline to swap/liquidity extrinsics |
| 5 | Fungible token max_supply is mutable | HIGH | Remove or restrict set_max_supply |
| 6 | Clippy fails (5 errors) | HIGH | Fix trait impls and missing fields |
| 7 | WASM build fails | HIGH | Fix feature flags for WASM target |
| 8 | 8 cargo audit vulnerabilities | HIGH | Update dependencies |
| 9 | No external security audit | MEDIUM | Commission third-party audit |
| 10 | No chaos/stress testing | MEDIUM | Multi-node stress tests |

---

## CI COMMANDS (EXACT)

```bash
# All run at SHA 477470943cb45aec05781ebc777d8fcf668ce7c5

cargo fmt --check                                    # EXIT 0   ✅
cargo check --workspace                              # EXIT 0   ✅
cargo test --workspace                               # EXIT 0   ✅ 446 tests
cargo clippy --all-targets --all-features -- -D warnings  # EXIT 101 ❌
cargo build --release                                # EXIT 0   ✅
cargo build --release --no-default-features --target wasm32-unknown-unknown  # EXIT 101 ❌
cargo audit                                          # EXIT 1   ❌
```

---

*This report is based on direct source code inspection and CI execution at SHA 477470943cb45aec05781ebc777d8fcf668ce7c5. No claims were marked PASS based on commit messages.*
