# Verdis AMM DEX Pallet — Security Review

---

## Finding 1: State Updated Before Transfer — Reentrancy-style Inconsistency in `swap`

**Severity: CRITICAL**
**Location: `swap()`, ~line 390–420**

The pool reserves are updated **before** the actual token transfers occur. If `T::Currency::transfer` fails after the pool state has been mutated in memory (and especially after `Pools::<T>::insert` is called), the state becomes inconsistent. More critically: the reserve update happens before transfers, meaning the AMM invariant `x*y=k` is violated during the transfer window. In `swap_token`, the transfers happen **before** the reserve update, but then the pool is written with stale `amount_in` instead of `amount_in_after_fee`, inflating reserves incorrectly.

**In `swap` — reserve updated with `amount_in` but fee is taken out of band:**

```rust
// BEFORE — reserves updated with full amount_in, but only amount_in_after_fee
// was used to compute amount_out. Fee stays in pool but k grows incorrectly.
if is_a_to_b {
    pool.reserve_a = pool.reserve_a
        .checked_add(&amount_in)           // ← adds full amount_in
        .ok_or(Error::<T>::ArithmeticOverflow)?;
    pool.reserve_b = pool.reserve_b
        .checked_sub(&amount_out)
        .ok_or(Error::<T>::ArithmeticUnderflow)?;
}
// transfers happen after
T::Currency::transfer(&who, &dex_account, amount_in, ...)?;
T::Currency::transfer(&dex_account, &who, amount_out, ...)?;
Pools::<T>::insert(pool_id, pool.clone());
```

```rust
// AFTER — transfers first, then update storage; reserve_in grows by
// amount_in (fee stays in pool as intended by constant-product AMM)
let dex_account: T::AccountId = T::PalletId::get().into_account_truncating();
// 1. Transfers first — if either fails we revert with no state change
T::Currency::transfer(&who, &dex_account, amount_in, ExistenceRequirement::KeepAlive)?;
T::Currency::transfer(&dex_account, &who, amount_out, ExistenceRequirement::KeepAlive)?;

// 2. Only update storage after both transfers succeed
if is_a_to_b {
    pool.reserve_a = pool.reserve_a
        .checked_add(&amount_in)   // full amount_in — fee accrues in reserve
        .ok_or(Error::<T>::ArithmeticOverflow)?;
    pool.reserve_b = pool.reserve_b
        .checked_sub(&amount_out)
        .ok_or(Error::<T>::ArithmeticUnderflow)?;
} else {
    pool.reserve_b = pool.reserve_b
        .checked_add(&amount_in)
        .ok_or(Error::<T>::ArithmeticOverflow)?;
    pool.reserve_a = pool.reserve_a
        .checked_sub(&amount_out)
        .ok_or(Error::<T>::ArithmeticUnderflow)?;
}
Pools::<T>::insert(pool_id, pool.clone());
TotalVolume::<T>::mutate(|v| *v = v.saturating_add(amount_in));
TotalSwaps::<T>::mutate(|s| *s += 1);
```

---

## Finding 2: `swap_token` Reserve Updated with `amount_in` Instead of `amount_in_after_fee` — k Inflated

**Severity: CRITICAL**
**Location: `swap_token()`, ~line 570–585**

The fee is correctly deducted from the swap computation (`amount_in_after_fee` drives `amount_out`), but the reserve is incremented by the full `amount_in`. While this is actually **correct for the fee-accrual model** (fee stays in the pool), the computed `amount_out` used `amount_in_after_fee` in the denominator. This means `k_new = (reserve_in + amount_in) * (reserve_out - amount_out)` which is *larger* than `k_old` — that is intentional for fee accrual. **However**, the price impact circuit breaker checks `amount_in_after_fee <= max_swap_in` but the reserve is updated with `amount_in`, so a user can bypass the price-impact limit by choosing a tiny fee numerator at genesis. Additionally the `has_balance` check happens **after** computing `amount_out` but **before** transfer — this is the correct order. The real bug is that `swap_token` does transfers **before** updating reserves (good), but then updates with `amount_in` — this is inconsistent with how `amount_out` was computed and leaks fee value to the LPs asymmetrically versus `swap`.

