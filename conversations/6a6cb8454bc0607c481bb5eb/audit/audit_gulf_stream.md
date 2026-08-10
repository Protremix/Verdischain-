# Gulf Stream Pallet — Security Code Review

## Executive Summary

This pallet has **critical authorization failures**, **arithmetic overflow risks**, **unbounded storage growth**, and **state consistency bugs** that would allow any user to manipulate blockchain state, corrupt statistics, and cause storage bloat.

---

## Finding 1: Missing MaxPendingForwards Enforcement

**Severity:** HIGH
**Location:** `forward_transaction`

**Description:** The config defines `MaxPendingForwards: Get<u32>` but it is **never checked**. Any caller can insert unlimited entries into `PendingForwards`, causing unbounded storage growth and potential DoS.

```rust
// BEFORE — no cap enforced
pub fn forward_transaction(
    origin: OriginFor<T>,
    tx_hash: [u8; 32],
    to_validator: Vec<u8>,
    tx_size: u32,
) -> DispatchResult {
    let who = ensure_signed(origin)?;
    ensure!(
        !PendingForwards::<T>::contains_key(tx_hash),
        Error::<T>::AlreadyForwarded
    );
    // ... inserts unconditionally

// AFTER — enforce the cap BEFORE inserting
pub fn forward_transaction(
    origin: OriginFor<T>,
    tx_hash: [u8; 32],
    to_validator: Vec<u8>,
    tx_size: u32,
) -> DispatchResult {
    let who = ensure_signed(origin)?;

    ensure!(
        !PendingForwards::<T>::contains_key(tx_hash),
        Error::<T>::AlreadyForwarded
    );

    // Enforce the configured cap using the tracked counter,
    // NOT an unbounded iter().count() call.
    let stats = GulfStreamStatsStorage::<T>::get();
    ensure!(
        stats.current_pending < T::MaxPendingForwards::get(),
        Error::<T>::MaxPendingExceeded
    );
    // ... rest of function unchanged
```

---

## Finding 2: Authorization — Anyone Can Mark Transactions Included or Expired

**Severity:** CRITICAL
**Location:** `mark_included`, `expire_transaction`

**Description:** Both functions discard the caller identity with `let _ = ensure_signed(origin)?`. Any signed account — not just the intended validator or a privileged origin — can mark **any** pending transaction as included or expired, corrupt statistics, and grief legitimate validators.

```rust
// BEFORE — identity thrown away, no ownership check
pub fn mark_included(
    origin: OriginFor<T>,
    tx_hash: [u8; 32],
    block_number: u32,
    forward_time_ms: u64,
) -> DispatchResult {
    let _ = ensure_signed(origin)?;
    let mut tx =
        PendingForwards::<T>::get(tx_hash).ok_or(Error::<T>::TransactionNotFound)?;
    // ...

// AFTER — caller must be the original forwarder (or a root/sudo origin)
pub fn mark_included(
    origin: OriginFor<T>,
    tx_hash: [u8; 32],
    block_number: u32,
    forward_time_ms: u64,
) -> DispatchResult {
    let who = ensure_signed(origin)?;

    let tx = PendingForwards::<T>::get(tx_hash)
        .ok_or(Error::<T>::TransactionNotFound)?;

    // Only the validator who originally forwarded the tx may mark it included.
    ensure!(
        tx.from_validator == who.encode(),
        Error::<T>::NotAuthorized       // add this variant to Error<T>
    );
    // ... rest of function unchanged
```

Apply the identical fix to `expire_transaction`:

```rust
// BEFORE
pub fn expire_transaction(origin: OriginFor<T>, tx_hash: [u8; 32]) -> DispatchResult {
    let _ = ensure_signed(origin)?;
    let _tx = PendingForwards::<T>::get(tx_hash).ok_or(Error::<T>::TransactionNotFound)?;

// AFTER
pub fn expire_transaction(origin: OriginFor<T>, tx_hash: [u8; 32]) -> DispatchResult {
    let who = ensure_signed(origin)?;
    let tx = PendingForwards::<T>::get(tx_hash)
        .ok_or(Error::<T>::TransactionNotFound)?;
    ensure!(
        tx.from_validator == who.encode(),
        Error::<T>::NotAuthorized
    );
```

Add the new error variant:

