#![allow(unused_imports)]
#[path = "luna_adversarial_tests.rs"]
mod luna_adversarial_tests;
#[path = "presale_tests.rs"]
mod presale_tests;
#[path = "regression_tests.rs"]
mod regression_tests;
use crate::*;
use frame_support::{
    assert_noop, assert_ok, construct_runtime, derive_impl, parameter_types,
    traits::{ConstU32, ConstU64, Currency},
};
use sp_io::TestExternalities;
use sp_runtime::{
    traits::{AccountIdConversion, IdentityLookup},
    BuildStorage,
};

type Block = frame_system::mocking::MockBlock<Test>;

construct_runtime!(
    pub enum Test {
        System: frame_system,
        Balances: pallet_balances,
        Presale: crate,
    }
);

#[derive_impl(frame_system::config_preludes::TestDefaultConfig as frame_system::DefaultConfig)]
impl frame_system::Config for Test {
    type AccountId = u64;
    type Lookup = IdentityLookup<Self::AccountId>;
    type Block = Block;
    type AccountData = pallet_balances::AccountData<u64>;
}

impl pallet_balances::Config for Test {
    type MaxLocks = ConstU32<50>;
    type MaxReserves = ConstU32<50>;
    type ReserveIdentifier = [u8; 8];
    type Balance = u64;
    type RuntimeEvent = RuntimeEvent;
    type DustRemoval = ();
    type ExistentialDeposit = ConstU64<1>;
    type AccountStore = System;
    type WeightInfo = ();
    type FreezeIdentifier = ();
    type MaxFreezes = ConstU32<0>;
    type RuntimeHoldReason = ();
    type RuntimeFreezeReason = ();
    type DoneSlashHandler = ();
}

parameter_types! {
    pub const PresalePalletId: frame_support::PalletId = frame_support::PalletId(*b"verdisps");
    pub const TestTreasury: u64 = 999;
}

impl crate::Config for Test {
    type RuntimeEvent = RuntimeEvent;
    type Currency = Balances;
    type PaymentCurrency = Balances;
    type PalletId = PresalePalletId;
    type AdminOrigin = frame_system::EnsureRoot<u64>;
    type Vesting = ();
    type WeightInfo = ();
    type Treasury = TestTreasury;
}

pub fn new_test_ext() -> TestExternalities {
    let mut t = frame_system::GenesisConfig::<Test>::default()
        .build_storage()
        .unwrap();
    let escrow_0 = PresalePalletId::get().into_sub_account_truncating(0u32);
    let escrow_1 = PresalePalletId::get().into_sub_account_truncating(1u32);
    let escrow_2 = PresalePalletId::get().into_sub_account_truncating(2u32);
    // Build deduplicated genesis balances (sub-accounts may collide with test accounts)
    use std::collections::BTreeMap;
    let mut balances_map = BTreeMap::new();
    balances_map.insert(1u64, 1_000_000_000u64);
    balances_map.insert(2u64, 1_000_000_000u64);
    balances_map.insert(3u64, 1_000_000_000u64);
    balances_map.insert(escrow_0, 1_000_000_000_000u64);
    balances_map.insert(escrow_1, 1_000_000_000_000u64);
    balances_map.insert(escrow_2, 1_000_000_000_000u64);
    balances_map.insert(999u64, 1_000_000_000u64); // treasury
    let balances: Vec<(u64, u64)> = balances_map.into_iter().collect();
    pallet_balances::GenesisConfig::<Test> {
        dev_accounts: None,
        balances,
    }
    .assimilate_storage(&mut t)
    .unwrap();
    TestExternalities::new(t)
}

fn set_block(n: u64) {
    System::set_block_number(n);
}

fn escrow_account() -> u64 {
    // Backward compat: returns round-0 escrow (most tests use round 0)
    PresalePalletId::get().into_sub_account_truncating(0u32)
}

fn round_escrow_account(round_id: u32) -> u64 {
    PresalePalletId::get().into_sub_account_truncating(round_id)
}

