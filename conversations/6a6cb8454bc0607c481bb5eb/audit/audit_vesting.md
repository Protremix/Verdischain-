# Verdis Vesting Pallet — Security Review

## Summary Table

| # | Severity | Location | Issue |
|---|----------|----------|-------|
| 1 | CRITICAL | `release_vested` ~L195 | Double-block-time computation creates window for re-entrancy-like state inconsistency |
| 2 | CRITICAL | `release_vested` ~L215 | Integer division truncation in vested amount causes permanent token lock (dust never released) |
| 3 | CRITICAL | `do_assign_vesting` ~L290 | Public `pub` function with no origin check — any pallet/extrinsic can assign vesting to arbitrary accounts |
| 4 | CRITICAL | `release_vested` ~L235 | `LockedBalances` decremented by `total_releasable` but computed in first pass; second pass may compute different value if block advances (TOCTOU) |
| 5 | HIGH | `release_vested` ~L195 | `try_into().unwrap_or(0)` silently caps elapsed blocks at u32::MAX, causing incorrect vesting for long-running chains |
| 6 | HIGH | `release_vested` ~L215 | Vesting math: `saturating_mul` on Balance×u32 can overflow before division; no checked arithmetic |
| 7 | HIGH | `release_vested` ~L240 | `LockedBalances` can go negative relative to actual lock — balance inconsistency if `total_releasable > LockedBalances` |
| 8 | HIGH | `do_assign_vesting` | No check that `amount <= free_balance(who)` — can assign vesting for more than account holds |
| 9 | MEDIUM | `release_vested` ~L225 | Storage read (`Schedules`) inside `mutate` closure — nested storage ops violate atomicity guarantees |
| 10 | MEDIUM | `release_vested` | After full vesting, `UserVestings` entry is never cleaned up — unbounded storage growth |
| 11 | MEDIUM | `release_vested` | `NothingToRelease` emitted as error but `LockUpdated` event still fires if lock is zero |
| 12 | MEDIUM | `do_assign_vesting` | `_schedule` is fetched but only used to confirm existence — `total_amount` on schedule is never validated against `amount` |
| 13 | LOW | `add_schedule` | Error `VestingNotStarted` reused for both `vesting_days == 0` and `cliff_days > vesting_days` — misleading |
| 14 | LOW | Genesis `build` | `unwrap_or_default()` silently truncates labels >64 bytes — should panic or skip with warning |
| 15 | LOW | `release_vested` | `block_time_ms` hardcoded as `5000` — not a config constant, breaks on different block times |

---

## Detailed Findings

---

### CRITICAL-1: TOCTOU State Inconsistency — Two-Pass Block Number

**Location:** `release_vested`, ~L195 and ~L220

**Description:**
The function computes `total_releasable` in a first pass at the current block, then re-computes the per-entry amounts in a second pass inside `mutate`. If the block number were to change between passes (impossible in single-block execution, but the code structure is fragile and copy-paste error prone), or if a future refactor introduces async logic, the two passes can diverge. More concretely, the `current_block` is captured once, but the second pass re-runs the identical logic. The real bug is that the second pass result may differ from the first pass if schedules are mutated mid-flight — the code reads `Schedules` inside a `mutate` on `UserVestings`.

**Fix:** Capture all computed values in the first pass and apply them directly in the second pass without recomputation.

