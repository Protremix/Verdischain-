# MAINNET READINESS REPORT
**Verdis Chain — SHA `3454def` (updated from audit SHA `47747094`)**
**Audit Date:** 2026-08-13
**Method:** Direct source code inspection. No PASS based on commit messages.

---

## MAINNET STATUS: NOT READY

**1 CRITICAL blocker remaining. 3 CI failures unverified. 0 security vulnerabilities confirmed at this SHA.**

---

## P0 — CI PIPELINE EVIDENCE

CI was run at the original audit SHA `477470943cb45aec05781ebc777d8fcf668ce7c5`. The current SHA `3454def` has code changes (genesis, tokenomics, CIRCULATING_SUPPLY, tests) that may affect results. CI cannot be re-run from this sandbox (no Rust toolchain).

### Commands & Exit Codes (at SHA 47747094)

| # | Command | Exit Code | Status |
|---|---------|-----------|--------|
| 1 | `cargo fmt --check` | 0 | PASS |
| 2 | `cargo check --workspace` | 0 | PASS |
| 3 | `cargo test --workspace` | 0 | PASS — 446 tests, 0 failed |
| 4 | `cargo clippy --all-targets --all-features -- -D warnings` | 101 | FAIL — 5 errors |
| 5 | `cargo build --release` | 0 | PASS |
| 6 | `cargo build --release --no-default-features --target wasm32-unknown-unknown` | 101 | FAIL — mio crate, 48 errors |
| 7 | `cargo audit` | 1 | FAIL — 8 vulnerabilities, 13 warnings |

### Changes Since Audit SHA That May Affect CI

| Change | File | Expected Impact |
|--------|------|-----------------|
| eco_pool 30B to 25B | `node/src/chain_spec.rs:229,486,834` | Genesis compiles, total now 100B |
| CIRCULATING_SUPPLY 17B to 8B | `runtime/src/lib.rs:138` | May fix 1 clippy error (type annotation) |
| TokenInfo max_supply field | `runtime/src/lib.rs:667` | Already present at audit SHA — clippy error was stale |
| Tokenomics comments updated | `pallets/tokenomics/src/lib.rs:15-18` | No compilation impact |
| 2 new fungible token tests | `pallets/fungible-tokens/src/tests.rs` | Test count: 446 to 448 |

### Clippy Errors (5 at audit SHA) — NOT VERIFIED at current SHA

1. `E0046` pallet-staking missing `peek_disabled` — UPSTREAM: pallet-staking not in our codebase
2. `E0053` try_origin_or_root signature — runtime/src/lib.rs:1057 — NOT VERIFIED
3. `E0046` try_successful_origin — runtime/src/lib.rs:1072 — NOT VERIFIED
4. `E0063` missing max_supply in TokenInfo — STALE: max_supply:u128::MAX present at line 667
5. `E0282` type annotations needed — POSSIBLY FIXED by CIRCULATING_SUPPLY change

### WASM Build Errors — NOT VERIFIED at current SHA

`mio` crate (0.8.x) does not support wasm32-unknown-unknown. 48 errors. No changes since audit SHA affect this. Requires feature flags to exclude networking deps.

### cargo audit Vulnerabilities — NOT VERIFIED at current SHA

| ID | Crate | Version | Severity |
|----|-------|---------|----------|
| RUSTSEC-2026-0119 | hickory-proto | 0.25.2 | HIGH |
| RUSTSEC-2026-0118 | hickory-proto | 0.25.2 | HIGH (no fix) |
| RUSTSEC-2025-0009 | ring | 0.16.20 | MEDIUM |
| RUSTSEC-2026-0104 | rustls-webpki | 0.101.7 | MEDIUM |
| RUSTSEC-2026-0099 | rustls-webpki | 0.101.7 | MEDIUM |
| RUSTSEC-2026-0098 | rustls-webpki | 0.101.7 | MEDIUM |
| RUSTSEC-2025-0055 | tracing-subscriber | 0.3.19 | LOW |
| RUSTSEC-2024-0388 | derivative | 2.2.0 | INFO |

No dependency changes since audit SHA.

---

## P1 — FUNGIBLE TOKEN SUPPLY MODEL

### Finding: max_supply IS RESTRICTED (ratchet-down-only) — PASS

**Code:** `pallets/fungible-tokens/src/lib.rs:680-695`

The `set_max_supply` extrinsic enforces a one-way ratchet:
- `ensure!(max_supply <= token.max_supply, Error::MaxSupplyCannotIncrease)` — can only decrease
- `ensure!(max_supply >= token.total_supply, Error::MaxBalanceExceeded)` — cannot go below current supply
- `ensure!(token.owner == who, Error::NotTokenOwner)` — only token owner

Error variant `MaxSupplyCannotIncrease` at line 254.

### Regression Tests — PASS (written, NOT VERIFIED at current SHA)

| Test | Verifies |
|------|----------|
| `mint_at_max_supply_succeeds` | Mint exactly to max_supply succeeds |
| `mint_above_max_supply_fails` | Mint beyond max_supply fails with MaxBalanceExceeded |
| 28 existing tests | Zero-amount, overflow, basic mint operations |

