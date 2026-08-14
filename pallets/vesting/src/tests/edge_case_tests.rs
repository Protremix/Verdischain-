// Comprehensive edge-case tests for Verdis Chain vesting pallet
// Verifies requirements 1-10 covering cliff boundaries, linear vesting, double claims,
// multi-schedules, transfer/clone restrictions, and chain_spec schedules (Seed, Presale, Team).

use super::*;
use frame_support::{assert_noop, assert_ok};
use frame_support::traits::Currency;
use sp_runtime::DispatchError;

const BLOCKS_PER_DAY: u64 = 17_280;

fn blocks_for_days(days: u64) -> u64 {
    1 + days * BLOCKS_PER_DAY
}

/// Helper to set up chain_spec schedules in storage for testing:
/// Seed: 3B, vesting 730 days, cliff 365 days
/// Presale: 2B, vesting 365 days, cliff 180 days
/// Team: 5B, vesting 1095 days, cliff 365 days
fn setup_chain_spec_schedules() {
    assert_ok!(Vesting::add_schedule(
        RuntimeOrigin::root(),
        bseed_spec.to_vec(),
        3_000_000_000u128,
        730,
        365,
    ));
    assert_ok!(Vesting::add_schedule(
        RuntimeOrigin::root(),
        bpresale_spec.to_vec(),
        2_000_000_000u128,
        365,
        180,
    ));
    assert_ok!(Vesting::add_schedule(
        RuntimeOrigin::root(),
        bteam_spec.to_vec(),
        5_000_000_000u128,
        1095,
        365,
    ));
}

// 1. Claim before cliff → 0 tokens unlocked
#[test]
fn test_edge_case_1_claim_before_cliff_unlocks_zero() {
    new_test_ext().execute_with(|| {
        setup_chain_spec_schedules();
        let alice = Sr25519Keyring::Alice.to_account_id();
        let amount = 3_000_000_000u128;

        assert_ok!(Vesting::assign_vesting(
            RuntimeOrigin::root(),
            alice.clone(),
            bseed_spec.to_vec(),
            amount,
        ));

        // Advance to 364 days (1 day before 365 cliff)
        System::set_block_number(blocks_for_days(364));

        // Attempting to release before cliff fails with NothingToRelease
        assert_noop!(
            Vesting::release_vested(RuntimeOrigin::signed(alice.clone())),
            Error::<Test>::NothingToRelease
        );

        // All 3B tokens remain locked
        assert_eq!(LockedBalances::<Test>::get(&alice), amount);
        let vestings = UserVestings::<Test>::get(&alice).unwrap();
        assert_eq!(vestings[0].released, 0);
    });
}

// 2. Claim exactly at cliff → cliff amount unlocked
#[test]
fn test_edge_case_2_claim_exactly_at_cliff() {
    new_test_ext().execute_with(|| {
        setup_chain_spec_schedules();
        let alice = Sr25519Keyring::Alice.to_account_id();
        let amount = 3_000_000_000u128;

        assert_ok!(Vesting::assign_vesting(
            RuntimeOrigin::root(),
            alice.clone(),
            bseed_spec.to_vec(),
            amount,
        ));

        // Advance to exactly day 365 (cliff)
        System::set_block_number(blocks_for_days(365));

        // Claim at cliff succeeds
        assert_ok!(Vesting::release_vested(RuntimeOrigin::signed(alice.clone())));

        // At day 365 out of 730 total days: vested = 3B * 365 / 730 = 1,500,000,000 (50% cliff portion)
        let expected_released = 1_500_000_000u128;
        let vestings = UserVestings::<Test>::get(&alice).unwrap();
        assert_eq!(vestings[0].released, expected_released);
        assert_eq!(LockedBalances::<Test>::get(&alice), amount - expected_released);
    });
}

// 3. Claim 1 block after cliff → cliff + linear vesting for elapsed time
#[test]
fn test_edge_case_3_claim_one_block_after_cliff() {
    new_test_ext().execute_with(|| {
        setup_chain_spec_schedules();
        let alice = Sr25519Keyring::Alice.to_account_id();
        let amount = 3_000_000_000u128;

        assert_ok!(Vesting::assign_vesting(
            RuntimeOrigin::root(),
            alice.clone(),
            bseed_spec.to_vec(),
            amount,
        ));

        // Advance to 1 block after cliff: 1 + 365 * 17280 + 1
        System::set_block_number(blocks_for_days(365) + 1);

        // First claim releases cliff amount (elapsed_days = 365)
        assert_ok!(Vesting::release_vested(RuntimeOrigin::signed(alice.clone())));
        let vestings = UserVestings::<Test>::get(&alice).unwrap();
        assert_eq!(vestings[0].released, 1_500_000_000u128);

        // Advance to 1 full day after cliff: day 366
        System::set_block_number(blocks_for_days(366));

        // Claim again: releases additional 1 day of linear vesting
        assert_ok!(Vesting::release_vested(RuntimeOrigin::signed(alice.clone())));
        // Day 366 of 730: vested = 3B * 366 / 730 = 1,504,109,589
        let expected_total_released = 3_000_000_000u128 * 366 / 730;
        let vestings = UserVestings::<Test>::get(&alice).unwrap();
        assert_eq!(vestings[0].released, expected_total_released);
        assert_eq!(expected_total_released - 1_500_000_000u128, 4_109_589u128);
    });
}

