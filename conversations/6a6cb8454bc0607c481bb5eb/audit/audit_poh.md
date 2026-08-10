# Substrate Pallet Code Review: Verdis Proof of History (PoH)

---

## Finding 1: Any Signed User Can Advance the Hash Chain

**Severity:** CRITICAL
**Location:** `record_block`, `tick_extrinsic`

**Description:**
Both `record_block` and `tick_extrinsic` use `ensure_signed_or_root`, meaning **any authenticated user** can advance the PoH hash chain and overwrite block stamps. This breaks the core security guarantee of PoH — the chain should only advance under controlled, deterministic conditions (e.g., via `on_initialize` hooks or privileged calls). A malicious actor can:
- Spam ticks to desynchronize the chain
- Overwrite an existing block's stamp by calling `record_block` again (no idempotency check)
- Grief by filling storage with arbitrary block stamps

**Before:**
```rust
pub fn record_block(origin: OriginFor<T>) -> DispatchResult {
    let _who = ensure_signed_or_root(origin)?;
    let block_number = <frame_system::Pallet<T>>::block_number();
    let hash = Self::tick();
    <PohHashes<T>>::insert(block_number, hash);
    Self::deposit_event(Event::BlockStamped { block_number, hash });
    Ok(())
}

pub fn tick_extrinsic(origin: OriginFor<T>) -> DispatchResult {
    let _who = ensure_signed_or_root(origin)?;
    Self::tick();
    Ok(())
}
```

**After:**
```rust
pub fn record_block(origin: OriginFor<T>) -> DispatchResult {
    ensure_root(origin)?;
    let block_number = <frame_system::Pallet<T>>::block_number();
    // Prevent overwriting an already-stamped block
    ensure!(
        !<PohHashes<T>>::contains_key(block_number),
        Error::<T>::BlockAlreadyStamped
    );
    let hash = Self::tick();
    <PohHashes<T>>::insert(block_number, hash);
    Self::deposit_event(Event::BlockStamped { block_number, hash });
    Ok(())
}

pub fn tick_extrinsic(origin: OriginFor<T>) -> DispatchResult {
    ensure_root(origin)?;
    Self::tick();
    Ok(())
}
```

Also add the new error variant:
```rust
#[pallet::error]
pub enum Error<T> {
    BlockHashNotFound,
    InvalidBlockRange,
    /// Block has already been stamped with a PoH hash
    BlockAlreadyStamped,
}
```

---

## Finding 2: Unbounded Storage Growth with No Cleanup

**Severity:** HIGH
**Location:** `record_block`, `PohHashes` storage map

**Description:**
`PohHashes` maps every block number to a hash with no eviction, pruning, or size bound. Over time this grows indefinitely. There is no `max_blocks` config, no `remove_old_entries` hook, and no weight that accounts for storage growth. This is a classic storage exhaustion vector and violates Substrate best practices for bounded storage.

**Before:**
```rust
/// Map of block_number -> PoH hash
#[pallet::storage]
#[pallet::getter(fn poh_hashes)]
pub type PohHashes<T: Config> =
    StorageMap<_, Blake2_128Concat, BlockNumberFor<T>, [u8; 32], OptionQuery>;
```

**After:**
```rust
#[pallet::config]
pub trait Config: frame_system::Config {
    /// How many historical PoH hashes to retain on-chain.
    #[pallet::constant]
    type MaxStoredHashes: Get<u32>;
}

/// Ordered queue of block numbers for which hashes are stored, for bounded pruning.
#[pallet::storage]
pub type PohHashKeys<T: Config> = StorageValue<
    _,
    BoundedVec<BlockNumberFor<T>, T::MaxStoredHashes>,
    ValueQuery,
>;

/// Map of block_number -> PoH hash (pruned to MaxStoredHashes entries)
#[pallet::storage]
#[pallet::getter(fn poh_hashes)]
pub type PohHashes<T: Config> =
    StorageMap<_, Blake2_128Concat, BlockNumberFor<T>, [u8; 32], OptionQuery>;
```

