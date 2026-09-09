// Luna Red-Team Adversarial Tests — Presale Pallet
// These tests attempt to break the per-round escrow, payment currency,
// and vesting weight fixes through creative attack vectors.
// Each test should FAIL to break the pallet (assert_ok or assert_noop).

use super::*;
use frame_support::{assert_noop, assert_ok};
use sp_runtime::DispatchError;

// === ATTACK 1: Cross-round drain via collect_funds ===
// Attacker collects round 0 funds, hoping it also drains round 1.
// Expected: round 1 escrow is independent, cannot be drained.

#[test]
fn luna_cross_round_drain_collect_funds() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 1000, 100, 1, 100, b"vest".to_vec());
        create_and_activate_round(1, 5, 1000, 100, 1, 100, b"vest".to_vec());

        // Contributions
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(2), 1, 20));

        // Finalize both
        set_block(101);
        assert_ok!(Presale::finalize_round(RuntimeOrigin::root(), 0));
        assert_ok!(Presale::finalize_round(RuntimeOrigin::root(), 1));

        // Collect round 0
        let treasury_before = Balances::free_balance(999);
        assert_ok!(Presale::collect_funds(RuntimeOrigin::root(), 0, 999));
        let collected_0 = Balances::free_balance(999) - treasury_before;
        assert_eq!(collected_0, 10, "Round 0 collected = 10");

        // Collect round 1 — should still get 20 (not 0, not drained)
        let treasury_before_1 = Balances::free_balance(999);
        assert_ok!(Presale::collect_funds(RuntimeOrigin::root(), 1, 999));
        let collected_1 = Balances::free_balance(999) - treasury_before_1;
        assert_eq!(collected_1, 20, "Round 1 still has its own 20");
    });
}

// === ATTACK 2: Double collect via re-entrant finalize ===
// Attacker tries to finalize a round twice, then collect twice.

#[test]
fn luna_double_finalize_collect() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 1000, 100, 1, 100, b"vest".to_vec());
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));

        set_block(101);
        assert_ok!(Presale::finalize_round(RuntimeOrigin::root(), 0));

        // Double finalize should fail
        assert_noop!(
            Presale::finalize_round(RuntimeOrigin::root(), 0),
            Error::<Test>::RoundAlreadyFinalized
        );

        // Collect once
        let treasury_before = Balances::free_balance(999);
        assert_ok!(Presale::collect_funds(RuntimeOrigin::root(), 0, 999));
        assert_eq!(Balances::free_balance(999) - treasury_before, 10);

        // Double collect should fail
        assert_noop!(
            Presale::collect_funds(RuntimeOrigin::root(), 0, 999),
            Error::<Test>::RoundStatusInvalid
        );
    });
}

// === ATTACK 3: Refund after successful round ===
// Attacker finalizes round as Successful, then tries to claim refund.

#[test]
fn luna_refund_after_successful_round() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 1000, 100, 1, 100, b"vest".to_vec());
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));

        set_block(101);
        assert_ok!(Presale::finalize_round(RuntimeOrigin::root(), 0));

        // Cannot refund on a Successful round
        assert_noop!(
            Presale::claim_refund(RuntimeOrigin::signed(1), 0),
            Error::<Test>::RoundNotRefundable
        );
    });
}

// === ATTACK 4: Collect funds on cancelled round ===
// Attacker cancels a round, then tries to collect funds (drain escrow).

#[test]
fn luna_collect_on_cancelled_round() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 1000, 100, 1, 100, b"vest".to_vec());
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));

        // Cancel the round
        assert_ok!(Presale::cancel_round(RuntimeOrigin::root(), 0));

        // Cannot collect funds on a Cancelled round
        assert_noop!(
            Presale::collect_funds(RuntimeOrigin::root(), 0, 999),
            Error::<Test>::RoundStatusInvalid
        );
    });
}

// === ATTACK 5: Contribute to cancelled/paused round ===

