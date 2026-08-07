#![allow(clippy::let_unit_value)]
use crate::{self as pallet_storage, *};
use frame_support::{
    assert_noop, assert_ok, construct_runtime, derive_impl, parameter_types,
    traits::{ConstU16, ConstU32, ConstU64},
    BoundedVec, PalletId,
};
use sp_core::H256;
use sp_runtime::{
    traits::{BlakeTwo256, IdentityLookup},
    BuildStorage, DispatchError,
};

type Block = frame_system::mocking::MockBlock<Test>;

construct_runtime!(
    pub enum Test {
        System: frame_system,
        Storage: pallet_storage,
    }
);

#[derive_impl(frame_system::config_preludes::TestDefaultConfig)]
impl frame_system::Config for Test {
    type BaseCallFilter = frame_support::traits::Everything;
    type BlockWeights = ();
    type BlockLength = ();
    type DbWeight = ();
    type RuntimeOrigin = RuntimeOrigin;
    type RuntimeCall = RuntimeCall;
    type Nonce = u64;
    type Hash = H256;
    type Hashing = BlakeTwo256;
    type AccountId = u64;
    type Lookup = IdentityLookup<Self::AccountId>;
    type Block = Block;
    type RuntimeEvent = RuntimeEvent;
    type BlockHashCount = ConstU64<250>;
    type Version = ();
    type PalletInfo = PalletInfo;
    type AccountData = ();
    type OnNewAccount = ();
    type OnKilledAccount = ();
    type SystemWeightInfo = ();
    type SS58Prefix = ConstU16<42>;
    type OnSetCode = ();
    type MaxConsumers = ConstU32<16>;
}

parameter_types! {
    pub const StoragePalletId: PalletId = PalletId(*b"ver/stor");
    pub const MaxRecords: u32 = 1000;
}

impl pallet_storage::Config for Test {
    type RuntimeEvent = RuntimeEvent;
    type PalletId = StoragePalletId;
    type MaxRecords = MaxRecords;
    type WeightInfo = pallet_storage::SubstrateWeight<Test>;
}

pub fn new_test_ext() -> sp_io::TestExternalities {
    let t = frame_system::GenesisConfig::<Test>::default()
        .build_storage()
        .unwrap();
    let mut ext = sp_io::TestExternalities::new(t);
    ext.execute_with(|| System::set_block_number(1));
    ext
}

fn bv64(bytes: &[u8]) -> BoundedVec<u8, ConstU32<64>> {
    bytes.to_vec().try_into().unwrap()
}

fn dummy_hash() -> [u8; 32] {
    [0xab; 32]
}

// =========================================================================
// register_storage tests
// =========================================================================

#[test]
fn register_storage_ipfs_success() {
    new_test_ext().execute_with(|| {
        let id = b"QmHash123abc".to_vec();
        let hash = dummy_hash();

        assert_ok!(Storage::register_storage(
            RuntimeOrigin::signed(1),
            id.clone(),
            StorageBackend::Ipfs,
            1024,
            hash,
        ));

        // Verify storage
        let record = Storage::get_record(&bv64(&id)).unwrap();
        assert_eq!(record.backend, StorageBackend::Ipfs);
        assert_eq!(record.owner, 1);
        assert_eq!(record.size_bytes, 1024);
        assert_eq!(record.blake3_hash, hash);
        assert!(!record.pinned);

        // Verify total stored
        assert_eq!(Storage::get_total_stored(), 1024);

        // Verify event
        System::assert_last_event(RuntimeEvent::Storage(
            Event::StorageRecordCreated {
                id,
                backend: StorageBackend::Ipfs,
                owner: 1,
                size: 1024,
            }
            .into(),
        ));
    });
}

#[test]
fn register_storage_arweave_success() {
    new_test_ext().execute_with(|| {
        let id = b"arweave-tx-001".to_vec();
        let hash = dummy_hash();

        assert_ok!(Storage::register_storage(
            RuntimeOrigin::signed(2),
            id.clone(),
            StorageBackend::Arweave,
            5_000_000,
            hash,
        ));

        let record = Storage::get_record(&bv64(&id)).unwrap();
        assert_eq!(record.backend, StorageBackend::Arweave);
        assert_eq!(record.owner, 2);
        assert_eq!(record.size_bytes, 5_000_000);
        assert_eq!(Storage::get_total_stored(), 5_000_000);
    });
}

