#![allow(unused_imports)]
use crate::*;
use frame_support::{
    assert_noop, assert_ok, construct_runtime, derive_impl, parameter_types,
    traits::{ConstU32, ConstU64},
};
use sp_io::TestExternalities;
use sp_runtime::{traits::IdentityLookup, BuildStorage};

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
}

impl crate::Config for Test {
    type RuntimeEvent = RuntimeEvent;
    type Currency = Balances;
    type PalletId = PresalePalletId;
    type AdminOrigin = frame_system::EnsureRoot<u64>;
    type Vesting = (); // no-op vesting handler for presale-only tests
    type WeightInfo = crate::SubstrateWeight<Test>;
}

// === Test setup ===

pub fn new_test_ext() -> TestExternalities {
    let mut t = frame_system::GenesisConfig::<Test>::default()
        .build_storage()
        .unwrap();
    pallet_balances::GenesisConfig::<Test> {
        dev_accounts: None,
        balances: vec![(1, 1_000_000_000), (2, 1_000_000_000), (3, 1_000_000_000)],
    }
    .assimilate_storage(&mut t)
    .unwrap();
    TestExternalities::new(t)
}

fn set_block(n: u64) {
    System::set_block_number(n);
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

// === Existing tests (updated for per-round storage) ===

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
        create_and_activate_round(0, 5, 1000, 100, 1, 100, vec![]);
        assert!(Presale::rounds(0).unwrap().is_active);
        assert_ok!(Presale::deactivate_round(RuntimeOrigin::root(), 0));
        assert!(!Presale::rounds(0).unwrap().is_active);
    });
}

#[test]
fn test_contribute_to_round() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 1000, 100, 1, 100, vec![]);
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
        create_and_activate_round(0, 5, 10000, 100, 1, 100, vec![]);
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 20)); // 100 tokens
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
        create_and_activate_round(0, 5, 50, 1000, 1, 100, vec![]);
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10)); // 50 tokens
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
            vec![],
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
        create_and_activate_round(0, 5, 1000, 100, 50, 100, vec![]);
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
        create_and_activate_round(0, 5, 1000, 100, 1, 100, vec![]);
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
        create_and_activate_round(0, 5, 1000, 100, 1, 100, vec![]);
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
        create_and_activate_round(0, 5, 1000, 100, 1, 100, vec![]);
        assert_ok!(Presale::update_whitelist(RuntimeOrigin::root(), 0, 1, true));
        // Whitelisted user can contribute
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
        // Non-whitelisted user cannot
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
        create_and_activate_round(0, 5, 1000, 100, 1, 100, vec![]);
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
        create_and_activate_round(0, 5, 10000, 1000, 1, 100, vec![]);
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(2), 0, 20));
        assert_eq!(Presale::total_raised(), 30);
        assert_eq!(Presale::total_sold(), 150); // 10*5 + 20*5
    });
}

// === P0: Per-round cap independence ===

#[test]
fn test_per_round_cap_independence() {
    new_test_ext().execute_with(|| {
        set_block(1);
        // Round A: cap=100 tokens, price=5
        create_and_activate_round(0, 5, 10000, 100, 1, 100, vec![]);
        // Round B: cap=100 tokens, price=5
        create_and_activate_round(1, 5, 10000, 100, 1, 100, vec![]);

        // User 1 buys 100 tokens (cap) in Round A
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 20));
        let contrib_a = Presale::contributions(0, 1).unwrap();
        assert_eq!(contrib_a.total_purchased, 100);

        // Same user can still buy 100 tokens in Round B
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 1, 20));
        let contrib_b = Presale::contributions(1, 1).unwrap();
        assert_eq!(contrib_b.total_purchased, 100);

        // Verify independence: Round A cap is NOT affected by Round B
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(1), 0, 1),
            Error::<Test>::ExceedsPerAccountCap
        );
    });
}

// === P0: Per-round whitelist independence ===

#[test]
fn test_per_round_whitelist_independence() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 1000, 100, 1, 100, vec![]);
        create_and_activate_round(1, 5, 1000, 100, 1, 100, vec![]);

        // Round A: whitelist Alice (user 1)
        assert_ok!(Presale::update_whitelist(RuntimeOrigin::root(), 0, 1, true));
        // Round B: whitelist Bob (user 2)
        assert_ok!(Presale::update_whitelist(RuntimeOrigin::root(), 1, 2, true));

        // Alice allowed in A, not in B
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(1), 1, 10),
            Error::<Test>::NotWhitelisted
        );

        // Bob allowed in B, not in A
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(2), 1, 10));
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(2), 0, 10),
            Error::<Test>::NotWhitelisted
        );
    });
}