#[test]
fn luna_contribute_to_cancelled_round() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 1000, 100, 1, 100, b"vest".to_vec());

        assert_ok!(Presale::cancel_round(RuntimeOrigin::root(), 0));

        // Cannot contribute to a cancelled round
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(1), 0, 10),
            Error::<Test>::RoundNotActive
        );
    });
}

// === ATTACK 6: Overflow in price formula ===
// Attacker sends maximum possible payment, hoping to overflow purchased amount.

#[test]
fn luna_price_overflow_attack() {
    new_test_ext().execute_with(|| {
        set_block(1);
        // price=5, allocation=1000, per_cap=100
        create_and_activate_round(0, 5, 1000, 100, 1, 100, b"vest".to_vec());

        // Try to contribute an enormous amount
        // The round allocation is 1000 tokens, so max useful payment is 200 (200*5=1000)
        // But per-user cap is 100, so max payment per user is 20 (20*5=100)
        // Contributing 25 would exceed per-user cap
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(1), 0, 25),
            Error::<Test>::ExceedsPerAccountCap
        );
    });
}

// === ATTACK 7: Double refund claim (reentrancy) ===
// Attacker claims refund twice for the same round.

#[test]
fn luna_double_refund_claim() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 1000, 100, 1, 100, b"vest".to_vec());
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));

        assert_ok!(Presale::cancel_round(RuntimeOrigin::root(), 0));
        assert_ok!(Presale::claim_refund(RuntimeOrigin::signed(1), 0));

        // Second refund should fail — contribution already removed
        assert_noop!(
            Presale::claim_refund(RuntimeOrigin::signed(1), 0),
            Error::<Test>::NoContribution
        );
    });
}

// === ATTACK 8: Contribute to non-existent round ===

#[test]
fn luna_contribute_nonexistent_round() {
    new_test_ext().execute_with(|| {
        set_block(1);
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(1), 999, 10),
            Error::<Test>::RoundNotFound
        );
    });
}

// === ATTACK 9: Non-admin tries admin operations ===

#[test]
fn luna_non_admin_create_round() {
    new_test_ext().execute_with(|| {
        set_block(1);
        // Non-root cannot create rounds
        assert_noop!(
            Presale::create_round(
                RuntimeOrigin::signed(1),
                b"test".to_vec(),
                5,
                1000,
                100,
                1,
                100,
                b"vest".to_vec()
            ),
            DispatchError::BadOrigin
        );
    });
}

// === ATTACK 10: Zero vesting label rejection ===

#[test]
fn luna_empty_vesting_label_rejected() {
    new_test_ext().execute_with(|| {
        set_block(1);
        // Empty vesting label should be rejected at create_round
        assert_noop!(
            Presale::create_round(
                RuntimeOrigin::root(),
                b"test".to_vec(),
                5,
                1000,
                100,
                1,
                100,
                vec![]
            ),
            Error::<Test>::EmptyVestingLabel
        );
    });
}

// === ATTACK 11: Round raised invariant — cancel should not inflate TotalRaised ===

#[test]
fn luna_cancel_does_not_inflate_total_raised() {
    new_test_ext().execute_with(|| {
        set_block(1);
        create_and_activate_round(0, 5, 1000, 100, 1, 100, b"vest".to_vec());
        create_and_activate_round(1, 5, 1000, 100, 1, 100, b"vest".to_vec());

        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(2), 1, 20));

        let total_raised_before = Presale::total_raised();

        // Cancel and refund round 0
        assert_ok!(Presale::cancel_round(RuntimeOrigin::root(), 0));
        assert_ok!(Presale::claim_refund(RuntimeOrigin::signed(1), 0));

        // TotalRaised should decrease by 10 (round 0 refund)
        let total_raised_after = Presale::total_raised();
        assert_eq!(
            total_raised_before as i64 - total_raised_after as i64,
            10,
            "TotalRaised should decrease by refunded amount"
        );
    });
}
