# Substrate Pallet Security Review

## Summary

This pallet manages address lookup tables with critical authorization, arithmetic, and logic vulnerabilities. I found **5 CRITICAL**, **2 HIGH**, and **2 MEDIUM** severity issues.

---

## CRITICAL-1: Missing Table Existence Check in `deactivate_table`

**Severity:** CRITICAL
**Location:** `deactivate_table`

**Description:** Any signed user can deactivate **any** table — including tables they don't own. There is no ownership tracking and no existence check. An attacker can deactivate all tables in the system, causing permanent denial of service.

**Before:**
```rust
pub fn deactivate_table(origin: OriginFor<T>, table_id: u32) -> DispatchResult {
    ensure_signed(origin)?;
    TableActive::<T>::insert(table_id, false);
    Self::deposit_event(Event::TableDeactivated { table_id });
    Ok(())
}
```

**After:**
```rust
// 1. Add ownership storage
#[pallet::storage]
pub type TableOwner<T: Config> = StorageMap<_, Twox64Concat, u32, T::AccountId>;

// 2. Fix create_table to record ownership
pub fn create_table(origin: OriginFor<T>) -> DispatchResult {
    let who = ensure_signed(origin)?;
    let table_id = AltTotalTables::<T>::get() as u32;
    let root = sp_io::hashing::blake2_256(&who.encode());
    TableIds::<T>::insert(table_id, root);
    TableActive::<T>::insert(table_id, true);
    TableOwner::<T>::insert(table_id, who.clone()); // NEW
    AltTotalTables::<T>::mutate(|t| *t += 1);
    Self::deposit_event(Event::TableCreated { table_id, root });
    Ok(())
}

// 3. Fix deactivate_table with ownership + existence check
pub fn deactivate_table(origin: OriginFor<T>, table_id: u32) -> DispatchResult {
    let who = ensure_signed(origin)?;
    let owner = TableOwner::<T>::get(table_id).ok_or(Error::<T>::TableNotFound)?;
    ensure!(owner == who, Error::<T>::NotTableOwner);
    ensure!(TableActive::<T>::get(table_id), Error::<T>::TableNotActive);
    TableActive::<T>::insert(table_id, false);
    Self::deposit_event(Event::TableDeactivated { table_id });
    Ok(())
}
```

---

## CRITICAL-2: Missing Table Existence Check in `add_address`

**Severity:** CRITICAL
**Location:** `add_address`

**Description:** `TableActive` uses `ValueQuery` which returns `false` for non-existent tables. The `ensure!` correctly blocks adding to inactive tables BUT allows adding to a table_id that was never created if someone first calls `deactivate_table` (which sets it to `false` for non-existent IDs). More critically: the `TableActive` default is `false`, but the check is `ensure!(TableActive::get(table_id), TableNotActive)` — this happens to block non-existent tables accidentally, but there is **no explicit existence guard**. A non-existent table_id that is somehow set active (e.g. storage manipulation in tests/migrations) would silently corrupt state. The proper fix is an explicit existence check.

**Before:**
```rust
pub fn add_address(origin: OriginFor<T>, table_id: u32) -> DispatchResult {
    ensure_signed(origin)?;
    ensure!(TableActive::<T>::get(table_id), Error::<T>::TableNotActive);
    let count = TableAddressCount::<T>::get(table_id);
    // ...
}
```

**After:**
```rust
pub fn add_address(origin: OriginFor<T>, table_id: u32) -> DispatchResult {
    ensure_signed(origin)?;
    // Explicit existence check BEFORE active check
    ensure!(TableIds::<T>::contains_key(table_id), Error::<T>::TableNotFound);
    ensure!(TableActive::<T>::get(table_id), Error::<T>::TableNotActive);
    let count = TableAddressCount::<T>::get(table_id);
    ensure!(
        count < T::MaxAddressesPerTable::get(),
        Error::<T>::TableFull
    );
    TableAddressCount::<T>::mutate(table_id, |c| *c += 1);
    AltTotalAddresses::<T>::mutate(|a| *a += 1);
    AltBytesSaved::<T>::mutate(|b| *b += 30);
    Self::deposit_event(Event::AddressAdded {
        table_id,
        index: count,
    });
    Ok(())
}
```

---

## CRITICAL-3: Arithmetic Overflow on `table_id` Cast in `create_table`

**Severity:** CRITICAL
**Location:** `create_table`