```rust
// BEFORE
T::TokenHandler::transfer(&asset_in, &who, &dex_account, amount_in)?;
T::TokenHandler::transfer(&asset_out, &dex_account, &who, amount_out)?;

if is_a_to_b {
    pool.reserve_a = pool.reserve_a
        .checked_add(&amount_in)          // ← should be amount_in for fee accrual
        ...
```

Both `swap` and `swap_token` should be consistent. The standard Uniswap V2 model adds the **full** `amount_in` to the reserve (fee stays). The fix is to ensure both use the same model and the price-impact check is against `amount_in`, not `amount_in_after_fee`:

```rust
// AFTER — consistent fee-accrual model, price impact on gross amount_in
// Price impact check should use amount_in (gross), not amount_in_after_fee
let max_impact: BalanceOf<T> = T::MaxPriceImpact::get().deconstruct().into();
let max_swap_in = reserve_in
    .checked_mul(&max_impact)
    .ok_or(Error::<T>::ArithmeticOverflow)?
    / 1_000_000u32.into();
ensure!(
    amount_in <= max_swap_in,   // ← was amount_in_after_fee
    Error::<T>::PriceImpactTooHigh
);

// transfers before storage write
T::TokenHandler::transfer(&asset_in, &who, &dex_account, amount_in)?;
T::TokenHandler::transfer(&asset_out, &dex_account, &who, amount_out)?;

if is_a_to_b {
    pool.reserve_a = pool.reserve_a
        .checked_add(&amount_in)
        .ok_or(Error::<T>::ArithmeticOverflow)?;
    pool.reserve_b = pool.reserve_b
        .checked_sub(&amount_out)
        .ok_or(Error::<T>::ArithmeticUnderflow)?;
} else {
    pool.reserve_b = pool.reserve_b
        .checked_add(&amount_in)
        .ok_or(Error::<T>::ArithmeticOverflow)?;
    pool.reserve_a = pool.reserve_a
        .checked_sub(&amount_out)
        .ok_or(Error::<T>::ArithmeticUnderflow)?;
}
TokenPools::<T>::insert(pool_id, pool);
```

---

## Finding 3: `create_pool` Uses `reserve` Instead of `transfer` — Funds Never Move to DEX Account

**Severity: CRITICAL**
**Location: `create_pool()`, ~line 295–300**

`T::Currency::reserve` locks funds **in the user's account** (reserved balance), it does **not** transfer them to the DEX pallet account. When `swap` later calls `T::Currency::transfer` from the DEX account to the user, the DEX account has zero balance, causing the transfer to fail or drain an unrelated account. `add_liquidity` correctly uses `transfer`.

```rust
// BEFORE
T::Currency::reserve(&who, amount_a)?;
T::Currency::reserve(&who, amount_b)?;

let pool = Pool { ... };
Pools::<T>::insert(pool_id, pool);
```

```rust
// AFTER
let dex_account: T::AccountId = T::PalletId::get().into_account_truncating();
T::Currency::transfer(
    &who,
    &dex_account,
    amount_a,
    ExistenceRequirement::KeepAlive,
)?;
T::Currency::transfer(
    &who,
    &dex_account,
    amount_b,
    ExistenceRequirement::KeepAlive,
)?;

let pool = Pool { ... };
Pools::<T>::insert(pool_id, pool);
```

---

## Finding 4: `remove_liquidity` Transfers Before Updating Storage — State Inconsistency on Transfer Failure

**Severity: HIGH**
**Location: `remove_liquidity()`, ~line 355–380**

The transfers to the user happen **before** the pool reserves and LP balances are updated in storage. If the second transfer fails (e.g., `amount_b` transfer fails due to existential deposit), `amount_a` has already been sent but the pool state still shows the old reserves. The user keeps their LP tokens and can drain again.

