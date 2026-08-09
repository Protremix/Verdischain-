use crate::*;
use frame_support::{assert_ok, construct_runtime, derive_impl, parameter_types};
use sp_io::TestExternalities;
use sp_runtime::{traits::IdentityLookup, BuildStorage};

type Block = frame_system::mocking::MockBlock<Test>;

construct_runtime!(
    pub enum Test {
        System: frame_system,
        Sealevel: crate,
    }
);

#[derive_impl(frame_system::config_preludes::TestDefaultConfig as frame_system::DefaultConfig)]
impl frame_system::Config for Test {
    type AccountId = sp_core::crypto::AccountId32;
    type Lookup = IdentityLookup<Self::AccountId>;
    type Block = Block;
}

parameter_types! {
    pub const MaxComputeUnits: u64 = 1000000;
    pub const MaxParallelBatches: u32 = 1000;
}

impl Config for Test {
    type MaxComputeUnits = MaxComputeUnits;
    type MaxParallelBatches = MaxParallelBatches;
}

pub fn new_test_ext() -> TestExternalities {
    let t = frame_system::GenesisConfig::<Test>::default()
        .build_storage()
        .unwrap();
    TestExternalities::new(t)
}

#[test]
fn create_batch_parallel_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(Pallet::<Test>::create_batch(
            frame_system::RawOrigin::Signed(sp_core::crypto::AccountId32::from([0xff; 32])).into(),
            10,
            false
        ));
        assert_eq!(SealevelTotalBatches::<Test>::get(), 1);
        assert_eq!(SealevelParallelBatches::<Test>::get(), 1);
    });
}

#[test]
fn create_batch_sequential_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(Pallet::<Test>::create_batch(
            frame_system::RawOrigin::Signed(sp_core::crypto::AccountId32::from([0xff; 32])).into(),
            10,
            true
        ));
        assert_eq!(SealevelSequentialBatches::<Test>::get(), 1);
    });
}

#[test]
fn report_execution_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(Pallet::<Test>::create_batch(
            frame_system::RawOrigin::Signed(sp_core::crypto::AccountId32::from([0xff; 32])).into(),
            5,
            false
        ));
        assert_ok!(Pallet::<Test>::report_execution(
            frame_system::RawOrigin::Signed(sp_core::crypto::AccountId32::from([0xff; 32])).into(),
            0,
            5000,
            5
        ));
        assert_eq!(SealevelTotalTxs::<Test>::get(), 5);
    });
}

#[test]
fn report_conflict_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(Pallet::<Test>::report_conflict(
            frame_system::RawOrigin::Signed(sp_core::crypto::AccountId32::from([0xff; 32])).into(),
            0,
            1,
            2
        ));
        assert_eq!(SealevelConflicts::<Test>::get(), 1);
    });
}
