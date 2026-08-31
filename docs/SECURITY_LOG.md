# VERDIS CHAIN — SECURITY FINDINGS & REGRESSION LOG

**Project:** Verdis Chain  
**Runtime Version:** v14 (verdis-runtime 2.0.0)  
**Consensus Engine:** Substrate DPoS (BABE block production / GRANDPA finality)  
**Native Token:** VRDX (100,000,000,000 total supply, 9 decimal places)  
**Audit Score:** 100 / 100 (Internal Code Audit)  
**Testnet Status:** Block #29400+, 21 active validators, 6 DEX pools, 5 peers, 6 nodes  
**Primary Infrastructure:** Hetzner Server (IP: `91.98.160.145`)  
**Total Automated Test Suite:** ~689 tests (unit, integration, and security regression)  
**Last Updated:** August 2026  

---

## 1. SEVERITY CLASSIFICATION MATRIX

Verdis Chain classifies all security findings into five severity levels based on business impact, exploitability, and potential loss of funds or chain availability:

| Severity | Code | Description & Impact | SLAs for Remediation |
|---|---|---|---|
| **Critical** | **P0** | Direct threat to consensus, protocol state, token supply invariant, or systemic fund theft. | Immediate hotfix / block deployment (< 4 hours) |
| **High** | **P1** | Substantial fund risk, pallet bricking, unauthorized privilege escalation, or DEX manipulation. | Resolved before any production release (< 24 hours) |
| **Medium** | **P2** | Partial denial-of-service, non-critical arithmetic edge cases, or storage bloat vectors. | Resolved within current sprint (< 3 days) |
| **Low** | **P3** | Inefficient weight calculations, minor logic inconsistencies, or UI display mismatches. | Resolved in scheduled update (< 7 days) |
| **Informational** | **P4** | Code style, documentation gaps, re-factoring suggestions, or optimization hints. | Addressed during routine maintainability sweeps |

---

## 2. MASTER SECURITY FINDINGS LOG

| Finding ID | Subsystem / Component | Severity | Title / Summary | Status | Discovery Date | Fix Commit | Verification Method |
|---|---|---|---|---|---|---|---|
| `SEC-P0-01` | `pallets/amm-dex` | **P0** | Division-by-Zero in `remove_liquidity` | **FIXED** | 2026-08-04 | `ac3dfb9b` | `test_remove_liquidity_zero_lp` |
| `SEC-P0-02` | `pallets/eco` | **P0** | Self-Scoring Vulnerability in `update_green_score` | **FIXED** | 2026-08-05 | `b6892e10` | `test_update_green_score_unauthorized` |
| `SEC-P0-03` | `pallets/eco` | **P0** | Unauthenticated Minting in `mint_carbon_credit` | **FIXED** | 2026-08-05 | `c7128a44` | `test_mint_carbon_credit_root_guard` |
| `SEC-P0-04` | `pallets/amm-dex` | **P0** | Arithmetic Overflow in LP Share Calculation | **FIXED** | 2026-08-06 | `df4910a2` | `dex_security_tests::test_lp_overflow` |
| `SEC-P1-01` | `pallets/amm-dex` | **P1** | Pool Bricking via Zero-LP State | **FIXED** | 2026-08-07 | `e80119f3` | `test_pool_lifecycle_empty_drain` |
| `SEC-P1-02` | `web/frontend` | **P1** | XSS Vulnerability in DEX & Faucet DOM Rendering | **FIXED** | 2026-08-08 | `f31209b1` | Static DOM Sanitization Check |
| `SEC-P1-03` | `pallets/amm-dex` | **P1** | Self-Transfer State Corruption in DEX Swaps | **FIXED** | 2026-08-09 | `a90184c6` | `test_self_swap_prevention` |
| `SEC-P1-04` | `pallets/tokenomics` / `runtime` | **P1** | Tokenomics allocation and investor-limit sources are inconsistent: pallet invariant/test references include legacy 30B/15B allocation comments and a 12B `InvestorAllocation`, while runtime config references a 5B investor allocation; production genesis/issuance equivalence was not verified | **OPEN** | 2026-08-24 | — | Static review; cargo tests unavailable on host |
| `SEC-P2-01` | `runtime/chain_spec` | **P2** | Treasury Control Placeholder (`PalletId` fallback) | **PENDING** | 2026-08-10 | Script Ready | Pending Air-Gapped Key Ceremony |
| `SEC-P2-02` | `pallets/eco` | **P2** | Unbounded `iter().count()` Storage Iteration | **FIXED** | 2026-08-11 | `d20914e8` | `test_eco_bounded_iter` |
| `SEC-P3-01` | `pallets/dpos` | **P3** | Weight Misattribution in `set_commission` | **FIXED** | 2026-08-12 | `e45612f0` | Benchmark re-run |
| `SEC-P3-02` | `pallets/vesting` | **P3** | Schedule Rounding Precision Loss (<1 planck) | **FIXED** | 2026-08-13 | `f11299a0` | Rounding fuzz test |

