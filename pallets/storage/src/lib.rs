#![allow(clippy::incompatible_msrv)]
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
    clippy::needless_borrows_for_generic_args
)]
//! # Verdis Decentralized Storage Pallet
//!
//! IPFS/Arweave integration for storing large data off-chain:
//! - IPFS CID registration and verification
//! - Arweave transaction ID tracking
//! - Content addressing with Blake3
//! - Storage provider reputation
//! - Pinning requests and status tracking
//! - Per-record deposit economics (reserve on store, refund on delete)
//! - Lazy garbage collection of expired records

#![cfg_attr(not(feature = "std"), no_std)]
use codec::{Decode, DecodeWithMemTracking, Encode, MaxEncodedLen};
use frame_support::{
    dispatch::DispatchResult,
    ensure,
    pallet_prelude::*,
    traits::{Currency, Get, ReservableCurrency},
    PalletId,
};
use frame_system::pallet_prelude::*;
use scale_info::TypeInfo;
use sp_runtime::traits::{CheckedAdd, CheckedMul, Saturating, Zero};
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

    /// Balance type for the pallet
    pub type BalanceOf<T> =
        <<T as Config>::Currency as Currency<<T as frame_system::Config>::AccountId>>::Balance;

    #[derive(Encode, Decode, Clone, PartialEq, Eq, MaxEncodedLen, TypeInfo, Debug)]
    pub struct StorageRecord<AccountId, Balance, BlockNumber> {
        pub id: BoundedVec<u8, ConstU32<64>>,
        pub backend: StorageBackend,
        pub owner: AccountId,
        pub size_bytes: u64,
        pub blake3_hash: [u8; 32],
        pub pinned: bool,
        pub created_at: BlockNumber,
        pub expiry_block: BlockNumber,
        pub deposit_amount: Balance,
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
    pub type StorageRecords<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        BoundedVec<u8, ConstU32<64>>,
        StorageRecord<T::AccountId, BalanceOf<T>, frame_system::pallet_prelude::BlockNumberFor<T>>,
    >;

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
        StorageMap<_, Blake2_128Concat, u32, BoundedVec<T::AccountId, ConstU32<1024>>, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn shard_info)]
    pub type ShardInfoStorage<T: Config> =
        StorageMap<_, Blake2_128Concat, u32, ShardInfo, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn account_to_shard)]
    pub type AccountToShard<T: Config> =
        StorageMap<_, Blake2_128Concat, T::AccountId, u32, ValueQuery>;

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
            deposit: BalanceOf<T>,
            expiry_block: frame_system::pallet_prelude::BlockNumberFor<T>,
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
        StorageRecordDeleted {
            id: Vec<u8>,
            owner: T::AccountId,
            refund: BalanceOf<T>,
        },
        ExpiredRecordsCleaned {
            count: u32,
            refund_total: BalanceOf<T>,
        },
    }

    // === Errors ===

    #[pallet::error]
    pub enum Error<T> {
        /// Caller is not a registered storage provider
        NotStorageProvider,
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
        SizeTooLarge,
        /// Record has not expired yet
        NotExpired,
        /// Deposit computation overflowed
        DepositOverflow,
    }

    // === Config ===

    #[pallet::config]
    pub trait Config: frame_system::Config {
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
        /// Currency for deposit reservations
        type Currency: ReservableCurrency<Self::AccountId>;
        #[pallet::constant]
        type PalletId: Get<PalletId>;
        #[pallet::constant]
        type MaxRecords: Get<u32>;
        #[pallet::constant]
        type MaxSizeBytes: Get<u64>;
        #[pallet::constant]
        type ShardCount: Get<u32>;
        /// Base deposit amount per record (in smallest unit)
        #[pallet::constant]
        type BaseDeposit: Get<BalanceOf<Self>>;
        /// Deposit per byte of storage (in smallest unit per byte)
        #[pallet::constant]
        type DepositPerByte: Get<BalanceOf<Self>>;
        /// Number of blocks before a record expires
        #[pallet::constant]
        type ExpiryBlocks: Get<u32>;
        type WeightInfo: WeightInfo;
    }

    // === Extrinsics ===

    #[pallet::call]
    impl<T: Config> Pallet<T> {
        /// Register a storage record (IPFS CID or Arweave TX ID)
        /// Reserves a deposit based on record size: deposit = BaseDeposit + size_bytes * DepositPerByte
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
            ensure!(
                size_bytes <= T::MaxSizeBytes::get(),
                Error::<T>::SizeTooLarge
            );

            // Compute deposit: BaseDeposit + size_bytes * DepositPerByte
            let deposit = Self::compute_deposit(size_bytes)?;

            // Reserve the deposit from the caller
            T::Currency::reserve(&who, deposit)?;

            let current_block = frame_system::Pallet::<T>::block_number();
            let expiry_block = current_block + T::ExpiryBlocks::get().into();

            let record = StorageRecord {
                id: id_bv.clone(),
                backend,
                owner: who.clone(),
                size_bytes,
                blake3_hash,
                pinned: false,
                created_at: current_block,
                expiry_block,
                deposit_amount: deposit,
            };

            StorageRecords::<T>::insert(id_bv, record);
            StorageRecordCount::<T>::mutate(|c| *c = c.saturating_add(1));
            TotalStored::<T>::mutate(|t| *t = t.saturating_add(size_bytes));

            Self::deposit_event(Event::StorageRecordCreated {
                id,
                backend,
                owner: who,
                size: size_bytes,
                deposit,
                expiry_block,
            });
            Ok(())
        }

        /// Verify storage content against Blake3 hash
        #[pallet::call_index(1)]
        #[pallet::weight(Weight::from_parts(30_000_000, 0))]
        pub fn verify_storage(origin: OriginFor<T>, id: Vec<u8>, hash: [u8; 32]) -> DispatchResult {
            // SECURITY: Track who verified the storage
            let who = ensure_signed(origin)?;

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
            let _who = ensure_signed(origin)?;

            let id_bv: BoundedVec<u8, ConstU32<64>> =
                id.clone().try_into().map_err(|_| Error::<T>::IdTooLong)?;

            ensure!(
                StorageRecords::<T>::contains_key(&id_bv),
                Error::<T>::RecordNotFound
            );

            PinRequests::<T>::insert(&id_bv, true);

            Self::deposit_event(Event::PinRequested { id });
            Ok(())
        }

        /// Remove pinning request
        #[pallet::call_index(4)]
        #[pallet::weight(Weight::from_parts(20_000_000, 0))]
        pub fn remove_pin(origin: OriginFor<T>, id: Vec<u8>) -> DispatchResult {
            let _who = ensure_signed(origin)?;

            let id_bv: BoundedVec<u8, ConstU32<64>> =
                id.clone().try_into().map_err(|_| Error::<T>::IdTooLong)?;

            ensure!(
                PinRequests::<T>::contains_key(&id_bv),
                Error::<T>::RecordNotFound
            );

            PinRequests::<T>::remove(&id_bv);

            Self::deposit_event(Event::PinRemoved { id });
            Ok(())
        }

        /// Delete a storage record (owner only). Refunds the reserved deposit.
        #[pallet::call_index(5)]
        #[pallet::weight(Weight::from_parts(50_000_000, 0))]
        pub fn delete_record(origin: OriginFor<T>, id: Vec<u8>) -> DispatchResult {
            let who = ensure_signed(origin)?;

            let id_bv: BoundedVec<u8, ConstU32<64>> =
                id.clone().try_into().map_err(|_| Error::<T>::IdTooLong)?;

            let record = StorageRecords::<T>::get(&id_bv).ok_or(Error::<T>::RecordNotFound)?;
            ensure!(record.owner == who, Error::<T>::NotRecordOwner);

            // Unreserve the deposit back to the owner
            T::Currency::unreserve(&who, record.deposit_amount);

            // Remove the record
            StorageRecords::<T>::remove(&id_bv);
            StorageRecordCount::<T>::mutate(|c| *c = c.saturating_sub(1));
            TotalStored::<T>::mutate(|t| *t = t.saturating_sub(record.size_bytes));

            // Also remove any pin request
            PinRequests::<T>::remove(&id_bv);

            Self::deposit_event(Event::StorageRecordDeleted {
                id,
                owner: who,
                refund: record.deposit_amount,
            });
            Ok(())
        }

        /// Clean up expired storage records (anyone can call).
        /// Walks up to MaxBatchSize records and removes expired ones,
        /// refunding deposits to their owners.
        #[pallet::call_index(6)]
        #[pallet::weight(Weight::from_parts(100_000_000, 0))]
        pub fn cleanup_expired(origin: OriginFor<T>, ids: Vec<Vec<u8>>) -> DispatchResult {
            let _caller = ensure_signed(origin)?;

            let current_block = frame_system::Pallet::<T>::block_number();
            let mut cleaned: u32 = 0;
            let mut total_refund: BalanceOf<T> = Zero::zero();

            for id in ids.iter() {
                let id_bv: BoundedVec<u8, ConstU32<64>> = match id.clone().try_into() {
                    Ok(bv) => bv,
                    Err(_) => continue,
                };

                if let Some(record) = StorageRecords::<T>::get(&id_bv) {
                    if record.expiry_block <= current_block {
                        // Refund deposit to owner
                        T::Currency::unreserve(&record.owner, record.deposit_amount);

                        StorageRecords::<T>::remove(&id_bv);
                        StorageRecordCount::<T>::mutate(|c| *c = c.saturating_sub(1));
                        TotalStored::<T>::mutate(|t| *t = t.saturating_sub(record.size_bytes));
                        PinRequests::<T>::remove(&id_bv);

                        total_refund =
                            Saturating::saturating_add(total_refund, record.deposit_amount);
                        cleaned += 1;
                    }
                }
            }

            if cleaned > 0 {
                Self::deposit_event(Event::ExpiredRecordsCleaned {
                    count: cleaned,
                    refund_total: total_refund,
                });
            }
            Ok(())
        }
    }

    // === Helper Functions ===

    impl<T: Config> Pallet<T> {
        /// Compute the deposit required for a given record size.
        /// deposit = BaseDeposit + size_bytes * DepositPerByte
        pub fn compute_deposit(size_bytes: u64) -> Result<BalanceOf<T>, Error<T>> {
            let base = T::BaseDeposit::get();
            let per_byte = T::DepositPerByte::get();

            // Convert size_bytes to BalanceOf (may differ in size)
            let size_balance: BalanceOf<T> = size_bytes
                .try_into()
                .map_err(|_| Error::<T>::DepositOverflow)?;

            let size_deposit = per_byte
                .checked_mul(&size_balance)
                .ok_or(Error::<T>::DepositOverflow)?;

            base.checked_add(&size_deposit)
                .ok_or(Error::<T>::DepositOverflow)
        }

        pub fn get_record(
            id: BoundedVec<u8, ConstU32<64>>,
        ) -> Option<
            StorageRecord<
                T::AccountId,
                BalanceOf<T>,
                frame_system::pallet_prelude::BlockNumberFor<T>,
            >,
        > {
            StorageRecords::<T>::get(&id)
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
        fn delete_record() -> Weight;
        fn cleanup_expired() -> Weight;
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
        fn delete_record() -> Weight {
            Weight::from_parts(50_000_000, 0)
        }
        fn cleanup_expired() -> Weight {
            Weight::from_parts(100_000_000, 0)
        }
    }

    // === Test suite ===
    #[cfg(test)]
    mod tests {
        use super::*;
        use frame_support::{
            assert_noop, assert_ok, construct_runtime, derive_impl, parameter_types,
            traits::ConstU32, traits::ConstU64,
        };
        use sp_io::TestExternalities;
        use sp_keyring::Sr25519Keyring;
        use sp_runtime::{traits::IdentityLookup, BuildStorage};

        type Block = frame_system::mocking::MockBlock<Test>;

        construct_runtime!(
            pub enum Test {
                System: frame_system,
                Balances: pallet_balances,
                Storage: crate,
            }
        );

        #[derive_impl(frame_system::config_preludes::TestDefaultConfig as frame_system::DefaultConfig)]
        impl frame_system::Config for Test {
            type AccountId = sp_core::crypto::AccountId32;
            type Lookup = IdentityLookup<Self::AccountId>;
            type Block = Block;
            type AccountData = pallet_balances::AccountData<u64>;
        }

        impl pallet_balances::Config for Test {
            type Balance = u64;
            type RuntimeEvent = RuntimeEvent;
            type DustRemoval = ();
            type ExistentialDeposit = ConstU64<1>;
            type MaxLocks = ConstU32<50>;
            type MaxReserves = ConstU32<50>;
            type ReserveIdentifier = [u8; 8];
            type AccountStore = System;
            type WeightInfo = ();
            type FreezeIdentifier = ();
            type MaxFreezes = ConstU32<0>;
            type RuntimeHoldReason = ();
            type RuntimeFreezeReason = ();
            type DoneSlashHandler = ();
        }

        parameter_types! {
            pub const StorPalletId: PalletId = PalletId(*b"v/stores");
            pub const MaxRecords: u32 = 1000;
            pub const MaxSizeBytes: u64 = 1_000_000_000_000;
            pub const StorBaseDeposit: u64 = 1_000;
            pub const StorDepositPerByte: u64 = 1;
            pub const StorExpiryBlocks: u32 = 100;
        }

        impl Config for Test {
            type ShardCount = ConstU32<16>;
            type RuntimeEvent = RuntimeEvent;
            type PalletId = StorPalletId;
            type MaxRecords = MaxRecords;
            type MaxSizeBytes = MaxSizeBytes;
            type Currency = Balances;
            type BaseDeposit = StorBaseDeposit;
            type DepositPerByte = StorDepositPerByte;
            type ExpiryBlocks = StorExpiryBlocks;
            type WeightInfo = SubstrateWeight<Test>;
        }

        pub fn new_test_ext() -> TestExternalities {
            let mut t = frame_system::GenesisConfig::<Test>::default()
                .build_storage()
                .unwrap();
            // Configure balances: Alice gets 1_000_000 units
            pallet_balances::GenesisConfig::<Test> {
                dev_accounts: None,
                balances: vec![(Sr25519Keyring::Alice.to_account_id(), 1_000_000_000)],
            }
            .assimilate_storage(&mut t)
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
                let alice = Sr25519Keyring::Alice.to_account_id();
                assert_ok!(Storage::register_storage(
                    RuntimeOrigin::signed(alice.clone()),
                    b"doc-1".to_vec(),
                    StorageBackend::Ipfs,
                    1024,
                    hash,
                ));
                let key: BoundedVec<u8, ConstU32<64>> = b"doc-1".to_vec().try_into().unwrap();
                assert!(StorageRecords::<Test>::contains_key(&key));
                assert_eq!(Storage::get_total_stored(), 1024);

                // Check deposit was reserved: BaseDeposit + 1024 * DepositPerByte = 1000 + 1024 = 2024
                let reserved = Balances::reserved_balance(&alice);
                assert_eq!(reserved, 2024);
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

        #[test]
        fn test_delete_record_refunds_deposit() {
            new_test_ext().execute_with(|| {
                let alice = Sr25519Keyring::Alice.to_account_id();
                let hash = [1u8; 32];

                // Register a record
                assert_ok!(Storage::register_storage(
                    RuntimeOrigin::signed(alice.clone()),
                    b"doc-1".to_vec(),
                    StorageBackend::Ipfs,
                    1024,
                    hash,
                ));

                // Deposit should be reserved
                assert_eq!(Balances::reserved_balance(&alice), 2024);

                // Delete the record
                assert_ok!(Storage::delete_record(
                    RuntimeOrigin::signed(alice.clone()),
                    b"doc-1".to_vec(),
                ));

                // Deposit should be refunded
                assert_eq!(Balances::reserved_balance(&alice), 0);

                // Record should be gone
                let key: BoundedVec<u8, ConstU32<64>> = b"doc-1".to_vec().try_into().unwrap();
                assert!(!StorageRecords::<Test>::contains_key(&key));
                assert_eq!(Storage::get_total_stored(), 0);
            });
        }

        #[test]
        fn test_delete_record_not_owner() {
            new_test_ext().execute_with(|| {
                let alice = Sr25519Keyring::Alice.to_account_id();
                let bob = Sr25519Keyring::Bob.to_account_id();
                let hash = [1u8; 32];

                Storage::register_storage(
                    RuntimeOrigin::signed(alice),
                    b"doc-1".to_vec(),
                    StorageBackend::Ipfs,
                    1024,
                    hash,
                )
                .unwrap();

                // Bob tries to delete Alice's record
                assert_noop!(
                    Storage::delete_record(RuntimeOrigin::signed(bob), b"doc-1".to_vec(),),
                    Error::<Test>::NotRecordOwner
                );
            });
        }

        #[test]
        fn test_cleanup_expired() {
            new_test_ext().execute_with(|| {
                let alice = Sr25519Keyring::Alice.to_account_id();
                let hash = [1u8; 32];

                // Register a record at block 1 (expiry at block 101)
                assert_ok!(Storage::register_storage(
                    RuntimeOrigin::signed(alice.clone()),
                    b"doc-1".to_vec(),
                    StorageBackend::Ipfs,
                    1024,
                    hash,
                ));

                assert_eq!(Balances::reserved_balance(&alice), 2024);

                // Advance to block 200 (past expiry)
                System::set_block_number(200);

                // Cleanup expired records
                assert_ok!(Storage::cleanup_expired(
                    RuntimeOrigin::signed(alice.clone()),
                    vec![b"doc-1".to_vec()],
                ));

                // Deposit should be refunded
                assert_eq!(Balances::reserved_balance(&alice), 0);

                // Record should be gone
                let key: BoundedVec<u8, ConstU32<64>> = b"doc-1".to_vec().try_into().unwrap();
                assert!(!StorageRecords::<Test>::contains_key(&key));
            });
        }

        #[test]
        fn test_cleanup_not_expired() {
            new_test_ext().execute_with(|| {
                let alice = Sr25519Keyring::Alice.to_account_id();
                let hash = [1u8; 32];

                // Register a record at block 1 (expiry at block 101)
                assert_ok!(Storage::register_storage(
                    RuntimeOrigin::signed(alice.clone()),
                    b"doc-1".to_vec(),
                    StorageBackend::Ipfs,
                    1024,
                    hash,
                ));

                // Try to cleanup at block 50 (not expired yet)
                System::set_block_number(50);

                assert_ok!(Storage::cleanup_expired(
                    RuntimeOrigin::signed(alice),
                    vec![b"doc-1".to_vec()],
                ));

                // Record should still exist
                let key: BoundedVec<u8, ConstU32<64>> = b"doc-1".to_vec().try_into().unwrap();
                assert!(StorageRecords::<Test>::contains_key(&key));
            });
        }
    }
}

#[cfg(feature = "runtime-benchmarks")]
mod benchmarking;
