# Substrate Pallet Code Review: Verdis Presale Pallet

---

## Finding 1: Unbounded Storage Iteration in Whitelist Check

**Severity: HIGH**
**Location: `contribute()`, whitelist check block (~line 290)**

The whitelist check uses `iter_prefix()` to detect if *any* whitelist entry exists for a round. This is an unbounded iteration that reads an unknown number of storage entries, making weight calculation impossible and opening a DoS vector where an attacker (or admin) could create a round with thousands of whitelist entries, making the `contribute()` call prohibitively expensive or exceed block weight limits.

**Before:**
```rust
// Per-round whitelist check
if Whitelist::<T>::iter_prefix(round_id).next().is_some() {
    ensure!(
        Whitelist::<T>::get(round_id, &who),
        Error::<T>::NotWhitelisted
    );
}
```

**After:**
```rust
// Per-round whitelist enforcement via a dedicated flag.
// Use WhitelistEnabled storage instead of iterating all entries.
if WhitelistEnabled::<T>::get(round_id) {
    ensure!(
        Whitelist::<T>::get(round_id, &who),
        Error::<T>::NotWhitelisted
    );
}
```

Add this storage item:
```rust
/// Per-round whitelist enforcement flag. When true, only whitelisted accounts may contribute.
#[pallet::storage]
#[pallet::getter(fn whitelist_enabled)]
pub type WhitelistEnabled<T: Config> =
    StorageMap<_, Blake2_128Concat, u32, bool, ValueQuery>;
```

And add a new admin extrinsic:
```rust
/// Enable or disable whitelist enforcement for a round (admin only).
#[pallet::call_index(7)]
#[pallet::weight(T::WeightInfo::set_whitelist_enabled())]
pub fn set_whitelist_enabled(
    origin: OriginFor<T>,
    round_id: u32,
    enabled: bool,
) -> DispatchResult {
    T::AdminOrigin::ensure_origin(origin)?;
    ensure!(
        Rounds::<T>::contains_key(round_id),
        Error::<T>::RoundNotFound
    );
    WhitelistEnabled::<T>::insert(round_id, enabled);
    Self::deposit_event(Event::WhitelistEnforcementChanged { round_id, enabled });
    Ok(())
}
```

---

## Finding 2: Economic Logic Error — Payment and Token Use the Same Currency

**Severity: CRITICAL**
**Location: `contribute()`, transfer blocks (~lines 327–341)**

The pallet uses a single `T::Currency` for both the payment token and the VRDX token. This means:

1. The buyer sends `payment_amount` of the native token to escrow.
2. The escrow sends `token_amount` of the **same** native token back to the buyer.

With `token_price = 5`, a buyer paying `1` unit receives `5` units — a **5x free money exploit**. Any `token_price > 1` allows infinite value extraction from the escrow. This is only safe if `token_price < 1`, but `Balance` is typically an integer type making that impossible.

The architecture requires two separate currency types: one for payment (e.g., USDT/native) and one for VRDX tokens.

**Before:**
```rust
type BalanceOf<T> =
    <<T as Config>::Currency as Currency<<T as frame_system::Config>::AccountId>>::Balance;

// In contribute():
T::Currency::transfer(&who, &escrow, payment_amount, ExistenceRequirement::KeepAlive)
    .map_err(|_| Error::<T>::InsufficientPayment)?;

T::Currency::transfer(&escrow, &who, token_amount, ExistenceRequirement::AllowDeath)
    .map_err(|_| Error::<T>::InsufficientAllocation)?;
```

**After:**
```rust
// Two separate currency types in Config
pub trait Config: frame_system::Config {
    // ... existing fields ...
    
    /// Currency used for payments (e.g., native token / stablecoin)
    type PaymentCurrency: Currency<Self::AccountId>;
    
    /// Currency used for VRDX token distribution
    type VrdxCurrency: Currency<Self::AccountId>;
}

type PaymentBalanceOf<T> =
    <<T as Config>::PaymentCurrency as Currency<<T as frame_system::Config>::AccountId>>::Balance;

type VrdxBalanceOf<T> =
    <<T as Config>::VrdxCurrency as Currency<<T as frame_system::Config>::AccountId>>::Balance;

// In contribute(), separate transfers:
T::PaymentCurrency::transfer(
    &who,
    &escrow,
    payment_amount,
    ExistenceRequirement::KeepAlive,
).map_err(|_| Error::<T>::InsufficientPayment)?;

T::VrdxCurrency::transfer(
    &escrow,
    &who,
    token_amount,
    ExistenceRequirement::AllowDeath,
).map_err(|_| Error::<T>::InsufficientAllocation)?;
```

