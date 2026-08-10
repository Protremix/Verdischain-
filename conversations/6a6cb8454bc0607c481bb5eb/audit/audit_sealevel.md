# Substrate Pallet Code Review

## Summary of Findings

| Severity | Count |
|----------|-------|
| CRITICAL | 2 |
| HIGH | 3 |
| MEDIUM | 3 |
| LOW | 2 |

---

## CRITICAL Findings

### CRITICAL-1: Arithmetic Overflow in `SealevelParallelizationRate` Calculation

**Location:** `create_batch`

**Description:** `parallel_count * 100` is performed on a `u64` without overflow protection. With `u64::MAX / 100 ≈ 1.8 × 10¹⁷` batches this wraps, but more critically the cast `as u32` silently truncates any value above `u32::MAX`. The result stored in `SealevelParallelizationRate` would be completely wrong. Additionally `parallel_count * 100 / total` performs integer division on a `u64` then casts, losing precision silently.

**Before:**
```rust
if total > 0 {
    SealevelParallelizationRate::<T>::put((parallel_count * 100 / total) as u32);
}
```

**After:**
```rust
if total > 0 {
    // Use saturating arithmetic and keep numerator multiplication safe.
    // Rate is in basis points (0..=100), so u32 is sufficient after safe cast.
    let rate = parallel_count
        .saturating_mul(100)
        .checked_div(total)
        .unwrap_or(0);
    // rate is at most 100, so the cast is safe, but we guard it anyway.
    let rate_u32 = u32::try_from(rate).unwrap_or(100u32);
    SealevelParallelizationRate::<T>::put(rate_u32);
}
```

---

### CRITICAL-2: Arithmetic Overflow/Underflow in Running Average Calculation

**Location:** `report_execution`

**Description:** The incremental average formula `(old_avg * (total_txs - tx_count) + compute_units) / total_txs` has **two independent overflow vectors**:

1. `old_avg * (total_txs - tx_count as u64)` — both operands are `u64`; the product can easily overflow (e.g., avg = 10⁹ CU × 10¹⁰ previous txs = 10¹⁹ > u64::MAX ≈ 1.8 × 10¹⁹).
2. `total_txs - tx_count as u64` — if `tx_count > total_txs` (possible due to the read-then-mutate ordering discussed in HIGH-2), this **underflows and panics in debug / wraps in release**.

Furthermore the formula itself is mathematically incorrect: a correct incremental average weights `compute_units` by `tx_count`, not by 1.

**Before:**
```rust
SealevelTotalTxs::<T>::mutate(|t| *t += tx_count as u64);
let total_txs = SealevelTotalTxs::<T>::get();
if total_txs > 0 {
    let avg = (SealevelAvgComputeUnits::<T>::get() * (total_txs - tx_count as u64)
        + compute_units)
        / total_txs;
    SealevelAvgComputeUnits::<T>::put(avg);
}
```

**After:**
```rust
let tx_count_u64 = tx_count as u64;

// Read BEFORE mutating so previous_total is consistent.
let previous_total = SealevelTotalTxs::<T>::get();
let new_total = previous_total.saturating_add(tx_count_u64);
SealevelTotalTxs::<T>::put(new_total);

if new_total > 0 {
    let old_avg = SealevelAvgComputeUnits::<T>::get();

    // Weighted incremental average:
    //   new_avg = (old_avg * previous_total + compute_units * tx_count) / new_total
    // Use u128 to avoid overflow before dividing back to u64.
    let numerator = (old_avg as u128)
        .saturating_mul(previous_total as u128)
        .saturating_add((compute_units as u128).saturating_mul(tx_count_u64 as u128));

    let new_avg = (numerator / new_total as u128) as u64;
    SealevelAvgComputeUnits::<T>::put(new_avg);
}
```

---

## HIGH Findings

### HIGH-1: Missing Authorization on `report_execution` and `report_conflict`

**Location:** `report_execution`, `report_conflict`

**Description:** Any signed account can call `report_execution` with an arbitrary `batch_id` and `compute_units`, or call `report_conflict` for any batch. There is no check that the caller owns or submitted the batch. This allows:
- Griefing: inflating `SealevelTotalTxs`, corrupting the average.
- Denial-of-service: spamming conflict events, inflating `SealevelConflicts`.
- Stat manipulation: any user can mark their batch as parallel and report 0 conflicts.