fn create_and_activate_round(
    round_id_expected: u32,
    price: u64,
    allocation: u64,
    cap: u64,
    start: u64,
    end: u64,
    vesting: Vec<u8>,
) {
    assert_ok!(Presale::create_round(
        RuntimeOrigin::root(),
        b"test".to_vec(),
        price,
        allocation,
        cap,
        start,
        end,
        vesting,
    ));
    assert_ok!(Presale::activate_round(
        RuntimeOrigin::root(),
        round_id_expected
    ));
}

// === EXISTING TESTS ===

#[test]
fn test_create_round_admin_only() {
    new_test_ext().execute_with(|| {
        set_block(1);
        assert_ok!(Presale::create_round(
            RuntimeOrigin::root(),
            b"seed".to_vec(),
            5_000_000,
            3_000_000_000,
            100_000_000,
            10,
            1000,
            b"seed".to_vec(),
        ));
        assert!(Presale::rounds(0).is_some());
    });
}

#[test]
fn test_create_round_non_admin_fails() {
    new_test_ext().execute_with(|| {
        set_block(1);
        assert_noop!(
            Presale::create_round(
                RuntimeOrigin::signed(1),
                b"seed".to_vec(),
                5_000_000,
                3_000_000_000,
                100_000_000,
                10,
                1000,
                b"seed".to_vec(),
            ),
            sp_runtime::DispatchError::BadOrigin
        );
    });
}

#[test]
fn test_activate_deactivate_round() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 1000, 100, 1, 100, b"vest".to_vec());
        assert!(Presale::rounds(0).unwrap().status == RoundStatus::Active);
        assert_ok!(Presale::deactivate_round(RuntimeOrigin::root(), 0));
        assert!(Presale::rounds(0).unwrap().status != RoundStatus::Active);
    });
}

#[test]
fn test_contribute_to_round() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 1000, 100, 1, 100, b"vest".to_vec());
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
        let contrib = Presale::contributions(0, 1).unwrap();
        assert_eq!(contrib.total_purchased, 50);
        assert_eq!(contrib.total_paid, 10);
    });
}

#[test]
fn test_contribute_exceeds_per_account_cap() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 10000, 100, 1, 100, b"vest".to_vec());
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 20));
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(1), 0, 1),
            Error::<Test>::ExceedsPerAccountCap
        );
    });
}

#[test]
fn test_contribute_exceeds_round_allocation() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 50, 1000, 1, 100, b"vest".to_vec());
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(2), 0, 1),
            Error::<Test>::ExceedsRoundAllocation
        );
    });
}

#[test]
fn test_contribute_round_not_active() {
    new_test_ext().execute_with(|| {
        set_block(1);
        assert_ok!(Presale::create_round(
            RuntimeOrigin::root(),
            b"test".to_vec(),
            5,
            1000,
            100,
            1,
            100,
            b"vest".to_vec(),
        ));
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(1), 0, 10),
            Error::<Test>::RoundNotActive
        );
    });
}

#[test]
fn test_contribute_round_not_started() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 1000, 100, 50, 100, b"vest".to_vec());
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(1), 0, 10),
            Error::<Test>::RoundNotStarted
        );
    });
}

#[test]
fn test_contribute_round_ended() {
    new_test_ext().execute_with(|| {
        set_block(150);
        create_and_activate_round(0, 5, 1000, 100, 1, 100, b"vest".to_vec());
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(1), 0, 10),
            Error::<Test>::RoundEnded
        );
    });
}

#[test]
fn test_paused_blocks_contributions() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 1000, 100, 1, 100, b"vest".to_vec());
        assert_ok!(Presale::set_paused(RuntimeOrigin::root(), true));
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(1), 0, 10),
            Error::<Test>::Paused
        );
    });
}

#[test]
fn test_whitelist() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 1000, 100, 1, 100, b"vest".to_vec());
        assert_ok!(Presale::set_whitelist_required(
            RuntimeOrigin::root(),
            0,
            true
        ));
        assert_ok!(Presale::update_whitelist(RuntimeOrigin::root(), 0, 1, true));
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(2), 0, 10),
            Error::<Test>::NotWhitelisted
        );
    });
}

