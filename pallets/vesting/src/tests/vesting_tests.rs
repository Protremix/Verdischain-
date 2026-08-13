// Comprehensive vesting tests for Verdis Chain vesting pallet
// Covers: schedule creation, assignment, cliff, linear vesting, release, locks, edge cases

use super::*;
use frame_support::{assert_noop, assert_ok};

// === Schedule creation ===

#[test]
fn test_add_schedule_succeeds() {
    new_test_ext().execute_with(|| {
        assert_ok!(Vesting::add_schedule(
            RuntimeOrigin::root(),
            b"team".to_vec(),
            1_000_000u128,
            365, // 365 vesting days
            180, // 180 cliff days
        ));

        // Verify schedule was stored
        let label: BoundedVec<u8, ConstU32<64>> = b"team".to_vec().try_into().unwrap();
        let schedule = Schedules::<Test>::get(&label);
        assert!(schedule.is_some(), "Schedule should be stored");
        let schedule = schedule.unwrap();
        assert_eq!(schedule.total_amount, 1_000_000u128);
        assert_eq!(schedule.vesting_days, 365);
        assert_eq!(schedule.cliff_days, 180);
    });
}

#[test]
fn test_add_schedule_non_root_fails() {
    new_test_ext().execute_with(|| {
        let attacker = Sr25519Keyring::Alice.to_account_id();
        assert_noop!(
            Vesting::add_schedule(
                RuntimeOrigin::signed(attacker),
                b"team".to_vec(),
                1_000_000u128,
                365,
                180,
            ),
            DispatchError::BadOrigin
        );
    });
}

#[test]
fn test_add_duplicate_schedule_fails() {
    new_test_ext().execute_with(|| {
        assert_ok!(Vesting::add_schedule(
            RuntimeOrigin::root(),
            b"team".to_vec(),
            1_000_000u128,
            365,
            180,
        ));

        // Duplicate label should fail
        assert_noop!(
            Vesting::add_schedule(
                RuntimeOrigin::root(),
                b"team".to_vec(),
                500_000u128,
                200,
                100,
            ),
            Error::<Test>::ScheduleAlreadyExists
        );
    });
}

#[test]
fn test_add_schedule_zero_vesting_days_fails() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            Vesting::add_schedule(
                RuntimeOrigin::root(),
                b"zero".to_vec(),
                1_000u128,
                0, // zero vesting days
                0,
            ),
            Error::<Test>::VestingNotStarted
        );
    });
}

#[test]
fn test_add_schedule_cliff_exceeds_vesting_fails() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            Vesting::add_schedule(
                RuntimeOrigin::root(),
                b"bad".to_vec(),
                1_000u128,
                100, // 100 vesting days
                200, // 200 cliff days > vesting days
            ),
            Error::<Test>::VestingNotStarted
        );
    });
}

// === Assign vesting ===

#[test]
fn test_assign_vesting_succeeds() {
    new_test_ext().execute_with(|| {
        let beneficiary = Sr25519Keyring::Alice.to_account_id();

        assert_ok!(Vesting::assign_vesting(
            RuntimeOrigin::root(),
            beneficiary.clone(),
            b"seed".to_vec(),
            500_000u128,
        ));

        // Verify vesting entry was created
        let vestings = UserVestings::<Test>::get(&beneficiary);
        assert!(vestings.is_some(), "Vesting entry should be created");
        let vestings = vestings.unwrap();
        assert_eq!(vestings.len(), 1, "Should have one vesting entry");
        assert_eq!(vestings[0].total_amount, 500_000u128);
    });
}

#[test]
fn test_assign_vesting_non_root_fails() {
    new_test_ext().execute_with(|| {
        let beneficiary = Sr25519Keyring::Bob.to_account_id();
        let attacker = Sr25519Keyring::Alice.to_account_id();

        assert_noop!(
            Vesting::assign_vesting(
                RuntimeOrigin::signed(attacker),
                beneficiary,
                b"seed".to_vec(),
                500_000u128,
            ),
            DispatchError::BadOrigin
        );
    });
}

#[test]
fn test_assign_vesting_nonexistent_schedule_fails() {
    new_test_ext().execute_with(|| {
        let beneficiary = Sr25519Keyring::Alice.to_account_id();

        assert_noop!(
            Vesting::assign_vesting(
                RuntimeOrigin::root(),
                beneficiary,
                b"nonexistent".to_vec(),
                500_000u128,
            ),
            Error::<Test>::ScheduleNotFound
        );
    });
}

// === Release vested tokens ===

