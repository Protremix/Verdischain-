# Substrate DPoS Pallet Security Review

## Summary of Findings

| # | Severity | Location | Issue |
|---|----------|----------|-------|
| 1 | CRITICAL | `do_slash` ~line 420 | Unbounded storage iteration across all voters |
| 2 | CRITICAL | `do_slash` ~line 415 | Arithmetic: division before multiplication, wrong slash fraction calculation |
| 3 | CRITICAL | `slash_validator` ~line 310 | Slash accounting: unreserve semantics misunderstood, slashing wrong amount |
| 4 | CRITICAL | `reactivate_validator` ~line 370 | Arithmetic overflow on cooldown check |
| 5 | CRITICAL | `refill_reward_pool` ~line 395 | Missing root/governance authorization - anyone can drain their own funds but event spoofing risk; combined with treasury confusion |
| 6 | HIGH | `do_slash` ~line 408 | State inconsistency: validator storage mutated before delegator slash, delegator slash reads stale state |
| 7 | HIGH | `unregister_validator` ~line 258 | Stake not properly cleaned up; voter funds remain reserved permanently |
| 8 | HIGH | `SlashingEvents::mutate` ~line 335 | Unchecked arithmetic: `*c += 1` can overflow |
| 9 | HIGH | `set_commission` ~line 355 | Wrong event emitted (`GreenScoreUpdated` instead of commission event) |
| 10 | HIGH | `rotate_epoch` ~line 456 | Unbounded iteration over entire `ValidatorList` on every epoch |
| 11 | MEDIUM | `vote` ~line 275 | TOCTOU: validator existence checked then re-fetched without atomicity |
| 12 | MEDIUM | `reactivate_validator` ~line 370 | Reactivated validator not added back to `ValidatorList` or `ActiveValidators` |
| 13 | MEDIUM | `reward_block_producer` ~line 495 | No check that `validator` is actually in `ActiveValidators` |
| 14 | MEDIUM | `do_slash` | Missing `ValidatorList` cleanup on slash |
| 15 | LOW | `set_commission` | Weight attributed to `update_green_score` instead of dedicated weight |
| 16 | LOW | `unvote` | `TotalStaked` decremented immediately but funds stay reserved until withdrawal |

---

## Detailed Findings

---

### CRITICAL-1: Unbounded Storage Iteration in `do_slash`

**Location:** `do_slash`, delegator slash loop ~line 420

**Description:** `Votes::<T>::iter()` performs a full scan of ALL voter entries in storage. With potentially thousands of voters across all validators, this will exceed block weight limits and can be exploited by registering many small delegations to a target validator, making it impossible to slash them (transaction OOMs/runs out of weight).

```rust
// BEFORE (CRITICAL - unbounded O(N) over ALL voters globally):
let delegators: Vec<(T::AccountId, BalanceOf<T>)> = Votes::<T>::iter()
    .filter_map(|(voter, votes)| {
        votes.into_iter()
            .find(|vr| vr.validator == *validator)
            .map(|vr| (voter, vr.amount))
    })
    .collect();
```

**Fix:** Add a reverse index mapping `validator -> voters` with a bounded `BoundedVec`, populated on `vote`/`unvote`.

```rust
// Add new storage (alongside existing storage declarations):
#[pallet::storage]
pub type ValidatorDelegators<T: Config> = StorageMap<
    _,
    Blake2_128Concat,
    T::AccountId, // validator
    BoundedVec<T::AccountId, ConstU32<512>>,
    ValueQuery,
>;

// AFTER - in do_slash, replace the unbounded iter with:
let delegators: Vec<(T::AccountId, BalanceOf<T>)> =
    ValidatorDelegators::<T>::get(validator)
        .iter()
        .filter_map(|voter| {
            Votes::<T>::get(voter).and_then(|votes| {
                votes
                    .into_iter()
                    .find(|vr| vr.validator == *validator)
                    .map(|vr| (voter.clone(), vr.amount))
            })
        })
        .collect();

// In vote() extrinsic, after inserting the VoteRecord:
ValidatorDelegators::<T>::try_mutate(&validator, |delegators| {
    if !delegators.contains(&who) {
        delegators.try_push(who.clone()).map_err(|_| Error::<T>::VoteStorageFull)
    } else {
        Ok(())
    }
})?;

// In unvote() extrinsic, after removing the VoteRecord:
ValidatorDelegators::<T>::mutate(&validator, |delegators| {
    delegators.retain(|d| d != &who);
});
```

---

### CRITICAL-2: Wrong Slash Fraction Arithmetic in `do_slash`