And update `record_block` to prune old entries:
```rust
pub fn record_block(origin: OriginFor<T>) -> DispatchResult {
    ensure_root(origin)?;
    let block_number = <frame_system::Pallet<T>>::block_number();
    ensure!(
        !<PohHashes<T>>::contains_key(block_number),
        Error::<T>::BlockAlreadyStamped
    );
    let hash = Self::tick();
    <PohHashes<T>>::insert(block_number, hash);

    PohHashKeys::<T>::mutate(|keys| {
        // If at capacity, evict the oldest entry
        if keys.len() as u32 >= T::MaxStoredHashes::get() {
            let oldest = keys.remove(0);
            <PohHashes<T>>::remove(oldest);
        }
        // Safe: we just made room if needed
        keys.try_push(block_number)
            .expect("capacity enforced above; qed")
    });

    Self::deposit_event(Event::BlockStamped { block_number, hash });
    Ok(())
}
```

---

## Finding 3: Duplicate State — `PohTick` and `PohConfigVal::tick_count` Are Redundant and Can Diverge

**Severity:** HIGH
**Location:** `tick`, `set_config`

**Description:**
The pallet maintains tick count in **two separate storage locations**: `PohTick<T>` and `PohConfigVal::tick_count`. In `tick()`, both are updated, but `set_config` reads `PohTick` and writes to `PohConfigVal` independently. Any path that updates one without the other creates a **permanent state inconsistency**. This also means `calculate_hash` could silently use a stale tick count if `PohConfigVal` and `PohTick` diverge.

**Before:**
```rust
pub fn tick() -> [u8; 32] {
    let mut config = PohConfigVal::<T>::get();
    config.tick_count = config.tick_count.saturating_add(1);
    let new_hash = Self::calculate_hash(&config.last_hash, &config.seed, config.tick_count);
    config.last_hash = new_hash;

    PohTick::<T>::put(config.tick_count);  // duplicate write
    PohConfigVal::<T>::put(&config);
    // ...
}

pub fn set_config(...) -> DispatchResult {
    ensure_root(origin)?;
    let current_tick = PohTick::<T>::get();  // reads from separate store
    let new_config = PoHConfig {
        seed,
        last_hash,
        tick_count: current_tick,
    };
    PohConfigVal::<T>::put(new_config);
    // PohTick is NOT updated here — divergence possible
    Ok(())
}
```

**After:**
Remove `PohTick` entirely. Use `PohConfigVal` as the single source of truth:

```rust
// REMOVE this storage item entirely:
// pub type PohTick<T: Config> = StorageValue<_, u64, ValueQuery>;

pub fn tick() -> [u8; 32] {
    let mut config = PohConfigVal::<T>::get();
    config.tick_count = config.tick_count.saturating_add(1);
    let new_hash = Self::calculate_hash(&config.last_hash, &config.seed, config.tick_count);
    config.last_hash = new_hash;
    PohConfigVal::<T>::put(&config);

    Self::deposit_event(Event::TickGenerated {
        tick_count: config.tick_count,
        hash: new_hash,
    });

    new_hash
}

pub fn set_config(
    origin: OriginFor<T>,
    seed: [u8; 32],
    last_hash: [u8; 32],
) -> DispatchResult {
    ensure_root(origin)?;
    // Preserve tick_count from canonical source
    let current_tick = PohConfigVal::<T>::get().tick_count;
    let new_config = PoHConfig {
        seed,
        last_hash,
        tick_count: current_tick,
    };
    PohConfigVal::<T>::put(new_config);
    Self::deposit_event(Event::ConfigUpdated { seed, last_hash });
    Ok(())
}
```

---

## Finding 4: `verify_poh` Can Loop Indefinitely on Large Ranges

**Severity:** HIGH
**Location:** `verify_poh`

**Description:**
`verify_poh` iterates from `start_block` to `end_block` with no upper bound on range size. A caller can pass `start_block = 0, end_block = u32::MAX` causing the node to exhaust execution budget or hang. There is no weight charged for this function either. Even if called internally, any extrinsic wiring it would be exploitable.

**Before:**
```rust
pub fn verify_poh(start_block: BlockNumberFor<T>, end_block: BlockNumberFor<T>) -> bool {
    if start_block > end_block {
        return false;
    }
    let mut current = start_block;
    while current <= end_block {
        if !<PohHashes<T>>::contains_key(current) {
            return false;
        }
        if current == end_block {
            break;
        }
        current = current.saturating_add(1u32.into());
    }
    true
}
```