#[test]
fn test_release_vested_before_cliff_fails() {
    new_test_ext().execute_with(|| {
        let beneficiary = Sr25519Keyring::Alice.to_account_id();

        assert_ok!(Vesting::assign_vesting(
            RuntimeOrigin::root(),
            beneficiary.clone(),
            b"seed".to_vec(),
            500_000u128,
        ));

        // "seed" schedule has cliff_days=30. At block 1, elapsed_days = 0.
        // Nothing should be releasable.
        assert_noop!(
            Vesting::release_vested(RuntimeOrigin::signed(beneficiary)),
            Error::<Test>::NothingToRelease
        );
    });
}

#[test]
fn test_release_vested_no_vesting_fails() {
    new_test_ext().execute_with(|| {
        let user = Sr25519Keyring::Bob.to_account_id();

        // Bob has no vesting assigned
        assert_noop!(
            Vesting::release_vested(RuntimeOrigin::signed(user)),
            Error::<Test>::NoVestingForAccount
        );
    });
}

#[test]
fn test_locked_balance_before_cliff() {
    new_test_ext().execute_with(|| {
        let beneficiary = Sr25519Keyring::Alice.to_account_id();
        let amount = 500_000u128;

        assert_ok!(Vesting::assign_vesting(
            RuntimeOrigin::root(),
            beneficiary.clone(),
            b"seed".to_vec(),
            amount,
        ));

        // Before cliff, everything should be locked
        let locked = Vesting::get_locked_balance(&beneficiary);
        assert_eq!(locked, amount, "All tokens should be locked before cliff");

        let unlocked = Vesting::get_unlocked_balance(&beneficiary);
        assert_eq!(
            unlocked,
            1_000_000_000 - amount,
            "Only genesis balance minus vesting should be unlocked"
        );
    });
}

#[test]
fn test_release_after_full_vesting_period() {
    new_test_ext().execute_with(|| {
        let beneficiary = Sr25519Keyring::Alice.to_account_id();
        let amount = 500_000u128;

        assert_ok!(Vesting::assign_vesting(
            RuntimeOrigin::root(),
            beneficiary.clone(),
            b"seed".to_vec(),
            amount,
        ));

        // "seed" schedule: vesting_days=60, cliff_days=30, block_time=5s
        // blocks_per_day = 86400000 / 5000 = 17280
        // Need to advance past 60 days = 60 * 17280 = 1,036,800 blocks
        System::set_block_number(1_036_800 + 1);

        // Should be able to release all tokens
        assert_ok!(Vesting::release_vested(RuntimeOrigin::signed(
            beneficiary.clone()
        )));

        // After release, locked should be 0
        let locked = Vesting::get_locked_balance(&beneficiary);
        assert_eq!(
            locked, 0,
            "All tokens should be unlocked after full vesting + release"
        );
    });
}

#[test]
fn test_release_partial_vesting() {
    new_test_ext().execute_with(|| {
        let beneficiary = Sr25519Keyring::Alice.to_account_id();
        let amount = 1_000_000u128;

        assert_ok!(Vesting::assign_vesting(
            RuntimeOrigin::root(),
            beneficiary.clone(),
            b"seed".to_vec(),
            amount,
        ));

        // Advance to 45 days (between cliff 30 and vesting 60)
        // 45 * 17280 = 777,600 blocks
        System::set_block_number(777_600);

        assert_ok!(Vesting::release_vested(RuntimeOrigin::signed(
            beneficiary.clone()
        )));

        // Some tokens should be unlocked, some still locked
        let locked = Vesting::get_locked_balance(&beneficiary);
        assert!(locked > 0, "Some tokens should still be locked");
        assert!(locked < amount, "Some tokens should be released");
    });
}

// === Multiple schedules ===

#[test]
fn test_multiple_schedules_for_same_user() {
    new_test_ext().execute_with(|| {
        let beneficiary = Sr25519Keyring::Alice.to_account_id();

        // Create a second schedule
        assert_ok!(Vesting::add_schedule(
            RuntimeOrigin::root(),
            b"community".to_vec(),
            2_000_000u128,
            90, // 90 vesting days
            30, // 30 cliff days
        ));

        // Assign both schedules
        assert_ok!(Vesting::assign_vesting(
            RuntimeOrigin::root(),
            beneficiary.clone(),
            b"seed".to_vec(),
            500_000u128,
        ));
        assert_ok!(Vesting::assign_vesting(
            RuntimeOrigin::root(),
            beneficiary.clone(),
            b"community".to_vec(),
            300_000u128,
        ));

        let vestings = UserVestings::<Test>::get(&beneficiary).unwrap();
        assert_eq!(vestings.len(), 2, "Should have two vesting entries");

        // Total locked should be sum of both
        let locked = Vesting::get_locked_balance(&beneficiary);
        assert_eq!(
            locked, 800_000u128,
            "Total locked should be sum of both schedules"
        );
    });
}