```rust
// BEFORE
let dex_account = ...;
T::Currency::transfer(&dex_account, &who, amount_a, ExistenceRequirement::KeepAlive)?;
T::Currency::transfer(&dex_account, &who, amount_b, ExistenceRequirement::KeepAlive)?;

pool.reserve_a = pool.reserve_a.checked_sub(&amount_a)...;
pool.reserve_b = pool.reserve_b.checked_sub(&amount_b)...;
pool.total_lp  = pool.total_lp.checked_sub(&lp_amount)...;

Pools::<T>::insert(pool_id, pool.clone());
LiquidityProviders::<T>::mutate(pool_id, &who, |lp| { ... });
```

```rust
// AFTER — compute new state, write storage, then transfer
// 1. Compute new reserves
let new_reserve_a = pool.reserve_a
    .checked_sub(&amount_a)
    .ok_or(Error::<T>::ArithmeticUnderflow)?;
let new_reserve_b = pool.reserve_b
    .checked_sub(&amount_b)
    .ok_or(Error::<T>::ArithmeticUnderflow)?;
let new_total_lp = pool.total_lp
    .checked_sub(&lp_amount)
    .ok_or(Error::<T>::ArithmeticUnderflow)?;
let new_user_lp = user_lp
    .checked_sub(&lp_amount)
    .ok_or(Error::<T>::ArithmeticUnderflow)?;

// 2. Write storage atomically before external calls
pool.reserve_a = new_reserve_a;
pool.reserve_b = new_reserve_b;
pool.total_lp  = new_total_lp;
Pools::<T>::insert(pool_id, pool.clone());
LiquidityProviders::<T>::insert(pool_id, &who, new_user_lp);

// 3. Transfers last — if either fails, the whole extrinsic reverts
let dex_account: T::AccountId = T::PalletId::get().into_account_truncating();
T::Currency::transfer(
    &dex_account, &who, amount_a, ExistenceRequirement::KeepAlive,
)?;
T::Currency::transfer(
    &dex_account, &who, amount_b, ExistenceRequirement::KeepAlive,
)?;
```

> Apply the same fix to `remove_token_liquidity`.

---

## Finding 5: `PoolCount` Overflow — Unchecked Increment

**Severity: HIGH**
**Location: `create_pool()`, ~line 310 and `create_token_pool()`, ~line 460**

`PoolCount::<T>::mutate(|c| *c += 1)` uses plain `+=` on a `u32`. If `MaxPools` is `u32::MAX` the `ensure!(count < T::MaxPools::get())` check prevents creation, but if `MaxPools` is set to `u32::MAX` itself, the counter overflows and wraps to 0, allowing pool ID collisions that overwrite existing pools.

```rust
// BEFORE
PoolCount::<T>::mutate(|c| *c += 1);
```

```rust
// AFTER
PoolCount::<T>::mutate(|c| {
    *c = c.saturating_add(1);
});
```

---

## Finding 6: Integer Division in LP Calculation Allows Liquidity Donation Griefing

**Severity: HIGH**
**Location: `add_liquidity()`, ~line 330–345**

The LP minting formula `lp_a = total_lp * amount_a / reserve_a` uses integer division. A large existing LP holder can manipulate `reserve_a` by donating tokens directly to the DEX account (bypassing the pallet), causing new LPs to receive 0 LP tokens while their funds are accepted. Additionally, the check `ensure!(lp > 0)` fires too late — the tokens have not been transferred yet, so no funds are lost, but the UX is broken and the check ordering is misleading.

```rust
// BEFORE — lp computed, then transfers, then storage updated
let lp_a = pool.total_lp
    .checked_mul(&amount_a)
    .ok_or(Error::<T>::ArithmeticOverflow)?
    / pool.reserve_a;
let lp_b = pool.total_lp
    .checked_mul(&amount_b)
    .ok_or(Error::<T>::ArithmeticOverflow)?
    / pool.reserve_b;
let lp = lp_a.min(lp_b);
ensure!(lp > BalanceOf::<T>::zero(), Error::<T>::InsufficientAmount);

// ...transfers happen here...
```