#[test]
fn register_storage_duplicate_fails() {
    new_test_ext().execute_with(|| {
        let id = b"duplicate-id".to_vec();
        let hash = dummy_hash();

        assert_ok!(Storage::register_storage(
            RuntimeOrigin::signed(1),
            id.clone(),
            StorageBackend::Ipfs,
            100,
            hash,
        ));

        assert_noop!(
            Storage::register_storage(
                RuntimeOrigin::signed(2),
                id.clone(),
                StorageBackend::Ipfs,
                200,
                hash,
            ),
            Error::<Test>::RecordAlreadyExists
        );
    });
}

#[test]
fn register_storage_id_too_long_fails() {
    new_test_ext().execute_with(|| {
        let long_id = vec![0u8; 65]; // Max is 64
        let hash = dummy_hash();

        assert_noop!(
            Storage::register_storage(
                RuntimeOrigin::signed(1),
                long_id,
                StorageBackend::Ipfs,
                100,
                hash,
            ),
            Error::<Test>::IdTooLong
        );
    });
}

#[test]
fn register_storage_max_records_reached() {
    new_test_ext().execute_with(|| {
        // MaxRecords = 1000, register 1000 then try one more
        for i in 0..1000u32 {
            let id = format!("id{}", i).into_bytes();
            assert_ok!(Storage::register_storage(
                RuntimeOrigin::signed(1),
                id,
                StorageBackend::Ipfs,
                10,
                dummy_hash(),
            ));
        }

        assert_noop!(
            Storage::register_storage(
                RuntimeOrigin::signed(1),
                b"overflow-id".to_vec(),
                StorageBackend::Ipfs,
                10,
                dummy_hash(),
            ),
            Error::<Test>::MaxRecordsReached
        );
    });
}

#[test]
fn register_storage_accumulates_total() {
    new_test_ext().execute_with(|| {
        assert_ok!(Storage::register_storage(
            RuntimeOrigin::signed(1),
            b"file1".to_vec(),
            StorageBackend::Ipfs,
            500,
            dummy_hash(),
        ));
        assert_ok!(Storage::register_storage(
            RuntimeOrigin::signed(2),
            b"file2".to_vec(),
            StorageBackend::Arweave,
            1500,
            dummy_hash(),
        ));

        assert_eq!(Storage::get_total_stored(), 2000);
    });
}

// =========================================================================
// verify_storage tests
// =========================================================================

#[test]
fn verify_storage_success() {
    new_test_ext().execute_with(|| {
        let id = b"verify-me".to_vec();
        let hash = dummy_hash();

        assert_ok!(Storage::register_storage(
            RuntimeOrigin::signed(1),
            id.clone(),
            StorageBackend::Ipfs,
            100,
            hash,
        ));

        assert_ok!(Storage::verify_storage(
            RuntimeOrigin::signed(2),
            id.clone(),
            hash,
        ));

        System::assert_last_event(RuntimeEvent::Storage(
            Event::StorageRecordVerified { id, hash }.into(),
        ));
    });
}

#[test]
fn verify_storage_wrong_hash_fails() {
    new_test_ext().execute_with(|| {
        let id = b"verify-wrong".to_vec();
        let hash = dummy_hash();
        let wrong_hash = [0xcd; 32];

        assert_ok!(Storage::register_storage(
            RuntimeOrigin::signed(1),
            id.clone(),
            StorageBackend::Ipfs,
            100,
            hash,
        ));

        assert_noop!(
            Storage::verify_storage(RuntimeOrigin::signed(1), id, wrong_hash),
            Error::<Test>::InvalidHash
        );
    });
}

#[test]
fn verify_storage_not_found_fails() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            Storage::verify_storage(
                RuntimeOrigin::signed(1),
                b"nonexistent".to_vec(),
                dummy_hash(),
            ),
            Error::<Test>::RecordNotFound
        );
    });
}

#[test]
fn verify_storage_id_too_long_fails() {
    new_test_ext().execute_with(|| {
        let long_id = vec![0u8; 65];

        assert_noop!(
            Storage::verify_storage(RuntimeOrigin::signed(1), long_id, dummy_hash()),
            Error::<Test>::IdTooLong
        );
    });
}

// =========================================================================
// register_provider tests
// =========================================================================

