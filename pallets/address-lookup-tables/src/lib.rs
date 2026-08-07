#![cfg_attr(not(feature = "std"), no_std)]
use frame_support::{pallet_prelude::*, dispatch::DispatchResult};
use frame_system::pallet_prelude::*;
use sp_std::prelude::*;
pub use pallet::*;

#[frame_support::pallet]
pub mod pallet {
    use super::*;
    #[pallet::pallet] pub struct Pallet<T>(_);
    #[pallet::config]
    pub trait Config: frame_system::Config {
        type MaxAddressesPerTable: Get<u32>;
        type MaxTablesPerAccount: Get<u32>;
    }
    #[pallet::storage] pub type AltTotalTables<T> = StorageValue<_, u64, ValueQuery>;
    #[pallet::storage] pub type AltTotalAddresses<T> = StorageValue<_, u64, ValueQuery>;
    #[pallet::storage] pub type AltTotalLookups<T> = StorageValue<_, u64, ValueQuery>;
    #[pallet::storage] pub type AltBytesSaved<T> = StorageValue<_, u64, ValueQuery>;
    #[pallet::storage] pub type TableIds<T> = StorageMap<_, Twox64Concat, u32, [u8; 32]>;
    #[pallet::storage] pub type TableAddressCount<T> = StorageMap<_, Twox64Concat, u32, u32, ValueQuery>;
    #[pallet::storage] pub type TableActive<T> = StorageMap<_, Twox64Concat, u32, bool, ValueQuery>;
    #[pallet::event] #[pallet::generate_deposit(fn deposit_event)]
    pub enum Event<T: Config> {
        TableCreated { table_id: u32, root: [u8; 32] },
        AddressAdded { table_id: u32, index: u32 },
        TableDeactivated { table_id: u32 },
        LookupPerformed { table_id: u32, index: u32, bytes_saved: u32 },
    }
    #[pallet::error] pub enum Error<T> { TableNotFound, TableNotActive, TableFull, MaxTablesExceeded }
    #[pallet::call]
    impl<T: Config> Pallet<T> {
        #[pallet::weight(0)]
        #[pallet::call_index(0)]
        pub fn create_table(origin: OriginFor<T>) -> DispatchResult {
            let who = ensure_signed(origin)?;
            let table_id = AltTotalTables::<T>::get() as u32;
            let root = sp_io::hashing::blake2_256(&who.encode());
            TableIds::<T>::insert(table_id, root);
            TableActive::<T>::insert(table_id, true);
            AltTotalTables::<T>::mutate(|t| *t += 1);
            Self::deposit_event(Event::TableCreated { table_id, root });
            Ok(())
        }
        #[pallet::weight(0)]
        #[pallet::call_index(1)]
        pub fn add_address(origin: OriginFor<T>, table_id: u32) -> DispatchResult {
            let _ = ensure_signed(origin)?;
            ensure!(TableActive::<T>::get(table_id), Error::<T>::TableNotActive);
            let count = TableAddressCount::<T>::get(table_id);
            ensure!(count < T::MaxAddressesPerTable::get(), Error::<T>::TableFull);
            TableAddressCount::<T>::mutate(table_id, |c| *c += 1);
            AltTotalAddresses::<T>::mutate(|a| *a += 1);
            AltBytesSaved::<T>::mutate(|b| *b += 30);
            Self::deposit_event(Event::AddressAdded { table_id, index: count });
            Ok(())
        }
        #[pallet::weight(0)]
        #[pallet::call_index(2)]
        pub fn deactivate_table(origin: OriginFor<T>, table_id: u32) -> DispatchResult {
            let _ = ensure_signed(origin)?;
            TableActive::<T>::insert(table_id, false);
            Self::deposit_event(Event::TableDeactivated { table_id });
            Ok(())
        }
        #[pallet::weight(0)]
        #[pallet::call_index(3)]
        pub fn lookup_address(origin: OriginFor<T>, table_id: u32, index: u32) -> DispatchResult {
            let _ = ensure_signed(origin)?;
            AltTotalLookups::<T>::mutate(|l| *l += 1);
            AltBytesSaved::<T>::mutate(|b| *b += 30);
            Self::deposit_event(Event::LookupPerformed { table_id, index, bytes_saved: 30 });
            Ok(())
        }
    }
}
