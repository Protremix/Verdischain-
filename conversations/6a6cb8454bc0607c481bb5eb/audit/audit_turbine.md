# Substrate Pallet Security Review

## Summary Table

| # | Severity | Location | Issue |
|---|----------|----------|-------|
| 1 | CRITICAL | `rebuild_tree` | Missing root/sudo origin check — any signed account can overwrite tree state |
| 2 | CRITICAL | `calc_depth` | Integer overflow in `n *= fanout` with no saturation/checked arithmetic |
| 3 | HIGH | `register_shard` | Missing root/sudo origin check — any account can register shards |
| 4 | HIGH | `mark_block_propagated` | Missing root/sudo origin check + no validation that block exists |
| 5 | HIGH | `TurbineTotalShards` / `TurbineTotalBlocks` | Arithmetic overflow on `+= 1` (u64 wraps in release mode without `checked`) |
| 6 | HIGH | `BlockShardCount` | Arithmetic overflow on `*c += 1` (u32) |
| 7 | HIGH | `register_shard` | `shard_index` is accepted but never validated against `total_shards` |
| 8 | MEDIUM | `mark_block_propagated` | `BlockShardCount` entry is never removed — permanent storage leak |
| 9 | MEDIUM | `calc_depth` | Infinite loop when `fanout == 1` and `count > 1` |
| 10 | LOW | All calls | `#[pallet::weight(0)]` — zero weight enables free DoS spam |

---

## Finding 1 — CRITICAL: `rebuild_tree` has no privileged origin check

**Description:** Any externally-owned account can call `rebuild_tree` and freely overwrite `TurbineTreeDepth` and `TurbineValidatorCount`, completely disrupting the propagation tree that all validators depend on.

```rust
// BEFORE
pub fn rebuild_tree(origin: OriginFor<T>, validator_count: u32) -> DispatchResult {
    let _ = ensure_signed(origin)?;
    ...
}

// AFTER
pub fn rebuild_tree(origin: OriginFor<T>, validator_count: u32) -> DispatchResult {
    ensure_root(origin)?;   // only sudo / governance can rebuild the tree
    ...
}
```

---

## Finding 2 — CRITICAL: Integer overflow in `calc_depth`

**Description:** `n *= fanout` uses wrapping multiplication in release builds. When `fanout` is large (e.g. `u32::MAX`) or iterates several times, `n` silently wraps to a small value, causing the loop to run far longer than intended (or forever), panicking or exhausting block weight.

```rust
// BEFORE
fn calc_depth(count: u32, fanout: u32) -> u32 {
    if fanout == 0 {
        return 1;
    }
    let mut d = 1;
    let mut n = fanout;
    while n < count {
        n *= fanout;   // <-- wrapping overflow in release mode
        d += 1;
    }
    d
}

// AFTER
fn calc_depth(count: u32, fanout: u32) -> u32 {
    if fanout <= 1 {
        // fanout == 0: degenerate tree, depth 1
        // fanout == 1: would loop forever; treat as linear, depth == count
        return count.max(1);
    }
    let mut d = 1u32;
    let mut n = fanout;
    while n < count {
        // If multiplication would overflow we have already enough levels
        // to cover any realistic validator set; cap and return.
        n = match n.checked_mul(fanout) {
            Some(v) => v,
            None => return d + 1,
        };
        d = d.checked_add(1).unwrap_or(u32::MAX);
    }
    d
}
```

---

## Finding 3 — HIGH: `register_shard` has no privileged origin check

**Description:** Any signed account can spam `register_shard` with arbitrary `block_number` values, inflating `TurbineTotalShards` and polluting `BlockShardCount` storage without limit.

```rust
// BEFORE
pub fn register_shard(
    origin: OriginFor<T>,
    block_number: u32,
    shard_index: u32,
    total_shards: u32,
) -> DispatchResult {
    let _ = ensure_signed(origin)?;
    ...
}

// AFTER
pub fn register_shard(
    origin: OriginFor<T>,
    block_number: u32,
    shard_index: u32,
    total_shards: u32,
) -> DispatchResult {
    ensure_root(origin)?;
    ...
}
```

---

## Finding 4 — HIGH: `mark_block_propagated` has no privileged origin check and no existence check

**Description:** Any account can increment `TurbineTotalBlocks` and emit events for blocks that were never sharded, corrupting accounting and potentially front-running legitimate propagation records.

