# Substrate Pallet Security Review: Verdis Decentralized Storage

## Executive Summary

Found **9 security findings** across the codebase: 2 CRITICAL, 3 HIGH, 2 MEDIUM, 2 LOW severity issues.

---

## CRITICAL Findings

### CRITICAL-1: Unbounded Storage Iteration in `register_storage`

**Location:** `register_storage` function  
**Description:** `StorageRecords::<T>::iter().count()` performs a full scan of all storage records on every registration call. With `MaxRecords = 1000`, this is a DoS vector — an attacker can front-run legitimate users by filling records to 999, forcing all subsequent calls to iterate the entire map. This also makes block weight unpredictable and unbounded, breaking the weight system entirely. The declared weight of `80_000_000` is fictional.

**Before:**
```rust
ensure!(
    (StorageRecords::<T>::iter().count() as u32) < T::MaxRecords::get(),
    Error::<T>::MaxRecordsReached
);
```

**After:**
```rust
// Add a counter to storage
#[pallet::storage]
#[pallet::getter(fn record_count)]
pub type RecordCount<T: Config> = StorageValue<_, u32, ValueQuery>;

// In register_storage:
let current_count = RecordCount::<T>::get();
ensure!(current_count < T::MaxRecords::get(), Error::<T>::MaxRecordsReached);

// After inserting:
StorageRecords::<T>::insert(id_bv, record);
RecordCount::<T>::put(current_count.saturating_add(1));
TotalStored::<T>::mutate(|t| *t = t.saturating_add(size_bytes));
```

---

### CRITICAL-2: Missing Authorization on `request_pin`

**Location:** `request_pin` function  
**Description:** Any signed account can pin any storage record owned by anyone else. Pinning is a resource-consuming operation (it signals to providers to replicate data). An attacker can spam pin requests on all records, causing storage providers to waste resources pinning arbitrary content, and set `pinned = true` on records they don't own — interfering with the owner's ability to manage their content lifecycle. The `_who` variable is explicitly discarded.

**Before:**
```rust
pub fn request_pin(origin: OriginFor<T>, id: Vec<u8>) -> DispatchResult {
    let _who = ensure_signed(origin)?;

    let id_bv: BoundedVec<u8, ConstU32<64>> =
        id.clone().try_into().map_err(|_| Error::<T>::IdTooLong)?;

    ensure!(
        StorageRecords::<T>::contains_key(&id_bv),
        Error::<T>::RecordNotFound
    );
    PinRequests::<T>::insert(&id_bv, true);
    StorageRecords::<T>::mutate(&id_bv, |r| {
        if let Some(r) = r {
            r.pinned = true;
        }
    });

    Self::deposit_event(Event::PinRequested { id });
    Ok(())
}
```

**After:**
```rust
pub fn request_pin(origin: OriginFor<T>, id: Vec<u8>) -> DispatchResult {
    let who = ensure_signed(origin)?;

    let id_bv: BoundedVec<u8, ConstU32<64>> =
        id.clone().try_into().map_err(|_| Error::<T>::IdTooLong)?;

    let record = StorageRecords::<T>::get(&id_bv)
        .ok_or(Error::<T>::RecordNotFound)?;
    ensure!(record.owner == who, Error::<T>::NotRecordOwner);

    PinRequests::<T>::insert(&id_bv, true);
    StorageRecords::<T>::mutate(&id_bv, |r| {
        if let Some(r) = r {
            r.pinned = true;
        }
    });

    Self::deposit_event(Event::PinRequested { id });
    Ok(())
}
```

---

## HIGH Findings

### HIGH-1: `TotalStored` Never Decremented — Permanent Inflation

**Location:** No deletion/cleanup function exists  
**Description:** `TotalStored` is incremented when records are registered but there is no extrinsic to delete a storage record. Even if one were added later, the current architecture has no `remove_storage` call, meaning `TotalStored` permanently grows and never reflects actual stored bytes. Any on-chain logic or off-chain indexers relying on this value for capacity planning will be corrupted. Additionally, if a delete function is later naively added without decrementing `TotalStored`, the counter permanently diverges.

**Before:**
```rust
// No remove_storage extrinsic exists at all
StorageRecords::<T>::insert(id_bv, record);
TotalStored::<T>::mutate(|t| *t = t.saturating_add(size_bytes));
```

**After:**
```rust
// In register_storage — unchanged, correct
StorageRecords::<T>::insert(id_bv, record);
RecordCount::<T>::put(current_count.saturating_add(1)); // from CRITICAL-1 fix
TotalStored::<T>::mutate(|t| *t = t.saturating_add(size_bytes));

// Add remove_storage extrinsic:
#[pallet::call_index(5)]
#[pallet::weight(Weight::from_parts(25_000_000, 0))]
pub fn remove_storage(origin: OriginFor<T>, id: Vec<u8>) -> DispatchResult {
    let who = ensure_signed(origin)?;

    let id_bv: BoundedVec<u8, ConstU32<64>> =
        id.clone().try_into().map_err(|_| Error::<T>::IdTooLong)?;

    let record = StorageRecords::<T>::get(&id_bv)
        .ok_or(Error::<T>::RecordNotFound)?;
    ensure!(record.owner == who, Error::<T>::NotRecordOwner);

    StorageRecords::<T>::remove(&id_bv);
    PinRequests::<T>::remove(&id_bv); // cleanup orphaned pin
    RecordCount::<T>::mutate(|c| *c = c.saturating_sub(1));
    TotalStored::<T>::mutate(|t| *t = t.saturating_sub(record.size_bytes));

    Ok(())
}
```

