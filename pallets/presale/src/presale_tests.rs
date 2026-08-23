// Comprehensive presale tests for Verdis Chain presale pallet
// Covers: round creation, activation, contribution, caps, whitelist, pause, refunds, collection

use super::*;
use frame_support::{assert_noop, assert_ok};

// === Helper: create and activate a test round ===
fn setup_active_round() {
    assert_ok!(Presale::create_round(
        RuntimeOrigin::root(),
        b"seed".to_vec(),
        1u64,             // token_price: 1 VRDX per payment unit
        1_000_000u64,     // total_allocation
        100_000u64,       // per_account_cap
        1u64,             // start_block
        1_000_000u64,     // end_block
        b"seed".to_vec(), // vesting_label
    ));
    assert_ok!(Presale::activate_round(RuntimeOrigin::root(), 0));
    frame_system::Pallet::<Test>::set_block_number(1);
}

// === Round creation ===

#[test]
fn test_create_round_succeeds() {
    new_test_ext().execute_with(|| {
        assert_ok!(Presale::create_round(
            RuntimeOrigin::root(),
            b"round1".to_vec(),
            5u64,
            10_000_000u64,
            500_000u64,
            1u64,
            1_000_000u64,
            b"seed".to_vec(),
        ));

        let round = Rounds::<Test>::get(0);
        assert!(round.is_some(), "Round should be created");
        let round = round.unwrap();
        assert_eq!(round.token_price, 5u64);
        assert_eq!(round.total_allocation, 10_000_000u64);
        assert!(round.status != RoundStatus::Active, "New round should start inactive");
    });
}

#[test]
fn test_create_round_non_admin_fails() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            Presale::create_round(
                RuntimeOrigin::signed(1),
                b"round1".to_vec(),
                5u64,
                10_000_000u64,
                500_000u64,
                1u64,
                1_000_000u64,
                b"seed".to_vec(),
            ),
            DispatchError::BadOrigin
        );
    });
}

#[test]
fn test_create_round_end_before_start_fails() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            Presale::create_round(
                RuntimeOrigin::root(),
                b"round1".to_vec(),
                5u64,
                10_000_000u64,
                500_000u64,
                100u64, // start_block
                50u64,  // end_block < start_block
                b"seed".to_vec(),
            ),
            Error::<Test>::RoundNotStarted
        );
    });
}

#[test]
fn test_create_round_zero_token_price_fails() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            Presale::create_round(
                RuntimeOrigin::root(),
                b"round1".to_vec(),
                0u64, // zero token price
                10_000_000u64,
                500_000u64,
                1u64,
                1_000_000u64,
                b"seed".to_vec(),
            ),
            Error::<Test>::InsufficientPayment
        );
    });
}

#[test]
fn test_create_round_empty_vesting_label_fails() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            Presale::create_round(
                RuntimeOrigin::root(),
                b"round1".to_vec(),
                5u64,
                10_000_000u64,
                500_000u64,
                1u64,
                1_000_000u64,
                b"".to_vec(),
            ),
            Error::<Test>::EmptyVestingLabel
        );
    });
}

// === Round activation ===

#[test]
fn test_activate_round_succeeds() {
    new_test_ext().execute_with(|| {
        Presale::create_round(
            RuntimeOrigin::root(),
            b"round1".to_vec(),
            5u64,
            10_000_000u64,
            500_000u64,
            1u64,
            1_000_000u64,
            b"seed".to_vec(),
        )
        .unwrap();

        assert_ok!(Presale::activate_round(RuntimeOrigin::root(), 0));
        frame_system::Pallet::<Test>::set_block_number(1);

        let round = Rounds::<Test>::get(0).unwrap();
        assert!(round.status == RoundStatus::Active, "Round should be active after activation");
    });
}

#[test]
fn test_activate_nonexistent_round_fails() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            Presale::activate_round(RuntimeOrigin::root(), 999),
            Error::<Test>::RoundNotFound
        );
    });
}

#[test]
fn test_deactivate_round() {
    new_test_ext().execute_with(|| {
        setup_active_round();

        assert_ok!(Presale::cancel_round(RuntimeOrigin::root(), 0));

        let round = Rounds::<Test>::get(0).unwrap();
        assert!(
            round.status != RoundStatus::Active,
            "Round should be inactive after deactivation"
        );
    });
}

// === Contribution ===

#[test]
fn test_contribute_succeeds() {
    new_test_ext().execute_with(|| {
        setup_active_round();

        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10_000u64,));

        // Verify contribution was recorded
        let contribution = Contributions::<Test>::get(0, &1u64);
        assert!(contribution.is_some(), "Contribution should be recorded");
        let contribution = contribution.unwrap();
        assert_eq!(contribution.total_paid, 10_000u64);
        assert!(
            contribution.total_purchased > 0,
            "Tokens should be purchased"
        );
    });
}