```rust
// BEFORE
#[pallet::error]
pub enum Error<T> {
    MaxPendingExceeded,
    AlreadyForwarded,
    TransactionNotFound,
}

// AFTER
#[pallet::error]
pub enum Error<T> {
    MaxPendingExceeded,
    AlreadyForwarded,
    TransactionNotFound,
    NotAuthorized,
}
```

---

## Finding 3: Arithmetic Overflow in `success_rate` Calculation

**Severity:** CRITICAL
**Location:** `mark_included`, `expire_transaction`

**Description:** `stats.total_included * 100` is a `u64` multiplication with **no overflow guard**. At `u64::MAX / 100 ≈ 1.8 × 10¹⁷` included transactions this wraps and produces a nonsensical (and exploitable) success rate. The cast to `u32` also silently truncates values above `u32::MAX`.

```rust
// BEFORE — unchecked multiplication and lossy cast
let total = stats.total_included + stats.total_expired;
if total > 0 {
    stats.success_rate = (stats.total_included * 100 / total) as u32;
}

// AFTER — saturating arithmetic, then bounded cast
let total = stats.total_included.saturating_add(stats.total_expired);
if total > 0 {
    // saturating_mul prevents overflow; result is always ≤ 100,
    // so the u32 cast is always safe.
    let rate = stats.total_included
        .saturating_mul(100)
        .saturating_div(total);
    stats.success_rate = rate.min(100) as u32;
}
```

---

## Finding 4: Arithmetic Overflow in `total_forwarded` / `total_included` / `total_expired` Counters

**Severity:** HIGH
**Location:** `forward_transaction`, `mark_included`, `expire_transaction`

**Description:** All three `u64` counters use raw `+=` / `+` without overflow protection. A sufficiently active chain (or a malicious spam campaign) will eventually wrap these to zero, corrupting all downstream statistics.

```rust
// BEFORE — raw addition, panics in debug, wraps in release
stats.total_forwarded += 1;
stats.current_pending += 1;

// BEFORE (mark_included)
stats.total_included += 1;
let total = stats.total_included + stats.total_expired;

// AFTER — saturating everywhere
// forward_transaction:
stats.total_forwarded = stats.total_forwarded.saturating_add(1);
stats.current_pending = stats.current_pending.saturating_add(1);

// mark_included:
stats.total_included = stats.total_included.saturating_add(1);
let total = stats.total_included.saturating_add(stats.total_expired);

// expire_transaction:
stats.total_expired = stats.total_expired.saturating_add(1);
let total = stats.total_included.saturating_add(stats.total_expired);
```

---

## Finding 5: Unbounded `ForwardedTxs` Vec — Storage Growth and Missing Cleanup

**Severity:** HIGH
**Location:** `forward_transaction`, `mark_included`, `expire_transaction`

**Description:** Every call to `forward_transaction` unconditionally `push`es to the `ForwardedTxs` `StorageValue<Vec<[u8;32]>>`. Entries are **never removed** when transactions are included or expired. Over time this Vec grows without bound, decoding it on every mutate becomes progressively more expensive (O(n) decode + encode), and it can exceed block weight limits.

```rust
// BEFORE — push only, never remove, no cap
ForwardedTxs::<T>::mutate(|txs| txs.push(tx_hash));

// AFTER — option A: remove on finalisation (preferred)
// In forward_transaction — keep the push:
ForwardedTxs::<T>::mutate(|txs| {
    if txs.len() < T::MaxForwardedHistory::get() as usize {
        txs.push(tx_hash);
    }
});

// In mark_included AND expire_transaction — remove the entry:
ForwardedTxs::<T>::mutate(|txs| txs.retain(|h| h != &tx_hash));
```

For long-term production use, replace `StorageValue<Vec<_>>` with a `StorageMap` (already present as `PendingForwards`) and drop the separate `ForwardedTxs` list entirely, using `PendingForwards::iter_keys()` only in off-chain contexts.

---

## Finding 6: `get_pending_count` Uses Unbounded Full-Map Iteration

**Severity:** MEDIUM
**Location:** `get_pending_count`

**Description:** `PendingForwards::<T>::iter().count()` iterates every key in the map. Called on-chain (e.g., from a runtime API or benchmark) this is O(n) and can exhaust block weight. The `current_pending` field in `GulfStreamStats` already tracks this value and should be used instead.