#[test]
fn test_zero_payment_fails() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 1000, 100, 1, 100, b"vest".to_vec());
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(1), 0, 0),
            Error::<Test>::ZeroPayment
        );
    });
}

#[test]
fn test_round_not_found() {
    new_test_ext().execute_with(|| {
        set_block(1);
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(1), 99, 10),
            Error::<Test>::RoundNotFound
        );
    });
}

#[test]
fn test_total_raised_and_sold_tracking() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 10000, 1000, 1, 100, b"vest".to_vec());
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(2), 0, 20));
        assert_eq!(Presale::total_raised(), 30);
        assert_eq!(Presale::total_sold(), 150);
    });
}

// === P0: ESCROW-BASED PAYMENT TESTS ===

#[test]
fn test_payment_transferred_to_escrow_not_reserved() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 1000, 100, 1, 100, b"vest".to_vec());
        let escrow = round_escrow_account(0);
        let escrow_before = Balances::free_balance(escrow);
        let user1_before = Balances::free_balance(1);

        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));

        let escrow_after = Balances::free_balance(escrow);
        let user1_after = Balances::free_balance(1);

        // Payment (10) transferred to escrow, tokens (50) transferred out
        let escrow_change = escrow_after as i64 - escrow_before as i64;
        assert_eq!(escrow_change, 10i64 - 50, "Escrow: +10 payment, -50 tokens");
        // User: -10 payment + 50 tokens = +40 net
        let user1_change = user1_after as i64 - user1_before as i64;
        assert_eq!(
            user1_change,
            -10i64 + 50,
            "User net: -10 payment + 50 tokens"
        );
        // No reserved balance
        assert_eq!(
            Balances::reserved_balance(1),
            0,
            "No reserved balance for buyer"
        );
    });
}

#[test]
fn test_escrow_receives_payment_and_sends_tokens() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 1000, 100, 1, 100, b"vest".to_vec());
        let escrow = escrow_account();
        let escrow_before = Balances::free_balance(escrow);

        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));

        let escrow_after = Balances::free_balance(escrow);
        let escrow_change = escrow_after as i64 - escrow_before as i64;
        assert_eq!(escrow_change, 10i64 - 50, "Escrow: +10 payment, -50 tokens");
    });
}

// === P0: ROUND-LEVEL RAISED TRACKING ===

#[test]
fn test_round_raised_tracking() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 10000, 1000, 1, 100, b"vest".to_vec());
        create_and_activate_round(1, 3, 10000, 1000, 1, 100, b"vest".to_vec());

        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(2), 0, 20));
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 1, 15));

        assert_eq!(Presale::round_raised(0), 30);
        assert_eq!(Presale::round_raised(1), 15);
        assert_eq!(Presale::total_raised(), 45);
    });
}

// === P0: COLLECT_FUNDS — O(1) FROM ESCROW ===

#[test]
fn test_collect_funds_after_round_end() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 10000, 1000, 1, 100, b"vest".to_vec());
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 100));
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(2), 0, 200));

        set_block(50);
        assert_noop!(
            Presale::collect_funds(RuntimeOrigin::root(), 0, 3),
            Error::<Test>::RoundStatusInvalid
        );

        set_block(100);
        assert_ok!(Presale::finalize_round(RuntimeOrigin::root(), 0));
        let escrow = escrow_account();
        let escrow_before = Balances::free_balance(escrow);
        let beneficiary_before = Balances::free_balance(3);

        assert_ok!(Presale::collect_funds(RuntimeOrigin::root(), 0, 3));

        let raised = Presale::round_raised(0);
        assert_eq!(raised, 300);
        assert_eq!(Balances::free_balance(3) - beneficiary_before, 300);
        assert_eq!(escrow_before - Balances::free_balance(escrow), 300);
        assert!(Presale::round_funds_collected(0));
    });
}

#[test]
fn test_collect_funds_active_round_fails() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 10000, 1000, 1, 100, b"vest".to_vec());
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));

        set_block(50);
        assert_ok!(Presale::deactivate_round(RuntimeOrigin::root(), 0));
        assert_noop!(
            Presale::collect_funds(RuntimeOrigin::root(), 0, 3),
            Error::<Test>::RoundStatusInvalid
        );
    });
}