```rust
// BEFORE: two independent computation passes with potential divergence
let mut total_releasable = BalanceOf::<T>::zero();
for v in &vesting {
    // ... compute releasable ...
    total_releasable = total_releasable.saturating_add(releasable);
}
UserVestings::<T>::mutate(&who, |vests| {
    if let Some(vests) = vests {
        for v in vests.iter_mut() {
            // ... re-compute identically ...
            v.released = v.released.saturating_add(releasable);
        }
    }
});
LockedBalances::<T>::mutate(&who, |l| *l = l.saturating_sub(total_releasable));

// AFTER: single pass, store per-entry results, apply atomically
let current_block = frame_system::Pallet::<T>::block_number();
let blocks_per_day = 17_280u32; // TODO: make configurable

// Phase 1: collect (index, new_released, new_vested, releasable) without mutation
let vesting = UserVestings::<T>::get(&who).ok_or(Error::<T>::NoVestingForAccount)?;
let mut updates: Vec<(usize, BalanceOf<T>, BalanceOf<T>, BalanceOf<T>)> = Vec::new();
let mut total_releasable = BalanceOf::<T>::zero();

for (i, v) in vesting.iter().enumerate() {
    let elapsed_blocks: u32 = current_block
        .saturating_sub(v.start_block)
        .try_into()
        .unwrap_or(u32::MAX);
    let elapsed_days = elapsed_blocks / blocks_per_day;

    let schedule = Schedules::<T>::get(&v.schedule).ok_or(Error::<T>::ScheduleNotFound)?;

    if elapsed_days < schedule.cliff_days {
        continue;
    }

    let vested = if elapsed_days >= schedule.vesting_days {
        v.total_amount
    } else {
        // Safe: use checked math (see CRITICAL-2 fix below)
        let numer = v.total_amount
            .checked_mul(&elapsed_days.saturated_into())
            .ok_or(ArithmeticError::Overflow)?;
        numer / schedule.vesting_days.saturated_into()
    };

    let releasable = vested.saturating_sub(v.released);
    if releasable.is_zero() {
        continue;
    }
    let new_released = v.released.checked_add(&releasable).ok_or(ArithmeticError::Overflow)?;
    total_releasable = total_releasable.checked_add(&releasable).ok_or(ArithmeticError::Overflow)?;
    updates.push((i, new_released, vested, releasable));
}

ensure!(!total_releasable.is_zero(), Error::<T>::NothingToRelease);

// Phase 2: apply all updates atomically
UserVestings::<T>::try_mutate(&who, |maybe_vests| -> DispatchResult {
    let vests = maybe_vests.as_mut().ok_or(Error::<T>::NoVestingForAccount)?;
    for (i, new_released, new_vested, _) in &updates {
        vests[*i].released = *new_released;
        vests[*i].vested = *new_vested;
    }
    Ok(())
})?;

// Phase 3: update lock
LockedBalances::<T>::try_mutate(&who, |l| -> DispatchResult {
    *l = l.checked_sub(&total_releasable).ok_or(ArithmeticError::Underflow)?;
    Ok(())
})?;
```

---

### CRITICAL-2: Integer Division Truncation Causes Permanent Token Lock

**Location:** `release_vested`, ~L215 and ~L228

**Description:**
The vested amount calculation uses integer division which truncates. The final fractional tokens (up to `vesting_days - 1` balance units) can never be released because `vested` never reaches `total_amount` until `elapsed_days >= vesting_days`. This means users permanently lose dust amounts. Worse, `saturating_mul` is used before division — for large balances and large `elapsed_days`, this intermediate value **overflows** u128 silently (saturating to u128::MAX), producing a wildly incorrect `vested` value that could exceed `total_amount`.

```rust
// BEFORE: overflow risk + truncation
let vested = if elapsed_days >= schedule.vesting_days {
    v.total_amount
} else {
    v.total_amount.saturating_mul(elapsed_days.saturated_into())
        / schedule.vesting_days.saturated_into()
};

// AFTER: checked multiplication, correct ceiling for final period
use frame_support::traits::tokens::Balance;
use sp_runtime::ArithmeticError;

let vested = if elapsed_days >= schedule.vesting_days {
    v.total_amount
} else {
    // checked_mul prevents silent overflow
    let elapsed: BalanceOf<T> = elapsed_days.saturated_into();
    let total_days: BalanceOf<T> = schedule.vesting_days.saturated_into();
    v.total_amount
        .checked_mul(&elapsed)
        .ok_or(ArithmeticError::Overflow)?
        .checked_div(&total_days)
        .ok_or(ArithmeticError::DivisionByZero)?
};
```

---

### CRITICAL-3: `do_assign_vesting` is `pub` with No Origin Guard

**Location:** `do_assign_vesting`, ~L280

**Description:**
The function is declared `pub fn do_assign_vesting(...)` with a comment stating "no origin check." This means **any other pallet** in the runtime can call this function and assign vesting schedules to any account, locking arbitrary amounts. An attacker pallet or misconfigured coupling could grief users by locking their entire balance.

```rust
// BEFORE: completely open, any pallet can call
pub fn do_assign_vesting(
    who: T::AccountId,
    schedule_label: Vec<u8>,
    amount: BalanceOf<T>,
) -> DispatchResult {

// AFTER: restrict via a dedicated authorization trait, or at minimum document
// the coupling surface and restrict to a trusted caller type.
// Option A — add a caller allowlist trait to Config:
pub trait Config: frame_system::Config {
    // ... existing items ...
    /// Privileged origin that is allowed to call do_assign_vesting
    type AssignVestingOrigin: EnsureOrigin<Self::RuntimeOrigin>;
}

// In the public API, wrap with origin check:
pub fn do_assign_vesting(
    caller: &T::AccountId,   // or pass origin and verify
    who: T::AccountId,
    schedule_label: Vec<u8>,
    amount: BalanceOf<T>,
) -> DispatchResult {
    // Verify caller is the presale pallet's account or a whitelisted account
    ensure!(
        T::AuthorizedCallers::contains(caller),
        Error::<T>::Unauthorized
    );
    // ... rest of logic
}

// Option B (simpler): make it pub(crate) and expose via a trait
pub(crate) fn do_assign_vesting(
    who: T::AccountId,
    schedule_label: Vec<u8>,
    amount: BalanceOf<T>,
) -> DispatchResult {
```