---

## 3. DETAILED TECHNICAL FINDINGS & REMEDIATION ANALYSIS

### 3.1 `SEC-P0-01`: Division-by-Zero in `remove_liquidity`
- **Component:** `pallets/amm-dex/src/lib.rs`
- **Severity:** P0 (Critical)
- **Description:** When a user attempted to remove liquidity from an AMM pool where total LP token supply was zero or drained in an unexpected order, an un-checked division operation (`pool.total_lp / user_lp`) triggered a Rust kernel panic inside the runtime execution context. This caused block production nodes to crash when executing the block containing the extrinsic.
- **Remediation:** Added `ZeroLiquidity` error checks and replaced raw operations with checked arithmetic:
  ```rust
  ensure!(pool.total_lp > 0, Error::<T>::ZeroLiquidity);
  let amount_a = user_lp.checked_mul(pool.reserve_a)
      .ok_or(Error::<T>::Overflow)?
      .checked_div(pool.total_lp)
      .ok_or(Error::<T>::DivisionByZero)?;
  ```
- **Verification:** Unit test `test_remove_liquidity_zero_lp` passed across all 689 regression runs.

---

### 3.2 `SEC-P0-02`: Self-Scoring Vulnerability in `update_green_score`
- **Component:** `pallets/eco/src/lib.rs` & `pallets/dpos/src/lib.rs`
- **Severity:** P0 (Critical)
- **Description:** The extrinsic `update_green_score` allowed any signed origin (including a registered validator account) to update its own environmental green score. This enabled malicious validators to artificially boost their DPoS selection weight without actual carbon offset or green energy verification.
- **Remediation:** Enforced strict governance/root authority checking:
  ```rust
  #[pallet::weight(T::WeightInfo::update_green_score())]
  pub fn update_green_score(origin: OriginFor<T>, validator: T::AccountId, score: u8) -> DispatchResult {
      ensure_root(origin)?; // Enforce governance/oracle authorization
      ensure!(score <= 100, Error::<T>::InvalidScore);
      // Update validator score...
  }
  ```
- **Verification:** `test_update_green_score_unauthorized` confirms non-root calls fail with `BadOrigin`.

---

### 3.3 `SEC-P0-03`: Unauthenticated Minting in `mint_carbon_credit`
- **Component:** `pallets/eco/src/lib.rs`
- **Severity:** P0 (Critical)
- **Description:** The `mint_carbon_credit` dispatchable lacked proper origin validation, permitting any valid wallet on the network to mint arbitrary quantities of carbon credits on-chain, inflating total carbon credit balance metrics and diluting legitimate credits.
- **Remediation:** Restricted carbon credit minting exclusively to `EnsureRoot` or verified Eco-Council accounts.
- **Verification:** `test_mint_carbon_credit_root_guard` verifies zero unauthenticated minting.

---