**Description:** `AltTotalTables` is `u64` but is silently cast to `u32` for `table_id`. After 2³²−1 tables, the cast wraps/truncates and **overwrites existing table storage**, corrupting `TableIds`, `TableActive`, `TableOwner`, and `TableAddressCount` for those IDs. Additionally, `AltTotalTables` itself overflows at u64::MAX with no protection.

**Before:**
```rust
let table_id = AltTotalTables::<T>::get() as u32;
// ...
AltTotalTables::<T>::mutate(|t| *t += 1);
```

**After:**
```rust
// Change AltTotalTables to u32 to match table_id type
#[pallet::storage]
pub type AltTotalTables<T> = StorageValue<_, u32, ValueQuery>;

// In create_table:
let table_id = AltTotalTables::<T>::get();
let next_id = table_id.checked_add(1).ok_or(Error::<T>::TableIdOverflow)?;
let root = sp_io::hashing::blake2_256(&who.encode());
TableIds::<T>::insert(table_id, root);
TableActive::<T>::insert(table_id, true);
TableOwner::<T>::insert(table_id, who.clone());
AltTotalTables::<T>::put(next_id);
Self::deposit_event(Event::TableCreated { table_id, root });
Ok(())
```

---

## CRITICAL-4: `lookup_address` Performs No Validation

**Severity:** CRITICAL
**Location:** `lookup_address`

**Description:** The lookup function does **zero validation** — it doesn't check that `table_id` exists, that the table is active, or that `index` is within bounds. Anyone can call this with arbitrary inputs to:
1. Inflate `AltTotalLookups` and `AltBytesSaved` counters without limit (statistical manipulation / false reporting)
2. Emit fake `LookupPerformed` events that off-chain indexers may trust
3. The `AltBytesSaved` counter overflows silently with enough calls

**Before:**
```rust
pub fn lookup_address(origin: OriginFor<T>, table_id: u32, index: u32) -> DispatchResult {
    ensure_signed(origin)?;
    AltTotalLookups::<T>::mutate(|l| *l += 1);
    AltBytesSaved::<T>::mutate(|b| *b += 30);
    Self::deposit_event(Event::LookupPerformed {
        table_id,
        index,
        bytes_saved: 30,
    });
    Ok(())
}
```

**After:**
```rust
pub fn lookup_address(origin: OriginFor<T>, table_id: u32, index: u32) -> DispatchResult {
    ensure_signed(origin)?;
    // Validate table exists and is active
    ensure!(TableIds::<T>::contains_key(table_id), Error::<T>::TableNotFound);
    ensure!(TableActive::<T>::get(table_id), Error::<T>::TableNotActive);
    // Validate index is within the table's address count
    let count = TableAddressCount::<T>::get(table_id);
    ensure!(index < count, Error::<T>::IndexOutOfBounds);
    // Safe arithmetic for counters
    AltTotalLookups::<T>::mutate(|l| {
        *l = l.saturating_add(1);
    });
    AltBytesSaved::<T>::mutate(|b| {
        *b = b.saturating_add(30);
    });
    Self::deposit_event(Event::LookupPerformed {
        table_id,
        index,
        bytes_saved: 30,
    });
    Ok(())
}
```

---

## CRITICAL-5: All Global Counters Use Unchecked Arithmetic

**Severity:** CRITICAL
**Location:** `add_address`, `create_table`, `lookup_address`