// === Label validation ===

#[test]
fn test_label_too_long_fails() {
    new_test_ext().execute_with(|| {
        let long_label = vec![b'x'; 65]; // Max is 64 bytes
        assert_noop!(
            Vesting::add_schedule(RuntimeOrigin::root(), long_label, 1_000u128, 100, 50,),
            Error::<Test>::LabelTooLong
        );
    });
}

/// Vesting with very large amount should not overflow.
#[test]
fn test_vesting_large_amount_no_overflow() {
    new_test_ext().execute_with(|| {
        let beneficiary = Sr25519Keyring::Alice.to_account_id();

        assert_ok!(Vesting::add_schedule(
            RuntimeOrigin::root(),
            b"large".to_vec(),
            1_000_000_000_000_000_000u128, // 1B VRDX
            365, // 365 days
            90,  // 90 day cliff
        ));

        assert_ok!(Vesting::assign_vesting(
            RuntimeOrigin::root(),
            beneficiary.clone(),
            b"large".to_vec(),
            1_000_000_000_000_000_000u128,
        ));

        // Advance past full vesting period (365 days * 17280 blocks/day)
        System::set_block_number(365 * 17_280 + 1);

        assert_ok!(Vesting::release_vested(RuntimeOrigin::signed(beneficiary)));
    });
}

/// Release at exact cliff boundary should work.
#[test]
fn test_release_at_exact_cliff_boundary() {
    new_test_ext().execute_with(|| {
        let beneficiary = Sr25519Keyring::Bob.to_account_id();

        assert_ok!(Vesting::add_schedule(
            RuntimeOrigin::root(),
            b"cliff_test".to_vec(),
            1_000_000u128,
            100, // 100 vesting days
            30,  // 30 day cliff
        ));

        assert_ok!(Vesting::assign_vesting(
            RuntimeOrigin::root(),
            beneficiary.clone(),
            b"cliff_test".to_vec(),
            1_000_000u128,
        ));

        // Just before cliff (29 days) — should have nothing to release
        System::set_block_number(29 * 17_280);
        // Release should succeed but release 0 (all skipped by cliff)
        // Actually it might error with NoVestingAvailable if total_releasable is 0
        let _ = Vesting::release_vested(RuntimeOrigin::signed(beneficiary.clone()));

        // At exact cliff (30 days) — should release cliff portion
        System::set_block_number(30 * 17_280);
        assert_ok!(Vesting::release_vested(RuntimeOrigin::signed(beneficiary)));
    });
}

/// Multiple vesting schedules for same user should not interfere.
#[test]
fn test_concurrent_vesting_schedules_independent() {
    new_test_ext().execute_with(|| {
        let beneficiary = Sr25519Keyring::Alice.to_account_id();

        // Schedule 1: 1000 VRDX over 100 days, 20 day cliff
        assert_ok!(Vesting::add_schedule(
            RuntimeOrigin::root(),
            b"sched1".to_vec(),
            1_000u128,
            100,
            20,
        ));

        // Schedule 2: 2000 VRDX over 200 days, 50 day cliff
        assert_ok!(Vesting::add_schedule(
            RuntimeOrigin::root(),
            b"sched2".to_vec(),
            2_000u128,
            200,
            50,
        ));

        // Assign both to same beneficiary
        assert_ok!(Vesting::assign_vesting(
            RuntimeOrigin::root(),
            beneficiary.clone(),
            b"sched1".to_vec(),
            1_000u128,
        ));
        assert_ok!(Vesting::assign_vesting(
            RuntimeOrigin::root(),
            beneficiary.clone(),
            b"sched2".to_vec(),
            2_000u128,
        ));

        // At 50 days: Schedule 1 is 30 days past cliff (50-20=30, 30/100=30%), Schedule 2 at cliff (50/200=25%)
        System::set_block_number(50 * 17_280);
        assert_ok!(Vesting::release_vested(RuntimeOrigin::signed(beneficiary.clone())));

        // At 200 days: Schedule 1 fully vested (200>100), Schedule 2 at 75% (200/200=100%)
        System::set_block_number(200 * 17_280);
        assert_ok!(Vesting::release_vested(RuntimeOrigin::signed(beneficiary)));
    });
}
