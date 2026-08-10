# Verdis Tokenomics Pallet — Security Review

---

## Finding 1: CRITICAL — Presale Purchase Has No Payment Collection (Buyer Gets Free Tokens)

**Location:** `purchase()`, ~line 230

**Description:**
The `purchase()` function calculates a `cost` but **never transfers payment from the buyer to the treasury**. The buyer receives tokens from the treasury account with zero economic cost. The `PresaleRaised` counter is updated with `cost`, but no actual funds are moved from `who` to anyone. This is a complete economic exploit — any consented account can drain the entire investor allocation for free.

**Before:**
```rust
// Calculate price (price_bps is in basis points)
let price_bps = PresalePrice::<T>::get();
let price_bal: BalanceOf<T> = price_bps.saturated_into();
let divisor: BalanceOf<T> = 10_000u32.saturated_into();
let cost = amount.saturating_mul(price_bal) / divisor;

// Transfer tokens from pallet treasury
let treasury = T::PalletId::get().into_account_truncating();
T::Currency::transfer(&treasury, &who, amount, ExistenceRequirement::AllowDeath)?;

PresaleRaised::<T>::mutate(|r| *r = r.saturating_add(cost));
PresaleSold::<T>::mutate(|s| *s = s.saturating_add(amount));
CirculatingSupply::<T>::mutate(|c| *c = c.saturating_add(amount));
```

**After:**
```rust
// Calculate price (price_bps is in basis points)
let price_bps = PresalePrice::<T>::get();
let price_bal: BalanceOf<T> = price_bps.saturated_into();
let divisor: BalanceOf<T> = 10_000u32.saturated_into();
// Use checked arithmetic to prevent overflow in cost calculation
let cost = amount
    .checked_mul(&price_bal)
    .ok_or(ArithmeticError::Overflow)?
    .checked_div(&divisor)
    .ok_or(ArithmeticError::DivisionByZero)?;

ensure!(cost > Zero::zero(), Error::<T>::InsufficientFunds);

let treasury = T::PalletId::get().into_account_truncating();

// Step 1: Collect payment FROM buyer TO treasury
T::Currency::transfer(
    &who,
    &treasury,
    cost,
    ExistenceRequirement::KeepAlive,
)?;

// Step 2: Transfer tokens FROM treasury TO buyer
T::Currency::transfer(
    &treasury,
    &who,
    amount,
    ExistenceRequirement::AllowDeath,
)?;

PresaleRaised::<T>::mutate(|r| *r = r.saturating_add(cost));
PresaleSold::<T>::mutate(|s| *s = s.saturating_add(amount));
CirculatingSupply::<T>::mutate(|c| *c = c.saturating_add(amount));
```

---

## Finding 2: CRITICAL — Arithmetic Overflow in Cost Calculation

**Location:** `purchase()`, ~line 238

**Description:**
`amount.saturating_mul(price_bal)` silently clamps on overflow instead of returning an error. If `amount` is near `BalanceOf::MAX` and `price_bal > 1`, the multiplication saturates to `MAX` and the subsequent integer division produces a wildly incorrect cost. With saturation, an attacker purchasing a huge amount pays an effectively random (saturated/divided) price rather than the correct one. Must use `checked_mul`.

**Before:**
```rust
let cost = amount.saturating_mul(price_bal) / divisor;
```

**After:**
```rust
let cost = amount
    .checked_mul(&price_bal)
    .ok_or(ArithmeticError::Overflow)?
    .checked_div(&divisor)
    .ok_or(ArithmeticError::DivisionByZero)?;
```

---

## Finding 3: CRITICAL — Non-Atomic State Update Enables Double-Spend via Re-entrancy / Partial Failure

**Location:** `purchase()`, ~line 242–250