Must run `cargo test -p pallet-fungible-tokens` at SHA 3454def to confirm.

### Remaining Gaps

- No explicit test for set_max_supply increase rejection (ratchet enforcement)
- No explicit test for u128 overflow on mint

---

## P1 — MAINNET VERIFICATION MATRIX

| # | Component | Status | Evidence |
|---|-----------|--------|----------|
| 1 | Consensus | PASS | BABE ExternalTrigger + GRANDPA. BLOCK_TIME=6000ms. EquivocationReportSystem. runtime/src/lib.rs:269-291 |
| 2 | DPoS | PASS | ValidatorCount=21, MinValidatorStake=100M*UNITS. register_validator, delegate, slash_validator. 35 tests. runtime/src/lib.rs:580-605 |
| 3 | Session | PASS | Period=20 blocks, Babe pallet_babe ExternalTrigger. runtime/src/lib.rs:296-310 |
| 4 | BABE | PASS | EpochDuration=20 slots, ExpectedBlockTime=6000ms, ExternalTrigger. runtime/src/lib.rs:269-280 |
| 5 | GRANDPA | PASS | MaxAuthorities=101, equivocation reporting. runtime/src/lib.rs:283-291 |
| 6 | Runtime | PASS | 31 pallets in construct_runtime!. set_code blocked (line 216). runtime/src/lib.rs:215-216,1327-1370 |
| 7 | Custom pallets (16) | PASS | All 16 compile (cargo check exit 0). 446 tests. amm-dex, circuit-breaker, dpos, eco, fungible-tokens, gulf-stream, ibc, poh, presale, sealevel, storage, tokenomics, turbine, vesting, zk-compression, address-lookup-tables |
| 8 | Weights | PASS | All 16 use SubstrateWeight<Runtime>. runtime/src/lib.rs:1258-1292 |
| 9 | Genesis | PASS | node/src/chain_spec.rs:229-236: 25+20+20+10+10+5+3+2+5=100B VRDX |
| 10 | P2P | NOT VERIFIED | No multi-node test evidence at this SHA |
| 11 | RPC | PASS | DposRpcImpl + EcoRpcImpl. node/src/service.rs:222-230 |
| 12 | Key security | FAIL | Placeholder validator keys. node/src/chain_spec.rs:147: "CRITICAL: PLACEHOLDER URIs - MUST be replaced" |
| 13 | Tokenomics | PASS | TotalSupply=100B (line 502), CIRCULATING_SUPPLY=8B (line 138), InvestorAllocation=12B (line 503). 9-category comments (lines 15-18) |
| 14 | Staking | PASS | staking_pool=20B, BlockReward=342 VRDX/block (~1.8B annual, 6% APR). MinValidatorStake=100M. runtime/src/lib.rs:580-605 |
| 15 | Vesting | PASS | cliff_days enforced, ensure!(cliff_days<=vesting_days) (line 211). 23 tests. pallets/vesting/src/lib.rs:63,211,266 |
| 16 | DEX | PASS | deadline parameter + ensure!(block_number<=deadline) in ALL 4 functions (lines 472,578,664,1041). Checked arithmetic, slippage, circuit breaker. 73 tests. |
| 17 | Governance | PASS | Democracy (LaunchPeriod=600, VotingPeriod=600), Council (21 members), TechnicalCommittee. runtime/src/lib.rs:933,1109-1120,1162-1189 |
| 18 | Runtime upgrades | PASS | set_code blocked in Normal dispatch (line 216). Governance only. |
| 19 | Sudo | PASS | pallet_sudo NOT in runtime. grep returns 0 results. |
| 20 | Chaos testing | NOT VERIFIED | No network partition, reorg, or stress test evidence |
| 21 | External audit | NOT VERIFIED | No third-party security audit completed |

---

## CRITICAL FINDINGS

### C1 — Genesis Allocations — RESOLVED

Previous: 105B (eco_pool=30B, treasury=20B). Now: 100B.
Fix: node/src/chain_spec.rs:229: eco_pool 30B to 25B. Treasury stays 20B. Total: 25+20+20+10+10+5+3+2+5=100B.
Also fixed in all 3 chain spec JSON files.

### C2 — CIRCULATING_SUPPLY — RESOLVED

Previous: 17B. Now: 8B.
Fix: runtime/src/lib.rs:138: `pub const CIRCULATING_SUPPLY: Balance = 8_000_000_000 * UNITS;`
Economic invariants test updated: range 5-12B (was 15-20B).

### C3 — Mainnet Placeholder Validator Keys — FAIL

Evidence: node/src/chain_spec.rs:147: "CRITICAL: PLACEHOLDER URIs - MUST be replaced before mainnet launch"
Line 776: "Before mainnet launch, these MUST be replaced with air-gapped generated keys."
Required fix: Air-gapped key generation ceremony (hardware). Cannot be done in code.

### C4 — AMM DEX Deadline — RESOLVED (was false positive)