#[test]
fn test_public_round_no_whitelist() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 1000, 100, 1, 100, vec![]);
        // No whitelist entries → round is public
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(2), 0, 10));
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(3), 0, 10));
    });
}

// === P0: Economic invariants ===

#[test]
fn test_invariant_total_sold_cannot_exceed_allocation() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 50, 1000, 1, 100, vec![]); // allocation=50 tokens
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10)); // 50 tokens
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(2), 0, 1),
            Error::<Test>::ExceedsRoundAllocation
        );
    });
}

#[test]
fn test_invariant_user_cannot_exceed_per_round_cap() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 10000, 50, 1, 100, vec![]); // cap=50 tokens
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10)); // 50 tokens
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(1), 0, 1),
            Error::<Test>::ExceedsPerAccountCap
        );
    });
}

#[test]
fn test_invariant_multiple_rounds_independent_caps() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 1, 10000, 100, 1, 100, vec![]);
        create_and_activate_round(1, 1, 10000, 100, 1, 100, vec![]);
        create_and_activate_round(2, 1, 10000, 100, 1, 100, vec![]);

        for rid in 0..3u32 {
            assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), rid, 100));
        }
        // Each round independently allows 100
        for rid in 0..3u32 {
            assert_noop!(
                Presale::contribute(RuntimeOrigin::signed(1), rid, 1),
                Error::<Test>::ExceedsPerAccountCap
            );
        }
    });
}

#[test]
fn test_invariant_payment_cannot_be_zero() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 1000, 100, 1, 100, vec![]);
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(1), 0, 0),
            Error::<Test>::ZeroPayment
        );
    });
}

#[test]
fn test_invariant_token_calculation_cannot_overflow() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, u64::MAX, 10000, u64::MAX, 1, 100, vec![]);
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(1), 0, 2),
            Error::<Test>::CalculationOverflow
        );
    });
}

#[test]
fn test_invariant_total_sold_consistent() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 10000, 1000, 1, 100, vec![]);
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(2), 0, 20));
        assert_eq!(Presale::total_sold(), 150);
        assert_eq!(Presale::rounds(0).unwrap().sold, 150);
    });
}

#[test]
fn test_invariant_total_raised_consistent() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 10000, 1000, 1, 100, vec![]);
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(2), 0, 20));
        assert_eq!(Presale::total_raised(), 30);
    });
}

#[test]
fn test_invariant_failed_contribution_changes_no_state() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 10000, 50, 1, 100, vec![]);

        // Succeed
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10)); // 50 tokens = cap
        let sold_before = Presale::rounds(0).unwrap().sold;
        let raised_before = Presale::total_raised();
        let bal_before = pallet_balances::Pallet::<Test>::free_balance(1);

        // Fail (exceeds cap)
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(1), 0, 1),
            Error::<Test>::ExceedsPerAccountCap
        );

        // Nothing changed
        assert_eq!(Presale::rounds(0).unwrap().sold, sold_before);
        assert_eq!(Presale::total_raised(), raised_before);
        assert_eq!(
            pallet_balances::Pallet::<Test>::free_balance(1),
            bal_before
        );
    });
}

#[test]
fn test_invariant_paused_rejects_contributions() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 1000, 100, 1, 100, vec![]);
        assert_ok!(Presale::set_paused(RuntimeOrigin::root(), true));
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(1), 0, 10),
            Error::<Test>::Paused
        );
    });
}

#[test]
fn test_invariant_expired_round_rejects() {
    new_test_ext().execute_with(|| {
        set_block(200);
        create_and_activate_round(0, 5, 1000, 100, 1, 100, vec![]);
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(1), 0, 10),
            Error::<Test>::RoundEnded
        );
    });
}

#[test]
fn test_invariant_before_start_rejects() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 1000, 100, 50, 100, vec![]);
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(1), 0, 10),
            Error::<Test>::RoundNotStarted
        );
    });
}