**Description:**
The three `mutate` calls on `PresaleRaised`, `PresaleSold`, and `CirculatingSupply` are separate storage writes that occur **after** both token transfers. If any intermediate step fails (unlikely with Substrate's transactional storage but architecturally unsound), or if future refactors introduce fallible logic between them, the state becomes inconsistent: tokens already moved but counters wrong. Additionally, the investor allocation check reads `PresaleSold` before writing it, but within the same extrinsic there is no lock — in a parallel execution model this would be a TOCTOU. All state should be staged before side effects.

**Before:**
```rust
T::Currency::transfer(&treasury, &who, amount, ExistenceRequirement::AllowDeath)?;

PresaleRaised::<T>::mutate(|r| *r = r.saturating_add(cost));
PresaleSold::<T>::mutate(|s| *s = s.saturating_add(amount));
CirculatingSupply::<T>::mutate(|c| *c = c.saturating_add(amount));
```

**After:**
```rust
// Stage all state reads and validation BEFORE any side effects
let new_sold = sold
    .checked_add(&amount)
    .ok_or(ArithmeticError::Overflow)?;
ensure!(new_sold <= max, Error::<T>::MaxInvestorAllocationReached);

let new_raised = PresaleRaised::<T>::get()
    .checked_add(&cost)
    .ok_or(ArithmeticError::Overflow)?;

let new_circulating = CirculatingSupply::<T>::get()
    .checked_add(&amount)
    .ok_or(ArithmeticError::Overflow)?;

// Side effects only after all validation passes
T::Currency::transfer(&who, &treasury, cost, ExistenceRequirement::KeepAlive)?;
T::Currency::transfer(&treasury, &who, amount, ExistenceRequirement::AllowDeath)?;

// Commit state atomically (all or nothing guaranteed by Substrate's overlay)
PresaleSold::<T>::put(new_sold);
PresaleRaised::<T>::put(new_raised);
CirculatingSupply::<T>::put(new_circulating);
```

---

## Finding 4: HIGH — `release_distribution` Does Not Transfer Actual Tokens

**Location:** `release_distribution()`, ~line 270

**Description:**
The function updates `cat.released` and increments `CirculatingSupply` but performs no actual `Currency::transfer`. The accounting says tokens were released but they were never moved to any recipient. This makes the circulating supply counter permanently inconsistent with reality, and the intended beneficiaries (community, team, advisors, etc.) receive nothing.

**Before:**
```rust
Distribution::<T>::mutate(&cat_bv, |c| {
    let cat = c.as_mut().ok_or(Error::<T>::InvalidCategory)?;
    ensure!(
        cat.released.saturating_add(amount) <= cat.amount,
        Error::<T>::DistributionComplete
    );
    cat.released = cat.released.saturating_add(amount);
    Ok::<(), Error<T>>(())
})?;

CirculatingSupply::<T>::mutate(|c| *c = c.saturating_add(amount));
```

**After:**
```rust
// Accept explicit recipient in the function signature:
// pub fn release_distribution(
//     origin: OriginFor<T>,
//     category: Vec<u8>,
//     amount: BalanceOf<T>,
//     recipient: T::AccountId,   // <-- ADD THIS PARAMETER
// ) -> DispatchResult {

Distribution::<T>::try_mutate(&cat_bv, |c| -> DispatchResult {
    let cat = c.as_mut().ok_or(Error::<T>::InvalidCategory)?;
    let new_released = cat
        .released
        .checked_add(&amount)
        .ok_or(ArithmeticError::Overflow)?;
    ensure!(new_released <= cat.amount, Error::<T>::DistributionComplete);
    cat.released = new_released;
    Ok(())
})?;

let new_circulating = CirculatingSupply::<T>::get()
    .checked_add(&amount)
    .ok_or(ArithmeticError::Overflow)?;

let treasury = T::PalletId::get().into_account_truncating();
T::Currency::transfer(
    &treasury,
    &recipient,
    amount,
    ExistenceRequirement::AllowDeath,
)?;

CirculatingSupply::<T>::put(new_circulating);

Self::deposit_event(Event::DistributionUpdated {
    category,
    released: amount,
});
```

---

## Finding 5: HIGH — `release_distribution` Arithmetic Overflow in Released Counter

**Location:** `release_distribution()`, ~line 276

**Description:**
`cat.released.saturating_add(amount)` is used for the guard check but if it saturates to `Balance::MAX`, the check `<= cat.amount` may still pass (if `cat.amount == Balance::MAX`), allowing an attacker with root to mark infinite releases. The same saturation is then written back. Must use `checked_add` and reject on overflow.

**Before:**
```rust
ensure!(
    cat.released.saturating_add(amount) <= cat.amount,
    Error::<T>::DistributionComplete
);
cat.released = cat.released.saturating_add(amount);
```

**After:**
```rust
let new_released = cat
    .released
    .checked_add(&amount)
    .ok_or(ArithmeticError::Overflow)?;
ensure!(new_released <= cat.amount, Error::<T>::DistributionComplete);
cat.released = new_released;
```

---

## Finding 6: HIGH — `CirculatingSupply` Can Exceed `TotalSupply`

**Location:** `purchase()` and `release_distribution()`, ~lines 248 and 282

**Description:**
Neither function checks that the resulting `CirculatingSupply` stays within `TotalSupply`. An operator could call `release_distribution` repeatedly across categories until the circulating supply overflows the 100B cap. The invariant `circulating ≤ total_supply` is never enforced at the mutation site.

**Before:**
```rust
// purchase():
CirculatingSupply::<T>::mutate(|c| *c = c.saturating_add(amount));

// release_distribution():
CirculatingSupply::<T>::mutate(|c| *c = c.saturating_add(amount));
```

**After:**
```rust
// In both purchase() and release_distribution(), before committing:
let total = TotalSupply::<T>::get();
let new_circulating = CirculatingSupply::<T>::get()
    .checked_add(&amount)
    .ok_or(ArithmeticError::Overflow)?;
ensure!(
    new_circulating <= total,
    Error::<T>::MaxInvestorAllocationReached // or add: SupplyCapExceeded
);
CirculatingSupply::<T>::put(new_circulating);
```

---

## Finding 7: HIGH — Permanent Delegate Has Unbounded Power with No Access Control Extrinsic

**Location:** `PermanentDelegate` storage, throughout

**Description:**
`PermanentDelegate` is defined in storage and referenced in events, but **no extrinsic exists to set or revoke it**, and no authorization check is implemented anywhere. If future code is added that checks `PermanentDelegate` to authorize privileged operations (as the name implies), there is no setter with proper access control, meaning either: (a) the field can never be set (dead code / broken feature), or (b) whoever adds the setter later may not add proper guards. The storage and event exist but the feature is incomplete in a dangerous way.

**After:** Add a properly guarded setter:
```rust
#[pallet::call_index(5)]
#[pallet::weight(T::WeightInfo::set_permanent_delegate())]
pub fn set_permanent_delegate(
    origin: OriginFor<T>,
    delegate: Option<T::AccountId>,
) -> DispatchResult {
    ensure_root(origin)?; // or a designated council origin

    match &delegate {
        Some(d) => {
            PermanentDelegate::<T>::put(Some(d.clone()));
            Self::deposit_event(Event::PermanentDelegateSet {
                delegate: d.clone(),
            });
        }
        None => {
            PermanentDelegate::<T>::kill();
        }
    }
    Ok(())
}
```

---

## Finding 8: HIGH — Freeze/Unfreeze Functions Missing — Storage Exists, Extrinsics Do Not

**Location:** `FrozenAccounts`, `FreezeAuthority` storage, throughout

**Description:**
`FrozenAccounts` and `FreezeAuthority` storage items are declared, and `AccountFrozen`/`AccountUnfrozen` events are defined, but **no extrinsics implement freeze/unfreeze logic**. More critically, no transfer hook checks `FrozenAccounts` before allowing token movement. A frozen account can still transact freely. The events and errors (`AccountFrozen`, `NotFreezeAuthority`) suggest this was intended to be enforced.

**After:** Add extrinsics and enforce in transfer path:
```rust
#[pallet::call_index(6)]
#[pallet::weight(T::WeightInfo::freeze_account())]
pub fn freeze_account(
    origin: OriginFor<T>,
    who: T::AccountId,
) -> DispatchResult {
    let caller = ensure_signed(origin)?;
    let authority = FreezeAuthority::<T>::get()
        .ok_or(Error::<T>::NotFreezeAuthority)?;
    ensure!(caller == authority, Error::<T>::NotFreezeAuthority);
    FrozenAccounts::<T>::insert(&who, true);
    Self::deposit_event(Event::AccountFrozen { account: who });
    Ok(())
}

#[pallet::call_index(7)]
#[pallet::weight(T::WeightInfo::unfreeze_account())]
pub fn unfreeze_account(
    origin: OriginFor<T>,
    who: T::AccountId,
) -> DispatchResult {
    let caller = ensure_signed(origin)?;
    let authority = FreezeAuthority::<T>::get()
        .ok_or(Error::<T>::NotFreezeAuthority)?;
    ensure!(caller == authority, Error::<T>::NotFreezeAuthority);
    FrozenAccounts::<T>::remove(&who);
    Self::deposit_event(Event::AccountUnfrozen { account: who });
    Ok(())
}

// Add a frozen-account guard helper used before any transfer:
fn ensure_not_frozen(who: &T::AccountId) -> DispatchResult {
    ensure!(
        !FrozenAccounts::<T>::get(who),
        Error::<T>::AccountFrozen
    );
    Ok(())
}
```

---

## Finding 9: MEDIUM — `PresaleSold` Check Is a TOCTOU Race (Read-Check-Write Not Atomic)

**Location:** `purchase()`, ~line 218

**Description:**
The allocation check reads `PresaleSold` and then the write happens later after currency transfers. In Substrate's single-threaded model this is safe today, but using `try_mutate` makes the intent explicit and safe against future refactors. The current pattern is:

```
read sold → check → transfer → write sold
```

If `transfer` fails after the check but before the write, sold is not updated — this is actually safe. But if logic is reordered or the check is not inside the same `mutate` closure, the atomicity guarantee is lost.

**Before:**
```rust
let sold = PresaleSold::<T>::get();
let max = T::InvestorAllocation::get();
ensure!(
    sold.saturating_add(amount) <= max,
    Error::<T>::MaxInvestorAllocationReached
);
// ... later ...
PresaleSold::<T>::mutate(|s| *s = s.saturating_add(amount));
```

**After:**
```rust
// Compute and validate before any side effects, then use put() after transfers succeed
let sold = PresaleSold::<T>::get();
let max = T::InvestorAllocation::get();
let new_sold = sold
    .checked_add(&amount)
    .ok_or(ArithmeticError::Overflow)?;
ensure!(new_sold <= max, Error::<T>::MaxInvestorAllocationReached);

// ... perform transfers ...

// Only write after all fallible operations succeed
PresaleSold::<T>::put(new_sold);
```

---

## Finding 10: MEDIUM — `TransferFeeBps` and `GreenTreasuryCollected` Are Never Used

**Location:** Storage declarations, ~line 90–96

**Description:**
`TransferFeeBps` is stored and `EcoFeeCollected` event exists, but **no transfer hook deducts the fee**. The eco/green fee is purely cosmetic. An attacker transferring tokens pays no eco fee regardless of the configured BPS. If this is a core tokenomics invariant (Token-2022 transfer fee), it must be enforced in a transfer hook or wrapper.

**After:** Implement a fee-charging transfer helper:
```rust
pub fn transfer_with_eco_fee(
    from: &T::AccountId,
    to: &T::AccountId,
    amount: BalanceOf<T>,
) -> DispatchResult {
    let bps: BalanceOf<T> = TransferFeeBps::<T>::get().saturated_into();
    let divisor: BalanceOf<T> = 10_000u32.saturated_into();
    let fee = amount
        .checked_mul(&bps)
        .ok_or(ArithmeticError::Overflow)?
        .checked_div(&divisor)
        .ok_or(ArithmeticError::DivisionByZero)?;
    let net = amount
        .checked_sub(&fee)
        .ok_or(ArithmeticError::Underflow)?;

    let green = T::GreenTreasury::get();
    T::Currency::transfer(from, &green, fee, ExistenceRequirement::KeepAlive)?;
    T::Currency::transfer(from, to, net, ExistenceRequirement::AllowDeath)?;

    GreenTreasuryCollected::<T>::mutate(|c| *c = c.saturating_add(fee));
    Self::deposit_event(Event::EcoFeeCollected { amount: fee });
    Ok(())
}
```

---

## Finding 11: MEDIUM — `PriorityFees` Uses `Twox64Concat` for User-Controlled Keys

**Location:** `PriorityFees` storage declaration, ~line 83

**Description:**
`Twox64Concat` is not collision-resistant against user-controlled input. For storage maps keyed by `AccountId` (externally provided), `Blake2_128Concat` must be used to prevent storage trie manipulation attacks where an attacker crafts account IDs that collide in the Twox64 hash space.

**Before:**
```rust
pub type PriorityFees<T: Config> = StorageMap<_, Twox64Concat, T::AccountId, u32, ValueQuery>;
```

**After:**
```rust
pub type PriorityFees<T: Config> = StorageMap<_, Blake2_128Concat, T::AccountId, u32, ValueQuery>;
```

Same fix applies to `ConfidentialAccounts` and `FrozenAccounts`:
```rust
pub type ConfidentialAccounts<T: Config> =
    StorageMap<_, Blake2_128Concat, T::AccountId, bool, ValueQuery>;

pub type FrozenAccounts<T: Config> =
    StorageMap<_, Blake2_128Concat, T::AccountId, bool, ValueQuery>;
```

---

## Finding 12: MEDIUM — Genesis Build Does Not Validate Distribution Percentages Sum to 100

**Location:** `genesis_build`, ~line 195

**Description:**
The genesis config accepts arbitrary `(amount, percentage)` pairs with no validation that percentages sum to 100 or that total amounts equal `TotalSupply`. A misconfigured genesis could silently bootstrap an invalid tokenomics state.

**Before:**
```rust
fn build(&self) {
    TotalSupply::<T>::put(self.total_supply);
    // No validation
    for (name, amount, pct, vesting, cliff) in &self.distribution {
```

**After:**
```rust
fn build(&self) {
    assert!(
        self.total_supply == T::TotalSupply::get(),
        "Genesis total_supply must match TotalSupply constant"
    );

    let total_pct: u32 = self.distribution.iter()
        .map(|(_, _, pct, _, _)| *pct as u32)
        .sum();
    assert!(total_pct == 100, "Distribution percentages must sum to 100, got {}", total_pct);

    let total_amount: BalanceOf<T> = self.distribution.iter()
        .map(|(_, amount, _, _, _)| *amount)
        .fold(BalanceOf::<T>::zero(), |acc, a| acc.saturating_add(a));
    assert!(
        total_amount <= self.total_supply,
        "Distribution total exceeds total supply"
    );

    TotalSupply::<T>::put(self.total_supply);
    CirculatingSupply::<T>::put(self.circulating_supply);
    PresalePrice::<T>::put(self.presale_price);

    for (name, amount, pct, vesting, cliff) in &self.distribution {
        // ... existing insert logic
    }
}
```

---

## Finding 13: LOW — `ConsentGiven` Map Is Never Cleaned Up

**Location:** `ConsentGiven` storage, `give_consent()`, ~line 207

**Description:**
Consent records are written once and never removed. If an account is reaped (balance goes to zero), the account storage is cleaned by the system, but the `ConsentGiven` map entry persists, bloating state indefinitely. For a pallet expecting millions of users in a presale, this is an unbounded storage growth issue.

**After:** Use a bounded approach or document explicit cleanup:
```rust
// Option 1: Store consent as a bit in a bounded collection (preferred at scale)
// Option 2: Clean up on account reaping via a system event hook
// Option 3: At minimum, document the growth bound in storage attributes:

#[pallet::storage]
#[pallet::getter(fn consent_given)]
// NOTE: This map grows unboundedly. Entries are never removed.
// Maximum size bounded by number of unique participants in the presale.
pub type ConsentGiven<T: Config> = StorageMap<
    _,
    Blake2_128Concat,
    T::AccountId,
    bool,
    // Use OptionQuery so non-existent == no consent (avoids default ValueQuery confusion)
>;
```

---

## Finding 14: LOW — Missing `#[transactional]` Attribute on Multi-Step Extrinsics

**Location:** `purchase()`, ~line 215

**Description:**
`purchase()` performs two currency transfers and three storage mutations. If the second `Currency::transfer` (tokens out) fails after the first (payment in) succeeded, funds are taken from the buyer but no tokens are delivered. While Substrate's storage overlay rolls back on `DispatchError`, `Currency::transfer` side effects within the overlay should be wrapped in `#[transactional]` for explicit atomicity guarantees.

**Before:**
```rust
pub fn purchase(origin: OriginFor<T>, amount: BalanceOf<T>) -> DispatchResult {
```

**After:**
```rust
#[pallet::call_index(1)]
#[pallet::weight(T::WeightInfo::purchase())]
#[frame_support::transactional]
pub fn purchase(origin: OriginFor<T>, amount: BalanceOf<T>) -> DispatchResult {
```

---

## Summary Table

| # | Severity | Location | Issue |
|---|----------|----------|-------|
| 1 | CRITICAL | `purchase()` | No payment collected from buyer |
| 2 | CRITICAL | `purchase()` | Overflow in cost calculation via `saturating_mul` |
| 3 | CRITICAL | `purchase()` | Non-atomic state updates after side effects |
| 4 | HIGH | `release_distribution()` | No actual token transfer to recipient |
| 5 | HIGH | `release_distribution()` | Overflow in `released` counter |
| 6 | HIGH | Both mutators | `CirculatingSupply` can exceed `TotalSupply` |
| 7 | HIGH | `PermanentDelegate` | No setter extrinsic, no access control |
| 8 | HIGH | `FrozenAccounts` | Freeze not enforced on transfers |
| 9 | MEDIUM | `purchase()` | TOCTOU on sold counter |
| 10 | MEDIUM | Transfer path | Eco fee never deducted |
| 11 | MEDIUM | 3 StorageMaps | `Twox64Concat` on user-controlled keys |
| 12 | MEDIUM | `genesis_build` | No invariant validation at genesis |
| 13 | LOW | `ConsentGiven` | Unbounded storage growth |
| 14 | LOW | `purchase()` | Missing `#[transactional]` |