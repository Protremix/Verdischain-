//! Unit tests for pallet-poh

use crate::*;
use frame_support::{assert_noop, assert_ok, construct_runtime, derive_impl};
use sp_io::TestExternalities;
use sp_runtime::{traits::IdentityLookup, BuildStorage, DispatchError};

type Block = frame_system::mocking::MockBlock<Test>;

construct_runtime!(
    pub enum Test {
        System: frame_system,
        Poh: crate,
    }
);

#[derive_impl(frame_system::config_preludes::TestDefaultConfig as frame_system::DefaultConfig)]
impl frame_system::Config for Test {
    type AccountId = sp_core::crypto::AccountId32;
    type Lookup = IdentityLookup<Self::AccountId>;
    type Block = Block;
}

impl Config for Test {}

pub fn new_test_ext() -> TestExternalities {
    let t = frame_system::GenesisConfig::<Test>::default()
        .build_storage()
        .unwrap();
    let mut ext = TestExternalities::new(t);
    ext.execute_with(|| System::set_block_number(1));
    ext
}

#[allow(dead_code)]
fn alice() -> sp_core::crypto::AccountId32 {
    sp_keyring::Sr25519Keyring::Alice.to_account_id()
}

#[test]
fn initial_state_is_empty() {
    new_test_ext().execute_with(|| {
        assert_eq!(PohTick::<Test>::get(), 0);
        let config = PohConfigVal::<Test>::get();
        assert_eq!(config.tick_count, 0);
        assert_eq!(config.seed, [0u8; 32]);
        assert_eq!(config.last_hash, [0u8; 32]);
        assert_eq!(Poh::get_poh_hash(1), None);
    });
}

#[test]
fn tick_generates_vdf_hash() {
    new_test_ext().execute_with(|| {
        let h1 = Poh::tick();
        assert_eq!(PohTick::<Test>::get(), 1);

        // Expected calculation: sha256(last_hash=0 || seed=0 || tick_count=1)
        let expected = Poh::calculate_hash(&[0u8; 32], &[0u8; 32], 1);
        assert_eq!(h1, expected);

        let config = PohConfigVal::<Test>::get();
        assert_eq!(config.tick_count, 1);
        assert_eq!(config.last_hash, h1);

        // Second tick
        let h2 = Poh::tick();
        assert_eq!(PohTick::<Test>::get(), 2);
        let expected2 = Poh::calculate_hash(&h1, &[0u8; 32], 2);
        assert_eq!(h2, expected2);
        assert_ne!(h1, h2);
    });
}

#[test]
fn record_block_works() {
    new_test_ext().execute_with(|| {
        System::set_block_number(1);
        assert_ok!(Poh::record_block(frame_system::RawOrigin::Root.into()));

        let hash1 = Poh::get_poh_hash(1).unwrap();
        assert_eq!(PohTick::<Test>::get(), 1);

        System::set_block_number(2);
        assert_ok!(Poh::record_block(frame_system::RawOrigin::Root.into()));

        let hash2 = Poh::get_poh_hash(2).unwrap();
        assert_eq!(PohTick::<Test>::get(), 2);
        assert_ne!(hash1, hash2);
    });
}

#[test]
fn verify_poh_works() {
    new_test_ext().execute_with(|| {
        System::set_block_number(1);
        assert_ok!(Poh::record_block(frame_system::RawOrigin::Root.into()));

        System::set_block_number(2);
        assert_ok!(Poh::record_block(frame_system::RawOrigin::Root.into()));

        System::set_block_number(3);
        assert_ok!(Poh::record_block(frame_system::RawOrigin::Root.into()));

        assert!(Poh::verify_poh(1, 3));
        assert!(Poh::verify_poh(1, 2));
        assert!(Poh::verify_poh(2, 3));

        // Block 4 not stamped yet
        assert!(!Poh::verify_poh(1, 4));

        // Invalid range
        assert!(!Poh::verify_poh(3, 1));
    });
}

#[test]
fn set_config_works() {
    new_test_ext().execute_with(|| {
        let seed = [7u8; 32];
        let last_hash = [9u8; 32];

        assert_ok!(Poh::set_config(frame_system::RawOrigin::Root.into(), seed, last_hash));

        let config = PohConfigVal::<Test>::get();
        assert_eq!(config.seed, seed);
        assert_eq!(config.last_hash, last_hash);

        let new_hash = Poh::tick();
        let expected = Poh::calculate_hash(&last_hash, &seed, 1);
        assert_eq!(new_hash, expected);
    });
}

#[test]
fn tick_extrinsic_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(Poh::tick_extrinsic(frame_system::RawOrigin::Root.into()));
        assert_eq!(PohTick::<Test>::get(), 1);
    });
}

#[test]
fn record_block_non_root_rejected() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            Poh::record_block(frame_system::RawOrigin::Signed(alice()).into()),
            DispatchError::BadOrigin
        );
    });
}

#[test]
fn set_config_non_root_rejected() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            Poh::set_config(frame_system::RawOrigin::Signed(alice()).into(), [1u8; 32], [2u8; 32]),
            DispatchError::BadOrigin
        );
    });
}

#[test]
fn tick_extrinsic_non_root_rejected() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            Poh::tick_extrinsic(frame_system::RawOrigin::Signed(alice()).into()),
            DispatchError::BadOrigin
        );
    });
}

#[test]
fn verify_poh_invalid_range_returns_false() {
    new_test_ext().execute_with(|| {
        assert!(!Poh::verify_poh(5, 1));
    });
}