#[test]
fn test_collect_funds_deactivated_not_ended_fails() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 10000, 1000, 1, 200, b"vest".to_vec());
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));

        set_block(100);
        assert_ok!(Presale::deactivate_round(RuntimeOrigin::root(), 0));

        assert_noop!(
            Presale::collect_funds(RuntimeOrigin::root(), 0, 3),
            Error::<Test>::RoundStatusInvalid
        );
    });
}

#[test]
fn test_collect_funds_double_collection_fails() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 10000, 1000, 1, 100, b"vest".to_vec());
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 100));

        set_block(100);
        assert_ok!(Presale::finalize_round(RuntimeOrigin::root(), 0));
        assert_ok!(Presale::collect_funds(RuntimeOrigin::root(), 0, 3));
        // Second collect fails: round is now Closed (status check fails first)
        assert_noop!(
            Presale::collect_funds(RuntimeOrigin::root(), 0, 3),
            Error::<Test>::RoundStatusInvalid
        );
    });
}

#[test]
fn test_collect_funds_round_not_found() {
    new_test_ext().execute_with(|| {
        set_block(1);
        assert_noop!(
            Presale::collect_funds(RuntimeOrigin::root(), 99, 3),
            Error::<Test>::RoundNotFound
        );
    });
}

#[test]
fn test_collect_funds_non_admin_fails() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 10000, 1000, 1, 100, b"vest".to_vec());
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 100));

        set_block(100);
        assert_noop!(
            Presale::collect_funds(RuntimeOrigin::signed(1), 0, 3),
            sp_runtime::DispatchError::BadOrigin
        );
    });
}

#[test]
fn test_collect_funds_zero_raised() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 10000, 1000, 1, 100, b"vest".to_vec());

        set_block(100);
        assert_ok!(Presale::finalize_round(RuntimeOrigin::root(), 0));
        assert_ok!(Presale::collect_funds(RuntimeOrigin::root(), 0, 3));
        assert!(Presale::round_funds_collected(0));
    });
}

// === P0: ESCROW BALANCE VERIFICATION ===

#[test]
fn test_escrow_insufficient_balance_fails() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 1000, 10000, 1, 100, b"vest".to_vec());

        let escrow = escrow_account();
        let escrow_bal = Balances::free_balance(escrow);
        assert_ok!(Balances::transfer_allow_death(
            RuntimeOrigin::signed(escrow),
            3,
            escrow_bal - 100,
        ));

        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(1), 0, 21),
            Error::<Test>::InsufficientEscrowBalance
        );
    });
}

// === P0: ECONOMIC INVARIANTS ===

#[test]
fn test_invariant_round_sold_le_allocation() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 100, 1000, 1, 100, b"vest".to_vec());
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 20));
        assert_eq!(Presale::rounds(0).unwrap().sold, 100);
        assert_eq!(Presale::rounds(0).unwrap().total_allocation, 100);
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(2), 0, 1),
            Error::<Test>::ExceedsRoundAllocation
        );
    });
}

#[test]
fn test_invariant_total_sold_le_total_allocation() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 100, 1000, 1, 100, b"vest".to_vec());
        create_and_activate_round(1, 5, 100, 1000, 1, 100, b"vest".to_vec());

        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 20));
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(2), 1, 20));

        assert_eq!(Presale::total_sold(), 200);
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(1), 0, 1),
            Error::<Test>::ExceedsRoundAllocation
        );
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(2), 1, 1),
            Error::<Test>::ExceedsRoundAllocation
        );
    });
}

#[test]
fn test_invariant_collected_le_round_raised() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 10000, 1000, 1, 100, b"vest".to_vec());
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 100));
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(2), 0, 200));

        set_block(100);
        let beneficiary_before = Balances::free_balance(3);
        assert_ok!(Presale::finalize_round(RuntimeOrigin::root(), 0));
        assert_ok!(Presale::collect_funds(RuntimeOrigin::root(), 0, 3));

        let collected = Balances::free_balance(3) - beneficiary_before;
        assert_eq!(collected, Presale::round_raised(0));
        assert_eq!(collected, 300);
    });
}