---

## Finding 3: State Inconsistency — Transfers Execute Before Storage Updates, Vesting Failure Leaves Inconsistent State

**Severity: HIGH**
**Location: `contribute()`, steps 1–7 (~lines 325–375)**

The comment claims "3. Create vesting entry (if this fails, the transfers above are reverted by the dispatchable's automatic state rollback)" — **this is incorrect**. Substrate does NOT automatically roll back storage changes on `DispatchError`. Currency transfers modify storage immediately. If vesting fails after the two transfers complete, the buyer has sent payment and received tokens, but vesting was never created. The storage counters (`sold`, `TotalRaised`, etc.) are also NOT updated, leaving them inconsistent with the actual on-chain balances.

**Before:**
```rust
// 1. Transfer payment from buyer to presale escrow
T::Currency::transfer(&who, &escrow, payment_amount, ExistenceRequirement::KeepAlive)
    .map_err(|_| Error::<T>::InsufficientPayment)?;

// 2. Transfer purchased VRDX from escrow to buyer
T::Currency::transfer(&escrow, &who, token_amount, ExistenceRequirement::AllowDeath)
    .map_err(|_| Error::<T>::InsufficientAllocation)?;

// 3. Create vesting entry (if this fails, the transfers above are reverted
//    by the dispatchable's automatic state rollback)  ← WRONG COMMENT, WRONG ASSUMPTION
if !round.vesting_label.is_empty() {
    T::Vesting::assign_vesting(
        &who,
        round.vesting_label.clone().into_inner(),
        token_amount,
    )
    .map_err(|_| Error::<T>::VestingFailed)?;
    // ...
}

// 4. Update round sold
Rounds::<T>::mutate(round_id, |round_opt| { ... });
// 5–7. Update storage counters
```

**After:**
```rust
// All fallible operations must be validated BEFORE any state mutation.
// Vesting must be validated first if possible, or use with_transaction for atomicity.

use frame_support::storage::with_transaction;
use sp_runtime::TransactionOutcome;

with_transaction(|| -> TransactionOutcome<DispatchResult> {
    // 1. Transfer payment from buyer to presale escrow
    let transfer_result = T::Currency::transfer(
        &who,
        &escrow,
        payment_amount,
        ExistenceRequirement::KeepAlive,
    );
    if let Err(e) = transfer_result {
        return TransactionOutcome::Rollback(Err(Error::<T>::InsufficientPayment.into()));
    }

    // 2. Transfer VRDX from escrow to buyer
    let token_result = T::Currency::transfer(
        &escrow,
        &who,
        token_amount,
        ExistenceRequirement::AllowDeath,
    );
    if let Err(_) = token_result {
        return TransactionOutcome::Rollback(Err(Error::<T>::InsufficientAllocation.into()));
    }

    // 3. Create vesting entry
    if !round.vesting_label.is_empty() {
        let vesting_result = T::Vesting::assign_vesting(
            &who,
            round.vesting_label.clone().into_inner(),
            token_amount,
        );
        if let Err(_) = vesting_result {
            return TransactionOutcome::Rollback(Err(Error::<T>::VestingFailed.into()));
        }
    }

    // 4. Update all storage counters (only reached if all above succeed)
    Rounds::<T>::mutate(round_id, |round_opt| {
        if let Some(r) = round_opt { r.sold = new_sold; }
    });
    Contributions::<T>::insert(
        round_id,
        &who,
        UserContribution { total_purchased: new_total, total_paid: new_total_paid },
    );
    RoundRaised::<T>::insert(round_id, new_round_raised);
    TotalRaised::<T>::put(new_global_raised);
    TotalSold::<T>::put(new_global_sold);

    TransactionOutcome::Commit(Ok(()))
})?;

// Events emitted outside transaction (after commit)
if !round.vesting_label.is_empty() {
    Self::deposit_event(Event::VestingCreated { ... });
}
Self::deposit_event(Event::Contribution { ... });
```

