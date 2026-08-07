# Verdis Chain — Security Audit Report

**Date:** August 7, 2026
**Auditor:** EvolvixOS (Static Analysis)
**Scope:** All 7 pallets (DPoS, AmmDex, Eco, Tokenomics, Vesting, Storage) + Runtime
**Codebase:** 3,417 lines of Rust (Substrate FRAME)

---

## Summary

| Severity | Count |
|----------|-------|
| Critical | 1 |
| High | 3 |
| Medium | 4 |
| Low | 3 |
| Info | 5 |

**Overall Security Score: 72/100**

---

## Critical Findings

### C1: Division by Zero in `remove_liquidity`
**File:** `pallets/amm-dex/src/lib.rs`
**Severity:** Critical
**Description:** The `remove_liquidity` function calculates token amounts using `pool.reserve_a.saturating_mul(lp_amount) / pool.total_lp`. If `total_lp` is zero (e.g., after a pool is drained or in an edge case during creation), this division will **panic** and crash the node.
**Code:**
```rust
let amount_a = pool.reserve_a.saturating_mul(lp_amount) / pool.total_lp;  // PANIC if total_lp == 0
let amount_b = pool.reserve_b.saturating_mul(lp_amount) / pool.total_lp;  // PANIC if total_lp == 0
```
**Fix:** Add a zero check:
```rust
ensure!(pool.total_lp > BalanceOf::<T>::zero(), Error::<T>::PoolEmpty);
let amount_a = pool.reserve_a.saturating_mul(lp_amount) / pool.total_lp;
```

---

## High Findings

### H1: `update_green_score` Allows Self-Scoring
**File:** `pallets/dpos/src/lib.rs:380`
**Severity:** High
**Description:** `update_green_score` uses `ensure_signed(origin)` and only checks that the caller is a validator. This allows **any validator to set their own green score to 255** (maximum), undermining the entire eco-credibility system. Green scores should be assigned by a council or oracle, not self-reported.
**Fix:**
```rust
pub fn update_green_score(origin: OriginFor<T>, validator: T::AccountId, score: u8) -> DispatchResult {
    ensure_root(origin)?;  // Only council/root can update scores
    ensure!(Validators::<T>::contains_key(&validator), Error::<T>::NotValidator);
    // ...
}
```

### H2: `mint_carbon_credit` Has No Authorization
**File:** `pallets/eco/src/lib.rs:229`
**Severity:** High
**Description:** `mint_carbon_credit` uses `ensure_signed(origin)` — **any account can mint carbon credits** without authorization. While credits must be verified by root (`verify_carbon_credit`), the ability to create unlimited unverified credits could spam storage and mislead users viewing the explorer.
**Fix:** Require root or a designated "credit issuer" role:
```rust
pub fn mint_carbon_credit(origin: OriginFor<T>, ...) -> DispatchResult {
    ensure_root(origin)?;  // Or T::CreditIssuer::ensure_origin(origin)?
    // ...
}
```

### H3: LP Minting Overflow in `create_pool`
**File:** `pallets/amm-dex/src/lib.rs` (create_pool)
**Severity:** High
**Description:** LP tokens are calculated as `(amount_a * amount_b).integer_sqrt()`. If `amount_a` and `amount_b` are large (close to `BalanceOf::MAX`), the multiplication **overflows and panics**. `saturating_mul` is not used here — it's raw `*`.
**Code:**
```rust
let lp_minted = (amount_a * amount_b).integer_sqrt();  // PANIC on overflow
```
**Fix:**
```rust
let lp_minted = amount_a.checked_mul(amount_b)
    .ok_or(Error::<T>::AmountTooLow)?
    .integer_sqrt();
```

---

## Medium Findings

### M1: `create_reforest_project` Has No Authorization
**File:** `pallets/eco/src/lib.rs:343`
**Severity:** Medium
**Description:** Any signed account can create reforest projects. While verification requires root, unlimited project creation can spam storage. Bounded by `MaxReforestProjects` config, but still allows low-quality entries.
**Fix:** Consider requiring root or a council motion for project creation.

### M2: Division by Zero Risk in `swap`
**File:** `pallets/amm-dex/src/lib.rs` (swap)
**Severity:** Medium
**Description:** `let amount_out = numerator / denominator;` where `denominator = reserve_in.saturating_add(amount_in_after_fee)`. If `fee_numerator >= fee_denominator` (misconfiguration), `amount_in_after_fee` could be 0, and if `reserve_in` is also 0, this panics. The `ensure!(amount_out > 0)` check comes **after** the division.
**Fix:**
```rust
ensure!(denominator > BalanceOf::<T>::zero(), Error::<T>::InsufficientLiquidity);
let amount_out = numerator / denominator;
```

