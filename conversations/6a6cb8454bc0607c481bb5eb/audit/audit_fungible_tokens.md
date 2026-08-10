# Substrate Pallet Code Review: Verdis Fungible Tokens

---

## Finding 1: Wrong Event Emitted in `transfer_ownership`

**Severity: HIGH**
**Location: `transfer_ownership`, ~line 390**

`TokenCreated` is emitted with empty name/symbol/decimals=0 instead of a proper `OwnershipTransferred` event. This corrupts off-chain indexers and could be exploited to spoof token creation events.

**Before:**
```rust
Self::deposit_event(Event::TokenCreated {
    token_id,
    owner: new_owner,
    name: Vec::new(),
    symbol: Vec::new(),
    decimals: 0,
});
```

**After:**
```rust
// First, add to Event enum:
OwnershipTransferred {
    token_id: u64,
    old_owner: T::AccountId,
    new_owner: T::AccountId,
},

// Then in transfer_ownership:
Self::deposit_event(Event::OwnershipTransferred {
    token_id,
    old_owner: who,
    new_owner,
});
```

---

## Finding 2: Deposit Not Re-Reserved for New Owner in `transfer_ownership`

**Severity: HIGH**
**Location: `transfer_ownership`, ~line 360**

When ownership is transferred, the deposit is still held against the old owner's reserved balance, but the new owner has no deposit reserved. If the new owner then calls `destroy`, they receive no unreserved funds (the old owner's deposit stays locked forever) OR if the old owner's deposit is unreserved at destroy time they get funds without ever having paid the deposit.

**Before:**
```rust
// No deposit handling in transfer_ownership at all
token.owner = new_owner.clone();
Tokens::<T>::insert(token_id, token);
```

**After:**
```rust
let deposit = T::CreateTokenDeposit::get();

// Transfer deposit from old owner to new owner
T::Currency::unreserve(&who, deposit);
T::Currency::reserve(&new_owner, deposit)?;

token.owner = new_owner.clone();
Tokens::<T>::insert(token_id, token);
```

---

## Finding 3: Bare Arithmetic Subtraction in `do_transfer`

**Severity: HIGH**
**Location: `do_transfer`, ~line 420**

`from_balance - amount` uses bare subtraction. Although there is an `ensure!(from_balance >= amount)` guard above it, this pattern is fragile and panics in debug mode if the invariant is ever violated by a logic change. The rest of the codebase uses `saturating_sub` or `checked_sub`.

**Before:**
```rust
ensure!(from_balance >= amount, Error::<T>::InsufficientBalance);

let to_balance = TokenBalances::<T>::get(token_id, to);
let new_to_balance = to_balance.checked_add(amount).ok_or(Error::<T>::Overflow)?;

TokenBalances::<T>::insert(token_id, from, from_balance - amount);
```

**After:**
```rust
ensure!(from_balance >= amount, Error::<T>::InsufficientBalance);

let to_balance = TokenBalances::<T>::get(token_id, to);
let new_to_balance = to_balance.checked_add(amount).ok_or(Error::<T>::Overflow)?;

let new_from_balance = from_balance
    .checked_sub(amount)
    .ok_or(Error::<T>::Underflow)?;
TokenBalances::<T>::insert(token_id, from, new_from_balance);
```

---

## Finding 4: `batch_transfer` — Sender Can Transfer to Themselves, Inflating Effective Balance Check

**Severity: HIGH**
**Location: `batch_transfer`, ~line 315**

If `who` appears in the `recipients` list, their balance is credited during the loop but `from_balance` was snapshotted before the loop. The final write at the bottom overwrites any credit received. More critically, the pre-loop balance check passes because total_needed is checked against the snapshot, but then the loop credits back to `who`, making the net deduction less than `total_needed`. An attacker can transfer tokens to themselves to effectively reduce their actual net loss.

**Before:**
```rust
let from_balance = TokenBalances::<T>::get(token_id, &who);
ensure!(from_balance >= total_needed, Error::<T>::InsufficientBalance);

for (to, amount) in recipients.into_iter() {
    let to_balance = TokenBalances::<T>::get(token_id, &to);
    let new_to_balance = to_balance.checked_add(amount).ok_or(Error::<T>::Overflow)?;
    TokenBalances::<T>::insert(token_id, &to, new_to_balance);
    // ...
}

TokenBalances::<T>::insert(token_id, &who, from_balance.saturating_sub(total_needed));
```

**After:**
```rust
let from_balance = TokenBalances::<T>::get(token_id, &who);
ensure!(from_balance >= total_needed, Error::<T>::InsufficientBalance);

// Deduct first to prevent self-transfer inflation
let new_from_balance = from_balance
    .checked_sub(total_needed)
    .ok_or(Error::<T>::Underflow)?;
TokenBalances::<T>::insert(token_id, &who, new_from_balance);

for (to, amount) in recipients.into_iter() {
    ensure!(to != who, Error::<T>::InvalidRecipient); // add variant to Error enum
    let to_balance = TokenBalances::<T>::get(token_id, &to);
    let new_to_balance = to_balance.checked_add(amount).ok_or(Error::<T>::Overflow)?;
    TokenBalances::<T>::insert(token_id, &to, new_to_balance);
    Self::deposit_event(Event::Transferred {
        token_id,
        from: who.clone(),
        to,
        amount,
    });
}
```