**Location:** `do_slash` ~line 415

**Description:** The slash fraction calculation multiplies `BalanceOf` values where the denominator is `val_stake` (the validator's own stake), not `val_total`. More critically, the `saturating_mul` of a large `BalanceOf` by `10_000u32` will overflow for any non-trivial token balance. The division-before-multiplication also causes precision loss. Additionally `slash_fraction_bps` is computed from `val_stake` but applied to delegators' amounts, which is semantically incorrect — the intention is to slash delegators by the same *fraction* as the validator lost.

```rust
// BEFORE (overflow risk + wrong denominator):
let slash_fraction_bps = actual_slash
    .saturating_mul(10_000u32.into()) / val_stake;
// ...
let delegator_slash = delegated_amount
    .saturating_mul(slash_fraction_bps) / 10_000u32.into();
```

**Fix:** Use integer arithmetic that avoids overflow by ordering operations correctly and using the correct denominator:

```rust
// AFTER: compute fraction as (actual_slash / val_stake) applied to each delegator.
// To avoid overflow: delegator_slash = delegated_amount * actual_slash / val_total
// where val_total is the total stake the slash covers.
// Use u128/u64 intermediate if BalanceOf is u128.

// Helper: proportional slash without BPS intermediate
fn proportional_slash(
    amount: BalanceOf<T>,
    numerator: BalanceOf<T>,
    denominator: BalanceOf<T>,
) -> BalanceOf<T> {
    if denominator.is_zero() {
        return Zero::zero();
    }
    // Multiply first in wider arithmetic if needed; saturating_mul gives us
    // protection against overflow at the cost of capping — acceptable for slashing.
    amount
        .saturating_mul(numerator)
        .checked_div(&denominator)
        .unwrap_or_else(Zero::zero)
}

// In do_slash, replace the fraction calculation:
// AFTER:
for (delegator, delegated_amount) in delegators {
    // Slash each delegator by the same fraction: actual_slash / val_stake
    let delegator_slash =
        Self::proportional_slash(delegated_amount, actual_slash, val_stake);
    if !delegator_slash.is_zero() {
        let actually_unreserved =
            T::Currency::unreserve(&delegator, delegator_slash);
        // unreserve returns the amount it could NOT unreserve; 
        // the actual freed amount is delegator_slash - actually_unreserved
        let freed = delegator_slash.saturating_sub(actually_unreserved);
        if !freed.is_zero() {
            if T::Currency::transfer(
                &delegator,
                &treasury,
                freed,
                ExistenceRequirement::AllowDeath,
            )
            .is_ok()
            {
                // Update the voter's VoteRecord to reflect reduced delegation
                Votes::<T>::mutate(&delegator, |votes| {
                    if let Some(ref mut vote_list) = votes {
                        for vr in vote_list.iter_mut() {
                            if vr.validator == *validator {
                                vr.amount = vr.amount.saturating_sub(freed);
                            }
                        }
                    }
                });
                TotalStaked::<T>::mutate(|t| *t = t.saturating_sub(freed));
            }
        }
    }
}
```

---

### CRITICAL-3: `slash_validator` Extrinsic — Wrong Unreserve Semantics

**Location:** `slash_validator` ~line 310-322

**Description:** `T::Currency::unreserve()` returns the amount it **could not** unreserve (the shortfall), NOT the amount successfully unreserved. The code subtracts the return value from `slash_amount` to get `actual_slash`, which means if unreserve fully succeeds (returns 0), `actual_slash = slash_amount - 0 = slash_amount` ✓. But if it partially fails (returns N), `actual_slash = slash_amount - N` which is the *successfully freed* amount. The `ensure!(!actual_slash.is_zero())` then prevents the slash from proceeding in normal cases where unreserve fully succeeded. The naming and ensure logic are inverted — this causes valid slashes to fail.

Additionally the comment says "track shortfall" but the logic uses the result as if it's the successfully freed amount, which is semantically inconsistent with `do_slash` where the same pattern appears but `actual_slash` means something different.

```rust
// BEFORE (semantically inverted, causes slashes to fail incorrectly):
let unreserved = T::Currency::unreserve(&validator, slash_amount);
let actual_slash = slash_amount.saturating_sub(unreserved);
ensure!(
    !actual_slash.is_zero(),
    Error::<T>::SlashingFailed
);
```

```rust
// AFTER: unreserve returns the amount it COULD NOT unreserve (the deficit).
// The amount successfully freed is: slash_amount - deficit.
let deficit = T::Currency::unreserve(&validator, slash_amount);
let actual_slash = slash_amount.saturating_sub(deficit);
ensure!(
    actual_slash > BalanceOf::<T>::zero(),
    Error::<T>::SlashingFailed
);

// Now transfer the actually-freed (unreserved) funds to treasury.
// These funds are now FREE (not reserved), so transfer works.
let treasury = T::PalletId::get().into_account_truncating();
T::Currency::transfer(
    &validator,
    &treasury,
    actual_slash,
    ExistenceRequirement::AllowDeath,
)?;
```

---

### CRITICAL-4: Arithmetic Overflow in `reactivate_validator` Cooldown Check

**Location:** `reactivate_validator` ~line 380

**Description:** `last_slash + T::ReactivationCooldown::get()` uses plain `+` on `u32` values, which will panic in debug builds or wrap in release builds if `last_slash` is near `u32::MAX`. Must use saturating/checked arithmetic.

```rust
// BEFORE (overflow risk):
ensure!(
    current_block >= last_slash + T::ReactivationCooldown::get(),
    Error::<T>::ReactivationCooldownNotElapsed
);
```

```rust
// AFTER:
let cooldown_ends = last_slash.saturating_add(T::ReactivationCooldown::get());
ensure!(
    current_block >= cooldown_ends,
    Error::<T>::ReactivationCooldownNotElapsed
);
```

---

### CRITICAL-5: `refill_reward_pool` Missing Authorization

**Location:** `refill_reward_pool` ~line 395

**Description:** This extrinsic uses `ensure_signed` — any user can call it and transfer arbitrary funds from their own account to the reward pool. While economically this isn't directly harmful, the **reward pool is the same account used to hold slashed funds** (the `PalletId` treasury account). An attacker can inflate the reward pool to dilute slashing accountability tracking. More seriously, the extrinsic should require governance (`ensure_root`) if it's described as "governance only" in the doc comment, creating a documentation/implementation mismatch that could be exploited in governance contexts. The pool account also receives slash funds in `slash_validator`, conflating two separate concerns.

```rust
// BEFORE (anyone can call, mislabeled as governance-only):
pub fn refill_reward_pool(
    origin: OriginFor<T>,
    amount: BalanceOf<T>,
) -> DispatchResult {
    let who = ensure_signed(origin)?;
    // ...
}
```

```rust
// AFTER option A — keep permissionless but fix the doc comment and separate pool from treasury:
// Add a separate PalletId for the reward pool vs treasury in Config:
type RewardPoolId: Get<PalletId>;  // separate from treasury PalletId

pub fn refill_reward_pool(
    origin: OriginFor<T>,
    amount: BalanceOf<T>,
) -> DispatchResult {
    // Permissionless — anyone may donate to the reward pool.
    let who = ensure_signed(origin)?;
    ensure!(amount > BalanceOf::<T>::zero(), Error::<T>::ZeroAmount);

    let reward_pool: T::AccountId = T::RewardPoolId::get().into_account_truncating();
    T::Currency::transfer(
        &who,
        &reward_pool,
        amount,
        ExistenceRequirement::KeepAlive,
    )?;
    Self::deposit_event(Event::RewardPoolRefilled { amount });
    Ok(())
}

// AFTER option B — make it root-only as documented:
pub fn refill_reward_pool(
    origin: OriginFor<T>,
    amount: BalanceOf<T>,
) -> DispatchResult {
    ensure_root(origin)?;  // governance only, as documented
    ensure!(amount > BalanceOf::<T>::zero(), Error::<T>::ZeroAmount);
    // ... rest unchanged
}
```

---

### HIGH-1: State Inconsistency in `do_slash` — Validator Mutated Before Delegators Processed

**Location:** `do_slash` ~line 408-430

**Description:** `Validators::<T>::mutate` modifies `v.stake` and `v.total_votes` **before** the delegator loop reads `val_stake` and `val_total` (captured earlier). If the mutation were reordered or the captured values wrong, the slash fraction calculation uses stale/incorrect values. The current code captures `val_stake` and `val_total` before mutation (which is correct), but the validator is marked `active = false` before delegators are processed, which means any re-entrant call during delegator iteration sees an inactive validator. The fix is to ensure all reads happen before all writes.

```rust
// BEFORE (validator state mutated mid-operation):
let val_stake = val.stake;
let val_total = val.total_votes;
let delegator_pool = val_total.saturating_sub(val_stake);

Validators::<T>::mutate(validator, |v| {  // <-- mutates BEFORE delegator loop
    if let Some(v) = v {
        v.stake = v.stake.saturating_sub(actual_slash);
        v.total_votes = v.total_votes.saturating_sub(actual_slash);
        v.slashed = true;
        v.active = false;
    }
});

// THEN processes delegators using val_stake captured above...
```

```rust
// AFTER: collect all delegator data first, then apply all mutations atomically:
pub fn do_slash(validator: &T::AccountId, slash_amount: BalanceOf<T>) {
    let val = match Validators::<T>::get(validator) {
        Some(v) => v,
        None => return,
    };

    let slash_amount = slash_amount.min(val.stake);
    if slash_amount.is_zero() {
        return;
    }

    // Capture all state needed BEFORE any mutations
    let val_stake = val.stake;
    
    // Collect delegator data before any storage mutations
    let delegators: Vec<(T::AccountId, BalanceOf<T>)> =
        ValidatorDelegators::<T>::get(validator) // use bounded reverse index
            .iter()
            .filter_map(|voter| {
                Votes::<T>::get(voter).and_then(|votes| {
                    votes
                        .into_iter()
                        .find(|vr| vr.validator == *validator)
                        .map(|vr| (voter.clone(), vr.amount))
                })
            })
            .collect();

    // Perform financial operations
    let deficit = T::Currency::unreserve(validator, slash_amount);
    let actual_slash = slash_amount.saturating_sub(deficit);
    if actual_slash.is_zero() {
        return;
    }

    let treasury: T::AccountId = T::PalletId::get().into_account_truncating();
    if T::Currency::transfer(
        validator,
        &treasury,
        actual_slash,
        ExistenceRequirement::AllowDeath,
    )
    .is_err()
    {
        return;
    }

    // Process delegator slashes
    let mut total_delegator_slashed = BalanceOf::<T>::zero();
    for (delegator, delegated_amount) in &delegators {
        let delegator_slash =
            Self::proportional_slash(*delegated_amount, actual_slash, val_stake);
        if delegator_slash.is_zero() {
            continue;
        }
        let deficit_d = T::Currency::unreserve(delegator, delegator_slash);
        let freed_d = delegator_slash.saturating_sub(deficit_d);
        if !freed_d.is_zero() {
            if T::Currency::transfer(
                delegator,
                &treasury,
                freed_d,
                ExistenceRequirement::AllowDeath,
            )
            .is_ok()
            {
                total_delegator_slashed =
                    total_delegator_slashed.saturating_add(freed_d);
                // Update VoteRecord for slashed delegator
                Votes::<T>::mutate(delegator, |votes| {
                    if let Some(ref mut vote_list) = votes {
                        for vr in vote_list.iter_mut() {
                            if vr.validator == *validator {
                                vr.amount = vr.amount.saturating_sub(freed_d);
                            }
                        }
                    }
                });
            }
        }
    }

    // Apply ALL validator storage mutations AFTER financial ops succeed
    Validators::<T>::mutate(validator, |v| {
        if let Some(v) = v {
            v.stake = v.stake.saturating_sub(actual_slash);
            v.total_votes = v
                .total_votes
                .saturating_sub(actual_slash.saturating_add(total_delegator_slashed));
            v.slashed = true;
            v.active = false;
        }
    });

    let current_block: u32 = frame_system::Pallet::<T>::block_number()
        .try_into()
        .unwrap_or(0);
    LastSlashedBlock::<T>::insert(validator, current_block);
    SlashingEvents::<T>::mutate(validator, |c| {
        *c = c.saturating_add(1);
    });
    TotalStaked::<T>::mutate(|t| {
        *t = t.saturating_sub(actual_slash.saturating_add(total_delegator_slashed));
    });
    ActiveValidators::<T>::mutate(|v| v.retain(|a| a != validator));

    Self::deposit_event(Event::ValidatorSlashed {
        who: validator.clone(),
        penalty: actual_slash,
        reason: b"equivocation".to_vec(),
    });
}
```

---

### HIGH-2: Permanent Fund Lock on `unregister_validator`

**Location:** `unregister_validator` ~line 258

**Description:** When a validator unregisters, their own stake is unreserved. However, all delegators' votes remain in `Votes::<T>` with funds still reserved. After the validator is removed from `Validators::<T>`, delegators can still call `unvote()` (which checks `Validators::contains_key`) — but this will fail with `ValidatorNotFound`. Delegator funds are permanently locked. Additionally, `ValidatorNames` is not cleaned up (storage leak).

```rust
// BEFORE (delegator funds permanently locked, storage leak):
pub fn unregister_validator(origin: OriginFor<T>) -> DispatchResult {
    let who = ensure_signed(origin)?;
    let validator = Validators::<T>::get(&who).ok_or(Error::<T>::ValidatorNotFound)?;
    ensure!(validator.active, Error::<T>::NotActiveValidator);
    ensure!(
        validator.total_votes <= validator.stake,
        Error::<T>::ActiveDelegations
    );
    T::Currency::unreserve(&who, validator.stake);
    Validators::<T>::remove(&who);
    ValidatorList::<T>::mutate(|v| v.retain(|a| a != &who));
    ActiveValidators::<T>::mutate(|v| v.retain(|a| a != &who));
    TotalStaked::<T>::mutate(|t| *t = t.saturating_sub(validator.stake));
    // ... delegators' funds remain locked forever
}
```

```rust
// AFTER: force-release all delegator funds before allowing unregistration:
pub fn unregister_validator(origin: OriginFor<T>) -> DispatchResult {
    let who = ensure_signed(origin)?;
    let validator = Validators::<T>::get(&who).ok_or(Error::<T>::ValidatorNotFound)?;
    ensure!(validator.active, Error::<T>::NotActiveValidator);

    // Release all delegator funds using the bounded reverse index
    let delegators = ValidatorDelegators::<T>::get(&who);
    for delegator in delegators.iter() {
        let mut total_unreserve = BalanceOf::<T>::zero();
        Votes::<T>::mutate(delegator, |votes| {
            if let Some(ref mut vote_list) = votes {
                vote_list.retain(|vr| {
                    if vr.validator == who {
                        total_unreserve =
                            total_unreserve.saturating_add(vr.amount);
                        false
                    } else {
                        true
                    }
                });
            }
        });
        if !total_unreserve.is_zero() {
            T::Currency::unreserve(delegator, total_unreserve);
            TotalStaked::<T>::mutate(|t| *t = t.saturating_sub(total_unreserve));
        }
    }
    ValidatorDelegators::<T>::remove(&who);

    // Unreserve validator's own stake
    T::Currency::unreserve(&who, validator.stake);
    TotalStaked::<T>::mutate(|t| *t = t.saturating_sub(validator.stake));

    // Clean up all associated storage
    Validators::<T>::remove(&who);
    ValidatorList::<T>::mutate(|v| v.retain(|a| a != &who));
    ActiveValidators::<T>::mutate(|v| v.retain(|a| a != &who));
    ValidatorNames::<T>::remove(&who);        // fix storage leak
    SlashingEvents::<T>::remove(&who);        // fix storage leak
    LastSlashedBlock::<T>::remove(&who);      // fix storage leak

    Self::deposit_event(Event::ValidatorUnregistered { who });
    Ok(())
}
```

---

### HIGH-3: Unchecked Arithmetic in `SlashingEvents`

**Location:** `slash_validator` ~line 335 and `do_slash` ~line 445

**Description:** `*c += 1` on a `u32` counter will panic in debug mode on overflow. Must use `saturating_add`.

```rust
// BEFORE (panic on overflow in debug, wrap in release):
SlashingEvents::<T>::mutate(&validator, |c| *c += 1);
```

```rust
// AFTER:
SlashingEvents::<T>::mutate(&validator, |c| {
    *c = c.saturating_add(1);
});
```

---

### HIGH-4: Wrong Event Emitted in `set_commission`

**Location:** `set_commission` ~line 355

**Description:** `set_commission` emits `GreenScoreUpdated` with the commission `rate` as the `score` field. This is semantically incorrect, pollutes event logs with false green score updates, and breaks any off-chain indexer that relies on `GreenScoreUpdated` events.

```rust
// BEFORE (wrong event, misleads indexers):
Self::deposit_event(Event::GreenScoreUpdated { validator: who, score: rate });
```

```rust
// AFTER: Add a proper event and emit it:

// In Event enum, add:
CommissionUpdated {
    validator: T::AccountId,
    rate: u8,
},

// In set_commission:
pub fn set_commission(origin: OriginFor<T>, rate: u8) -> DispatchResult {
    let who = ensure_signed(origin)?;
    ensure!(rate <= 100, Error::<T>::InvalidSlashReason);

    ensure!(
        Validators::<T>::contains_key(&who),
        Error::<T>::NotValidator
    );

    Validators::<T>::try_mutate(&who, |v| -> DispatchResult {
        let v = v.as_mut().ok_or(Error::<T>::NotValidator)?;
        v.commission = rate;
        Ok(())
    })?;

    Self::deposit_event(Event::CommissionUpdated { validator: who, rate });
    Ok(())
}
```

---

### HIGH-5: `rotate_epoch` Unbounded Iteration

**Location:** `rotate_epoch` ~line 456

**Description:** `ValidatorList::<T>::get()` loads up to 1001 `AccountId`s into memory and then iterates, fetching each validator from storage individually. With 1001 validators this is 1001 storage reads per epoch rotation. This can be mitigated but the bound of `ConstU32<1001>` should be tied to `T::MaxValidators` and the weight must account for this.

```rust
// BEFORE (O(MaxValidators) storage reads, weight not accounted for):
let mut all_validators: Vec<(T::AccountId, BalanceOf<T>)> = ValidatorList::<T>::get()
    .into_iter()
    .filter_map(|addr| {
        Validators::<T>::get(&addr)  // N individual storage reads
        // ...
    })
    .collect();
```

```rust
// AFTER: Cache effective votes in a separate StorageMap updated on vote/unvote/score-change,
// so rotate_epoch only reads one bounded collection:

#[pallet::storage]
pub type ValidatorEffectiveVotes<T: Config> =
    StorageMap<_, Blake2_128Concat, T::AccountId, BalanceOf<T>, ValueQuery>;

// Update ValidatorEffectiveVotes whenever total_votes or green_score changes.
// rotate_epoch becomes:
fn rotate_epoch(block: u32) {
    let mut scored: Vec<(T::AccountId, BalanceOf<T>)> = ValidatorList::<T>::get()
        .into_iter()
        .filter_map(|addr| {
            // Single storage read per validator from cache
            let v = Validators::<T>::get(&addr)?;
            if !v.active || v.slashed {
                return None;
            }
            let effective = ValidatorEffectiveVotes::<T>::get(&addr);
            Some((addr, effective))
        })
        .collect();

    scored.sort_by(|a, b| b.1.cmp(&a.1).then_with(|| a.0.cmp(&b.0)));
    // ... rest unchanged
}
```

---

### MEDIUM-1: TOCTOU Race in `vote` Extrinsic

**Location:** `vote` ~line 275

**Description:** The validator is checked with `contains_key`, then fetched again with `get`. Between these two calls (in theory, or in a future refactor), the validator could be removed. More concretely, `total_votes` cap check uses the fetched `val` but then `Validators::mutate` re-reads storage — if another call modified the validator between the two reads, the cap could be exceeded.

```rust
// BEFORE (double fetch, cap can be violated):
ensure!(
    Validators::<T>::contains_key(&validator),
    Error::<T>::ValidatorNotFound
);
// ... other checks ...
let val = Validators::<T>::get(&validator).ok_or(Error::<T>::ValidatorNotFound)?;
ensure!(
    val.total_votes.saturating_add(amount) <= max_stake,
    Error::<T>::StakeExceedsCap
);
// ... reserve funds ...
Validators::<T>::mutate(&validator, |val| {  // third access
    if let Some(v) = val {
        v.total_votes = v.total_votes.saturating_add(amount);
    }
});
```

```rust
// AFTER: use try_mutate for atomic read-modify-write:
pub fn vote(
    origin: OriginFor<T>,
    validator: T::AccountId,
    amount: BalanceOf<T>,
) -> DispatchResult {
    let who = ensure_signed(origin)?;
    ensure!(amount > BalanceOf::<T>::zero(), Error::<T>::ZeroAmount);
    ensure!(
        T::Currency::can_reserve(&who, amount),
        Error::<T>::InsufficientFunds
    );

    let mut existing_votes = Votes::<T>::get(&who).unwrap_or_default();
    ensure!(
        !existing_votes.iter().any(|v| v.validator == validator),
        Error::<T>::AlreadyVoted
    );

    // Reserve before mutating validator storage (fail-fast)
    T::Currency::reserve(&who, amount)?;

    // Atomic read-check-write on validator
    let result = Validators::<T>::try_mutate(&validator, |maybe_val| {
        let val = maybe_val.as_mut().ok_or(Error::<T>::ValidatorNotFound)?;
        ensure!(val.active && !val.slashed, Error::<T>::NotActiveValidator);
        ensure!(
            val.total_votes.saturating_add(amount) <= T::MaxStakePerValidator::get(),
            Error::<T>::StakeExceedsCap
        );
        val.total_votes = val.total_votes.saturating_add(amount);
        Ok(())
    });

    if result.is_err() {
        // Undo the reserve if validator mutation failed
        T::Currency::unreserve(&who, amount);
        return result;
    }

    let vote_record = VoteRecord {
        voter: who.clone(),
        validator: validator.clone(),
        amount,
    };
    existing_votes
        .try_push(vote_record)
        .map_err(|_| Error::<T>::VoteStorageFull)?;
    Votes::<T>::insert(&who, existing_votes);

    ValidatorDelegators::<T>::try_mutate(&validator, |delegators| {
        if !delegators.contains(&who) {
            delegators
                .try_push(who.clone())
                .map_err(|_| Error::<T>::VoteStorageFull)
        } else {
            Ok(())
        }
    })?;

    TotalStaked::<T>::mutate(|t| *t = t.saturating_add(amount));

    Self::deposit_event(Event::Voted { voter: who, validator, amount });
    Ok(())
}
```

---

### MEDIUM-2: `reactivate_validator` Doesn't Restore Active Status Properly

**Location:** `reactivate_validator` ~line 370

**Description:** The validator is marked `active = true` in `Validators` storage but is never re-added to `ValidatorList` or `ActiveValidators`. It will never be selected for block production and the reactivation has no practical effect. Also, the wrong event is emitted (`ValidatorRegistered` instead of a reactivation event).

```rust
// BEFORE (validator set to active but never added to lists, wrong event):
Validators::<T>::mutate(&validator, |v| {
    if let Some(v) = v {
        v.slashed = false;
        v.active = true;
    }
});
Self::deposit_event(Event::ValidatorRegistered {  // wrong event!
    who: validator,
    stake: val.stake,
});
```

```rust
// AFTER: Add validator back to ValidatorList if missing, emit correct event:

// Add to Event enum:
ValidatorReactivated {
    who: T::AccountId,
    stake: BalanceOf<T>,
},

// In reactivate_validator:
Validators::<T>::try_mutate(&validator, |v| -> DispatchResult {
    let v = v.as_mut().ok_or(Error::<T>::ValidatorNotFound)?;
    v.slashed = false;
    v.active = true;
    Ok(())
})?;

// Re-add to ValidatorList if not present
ValidatorList::<T>::try_mutate(|list| -> DispatchResult {
    if !list.contains(&validator) {
        list.try_push(validator.clone())
            .map_err(|_| Error::<T>::MaxValidatorsReached)?;
    }
    Ok(())
})?;

Self::deposit_event(Event::ValidatorReactivated {
    who: validator,
    stake: val.stake,
});
Ok(())
```

---

### MEDIUM-3: `reward_block_producer` — No Active Validator Check

**Location:** `reward_block_producer` ~line 495

**Description:** Any account in `Validators` storage can receive a block reward, even if they are inactive, slashed, or not in `ActiveValidators`. An attacker who registers as a validator but never participates in consensus could potentially receive rewards if this function is called with their account ID.

```rust
// BEFORE (no check that validator is active or in ActiveValidators):
pub fn reward_block_producer(validator: &T::AccountId, block: u32) {
    let reward = T::BlockReward::get();
    if let Some(_val) = Validators::<T>::get(validator) {
        // Rewards given to ANY registered validator
```

```rust
// AFTER: verify validator is active and in the active set:
pub fn reward_block_producer(validator: &T::AccountId, block: u32) {
    let reward = T::BlockReward::get();

    // Only reward active, non-slashed validators in the active set
    let active_validators = ActiveValidators::<T>::get();
    if !active_validators.contains(validator) {
        return;
    }

    let val = match Validators::<T>::get(validator) {
        Some(v) if v.active && !v.slashed => v,
        _ => return,
    };

    let reward_pool: T::AccountId = T::PalletId::get().into_account_truncating();
    let pool_balance = T::Currency::free_balance(&reward_pool);

    if pool_balance < reward {
        Self::deposit_event(Event::RewardPoolDepleted {
            remaining: pool_balance,
        });
        return;
    }

    if T::Currency::transfer(
        &reward_pool,
        validator,
        reward,
        ExistenceRequirement::AllowDeath,
    )
    .is_err()
    {
        return;
    }

    Validators::<T>::mutate(validator, |v| {
        if let Some(v) = v {
            v.blocks_produced = v.blocks_produced.saturating_add(1);
            v.rewards_earned = v.rewards_earned.saturating_add(reward);
        }
    });

    Self::deposit_event(Event::BlockReward {
        validator: validator.clone(),
        reward,
        block,
    });
}
```

---

### MEDIUM-4: Missing `ValidatorList` Cleanup on Slash

**Location:** `slash_validator` and `do_slash`

**Description:** When a validator is slashed, they are removed from `ActiveValidators` but **not** from `ValidatorList`. On the next `rotate_epoch`, they will be considered as candidates again (filtered by `!v.slashed`), but their entry wastes iteration space and they remain in `ValidatorList` until manual cleanup or reactivation. Over time this clutters the list.

```rust
// BEFORE (ValidatorList not cleaned up on slash):
ActiveValidators::<T>::mutate(|v| v.retain(|a| a != &validator));
// ValidatorList unchanged — slashed validator stays in candidate pool

// AFTER: remove from ValidatorList on slash too:
ActiveValidators::<T>::mutate(|v| v.retain(|a| a != &validator));
ValidatorList::<T>::mutate(|v| v.retain(|a| a != &validator));
// On reactivate_validator, re-add to ValidatorList as shown in MEDIUM-2 fix
```

---

### LOW-1: `set_commission` Uses Wrong Weight

**Location:** `set_commission` ~line 350

**Description:** `set_commission` is attributed `T::WeightInfo::update_green_score()` weight. It should have its own weight benchmark.

```rust
// BEFORE:
#[pallet::weight(T::WeightInfo::update_green_score())]
pub fn set_commission(origin: OriginFor<T>, rate: u8) -> DispatchResult {
```

```rust
// AFTER: add to WeightInfo trait and use correct weight:
pub trait WeightInfo {
    fn register_validator() -> Weight;
    fn unregister_validator() -> Weight;
    fn vote() -> Weight;
    fn unvote() -> Weight;
    fn slash_validator() -> Weight;
    fn update_green_score() -> Weight;
    fn withdraw_unbonded() -> Weight;
    fn set_commission() -> Weight;      // ADD THIS
    fn reactivate_validator() -> Weight; // ADD THIS
    fn refill_reward_pool() -> Weight;   // ADD THIS
}

#[pallet::weight(T::WeightInfo::set_commission())]
pub fn set_commission(origin: OriginFor<T>, rate: u8) -> DispatchResult {
```

---

### LOW-2: `TotalStaked` Decremented in `unvote` But Funds Remain Reserved

**Location:** `unvote` ~line 300

**Description:** `TotalStaked` is decremented when `unvote` is called, but the funds remain reserved until `withdraw_unbonded`. This means `TotalStaked` doesn't accurately reflect the total amount of reserved/locked tokens in the system during the unbonding window. Depending on how `TotalStaked` is used (e.g., for security calculations, reward distribution ratios), this creates an accounting discrepancy.

```rust
// BEFORE (TotalStaked decremented while funds still reserved):
// Reduce total staked but keep funds locked in unbonding queue
TotalStaked::<T>::mutate(|t| *t = t.saturating_sub(amount));
```

```rust
// AFTER option A — decrement TotalStaked only on actual withdrawal:
// In unvote(): remove the TotalStaked decrement entirely.
// In withdraw_unbonded(): keep the existing unreserve and add:
TotalStaked::<T>::mutate(|t| *t = t.saturating_sub(total_withdrawable));

// AFTER option B — add UnbondingTotal tracking:
#[pallet::storage]
pub type TotalUnbonding<T: Config> = StorageValue<_, BalanceOf<T>, ValueQuery>;

// In unvote(): 
TotalStaked::<T>::mutate(|t| *t = t.saturating_sub(amount));
TotalUnbonding::<T>::mutate(|t| *t = t.saturating_add(amount));

// In withdraw_unbonded():
TotalUnbonding::<T>::mutate(|t| *t = t.saturating_sub(total_withdrawable));
```

---

## Summary Fix Priority

```
CRITICAL (fix immediately):
  1. do_slash: unbounded Votes::iter() → add ValidatorDelegators reverse index
  2. do_slash: overflow in slash fraction BPS calculation → proportional_slash helper
  3. slash_validator: unreserve return value semantics inverted
  4. reactivate_validator: u32 overflow on cooldown addition → saturating_add
  5. refill_reward_pool: separate reward pool from treasury PalletId

HIGH (fix before mainnet):
  6. do_slash: validator mutated before delegator loop → collect-then-mutate
  7. unregister_validator: delegator funds permanently locked → release on unregister
  8. SlashingEvents: *c += 1 overflow → saturating_add
  9. set_commission: wrong event emitted → CommissionUpdated event
 10. rotate_epoch: O(N) storage reads → cache effective votes

MEDIUM (fix before production):
 11. vote: TOCTOU on validator total_votes cap → try_mutate
 12. reactivate_validator: not re-added to ValidatorList/ActiveValidators
 13. reward_block_producer: no active set membership check
 14. slash: ValidatorList not cleaned up

LOW (best practices):
 15. set_commission: wrong weight attribution
 16. unvote: TotalStaked accounting during unbonding period
```