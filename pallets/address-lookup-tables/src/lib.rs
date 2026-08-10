#![allow(
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
            let table_id = AltTotalTables::<T>::get()
                .try_into()
                .map_err(|_| Error::<T>::TableLimitReached)?;
            let root = sp_io::hashing::blake2_256(&who.encode());
            TableIds::<T>::insert(table_id, root);
            TableActive::<T>::insert(table_id, true);
            AltTotalTables::<T>::mutate(|t| *t = t.saturating_add(1));
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