**After:**
```rust
/// Maximum number of blocks that can be verified in a single call.
const MAX_VERIFY_RANGE: u32 = 1_000;

pub fn verify_poh(
    start_block: BlockNumberFor<T>,
    end_block: BlockNumberFor<T>,
) -> Result<bool, Error<T>> {
    if start_block > end_block {
        return Err(Error::<T>::InvalidBlockRange);
    }

    // Enforce bounded iteration
    let range_size = end_block
        .saturating_sub(start_block)
        .saturated_into::<u32>()
        .saturating_add(1u32);

    ensure!(
        range_size <= MAX_VERIFY_RANGE,
        Error::<T>::InvalidBlockRange
    );

    let mut current = start_block;
    loop {
        if !<PohHashes<T>>::contains_key(current) {
            return Ok(false);
        }
        if current == end_block {
            break;
        }
        current = current.saturating_add(One::one());
    }
    Ok(true)
}
```

---

## Finding 5: `set_config` Allows Root to Silently Rewrite Hash Chain History

**Severity:** HIGH
**Location:** `set_config`

**Description:**
Root can call `set_config` with an arbitrary `last_hash` and `seed` at any time, **silently breaking the integrity of all future PoH hashes** without any on-chain record of the chain discontinuity. All historical hashes stored in `PohHashes` become unverifiable against the new chain. There is no event field indicating the old values, and no mechanism to detect or dispute a chain reset.

**Before:**
```rust
pub fn set_config(
    origin: OriginFor<T>,
    seed: [u8; 32],
    last_hash: [u8; 32],
) -> DispatchResult {
    ensure_root(origin)?;
    let current_tick = PohTick::<T>::get();
    let new_config = PoHConfig {
        seed,
        last_hash,
        tick_count: current_tick,
    };
    PohConfigVal::<T>::put(new_config);
    Self::deposit_event(Event::ConfigUpdated { seed, last_hash });
    Ok(())
}
```

**After:**
```rust
pub fn set_config(
    origin: OriginFor<T>,
    seed: [u8; 32],
    last_hash: [u8; 32],
) -> DispatchResult {
    ensure_root(origin)?;
    let old_config = PohConfigVal::<T>::get();
    let new_config = PoHConfig {
        seed,
        last_hash,
        tick_count: old_config.tick_count, // preserve tick count
    };
    PohConfigVal::<T>::put(new_config);

    // Emit old values so off-chain observers can detect chain resets
    Self::deposit_event(Event::ConfigUpdated {
        old_seed: old_config.seed,
        old_last_hash: old_config.last_hash,
        new_seed: seed,
        new_last_hash: last_hash,
        at_tick: old_config.tick_count,
    });
    Ok(())
}
```

Update the event definition:
```rust
pub enum Event<T: Config> {
    TickGenerated { tick_count: u64, hash: [u8; 32] },
    BlockStamped {
        block_number: BlockNumberFor<T>,
        hash: [u8; 32],
    },
    /// PoH configuration was reset by root
    ConfigUpdated {
        old_seed: [u8; 32],
        old_last_hash: [u8; 32],
        new_seed: [u8; 32],
        new_last_hash: [u8; 32],
        at_tick: u64,
    },
}
```

---

## Finding 6: Zero Weights on All Extrinsics

**Severity:** HIGH
**Location:** `record_block`, `set_config`, `tick_extrinsic`

**Description:**
All three extrinsics declare `#[pallet::weight(0)]`. This means they cost nothing to execute, making **DoS attacks free**. An attacker can spam `tick_extrinsic` or `record_block` with zero fee, exhausting block capacity and storage. Weights must reflect actual computational and storage costs measured via benchmarks.

**Before:**
```rust
#[pallet::weight(0)]
pub fn record_block(origin: OriginFor<T>) -> DispatchResult { ... }

#[pallet::weight(0)]
pub fn set_config(...) -> DispatchResult { ... }

#[pallet::weight(0)]
pub fn tick_extrinsic(origin: OriginFor<T>) -> DispatchResult { ... }
```