### M3: `transfer_carbon_credit` No Origin Check on Recipient
**File:** `pallets/eco/src/lib.rs:315`
**Severity:** Medium
**Description:** Carbon credit transfer checks that the sender owns the credit but doesn't verify the credit is "verified" before transfer. Unverified credits could be transferred to unsuspecting users.
**Fix:** Add a check: `ensure!(credit.verified, Error::<T>::CreditNotVerified)` for transfers, or clearly mark unverified credits in the transfer event.

### M4: No Slashing Amount Validation
**File:** `pallets/dpos/src/lib.rs` (slash_validator)
**Severity:** Medium
**Description:** `slash_validator` accepts an arbitrary `penalty: BalanceOf<T>` parameter. While it's capped at `val.stake` via `.min()`, there's no minimum or maximum bound on the penalty parameter itself. A root key compromise could slash 100% of all validators' stakes.
**Fix:** Add configurable max slash percentage:
```rust
let max_slash = val.stake.saturating_mul(T::MaxSlashPercentage::get().into()) / 100u32.into();
ensure!(slash_amount <= max_slash, Error::<T>::SlashExceedsMaximum);
```

---

## Low Findings

### L1: No Event for Failed Operations
**Severity:** Low
**Description:** Several functions return errors without emitting events. While this is standard in Substrate, logging failed attempts (especially for slashing, minting) would improve auditability.

### L2: `create_pool` LP Calculation Uses `integer_sqrt`
**Severity:** Low
**Description:** Using `integer_sqrt` for LP token calculation is simpler than the geometric mean used by Uniswap V2, but it's less precise for asymmetric pools. Consider using `amount_a.checked_mul(amount_b).ok_or(...)?.integer_sqrt()` with overflow protection.

### L3: No Pool Fee Cap
**File:** `pallets/amm-dex/src/lib.rs`
**Severity:** Low
**Description:** The fee is configurable via `FeeNumerator`/`FeeDenominator` but there's no runtime check that `FeeNumerator < FeeDenominator`. A misconfiguration could make swaps impossible.
**Fix:** Add a genesis config validation: `ensure!(FeeNumerator < FeeDenominator, ...)`.

---

## Info Findings

### I1: All dispatchable functions have origin checks ✅
Every `#[pallet::call]` function takes `origin: OriginFor<T>` and calls either `ensure_signed` or `ensure_root`.

### I2: AMM uses `saturating_add/sub/mul` for most operations ✅
The AMM pallet correctly uses saturating arithmetic for reserve updates, with the exception of `create_pool` (see H3).

### I3: BoundedVec used for all variable-length storage ✅
All Vec<u8> parameters are converted to BoundedVec with max lengths, preventing unbounded storage growth.

### I4: MaxPools, MaxCarbonCredits, MaxReforestProjects configured ✅
Storage is bounded by configurable limits in all pallets.

### I5: Events emitted for all state changes ✅
Every dispatchable function emits events for important state transitions.

---

## Per-Pallet Security Summary

| Pallet | Origin Checks | Math Safety | Storage Safety | Access Control | Score |
|--------|:---:|:---:|:---:|:---:|:---:|
| DPoS | ✅ | ✅ | ✅ | ⚠️ (H1) | 75 |
| AmmDex | ✅ | ⚠️ (C1, H3) | ✅ | ✅ | 65 |
| Eco | ✅ | ✅ | ✅ | ⚠️ (H2, M1) | 70 |
| Tokenomics | ✅ | ✅ | ✅ | ✅ | 90 |
| Vesting | ✅ | ✅ | ✅ | ✅ | 90 |
| Storage | ✅ | ✅ | ✅ | ✅ | 90 |
| Runtime | ✅ | ✅ | ✅ | ✅ | 85 |

---

## Recommended Priority Fixes

1. **C1** — Add zero check before division in `remove_liquidity` (30 min)
2. **H1** — Change `update_green_score` to `ensure_root` (10 min)
3. **H2** — Change `mint_carbon_credit` to `ensure_root` or add issuer role (10 min)
4. **H3** — Use `checked_mul` in `create_pool` LP calculation (10 min)
5. **M2** — Add zero check before division in `swap` (10 min)
6. **M4** — Add max slash percentage config (30 min)

**Estimated fix time:** 2-4 hours
