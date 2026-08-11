#!/usr/bin/env python3
"""Fix ALT and Storage pallets for security issues."""

import subprocess

# === FIX 1: ALT pallet — enforce MaxTablesPerAccount ===
alt_new = r'''#![allow(
    clippy::let_unit_value,
    deprecated,
    clippy::clone_on_copy,
    clippy::type_complexity,
    clippy::needless_borrow,
    clippy::collapsible_if,
    clippy::redundant_closure,
    clippy::manual_saturating_arithmetic,
    clippy::unnecessary_cast,
    clippy::derivable_impls,
    clippy::manual_checked_ops,
    clippy::needless_borrows_for_generic_args,
    clippy::bool_assert_comparison
)]
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
    pub type AltTotalTables<T> = StorageValue<_, u64, ValueQuery>;
    #[pallet::storage]
    pub type AltTotalAddresses<T> = StorageValue<_, u64, ValueQuery>;
    #[pallet::storage]
    pub type AltTotalLookups<T> = StorageValue<_, u64, ValueQuery>;
    #[pallet::storage]
    pub type AltBytesSaved<T> = StorageValue<_, u64, ValueQuery>;
    #[pallet::storage]
    pub type TableIds<T> = StorageMap<_, Blake2_128Concat, u32, [u8; 32]>;
    #[pallet::storage]
    pub type TableAddressCount<T> = StorageMap<_, Blake2_128Concat, u32, u32, ValueQuery>;
    #[pallet::storage]
    pub type TableActive<T> = StorageMap<_, Blake2_128Concat, u32, bool, ValueQuery>;
    /// Track how many tables each account has created (DoS prevention)
    #[pallet::storage]
    pub type TablesPerAccount<T: Config> =
        StorageMap<_, Blake2_128Concat, T::AccountId, u32, ValueQuery>;
    #[pallet::event]
    #[pallet::generate_deposit(fn deposit_event)]
    pub enum Event<T: Config> {
        TableCreated {
            table_id: u32,
            root: [u8; 32],
        },
        AddressAdded {
            table_id: u32,
            index: u32,
        },
        TableDeactivated {
            table_id: u32,
        },
        LookupPerformed {
            table_id: u32,
            index: u32,
            bytes_saved: u32,
        },
    }
    #[pallet::error]
    pub enum Error<T> {
        TableNotFound,
        TableNotActive,
        AddressTooLong,
        TableFull,
        MaxTablesExceeded,
        NotTableOwner,
        TableLimitReached,
    }
    #[pallet::call]
    impl<T: Config> Pallet<T> {
        #[pallet::weight(0)]
        #[pallet::call_index(0)]
        pub fn create_table(origin: OriginFor<T>) -> DispatchResult {
            let who = ensure_signed(origin)?;

            // SECURITY: Enforce MaxTablesPerAccount to prevent DoS
            let current_count = TablesPerAccount::<T>::get(&who);
            ensure!(
                current_count < T::MaxTablesPerAccount::get(),
                Error::<T>::MaxTablesExceeded
            );

            let table_id = AltTotalTables::<T>::get()
                .try_into()
                .map_err(|_| Error::<T>::TableLimitReached)?;
            let root = sp_io::hashing::blake2_256(&who.encode());
            TableIds::<T>::insert(table_id, root);
            TableActive::<T>::insert(table_id, true);
            AltTotalTables::<T>::mutate(|t| *t = t.saturating_add(1));
            TablesPerAccount::<T>::insert(&who, current_count.saturating_add(1));

            Self::deposit_event(Event::TableCreated { table_id, root });
            Ok(())
        }
        #[pallet::weight(0)]
        #[pallet::call_index(1)]
        pub fn add_address(origin: OriginFor<T>, table_id: u32) -> DispatchResult {
            // SECURITY: Only table owner can add addresses
            let who = ensure_signed(origin)?;
            ensure!(TableActive::<T>::get(table_id), Error::<T>::TableNotActive);
            // Verify caller is the table owner
            let root = TableIds::<T>::get(table_id).ok_or(Error::<T>::TableNotFound)?;
            let expected_root = sp_io::hashing::blake2_256(&who.encode());
            ensure!(root == expected_root, Error::<T>::NotTableOwner);
            let count = TableAddressCount::<T>::get(table_id);
            ensure!(
                count < T::MaxAddressesPerTable::get(),
                Error::<T>::TableFull
            );
            TableAddressCount::<T>::mutate(table_id, |c| *c = c.saturating_add(1));
            AltTotalAddresses::<T>::mutate(|a| *a += 1);
            AltBytesSaved::<T>::mutate(|b| *b = b.saturating_add(30));
            Self::deposit_event(Event::AddressAdded {
                table_id,
                index: count,
            });
            Ok(())
        }
        #[pallet::weight(0)]
        #[pallet::call_index(2)]
        pub fn deactivate_table(origin: OriginFor<T>, table_id: u32) -> DispatchResult {
            let who = ensure_signed(origin)?;
            ensure!(TableActive::<T>::get(table_id), Error::<T>::TableNotActive);
            // Only table owner can deactivate
            let root = TableIds::<T>::get(table_id).ok_or(Error::<T>::TableNotFound)?;
            let expected_root = sp_io::hashing::blake2_256(&who.encode());
            ensure!(root == expected_root, Error::<T>::NotTableOwner);
            TableActive::<T>::insert(table_id, false);
            // Decrement per-account table count
            TablesPerAccount::<T>::mutate(&who, |c| *c = c.saturating_sub(1));
            Self::deposit_event(Event::TableDeactivated { table_id });
            Ok(())
        }
        #[pallet::weight(0)]
        #[pallet::call_index(3)]
        pub fn lookup_address(origin: OriginFor<T>, table_id: u32, index: u32) -> DispatchResult {
            let _who = ensure_signed(origin)?;
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

#[cfg(test)]
mod tests;
'''