```rust
// AFTER — validate ratio matches pool before accepting tokens
// Enforce that the user provides tokens in the exact pool ratio
// (within 1 unit tolerance due to integer rounding).
let expected_b = pool.reserve_b
    .checked_mul(&amount_a)
    .ok_or(Error::<T>::ArithmeticOverflow)?
    / pool.reserve_a;
ensure!(
    amount_b >= expected_b &&
    amount_b <= expected_b.saturating_add(1u32.into()),
    Error::<T>::SlippageExceeded
);

let lp_a = pool.total_lp
    .checked_mul(&amount_a)
    .ok_or(Error::<T>::ArithmeticOverflow)?
    / pool.reserve_a;
let lp_b = pool.total_lp
    .checked_mul(&amount_b)
    .ok_or(Error::<T>::ArithmeticOverflow)?
    / pool.reserve_b;
let lp = lp_a.min(lp_b);
ensure!(lp > BalanceOf::<T>::zero(), Error::<T>::InsufficientAmount);
// transfers follow
```

---

## Finding 7: Reverse-Pair Pool Bypass — `PoolByPair` Only Stores One Ordering

**Severity: HIGH**
**Location: `create_pool()`, ~line 285 and `PoolByPair` storage**

`PoolByPair` only stores `(token_a, token_b)` but not `(token_b, token_a)`. An attacker can create a second pool with the tokens reversed (`token_a` and `token_b` swapped), fragmenting liquidity and confusing integrators.

```rust
// BEFORE — only one ordering stored
ensure!(
    !PoolByPair::<T>::contains_key((ta.clone(), tb.clone())),
    Error::<T>::PoolAlreadyExists
);
// ...
PoolByPair::<T>::insert((ta, tb), pool_id);
```

```rust
// AFTER — check and store both orderings
ensure!(
    !PoolByPair::<T>::contains_key((ta.clone(), tb.clone()))
        && !PoolByPair::<T>::contains_key((tb.clone(), ta.clone())),
    Error::<T>::PoolAlreadyExists
);
// ...
// Canonicalize pair ordering (lexicographic) so lookup is deterministic
let (canonical_a, canonical_b) = if ta <= tb {
    (ta.clone(), tb.clone())
} else {
    (tb.clone(), ta.clone())
};
PoolByPair::<T>::insert((canonical_a, canonical_b), pool_id);
```

Apply the same fix to `TokenPoolByPair` and `create_token_pool`.

---

## Finding 8: `LiquidityProviders` Entry Never Removed — Unbounded Storage Growth

**Severity: MEDIUM**
**Location: `remove_liquidity()`, ~line 375**

When a user burns all their LP tokens, the `LiquidityProviders` entry is set to `Some(0)` but never removed. Over time this leaks storage. An attacker can add/remove liquidity repeatedly across many accounts to bloat the map with zero-value entries.

```rust
// BEFORE
LiquidityProviders::<T>::mutate(pool_id, &who, |lp| {
    *lp = Some(
        lp.unwrap_or(BalanceOf::<T>::zero())
            .saturating_sub(lp_amount),
    );
});
```

```rust
// AFTER — remove entry when balance reaches zero
let remaining = user_lp.saturating_sub(lp_amount);
if remaining == BalanceOf::<T>::zero() {
    LiquidityProviders::<T>::remove(pool_id, &who);
} else {
    LiquidityProviders::<T>::insert(pool_id, &who, remaining);
}
```

Apply the same fix to `TokenLiquidityProviders` in `remove_token_liquidity`.

---

## Finding 9: Fee Calculation Can Round to Zero for Small Swaps — Fee Bypass

**Severity: MEDIUM**
**Location: `swap()` and `swap_token()`, fee computation ~line 370**

For small `amount_in` values, `amount_in * fee_numerator / fee_denominator` rounds to zero. With `FeeNumerator=3, FeeDenominator=1000`, any `amount_in < 334` (in the smallest unit) pays zero fee. Repeated small swaps can drain a pool fee-free.