```rust
// BEFORE
pub fn mark_block_propagated(origin: OriginFor<T>, block_number: u32) -> DispatchResult {
    let _ = ensure_signed(origin)?;
    TurbineTotalBlocks::<T>::mutate(|b| *b += 1);
    let sc = BlockShardCount::<T>::get(block_number);
    Self::deposit_event(Event::BlockSharded {
        block_number,
        shard_count: sc,
    });
    Ok(())
}

// AFTER
pub fn mark_block_propagated(origin: OriginFor<T>, block_number: u32) -> DispatchResult {
    ensure_root(origin)?;

    // Block must have at least one registered shard before it can be marked propagated.
    ensure!(
        BlockShardCount::<T>::contains_key(block_number),
        Error::<T>::InvalidShardIndex   // or add a dedicated BlockNotFound error
    );

    TurbineTotalBlocks::<T>::mutate(|b| {
        *b = b.checked_add(1).unwrap_or(u64::MAX)
    });

    let sc = BlockShardCount::<T>::get(block_number);

    // Clean up shard count for this block now that propagation is complete.
    BlockShardCount::<T>::remove(block_number);

    Self::deposit_event(Event::BlockSharded {
        block_number,
        shard_count: sc,
    });
    Ok(())
}
```

---

## Finding 5 — HIGH: Overflow on `TurbineTotalShards` and `TurbineTotalBlocks` counters

**Description:** Both `u64` counters use `*s += 1` / `*b += 1`, which wraps in release mode, silently resetting the counter to zero and corrupting global state.

```rust
// BEFORE — register_shard
TurbineTotalShards::<T>::mutate(|s| *s += 1);

// AFTER — register_shard
TurbineTotalShards::<T>::mutate(|s| {
    *s = s.checked_add(1).expect("TurbineTotalShards overflow; this is a critical bug")
    // OR use saturating_add if silent saturation is acceptable:
    // *s = s.saturating_add(1);
});

// BEFORE — mark_block_propagated
TurbineTotalBlocks::<T>::mutate(|b| *b += 1);

// AFTER — mark_block_propagated
TurbineTotalBlocks::<T>::mutate(|b| {
    *b = b.saturating_add(1);
});
```

---

## Finding 6 — HIGH: Overflow on `BlockShardCount` counter

**Description:** `*c += 1` on a `u32` wraps on overflow; an attacker (or bug) submitting 2³²+ shards for one block resets the count to zero.

```rust
// BEFORE
BlockShardCount::<T>::mutate(block_number, |c| *c += 1);

// AFTER
BlockShardCount::<T>::mutate(block_number, |c| {
    *c = c.saturating_add(1);
});
```

---

## Finding 7 — HIGH: `shard_index` is never validated against `total_shards`

**Description:** The call accepts `shard_index` but never checks `shard_index < total_shards`. An attacker can pass `shard_index = u32::MAX` with `total_shards = 1`, bypassing any intended range constraint.

```rust
// BEFORE
ensure!(
    total_shards <= T::MaxShards::get(),
    Error::<T>::MaxShardsExceeded
);
// shard_index is silently ignored

// AFTER
ensure!(
    total_shards <= T::MaxShards::get(),
    Error::<T>::MaxShardsExceeded
);
ensure!(
    shard_index < total_shards,
    Error::<T>::InvalidShardIndex
);
```

---

## Finding 8 — MEDIUM: `BlockShardCount` entries are never cleaned up (storage leak)

**Description:** Every unique `block_number` passed to `register_shard` creates a permanent `BlockShardCount` entry. Over time this grows unboundedly, increasing state proof sizes and trie traversal cost.

*Fix is incorporated in Finding 4's `mark_block_propagated` after-snippet:*

```rust
// After emitting the event, remove the now-stale entry:
BlockShardCount::<T>::remove(block_number);
```

---

## Finding 9 — MEDIUM: Infinite loop in `calc_depth` when `fanout == 1`

**Description:** When `fanout == 1`, the loop condition `n < count` is always true (n stays at 1), causing `calc_depth` to loop forever, which panics the node or exhausts block weight.

*Fixed as part of Finding 2's after-snippet by the `if fanout <= 1` early return.*

---

## Finding 10 — LOW: All extrinsics use `#[pallet::weight(0)]`

**Description:** Zero-weight extrinsics bypass the economic spam-prevention mechanism. A network attacker can flood the block with free calls, starving legitimate transactions.

```rust
// BEFORE
#[pallet::weight(0)]
pub fn register_shard(...) -> DispatchResult { ... }

// AFTER — replace with a concrete benchmark-derived weight
#[pallet::weight(T::DbWeight::get().reads_writes(1, 2)
    .saturating_add(Weight::from_parts(10_000_000, 0)))]
pub fn register_shard(...) -> DispatchResult { ... }
// Repeat analogously for rebuild_tree and mark_block_propagated.
// Ideally use pallet_benchmarking to derive accurate weights.
```