// 4. Claim at cliff + duration/2 → cliff + half of linear portion
#[test]
fn test_edge_case_4_claim_at_cliff_plus_half_duration() {
    new_test_ext().execute_with(|| {
        setup_chain_spec_schedules();
        let alice = Sr25519Keyring::Alice.to_account_id();
        let amount = 3_000_000_000u128;

        assert_ok!(Vesting::assign_vesting(
            RuntimeOrigin::root(),
            alice.clone(),
            bseed_spec.to_vec(),
            amount,
        ));

        // Seed: cliff = 365 days, duration = 365 days.
        // Cliff + half duration = 365 + 182 = 547 days.
        System::set_block_number(blocks_for_days(547));

        assert_ok!(Vesting::release_vested(RuntimeOrigin::signed(alice.clone())));

        // At day 547 of 730: vested = 3B * 547 / 730 = 2,247,945,205
        // This is cliff (1.5B) + half of linear portion (747,945,205)
        let expected_released = 3_000_000_000u128 * 547 / 730;
        let vestings = UserVestings::<Test>::get(&alice).unwrap();
        assert_eq!(vestings[0].released, expected_released);
        assert_eq!(LockedBalances::<Test>::get(&alice), amount - expected_released);
    });
}

// 5. Claim at cliff + full duration → 100% unlocked
#[test]
fn test_edge_case_5_claim_at_cliff_plus_full_duration() {
    new_test_ext().execute_with(|| {
        setup_chain_spec_schedules();
        let alice = Sr25519Keyring::Alice.to_account_id();
        let amount = 3_000_000_000u128;

        assert_ok!(Vesting::assign_vesting(
            RuntimeOrigin::root(),
            alice.clone(),
            bseed_spec.to_vec(),
            amount,
        ));

        // Seed: cliff 365 + full duration 365 = 730 days
        System::set_block_number(blocks_for_days(730));

        assert_ok!(Vesting::release_vested(RuntimeOrigin::signed(alice.clone())));

        // 100% unlocked
        assert_eq!(LockedBalances::<Test>::get(&alice), 0);
        let vestings = UserVestings::<Test>::get(&alice).unwrap();
        assert_eq!(vestings[0].released, amount);
    });
}

// 6. Claim after full duration → 100% unlocked (no inflation)
#[test]
fn test_edge_case_6_claim_after_full_duration_no_inflation() {
    new_test_ext().execute_with(|| {
        setup_chain_spec_schedules();
        let alice = Sr25519Keyring::Alice.to_account_id();
        let amount = 3_000_000_000u128;

        assert_ok!(Vesting::assign_vesting(
            RuntimeOrigin::root(),
            alice.clone(),
            bseed_spec.to_vec(),
            amount,
        ));

        // Advance far past full duration: day 2000
        System::set_block_number(blocks_for_days(2000));

        assert_ok!(Vesting::release_vested(RuntimeOrigin::signed(alice.clone())));

        // Exactly 100% unlocked (3B), locked balance is 0
        assert_eq!(LockedBalances::<Test>::get(&alice), 0);
        let vestings = UserVestings::<Test>::get(&alice).unwrap();
        assert_eq!(vestings[0].released, amount);

        // Advance even further: day 3000
        System::set_block_number(blocks_for_days(3000));

        // Subsequent release fails with NothingToRelease (no inflation, no extra tokens)
        assert_noop!(
            Vesting::release_vested(RuntimeOrigin::signed(alice.clone())),
            Error::<Test>::NothingToRelease
        );
        let vestings = UserVestings::<Test>::get(&alice).unwrap();
        assert_eq!(vestings[0].released, amount);
    });
}