```rust
// BEFORE
let fee = amount_in
    .checked_mul(&fee_num)
    .ok_or(Error::<T>::ArithmeticOverflow)?
    / T::FeeDenominator::get().into();
let amount_in_after_fee = amount_in
    .checked_sub(&fee)
    .ok_or(Error::<T>::ArithmeticUnderflow)?;
```

```rust
// AFTER — enforce minimum fee of 1 unit when swap is non-zero
let raw_fee = amount_in
    .checked_mul(&fee_num)
    .ok_or(Error::<T>::ArithmeticOverflow)?
    / T::FeeDenominator::get().into();
// Minimum fee: at least 1 unit so fee can never be zero on a non-zero swap
let fee: BalanceOf<T> = raw_fee.max(1u32.into());
let amount_in_after_fee = amount_in
    .checked_sub(&fee)
    .ok_or(Error::<T>::ArithmeticUnderflow)?;
// Ensure the swap is large enough to cover the minimum fee
ensure!(
    amount_in > fee,
    Error::<T>::AmountTooLow
);
```

---

## Finding 10: `get_price` Is a Signed Extrinsic with No Return Value — Should Be RPC/Query

**Severity: MEDIUM**
**Location: `get_price()`, ~line 455**

`get_price` is a signed extrinsic that charges the caller weight/fees but returns nothing useful on-chain. The price is only observable via events (of which none are emitted). The existing `pool_price` helper function serves this purpose correctly. The extrinsic wastes user funds and adds attack surface.

```rust
// BEFORE — full extrinsic, charges fee, returns nothing
#[pallet::call_index(4)]
#[pallet::weight(T::WeightInfo::get_price())]
pub fn get_price(origin: OriginFor<T>, pool_id: u32) -> DispatchResult {
    ensure_signed(origin)?;
    let pool = Pools::<T>::get(pool_id).ok_or(Error::<T>::PoolNotFound)?;
    ensure!(
        pool.reserve_b > BalanceOf::<T>::zero(),
        Error::<T>::InsufficientLiquidity
    );
    Ok(())
}
```

```rust
// AFTER — remove the extrinsic entirely; expose via runtime API or use
// the existing pool_price() helper. If an on-chain record is needed,
// emit an event:
#[pallet::call_index(4)]
#[pallet::weight(T::WeightInfo::get_price())]
pub fn get_price(origin: OriginFor<T>, pool_id: u32) -> DispatchResult {
    ensure_signed(origin)?;
    let pool = Pools::<T>::get(pool_id).ok_or(Error::<T>::PoolNotFound)?;
    ensure!(
        pool.reserve_b > BalanceOf::<T>::zero(),
        Error::<T>::InsufficientLiquidity
    );
    let price = pool.reserve_a / pool.reserve_b;
    // Emit event so the caller can observe the price
    Self::deposit_event(Event::PriceQueried {
        pool_id,
        reserve_a: pool.reserve_a,
        reserve_b: pool.reserve_b,
        price,
    });
    Ok(())
}
// Add to Event enum:
// PriceQueried { pool_id: u32, reserve_a: BalanceOf<T>,
//                reserve_b: BalanceOf<T>, price: BalanceOf<T> }
```

---

## Finding 11: Genesis Build Sets LP Without Tracking `LiquidityProviders`

**Severity: MEDIUM**
**Location: `build()` in `GenesisConfig`, ~line 245**

The genesis build inserts pools with `total_lp > 0` but never populates `LiquidityProviders`. The pallet account (creator) holds conceptual LP shares but can never call `remove_liquidity` because `user_lp` will be `0`. The initial liquidity is permanently locked.

```rust
// BEFORE — no LiquidityProviders entry created
Pools::<T>::insert(id, pool);
PoolByPair::<T>::insert((ta, tb), id);
id += 1;
```

```rust
// AFTER — track genesis LP shares against the pallet account
let pallet_account: T::AccountId = T::PalletId::get().into_account_truncating();
LiquidityProviders::<T>::insert(id, &pallet_account, pool.total_lp);
Pools::<T>::insert(id, pool);
PoolByPair::<T>::insert((ta, tb), id);
id += 1;
```