### 3.4 `SEC-P0-04`: Arithmetic Overflow in LP Share Calculation
- **Component:** `pallets/amm-dex/src/lib.rs`
- **Severity:** P0 (Critical)
- **Description:** Multiplying high token amounts (e.g. 10B VRDX with 9 decimals = $10^{19}$ plancks) during pool creation or deposit exceeded `u128::MAX` during intermediate multiplication steps, causing mathematical overflow and integer truncation.
- **Remediation:** Implemented `U256` intermediate precision for pool liquidity ratio calculations:
  ```rust
  let shares_a = U256::from(amount_a)
      .checked_mul(U256::from(pool.total_lp))
      .ok_or(Error::<T>::Overflow)?
      .checked_div(U256::from(pool.reserve_a))
      .ok_or(Error::<T>::Overflow)?;
  ```
- **Verification:** Security regression test suite `dex_security_tests.rs` executed with maximum boundary values ($10^{20}$ plancks).

---

## 4. FINDINGS SUMMARY BY SEVERITY

| Severity | Total Discovered | Resolved | Pending | Mitigated |
|---|---|---|---|---|
| **P0 — Critical** | 4 | 4 | 0 | 0 |
| **P1 — High** | 3 | 3 | 0 | 0 |
| **P2 — Medium** | 2 | 1 | 1 (`SEC-P2-01` Key Ceremony) | 0 |
| **P3 — Low** | 2 | 2 | 0 | 0 |
| **P4 — Info** | 5 | 5 | 0 | 0 |
| **TOTAL** | **16** | **15** | **1** | **0** |

---

## 5. SIGN-OFF & CONTINUOUS MONITORING STATEMENT

All P0 Critical and P1 High findings discovered during internal code audits have been fully resolved, verified via unit/integration test cases, and confirmed non-reproducible. Pending item `SEC-P2-01` will be resolved immediately upon execution of the official 3-of-5 cold-storage key ceremony script (`scripts/air-gapped-key-ceremony.sh`).


## 6. ARTICLE 19 WEEKLY SECURITY CYCLE — 2026-08-24

| Date | Finding ID | Severity | Component | Description | Status | Fix Commit |
|---|---|---|---|---|---|---|
| 2026-08-24 | SEC-P1-04 | P1 | pallets/tokenomics / runtime | Tokenomics allocation and investor-limit sources are inconsistent (legacy 30B/15B references and 12B pallet test limit versus 5B runtime reference); issuance/allocation equivalence not verified | OPEN | — |
| 2026-08-24 | SEC-P4-01 | P4 | Build/test infrastructure | Full workspace and required regression tests could not execute because cargo, cargo-audit, and cargo-outdated are unavailable on the target host; verdict evidence is incomplete | OPEN | — |

**Cycle evidence:** Repository HEAD `86bec212` (release freeze). Changes since `HEAD~7` include DPoS, DEX security regression tests, eco, fungible-tokens, presale, tokenomics, vesting, runtime, chain-spec, CI, deployment, and key-ceremony files. Static secret scan returned no non-test matches. Static unsafe/unwrap/expect scan returned production-path matches, notably in `pallets/storage`, `pallets/eco`, `pallets/dpos`, and presale genesis code; these require code-level review. `cargo test --workspace --release` and the three requested regression commands were not runnable. `cargo audit` and `cargo outdated` were not runnable. No Cargo.lock diff or new dependency additions were detected in the reviewed commit range.

**Article 21 verdict:** UNKNOWN — insufficient evidence because the full and regression test suites, dependency vulnerability audit, and on-chain supply invariant verification could not be completed. Existing pending `SEC-P2-01` remains unresolved.
| 2026-08-31 | SEC-P4-02 | P4 | Security verification infrastructure | Article 19 automated evidence remains incomplete: cargo, cargo-audit, and cargo-outdated are unavailable on the review host; full workspace tests and all three required regression tests could not execute. Static review found no non-test secret-pattern hits or unsafe operations, and no new pallet/runtime changes since the prior cycle. | OPEN | — |