**Before:**
```rust
pub fn report_execution(
    origin: OriginFor<T>,
    batch_id: u32,
    compute_units: u64,
    tx_count: u32,
) -> DispatchResult {
    let _ = ensure_signed(origin)?;
    // no further authorization
```

**After:**
```rust
// Add to storage: track who created each batch
#[pallet::storage]
pub type BatchOwner<T: Config> =
    StorageMap<_, Twox64Concat, u32, T::AccountId, OptionQuery>;

// In create_batch, after let batch_id = ...:
BatchOwner::<T>::insert(batch_id, &who); // `who` from ensure_signed

// In report_execution:
pub fn report_execution(
    origin: OriginFor<T>,
    batch_id: u32,
    compute_units: u64,
    tx_count: u32,
) -> DispatchResult {
    let who = ensure_signed(origin)?;
    let owner = BatchOwner::<T>::get(batch_id).ok_or(Error::<T>::BatchNotFound)?;
    ensure!(who == owner, Error::<T>::NotBatchOwner);
    // ... rest of logic

// In report_conflict:
pub fn report_conflict(
    origin: OriginFor<T>,
    batch_id: u32,
    tx1: u32,
    tx2: u32,
) -> DispatchResult {
    let who = ensure_signed(origin)?;
    let owner = BatchOwner::<T>::get(batch_id).ok_or(Error::<T>::BatchNotFound)?;
    ensure!(who == owner, Error::<T>::NotBatchOwner);
    // ... rest of logic
```

---

### HIGH-2: `BatchNotFound` Error is Dead Code — No Existence Check on `report_execution`

**Location:** `report_execution`

**Description:** `BatchParallel` uses `ValueQuery` with a default of `false`. If a caller supplies a non-existent `batch_id`, the pallet silently treats it as a sequential batch and records fake compute units. The `BatchNotFound` error variant is defined but **never returned**, making it impossible to detect invalid batch IDs.

**Before:**
```rust
let parallel = BatchParallel::<T>::get(batch_id);
BatchComputeUnits::<T>::insert(batch_id, compute_units);
```

**After:**
```rust
// Change BatchParallel storage to OptionQuery so absence is detectable:
#[pallet::storage]
pub type BatchParallel<T> = StorageMap<_, Twox64Concat, u32, bool, OptionQuery>;

// Then in report_execution:
let parallel = BatchParallel::<T>::get(batch_id)
    .ok_or(Error::<T>::BatchNotFound)?;
BatchComputeUnits::<T>::insert(batch_id, compute_units);
```

---

### HIGH-3: `NextBatchId` Overflow — Wraps and Overwrites Existing Batches

**Location:** `create_batch`

**Description:** `NextBatchId` is a `u32` incremented with `*b += 1` (plain Rust addition). In release builds this wraps to 0 and new batches silently overwrite old ones in `BatchParallel` and `BatchComputeUnits`. After `u32::MAX` (≈4 billion) calls, previously executed batches are corrupted.

**Before:**
```rust
let batch_id = NextBatchId::<T>::get();
NextBatchId::<T>::mutate(|b| *b += 1);
```

**After:**
```rust
let batch_id = NextBatchId::<T>::get();
let next = batch_id.checked_add(1).ok_or(Error::<T>::BatchIdOverflow)?;
NextBatchId::<T>::put(next);
```
```rust
// Add to Error enum:
BatchIdOverflow,
```

---

## MEDIUM Findings

### MEDIUM-1: Storage Leak — Batch Entries Are Never Cleaned Up

**Location:** `create_batch`, `report_execution` (no corresponding cleanup)

**Description:** `BatchParallel`, `BatchComputeUnits`, and (with the fix above) `BatchOwner` grow forever. There is no `finalize_batch` or `remove_batch` extrinsic. Over time this constitutes an unbounded state growth vector that can bloat the trie and slow down state proofs.

**Before:**
```rust
// No cleanup anywhere
BatchParallel::<T>::insert(batch_id, parallel);
BatchComputeUnits::<T>::insert(batch_id, compute_units);
```