# Write ALT pallet
proc = subprocess.Popen(
    ["ssh", "root@91.98.160.145", "cat > /opt/verdis-chain-rust/pallets/address-lookup-tables/src/lib.rs"],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
)
out, err = proc.communicate(input=alt_new, timeout=30)
print("ALT written:", out, err)

# Check if ALT tests need updating for new TablesPerAccount storage
alt_test = ssh_check = subprocess.run(
    ["ssh", "root@91.98.160.145", "grep -c MaxTablesPerAccount /opt/verdis-chain-rust/pallets/address-lookup-tables/src/tests.rs 2>/dev/null || echo 0"],
    capture_output=True, text=True, timeout=10
)
print("ALT test has MaxTablesPerAccount:", alt_test.stdout.strip())

# === FIX 2: Storage pallet — increment StorageRecordCount + add MaxSizeBytes + fix created_at ===
# We need to patch the existing file, not rewrite it entirely
# The key fix: add StorageRecordCount increment and size bound check in register_storage

storage_patch = r'''#!/bin/bash
cd /opt/verdis-chain-rust/pallets/storage/src

# Fix 1: Add MaxSizeBytes to Config
sed -i 's/type MaxRecords: Get<u32>;/type MaxRecords: Get<u32>;\n        #[pallet::constant]\n        type MaxSizeBytes: Get<u64>;/' lib.rs

# Fix 2: Add SizeTooLarge error
sed -i 's/EndpointTooLong,/EndpointTooLong,\n        SizeTooLarge,/' lib.rs

# Fix 3: Increment StorageRecordCount in register_storage + add size check + fix created_at
# Replace the register_storage body
python3 << 'PYEOF'
import re

with open("lib.rs", "r") as f:
    content = f.read()

# Add size check after MaxRecords check
old = '''            ensure!(
                StorageRecordCount::<T>::get() < T::MaxRecords::get(),
                Error::<T>::MaxRecordsReached
            );'''
new = '''            ensure!(
                StorageRecordCount::<T>::get() < T::MaxRecords::get(),
                Error::<T>::MaxRecordsReached
            );
            // SECURITY: Bound size_bytes to prevent inflation of TotalStored
            ensure!(
                size_bytes <= T::MaxSizeBytes::get(),
                Error::<T>::SizeTooLarge
            );'''
content = content.replace(old, new)

# Fix: increment StorageRecordCount (was missing!)
old2 = '''            StorageRecords::<T>::insert(id_bv, record);
            TotalStored::<T>::mutate(|t| *t = t.saturating_add(size_bytes));'''
new2 = '''            StorageRecords::<T>::insert(id_bv, record);
            StorageRecordCount::<T>::mutate(|c| *c = c.saturating_add(1));
            TotalStored::<T>::mutate(|t| *t = t.saturating_add(size_bytes));'''
content = content.replace(old2, new2)

# Fix: use block number for created_at instead of 0
old3 = 'created_at: 0,'
new3 = 'created_at: frame_system::Pallet::<T>::block_number().try_into().unwrap_or(0),'
content = content.replace(old3, new3)

with open("lib.rs", "w") as f:
    f.write(content)
print("Storage pallet patched")
PYEOF
'''