---

### HIGH-2: `get_all_providers` — Unbounded Iteration in Public API

**Location:** `get_all_providers` function  
**Description:** This function iterates the entire `StorageProviders` map with no bound. While it's not an extrinsic (so it doesn't directly affect block weight), it will be called by RPC nodes. With enough registered providers, this causes RPC node OOM or extreme latency, becoming a remote DoS vector against node infrastructure. It also signals an architectural pattern that may be copied into extrinsics.

**Before:**
```rust
pub fn get_all_providers() -> Vec<StorageProvider<T::AccountId>> {
    StorageProviders::<T>::iter().map(|(_, p)| p).collect()
}
```

**After:**
```rust
/// Returns up to `limit` providers starting after `start_key` for pagination.
pub fn get_providers_paginated(
    start_key: Option<T::AccountId>,
    limit: u32,
) -> Vec<StorageProvider<T::AccountId>> {
    let max_limit = limit.min(100u32); // Hard cap per page
    match start_key {
        None => StorageProviders::<T>::iter()
            .take(max_limit as usize)
            .map(|(_, p)| p)
            .collect(),
        Some(key) => StorageProviders::<T>::iter()
            .skip_while(|(k, _)| k != &key)
            .skip(1)
            .take(max_limit as usize)
            .map(|(_, p)| p)
            .collect(),
    }
}
```

---

### HIGH-3: Orphaned `PinRequests` Entry When Record Is Never Deleted

**Location:** `request_pin` / storage design  
**Description:** `PinRequests` is a separate storage map keyed by the same ID as `StorageRecords`. If a record is deleted (once deletion is supported), the corresponding `PinRequests` entry becomes an orphan — an unbounded ghost entry that leaks storage permanently. Additionally, since `PinRequests` uses `ValueQuery` (defaults to `false`), a removed entry reads as `false` but the map entry still occupies trie space after `insert(_, true)` unless explicitly removed. This is already partially handled in `remove_pin` but `remove_pin` only works if the record still exists, creating a cleanup gap.

**Before:**
```rust
// remove_pin requires record to exist first, then removes pin
let record = StorageRecords::<T>::get(&id_bv).ok_or(Error::<T>::RecordNotFound)?;
ensure!(record.owner == who, Error::<T>::NotRecordOwner);
PinRequests::<T>::remove(&id_bv);
StorageRecords::<T>::mutate(&id_bv, |r| {
    if let Some(r) = r {
        r.pinned = false;
    }
});
```

**After:**
```rust
// remove_pin should not gate on record existence for cleanup purposes;
// the owner check still happens via the record lookup, but removal
// of pin state is idempotent and should be independent:
pub fn remove_pin(origin: OriginFor<T>, id: Vec<u8>) -> DispatchResult {
    let who = ensure_signed(origin)?;

    let id_bv: BoundedVec<u8, ConstU32<64>> =
        id.clone().try_into().map_err(|_| Error::<T>::IdTooLong)?;

    let record = StorageRecords::<T>::get(&id_bv)
        .ok_or(Error::<T>::RecordNotFound)?;
    ensure!(record.owner == who, Error::<T>::NotRecordOwner);

    // Always remove both, even if one is already in the correct state
    PinRequests::<T>::remove(&id_bv);
    StorageRecords::<T>::mutate(&id_bv, |r| {
        if let Some(r) = r {
            r.pinned = false;
        }
    });

    Self::deposit_event(Event::PinRemoved { id });
    Ok(())
}

// And in the remove_storage extrinsic (from HIGH-1):
PinRequests::<T>::remove(&id_bv); // always clean up pin on record removal
```

---

## MEDIUM Findings

### MEDIUM-1: State Inconsistency — `pinned` Field and `PinRequests` Can Diverge

**Location:** `request_pin`, `remove_pin`  
**Description:** The `pinned` boolean on `StorageRecord` and the `PinRequests` storage map are maintained separately and can diverge. If `StorageRecords::mutate` fails silently (e.g., record disappears between `contains_key` check and `mutate` call due to a concurrent extrinsic in the same block), the `PinRequests` map says `true` but the record says `false` (or vice versa). This is a TOCTOU (time-of-check-time-of-use) window. The check-then-mutate pattern should be collapsed into a single atomic operation.

**Before:**
```rust
// Two separate storage operations — not atomic
ensure!(
    StorageRecords::<T>::contains_key(&id_bv),
    Error::<T>::RecordNotFound
);
PinRequests::<T>::insert(&id_bv, true);
StorageRecords::<T>::mutate(&id_bv, |r| {
    if let Some(r) = r {
        r.pinned = true;
    }
});
```