#[test]
fn test_invariant_unauthorized_admin_calls_reject() {
    new_test_ext().execute_with(|| {
        set_block(1);
        // Non-admin cannot create round
        assert_noop!(
            Presale::create_round(
                RuntimeOrigin::signed(1),
                b"test".to_vec(),
                5,
                1000,
                100,
                1,
                100,
                vec![],
            ),
            sp_runtime::DispatchError::BadOrigin
        );
        // Non-admin cannot activate
        assert_ok!(Presale::create_round(
            RuntimeOrigin::root(),
            b"test".to_vec(),
            5,
            1000,
            100,
            1,
            100,
            vec![],
        ));
        assert_noop!(
            Presale::activate_round(RuntimeOrigin::signed(1), 0),
            sp_runtime::DispatchError::BadOrigin
        );
        // Non-admin cannot pause
        assert_noop!(
            Presale::set_paused(RuntimeOrigin::signed(1), true),
            sp_runtime::DispatchError::BadOrigin
        );
        // Non-admin cannot update whitelist
        assert_noop!(
            Presale::update_whitelist(RuntimeOrigin::signed(1), 0, 1, true),
            sp_runtime::DispatchError::BadOrigin
        );
    });
}

#[test]
fn test_invariant_whitelist_restrictions_per_round() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 1000, 100, 1, 100, vec![]);
        create_and_activate_round(1, 5, 1000, 100, 1, 100, vec![]);

        // Only round 0 has whitelist for user 1
        assert_ok!(Presale::update_whitelist(RuntimeOrigin::root(), 0, 1, true));

        // User 1 can contribute to round 0
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
        // User 1 CAN contribute to round 1 (no whitelist = public)
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 1, 10));
        // User 2 cannot contribute to round 0 (not whitelisted)
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(2), 0, 10),
            Error::<Test>::NotWhitelisted
        );
        // User 2 CAN contribute to round 1 (no whitelist = public)
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(2), 1, 10));
    });
}

#[test]
fn test_invariant_duplicate_contribution_no_duplicate_allocation() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 10000, 1000, 1, 100, vec![]);

        // First contribution
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
        let contrib1 = Presale::contributions(0, 1).unwrap();

        // Second contribution (legitimate, not duplicate)
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
        let contrib2 = Presale::contributions(0, 1).unwrap();

        // Total purchased should be cumulative, not duplicated beyond payment
        assert_eq!(contrib2.total_purchased, contrib1.total_purchased + 50);
        assert_eq!(contrib2.total_paid, contrib1.total_paid + 10);

        // Round sold should match sum of contributions
        assert_eq!(Presale::rounds(0).unwrap().sold, 100); // 50 + 50
        assert_eq!(Presale::total_sold(), 100);
        assert_eq!(Presale::total_raised(), 20);
    });
}

#[test]
fn test_invariant_create_round_validates_inputs() {
    new_test_ext().execute_with(|| {
        set_block(1);
        // Zero price fails
        assert_noop!(
            Presale::create_round(
                RuntimeOrigin::root(),
                b"test".to_vec(),
                0,
                1000,
                100,
                1,
                100,
                vec![]
            ),
            Error::<Test>::InsufficientPayment
        );
        // Zero allocation fails
        assert_noop!(
            Presale::create_round(
                RuntimeOrigin::root(),
                b"test".to_vec(),
                5,
                0,
                100,
                1,
                100,
                vec![]
            ),
            Error::<Test>::InsufficientPayment
        );
        // end <= start fails
        assert_noop!(
            Presale::create_round(
                RuntimeOrigin::root(),
                b"test".to_vec(),
                5,
                1000,
                100,
                100,
                100,
                vec![]
            ),
            Error::<Test>::RoundNotStarted
        );
        // Label too long fails
        assert_noop!(
            Presale::create_round(
                RuntimeOrigin::root(),
                vec![0u8; 33],
                5,
                1000,
                100,
                1,
                100,
                vec![]
            ),
            Error::<Test>::LabelTooLong
        );
        // Vesting label too long fails
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
fn test_invariant_no_vesting_label_no_vesting_created() {
    new_test_ext().execute_with(|| {
        set_block(1);
        // Round with empty vesting label — contribution should succeed without vesting
        create_and_activate_round(0, 5, 1000, 100, 1, 100, vec![]);
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
        let contrib = Presale::contributions(0, 1).unwrap();
        assert_eq!(contrib.total_purchased, 50);
        assert_eq!(contrib.total_paid, 10);
    });
}