#[test]
fn test_invariant_funds_cannot_be_collected_twice() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 10000, 1000, 1, 100, b"vest".to_vec());
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 100));

        set_block(100);
        let before1 = Balances::free_balance(3);
        assert_ok!(Presale::finalize_round(RuntimeOrigin::root(), 0));
        assert_ok!(Presale::collect_funds(RuntimeOrigin::root(), 0, 3));
        let first = Balances::free_balance(3) - before1;

        let before2 = Balances::free_balance(3);
        assert_noop!(
            Presale::collect_funds(RuntimeOrigin::root(), 0, 3),
            Error::<Test>::RoundStatusInvalid
        );
        let second = Balances::free_balance(3) - before2;
        assert_eq!(second, 0);
        assert_eq!(first, 100);
    });
}

#[test]
fn test_invariant_user_purchased_le_per_round_cap() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 10000, 100, 1, 100, b"vest".to_vec());
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 20));
        assert_eq!(Presale::contributions(0, 1).unwrap().total_purchased, 100);
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(1), 0, 1),
            Error::<Test>::ExceedsPerAccountCap
        );
    });
}

#[test]
fn test_invariant_round_raised_contributes_once_to_total() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 10000, 1000, 1, 100, b"vest".to_vec());
        create_and_activate_round(1, 3, 10000, 1000, 1, 100, b"vest".to_vec());

        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 100));
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(2), 1, 200));

        assert_eq!(Presale::round_raised(0), 100);
        assert_eq!(Presale::round_raised(1), 200);
        assert_eq!(Presale::total_raised(), 300);
    });
}

// === P0: PER-ROUND CAP INDEPENDENCE ===

#[test]
fn test_per_round_cap_independence() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 10000, 100, 1, 100, b"vest".to_vec());
        create_and_activate_round(1, 5, 10000, 100, 1, 100, b"vest".to_vec());

        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 20));
        assert_eq!(Presale::contributions(0, 1).unwrap().total_purchased, 100);

        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 1, 20));
        assert_eq!(Presale::contributions(1, 1).unwrap().total_purchased, 100);

        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(1), 0, 1),
            Error::<Test>::ExceedsPerAccountCap
        );
    });
}

// === P0: PER-ROUND WHITELIST INDEPENDENCE ===

#[test]
fn test_per_round_whitelist_independence() {
    // H-02 FIX: whitelist_required flag must be set per round
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 1000, 100, 1, 100, b"vest".to_vec());
        assert_ok!(Presale::set_whitelist_required(
            RuntimeOrigin::root(),
            0,
            true
        ));
        create_and_activate_round(1, 5, 1000, 100, 1, 100, b"vest".to_vec());

        assert_ok!(Presale::update_whitelist(RuntimeOrigin::root(), 0, 1, true));

        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 1, 10));
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(2), 0, 10),
            Error::<Test>::NotWhitelisted
        );
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(2), 1, 10));
    });
}

// === P0: PRICE FORMULA EDGE CASES ===

#[test]
fn test_price_formula_minimum_payment() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 10000, 1000, 1, 100, b"vest".to_vec());
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 1));
        let contrib = Presale::contributions(0, 1).unwrap();
        assert_eq!(contrib.total_purchased, 5);
        assert_eq!(contrib.total_paid, 1);
    });
}

#[test]
fn test_price_formula_large_payment() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 100_000_000, 100_000_000, 1, 100, b"vest".to_vec());
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10_000_000));
        assert_eq!(
            Presale::contributions(0, 1).unwrap().total_purchased,
            50_000_000
        );
    });
}

#[test]
fn test_price_formula_overflow_protection() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, u64::MAX, 10000, 100_000_000, 1, 100, b"vest".to_vec());
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(1), 0, 2),
            Error::<Test>::CalculationOverflow
        );
    });
}

#[test]
fn test_price_formula_exact_allocation() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 10, 1000, 1000, 1, 100, b"vest".to_vec());
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 100));
        assert_eq!(Presale::rounds(0).unwrap().sold, 1000);
    });
}

// === P0: ATTACKER / SECURITY TESTS ===

