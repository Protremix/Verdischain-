use crate::*;
use frame_support::{assert_ok, construct_runtime, derive_impl, parameter_types};
use sp_io::TestExternalities;
use sp_runtime::{traits::IdentityLookup, BuildStorage};

type Block = frame_system::mocking::MockBlock<Test>;

construct_runtime!(
    pub enum Test {
        System: frame_system,
        Turbine: crate,
    }
);

#[derive_impl(frame_system::config_preludes::TestDefaultConfig as frame_system::DefaultConfig)]
impl frame_system::Config for Test {
    type AccountId = sp_core::crypto::AccountId32;
    type Lookup = IdentityLookup<Self::AccountId>;
    type Block = Block;
}

parameter_types! {
    pub const MaxShards: u32 = 256;
    pub const RedundancyFactor: u32 = 3;
    pub const MaxValidatorsPerNode: u32 = 8;
}

impl Config for Test {
    type MaxShards = MaxShards;
    type RedundancyFactor = RedundancyFactor;
    type MaxValidatorsPerNode = MaxValidatorsPerNode;
}

pub fn new_test_ext() -> TestExternalities {
    let t = frame_system::GenesisConfig::<Test>::default()
        .build_storage()
        .unwrap();
    TestExternalities::new(t)
}

#[test]
fn register_shard_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(Pallet::<Test>::register_shard(
            frame_system::RawOrigin::Signed(sp_core::crypto::AccountId32::from([0xff; 32])).into(),
            1,
            0,
            10
        ));
        assert_eq!(TurbineTotalShards::<Test>::get(), 1);
    });
}

#[test]
fn rebuild_tree_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(Pallet::<Test>::rebuild_tree(
            frame_system::RawOrigin::Signed(sp_core::crypto::AccountId32::from([0xff; 32])).into(),
            64
        ));
        assert_eq!(TurbineValidatorCount::<Test>::get(), 64);
        assert!(TurbineTreeDepth::<Test>::get() > 0);
    });
}

#[test]
fn mark_block_propagated_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(Pallet::<Test>::mark_block_propagated(
            frame_system::RawOrigin::Signed(sp_core::crypto::AccountId32::from([0xff; 32])).into(),
            1
        ));
        assert_eq!(TurbineTotalBlocks::<Test>::get(), 1);
    });
}

#[test]
fn max_shards_exceeded() {
    new_test_ext().execute_with(|| {
        assert!(Pallet::<Test>::register_shard(
            frame_system::RawOrigin::Signed(sp_core::crypto::AccountId32::from([0xff; 32])).into(),
            1,
            0,
            999
        )
        .is_err());
    });
}
