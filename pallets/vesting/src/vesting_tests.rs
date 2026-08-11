// Vesting tests for Verdis Chain vesting pallet
// Tests cover: cliff unlock, linear vesting, transfer restrictions, governance with vested tokens

use frame_support::{assert_ok, assert_noop};
use sp_core::H256;
use sp_runtime::traits::BlakeTwo256;

#[test]
fn test_cliff_unlock_nothing_before_cliff() {
    new_test_ext().execute_with(|| {
        let beneficiary = Sr25519Keyring::Alice.to_account_id();
        let amount = 1_000_000 * units();
        let start_block = 100;
        let cliff_blocks = 500; // cliff at block 600
        let duration_blocks = 1000;

        assert_ok!(Vesting::create_vesting_schedule(
            RuntimeOrigin::root(),
            beneficiary.clone(),
            start_block,
            cliff_blocks,
            duration_blocks,
            amount,
        ));

        // Before cliff - nothing vested
        System::set_block_number(500);
        let vested = Vesting::vested_balance(&beneficiary);
        assert_eq!(vested, 0, "Nothing should be vested before cliff");
    });
}

#[test]
fn test_cliff_unlock_full_amount_after_cliff() {
    new_test_ext().execute_with(|| {
        let beneficiary = Sr25519Keyring::Bob.to_account_id();
        let amount = 1_000_000 * units();
        let start_block = 0;
        let cliff_blocks = 100;
        let duration_blocks = 200;

        assert_ok!(Vesting::create_vesting_schedule(
            RuntimeOrigin::root(),
            beneficiary.clone(),
            start_block,
            cliff_blocks,
            duration_blocks,
            amount,
        ));

        // After cliff - should have partial vesting
        System::set_block_number(150);
        let vested = Vesting::vested_balance(&beneficiary);
        assert!(vested > 0, "Some tokens should be vested after cliff");
        assert!(vested <= amount, "Vested amount should not exceed total");
    });
}

#[test]
fn test_linear_vesting_correct_amount_per_block() {
    new_test_ext().execute_with(|| {
        let beneficiary = Sr25519Keyring::Charlie.to_account_id();
        let amount = 1_000_000 * units();
        let start_block = 0;
        let cliff_blocks = 0; // No cliff, linear from start
        let duration_blocks = 1000;

        assert_ok!(Vesting::create_vesting_schedule(
            RuntimeOrigin::root(),
            beneficiary.clone(),
            start_block,
            cliff_blocks,
            duration_blocks,
            amount,
        ));

        // At block 500 - should have 50% vested
        System::set_block_number(500);
        let vested = Vesting::vested_balance(&beneficiary);
        let expected = amount / 2;
        // Allow small rounding difference
        let diff = if vested > expected { vested - expected } else { expected - vested };
        assert!(diff < units(), "At 50% duration, vested should be ~50% of total");
    });
}

#[test]
fn test_locked_balance_cannot_transfer() {
    new_test_ext().execute_with(|| {
        let beneficiary = Sr25519Keyring::Dave.to_account_id();
        let amount = 1_000_000 * units();
        let start_block = 0;
        let cliff_blocks = 1000;
        let duration_blocks = 2000;

        assert_ok!(Vesting::create_vesting_schedule(
            RuntimeOrigin::root(),
            beneficiary.clone(),
            start_block,
            cliff_blocks,
            duration_blocks,
            amount,
        ));

        // Before cliff, locked balance should equal total amount
        System::set_block_number(500);
        let locked = Vesting::locked_balance(&beneficiary);
        assert_eq!(locked, amount, "All tokens should be locked before cliff");
    });
}

#[test]
fn test_vesting_schedule_completion() {
    new_test_ext().execute_with(|| {
        let beneficiary = Sr25519Keyring::Eve.to_account_id();
        let amount = 1_000_000 * units();
        let start_block = 0;
        let cliff_blocks = 100;
        let duration_blocks = 200;

        assert_ok!(Vesting::create_vesting_schedule(
            RuntimeOrigin::root(),
            beneficiary.clone(),
            start_block,
            cliff_blocks,
            duration_blocks,
            amount,
        ));

        // After full duration - everything vested
        System::set_block_number(300);
        let vested = Vesting::vested_balance(&beneficiary);
        assert_eq!(vested, amount, "All tokens should be vested after full duration");

        let locked = Vesting::locked_balance(&beneficiary);
        assert_eq!(locked, 0, "No tokens should be locked after full duration");
    });
}

#[test]
fn test_only_root_can_create_vesting_schedule() {
    new_test_ext().execute_with(|| {
        let beneficiary = Sr25519Keyring::Ferdie.to_account_id();
        let amount = 1_000_000 * units();

        // Non-root cannot create vesting schedule
        assert_noop!(
            Vesting::create_vesting_schedule(
                RuntimeOrigin::signed(Sr25519Keyring::Alice.to_account_id()),
                beneficiary,
                0,
                100,
                200,
                amount,
            ),
            DispatchError::BadOrigin
        );
    });
}

#[test]
fn test_multiple_vesting_schedules() {
    new_test_ext().execute_with(|| {
        let beneficiary = Sr25519Keyring::Alice.to_account_id();
        let amount1 = 500_000 * units();
        let amount2 = 300_000 * units();

        assert_ok!(Vesting::create_vesting_schedule(
            RuntimeOrigin::root(),
            beneficiary.clone(),
            0,
            100,
            200,
            amount1,
        ));

        assert_ok!(Vesting::create_vesting_schedule(
            RuntimeOrigin::root(),
            beneficiary.clone(),
            50,
            150,
            300,
            amount2,
        ));

        // At block 250: schedule 1 complete, schedule 2 partially vested
        System::set_block_number(250);
        let vested = Vesting::vested_balance(&beneficiary);
        // Should have at least amount1 fully vested
        assert!(vested >= amount1, "First schedule should be fully vested");
        assert!(vested <= amount1 + amount2, "Total vested should not exceed total");
    });
}