---

### CRITICAL-4: `LockedBalances` Can Underflow Relative to Actual Lock

**Location:** `release_vested`, ~L235

**Description:**
`LockedBalances` is decremented by `total_releasable`, but there is no check that `LockedBalances::get(&who) >= total_releasable`. If the storage drifts (e.g., due to external lock manipulation or a previous bug), this could produce an incorrect lock value. The `saturating_sub` hides this silently.

```rust
// BEFORE: silent saturation hides accounting errors
LockedBalances::<T>::mutate(&who, |l| *l = l.saturating_sub(total_releasable));

// AFTER: checked subtraction with explicit error
LockedBalances::<T>::try_mutate(&who, |l| -> DispatchResult {
    *l = l.checked_sub(&total_releasable)
        .ok_or(ArithmeticError::Underflow)?;
    Ok(())
})?;
```

---

### HIGH-1: `try_into().unwrap_or(0)` Silently Zeroes Elapsed Blocks

**Location:** `release_vested`, ~L200

**Description:**
`BlockNumberFor<T>` is typically `u32` or `u64`. When converting to `u32`, if the elapsed block count exceeds `u32::MAX` (~136 years at 5s blocks), `try_into` fails and `unwrap_or(0)` returns **zero elapsed blocks**, making it appear the user has just started vesting. This would prevent any releases after that point.

```rust
// BEFORE: silently returns 0 on overflow
let elapsed_blocks: u32 = current_block
    .saturating_sub(v.start_block)
    .try_into()
    .unwrap_or(0);

// AFTER: saturate to u32::MAX (equivalent to "very long time elapsed")
let elapsed_blocks: u32 = current_block
    .saturating_sub(v.start_block)
    .try_into()
    .unwrap_or(u32::MAX);
// If elapsed_blocks >= vesting_days * blocks_per_day, full amount is vested anyway.
```

---

### HIGH-2: No Validation That Account Has Sufficient Balance for Vesting Assignment

**Location:** `do_assign_vesting`, ~L285

**Description:**
A root caller can assign any `amount` to any account regardless of the account's actual balance. The lock is set via `Currency::set_lock` which does not fail if `amount > free_balance`. This misleads downstream code into thinking there are more locked tokens than the account holds. The `LockedBalances` accounting will then be inconsistent with actual balances.

```rust
// BEFORE: no balance check
let new_locked = LockedBalances::<T>::get(&who)
    .checked_add(&amount)
    .ok_or(Error::<T>::MaxVestingSchedules)?;
LockedBalances::<T>::insert(&who, new_locked);
T::Currency::set_lock(VESTING_LOCK_ID, &who, new_locked, WithdrawReasons::TRANSFER);

// AFTER: validate amount against free balance
let free = T::Currency::free_balance(&who);
let current_locked = LockedBalances::<T>::get(&who);
ensure!(
    amount <= free.saturating_sub(current_locked),
    Error::<T>::InsufficientUnlocked
);
let new_locked = current_locked
    .checked_add(&amount)
    .ok_or(ArithmeticError::Overflow)?;
LockedBalances::<T>::insert(&who, new_locked);
T::Currency::set_lock(VESTING_LOCK_ID, &who, new_locked, WithdrawReasons::TRANSFER);
```

---

### MEDIUM-1: Storage Read Inside `mutate` Closure

**Location:** `release_vested`, ~L225

**Description:**
`Schedules::<T>::get(&v.schedule)` is called inside `UserVestings::<T>::mutate(...)`. Substrate's storage is not transactional within a closure by default — reads inside a `mutate` are fine, but this pattern makes it easy to accidentally introduce writes that conflict, and it duplicates the schedule lookup already done in the first pass.

```rust
// BEFORE: schedule re-read inside mutate
UserVestings::<T>::mutate(&who, |vests| {
    if let Some(vests) = vests {
        for v in vests.iter_mut() {
            let schedule = Schedules::<T>::get(&v.schedule); // nested read
            if let Some(s) = schedule { ... }
        }
    }
});

// AFTER: pre-compute all values before mutate (see CRITICAL-1 fix),
// and pass them into the closure as a pre-built map:
let updates: BTreeMap<usize, (BalanceOf<T>, BalanceOf<T>)> = ...; // built in phase 1
UserVestings::<T>::try_mutate(&who, |maybe_vests| -> DispatchResult {
    let vests = maybe_vests.as_mut().ok_or(Error::<T>::NoVestingForAccount)?;
    for (i, (new_released, new_vested)) in &updates {
        vests[*i].released = *new_released;
        vests[*i].vested = *new_vested;
    }
    Ok(())
})?;
```