#[test]
fn test_attacker_double_collection_prevented() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 10000, 1000, 1, 100, b"vest".to_vec());
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 100));

        set_block(100);
        assert_ok!(Presale::finalize_round(RuntimeOrigin::root(), 0));
        assert_ok!(Presale::collect_funds(RuntimeOrigin::root(), 0, 3));
        assert_noop!(
            Presale::collect_funds(RuntimeOrigin::root(), 0, 2),
            Error::<Test>::RoundStatusInvalid
        );
    });
}

#[test]
fn test_attacker_collection_before_round_end() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 10000, 1000, 1, 200, b"vest".to_vec());
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 100));

        set_block(50);
        assert_noop!(
            Presale::collect_funds(RuntimeOrigin::root(), 0, 3),
            Error::<Test>::RoundStatusInvalid
        );
        assert_ok!(Presale::deactivate_round(RuntimeOrigin::root(), 0));
        assert_noop!(
            Presale::collect_funds(RuntimeOrigin::root(), 0, 3),
            Error::<Test>::RoundStatusInvalid
        );
    });
}

#[test]
fn test_attacker_whitelist_bypass() {
    // H-02 FIX: whitelist_required flag prevents bypass
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 1000, 100, 1, 100, b"vest".to_vec());
        assert_ok!(Presale::set_whitelist_required(
            RuntimeOrigin::root(),
            0,
            true
        ));
        assert_ok!(Presale::update_whitelist(RuntimeOrigin::root(), 0, 1, true));

        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(2), 0, 10),
            Error::<Test>::NotWhitelisted
        );
        assert_noop!(
            Presale::update_whitelist(RuntimeOrigin::signed(2), 0, 2, true),
            sp_runtime::DispatchError::BadOrigin
        );
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(2), 0, 10),
            Error::<Test>::NotWhitelisted
        );
    });
}

#[test]
fn test_attacker_cap_bypass() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 10000, 100, 1, 100, b"vest".to_vec());

        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 20));
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(1), 0, 1),
            Error::<Test>::ExceedsPerAccountCap
        );
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(2), 0, 20));
    });
}

#[test]
fn test_attacker_allocation_bypass() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 100, 1000, 1, 100, b"vest".to_vec());

        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 20));
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(2), 0, 1),
            Error::<Test>::ExceedsRoundAllocation
        );
    });
}

#[test]
fn test_attacker_overflow_attempt() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(
            0,
            u64::MAX / 2,
            10000,
            100_000_000,
            1,
            100,
            b"vest".to_vec(),
        );
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(1), 0, 3),
            Error::<Test>::CalculationOverflow
        );
    });
}

#[test]
fn test_attacker_unauthorized_admin() {
    new_test_ext().execute_with(|| {
        set_block(1);
        assert_noop!(
            Presale::create_round(
                RuntimeOrigin::signed(1),
                b"test".to_vec(),
                5,
                1000,
                100,
                1,
                100,
                b"vest".to_vec(),
            ),
            sp_runtime::DispatchError::BadOrigin
        );
        assert_ok!(Presale::create_round(
            RuntimeOrigin::root(),
            b"test".to_vec(),
            5,
            1000,
            100,
            1,
            100,
            b"vest".to_vec(),
        ));
        assert_noop!(
            Presale::activate_round(RuntimeOrigin::signed(1), 0),
            sp_runtime::DispatchError::BadOrigin
        );
        assert_noop!(
            Presale::set_paused(RuntimeOrigin::signed(1), true),
            sp_runtime::DispatchError::BadOrigin
        );
        assert_noop!(
            Presale::update_whitelist(RuntimeOrigin::signed(1), 0, 1, true),
            sp_runtime::DispatchError::BadOrigin
        );
        set_block(100);
        assert_noop!(
            Presale::collect_funds(RuntimeOrigin::signed(1), 0, 3),
            sp_runtime::DispatchError::BadOrigin
        );
    });
}

