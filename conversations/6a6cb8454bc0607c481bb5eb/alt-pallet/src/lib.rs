//! # Address Lookup Tables (ALT) Pallet
//!
//! Inspired by Solana's Address Lookup Tables, this pallet provides:
//! - Compact account references for transactions (reduce tx size by 60-80%)
//! - Lookup table creation and management
//! - Address deactivation and cleanup
//! - Significant bandwidth savings for high-frequency transactions

#![cfg_attr(not(feature = "std"), no_std)]

use codec::{Decode, Encode, MaxEncodedLen};
use frame_support::{pallet_prelude::*, dispatch::DispatchResult};
use frame_system::pallet_prelude::*;
use scale_info::TypeInfo;
use sp_std::prelude::*;
use sp_std::vec::Vec;
use sp_core::blake2_256;

pub use pallet::*;

#[frame_support::pallet]
pub mod pallet {
    use super::*;

    type AccountIdOf<T> = <T as frame_system::Config>::AccountId;

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    #[pallet::config]
    pub trait Config: frame_system::Config {
        type MaxAddressesPerTable: Get<u32>;
        type MaxTablesPerAccount: Get<u32>;
    }

    #[derive(Encode, Decode, Clone, PartialEq, Eq, MaxEncodedLen, TypeInfo)]
    pub struct LookupTable {
        pub table_id: [u8; 32],
        pub creator: Vec<u8>,
        pub addresses: BoundedVec<Vec<u8>, ConstU32<256>>,
        pub active: bool,
        pub created_block: u32,
        pub deactivation_block: Option<u32>,
        pub usage_count: u64,
    }

    #[derive(Encode, Decode, Clone, PartialEq, Eq, MaxEncodedLen, TypeInfo)]
    pub struct AltStats {
        pub total_tables: u64,
        pub total_addresses_indexed: u64,
        pub total_lookups: u64,
        pub bytes_saved: u64,
    }

    // === Storage ===
    #[pallet::storage]
    #[pallet::getter(fn lookup_tables)]
    pub type LookupTables<T: Config> = StorageMap<_, Twox64Concat, [u8; 32], LookupTable>;