**After:**
```rust
// Step 1: Define a WeightInfo trait
pub trait WeightInfo {
    fn record_block() -> Weight;
    fn set_config() -> Weight;
    fn tick_extrinsic() -> Weight;
}

// Step 2: Add to Config
pub trait Config: frame_system::Config {
    type WeightInfo: WeightInfo;
    // ...
}

// Step 3: Use measured weights
#[pallet::weight(T::WeightInfo::record_block())]
pub fn record_block(origin: OriginFor<T>) -> DispatchResult { ... }

#[pallet::weight(T::WeightInfo::set_config())]
pub fn set_config(...) -> DispatchResult { ... }

#[pallet::weight(T::WeightInfo::tick_extrinsic())]
pub fn tick_extrinsic(origin: OriginFor<T>) -> DispatchResult { ... }
```

---

## Finding 7: SHA-256 Hash Input Is Not Domain-Separated

**Severity:** MEDIUM
**Location:** `calculate_hash`

**Description:**
The hash inputs `last_hash || seed || tick_count` are concatenated without length prefixes or domain separators. Because `last_hash` and `seed` are both fixed 32 bytes this is not immediately exploitable for collision, but `tick_count` as a raw `u64` appended without a separator means the encoding is ambiguous across future protocol changes. A proper commitment scheme requires domain separation.

**Before:**
```rust
pub fn calculate_hash(last_hash: &[u8; 32], seed: &[u8; 32], tick_count: u64) -> [u8; 32] {
    use sha2::{Digest, Sha256};
    let mut hasher = Sha256::new();
    hasher.update(last_hash);
    hasher.update(seed);
    hasher.update(&tick_count.to_be_bytes());
    let result = hasher.finalize();
    let mut hash = [0u8; 32];
    hash.copy_from_slice(&result);
    hash
}
```

**After:**
```rust
/// Domain separation tag for PoH hash chain
const POH_DOMAIN_TAG: &[u8] = b"verdis-poh-v1";

pub fn calculate_hash(last_hash: &[u8; 32], seed: &[u8; 32], tick_count: u64) -> [u8; 32] {
    use sha2::{Digest, Sha256};
    let mut hasher = Sha256::new();
    // Domain separation prevents cross-context hash collisions
    hasher.update(POH_DOMAIN_TAG);
    hasher.update(b"|");
    hasher.update(last_hash);
    hasher.update(b"|");
    hasher.update(seed);
    hasher.update(b"|");
    hasher.update(&tick_count.to_be_bytes());
    let result = hasher.finalize();
    let mut hash = [0u8; 32];
    hash.copy_from_slice(&result);
    hash
}
```

---

## Finding 8: `#[allow(deprecated)]` and `#[allow(clippy::all)]` Suppress Safety Warnings

**Severity:** LOW
**Location:** Top of file

**Description:**
`#[allow(deprecated)]` indicates use of deprecated APIs that may have known issues. `#[allow(clippy::all)]` disables all Clippy lints, including lints that catch integer overflow, panicking code paths, and unsafe patterns. These should never appear in production blockchain code.

**Before:**
```rust
#![allow(deprecated)]
#![allow(clippy::all)]
```

**After:**
```rust
// Remove both attributes entirely.
// If specific Clippy lints need suppression for legitimate reasons,
// use targeted, documented suppressions at the specific call site:
// #[allow(clippy::specific_lint_name)] // reason: ...
```

---

## Summary Table

| # | Severity | Location | Issue |
|---|----------|----------|-------|
| 1 | CRITICAL | `record_block`, `tick_extrinsic` | Any signed user can advance/overwrite hash chain |
| 2 | HIGH | `record_block`, `PohHashes` | Unbounded storage growth, no pruning |
| 3 | HIGH | `tick`, `set_config` | Dual tick state can diverge, state inconsistency |
| 4 | HIGH | `verify_poh` | Unbounded loop, no range limit, DoS vector |
| 5 | HIGH | `set_config` | Root can silently rewrite chain history |
| 6 | HIGH | All extrinsics | Zero weights enable free DoS |
| 7 | MEDIUM | `calculate_hash` | Missing domain separation in hash input |
| 8 | LOW | File header | Suppressed deprecation and Clippy warnings |