---

## Finding 12: `add_liquidity` Double-Checks `pool.total_lp == 0` After Transfers

**Severity: LOW**
**Location: `add_liquidity()`, ~line 335–365**

The code checks `if pool.total_lp == 0` twice: once to compute `lp_minted` and once after transfers to decide whether to reset or add reserves. If another extrinsic somehow modifies the pool between these two points (not possible in single-threaded Substrate, but a logic smell), the reserve accounting would be wrong. More importantly, after transfers succeed the code re-reads `pool.total_lp` from the **local variable** (stale snapshot), not from storage.

```rust
// BEFORE — pool is a local snapshot; the second == 0 check is redundant
// and confusing; reserve update logic is duplicated
let lp_minted = if pool.total_lp == BalanceOf::<T>::zero() { ... }
else { ... };

T::Currency::transfer(...)?;
T::Currency::transfer(...)?;

if pool.total_lp == BalanceOf::<T>::zero() {   // ← same local var, always same result
    pool.reserve_a = amount_a;
    pool.reserve_b = amount_b;
} else {
    pool.reserve_a = pool.reserve_a.checked_add(&amount_a)...;
    pool.reserve_b = pool.reserve_b.checked_add(&amount_b)...;
}
```

```rust
// AFTER — use a boolean flag set once; eliminates duplicate check
let is_empty_pool = pool.total_lp == BalanceOf::<T>::zero();

let lp_minted = if is_empty_pool {
    let product = amount_a
        .checked_mul(&amount_b)
        .ok_or(Error::<T>::ArithmeticOverflow)?;
    product.integer_sqrt()
} else {
    // ... existing ratio logic
};

let dex_account: T::AccountId = T::PalletId::get().into_account_truncating();
T::Currency::transfer(&who, &dex_account, amount_a, ExistenceRequirement::KeepAlive)?;
T::Currency::transfer(&who, &dex_account, amount_b, ExistenceRequirement::KeepAlive)?;

if is_empty_pool {
    pool.reserve_a = amount_a;
    pool.reserve_b = amount_b;
} else {
    pool.reserve_a = pool.reserve_a
        .checked_add(&amount_a)
        .ok_or(Error::<T>::ArithmeticOverflow)?;
    pool.reserve_b = pool.reserve_b
        .checked_add(&amount_b)
        .ok_or(Error::<T>::ArithmeticOverflow)?;
}
pool.total_lp = pool.total_lp
    .checked_add(&lp_minted)
    .ok_or(Error::<T>::ArithmeticOverflow)?;

Pools::<T>::insert(pool_id, pool.clone());
```

---

## Summary Table

| # | Severity | Function | Issue |
|---|----------|----------|-------|
| 1 | CRITICAL | `swap` | State updated before transfer; inconsistent ordering |
| 2 | CRITICAL | `swap_token` | Price impact check on `amount_in_after_fee` inconsistent with `swap` |
| 3 | CRITICAL | `create_pool` | `reserve()` used instead of `transfer()` — funds stay with user |
| 4 | HIGH | `remove_liquidity` | Transfers before storage update — double-spend on partial failure |
| 5 | HIGH | `create_pool` / `create_token_pool` | `PoolCount` plain `+=` can overflow |
| 6 | HIGH | `add_liquidity` | Integer division allows liquidity donation griefing |
| 7 | HIGH | `create_pool` | Reverse-pair pool not blocked — duplicate pools possible |
| 8 | MEDIUM | `remove_liquidity` | Zero-LP entries never cleaned up — storage bloat |
| 9 | MEDIUM | `swap` / `swap_token` | Fee rounds to zero for small swaps |
| 10 | MEDIUM | `get_price` | Paid extrinsic with no observable output |
| 11 | MEDIUM | `build` (genesis) | Genesis LP not tracked in `LiquidityProviders` |
| 12 | LOW | `add_liquidity` | Redundant `total_lp == 0` check on local snapshot |