#[test]
fn register_provider_ipfs_success() {
    new_test_ext().execute_with(|| {
        let endpoint = b"https://ipfs.gateway.io".to_vec();

        assert_ok!(Storage::register_provider(
            RuntimeOrigin::signed(1),
            StorageBackend::Ipfs,
            endpoint.clone(),
        ));

        let provider = Storage::get_provider(&1).unwrap();
        assert_eq!(provider.backend, StorageBackend::Ipfs);
        assert_eq!(provider.reputation, 100);
        assert_eq!(provider.total_stored, 0);
        assert!(provider.active);

        System::assert_last_event(RuntimeEvent::Storage(
            Event::ProviderRegistered {
                address: 1,
                backend: StorageBackend::Ipfs,
                endpoint,
            }
            .into(),
        ));
    });
}

#[test]
fn register_provider_arweave_success() {
    new_test_ext().execute_with(|| {
        let endpoint = b"https://arweave.net".to_vec();

        assert_ok!(Storage::register_provider(
            RuntimeOrigin::signed(2),
            StorageBackend::Arweave,
            endpoint.clone(),
        ));

        let provider = Storage::get_provider(&2).unwrap();
        assert_eq!(provider.backend, StorageBackend::Arweave);
        assert!(provider.active);
    });
}

#[test]
fn register_provider_duplicate_fails() {
    new_test_ext().execute_with(|| {
        let endpoint = b"https://gw.io".to_vec();

        assert_ok!(Storage::register_provider(
            RuntimeOrigin::signed(1),
            StorageBackend::Ipfs,
            endpoint.clone(),
        ));

        assert_noop!(
            Storage::register_provider(
                RuntimeOrigin::signed(1),
                StorageBackend::Arweave,
                b"https://other.io".to_vec(),
            ),
            Error::<Test>::ProviderAlreadyRegistered
        );
    });
}

#[test]
fn register_provider_endpoint_too_long_fails() {
    new_test_ext().execute_with(|| {
        let long_endpoint = vec![0u8; 129]; // Max is 128

        assert_noop!(
            Storage::register_provider(
                RuntimeOrigin::signed(1),
                StorageBackend::Ipfs,
                long_endpoint,
            ),
            Error::<Test>::EndpointTooLong
        );
    });
}

#[test]
fn register_provider_default_reputation() {
    new_test_ext().execute_with(|| {
        assert_ok!(Storage::register_provider(
            RuntimeOrigin::signed(1),
            StorageBackend::Ipfs,
            b"https://gw.io".to_vec(),
        ));

        let provider = Storage::get_provider(&1).unwrap();
        assert_eq!(provider.reputation, 100);
        assert_eq!(provider.total_stored, 0);
        assert!(provider.active);
    });
}

// =========================================================================
// request_pin tests
// =========================================================================

#[test]
fn request_pin_success() {
    new_test_ext().execute_with(|| {
        let id = b"pin-me".to_vec();
        assert_ok!(Storage::register_storage(
            RuntimeOrigin::signed(1),
            id.clone(),
            StorageBackend::Ipfs,
            100,
            dummy_hash(),
        ));

        assert_ok!(Storage::request_pin(
            RuntimeOrigin::signed(2),
            id.clone(),
        ));

        // Verify pinned flag
        let record = Storage::get_record(&bv64(&id)).unwrap();
        assert!(record.pinned);

        // Verify pin request
        assert!(PinRequests::<Test>::get(&bv64(&id)));

        System::assert_last_event(RuntimeEvent::Storage(
            Event::PinRequested { id }.into(),
        ));
    });
}

#[test]
fn request_pin_record_not_found_fails() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            Storage::request_pin(RuntimeOrigin::signed(1), b"no-exist".to_vec()),
            Error::<Test>::RecordNotFound
        );
    });
}

#[test]
fn request_pin_id_too_long_fails() {
    new_test_ext().execute_with(|| {
        let long_id = vec![0u8; 65];

        assert_noop!(
            Storage::request_pin(RuntimeOrigin::signed(1), long_id),
            Error::<Test>::IdTooLong
        );
    });
}

// =========================================================================
// remove_pin tests
// =========================================================================