**Description:** All `mutate` calls on `u64` counters use `*t += 1` / `*b += 30` which will **panic in debug mode** and **silently wrap in release mode** (Rust's `u64` wraps on overflow in release without `overflow-checks = true`). In a blockchain context this corrupts on-chain statistics permanently.

**Before:**
```rust
AltTotalTables::<T>::mutate(|t| *t += 1);
AltTotalAddresses::<T>::mutate(|a| *a += 1);
AltTotalLookups::<T>::mutate(|l| *l += 1);
AltBytesSaved::<T>::mutate(|b| *b += 30);
AltBytesSaved::<T>::mutate(|b| *b += 30);  // in add_address
```

**After:**
```rust
AltTotalTables::<T>::mutate(|t| *t = t.saturating_add(1));
AltTotalAddresses::<T>::mutate(|a| *a = a.saturating_add(1));
AltTotalLookups::<T>::mutate(|l| *l = l.saturating_add(1));
AltBytesSaved::<T>::mutate(|b| *b = b.saturating_add(30));
```

---

## HIGH-1: `TableAddressCount` Underflow Risk if Addresses Are Ever Removed

**Severity:** HIGH
**Location:** Future `remove_address` function / `TableAddressCount`

**Description:** `TableAddressCount` uses `ValueQuery` (default 0). If any future function decrements this counter without a `checked_sub` or `saturating_sub`, it will underflow and wrap to `u32::MAX`, bypassing `MaxAddressesPerTable` limits. Fix proactively:

**Before (current mutation pattern):**
```rust
TableAddressCount::<T>::mutate(table_id, |c| *c += 1);
```

**After (establish safe pattern for both directions):**
```rust
// Increment (add_address)
TableAddressCount::<T>::try_mutate(table_id, |c| -> DispatchResult {
    *c = c.checked_add(1).ok_or(Error::<T>::TableFull)?;
    Ok(())
})?;

// Decrement (any future remove function)
TableAddressCount::<T>::try_mutate(table_id, |c| -> DispatchResult {
    *c = c.checked_sub(1).ok_or(Error::<T>::Underflow)?;
    Ok(())
})?;
```

---

## HIGH-2: `MaxTablesPerAccount` Config Parameter is Declared but Never Enforced

**Severity:** HIGH
**Location:** `Config` trait, `create_table`

**Description:** `MaxTablesPerAccount: Get<u32>` exists in config but is **never checked anywhere**. Any account can create unlimited tables, making the parameter misleading and the intended DOS protection completely absent.

**Before:**
```rust
// In Config:
type MaxTablesPerAccount: Get<u32>;

// In create_table: (no check exists)
pub fn create_table(origin: OriginFor<T>) -> DispatchResult {
    let who = ensure_signed(origin)?;
    let table_id = AltTotalTables::<T>::get() as u32;
    // MaxTablesPerAccount is never used
```

**After:**
```rust
// Add per-account table count storage
#[pallet::storage]
pub type AccountTableCount<T: Config> = StorageMap<_, Blake2_128Concat, T::AccountId, u32, ValueQuery>;

// In create_table:
pub fn create_table(origin: OriginFor<T>) -> DispatchResult {
    let who = ensure_signed(origin)?;
    
    // Enforce MaxTablesPerAccount
    let account_table_count = AccountTableCount::<T>::get(&who);
    ensure!(
        account_table_count < T::MaxTablesPerAccount::get(),
        Error::<T>::MaxTablesExceeded
    );
    
    let table_id = AltTotalTables::<T>::get(); // now u32
    let next_id = table_id.checked_add(1).ok_or(Error::<T>::TableIdOverflow)?;
    let root = sp_io::hashing::blake2_256(&who.encode());
    
    TableIds::<T>::insert(table_id, root);
    TableActive::<T>::insert(table_id, true);
    TableOwner::<T>::insert(table_id, who.clone());
    AccountTableCount::<T>::mutate(&who, |c| *c = c.saturating_add(1));
    AltTotalTables::<T>::put(next_id);
    
    Self::deposit_event(Event::TableCreated { table_id, root });
    Ok(())
}
```

---

## MEDIUM-1: `TableIds` Root is Derived Only from Caller — Not Unique

**Severity:** MEDIUM
**Location:** `create_table`

**Description:** `blake2_256(&who.encode())` produces the **same root** for every table created by the same account. If the root is used off-chain to identify or verify tables, this is a collision. Use `table_id` in the hash input.

**Before:**
```rust
let root = sp_io::hashing::blake2_256(&who.encode());
```

**After:**
```rust
let root = sp_io::hashing::blake2_256(&(who.clone(), table_id).encode());
```

---

## MEDIUM-2: No Storage Cleanup on `deactivate_table`

**Severity:** MEDIUM
**Location:** `deactivate_table`

**Description:** Deactivating a table leaves all associated storage entries (`TableIds`, `TableAddressCount`, `TableOwner`, `AccountTableCount`) permanently in storage. This is a storage leak. At minimum, decrement `AccountTableCount` so the account can create new tables, and optionally remove the table entries.

**Before:**
```rust
pub fn deactivate_table(origin: OriginFor<T>, table_id: u32) -> DispatchResult {
    let who = ensure_signed(origin)?;
    // ... ownership check ...
    TableActive::<T>::insert(table_id, false);
    Self::deposit_event(Event::TableDeactivated { table_id });
    Ok(())
}
```

**After:**
```rust
pub fn deactivate_table(origin: OriginFor<T>, table_id: u32) -> DispatchResult {
    let who = ensure_signed(origin)?;
    let owner = TableOwner::<T>::get(table_id).ok_or(Error::<T>::TableNotFound)?;
    ensure!(owner == who, Error::<T>::NotTableOwner);
    ensure!(TableActive::<T>::get(table_id), Error::<T>::TableNotActive);
    
    // Clean up storage
    TableActive::<T>::insert(table_id, false);
    // Decrement account's table count to allow creating new tables
    AccountTableCount::<T>::mutate(&who, |c| *c = c.saturating_sub(1));
    // Optional: full cleanup (depends on whether historical data is needed)
    // TableIds::<T>::remove(table_id);
    // TableAddressCount::<T>::remove(table_id);
    // TableOwner::<T>::remove(table_id);
    
    Self::deposit_event(Event::TableDeactivated { table_id });
    Ok(())
}
```

---

## Complete Fixed Pallet

```rust
#![cfg_attr(not(feature = "std"), no_std)]
use frame_support::{dispatch::DispatchResult, pallet_prelude::*};
use frame_system::pallet_prelude::*;
pub use pallet::*;
use sp_std::prelude::*;

#[frame_support::pallet]
pub mod pallet {
    use super::*;

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    #[pallet::config]
    pub trait Config: frame_system::Config {
        type MaxAddressesPerTable: Get<u32>;
        type MaxTablesPerAccount: Get<u32>;
    }

    #[pallet::storage]
    pub type AltTotalTables<T> = StorageValue<_, u32, ValueQuery>; // FIX: u32 not u64

    #[pallet::storage]
    pub type AltTotalAddresses<T> = StorageValue<_, u64, ValueQuery>;

    #[pallet::storage]
    pub type AltTotalLookups<T> = StorageValue<_, u64, ValueQuery>;

    #[pallet::storage]
    pub type AltBytesSaved<T> = StorageValue<_, u64, ValueQuery>;

    #[pallet::storage]
    pub type TableIds<T> = StorageMap<_, Twox64Concat, u32, [u8; 32]>;

    #[pallet::storage]
    pub type TableAddressCount<T> = StorageMap<_, Twox64Concat, u32, u32, ValueQuery>;

    #[pallet::storage]
    pub type TableActive<T> = StorageMap<_, Twox64Concat, u32, bool, ValueQuery>;

    // FIX: New storage items for ownership and per-account limits
    #[pallet::storage]
    pub type TableOwner<T: Config> =
        StorageMap<_, Twox64Concat, u32, T::AccountId>;

    #[pallet::storage]
    pub type AccountTableCount<T: Config> =
        StorageMap<_, Blake2_128Concat, T::AccountId, u32, ValueQuery>;

    #[pallet::event]
    #[pallet::generate_deposit(fn deposit_event)]
    pub enum Event<T: Config> {
        TableCreated { table_id: u32, root: [u8; 32] },
        AddressAdded { table_id: u32, index: u32 },
        TableDeactivated { table_id: u32 },
        LookupPerformed { table_id: u32, index: u32, bytes_saved: u32 },
    }

    #[pallet::error]
    pub enum Error<T> {
        TableNotFound,
        TableNotActive,
        TableFull,
        MaxTablesExceeded,
        NotTableOwner,       // FIX: new
        TableIdOverflow,     // FIX: new
        IndexOutOfBounds,    // FIX: new
        Underflow,           // FIX: new
    }

    #[pallet::call]
    impl<T: Config> Pallet<T> {
        #[pallet::weight(10_000)]
        #[pallet::call_index(0)]
        pub fn create_table(origin: OriginFor<T>) -> DispatchResult {
            let who = ensure_signed(origin)?;

            // FIX: Enforce MaxTablesPerAccount
            let account_table_count = AccountTableCount::<T>::get(&who);
            ensure!(
                account_table_count < T::MaxTablesPerAccount::get(),
                Error::<T>::MaxTablesExceeded
            );

            // FIX: Safe u32 arithmetic, no cast from u64
            let table_id = AltTotalTables::<T>::get();
            let next_id = table_id
                .checked_add(1)
                .ok_or(Error::<T>::TableIdOverflow)?;

            // FIX: Include table_id in hash to ensure uniqueness per account
            let root = sp_io::hashing::blake2_256(&(who.clone(), table_id).encode());

            TableIds::<T>::insert(table_id, root);
            TableActive::<T>::insert(table_id, true);
            TableOwner::<T>::insert(table_id, who.clone()); // FIX: record owner
            AccountTableCount::<T>::mutate(&who, |c| *c = c.saturating_add(1)); // FIX
            AltTotalTables::<T>::put(next_id); // FIX: safe increment

            Self::deposit_event(Event::TableCreated { table_id, root });
            Ok(())
        }

        #[pallet::weight(10_000)]
        #[pallet::call_index(1)]
        pub fn add_address(origin: OriginFor<T>, table_id: u32) -> DispatchResult {
            ensure_signed(origin)?;

            // FIX: Explicit existence check
            ensure!(
                TableIds::<T>::contains_key(table_id),
                Error::<T>::TableNotFound
            );
            ensure!(TableActive::<T>::get(table_id), Error::<T>::TableNotActive);

            // FIX: Safe increment with checked_add
            let count = TableAddressCount::<T>::get(table_id);
            ensure!(
                count < T::MaxAddressesPerTable::get(),
                Error::<T>::TableFull
            );
            TableAddressCount::<T>::try_mutate(table_id, |c| -> DispatchResult {
                *c = c.checked_add(1).ok_or(Error::<T>::TableFull)?;
                Ok(())
            })?;

            // FIX: saturating arithmetic on global counters
            AltTotalAddresses::<T>::mutate(|a| *a = a.saturating_add(1));
            AltBytesSaved::<T>::mutate(|b| *b = b.saturating_add(30));

            Self::deposit_event(Event::AddressAdded {
                table_id,
                index: count,
            });
            Ok(())
        }

        #[pallet::weight(10_000)]
        #[pallet::call_index(2)]
        pub fn deactivate_table(origin: OriginFor<T>, table_id: u32) -> DispatchResult {
            let who = ensure_signed(origin)?;

            // FIX: Existence + ownership check
            let owner = TableOwner::<T>::get(table_id)
                .ok_or(Error::<T>::TableNotFound)?;
            ensure!(owner == who, Error::<T>::NotTableOwner);
            ensure!(TableActive::<T>::get(table_id), Error::<T>::TableNotActive);

            TableActive::<T>::insert(table_id, false);

            // FIX: Decrement account table count on deactivation
            AccountTableCount::<T>::mutate(&who, |c| *c = c.saturating_sub(1));

            Self::deposit_event(Event::TableDeactivated { table_id });
            Ok(())
        }

        #[pallet::weight(10_000)]
        #[pallet::call_index(3)]
        pub fn lookup_address(
            origin: OriginFor<T>,
            table_id: u32,
            index: u32,
        ) -> DispatchResult {
            ensure_signed(origin)?;

            // FIX: Validate table exists, is active, and index is in bounds
            ensure!(
                TableIds::<T>::contains_key(table_id),
                Error::<T>::TableNotFound
            );
            ensure!(TableActive::<T>::get(table_id), Error::<T>::TableNotActive);
            let count = TableAddressCount::<T>::get(table_id);
            ensure!(index < count, Error::<T>::IndexOutOfBounds);

            // FIX: saturating arithmetic
            AltTotalLookups::<T>::mutate(|l| *l = l.saturating_add(1));
            AltBytesSaved::<T>::mutate(|b| *b = b.saturating_add(30));

            Self::deposit_event(Event::LookupPerformed {
                table_id,
                index,
                bytes_saved: 30,
            });
            Ok(())
        }
    }
}
```

---

## Finding Summary Table

| # | Severity | Location | Issue |
|---|----------|----------|-------|
| 1 | 🔴 CRITICAL | `deactivate_table` | Any user can deactivate any table — no ownership check |
| 2 | 🔴 CRITICAL | `add_address` | No explicit table existence check |
| 3 | 🔴 CRITICAL | `create_table` | `u64 as u32` cast causes table_id collision after 2³² tables |
| 4 | 🔴 CRITICAL | `lookup_address` | Zero validation — counters freely inflatable, fake events |
| 5 | 🔴 CRITICAL | All mutates | Unchecked `+=` arithmetic on all counters |
| 6 | 🟠 HIGH | `create_table` | `MaxTablesPerAccount` config declared but never enforced |
| 7 | 🟠 HIGH | `TableAddressCount` | Pattern enables underflow if decrement ever added |
| 8 | 🟡 MEDIUM | `create_table` | Table root hash collision for same account's multiple tables |
| 9 | 🟡 MEDIUM | `deactivate_table` | No storage cleanup / `AccountTableCount` not decremented |