proc2 = subprocess.Popen(
    ["ssh", "root@91.98.160.145", storage_patch],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=False
)
# Actually we need to send it as a script
proc2 = subprocess.run(
    ["ssh", "root@91.98.160.145", storage_patch],
    capture_output=True, text=True, timeout=30
)
print("Storage patched:", proc2.stdout, proc2.stderr)

# Now add MaxSizeBytes to runtime config
runtime_patch = r'''#!/bin/bash
cd /opt/verdis-chain-rust/runtime/src
# Check if MaxSizeBytes already exists
grep -q "MaxSizeBytes" lib.rs && echo "Already exists" || (
    # Add the constant
    sed -i '/pub const MaxRecords: u32 = 10000;/a\    pub const MaxSizeBytes: u64 = 1_000_000_000_000;  // 1 TB max per record' lib.rs
    # Add to Config impl
    sed -i '/type MaxRecords = MaxRecords;/a\        type MaxSizeBytes = MaxSizeBytes;' lib.rs
    echo "MaxSizeBytes added to runtime"
)
'''
proc3 = subprocess.run(
    ["ssh", "root@91.98.160.145", runtime_patch],
    capture_output=True, text=True, timeout=30
)
print("Runtime patched:", proc3.stdout, proc3.stderr)

# Update storage tests to include MaxSizeBytes
storage_test_patch = r'''#!/bin/bash
cd /opt/verdis-chain-rust/pallets/storage/src
# Add MaxSizeBytes to test config
sed -i '/type MaxRecords = MaxRecords;/a\        type MaxSizeBytes = MaxSizeBytes;' tests.rs 2>/dev/null
# Add the constant if not present
grep -q "MaxSizeBytes" tests.rs && echo "Test config updated" || (
    sed -i '/pub const MaxRecords: u32 = 1000;/a\    pub const MaxSizeBytes: u64 = 1_000_000_000_000;' tests.rs
    sed -i '/type MaxRecords = MaxRecords;/a\        type MaxSizeBytes = MaxSizeBytes;' tests.rs
    echo "Test config patched"
)
'''
proc4 = subprocess.run(
    ["ssh", "root@91.98.160.145", storage_test_patch],
    capture_output=True, text=True, timeout=30
)
print("Tests patched:", proc4.stdout, proc4.stderr)

# Check if ALT tests need MaxTablesPerAccount config
alt_test_check = r'''#!/bin/bash
cd /opt/verdis-chain-rust/pallets/address-lookup-tables/src
grep -q "MaxTablesPerAccount" tests.rs && echo "Already configured" || (
    echo "Need to add MaxTablesPerAccount to ALT tests"
    head -5 tests.rs
)
'''
proc5 = subprocess.run(
    ["ssh", "root@91.98.160.145", alt_test_check],
    capture_output=True, text=True, timeout=30
)
print("ALT test check:", proc5.stdout, proc5.stderr)
