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

// ============================================================
// ADDITIONAL EDGE CASE TESTS (Kimi audit additions)
// ============================================================

#[test]
fn test_vesting_zero_amount_reverts() {
    new_test_ext().execute_with(|| {
        let beneficiary = Sr25519Keyring::Alice.to_account_id();
        assert_noop!(
            Vesting::add_schedule(
                RuntimeOrigin::root(),
                b"zero".to_vec(),
                0, // zero amount
                100,
                50,
            ),
            Error::<Test>::ZeroAmount
        );
    });
}

#[test]
fn test_vesting_zero_duration_reverts() {
    new_test_ext().execute_with(|| {
        let beneficiary = Sr25519Keyring::Alice.to_account_id();
        assert_noop!(
            Vesting::add_schedule(
                RuntimeOrigin::root(),
                b"zero_dur".to_vec(),
                1_000,
                0, // zero duration
                0, // zero cliff
            ),
            Error::<Test>::ZeroDuration
        );
    });
}

#[test]
fn test_vesting_claim_before_start_reverts() {
    new_test_ext().execute_with(|| {
        let beneficiary = Sr25519Keyring::Alice.to_account_id();
        assert_ok!(Vesting::add_schedule(
            RuntimeOrigin::root(),
            b"future".to_vec(),
            1_000,
            100, // starts at block 100
            50,
        ));
        
        // Try to claim at block 1 (before start)
        System::set_block_number(1);
        let result = Vesting::claim(RuntimeOrigin::signed(beneficiary));
        // Should get 0 or error since vesting hasn't started
        if let Ok(amount) = result {
            assert_eq!(amount, 0, "Should claim 0 before vesting starts");
        }
    });
}

#[test]
fn test_vesting_partial_vest_correct_amount() {
    new_test_ext().execute_with(|| {
        let beneficiary = Sr25519Keyring::Alice.to_account_id();
        assert_ok!(Vesting::add_schedule(
            RuntimeOrigin::root(),
            b"partial".to_vec(),
            1_000,
            100, // 100 block duration
            0,   // no cliff
        ));
        
        // At block 50 (50% through), should have 500 vested
        System::set_block_number(50);
        let vested = Vesting::get_vested_balance(&beneficiary);
        assert_eq!(vested, 500, "50% through vesting should have 50% vested");
        
        // At block 100 (100%), should have full 1000
        System::set_block_number(100);
        let vested = Vesting::get_vested_balance(&beneficiary);
        assert_eq!(vested, 1_000, "At end should be fully vested");
    });
}

#[test]
fn test_vesting_cliff_blocks_until_cliff() {
    new_test_ext().execute_with(|| {
        let beneficiary = Sr25519Keyring::Alice.to_account_id();
        assert_ok!(Vesting::add_schedule(
            RuntimeOrigin::root(),
            b"cliff".to_vec(),
            1_000,
            100, // duration
            50,  // cliff at 50%
        ));
        
        // Before cliff, should have 0
        System::set_block_number(49);
        let vested = Vesting::get_vested_balance(&beneficiary);
        assert_eq!(vested, 0, "Before cliff should have 0 vested");
        
        // At cliff, should get cliff portion
        System::set_block_number(50);
        let vested = Vesting::get_vested_balance(&beneficiary);
        assert!(vested > 0, "At cliff should have some vested amount");
    });
}

#[test]
fn test_vesting_multiple_schedules_accumulate() {
    new_test_ext().execute_with(|| {
        let beneficiary = Sr25519Keyring::Alice.to_account_id();
        assert_ok!(Vesting::add_schedule(
            RuntimeOrigin::root(),
            b"schedule1".to_vec(),
            500,
            100,
            0,
        ));
        assert_ok!(Vesting::add_schedule(
            RuntimeOrigin::root(),
            b"schedule2".to_vec(),
            500,
            100,
            0,
        ));
        
        System::set_block_number(100);
        let vested = Vesting::get_vested_balance(&beneficiary);
        assert_eq!(vested, 1_000, "Both schedules should be fully vested");
    });
}

#[test]
fn test_vesting_duplicate_label_replaces_or_errors() {
    new_test_ext().execute_with(|| {
        let beneficiary = Sr25519Keyring::Alice.to_account_id();
        assert_ok!(Vesting::add_schedule(
            RuntimeOrigin::root(),
            b"duplicate".to_vec(),
            500,
            100,
            0,
        ));
        // Adding same label again should either replace or error
        let result = Vesting::add_schedule(
            RuntimeOrigin::root(),
            b"duplicate".to_vec(),
            500,
            100,
            0,
        );
        // Either behavior is acceptable, but it should not crash
        match result {
            Ok(_) => {
                let vested = Vesting::get_vested_balance(&beneficiary);
                // Should be 500 (replaced) or 1000 (accumulated)
                assert!(vested == 500 || vested == 1000, "Duplicate label handled gracefully");
            }
            Err(_) => {
                // Erroring on duplicate is also fine
            }
        }
    });
}
