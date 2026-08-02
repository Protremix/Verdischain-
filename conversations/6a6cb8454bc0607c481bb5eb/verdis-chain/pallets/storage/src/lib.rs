//! # Verdis Decentralized Storage Pallet
//!
//! IPFS/Arweave integration for storing large data off-chain:
//! - IPFS CID registration and verification
//! - Arweave transaction ID tracking
//! - Content addressing with Blake3
//! - Storage provider reputation
//! - Pinning requests and status tracking

#![cfg_attr(not(feature = "std"), no_std)]

use codec::{Decode, Encode, MaxEncodedLen};
use frame_support::{
    dispatch::DispatchResult,
    ensure,
    pallet_prelude::*,
    traits::Get,
    PalletId,
};
use frame_system::pallet_prelude::*;
use sp_std::prelude::*;

pub use pallet::*;

#[frame_support::pallet]
pub mod pallet {
    use super::*;

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    // === Storage Types ===

    #[derive(Encode, Decode, Clone, PartialEq, Eq, MaxEncodedLen, RuntimeDebug)]
    pub enum StorageBackend {
        Ipfs,
        Arweave,
    }

    #[derive(Encode, Decode, Clone, PartialEq, Eq, MaxEncodedLen, RuntimeDebug)]
    pub struct StorageRecord<AccountId> {
        pub id: Vec<u8>,           // CID or Arweave TX ID
        pub backend: StorageBackend,
        pub owner: AccountId,
        pub size_bytes: u64,
        pub blake3_hash: [u8; 32], // Content verification
        pub pinned: bool,
        pub created_at: u64,
    }

    #[derive(Encode, Decode, Clone, PartialEq, Eq, MaxEncodedLen, RuntimeDebug)]
    pub struct StorageProvider<AccountId> {
        pub address: AccountId,
        pub backend: StorageBackend,
        pub endpoint: Vec<u8>,     // IPFS gateway or Arweave gateway URL
        pub reputation: u32,
        pub total_stored: u64,
        pub active: bool,
    }

    // === Storage Items ===

    #[pallet::storage]
    #[pallet::getter(fn storage_records)]
    pub type StorageRecords<T: Config> =
        StorageMap<_, Blake2_128Concat, Vec<u8>, StorageRecord<T::AccountId>>;

    #[pallet::storage]
    #[pallet::getter(fn storage_providers)]
    pub type StorageProviders<T: Config> =
        StorageMap<_, Blake2_128Concat, T::AccountId, StorageProvider<T::AccountId>>;