#[test]
fn test_attacker_malicious_beneficiary() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 10000, 1000, 1, 100, b"vest".to_vec());
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 100));

        set_block(100);
        assert_ok!(Presale::finalize_round(RuntimeOrigin::root(), 0));
        assert_ok!(Presale::collect_funds(RuntimeOrigin::root(), 0, 1));
        assert_noop!(
            Presale::collect_funds(RuntimeOrigin::root(), 0, 2),
            Error::<Test>::RoundStatusInvalid
        );
    });
}

#[test]
fn test_attacker_replay_contribution() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 10000, 1000, 1, 100, b"vest".to_vec());

        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
        assert_eq!(Presale::contributions(0, 1).unwrap().total_paid, 10);

        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
        assert_eq!(Presale::contributions(0, 1).unwrap().total_paid, 20);
        assert_eq!(Presale::rounds(0).unwrap().sold, 100);
        assert_eq!(Presale::round_raised(0), 20);
        assert_eq!(Presale::total_raised(), 20);
    });
}

#[test]
fn test_attacker_zero_value_edge_cases() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 1000, 100, 1, 100, b"vest".to_vec());
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(1), 0, 0),
            Error::<Test>::ZeroPayment
        );
    });
}

#[test]
fn test_attacker_maximum_value_edge_cases() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 1, u64::MAX, u64::MAX, 1, 100, b"vest".to_vec());
        assert_ok!(Presale::contribute(
            RuntimeOrigin::signed(1),
            0,
            999_999_999
        ));
        assert_eq!(Presale::rounds(0).unwrap().sold, 999_999_999);
    });
}

// === P0: VESTING INVARIANTS ===

#[test]
fn test_vesting_invariant_purchased_equals_vested() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 10000, 1000, 1, 100, b"seed-12mo".to_vec());
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 100));
        assert_eq!(Presale::contributions(0, 1).unwrap().total_purchased, 500);

        System::assert_has_event(RuntimeEvent::Presale(crate::Event::VestingCreated {
            who: 1,
            round_id: 0,
            token_amount: 500,
            vesting_label: b"seed-12mo".to_vec(),
        }));
    });
}

#[test]
fn test_vesting_invariant_no_vesting_without_payment() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 10000, 1000, 1, 100, b"vest".to_vec());
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(1), 0, 0),
            Error::<Test>::ZeroPayment
        );
        assert!(Presale::contributions(0, 1).is_none());
    });
}

// === P0: ATOMIC TRANSACTION TESTS ===

#[test]
fn test_atomic_insufficient_payment_no_state_change() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, u64::MAX, u64::MAX, 1, 100, b"vest".to_vec());

        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 100));
        let remaining = Balances::free_balance(1);
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(1), 0, remaining + 1),
            Error::<Test>::InsufficientPayment
        );

        let contrib = Presale::contributions(0, 1).unwrap();
        assert_eq!(contrib.total_paid, 100);
        assert_eq!(Presale::rounds(0).unwrap().sold, 500);
        assert_eq!(Presale::total_raised(), 100);
    });
}

#[test]
fn test_atomic_insufficient_escrow_no_state_change() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 10000, 1000, 1, 100, b"vest".to_vec());

        let escrow = escrow_account();
        let escrow_bal = Balances::free_balance(escrow);
        assert_ok!(Balances::transfer_allow_death(
            RuntimeOrigin::signed(escrow),
            3,
            escrow_bal - 10,
        ));

        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(1), 0, 3),
            Error::<Test>::InsufficientEscrowBalance
        );

        assert!(Presale::contributions(0, 1).is_none());
        assert_eq!(Presale::rounds(0).unwrap().sold, 0);
        assert_eq!(Presale::total_raised(), 0);
    });
}

#[test]
fn test_atomic_invalid_round_no_state_change() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 10000, 1000, 1, 100, b"vest".to_vec());

        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(1), 99, 10),
            Error::<Test>::RoundNotFound
        );
        assert_eq!(Presale::total_raised(), 0);
        assert_eq!(Presale::total_sold(), 0);
    });
}

#[test]
fn test_atomic_allocation_exceeded_no_state_change() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 50, 1000, 1, 100, b"vest".to_vec());

        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(2), 0, 1),
            Error::<Test>::ExceedsRoundAllocation
        );

        assert!(Presale::contributions(0, 2).is_none());
        assert_eq!(Presale::rounds(0).unwrap().sold, 50);
    });
}