---

### MEDIUM-2: Fully-Vested Entries Never Cleaned Up

**Location:** `release_vested`

**Description:**
When a user fully vests all schedules, the `UserVestings` entry is never removed. Over many IDO rounds, accounts accumulate dead entries up to the `ConstU32<16>` limit, preventing new vesting assignments. The `UserVestings` entry should be removed when all entries are fully released.

```rust
// BEFORE: no cleanup after full release
UserVestings::<T>::mutate(&who, |vests| {
    // ... updates only, never removes ...
});

// AFTER: remove fully vested entries, and remove account entry if empty
UserVestings::<T>::try_mutate(&who, |maybe_vests| -> DispatchResult {
    let vests = maybe_vests.as_mut().ok_or(Error::<T>::NoVestingForAccount)?;
    for (i, (new_released, new_vested)) in updates.iter().rev() {
        vests[*i].released = *new_released;
        vests[*i].vested = *new_vested;
    }
    // Remove fully vested entries
    vests.retain(|v| v.released < v.total_amount);
    Ok(())
})?;

// Remove the storage key entirely if no entries remain
if UserVestings::<T>::get(&who).map(|v| v.is_empty()).unwrap_or(true) {
    UserVestings::<T>::remove(&who);
    // Also clean up LockedBalances if zero
    if LockedBalances::<T>::get(&who).is_zero() {
        LockedBalances::<T>::remove(&who);
    }
}
```

---

### MEDIUM-3: Hardcoded Block Time Constant

**Location:** `release_vested`, ~L197

**Description:**
`block_time_ms = 5000` is hardcoded. Different Substrate runtimes use 6s, 12s, or custom block times. This constant should be a pallet `Config` parameter.

```rust
// BEFORE:
let block_time_ms = 5000u64;
let blocks_per_day = (86_400_000 / block_time_ms) as u32;

// AFTER: add to Config trait
pub trait Config: frame_system::Config {
    // ...
    #[pallet::constant]
    type BlockTimeMs: Get<u64>;
}

// Usage:
let block_time_ms = T::BlockTimeMs::get();
let blocks_per_day = u32::try_from(86_400_000u64 / block_time_ms)
    .map_err(|_| ArithmeticError::Overflow)?;
ensure!(blocks_per_day > 0, ArithmeticError::DivisionByZero);
```

---

### LOW-1: Misleading Error Variant Reuse

**Location:** `add_schedule`, ~L175

```rust
// BEFORE: same error for two different conditions
ensure!(vesting_days > 0, Error::<T>::VestingNotStarted);
ensure!(cliff_days <= vesting_days, Error::<T>::VestingNotStarted);

// AFTER: distinct error variants
#[pallet::error]
pub enum Error<T> {
    // ...
    ZeroVestingDays,
    CliffExceedsVestingPeriod,
}

ensure!(vesting_days > 0, Error::<T>::ZeroVestingDays);
ensure!(cliff_days <= vesting_days, Error::<T>::CliffExceedsVestingPeriod);
```

---

### LOW-2: Genesis Build Silently Truncates Long Labels

**Location:** `genesis_build`, ~L158

```rust
// BEFORE: silently inserts empty key on truncation
let label_bv: BoundedVec<u8, ConstU32<64>> =
    label.clone().try_into().unwrap_or_default();

// AFTER: panic loudly on misconfiguration (genesis errors should be fatal)
let label_bv: BoundedVec<u8, ConstU32<64>> = label
    .clone()
    .try_into()
    .expect("Genesis vesting schedule label exceeds 64 bytes; fix genesis config");
```

---

## Summary of Required Actions

1. **Refactor `release_vested`** to a single-pass collect → atomic apply pattern (fixes CRITICAL-1, MEDIUM-1)
2. **Replace `saturating_mul`** with `checked_mul` in vesting math (fixes CRITICAL-2, HIGH-2)
3. **Restrict `do_assign_vesting`** access via an `AuthorizedCallers` trait or `pub(crate)` visibility (fixes CRITICAL-3)
4. **Add `checked_sub`** for `LockedBalances` decrement (fixes CRITICAL-4)
5. **Change `unwrap_or(0)` to `unwrap_or(u32::MAX)`** for elapsed block conversion (fixes HIGH-1)
6. **Add balance sufficiency check** before assigning vesting (fixes HIGH-2)
7. **Implement entry cleanup** after full vesting (fixes MEDIUM-2)
8. **Parameterize `block_time_ms`** via `Config` (fixes MEDIUM-3)
9. **Add distinct error variants** for schedule validation (fixes LOW-1)
10. **Panic in genesis** on label truncation (fixes LOW-2)