#[test]
fn remove_pin_success() {
    new_test_ext().execute_with(|| {
        let id = b"pin-removable".to_vec();
        assert_ok!(Storage::register_storage(
            RuntimeOrigin::signed(1),
            id.clone(),
            StorageBackend::Ipfs,
            100,
            dummy_hash(),
        ));
        assert_ok!(Storage::request_pin(
            RuntimeOrigin::signed(2),
            id.clone(),
        ));

        // Owner removes pin
        assert_ok!(Storage::remove_pin(
            RuntimeOrigin::signed(1),
            id.clone(),
        ));

        let record = Storage::get_record(&bv64(&id)).unwrap();
        assert!(!record.pinned);
        assert!(!PinRequests::<Test>::get(&bv64(&id)));

        System::assert_last_event(RuntimeEvent::Storage(
            Event::PinRemoved { id }.into(),
        ));
    });
}

#[test]
fn remove_pin_not_owner_fails() {
    new_test_ext().execute_with(|| {
        let id = b"pin-protected".to_vec();
        assert_ok!(Storage::register_storage(
            RuntimeOrigin::signed(1),
            id.clone(),
            StorageBackend::Ipfs,
            100,
            dummy_hash(),
        ));
        assert_ok!(Storage::request_pin(
            RuntimeOrigin::signed(2),
            id.clone(),
        ));

        assert_noop!(
            Storage::remove_pin(RuntimeOrigin::signed(3), id),
            Error::<Test>::NotRecordOwner
        );
    });
}

#[test]
fn remove_pin_record_not_found_fails() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            Storage::remove_pin(RuntimeOrigin::signed(1), b"ghost".to_vec()),
            Error::<Test>::RecordNotFound
        );
    });
}

#[test]
fn remove_pin_id_too_long_fails() {
    new_test_ext().execute_with(|| {
        let long_id = vec![0u8; 65];

        assert_noop!(
            Storage::remove_pin(RuntimeOrigin::signed(1), long_id),
            Error::<Test>::IdTooLong
        );
    });
}

// =========================================================================
// Query function tests
// =========================================================================

#[test]
fn get_record_returns_none_for_missing() {
    new_test_ext().execute_with(|| {
        assert!(Storage::get_record(&bv64(b"missing")).is_none());
    });
}

#[test]
fn get_provider_returns_none_for_missing() {
    new_test_ext().execute_with(|| {
        assert!(Storage::get_provider(&999).is_none());
    });
}

#[test]
fn get_total_stored_starts_zero() {
    new_test_ext().execute_with(|| {
        assert_eq!(Storage::get_total_stored(), 0);
    });
}

#[test]
fn get_all_providers_empty_initially() {
    new_test_ext().execute_with(|| {
        assert!(Storage::get_all_providers().is_empty());
    });
}

#[test]
fn get_all_providers_returns_registered() {
    new_test_ext().execute_with(|| {
        assert_ok!(Storage::register_provider(
            RuntimeOrigin::signed(1),
            StorageBackend::Ipfs,
            b"https://a.io".to_vec(),
        ));
        assert_ok!(Storage::register_provider(
            RuntimeOrigin::signed(2),
            StorageBackend::Arweave,
            b"https://b.io".to_vec(),
        ));

        let providers = Storage::get_all_providers();
        assert_eq!(providers.len(), 2);
    });
}

// =========================================================================
// Edge case tests
// =========================================================================

#[test]
fn register_storage_zero_size_succeeds() {
    new_test_ext().execute_with(|| {
        assert_ok!(Storage::register_storage(
            RuntimeOrigin::signed(1),
            b"empty".to_vec(),
            StorageBackend::Ipfs,
            0,
            dummy_hash(),
        ));
        assert_eq!(Storage::get_total_stored(), 0);
    });
}

#[test]
fn register_storage_max_id_length_succeeds() {
    new_test_ext().execute_with(|| {
        let max_id = vec![0u8; 64]; // Exactly 64, should succeed

        assert_ok!(Storage::register_storage(
            RuntimeOrigin::signed(1),
            max_id,
            StorageBackend::Ipfs,
            100,
            dummy_hash(),
        ));
    });
}

#[test]
fn register_provider_max_endpoint_succeeds() {
    new_test_ext().execute_with(|| {
        let max_endpoint = vec![0u8; 128]; // Exactly 128, should succeed

        assert_ok!(Storage::register_provider(
            RuntimeOrigin::signed(1),
            StorageBackend::Ipfs,
            max_endpoint,
        ));
    });
}

