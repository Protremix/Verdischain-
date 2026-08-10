//! # Verdis Decentralized Storage Pallet
//!
//! IPFS/Arweave integration for storing large data off-chain:
//! - IPFS CID registration and verification
//! - Arweave transaction ID tracking
//! - Content addressing with Blake3
//! - Storage provider reputation
//! - Pinning requests and status tracking

#![cfg_attr(not(feature = "std"), no_std)]
#![allow(deprecated)]
#![allow(clippy::all)]
use codec::{Decode, DecodeWithMemTracking, Encode, MaxEncodedLen};
use frame_support::{dispatch::DispatchResult, ensure, pallet_prelude::*, traits::Get, PalletId};
use frame_system::pallet_prelude::*;
use scale_info::TypeInfo;
use sp_std::prelude::*;

pub use pallet::*;

#[frame_support::pallet]
pub mod pallet {
    use super::*;

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    // === Storage Types ===

    #[derive(Encode, Decode, Clone, Copy, PartialEq, Eq, MaxEncodedLen, TypeInfo, Debug)]
    pub enum StorageBackend {
        Ipfs,
        Arweave,
    }
    impl DecodeWithMemTracking for StorageBackend {}

    #[derive(Encode, Decode, Clone, PartialEq, Eq, MaxEncodedLen, TypeInfo, Debug)]
    pub struct StorageRecord<AccountId> {
        pub id: BoundedVec<u8, ConstU32<64>>,
        pub backend: StorageBackend,
        pub owner: AccountId,
        pub size_bytes: u64,
        pub blake3_hash: [u8; 32],
        pub pinned: bool,
        pub created_at: u64,
    }

    #[derive(Encode, Decode, Clone, PartialEq, Eq, MaxEncodedLen, TypeInfo, Debug)]
    pub struct StorageProvider<AccountId> {
        pub address: AccountId,
        pub backend: StorageBackend,
        pub endpoint: BoundedVec<u8, ConstU32<128>>,
        pub reputation: u32,
        pub total_stored: u64,
        pub active: bool,
    }

    // === Storage Items ===

    #[pallet::storage]
    #[pallet::getter(fn storage_records)]
    pub type StorageRecords<T: Config> =
        StorageMap<_, Blake2_128Concat, BoundedVec<u8, ConstU32<64>>, StorageRecord<T::AccountId>>;

    #[pallet::storage]
    #[pallet::getter(fn storage_record_count)]
    pub type StorageRecordCount<T: Config> = StorageValue<_, u32, ValueQuery>;

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
        StorageMap<_, Blake2_128Concat, BoundedVec<u8, ConstU32<64>>, bool, ValueQuery>;

    // === Cloudbreak: Horizontal Account Scaling ===
    #[derive(Encode, Decode, Clone, PartialEq, Eq, MaxEncodedLen, TypeInfo, Default)]
    pub struct ShardInfo {
        pub shard_id: u32,
        pub account_count: u64,
        pub total_size_bytes: u64,
        pub last_updated_block: u32,
    }