---

## Finding 5: `transfer` Silently Succeeds with Zero Amount When `from == to`

**Severity: MEDIUM**
**Location: `transfer`, ~line 240**

When `from == to`, the function returns `Ok(())` before the `ensure!(amount > 0)` check. A caller can submit a zero-amount self-transfer that silently succeeds and emits no event. While not directly exploitable for fund theft, it pollutes the extrinsic history and wastes block space. More importantly the ordering of checks is inconsistent with the rest of the pallet.

**Before:**
```rust
pub fn transfer(...) -> DispatchResult {
    let who = ensure_signed(origin)?;
    if who == to {
        return Ok(());
    }
    ensure!(amount > 0, Error::<T>::ZeroAmount);
```

**After:**
```rust
pub fn transfer(...) -> DispatchResult {
    let who = ensure_signed(origin)?;
    ensure!(amount > 0, Error::<T>::ZeroAmount);
    ensure!(who != to, Error::<T>::SelfTransfer); // add SelfTransfer to Error enum
    
    let token = Tokens::<T>::get(token_id).ok_or(Error::<T>::TokenNotFound)?;
    ensure!(!token.is_frozen, Error::<T>::TokenFrozen);
```

---

## Finding 6: Unbounded `recipients` Vec in `batch_transfer` — DoS Vector

**Severity: MEDIUM**
**Location: `batch_transfer`, ~line 295**

The `recipients: Vec<(T::AccountId, u128)>` parameter is unbounded. An attacker can submit thousands of recipients in one extrinsic. The weight calculation `recipients.len() as u32` is used but the weight benchmark `batch_transfer(b: u32)` returns a constant `Weight::from_parts(10_000, 0)` regardless of `b`, meaning the actual weight is severely underestimated. This is a block-stuffing / DoS vector.

**Before:**
```rust
#[pallet::weight(T::WeightInfo::batch_transfer(recipients.len() as u32))]
pub fn batch_transfer(
    origin: OriginFor<T>,
    token_id: u64,
    recipients: Vec<(T::AccountId, u128)>,
) -> DispatchResult {
```

**After:**
```rust
// Add to Config:
type MaxBatchSize: Get<u32>;

// Add to Error:
BatchTooLarge,

#[pallet::weight(T::WeightInfo::batch_transfer(recipients.len() as u32))]
pub fn batch_transfer(
    origin: OriginFor<T>,
    token_id: u64,
    recipients: BoundedVec<(T::AccountId, u128), T::MaxBatchSize>,
) -> DispatchResult {
    let who = ensure_signed(origin)?;
    // recipients is now statically bounded; no runtime length check needed
    // Also fix the WeightInfo impl to scale linearly:
```

```rust
// In WeightInfo impl:
fn batch_transfer(b: u32) -> Weight {
    Weight::from_parts(5_000u64.saturating_add(3_000u64.saturating_mul(b as u64)), 0)
}
```

---

## Finding 7: `destroy` Does Not Clean Up `TokenBalances` or `Allowances` — Storage Leak

**Severity: MEDIUM**
**Location: `destroy`, ~line 345**