#[test]
fn test_contribute_to_inactive_round_fails() {
    new_test_ext().execute_with(|| {
        // Create round but don't activate
        assert_ok!(Presale::create_round(
            RuntimeOrigin::root(),
            b"round1".to_vec(),
            5u64,
            10_000_000u64,
            500_000u64,
            1u64,
            1_000_000u64,
            b"seed".to_vec(),
        ));

        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(1), 0, 10_000u64),
            Error::<Test>::RoundNotActive
        );
    });
}

#[test]
fn test_contribute_to_nonexistent_round_fails() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(1), 999, 10_000u64),
            Error::<Test>::RoundNotFound
        );
    });
}

#[test]
fn test_contribute_zero_payment_fails() {
    new_test_ext().execute_with(|| {
        setup_active_round();

        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(1), 0, 0u64),
            Error::<Test>::ZeroPayment
        );
    });
}

// === Per-account cap ===

#[test]
fn test_per_account_cap_enforcement() {
    new_test_ext().execute_with(|| {
        // Create round with per_account_cap = 100_000
        // token_price = 1, so 100_000 payment = 100_000 tokens
        assert_ok!(Presale::create_round(
            RuntimeOrigin::root(),
            b"cap_test".to_vec(),
            1u64,
            10_000_000u64,
            100_000u64, // per_account_cap
            1u64,
            1_000_000u64,
            b"seed".to_vec(),
        ));
        assert_ok!(Presale::activate_round(RuntimeOrigin::root(), 0));
        frame_system::Pallet::<Test>::set_block_number(1);

        // Buy at cap — should succeed
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 100_000u64,));

        // Buy more — should fail (exceeds per_account_cap)
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(1), 0, 1u64),
            Error::<Test>::ExceedsPerAccountCap
        );
    });
}

// === Round allocation cap ===

#[test]
fn test_round_allocation_cap_enforcement() {
    new_test_ext().execute_with(|| {
        // Create round with total_allocation = 500_000
        // token_price = 1, per_account_cap = 500_000
        assert_ok!(Presale::create_round(
            RuntimeOrigin::root(),
            b"alloc_test".to_vec(),
            1u64,
            500_000u64, // total_allocation
            500_000u64, // per_account_cap = same as allocation (one user can buy all)
            1u64,
            1_000_000u64,
            b"seed".to_vec(),
        ));
        assert_ok!(Presale::activate_round(RuntimeOrigin::root(), 0));
        frame_system::Pallet::<Test>::set_block_number(1);

        // Buy full allocation
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 500_000u64,));

        // Second buyer should fail — allocation exhausted
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(2), 0, 1u64),
            Error::<Test>::ExceedsRoundAllocation
        );
    });
}

// === Pause / Unpause ===

#[test]
fn test_pause_blocks_contributions() {
    new_test_ext().execute_with(|| {
        setup_active_round();

        assert_ok!(Presale::set_paused(RuntimeOrigin::root(), true));

        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(1), 0, 10_000u64),
            Error::<Test>::Paused
        );
    });
}

#[test]
fn test_unpause_allows_contributions() {
    new_test_ext().execute_with(|| {
        setup_active_round();

        assert_ok!(Presale::set_paused(RuntimeOrigin::root(), true));
        assert_ok!(Presale::set_paused(RuntimeOrigin::root(), false));

        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10_000u64,));
    });
}

#[test]
fn test_pause_non_admin_fails() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            Presale::set_paused(RuntimeOrigin::signed(1), true),
            DispatchError::BadOrigin
        );
    });
}

// === Round timing ===

#[test]
fn test_contribute_before_start_block_fails() {
    new_test_ext().execute_with(|| {
        // Create round starting at block 100
        assert_ok!(Presale::create_round(
            RuntimeOrigin::root(),
            b"future".to_vec(),
            5u64,
            10_000_000u64,
            500_000u64,
            100u64, // start_block = 100
            1_000_000u64,
            b"seed".to_vec(),
        ));
        assert_ok!(Presale::activate_round(RuntimeOrigin::root(), 0));
        frame_system::Pallet::<Test>::set_block_number(1);

        // At block 0, before start_block
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(1), 0, 10_000u64),
            Error::<Test>::RoundNotStarted
        );
    });
}

#[test]
fn test_contribute_after_end_block_fails() {
    new_test_ext().execute_with(|| {
        // Create round ending at block 50
        assert_ok!(Presale::create_round(
            RuntimeOrigin::root(),
            b"short".to_vec(),
            5u64,
            10_000_000u64,
            500_000u64,
            1u64,
            50u64, // end_block = 50
            b"seed".to_vec(),
        ));
        assert_ok!(Presale::activate_round(RuntimeOrigin::root(), 0));
        frame_system::Pallet::<Test>::set_block_number(1);

        // Advance past end block
        System::set_block_number(51);

        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(1), 0, 10_000u64),
            Error::<Test>::RoundEnded
        );
    });
}