**After:**
```rust
// Single atomic mutate — existence check and update in one operation
let mut found = false;
StorageRecords::<T>::mutate(&id_bv, |maybe_record| {
    if let Some(record) = maybe_record {
        ensure!(record.owner == who, Error::<T>::NotRecordOwner); // from CRITICAL-2
        record.pinned = true;
        found = true;
    }
});
ensure!(found, Error::<T>::RecordNotFound);
PinRequests::<T>::insert(&id_bv, true);
```

---

### MEDIUM-2: `created_at` Always Set to `0` — Missing Block Number

**Location:** `register_storage` function  
**Description:** `created_at` is hardcoded to `0` instead of using the current block number. This field is presumably intended for ordering, expiry logic, or audit purposes. Any downstream code (off-chain workers, other pallets) relying on this for temporal ordering will malfunction. All records appear to have been created at genesis.

**Before:**
```rust
let record = StorageRecord {
    id: id_bv.clone(),
    backend,
    owner: who.clone(),
    size_bytes,
    blake3_hash,
    pinned: false,
    created_at: 0, // BUG: always genesis
};
```

**After:**
```rust
// BlockNumberProvider gives current block as a u64-compatible type
let current_block = frame_system::Pallet::<T>::block_number();
// Convert BlockNumber to u64 safely
let created_at: u64 = TryInto::<u64>::try_into(current_block)
    .unwrap_or(u64::MAX);

let record = StorageRecord {
    id: id_bv.clone(),
    backend,
    owner: who.clone(),
    size_bytes,
    blake3_hash,
    pinned: false,
    created_at,
};
```

---

## LOW Findings

### LOW-1: Reputation System Has No Update Mechanism

**Location:** `register_provider`, `StorageProvider` struct  
**Description:** `reputation` is set to `100` at registration and there is no extrinsic or internal mechanism to update it. The field is dead code. This is not immediately exploitable but means the reputation system provides false assurance — all providers appear equally reputable regardless of behavior. Any consumer of this field makes decisions on stale data.

**Before:**
```rust
let provider = StorageProvider {
    address: who.clone(),
    backend,
    endpoint: endpoint_bv,
    reputation: 100,  // never updated
    total_stored: 0,  // never updated
    active: true,
};
```

**After:**
```rust
// Add update_provider_reputation extrinsic (admin/oracle only):
#[pallet::call_index(6)]
#[pallet::weight(Weight::from_parts(15_000_000, 0))]
pub fn update_provider_stats(
    origin: OriginFor<T>,
    provider: T::AccountId,
    reputation_delta: i32,
    stored_bytes_delta: u64,
) -> DispatchResult {
    // Require governance or a designated oracle origin
    T::UpdateOrigin::ensure_origin(origin)?;

    StorageProviders::<T>::mutate(&provider, |maybe_p| {
        if let Some(p) = maybe_p {
            p.reputation = if reputation_delta >= 0 {
                p.reputation.saturating_add(reputation_delta as u32)
            } else {
                p.reputation.saturating_sub((-reputation_delta) as u32)
            };
            p.total_stored = p.total_stored.saturating_add(stored_bytes_delta);
        }
    });
    Ok(())
}
```

---

### LOW-2: `#![allow(clippy::all)]` Suppresses Safety Lints Globally

**Location:** Top-level file attributes  
**Description:** `#![allow(clippy::all)]` disables all Clippy lints including arithmetic overflow warnings, iterator warnings, and correctness lints. Combined with `#![allow(deprecated)]`, this creates a "silent failure" environment where future regressions won't be caught by the linter. Several of the bugs in this review (unbounded iteration, unused variable `_who`) would have been flagged by Clippy.

**Before:**
```rust
#![allow(deprecated)]
#![allow(clippy::all)]
```

**After:**
```rust
#![allow(deprecated)] // Keep only if specific deprecated items are intentionally used
// Remove #![allow(clippy::all)] entirely, or use targeted allows:
#![allow(clippy::type_complexity)] // only if needed for specific complex types
```

---

## Summary Table

| ID | Severity | Location | Issue |
|---|---|---|---|
| CRITICAL-1 | CRITICAL | `register_storage` | Unbounded `iter().count()` — DoS + broken weight |
| CRITICAL-2 | CRITICAL | `request_pin` | Any user can pin any record — missing auth |
| HIGH-1 | HIGH | Missing extrinsic | `TotalStored` never decremented — no delete function |
| HIGH-2 | HIGH | `get_all_providers` | Unbounded iteration in public API |
| HIGH-3 | HIGH | `request_pin`/design | Orphaned `PinRequests` entries on record deletion |
| MEDIUM-1 | MEDIUM | `request_pin` | TOCTOU between `contains_key` and `mutate` |
| MEDIUM-2 | MEDIUM | `register_storage` | `created_at` hardcoded to `0` |
| LOW-1 | LOW | `register_provider` | Reputation/stats fields are dead code |
| LOW-2 | LOW | File attributes | `allow(clippy::all)` suppresses safety lints |