// 7. Double claim (claim twice at same block) → second claim gives 0
#[test]
fn test_edge_case_7_double_claim_same_block() {
    new_test_ext().execute_with(|| {
        setup_chain_spec_schedules();
        let alice = Sr25519Keyring::Alice.to_account_id();
        let amount = 3_000_000_000u128;

        assert_ok!(Vesting::assign_vesting(
            RuntimeOrigin::root(),
            alice.clone(),
            bseed_spec.to_vec(),
            amount,
        ));

        // Advance to day 400
        System::set_block_number(blocks_for_days(400));

        // First claim succeeds
        assert_ok!(Vesting::release_vested(RuntimeOrigin::signed(alice.clone())));
        let released_first = UserVestings::<Test>::get(&alice).unwrap()[0].released;

        // Second claim at exact same block fails with NothingToRelease
        assert_noop!(
            Vesting::release_vested(RuntimeOrigin::signed(alice.clone())),
            Error::<Test>::NothingToRelease
        );

        let released_second = UserVestings::<Test>::get(&alice).unwrap()[0].released;
        assert_eq!(released_first, released_second);
    });
}

// 8. Claim with no vested amount → error
#[test]
fn test_edge_case_8_claim_with_no_vested_amount_returns_error() {
    new_test_ext().execute_with(|| {
        let alice = Sr25519Keyring::Alice.to_account_id();
        let bob = Sr25519Keyring::Bob.to_account_id();

        // Case A: Account with no vesting assigned at all
        assert_noop!(
            Vesting::release_vested(RuntimeOrigin::signed(bob)),
            Error::<Test>::NoVestingForAccount
        );

        // Case B: Account assigned vesting, but before cliff
        setup_chain_spec_schedules();
        assert_ok!(Vesting::assign_vesting(
            RuntimeOrigin::root(),
            alice.clone(),
            bseed_spec.to_vec(),
            1_000_000u128,
        ));
        System::set_block_number(blocks_for_days(10));
        assert_noop!(
            Vesting::release_vested(RuntimeOrigin::signed(alice)),
            Error::<Test>::NothingToRelease
        );
    });
}

// 9. Multiple schedules for same beneficiary → each tracked independently
#[test]
fn test_edge_case_9_multiple_schedules_tracked_independently() {
    new_test_ext().execute_with(|| {
        setup_chain_spec_schedules();
        let alice = Sr25519Keyring::Alice.to_account_id();

        // Assign Seed (3B), Presale (2B), Team (5B)
        assert_ok!(Vesting::assign_vesting(
            RuntimeOrigin::root(),
            alice.clone(),
            bseed_spec.to_vec(),
            3_000_000_000u128,
        ));
        assert_ok!(Vesting::assign_vesting(
            RuntimeOrigin::root(),
            alice.clone(),
            bpresale_spec.to_vec(),
            2_000_000_000u128,
        ));
        assert_ok!(Vesting::assign_vesting(
            RuntimeOrigin::root(),
            alice.clone(),
            bteam_spec.to_vec(),
            5_000_000_000u128,
        ));

        // Total locked initially = 10B
        assert_eq!(LockedBalances::<Test>::get(&alice), 10_000_000_000u128);

        // Advance to day 200:
        // - Seed (cliff 365): 0 vested
        // - Presale (cliff 180, vesting 365): 2B * 200 / 365 = 1,095,890,410 vested
        // - Team (cliff 365): 0 vested
        System::set_block_number(blocks_for_days(200));

        assert_ok!(Vesting::release_vested(RuntimeOrigin::signed(alice.clone())));

        let vestings = UserVestings::<Test>::get(&alice).unwrap();
        assert_eq!(vestings.len(), 3);
        assert_eq!(vestings[0].released, 0, Seed released should be 0);
        assert_eq!(vestings[1].released, 1_095_890,410u128, Presale released should be ~1.09B);
        assert_eq!(vestings[2].released, 0, Team released should be 0);

        // Advance to day 400:
        // - Seed (cliff 365, vesting 730): 3B * 400 / 730 = 1,643,835,616
        // - Presale (vesting 365): fully vested (2B)
        // - Team (cliff 365, vesting 1095): 5B * 400 / 1095 = 1,826,484,018
        System::set_block_number(blocks_for_days(400));

        assert_ok!(Vesting::release_vested(RuntimeOrigin::signed(alice.clone())));

        let vestings = UserVestings::<Test>::get(&alice).unwrap();
        assert_eq!(vestings[0].released, 1_643_835_616u128);
        assert_eq!(vestings[1].released, 2_000_000_000u128);
        assert_eq!(vestings[2].released, 1_826,484,018u128);
    });
}

