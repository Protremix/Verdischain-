use crate::*;
use frame_support::{assert_ok, construct_runtime, derive_impl, parameter_types};
use sp_io::TestExternalities;
use sp_runtime::{traits::IdentityLookup, BuildStorage};

type Block = frame_system::mocking::MockBlock<Test>;

construct_runtime!(
    pub enum Test {
        System: frame_system,
        GulfStream: crate,
    }
);

#[derive_impl(frame_system::config_preludes::TestDefaultConfig as frame_system::DefaultConfig)]
impl frame_system::Config for Test {
    type AccountId = sp_core::crypto::AccountId32;
    type Lookup = IdentityLookup<Self::AccountId>;
    type Block = Block;
}

parameter_types! {
    pub const MaxPendingForwards: u32 = 10000;
    pub const MaxForwardedHistory: u32 = 1000;
}

// Mock validator checker that accepts all signed callers (for testing)
impl ValidatorChecker<sp_core::crypto::AccountId32> for Test {
    fn is_active_validator(_who: &sp_core::crypto::AccountId32) -> bool {
        true
    }
}

impl Config for Test {
    type MaxPendingForwards = MaxPendingForwards;
    type MaxForwardedHistory = MaxForwardedHistory;
    type ValidatorChecker = Test;
}

pub fn new_test_ext() -> TestExternalities {
    let t = frame_system::GenesisConfig::<Test>::default()
        .build_storage()
        .unwrap();
    TestExternalities::new(t)
}

#[test]
fn forward_tx_works() {
    new_test_ext().execute_with(|| {
        let tx_hash = [0u8; 32];
        assert_ok!(Pallet::<Test>::forward_transaction(
            frame_system::RawOrigin::Signed(sp_core::crypto::AccountId32::from([0xff; 32])).into(),
            tx_hash,
            vec![1, 2, 3],
            256
        ));
        let stats = Pallet::<Test>::get_stats();
        assert_eq!(stats.total_forwarded, 1);
    });
}

#[test]
fn mark_included_works() {
    new_test_ext().execute_with(|| {
        // Set block number so mark_included block validation passes
        frame_system::Pallet::<Test>::set_block_number(2);
        let tx_hash = [0u8; 32];
        assert_ok!(Pallet::<Test>::forward_transaction(
            frame_system::RawOrigin::Signed(sp_core::crypto::AccountId32::from([0xff; 32])).into(),
            tx_hash,
            vec![1, 2, 3],
            256
        ));
        assert_ok!(Pallet::<Test>::mark_included(
            frame_system::RawOrigin::Signed(sp_core::crypto::AccountId32::from([0xff; 32])).into(),
            tx_hash,
            1,
            100
        ));
        let stats = Pallet::<Test>::get_stats();
        assert_eq!(stats.total_included, 1);
    });
}

#[test]
fn get_pending_count_works() {
    new_test_ext().execute_with(|| {
        assert_eq!(Pallet::<Test>::get_pending_count(), 0);
        let tx_hash = [0u8; 32];
        assert_ok!(Pallet::<Test>::forward_transaction(
            frame_system::RawOrigin::Signed(sp_core::crypto::AccountId32::from([0xff; 32])).into(),
            tx_hash,
            vec![1, 2, 3],
            256
        ));
        assert_eq!(Pallet::<Test>::get_pending_count(), 1);
    });
}

#[test]
fn expire_transaction_works() {
    new_test_ext().execute_with(|| {
        let tx_hash = [0u8; 32];
        assert_ok!(Pallet::<Test>::forward_transaction(
            frame_system::RawOrigin::Signed(sp_core::crypto::AccountId32::from([0xff; 32])).into(),
            tx_hash,
            vec![1, 2, 3],
            256
        ));
        assert_ok!(Pallet::<Test>::expire_transaction(
            frame_system::RawOrigin::Signed(sp_core::crypto::AccountId32::from([0xff; 32])).into(),
            tx_hash
        ));
        let stats = Pallet::<Test>::get_stats();
        assert_eq!(stats.total_expired, 1);
    });
}