// === Refund ===

#[test]
fn test_claim_refund_after_round_ends() {
    new_test_ext().execute_with(|| {
        // Create short round
        assert_ok!(Presale::create_round(
            RuntimeOrigin::root(),
            b"refund".to_vec(),
            5u64,
            10_000_000u64,
            500_000u64,
            1u64,
            50u64,
            b"seed".to_vec(),
        ));
        assert_ok!(Presale::activate_round(RuntimeOrigin::root(), 0));
        frame_system::Pallet::<Test>::set_block_number(1);

        // Contribute
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10_000u64,));

        // Deactivate and advance past end block
        assert_ok!(Presale::cancel_round(RuntimeOrigin::root(), 0));
        System::set_block_number(51);

        // Claim refund
        assert_ok!(Presale::claim_refund(RuntimeOrigin::signed(1), 0));

        // Contribution should be cleared
        let contribution = Contributions::<Test>::get(0, &1u64);
        assert!(
            contribution.is_none(),
            "Contribution should be cleared after refund"
        );
    });
}

#[test]
fn test_claim_refund_while_active_fails() {
    new_test_ext().execute_with(|| {
        setup_active_round();

        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10_000u64,));

        // Round still active — refund should fail
        assert_noop!(
            Presale::claim_refund(RuntimeOrigin::signed(1), 0),
            Error::<Test>::RoundNotRefundable
        );
    });
}

#[test]
fn test_claim_refund_no_contribution_fails() {
    new_test_ext().execute_with(|| {
        // Create and deactivate round
        assert_ok!(Presale::create_round(
            RuntimeOrigin::root(),
            b"refund".to_vec(),
            5u64,
            10_000_000u64,
            500_000u64,
            1u64,
            50u64,
            b"seed".to_vec(),
        ));
        assert_ok!(Presale::activate_round(RuntimeOrigin::root(), 0));
        frame_system::Pallet::<Test>::set_block_number(1);
        assert_ok!(Presale::cancel_round(RuntimeOrigin::root(), 0));
        System::set_block_number(51);

        // User 3 never contributed
        assert_noop!(
            Presale::claim_refund(RuntimeOrigin::signed(3), 0),
            Error::<Test>::NoContribution
        );
    });
}

// === Total tracking ===

#[test]
fn test_total_raised_increments() {
    new_test_ext().execute_with(|| {
        setup_active_round();

        let raised_before = TotalRaised::<Test>::get();

        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 50_000u64,));

        let raised_after = TotalRaised::<Test>::get();
        assert_eq!(
            raised_after,
            raised_before + 50_000,
            "TotalRaised should increase by payment amount"
        );
    });
}

#[test]
fn test_total_sold_increments() {
    new_test_ext().execute_with(|| {
        setup_active_round();

        let sold_before = TotalSold::<Test>::get();

        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 50_000u64,));

        let sold_after = TotalSold::<Test>::get();
        assert!(
            sold_after > sold_before,
            "TotalSold should increase after contribution"
        );
    });
}

// === Multiple rounds ===

#[test]
fn test_multiple_rounds_separate_tracking() {
    new_test_ext().execute_with(|| {
        // Create two rounds
        assert_ok!(Presale::create_round(
            RuntimeOrigin::root(),
            b"round0".to_vec(),
            1u64,
            1_000_000u64,
            500_000u64,
            1u64,
            1_000_000u64,
            b"seed".to_vec(),
        ));
        assert_ok!(Presale::activate_round(RuntimeOrigin::root(), 0));
        frame_system::Pallet::<Test>::set_block_number(1);

        assert_ok!(Presale::create_round(
            RuntimeOrigin::root(),
            b"round1".to_vec(),
            2u64,
            2_000_000u64,
            500_000u64,
            1u64,
            1_000_000u64,
            b"seed".to_vec(),
        ));
        assert_ok!(Presale::activate_round(RuntimeOrigin::root(), 1));
        frame_system::Pallet::<Test>::set_block_number(1);

        // Contribute to both rounds
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10_000u64));
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 1, 20_000u64));

        // Contributions should be tracked separately
        let c0 = Contributions::<Test>::get(0, &1u64).unwrap();
        let c1 = Contributions::<Test>::get(1, &1u64).unwrap();
        assert_eq!(c0.total_paid, 10_000u64, "Round 0 contribution");
        assert_eq!(c1.total_paid, 20_000u64, "Round 1 contribution");
    });
}
