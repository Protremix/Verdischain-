# Verdis Eco Tracking Pallet — Security Review

---

## Finding 1: Unbounded Storage Iteration for Capacity Checks

**Severity:** HIGH
**Location:** `mint_carbon_credit` (~line 195), `create_reforest_project` (~line 280), `register_green_validator` (~line 340)

**Description:** All three capacity checks use `StorageMap::iter().count()` which iterates the **entire map on every call**. This is O(n) in block execution weight, is not reflected in the declared weight, can be used to DoS the chain as storage grows, and is a classic unbounded iteration vulnerability in Substrate pallets.

**Fix:** Add counter storage values and increment/decrement them atomically.

```rust
// BEFORE (in mint_carbon_credit):
ensure!(
    (CarbonCredits::<T>::iter().count() as u32) < T::MaxCarbonCredits::get(),
    Error::<T>::MaxCarbonCreditsReached
);

// AFTER — add these three storage items:
#[pallet::storage]
pub type CarbonCreditCount<T: Config> = StorageValue<_, u32, ValueQuery>;

#[pallet::storage]
pub type ReforestProjectCount<T: Config> = StorageValue<_, u32, ValueQuery>;

#[pallet::storage]
pub type GreenValidatorCount<T: Config> = StorageValue<_, u32, ValueQuery>;

// Then in mint_carbon_credit:
let count = CarbonCreditCount::<T>::get();
ensure!(count < T::MaxCarbonCredits::get(), Error::<T>::MaxCarbonCreditsReached);
// ... insert credit ...
CarbonCreditCount::<T>::put(count.saturating_add(1));

// Same pattern for create_reforest_project:
let count = ReforestProjectCount::<T>::get();
ensure!(count < T::MaxReforestProjects::get(), Error::<T>::MaxReforestProjectsReached);
// ... insert project ...
ReforestProjectCount::<T>::put(count.saturating_add(1));

// Same pattern for register_green_validator:
let count = GreenValidatorCount::<T>::get();
ensure!(count < T::MaxGreenValidators::get(), Error::<T>::MaxGreenValidatorsReached);
// ... insert validator ...
GreenValidatorCount::<T>::put(count.saturating_add(1));
```

---

## Finding 2: `retire_carbon_credit` — Double Read with TOCTOU Race and Missing `CreditNotVerified` Check

**Severity:** HIGH
**Location:** `retire_carbon_credit` (~lines 220–240)

**Description:** Two separate problems:

1. **TOCTOU / state inconsistency:** The function mutates the credit (sets `retired = true`) in a first storage access, then does a **second `get`** to read `tons_co2` for the `TotalCreditsRetired` update. Between the mutate and the get, in a concurrent or re-entrant context this could behave unexpectedly. More practically, it's unnecessary extra I/O and fragile pattern.

2. **Missing verified check:** A credit owner can retire an **unverified** credit, inflating `TotalCreditsRetired` with unaudited carbon tonnage. The `CreditNotVerified` error exists but is never used in `retire_carbon_credit`.

```rust
// BEFORE:
CarbonCredits::<T>::mutate(&id_bv, |c| {
    let credit = c.as_mut().ok_or(Error::<T>::CreditNotFound)?;
    ensure!(&credit.owner == &who, Error::<T>::NotCreditOwner);
    ensure!(!credit.retired, Error::<T>::CreditAlreadyRetired);
    credit.retired = true;
    Ok::<(), Error<T>>(())
})?;

let credit = CarbonCredits::<T>::get(&id_bv).ok_or(Error::<T>::CreditNotFound)?;
TotalCreditsRetired::<T>::mutate(|t| *t = t.saturating_add(credit.tons_co2));

Self::deposit_event(Event::CarbonCreditRetired {
    id,
    tons_co2: credit.tons_co2,
});

// AFTER — single atomic mutate, capture tons_co2, add verified check:
let tons_co2 = {
    let mut captured = 0u64;
    CarbonCredits::<T>::mutate(&id_bv, |c| {
        let credit = c.as_mut().ok_or(Error::<T>::CreditNotFound)?;
        ensure!(&credit.owner == &who, Error::<T>::NotCreditOwner);
        ensure!(credit.verified, Error::<T>::CreditNotVerified);
        ensure!(!credit.retired, Error::<T>::CreditAlreadyRetired);
        credit.retired = true;
        captured = credit.tons_co2;
        Ok::<(), Error<T>>(())
    })?;
    captured
};

TotalCreditsRetired::<T>::mutate(|t| *t = t.saturating_add(tons_co2));

Self::deposit_event(Event::CarbonCreditRetired { id, tons_co2 });
```