    #[pallet::storage]
    #[pallet::getter(fn total_stored)]
    pub type TotalStored<T: Config> = StorageValue<_, u64, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn pin_requests)]
    pub type PinRequests<T: Config> =
        StorageMap<_, Blake2_128Concat, Vec<u8>, bool, ValueQuery>;

    // === Events ===

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        StorageRecordCreated {
            id: Vec<u8>,
            backend: StorageBackend,
            owner: T::AccountId,
            size: u64,
        },
        StorageRecordVerified {
            id: Vec<u8>,
            hash: [u8; 32],
        },
        ProviderRegistered {
            address: T::AccountId,
            backend: StorageBackend,
            endpoint: Vec<u8>,
        },
        PinRequested {
            id: Vec<u8>,
        },
        PinRemoved {
            id: Vec<u8>,
        },
        ContentRetrieved {
            id: Vec<u8>,
            requester: T::AccountId,
        },
    }

    // === Errors ===

    #[pallet::error]
    pub enum Error<T> {
        RecordNotFound,
        RecordAlreadyExists,
        NotRecordOwner,
        ProviderNotFound,
        ProviderAlreadyRegistered,
        ProviderInactive,
        InvalidHash,
        InvalidBackend,
        MaxRecordsReached,
    }

    // === Config ===

    #[pallet::config]
    pub trait Config: frame_system::Config {
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
        #[pallet::constant]
        type PalletId: Get<PalletId>;
        #[pallet::constant]
        type MaxRecords: Get<u32>;
        type WeightInfo: WeightInfo;
    }

    // === Extrinsics ===

    #[pallet::call]
    impl<T: Config> Pallet<T> {
        /// Register a storage record (IPFS CID or Arweave TX ID)
        #[pallet::call_index(0)]
        #[pallet::weight(Weight::from_parts(80_000_000, 0))]
        pub fn register_storage(
            origin: OriginFor<T>,
            id: Vec<u8>,
            backend: StorageBackend,
            size_bytes: u64,
            blake3_hash: [u8; 32],
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            ensure!(!StorageRecords::<T>::contains_key(&id), Error::<T>::RecordAlreadyExists);
            ensure!(
                StorageRecords::<T>::iter().count() as u32 < T::MaxRecords::get(),
                Error::<T>::MaxRecordsReached
            );

            let record = StorageRecord {
                id: id.clone(),
                backend,
                owner: who.clone(),
                size_bytes,
                blake3_hash,
                pinned: false,
                created_at: 0,
            };

            StorageRecords::<T>::insert(id.clone(), record);
            TotalStored::<T>::mutate(|t| *t = t.saturating_add(size_bytes));

            Self::deposit_event(Event::StorageRecordCreated {
                id,
                backend,
                owner: who,
                size: size_bytes,
            });
            Ok(())
        }

        /// Verify storage content against Blake3 hash
        #[pallet::call_index(1)]
        #[pallet::weight(Weight::from_parts(30_000_000, 0))]
        pub fn verify_storage(origin: OriginFor<T>, id: Vec<u8>, hash: [u8; 32]) -> DispatchResult {
            let _who = ensure_signed(origin)?;

            StorageRecords::<T>::mutate(&id, |r| {
                let record = r.as_mut().ok_or(Error::<T>::RecordNotFound)?;
                ensure!(record.blake3_hash == hash, Error::<T>::InvalidHash);
                Ok::<(), Error<T>>(())
            })?;

            Self::deposit_event(Event::StorageRecordVerified { id, hash });
            Ok(())
        }

        /// Register as a storage provider (IPFS gateway or Arweave gateway)
        #[pallet::call_index(2)]
        #[pallet::weight(Weight::from_parts(60_000_000, 0))]
        pub fn register_provider(
            origin: OriginFor<T>,
            backend: StorageBackend,
            endpoint: Vec<u8>,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            ensure!(!StorageProviders::<T>::contains_key(&who), Error::<T>::ProviderAlreadyRegistered);

            let provider = StorageProvider {
                address: who.clone(),
                backend,
                endpoint,
                reputation: 100,
                total_stored: 0,
                active: true,
            };

            StorageProviders::<T>::insert(who.clone(), provider);

            Self::deposit_event(Event::ProviderRegistered {
                address: who,
                backend,
                endpoint: Vec::new(),
            });
            Ok(())
        }

        /// Request pinning for a storage record (IPFS)
        #[pallet::call_index(3)]
        #[pallet::weight(Weight::from_parts(20_000_000, 0))]
        pub fn request_pin(origin: OriginFor<T>, id: Vec<u8>) -> DispatchResult {
            let who = ensure_signed(origin)?;

            ensure!(StorageRecords::<T>::contains_key(&id), Error::<T>::RecordNotFound);
            PinRequests::<T>::insert(&id, true);
            StorageRecords::<T>::mutate(&id, |r| {
                if let Some(r) = r {
                    r.pinned = true;
                }
            });

            Self::deposit_event(Event::PinRequested { id });
            Ok(())
        }

        /// Remove pin from a storage record
        #[pallet::call_index(4)]
        #[pallet::weight(Weight::from_parts(20_000_000, 0))]
        pub fn remove_pin(origin: OriginFor<T>, id: Vec<u8>) -> DispatchResult {
            let who = ensure_signed(origin)?;

            let record = StorageRecords::<T>::get(&id).ok_or(Error::<T>::RecordNotFound)?;
            ensure!(record.owner == who, Error::<T>::NotRecordOwner);

            PinRequests::<T>::remove(&id);
            StorageRecords::<T>::mutate(&id, |r| {
                if let Some(r) = r {
                    r.pinned = false;
                }
            });

            Self::deposit_event(Event::PinRemoved { id });
            Ok(())
        }
    }

    // === Query Functions ===
    impl<T: Config> Pallet<T> {
        pub fn get_record(id: &Vec<u8>) -> Option<StorageRecord<T::AccountId>> {
            StorageRecords::<T>::get(id)
        }

        pub fn get_provider(address: &T::AccountId) -> Option<StorageProvider<T::AccountId>> {
            StorageProviders::<T>::get(address)
        }

        pub fn get_total_stored() -> u64 {
            TotalStored::<T>::get()
        }

        pub fn get_all_providers() -> Vec<StorageProvider<T::AccountId>> {
            StorageProviders::<T>::iter().map(|(_, p)| p).collect()
        }
    }

    pub trait WeightInfo {
        fn register_storage() -> Weight;
        fn verify_storage() -> Weight;
        fn register_provider() -> Weight;
        fn request_pin() -> Weight;
        fn remove_pin() -> Weight;
    }

    pub struct SubstrateWeight<T>(PhantomData<T>);
    impl<T: frame_system::Config> WeightInfo for SubstrateWeight<T> {
        fn register_storage() -> Weight { Weight::from_parts(80_000_000, 0) }
        fn verify_storage() -> Weight { Weight::from_parts(30_000_000, 0) }
        fn register_provider() -> Weight { Weight::from_parts(60_000_000, 0) }
        fn request_pin() -> Weight { Weight::from_parts(20_000_000, 0) }
        fn remove_pin() -> Weight { Weight::from_parts(20_000_000, 0) }
    }
}