---

## Finding 4: Missing Round Existence Validation in `NextRoundId` Overflow

**Severity: MEDIUM**
**Location: `create_round()` and `genesis_build()`, `NextRoundId` increment (~lines 248, 213)**

`NextRoundId` is incremented with `round_id + 1` (raw addition), which will silently overflow and wrap to 0 at `u32::MAX`, causing existing round data at ID 0 to be overwritten.

**Before:**
```rust
let round_id = NextRoundId::<T>::get();
Rounds::<T>::insert(round_id, round);
NextRoundId::<T>::put(round_id + 1);
```

**After:**
```rust
let round_id = NextRoundId::<T>::get();
Rounds::<T>::insert(round_id, round);
let next_id = round_id.checked_add(1).ok_or(Error::<T>::CalculationOverflow)?;
NextRoundId::<T>::put(next_id);
```

For genesis (where `?` isn't available):
```rust
let round_id = NextRoundId::<T>::get();
Rounds::<T>::insert(round_id, round);
NextRoundId::<T>::put(
    round_id.checked_add(1).expect("Presale genesis: round_id overflow")
);
```

---

## Finding 5: Missing Cleanup of Per-Round Storage on Round Deletion

**Severity: MEDIUM**
**Location: No `remove_round` extrinsic exists; `RoundRaised`, `RoundFundsCollected`, `Whitelist`, `Contributions` are never cleaned up**

There is no mechanism to remove stale rounds. Over time, `Contributions` (a `StorageDoubleMap`) and `Whitelist` will accumulate unbounded entries that can never be cleaned up, bloating chain state permanently. Additionally, if a round is re-created at a recycled ID (see Finding 4), stale whitelist/contribution data from the old round would silently affect the new round.

**Fix — Add admin cleanup extrinsic:**
```rust
/// Remove a completed round and clean up its associated storage (admin only).
/// Can only be called after funds have been collected.
#[pallet::call_index(8)]
#[pallet::weight(T::WeightInfo::remove_round())]
pub fn remove_round(
    origin: OriginFor<T>,
    round_id: u32,
) -> DispatchResult {
    T::AdminOrigin::ensure_origin(origin)?;

    // Ensure round exists
    ensure!(Rounds::<T>::contains_key(round_id), Error::<T>::RoundNotFound);

    // Only allow removal after funds are collected (or if nothing was raised)
    let raised = RoundRaised::<T>::get(round_id);
    if raised > BalanceOf::<T>::zero() {
        ensure!(
            RoundFundsCollected::<T>::get(round_id),
            Error::<T>::FundsAlreadyCollected // reuse or add RoundFundsNotCollected
        );
    }

    // Clean up round-level storage (O(1))
    Rounds::<T>::remove(round_id);
    RoundRaised::<T>::remove(round_id);
    RoundFundsCollected::<T>::remove(round_id);
    WhitelistEnabled::<T>::remove(round_id);

    // NOTE: Contributions and Whitelist double-maps require separate
    // bounded iteration via a clear_prefix call with a limit,
    // or an off-chain triggered multi-step cleanup extrinsic.
    let _ = Contributions::<T>::clear_prefix(round_id, u32::MAX, None);
    let _ = Whitelist::<T>::clear_prefix(round_id, u32::MAX, None);

    Ok(())
}
```

---

## Finding 6: `per_account_cap` of Zero Allows Unlimited Purchases

**Severity: HIGH**
**Location: `create_round()` (~line 231) and `contribute()` cap check (~line 303)**

When `per_account_cap` is `0`, the condition `new_total <= round.per_account_cap` is `token_amount <= 0`, which is always false for non-zero purchases. This means any `per_account_cap = 0` completely blocks all contributions rather than being treated as "no cap." However, an admin could intend `0` to mean "no cap." The current behavior is surprising and undocumented. It should either be explicitly validated as non-zero, or the check should be gated.

**Before:**
```rust
ensure!(
    new_total <= round.per_account_cap,
    Error::<T>::ExceedsPerAccountCap
);
```

**After:**
```rust
// per_account_cap == 0 means no per-account cap is enforced
if !round.per_account_cap.is_zero() {
    ensure!(
        new_total <= round.per_account_cap,
        Error::<T>::ExceedsPerAccountCap
    );
}
```

And add validation in `create_round` with a comment:
```rust
// per_account_cap of 0 means no per-account cap; document this explicitly.
// If a non-zero cap is required, uncomment the line below:
// ensure!(!per_account_cap.is_zero(), Error::<T>::InvalidPerAccountCap);
```

---

## Finding 7: `collect_funds` Does Not Verify Escrow Has Sufficient Balance

**Severity: HIGH**
**Location: `collect_funds()` (~line 415)**

The `collect_funds()` function transfers `round_raised` from the escrow without verifying the escrow actually holds that amount. If the escrow was drained by a bug, a direct transfer, or another round's collection, the transfer will fail with a generic error rather than the specific `InsufficientEscrowBalance` error, and the `RoundFundsCollected` flag will **not** be set (since the error occurs before that line). This is actually correct behavior (flag only set on success), but the missing balance check means the admin gets a confusing error with no actionable information.

**Before:**
```rust
if round_raised > BalanceOf::<T>::zero() {
    let escrow = T::PalletId::get().into_account_truncating();
    T::Currency::transfer(
        &escrow,
        &beneficiary,
        round_raised,
        ExistenceRequirement::AllowDeath,
    )?;
}

RoundFundsCollected::<T>::insert(round_id, true);
```

**After:**
```rust
if round_raised > BalanceOf::<T>::zero() {
    let escrow = T::PalletId::get().into_account_truncating();
    
    // Explicit escrow balance check for actionable error reporting
    let escrow_balance = T::Currency::free_balance(&escrow);
    ensure!(
        escrow_balance >= round_raised,
        Error::<T>::InsufficientEscrowBalance
    );
    
    T::Currency::transfer(
        &escrow,
        &beneficiary,
        round_raised,
        ExistenceRequirement::AllowDeath,
    )?;
}

// Mark as collected only after successful transfer
RoundFundsCollected::<T>::insert(round_id, true);
```

---

## Finding 8: Missing `VestingCreated` Event When Vesting Label Is Empty

**Severity: LOW**
**Location: `contribute()` (~line 343)**

When `round.vesting_label.is_empty()` the vesting step is skipped silently. Given the struct definition requires a non-empty `vesting_label` via `create_round` validation (`ensure!(!vesting_label.is_empty(), ...)`), this dead code branch is misleading. The `is_empty` guard should be removed or replaced with an invariant assertion.

**Before:**
```rust
if !round.vesting_label.is_empty() {
    T::Vesting::assign_vesting(...).map_err(|_| Error::<T>::VestingFailed)?;
    Self::deposit_event(Event::VestingCreated { ... });
}
```

**After:**
```rust
// vesting_label is guaranteed non-empty by create_round validation.
// Use debug_assert to catch invariant violations in testing.
debug_assert!(
    !round.vesting_label.is_empty(),
    "Round vesting_label should never be empty; enforced at creation"
);

T::Vesting::assign_vesting(
    &who,
    round.vesting_label.clone().into_inner(),
    token_amount,
)
.map_err(|_| Error::<T>::VestingFailed)?;

Self::deposit_event(Event::VestingCreated {
    who: who.clone(),
    round_id,
    token_amount,
    vesting_label: round.vesting_label.clone().into_inner(),
});
```

---

## Summary Table

| # | Severity | Location | Issue |
|---|----------|----------|-------|
| 1 | HIGH | `contribute()` whitelist check | Unbounded `iter_prefix()` — DoS / weight attack |
| 2 | CRITICAL | `contribute()` transfers | Single currency for payment + token — free money exploit |
| 3 | HIGH | `contribute()` steps 1–3 | Incorrect atomicity assumption — vesting failure leaves inconsistent state |
| 4 | MEDIUM | `create_round()`, `genesis_build()` | `NextRoundId` raw `+1` overflows at `u32::MAX` |
| 5 | MEDIUM | All storage maps | No cleanup mechanism — permanent state bloat |
| 6 | HIGH | `contribute()` cap check | `per_account_cap = 0` silently blocks all contributions |
| 7 | HIGH | `collect_funds()` | Missing escrow balance check before transfer |
| 8 | LOW | `contribute()` vesting block | Dead code branch inconsistent with creation-time invariant |