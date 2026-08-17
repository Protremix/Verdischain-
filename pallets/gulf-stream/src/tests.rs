use crate::*;
use frame_support::{assert_err, assert_ok, construct_runtime, derive_impl, parameter_types};
use sp_io::TestExternalities;
use sp_runtime::{traits::IdentityLookup, BuildStorage};

type Block = frame_system::mocking::MockBlock<Test>;

construct_runtime!(
    pub enum Test {
        System: frame_system,
        Timestamp: pallet_timestamp,
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
    pub const MinimumPeriod: u64 = 1;
}

impl pallet_timestamp::Config for Test {
    type Moment = u64;
    type OnTimestampSet = ();
    type MinimumPeriod = MinimumPeriod;
    type WeightInfo = ();
}

parameter_types! {
    pub const MaxPendingForwards: u32 = 10000;
    pub const MaxForwardedHistory: u32 = 1000;
    pub const MaxForwardTimeMs: u64 = 60_000;
}

// Mock validator checker: [0xff; 32] is active validator, others are not
impl ValidatorChecker<sp_core::crypto::AccountId32> for Test {
    fn is_active_validator(who: &sp_core::crypto::AccountId32) -> bool {
        who == &sp_core::crypto::AccountId32::from([0xff; 32])
    }
}

impl Config for Test {
    type MaxPendingForwards = MaxPendingForwards;
    type MaxForwardedHistory = MaxForwardedHistory;
    type MaxForwardTimeMs = MaxForwardTimeMs;
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

#[test]
fn mark_included_already_processed_fails() {
    new_test_ext().execute_with(|| {
        frame_system::Pallet::<Test>::set_block_number(2);
        let tx_hash = [0u8; 32];
        let validator = sp_core::crypto::AccountId32::from([0xff; 32]);
        assert_ok!(Pallet::<Test>::forward_transaction(
            frame_system::RawOrigin::Signed(validator.clone()).into(),
            tx_hash,
            vec![1, 2, 3],
            256
        ));
        // First mark_included succeeds
        assert_ok!(Pallet::<Test>::mark_included(
            frame_system::RawOrigin::Signed(validator.clone()).into(),
            tx_hash,
            1,
            100
        ));
        // Second mark_included should fail - already removed
        assert_err!(
            Pallet::<Test>::mark_included(
                frame_system::RawOrigin::Signed(validator).into(),
                tx_hash,
                1,
                100
            ),
            Error::<Test>::TransactionNotFound
        );
    });
}

#[test]
fn mark_included_excessive_forward_time_fails() {
    new_test_ext().execute_with(|| {
        frame_system::Pallet::<Test>::set_block_number(2);
        let tx_hash = [0u8; 32];
        let validator = sp_core::crypto::AccountId32::from([0xff; 32]);
        assert_ok!(Pallet::<Test>::forward_transaction(
            frame_system::RawOrigin::Signed(validator.clone()).into(),
            tx_hash,
            vec![1, 2, 3],
            256
        ));
        // forward_time_ms = 999_999 exceeds MaxForwardTimeMs (60_000)
        assert_err!(
            Pallet::<Test>::mark_included(
                frame_system::RawOrigin::Signed(validator).into(),
                tx_hash,
                1,
                999_999
            ),
            Error::<Test>::InvalidForwardTime
        );
    });
}

#[test]
fn test_forward_duplicate_rejected() {
    new_test_ext().execute_with(|| {
        let tx_hash = [1u8; 32];
        let validator = sp_core::crypto::AccountId32::from([0xff; 32]);
        assert_ok!(Pallet::<Test>::forward_transaction(
            frame_system::RawOrigin::Signed(validator.clone()).into(),
            tx_hash,
            vec![1, 2, 3],
            256
        ));
        assert_err!(
            Pallet::<Test>::forward_transaction(
                frame_system::RawOrigin::Signed(validator).into(),
                tx_hash,
                vec![1, 2, 3],
                256
            ),
            Error::<Test>::AlreadyForwarded
        );
    });
}

#[test]
fn test_forward_unsigned_rejected() {
    new_test_ext().execute_with(|| {
        let tx_hash = [2u8; 32];
        assert_err!(
            Pallet::<Test>::forward_transaction(
                frame_system::RawOrigin::None.into(),
                tx_hash,
                vec![1, 2, 3],
                256
            ),
            sp_runtime::DispatchError::BadOrigin
        );
    });
}

#[test]
fn test_mark_included_non_validator_rejected() {
    new_test_ext().execute_with(|| {
        frame_system::Pallet::<Test>::set_block_number(2);
        let tx_hash = [3u8; 32];
        let validator = sp_core::crypto::AccountId32::from([0xff; 32]);
        let non_validator = sp_core::crypto::AccountId32::from([0xee; 32]);
        assert_ok!(Pallet::<Test>::forward_transaction(
            frame_system::RawOrigin::Signed(validator).into(),
            tx_hash,
            vec![1, 2, 3],
            256
        ));
        assert_err!(
            Pallet::<Test>::mark_included(
                frame_system::RawOrigin::Signed(non_validator).into(),
                tx_hash,
                1,
                100
            ),
            Error::<Test>::NotActiveValidator
        );
    });
}

#[test]
fn test_mark_included_future_block_rejected() {
    new_test_ext().execute_with(|| {
        frame_system::Pallet::<Test>::set_block_number(10);
        let tx_hash = [4u8; 32];
        let validator = sp_core::crypto::AccountId32::from([0xff; 32]);
        assert_ok!(Pallet::<Test>::forward_transaction(
            frame_system::RawOrigin::Signed(validator.clone()).into(),
            tx_hash,
            vec![1, 2, 3],
            256
        ));
        // block_number = 16 > current(10) + 5
        assert_err!(
            Pallet::<Test>::mark_included(
                frame_system::RawOrigin::Signed(validator).into(),
                tx_hash,
                16,
                100
            ),
            Error::<Test>::InvalidBlockNumber
        );
    });
}

#[test]
fn test_mark_included_old_block_rejected() {
    new_test_ext().execute_with(|| {
        frame_system::Pallet::<Test>::set_block_number(10);
        let tx_hash = [5u8; 32];
        let validator = sp_core::crypto::AccountId32::from([0xff; 32]);
        assert_ok!(Pallet::<Test>::forward_transaction(
            frame_system::RawOrigin::Signed(validator.clone()).into(),
            tx_hash,
            vec![1, 2, 3],
            256
        ));
        // block_number = 4 is more than 5 blocks older than current(10) (10 - 4 = 6 > 5)
        assert_err!(
            Pallet::<Test>::mark_included(
                frame_system::RawOrigin::Signed(validator).into(),
                tx_hash,
                4,
                100
            ),
            Error::<Test>::InvalidBlockNumber
        );
    });
}

#[test]
fn test_expire_nonexistent_rejected() {
    new_test_ext().execute_with(|| {
        let tx_hash = [99u8; 32];
        let caller = sp_core::crypto::AccountId32::from([0xff; 32]);
        assert_err!(
            Pallet::<Test>::expire_transaction(
                frame_system::RawOrigin::Signed(caller).into(),
                tx_hash
            ),
            Error::<Test>::TransactionNotFound
        );
    });
}

#[test]
fn test_expire_already_included_rejected() {
    new_test_ext().execute_with(|| {
        frame_system::Pallet::<Test>::set_block_number(2);
        let tx_hash = [6u8; 32];
        let validator = sp_core::crypto::AccountId32::from([0xff; 32]);
        assert_ok!(Pallet::<Test>::forward_transaction(
            frame_system::RawOrigin::Signed(validator.clone()).into(),
            tx_hash,
            vec![1, 2, 3],
            256
        ));
        assert_ok!(Pallet::<Test>::mark_included(
            frame_system::RawOrigin::Signed(validator.clone()).into(),
            tx_hash,
            1,
            100
        ));
        // Expire after included fails with TransactionNotFound
        assert_err!(
            Pallet::<Test>::expire_transaction(
                frame_system::RawOrigin::Signed(validator).into(),
                tx_hash
            ),
            Error::<Test>::TransactionNotFound
        );
    });
}

#[test]
fn test_forward_and_expire_works() {
    new_test_ext().execute_with(|| {
        let tx_hash = [7u8; 32];
        let caller = sp_core::crypto::AccountId32::from([0xff; 32]);
        assert_ok!(Pallet::<Test>::forward_transaction(
            frame_system::RawOrigin::Signed(caller.clone()).into(),
            tx_hash,
            vec![1, 2, 3],
            256
        ));
        assert_eq!(Pallet::<Test>::get_pending_count(), 1);
        assert_ok!(Pallet::<Test>::expire_transaction(
            frame_system::RawOrigin::Signed(caller).into(),
            tx_hash
        ));
        assert_eq!(Pallet::<Test>::get_pending_count(), 0);
    });
}

#[test]
fn test_mark_included_without_forward_rejected() {
    new_test_ext().execute_with(|| {
        frame_system::Pallet::<Test>::set_block_number(2);
        let tx_hash = [88u8; 32];
        let validator = sp_core::crypto::AccountId32::from([0xff; 32]);
        assert_err!(
            Pallet::<Test>::mark_included(
                frame_system::RawOrigin::Signed(validator).into(),
                tx_hash,
                1,
                100
            ),
            Error::<Test>::TransactionNotFound
        );
    });
}

#[test]
fn test_get_stats_after_operations() {
    new_test_ext().execute_with(|| {
        frame_system::Pallet::<Test>::set_block_number(10);
        let tx1 = [10u8; 32];
        let tx2 = [20u8; 32];
        let tx3 = [30u8; 32];
        let validator = sp_core::crypto::AccountId32::from([0xff; 32]);

        // Forward 3 transactions
        assert_ok!(Pallet::<Test>::forward_transaction(
            frame_system::RawOrigin::Signed(validator.clone()).into(),
            tx1,
            vec![1, 2, 3],
            256
        ));
        assert_ok!(Pallet::<Test>::forward_transaction(
            frame_system::RawOrigin::Signed(validator.clone()).into(),
            tx2,
            vec![1, 2, 3],
            256
        ));
        assert_ok!(Pallet::<Test>::forward_transaction(
            frame_system::RawOrigin::Signed(validator.clone()).into(),
            tx3,
            vec![1, 2, 3],
            256
        ));

        // Mark tx1 included
        assert_ok!(Pallet::<Test>::mark_included(
            frame_system::RawOrigin::Signed(validator.clone()).into(),
            tx1,
            10,
            100
        ));

        // Expire tx2
        assert_ok!(Pallet::<Test>::expire_transaction(
            frame_system::RawOrigin::Signed(validator).into(),
            tx2
        ));

        let stats = Pallet::<Test>::get_stats();
        assert_eq!(stats.total_forwarded, 3);
        assert_eq!(stats.total_included, 1);
        assert_eq!(stats.total_expired, 1);
        assert_eq!(stats.current_pending, 1);
        assert_eq!(stats.success_rate, 50);
        assert_eq!(stats.avg_forward_time_ms, 100);
    });
}