When a token is destroyed, `Tokens` and `TokenMetadataMap` entries are removed, but all `TokenBalances` and `Allowances` entries for that token remain in storage permanently. This leaks storage and means if `token_id` is ever reused (which it won't be with monotonic IDs, but is still bad practice), stale balances could be inherited.

**Before:**
```rust
pub fn destroy(origin: OriginFor<T>, token_id: u64) -> DispatchResult {
    let who = ensure_signed(origin)?;
    let token = Tokens::<T>::get(token_id).ok_or(Error::<T>::TokenNotFound)?;
    ensure!(token.owner == who, Error::<T>::NotTokenOwner);
    ensure!(token.total_supply == 0, Error::<T>::TokenStillHasSupply);

    Tokens::<T>::remove(token_id);
    TokenMetadataMap::<T>::remove(token_id);
    // TokenBalances and Allowances NOT cleaned up
```

**After:**
```rust
pub fn destroy(origin: OriginFor<T>, token_id: u64) -> DispatchResult {
    let who = ensure_signed(origin)?;
    let token = Tokens::<T>::get(token_id).ok_or(Error::<T>::TokenNotFound)?;
    ensure!(token.owner == who, Error::<T>::NotTokenOwner);
    ensure!(token.total_supply == 0, Error::<T>::TokenStillHasSupply);

    Tokens::<T>::remove(token_id);
    TokenMetadataMap::<T>::remove(token_id);

    // Remove all balance and allowance entries for this token
    // Note: since total_supply == 0, all balances must be zero.
    // We still clear storage to reclaim space and prevent stale state.
    let _ = TokenBalances::<T>::clear_prefix(token_id, u32::MAX, None);
    let _ = Allowances::<T>::clear_prefix(token_id, u32::MAX, None);
```

---

## Finding 8: `transfer_from` — Allowance Underflow When `from == to` (Spender Self-Approval)

**Severity: MEDIUM**
**Location: `transfer_from`, ~line 275**

If `from == to`, the balance check passes trivially (net movement is zero), but the allowance is still decremented. A spender who is also the `from` account burns their own allowance for a no-op. Additionally there is no guard against `from == who` (the spender equals the from account), which means the spender could consume their own allowance on a self-transfer.

**Before:**
```rust
pub fn transfer_from(...) -> DispatchResult {
    let who = ensure_signed(origin)?;
    ensure!(amount > 0, Error::<T>::ZeroAmount);

    let token = Tokens::<T>::get(token_id).ok_or(Error::<T>::TokenNotFound)?;
    ensure!(!token.is_frozen, Error::<T>::TokenFrozen);

    let allowance = Allowances::<T>::get(token_id, (&from, &who));
    ensure!(allowance >= amount, Error::<T>::InsufficientAllowance);
```

**After:**
```rust
pub fn transfer_from(...) -> DispatchResult {
    let who = ensure_signed(origin)?;
    ensure!(amount > 0, Error::<T>::ZeroAmount);
    // Prevent spender from being the same as from (self-allowance abuse)
    ensure!(from != who, Error::<T>::InvalidSpender); // add to Error enum

    let token = Tokens::<T>::get(token_id).ok_or(Error::<T>::TokenNotFound)?;
    ensure!(!token.is_frozen, Error::<T>::TokenFrozen);

    let allowance = Allowances::<T>::get(token_id, (&from, &who));
    ensure!(allowance >= amount, Error::<T>::InsufficientAllowance);
```

---

## Finding 9: `NextTokenId` Overflow with `saturating_add` Causes Token ID Collision

**Severity: MEDIUM**
**Location: `create`, ~line 200**

`NextTokenId` uses `saturating_add(1)`. If `token_id` ever reaches `u64::MAX` (unlikely in practice but must be handled), `saturating_add` will return `u64::MAX` forever, causing every subsequent `create` call to overwrite the existing token at `u64::MAX`.

**Before:**
```rust
let token_id = NextTokenId::<T>::get();
NextTokenId::<T>::set(token_id.saturating_add(1));
```

**After:**
```rust
let token_id = NextTokenId::<T>::get();
let next_id = token_id.checked_add(1).ok_or(Error::<T>::Overflow)?;
NextTokenId::<T>::set(next_id);
```

---

## Finding 10: Missing `TransferOwnership` Event — Silent Ownership Change

**Severity: LOW**
**Location: `transfer_ownership`, ~line 385**

Already partially covered in Finding 1, but worth calling out separately: there is zero correct event for ownership transfer. Off-chain monitoring systems (block explorers, security alerts) cannot detect ownership changes, which is a critical administrative action.

This is resolved by the fix in Finding 1 (adding `OwnershipTransferred` event).

---

## Finding 11: `do_transfer` Is Public — Authorization Bypass

**Severity: LOW**
**Location: `do_transfer`, ~line 410**

`do_transfer` is `pub` with no origin check. While intended for inter-pallet use, any pallet in the runtime can call it to transfer any user's tokens without their consent. This should be gated or the visibility documented explicitly with a security note.

**Before:**
```rust
pub fn do_transfer(
    token_id: u64,
    from: &T::AccountId,
    to: &T::AccountId,
    amount: u128,
) -> DispatchResult {
```

**After:**
```rust
/// Internal transfer callable from trusted pallets only.
/// SECURITY: Caller is responsible for verifying authorization before calling this.
/// This function performs NO authorization check on `from`.
pub(crate) fn do_transfer(  // restrict visibility to crate
    token_id: u64,
    from: &T::AccountId,
    to: &T::AccountId,
    amount: u128,
) -> DispatchResult {
```

---

## Summary Table

| # | Severity | Location | Issue |
|---|----------|----------|-------|
| 1 | HIGH | `transfer_ownership` | Wrong event (`TokenCreated`) emitted |
| 2 | HIGH | `transfer_ownership` | Deposit not transferred to new owner |
| 3 | HIGH | `do_transfer` | Bare subtraction `from_balance - amount` |
| 4 | HIGH | `batch_transfer` | Self-recipient inflates balance check |
| 5 | MEDIUM | `transfer` | Silent success on self-transfer before zero-amount check |
| 6 | MEDIUM | `batch_transfer` | Unbounded Vec DoS + constant weight benchmark |
| 7 | MEDIUM | `destroy` | `TokenBalances` and `Allowances` not cleaned up |
| 8 | MEDIUM | `transfer_from` | Spender can equal `from`, burning allowance on no-op |
| 9 | MEDIUM | `create` | `saturating_add` on `NextTokenId` causes ID collision at `u64::MAX` |
| 10 | LOW | `transfer_ownership` | No correct event for ownership transfer |
| 11 | LOW | `do_transfer` | `pub` visibility with no authorization — should be `pub(crate)` |