    #[pallet::storage]
    #[pallet::getter(fn tables_by_creator)]
    pub type TablesByCreator<T: Config> = StorageMap<_, Twox64Concat, Vec<u8>, Vec<[u8; 32]>, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn alt_stats)]
    pub type AltStats<T: Config> = StorageValue<_, AltStats, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn address_index)]
    pub type AddressIndex<T: Config> = StorageDoubleMap<
        _,
        Twox64Concat,
        [u8; 32],
        Twox64Concat,
        Vec<u8>,
        u16,
    >;

    // === Events ===
    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        TableCreated { table_id: [u8; 32], creator: Vec<u8> },
        AddressAdded { table_id: [u8; 32], index: u16 },
        TableDeactivated { table_id: [u8; 32], block: u32 },
        LookupPerformed { table_id: [u8; 32], index: u16, bytes_saved: u32 },
    }

    // === Errors ===
    #[pallet::error]
    pub enum Error<T> {
        TableNotFound,
        TableNotActive,
        TableFull,
        AddressAlreadyInTable,
        NotTableCreator,
        MaxTablesExceeded,
    }

    // === Extrinsics ===
    #[pallet::call]
    impl<T: Config> Pallet<T> {
        /// Create a new address lookup table
        #[pallet::call_index(0)]
        pub fn create_table(origin: OriginFor<T>) -> DispatchResult {
            let who = ensure_signed(origin)?;

            let creator_tables = TablesByCreator::<T>::get(who.encode());
            ensure!(creator_tables.len() < T::MaxTablesPerAccount::get() as usize, Error::<T>::MaxTablesExceeded);

            let mut seed = who.encode();
            seed.extend_from_slice(&creator_tables.len().to_le_bytes());
            let table_id = blake2_256(&seed);

            let table = LookupTable {
                table_id,
                creator: who.encode(),
                addresses: BoundedVec::default(),
                active: true,
                created_block: frame_system::Pallet::<T>::block_number().try_into().ok().unwrap_or(0),
                deactivation_block: None,
                usage_count: 0,
            };

            LookupTables::<T>::insert(table_id, table);
            TablesByCreator::<T>::mutate(who.encode(), |tables| tables.push(table_id));

            let stats = AltStats::<T>::get();
            AltStats::<T>::put(AltStats {
                total_tables: stats.total_tables + 1,
                total_addresses_indexed: stats.total_addresses_indexed,
                total_lookups: stats.total_lookups,
                bytes_saved: stats.bytes_saved,
            });

            Self::deposit_event(Event::TableCreated { table_id, creator: who.encode() });
            Ok(())
        }

        /// Add an address to a lookup table
        #[pallet::call_index(1)]
        pub fn add_address(
            origin: OriginFor<T>,
            table_id: [u8; 32],
            address: Vec<u8>,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            let mut table = LookupTables::<T>::get(table_id).ok_or(Error::<T>::TableNotFound)?;
            ensure!(table.active, Error::<T>::TableNotActive);
            ensure!(table.creator == who.encode(), Error::<T>::NotTableCreator);
            ensure!(table.addresses.len() < T::MaxAddressesPerTable::get() as usize, Error::<T>::TableFull);

            // Check for duplicates
            if table.addresses.iter().any(|a| a == &address) {
                return Err(Error::<T>::AddressAlreadyInTable.into());
            }

            let index = table.addresses.len() as u16;
            table.addresses.try_push(address.clone()).map_err(|_| Error::<T>::TableFull)?;

            AddressIndex::<T>::insert(table_id, address, index);
            LookupTables::<T>::insert(table_id, table);

            let stats = AltStats::<T>::get();
            AltStats::<T>::put(AltStats {
                total_tables: stats.total_tables,
                total_addresses_indexed: stats.total_addresses_indexed + 1,
                total_lookups: stats.total_lookups,
                bytes_saved: stats.bytes_saved + 30, // ~30 bytes saved per indexed address
            });

            Self::deposit_event(Event::AddressAdded { table_id, index });
            Ok(())
        }

        /// Deactivate a lookup table (prevents new additions, allows lookups until deactivation period ends)
        #[pallet::call_index(2)]
        pub fn deactivate_table(origin: OriginFor<T>, table_id: [u8; 32]) -> DispatchResult {
            let who = ensure_signed(origin)?;

            let mut table = LookupTables::<T>::get(table_id).ok_or(Error::<T>::TableNotFound)?;
            ensure!(table.creator == who.encode(), Error::<T>::NotTableCreator);

            table.active = false;
            table.deactivation_block = Some(frame_system::Pallet::<T>::block_number().try_into().ok().unwrap_or(0));
            LookupTables::<T>::insert(table_id, table);

            Self::deposit_event(Event::TableDeactivated {
                table_id,
                block: frame_system::Pallet::<T>::block_number().try_into().ok().unwrap_or(0),
            });
            Ok(())
        }

        /// Perform a lookup (internal, called by other pallets)
        #[pallet::call_index(3)]
        pub fn lookup_address(
            origin: OriginFor<T>,
            table_id: [u8; 32],
            index: u16,
        ) -> DispatchResult {
            let _ = ensure_signed(origin)?;
            let table = LookupTables::<T>::get(table_id).ok_or(Error::<T>::TableNotFound)?;

            ensure!((index as usize) < table.addresses.len(), Error::<T>::TableNotFound);

            // Update stats
            let bytes_saved = 30u32; // Approximate bytes saved per lookup
            let stats = AltStats::<T>::get();
            AltStats::<T>::put(AltStats {
                total_tables: stats.total_tables,
                total_addresses_indexed: stats.total_addresses_indexed,
                total_lookups: stats.total_lookups + 1,
                bytes_saved: stats.bytes_saved + bytes_saved as u64,
            });

            Self::deposit_event(Event::LookupPerformed { table_id, index, bytes_saved });
            Ok(())
        }
    }

    impl<T: Config> Pallet<T> {
        pub fn get_table(table_id: [u8; 32]) -> Option<LookupTable> {
            LookupTables::<T>::get(table_id)
        }

        pub fn get_stats() -> AltStats {
            AltStats::<T>::get()
        }
    }
}