// === GENESIS VALIDATION ===

#[test]
fn test_invariant_create_round_validates_inputs() {
    new_test_ext().execute_with(|| {
        set_block(1);
        assert_noop!(
            Presale::create_round(
                RuntimeOrigin::root(),
                b"test".to_vec(),
                0,
                1000,
                100,
                1,
                100,
                b"vest".to_vec()
            ),
            Error::<Test>::InsufficientPayment
        );
        assert_noop!(
            Presale::create_round(
                RuntimeOrigin::root(),
                b"test".to_vec(),
                5,
                0,
                100,
                1,
                100,
                b"vest".to_vec()
            ),
            Error::<Test>::InsufficientPayment
        );
        assert_noop!(
            Presale::create_round(
                RuntimeOrigin::root(),
                b"test".to_vec(),
                5,
                1000,
                100,
                100,
                100,
                b"vest".to_vec()
            ),
            Error::<Test>::RoundNotStarted
        );
        assert_noop!(
            Presale::create_round(
                RuntimeOrigin::root(),
                vec![0u8; 33],
                5,
                1000,
                100,
                1,
                100,
                b"vest".to_vec()
            ),
            Error::<Test>::LabelTooLong
        );
        assert_noop!(
            Presale::create_round(
                RuntimeOrigin::root(),
                b"test".to_vec(),
                5,
                1000,
                100,
                1,
                100,
                vec![0u8; 65]
            ),
            Error::<Test>::VestingLabelTooLong
        );
    });
}

#[test]
fn test_invariant_empty_vesting_label_rejected() {
    new_test_ext().execute_with(|| {
        set_block(1);
        assert_noop!(
            Presale::create_round(
                RuntimeOrigin::root(),
                b"test".to_vec(),
                5,
                1000,
                100,
                1,
                100,
                vec![],
            ),
            Error::<Test>::EmptyVestingLabel
        );
    });
}

// === PALLET ID / ESCROW CONSISTENCY ===

#[test]
fn test_escrow_account_deterministic() {
    new_test_ext().execute_with(|| {
        let escrow = Presale::escrow_account();
        let expected: u64 = PresalePalletId::get().into_account_truncating();
        assert_eq!(escrow, expected);
    });
}

#[test]
fn test_escrow_account_funded_in_genesis() {
    new_test_ext().execute_with(|| {
        let escrow = escrow_account();
        let balance = Balances::free_balance(escrow);
        assert!(balance > 0);
        assert_eq!(balance, 1_000_000_000_000);
    });
}

// === WHITELIST RESTRICTIONS PER ROUND ===

#[test]
fn test_invariant_whitelist_restrictions_per_round() {
    // H-02 FIX: whitelist_required flag enforces per-round restrictions
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 1000, 100, 1, 100, b"vest".to_vec());
        assert_ok!(Presale::set_whitelist_required(
            RuntimeOrigin::root(),
            0,
            true
        ));
        create_and_activate_round(1, 5, 1000, 100, 1, 100, b"vest".to_vec());

        assert_ok!(Presale::update_whitelist(RuntimeOrigin::root(), 0, 1, true));
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 1, 10));
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(2), 0, 10),
            Error::<Test>::NotWhitelisted
        );
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(2), 1, 10));
    });
}

#[test]
fn test_invariant_duplicate_contribution_no_duplicate_allocation() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 10000, 1000, 1, 100, b"vest".to_vec());

        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
        let contrib1 = Presale::contributions(0, 1).unwrap();

        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
        let contrib2 = Presale::contributions(0, 1).unwrap();

        assert_eq!(contrib2.total_purchased, contrib1.total_purchased + 50);
        assert_eq!(contrib2.total_paid, contrib1.total_paid + 10);
        assert_eq!(Presale::rounds(0).unwrap().sold, 100);
        assert_eq!(Presale::total_sold(), 100);
        assert_eq!(Presale::total_raised(), 20);
    });
}
#[path = "halborn_tests.rs"]
mod halborn_tests;