**After:**
```rust
// Add a finalize_batch extrinsic called by the owner after execution:
#[pallet::weight(0)]
#[pallet::call_index(3)]
pub fn finalize_batch(origin: OriginFor<T>, batch_id: u32) -> DispatchResult {
    let who = ensure_signed(origin)?;
    let owner = BatchOwner::<T>::get(batch_id).ok_or(Error::<T>::BatchNotFound)?;
    ensure!(who == owner, Error::<T>::NotBatchOwner);

    BatchParallel::<T>::remove(batch_id);
    BatchComputeUnits::<T>::remove(batch_id);
    BatchOwner::<T>::remove(batch_id);
    Ok(())
}
```

---

### MEDIUM-2: `report_execution` Can Be Called Multiple Times for the Same Batch

**Location:** `report_execution`

**Description:** Nothing prevents calling `report_execution` twice for the same `batch_id`. Each call re-inserts `compute_units` (overwriting the previous value is harmless) but **also increments `SealevelTotalTxs` again**, corrupting the global counters and the average permanently.

**Before:**
```rust
// No guard against duplicate execution reports
BatchComputeUnits::<T>::insert(batch_id, compute_units);
SealevelTotalTxs::<T>::mutate(|t| *t += tx_count as u64);
```

**After:**
```rust
// Add executed flag storage:
#[pallet::storage]
pub type BatchExecutedFlag<T> = StorageMap<_, Twox64Concat, u32, bool, ValueQuery>;

// At the start of report_execution (after ownership check):
ensure!(
    !BatchExecutedFlag::<T>::get(batch_id),
    Error::<T>::BatchAlreadyExecuted
);
BatchExecutedFlag::<T>::insert(batch_id, true);
// ... proceed with mutating global counters
```

---

### MEDIUM-3: `SealevelParallelBatches` Cast Truncation in Rate Calculation

**Location:** `create_batch`

**Description:** `parallel_count` is `u64` but is multiplied as `u64` then divided, and the result cast to `u32`. Since `parallel_count * 100 / total` is always in `[0, 100]` the truncation does not corrupt the value here, but the intermediate product `parallel_count * 100` can overflow `u64` at ~1.84 × 10¹⁷ parallel batches. Covered partially by CRITICAL-1, called out separately because the type mismatch itself is a design smell.

**Before:**
```rust
SealevelParallelizationRate::<T>::put((parallel_count * 100 / total) as u32);
```

**After:** *(See CRITICAL-1 fix — use `saturating_mul` and `u128` intermediate)*

---

## LOW Findings

### LOW-1: Suppressed Clippy Lints Hide Real Bugs

**Location:** Top of file

**Description:** `#![allow(clippy::all)]` disables all Clippy lints globally. Several of the bugs above (integer arithmetic, cast truncation) would have been caught by `clippy::integer_arithmetic` and `clippy::cast_possible_truncation`.

**Before:**
```rust
#![allow(deprecated)]
#![allow(clippy::all)]
```

**After:**
```rust
#![allow(deprecated)]
// Remove the blanket allow; add targeted exceptions if truly needed:
// #![allow(clippy::specific_lint_name)]
```

---

### LOW-2: Weights Are All Zero — Enables DoS via Free Extrinsics

**Location:** All extrinsics

**Description:** `#[pallet::weight(0)]` on every extrinsic means an attacker can spam all three calls at zero cost, filling blocks with storage writes and counter mutations.

**Before:**
```rust
#[pallet::weight(0)]
pub fn create_batch(...
```

**After:**
```rust
// Benchmark and assign real weights. Minimal example using a constant:
#[pallet::weight(T::DbWeight::get().reads_writes(3, 4))]
pub fn create_batch(...
```

---

## Fix Priority Checklist

```
[CRITICAL] Use saturating_mul + u128 for parallelization rate        → create_batch
[CRITICAL] Fix average formula with u128, correct ordering           → report_execution
[HIGH]     Add BatchOwner storage + ownership checks                  → all extrinsics
[HIGH]     Switch BatchParallel to OptionQuery + return BatchNotFound → report_execution
[HIGH]     Use checked_add for NextBatchId                           → create_batch
[MEDIUM]   Add finalize_batch for storage cleanup                     → new extrinsic
[MEDIUM]   Guard against duplicate report_execution calls            → report_execution
[LOW]      Remove #![allow(clippy::all)]                             → crate root
[LOW]      Assign real benchmark weights                              → all extrinsics
```