---

## Finding 3: `update_reforest_project` — `TotalTreesPlanted` Not Updated (State Consistency Bug)

**Severity:** HIGH
**Location:** `update_reforest_project` (~lines 300–320)

**Description:** When a project's `trees_planted` is updated, `TotalTreesPlanted` is **never adjusted**. The global aggregate becomes permanently desynchronized from project data. An admin could call this to update to any value (higher or lower), making the on-chain metric meaningless and exploitable for false reporting.

```rust
// BEFORE:
ReforestProjects::<T>::mutate(&id_bv, |p| {
    let project = p.as_mut().ok_or(Error::<T>::ProjectNotFound)?;
    project.trees_planted = trees_planted;
    project.survival_rate = survival_rate;
    Ok::<(), Error<T>>(())
})?;

// AFTER — read old value, compute delta, update aggregate:
let old_trees = {
    let mut old = 0u32;
    ReforestProjects::<T>::mutate(&id_bv, |p| {
        let project = p.as_mut().ok_or(Error::<T>::ProjectNotFound)?;
        old = project.trees_planted;
        project.trees_planted = trees_planted;
        project.survival_rate = survival_rate;
        Ok::<(), Error<T>>(())
    })?;
    old
};

TotalTreesPlanted::<T>::mutate(|total| {
    *total = total.saturating_sub(old_trees).saturating_add(trees_planted);
});
```

---

## Finding 4: `transfer_carbon_credit` — Allows Transfer of Retired Credits

**Severity:** HIGH
**Location:** `transfer_carbon_credit` (~lines 250–268)

**Description:** The transfer function checks `!credit.retired`, but does **not** check `credit.verified`. More critically, a retired credit's ownership can still be transferred due to a logic error — the `retired` check is present but let's verify the exact guard order. Actually the check IS present for retired. However, there is **no check that the credit is not retired before transfer** at the protocol level for verified-only transfers. More importantly: **verified credits can be transferred freely, allowing wash trading** of unverified credits that may later be verified by a colluding root. Consider whether unverified credits should be transferable.

Additionally, the function emits `CarbonCreditTransferred` even when transferring to the **same account** (self-transfer), which pollutes event history and could be used to fake activity.

```rust
// BEFORE:
CarbonCredits::<T>::mutate(&id_bv, |c| {
    let credit = c.as_mut().ok_or(Error::<T>::CreditNotFound)?;
    ensure!(&credit.owner == &who, Error::<T>::NotCreditOwner);
    ensure!(!credit.retired, Error::<T>::CreditAlreadyRetired);
    credit.owner = to.clone();
    Ok::<(), Error<T>>(())
})?;

// AFTER — add self-transfer guard and verified check:
ensure!(who != to, Error::<T>::InvalidTransfer); // add InvalidTransfer variant

CarbonCredits::<T>::mutate(&id_bv, |c| {
    let credit = c.as_mut().ok_or(Error::<T>::CreditNotFound)?;
    ensure!(&credit.owner == &who, Error::<T>::NotCreditOwner);
    ensure!(credit.verified, Error::<T>::CreditNotVerified);
    ensure!(!credit.retired, Error::<T>::CreditAlreadyRetired);
    credit.owner = to.clone();
    Ok::<(), Error<T>>(())
})?;
```

---

## Finding 5: `last_updated` Always Set to `0` — No Block Number Tracking

**Severity:** MEDIUM
**Location:** `register_green_validator` (~line 355), `update_green_score` (~line 385), genesis build