#[test]
fn multiple_records_different_owners() {
    new_test_ext().execute_with(|| {
        for i in 0..5u64 {
            let id = format!("file-{}", i).into_bytes();
            assert_ok!(Storage::register_storage(
                RuntimeOrigin::signed(i),
                id,
                StorageBackend::Ipfs,
                (i + 1) * 100,
                dummy_hash(),
            ));
        }

        assert_eq!(Storage::get_total_stored(), 100 + 200 + 300 + 400 + 500);
    });
}

#[test]
fn pin_unpin_lifecycle() {
    new_test_ext().execute_with(|| {
        let id = b"lifecycle".to_vec();

        // Register
        assert_ok!(Storage::register_storage(
            RuntimeOrigin::signed(1),
            id.clone(),
            StorageBackend::Ipfs,
            256,
            dummy_hash(),
        ));

        // Pin
        assert_ok!(Storage::request_pin(
            RuntimeOrigin::signed(2),
            id.clone(),
        ));
        assert!(Storage::get_record(&bv64(&id)).unwrap().pinned);

        // Unpin
        assert_ok!(Storage::remove_pin(
            RuntimeOrigin::signed(1),
            id.clone(),
        ));
        assert!(!Storage::get_record(&bv64(&id)).unwrap().pinned);

        // Re-pin
        assert_ok!(Storage::request_pin(
            RuntimeOrigin::signed(3),
            id,
        ));
        assert!(Storage::get_record(&bv64(b"lifecycle")).unwrap().pinned);
    });
}


// ==================== REAL BENCHMARK WEIGHT GENERATION ====================
#[cfg(feature = "runtime-benchmarks")]
mod real_bench {
    use super::*;
    use super::{Test, new_test_ext};
    use std::time::Instant;
    use frame_support::traits::fungible::Mutate;

    fn measure_bench<F: FnMut() -> bool>(name: &str, iters: u32, mut f: F) -> u64 {
        let mut times: Vec<u64> = Vec::new();
        for _ in 0..iters {
            let start = Instant::now();
            let ok = f();
            let elapsed = start.elapsed().as_nanos() as u64;
            if ok { times.push(elapsed); }
        }
        if times.is_empty() {
            println!("  {pallet}::{name} -> FAILED", pallet = PALLET_NAME, name = name);
            return 10_000;
        }
        let avg = times.iter().sum::<u64>() / times.len() as u64;
        let max = *times.iter().max().unwrap();
        let weight = (avg as f64 * 1.25).max(10000.0) as u64;
        println!("  {pallet}::{name} -> avg={avg}ns max={max}ns weight={weight}", pallet = PALLET_NAME, name = name, avg = avg, max = max, weight = weight);
        weight
    }

    const PALLET_NAME: &str = "storage";

    #[test]
    #[ignore]
    fn real_bench() {
        new_test_ext().execute_with(|| {{
            use frame_system::Pallet as System;
            System::<Test>::set_block_number(1);
            
            let mut results: Vec<(&str, u64)> = Vec::new();

            // Benchmark: register_provider
            let mut idx = 0u64;
            let w = measure_bench("register_provider", 50, || {
                idx += 1;
                Storage::register_provider(RuntimeOrigin::signed(idx), crate::StorageBackend::Ipfs, b"https://ipfs.io".to_vec()).is_ok()
            });
            results.push(("register_provider", w));

            // Benchmark: register_storage
            let mut sidx = 0u64;
            let w = measure_bench("register_storage", 50, || {
                sidx += 1;
                let id = format!("rec_{}", sidx).into_bytes();
                Storage::register_storage(RuntimeOrigin::signed(1), id, crate::StorageBackend::Ipfs, 1024, [0xab; 32]).is_ok()
            });
            results.push(("register_storage", w));

            // Benchmark: verify_storage (root only)
            assert_ok!(Storage::register_storage(RuntimeOrigin::signed(1), b"rec_v".to_vec(), crate::StorageBackend::Ipfs, 1024, [0xcd; 32]));
            let w = measure_bench("verify_storage", 50, || {
                Storage::verify_storage(RuntimeOrigin::root(), b"rec_v".to_vec(), [0xcd; 32]).is_ok()
            });
            results.push(("verify_storage", w));

            println!("\n//! WeightInfo for pallet-storage (real benchmark)");
            println!("pub struct WeightInfo;");
            for (name, weight) in &results {
                println!("// {}: {} weight units", name, weight);
            }

        }});
    }
}