    #[pallet::storage]
    #[pallet::getter(fn account_shards)]
    pub type AccountShards<T: Config> =
        StorageMap<_, Twox64Concat, u32, BoundedVec<T::AccountId, ConstU32<1024>>, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn shard_info)]
    pub type ShardInfoStorage<T: Config> = StorageMap<_, Twox64Concat, u32, ShardInfo, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn account_to_shard)]
    pub type AccountToShard<T: Config> = StorageMap<_, Twox64Concat, T::AccountId, u32, ValueQuery>;

    // === Events ===

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        AccountSharded {
            account: T::AccountId,
            shard_id: u32,
        },
        ShardRebalanced {
            shard_id: u32,
            new_count: u64,
        },
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
        NotOwner,
        NotRecordOwner,
        ProviderNotFound,
        ProviderAlreadyRegistered,
        ProviderInactive,
        InvalidHash,
        InvalidBackend,
        MaxRecordsReached,
        IdTooLong,
        EndpointTooLong,
    }

    // === Config ===

    #[pallet::config]
    pub trait Config: frame_system::Config {
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
        #[pallet::constant]
        type PalletId: Get<PalletId>;
        #[pallet::constant]
        type MaxRecords: Get<u32>;
        #[pallet::constant]
        type ShardCount: Get<u32>;
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

            let id_bv: BoundedVec<u8, ConstU32<64>> =
                id.clone().try_into().map_err(|_| Error::<T>::IdTooLong)?;

            ensure!(
                !StorageRecords::<T>::contains_key(&id_bv),
                Error::<T>::RecordAlreadyExists
            );
            ensure!(
                StorageRecordCount::<T>::get() < T::MaxRecords::get(),
                Error::<T>::MaxRecordsReached
            );

            let record = StorageRecord {
                id: id_bv.clone(),
                backend,
                owner: who.clone(),
                size_bytes,
                blake3_hash,
                pinned: false,
                created_at: 0,
            };

            StorageRecords::<T>::insert(id_bv, record);
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

            let id_bv: BoundedVec<u8, ConstU32<64>> =
                id.clone().try_into().map_err(|_| Error::<T>::IdTooLong)?;

            StorageRecords::<T>::mutate(&id_bv, |r| {
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

            ensure!(
                !StorageProviders::<T>::contains_key(&who),
                Error::<T>::ProviderAlreadyRegistered
            );

            let endpoint_bv: BoundedVec<u8, ConstU32<128>> = endpoint
                .clone()
                .try_into()
                .map_err(|_| Error::<T>::EndpointTooLong)?;

            let provider = StorageProvider {
                address: who.clone(),
                backend,
                endpoint: endpoint_bv,
                reputation: 100,
                total_stored: 0,
                active: true,
            };

            StorageProviders::<T>::insert(who.clone(), provider);

            Self::deposit_event(Event::ProviderRegistered {
                address: who,
                backend,
                endpoint,
            });
            Ok(())
        }

        /// Request pinning for a storage record (IPFS)
        #[pallet::call_index(3)]
        #[pallet::weight(Weight::from_parts(20_000_000, 0))]
        pub fn request_pin(origin: OriginFor<T>, id: Vec<u8>) -> DispatchResult {
            let who = ensure_signed(origin)?;

            let id_bv: BoundedVec<u8, ConstU32<64>> =
                id.clone().try_into().map_err(|_| Error::<T>::IdTooLong)?;

            ensure!(
                StorageRecords::<T>::contains_key(&id_bv),
                Error::<T>::RecordNotFound
            );
            // Only record owner can pin
            let record = StorageRecords::<T>::get(&id_bv).ok_or(Error::<T>::RecordNotFound)?;
            ensure!(record.owner == who, Error::<T>::NotOwner);
            PinRequests::<T>::insert(&id_bv, true);
            StorageRecords::<T>::mutate(&id_bv, |r| {
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

            let id_bv: BoundedVec<u8, ConstU32<64>> =
                id.clone().try_into().map_err(|_| Error::<T>::IdTooLong)?;

            let record = StorageRecords::<T>::get(&id_bv).ok_or(Error::<T>::RecordNotFound)?;
            ensure!(record.owner == who, Error::<T>::NotRecordOwner);

            PinRequests::<T>::remove(&id_bv);
            StorageRecords::<T>::mutate(&id_bv, |r| {
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
        pub fn get_record(
            id: &BoundedVec<u8, ConstU32<64>>,
        ) -> Option<StorageRecord<T::AccountId>> {
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
        fn register_storage() -> Weight {
            Weight::from_parts(80_000_000, 0)
        }
        fn verify_storage() -> Weight {
            Weight::from_parts(30_000_000, 0)
        }
        fn register_provider() -> Weight {
            Weight::from_parts(60_000_000, 0)
        }
        fn request_pin() -> Weight {
            Weight::from_parts(20_000_000, 0)
        }
        fn remove_pin() -> Weight {
            Weight::from_parts(20_000_000, 0)
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use frame_support::{
        assert_noop, assert_ok, construct_runtime, derive_impl, parameter_types, traits::ConstU32,
    };
    use sp_io::TestExternalities;
    use sp_keyring::Sr25519Keyring;
    use sp_runtime::{traits::IdentityLookup, BuildStorage};

    type Block = frame_system::mocking::MockBlock<Test>;

    construct_runtime!(
        pub enum Test { System: frame_system, Storage: crate }
    );

    #[derive_impl(frame_system::config_preludes::TestDefaultConfig as frame_system::DefaultConfig)]
    impl frame_system::Config for Test {
        type AccountId = sp_core::crypto::AccountId32;
        type Lookup = IdentityLookup<Self::AccountId>;
        type Block = Block;
        type AccountData = ();
    }

    parameter_types! {
        pub const StorPalletId: PalletId = PalletId(*b"v/stores");
        pub const MaxRecords: u32 = 1000;
    }

    impl Config for Test {
        type ShardCount = ConstU32<16>;
        type RuntimeEvent = RuntimeEvent;
        type PalletId = StorPalletId;
        type MaxRecords = MaxRecords;
        type WeightInfo = SubstrateWeight<Test>;
    }

    pub fn new_test_ext() -> TestExternalities {
        let t = frame_system::GenesisConfig::<Test>::default()
            .build_storage()
            .unwrap();
        let mut ext = TestExternalities::new(t);
        ext.execute_with(|| System::set_block_number(1));
        ext
    }

    #[test]
    fn test_genesis_empty() {
        new_test_ext().execute_with(|| {
            assert_eq!(Storage::get_total_stored(), 0);
        });
    }

    #[test]
    fn test_register_storage() {
        new_test_ext().execute_with(|| {
            let hash = [1u8; 32];
            assert_ok!(Storage::register_storage(
                RuntimeOrigin::signed(Sr25519Keyring::Alice.to_account_id()),
                b"doc-1".to_vec(),
                StorageBackend::Ipfs,
                1024,
                hash,
            ));
            let key: BoundedVec<u8, ConstU32<64>> = b"doc-1".to_vec().try_into().unwrap();
            assert!(StorageRecords::<Test>::contains_key(&key));
            assert_eq!(Storage::get_total_stored(), 1024);
        });
    }

    #[test]
    fn test_register_duplicate() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            let hash = [1u8; 32];
            Storage::register_storage(
                RuntimeOrigin::signed(alice.clone()),
                b"doc-1".to_vec(),
                StorageBackend::Ipfs,
                1024,
                hash,
            )
            .unwrap();
            assert_noop!(
                Storage::register_storage(
                    RuntimeOrigin::signed(alice),
                    b"doc-1".to_vec(),
                    StorageBackend::Ipfs,
                    512,
                    hash,
                ),
                Error::<Test>::RecordAlreadyExists
            );
        });
    }

    #[test]
    fn test_verify_storage() {
        new_test_ext().execute_with(|| {
            let hash = [1u8; 32];
            Storage::register_storage(
                RuntimeOrigin::signed(Sr25519Keyring::Alice.to_account_id()),
                b"doc-1".to_vec(),
                StorageBackend::Ipfs,
                1024,
                hash,
            )
            .unwrap();
            assert_ok!(Storage::verify_storage(
                RuntimeOrigin::signed(Sr25519Keyring::Bob.to_account_id()),
                b"doc-1".to_vec(),
                hash,
            ));
        });
    }

    #[test]
    fn test_register_provider() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            assert_ok!(Storage::register_provider(
                RuntimeOrigin::signed(alice.clone()),
                StorageBackend::Ipfs,
                b"https://pinata.cloud".to_vec(),
            ));
            assert!(StorageProviders::<Test>::contains_key(&alice));
        });
    }
}