**Description:** `last_updated` is always hardcoded to `0` instead of using `frame_system::Pallet::<T>::block_number()`. This makes the field completely useless for any rate-limiting, staleness detection, or audit purposes. It also means the `GreenValidator` struct stores misleading data that could be relied upon by off-chain systems.

```rust
// BEFORE (in register_green_validator):
let gv = GreenValidator {
    // ...
    last_updated: 0,
};

// BEFORE (in update_green_score):
GreenValidators::<T>::mutate(&who, |v| {
    if let Some(v) = v {
        v.score = score;
        v.last_updated = 0;  // bug
    }
});

// AFTER — use actual block number:
// First, change last_updated field type to T::BlockNumber or u64 via block number conversion.
// Simplest approach with u64:
use sp_runtime::traits::SaturatedConversion;

let current_block: u64 = 
    frame_system::Pallet::<T>::block_number().saturated_into::<u64>();

// in register_green_validator:
let gv = GreenValidator {
    // ...
    last_updated: current_block,
};

// in update_green_score:
GreenValidators::<T>::mutate(&who, |v| {
    if let Some(v) = v {
        v.score = score;
        v.last_updated = current_block;
    }
});
```

---

## Finding 6: `mint_carbon_credit` — `TotalCO2Offset` Incremented for Unverified Credits

**Severity:** MEDIUM
**Location:** `mint_carbon_credit` (~line 210)

**Description:** `TotalCO2Offset` is incremented at mint time, before verification. This means the aggregate metric reflects unaudited, potentially fraudulent carbon claims. A malicious root (or compromised root key) can inflate the global CO2 offset metric without any verification step. The offset should only count verified credits.

```rust
// BEFORE (in mint_carbon_credit):
CarbonCredits::<T>::insert(id_bv, credit);
TotalCO2Offset::<T>::mutate(|t| *t = t.saturating_add(tons_co2));

// AFTER — remove from mint, add to verify:
// In mint_carbon_credit, remove the TotalCO2Offset mutation entirely:
CarbonCredits::<T>::insert(id_bv, credit);
// (no TotalCO2Offset update here)

// In verify_carbon_credit, capture tons_co2 and update:
let tons_co2 = {
    let mut captured = 0u64;
    CarbonCredits::<T>::mutate(&id_bv, |c| {
        let credit = c.as_mut().ok_or(Error::<T>::CreditNotFound)?;
        ensure!(!credit.verified, Error::<T>::AlreadyVerified);
        credit.verified = true;
        captured = credit.tons_co2;
        Ok::<(), Error<T>>(())
    })?;
    captured
};

TotalCO2Offset::<T>::mutate(|t| *t = t.saturating_add(tons_co2));
```

---

## Finding 7: `update_reforest_project` — No Authorization Beyond Root, Verified Projects Can Be Silently Modified

**Severity:** MEDIUM
**Location:** `update_reforest_project` (~line 300)

**Description:** A verified project's `trees_planted` and `survival_rate` can be updated by root **after verification** with no re-verification required and no event indicating that a previously-verified project was modified. This breaks the integrity of the verification system — verified data should be immutable or require re-verification.

```rust
// BEFORE:
ReforestProjects::<T>::mutate(&id_bv, |p| {
    let project = p.as_mut().ok_or(Error::<T>::ProjectNotFound)?;
    project.trees_planted = trees_planted;
    project.survival_rate = survival_rate;
    Ok::<(), Error<T>>(())
})?;

// AFTER — invalidate verification on update:
ReforestProjects::<T>::mutate(&id_bv, |p| {
    let project = p.as_mut().ok_or(Error::<T>::ProjectNotFound)?;
    project.trees_planted = trees_planted;
    project.survival_rate = survival_rate;
    // Reset verification — data has changed, must re-verify
    project.verified = false;
    Ok::<(), Error<T>>(())
})?;
```

---

## Finding 8: `register_green_validator` — Self-Reported Score with No Validation Against Actual Data

**Severity:** MEDIUM
**Location:** `register_green_validator` (~line 335)