```rust
// BEFORE — O(n) full iteration
pub fn get_pending_count() -> u32 {
    PendingForwards::<T>::iter().count() as u32
}

// AFTER — O(1) cached counter
pub fn get_pending_count() -> u32 {
    GulfStreamStatsStorage::<T>::get().current_pending
}
```

---

## Finding 7: Moving Average Overflow in `avg_forward_time_ms`

**Severity:** HIGH
**Location:** `mark_included`

**Description:** The incremental average computation multiplies two `u64` values together: `stats.avg_forward_time_ms * (stats.total_included - 1)`. If `avg_forward_time_ms` is large (e.g., a malicious caller passes `u64::MAX` as `forward_time_ms`) and `total_included` is non-trivial, this overflows silently in release mode.

```rust
// BEFORE — overflow-prone moving average
let new_avg = if stats.total_included == 1 {
    forward_time_ms
} else {
    (stats.avg_forward_time_ms * (stats.total_included - 1) + forward_time_ms)
        / stats.total_included
};
stats.avg_forward_time_ms = new_avg;

// AFTER — saturating moving average
let new_avg = if stats.total_included == 1 {
    forward_time_ms
} else {
    let prev_count = stats.total_included.saturating_sub(1);
    let weighted_prev = stats.avg_forward_time_ms.saturating_mul(prev_count);
    let total_time = weighted_prev.saturating_add(forward_time_ms);
    total_time.saturating_div(stats.total_included)
};
stats.avg_forward_time_ms = new_avg;
```

---

## Finding 8: Unbounded `to_validator` Input — No Length Validation

**Severity:** MEDIUM
**Location:** `forward_transaction`

**Description:** `to_validator: Vec<u8>` is accepted without any length cap. A caller can submit a multi-megabyte byte vector that is persisted in `PendingForwards` storage, consuming chain storage at negligible cost (weight is `0`).

```rust
// BEFORE — no length check
pub fn forward_transaction(
    origin: OriginFor<T>,
    tx_hash: [u8; 32],
    to_validator: Vec<u8>,
    tx_size: u32,
) -> DispatchResult {

// AFTER — add a config constant and enforce it
// In Config trait:
type MaxValidatorIdLen: Get<u32>;

// In forward_transaction:
ensure!(
    to_validator.len() <= T::MaxValidatorIdLen::get() as usize,
    Error::<T>::ValidatorIdTooLong   // add to Error<T>
);
```

---

## Finding 9: Zero Transaction Weight Enables Free DoS

**Severity:** MEDIUM
**Location:** `forward_transaction`, `mark_included`, `expire_transaction`

**Description:** All three extrinsics declare `#[pallet::weight(0)]`. This means callers pay zero fees regardless of storage written or reads performed, making spam economically free.

```rust
// BEFORE
#[pallet::weight(0)]
pub fn forward_transaction( ...

// AFTER — use a benchmarked WeightInfo; as a minimum viable fix:
#[pallet::weight(T::DbWeight::get().reads_writes(2, 3))]
pub fn forward_transaction( ...

#[pallet::weight(T::DbWeight::get().reads_writes(2, 3))]
pub fn mark_included( ...

#[pallet::weight(T::DbWeight::get().reads_writes(2, 2))]
pub fn expire_transaction( ...
```

---

## Summary Table

| # | Severity | Location | Issue |
|---|----------|----------|-------|
| 1 | HIGH | `forward_transaction` | `MaxPendingForwards` never enforced |
| 2 | **CRITICAL** | `mark_included`, `expire_transaction` | Any user can mutate any transaction |
| 3 | **CRITICAL** | `mark_included`, `expire_transaction` | Overflow in `success_rate` multiplication |
| 4 | HIGH | all three calls | Raw `+=` on counters, no overflow protection |
| 5 | HIGH | `forward_transaction` | `ForwardedTxs` grows forever, never cleaned |
| 6 | MEDIUM | `get_pending_count` | O(n) full-map iteration on-chain |
| 7 | HIGH | `mark_included` | Moving average multiplication overflow |
| 8 | MEDIUM | `forward_transaction` | Unbounded `to_validator` input length |
| 9 | MEDIUM | all three calls | Zero weight — free DoS vector |