// 10. Transfer/clone of vesting schedule → not allowed / properly handled
#[test]
fn test_edge_case_10_transfer_and_clone_handling() {
    new_test_ext().execute_with(|| {
        setup_chain_spec_schedules();
        let alice = Sr25519Keyring::Alice.to_account_id();
        let bob = Sr25519Keyring::Bob.to_account_id();

        // Assign 1B vesting to Alice (Alice has genesis balance of 1B)
        assert_ok!(Vesting::assign_vesting(
            RuntimeOrigin::root(),
            alice.clone(),
            bseed_spec.to_vec(),
            1_000_000_000u128,
        ));

        // Alice cannot transfer locked balance to Bob
        assert_noop!(
            Balances::transfer_allow_death(RuntimeOrigin::signed(alice.clone()), bob.clone(), 500_000_000),
            pallet_balances::Error::<Test>::LiquidityRestrictions
        );

        // Non-root user (Alice) cannot assign/transfer vesting to another account
        assert_noop!(
            Vesting::assign_vesting(
                RuntimeOrigin::signed(alice.clone()),
                bob.clone(),
                bseed_spec.to_vec(),
                100_000u128,
            ),
            DispatchError::BadOrigin
        );

        // Max vesting schedules limit per account enforced
        for i in 0..8 {
            let label = format!(sched_{}, i).into_bytes();
            assert_ok!(Vesting::add_schedule(
                RuntimeOrigin::root(),
                label.clone(),
                100_000u128,
                365,
                30,
            ));
            assert_ok!(Vesting::assign_vesting(
                RuntimeOrigin::root(),
                alice.clone(),
                label,
                100_000u128,
            ));
        }

        // 1 (seed) + 8 = 9 schedules. Assigning 2 more (total 11 > MaxSchedulesPerAccount=10) fails
        assert_ok!(Vesting::add_schedule(
            RuntimeOrigin::root(),
            bsched_8.to_vec(),
            100_000u128,
            365,
            30,
        ));
        assert_ok!(Vesting::assign_vesting(
            RuntimeOrigin::root(),
            alice.clone(),
            bsched_8.to_vec(),
            100_000u128,
        ));

        assert_ok!(Vesting::add_schedule(
            RuntimeOrigin::root(),
            bsched_9.to_vec(),
            100_000u128,
            365,
            30,
        ));
        assert_noop!(
            Vesting::assign_vesting(
                RuntimeOrigin::root(),
                alice.clone(),
                bsched_9.to_vec(),
                100_000u128,
            ),
            Error::<Test>::MaxVestingSchedules
        );
    });
}

// Dedicated test for Presale schedule from chain_spec (2B, cliff 180, vesting 365)
#[test]
fn test_presale_schedule_flow() {
    new_test_ext().execute_with(|| {
        setup_chain_spec_schedules();
        let alice = Sr25519Keyring::Alice.to_account_id();
        let amount = 2_000_000_000u128;

        assert_ok!(Vesting::assign_vesting(
            RuntimeOrigin::root(),
            alice.clone(),
            bpresale_spec.to_vec(),
            amount,
        ));

        // Before cliff (day 179) -> NothingToRelease
        System::set_block_number(blocks_for_days(179));
        assert_noop!(
            Vesting::release_vested(RuntimeOrigin::signed(alice.clone())),
            Error::<Test>::NothingToRelease
        );

        // At cliff (day 180) -> vested = 2B * 180 / 365 = 986,301,369
        System::set_block_number(blocks_for_days(180));
        assert_ok!(Vesting::release_vested(RuntimeOrigin::signed(alice.clone())));
        let vestings = UserVestings::<Test>::get(&alice).unwrap();
        assert_eq!(vestings[0].released, 986_301,369u128);

        // At full vesting (day 365) -> 100% (2B)
        System::set_block_number(blocks_for_days(365));
        assert_ok!(Vesting::release_vested(RuntimeOrigin::signed(alice.clone())));
        assert_eq!(LockedBalances::<Test>::get(&alice), 0);
    });
}

// Dedicated test for Team schedule from chain_spec (5B, cliff 365, vesting 1095)
#[test]
fn test_team_schedule_flow() {
    new_test_ext().execute_with(|| {
        setup_chain_spec_schedules();
        let alice = Sr25519Keyring::Alice.to_account_id();
        let amount = 5_000_000_000u128;

        assert_ok!(Vesting::assign_vesting(
            RuntimeOrigin::root(),
            alice.clone(),
            bteam_spec.to_vec(),
            amount,
        ));

        // Before cliff (day 364) -> NothingToRelease
        System::set_block_number(blocks_for_days(364));
        assert_noop!(
            Vesting::release_vested(RuntimeOrigin::signed(alice.clone())),
            Error::<Test>::NothingToRelease
        );

        // At cliff (day 365) -> vested = 5B * 365 / 1095 = 1,666,666,666
        System::set_block_number(blocks_for_days(365));
        assert_ok!(Vesting::release_vested(RuntimeOrigin::signed(alice.clone())));
        let vestings = UserVestings::<Test>::get(&alice).unwrap();
        assert_eq!(vestings[0].released, 1_666_666_666u128);

        // At full vesting (day 1095) -> 100% (5B)
        System::set_block_number(blocks_for_days(1095));
        assert_ok!(Vesting::release_vested(RuntimeOrigin::signed(alice.clone())));
        assert_eq!(LockedBalances::<Test>::get(&alice), 0);
    });
}