**Description:** Any signed user can register as a green validator and **self-report** their `carbon_offset`, `trees_planted`, and `score` (within min/max bounds). The `renewable_energy` flag is hardcoded to `true` regardless of what `energy_source` the user provides. There is no on-chain linkage between the self-reported `carbon_offset` and actual `CarbonCredit` records, enabling Sybil attacks and false green credentials.

```rust
// BEFORE:
let gv = GreenValidator {
    address: who.clone(),
    renewable_energy: true,  // always true regardless of input
    energy_source: energy_bv,
    carbon_offset,           // self-reported, unverified
    trees_planted,           // self-reported, unverified
    score,                   // self-reported within bounds
    last_updated: 0,
};

// AFTER — score should be assigned by root/oracle, not self-reported:
// Change function signature: remove score parameter from register call.
// Score starts at MinGreenScore and is only updated by root via update_green_score.
pub fn register_green_validator(
    origin: OriginFor<T>,
    energy_source: Vec<u8>,
    carbon_offset: u64,
    trees_planted: u32,
    // score removed — assigned by authority only
) -> DispatchResult {
    let who = ensure_signed(origin)?;
    // ...
    let gv = GreenValidator {
        address: who.clone(),
        renewable_energy: false, // default false until verified by authority
        energy_source: energy_bv,
        carbon_offset,
        trees_planted,
        score: T::MinGreenScore::get(), // start at minimum
        last_updated: current_block,
    };
```

---

## Finding 9: `update_green_score` — Silent Failure if Validator Not Found in Mutate

**Severity:** LOW
**Location:** `update_green_score` (~lines 383–390)

**Description:** After the `contains_key` check, the `mutate` closure uses `if let Some(v) = v` which **silently does nothing** if the entry is missing (e.g., due to a race). The function would return `Ok(())` and emit a `GreenScoreUpdated` event without actually updating anything. Should use a hard error.

```rust
// BEFORE:
GreenValidators::<T>::mutate(&who, |v| {
    if let Some(v) = v {
        v.score = score;
        v.last_updated = 0;
    }
});

// AFTER — propagate error:
GreenValidators::<T>::mutate(&who, |v| {
    let validator = v.as_mut().ok_or(Error::<T>::ValidatorNotFound)?;
    validator.score = score;
    validator.last_updated = current_block;
    Ok::<(), Error<T>>(())
})?;
```

---

## Finding 10: Missing `created_at` Timestamp — Audit Trail Incomplete

**Severity:** LOW
**Location:** `mint_carbon_credit` (~line 197), genesis build

**Description:** `created_at` is always `0` in both the extrinsic and genesis build. Carbon credits require a creation timestamp for regulatory compliance and audit trails. Combined with Finding 5, the pallet stores no meaningful temporal data.

```rust
// BEFORE:
let credit = CarbonCredit {
    // ...
    created_at: 0,
};

// AFTER:
use sp_runtime::traits::SaturatedConversion;
let current_block: u64 = 
    frame_system::Pallet::<T>::block_number().saturated_into::<u64>();

let credit = CarbonCredit {
    // ...
    created_at: current_block,
};
```

---

## Summary Table

| # | Severity | Location | Issue |
|---|----------|----------|-------|
| 1 | HIGH | `mint_carbon_credit`, `create_reforest_project`, `register_green_validator` | Unbounded `iter().count()` for capacity checks |
| 2 | HIGH | `retire_carbon_credit` | TOCTOU double-read + unverified credits can be retired |
| 3 | HIGH | `update_reforest_project` | `TotalTreesPlanted` never updated on project update |
| 4 | HIGH | `transfer_carbon_credit` | Self-transfer allowed; unverified credits transferable |
| 5 | MEDIUM | `register_green_validator`, `update_green_score` | `last_updated` always `0` |
| 6 | MEDIUM | `mint_carbon_credit` | `TotalCO2Offset` counts unverified credits |
| 7 | MEDIUM | `update_reforest_project` | Verified projects silently mutable without re-verification |
| 8 | MEDIUM | `register_green_validator` | Self-reported score/data; `renewable_energy` hardcoded `true` |
| 9 | LOW | `update_green_score` | Silent failure in mutate closure |
| 10 | LOW | `mint_carbon_credit`, genesis | `created_at` always `0` |