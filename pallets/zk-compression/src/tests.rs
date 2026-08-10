use crate::*;
use frame_support::{assert_ok, construct_runtime, derive_impl, parameter_types};
use sp_io::TestExternalities;
use sp_runtime::{traits::IdentityLookup, BuildStorage};

type Block = frame_system::mocking::MockBlock<Test>;

construct_runtime!(
    pub enum Test {
        System: frame_system,
        ZkCompression: crate,
    }
);

#[derive_impl(frame_system::config_preludes::TestDefaultConfig as frame_system::DefaultConfig)]
impl frame_system::Config for Test {
    type AccountId = sp_core::crypto::AccountId32;
    type Lookup = IdentityLookup<Self::AccountId>;
    type Block = Block;
}

parameter_types! {
    pub const MaxLeaves: u32 = 1024;
    pub const MaxDepth: u32 = 20;
}

impl Config for Test {
    type MaxLeaves = MaxLeaves;
    type MaxDepth = MaxDepth;
}

pub fn new_test_ext() -> TestExternalities {
    let t = frame_system::GenesisConfig::<Test>::default()
        .build_storage()
        .unwrap();
    TestExternalities::new(t)
}

#[test]
fn create_tree_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(Pallet::<Test>::create_tree(
            frame_system::RawOrigin::Signed(sp_core::crypto::AccountId32::from([0xff; 32])).into(),
            10
        ));
        assert_eq!(ZkTotalTrees::<Test>::get(), 1);
    });
}

#[test]
fn compress_account_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(Pallet::<Test>::create_tree(
            frame_system::RawOrigin::Signed(sp_core::crypto::AccountId32::from([0xff; 32])).into(),
            10
        ));
        assert_ok!(Pallet::<Test>::compress_account(
            frame_system::RawOrigin::Signed(sp_core::crypto::AccountId32::from([0xff; 32])).into(),
            0,
            256
        ));
        assert_eq!(ZkTotalCompressed::<Test>::get(), 1);
    });
}

#[test]
fn verify_proof_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(Pallet::<Test>::verify_proof(
            frame_system::RawOrigin::Root.into(),
            0,
            0,
            [0u8; 32]
        ));
    });
}

#[test]
fn max_depth_exceeded() {
    new_test_ext().execute_with(|| {
        assert!(Pallet::<Test>::create_tree(
            frame_system::RawOrigin::Signed(sp_core::crypto::AccountId32::from([0xff; 32])).into(),
            999
        )
        .is_err());
    });
}