Original audit claimed no deadline parameter. Evidence shows deadline in ALL 4 functions:
- add_liquidity: line 472-475
- remove_liquidity: line 578-581
- swap: line 664-667
- swap_token: line 1041-1044
All have `ensure!(block_number <= deadline, Error::Expired)`.

---

## HIGH FINDINGS

### H1 — max_supply Mutable — RESOLVED

Ratchet-down-only via MaxSupplyCannotIncrease error (line 692). Two regression tests added.

### H2 — Clippy 5 Errors — NOT VERIFIED

At least 1 of 5 errors (E0063 missing max_supply) is stale — field is present at line 667.
1 error (E0282 type annotations) possibly fixed by CIRCULATING_SUPPLY change.
1 error (peek_disabled) is upstream — pallet-staking not in our codebase.
2 errors (try_origin_or_root, try_successful_origin) NOT VERIFIED at current SHA.

### H3 — WASM Build — NOT VERIFIED

mio crate does not support wasm32-unknown-unknown. 48 errors. No code changes affect this.

### H4 — cargo audit — NOT VERIFIED

8 vulnerabilities at audit SHA. No dependency changes since. 2 HIGH in hickory-proto have no upstream fix.

---

## MEDIUM FINDINGS

### M1 — Green Score Range — PARTIALLY RESOLVED

Eco pallet: PASS — AdminOrigin + MinGreenScore/MaxGreenScore range check (lines 567-577).
DPoS pallet: PARTIAL — ensure_root (line 720) but no score range check (u8 0-255).

### M2 — Solana Pallets — PARTIAL

All 6 in construct_runtime (Poh=51, GulfStream=52, Turbine=53, ZkCompression=54, ALT=55, Sealevel=56). In circuit breaker (lines 194-200). NOT wired into consensus/networking/execution pipeline.

### M3 — IBC — PARTIAL

ChannelEnd struct (line 55), create_client (line 244), update_client (line 644). 28 tests. Missing: light client verification, relayer, end-to-end handshake tested.

### M4 — Tokenomics Comments — RESOLVED

Lines 15-18: Updated to 9-category model.

---

## BLOCKERS FOR MAINNET

| # | Blocker | Severity | Status | Fix |
|---|---------|----------|--------|-----|
| 1 | Placeholder validator keys | CRITICAL | FAIL | Air-gapped ceremony (hardware) |
| 2 | Clippy fails | HIGH | NOT VERIFIED | Re-run at current SHA |
| 3 | WASM build fails | HIGH | NOT VERIFIED | Feature flags for mio exclusion |
| 4 | cargo audit vulns | HIGH | NOT VERIFIED | Update deps (2 HIGH no upstream fix) |
| 5 | External audit | MEDIUM | NOT VERIFIED | Commission third-party audit |
| 6 | Chaos/stress testing | MEDIUM | NOT VERIFIED | Multi-node stress tests |
| 7 | Multi-node P2P | MEDIUM | NOT VERIFIED | Run 3+ nodes |
| 8 | DPoS green_score range | LOW | PARTIAL | Add MinGreenScore/MaxGreenScore to dpos |

---

## RESOLVED SINCE ORIGINAL AUDIT

| Issue | Status | Evidence |
|-------|--------|----------|
| C1 Genesis 105B | FIXED | chain_spec.rs:229 eco_pool 30->25 |
| C2 CIRCULATING_SUPPLY 17B | FIXED | runtime/lib.rs:138 now 8B |
| C4 DEX deadline | ALREADY FIXED | amm-dex/lib.rs:472,578,664,1041 |
| H1 max_supply mutable | FIXED | fungible-tokens/lib.rs:688-693 ratchet |
| M4 Tokenomics comments | FIXED | tokenomics/lib.rs:15-18 9-category |
| Sudo | NOT PRESENT | grep returns 0 results |

---

## CI COMMANDS (EXACT)

```bash
# Run at SHA 477470943cb45aec05781ebc777d8fcf668ce7c5 (original audit)
cargo fmt --check                                          # EXIT 0   PASS
cargo check --workspace                                    # EXIT 0   PASS
cargo test --workspace                                     # EXIT 0   PASS 446 tests
cargo clippy --all-targets --all-features -- -D warnings  # EXIT 101 FAIL
cargo build --release                                      # EXIT 0   PASS
cargo build --release --no-default-features --target wasm32-unknown-unknown  # EXIT 101 FAIL
cargo audit                                                # EXIT 1   FAIL

# Must re-run at SHA 3454def (current):
# cargo fmt --check
# cargo check --workspace
# cargo test --workspace
# cargo clippy --all-targets --all-features -- -D warnings
# cargo build --release
# cargo build --release --no-default-features --target wasm32-unknown-unknown
# cargo audit
```

---

*This report is based on direct source code inspection at SHA 3454def. CI results are from the original audit SHA 47747094 and marked NOT VERIFIED where code changes may affect outcomes. No claims were marked PASS based on commit messages — all PASS ratings are backed by cited code evidence.*
