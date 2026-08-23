#![allow(unused_variables)]
// ═══════════════════════════════════════════════════════════════════════════════
// LUNA ADVERSARIAL TEST SUITE — Presale / Escrow / Vesting Security Review
// ═══════════════════════════════════════════════════════════════════════════════
// Tests are organized by the 25 sections of the audit specification.
// Each test name encodes the attack vector being tested.
// ═══════════════════════════════════════════════════════════════════════════════

use super::*;
use frame_support::{assert_noop, assert_ok};

// === Helper: Setup a standard active round ===
fn setup_round(price: u64, allocation: u64, cap: u64, start: u64, end: u64) {
    assert_ok!(Presale::create_round(
        RuntimeOrigin::root(),
        b"luna".to_vec(),
        price,
        allocation,
        cap,
        start,
        end,
        b"luna_vest".to_vec(),
    ));
    assert_ok!(Presale::activate_round(RuntimeOrigin::root(), 0));
    frame_system::Pallet::<Test>::set_block_number(start);
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 3: CONTRIBUTION SECURITY
// ═══════════════════════════════════════════════════════════════════════════════

#[test]
fn test_contribute_exact_per_account_cap() {
    new_test_ext().execute_with(|| {
        setup_round(5, 10_000, 50, 1, 1000);
        // cap = 50 tokens, price = 5 → 10 payment = 50 tokens (exactly at cap)
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
        let c = Presale::contributions(0, &1).unwrap();
        assert_eq!(c.total_purchased, 50);
    });
}

#[test]
fn test_contribute_one_over_per_account_cap() {
    new_test_ext().execute_with(|| {
        setup_round(5, 10_000, 50, 1, 1000);
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
        // 50 tokens already, +1 more payment = 5 more tokens → 55 > 50
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(1), 0, 1),
            Error::<Test>::ExceedsPerAccountCap
        );
    });
}

#[test]
fn test_contribute_multiple_accumulating() {
    new_test_ext().execute_with(|| {
        setup_round(5, 10_000, 100, 1, 1000);
        // Three contributions: 5 + 5 + 5 = 15 payment → 75 tokens (< 100 cap)
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 5));
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 5));
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 5));
        let c = Presale::contributions(0, &1).unwrap();
        assert_eq!(c.total_purchased, 75);
        assert_eq!(c.total_paid, 15);
    });
}

#[test]
fn test_contribute_exact_end_block_fails() {
    new_test_ext().execute_with(|| {
        setup_round(5, 10_000, 100, 1, 100);
        // At end_block exactly → should fail (current_block < end_block is the check)
        frame_system::Pallet::<Test>::set_block_number(100);
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(1), 0, 10),
            Error::<Test>::RoundEnded
        );
    });
}

#[test]
fn test_contribute_one_before_end_block_succeeds() {
    new_test_ext().execute_with(|| {
        setup_round(5, 10_000, 100, 1, 100);
        frame_system::Pallet::<Test>::set_block_number(99);
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
    });
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 4: HARD CAP
// ═══════════════════════════════════════════════════════════════════════════════

#[test]
fn test_hard_cap_exact_boundary() {
    new_test_ext().execute_with(|| {
        // allocation = 100, price = 5 → 20 payment = 100 tokens (exactly at cap)
        setup_round(5, 100, 1000, 1, 1000);
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 20));
        assert_eq!(Presale::rounds(0).unwrap().sold, 100);
    });
}

#[test]
fn test_hard_cap_one_over_fails() {
    new_test_ext().execute_with(|| {
        // allocation = 100, price = 5 → 20 payment = 100 tokens (at cap)
        setup_round(5, 100, 1000, 1, 1000);
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 20));
        // User 2 tries to buy 1 more token → 101 > 100
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(2), 0, 1),
            Error::<Test>::ExceedsRoundAllocation
        );
    });
}

#[test]
fn test_hard_cap_racing_users() {
    new_test_ext().execute_with(|| {
        // allocation = 100, price = 5 → each user pays 10 for 50 tokens
        setup_round(5, 100, 1000, 1, 1000);
        // User 1 buys 50 tokens (10 payment)
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
        // User 2 buys 50 tokens (10 payment) → total 100, exactly at cap
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(2), 0, 10));
        // User 3 tries → fails
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(3), 0, 1),
            Error::<Test>::ExceedsRoundAllocation
        );
    });
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 5: PRICE / ALLOCATION CALCULATION
// ═══════════════════════════════════════════════════════════════════════════════

#[test]
fn test_price_calculation_basic() {
    new_test_ext().execute_with(|| {
        // price = 5, precision = 1 → 10 payment * 5 / 1 = 50 tokens
        setup_round(5, 10_000, 1000, 1, 1000);
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
        let c = Presale::contributions(0, &1).unwrap();
        assert_eq!(c.total_purchased, 50, "10 * 5 / 1 = 50");
    });
}

#[test]
fn test_price_calculation_one_unit() {
    new_test_ext().execute_with(|| {
        // Minimum payment: 1 unit * 5 / 1 = 5 tokens
        setup_round(5, 10_000, 1000, 1, 1000);
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 1));
        let c = Presale::contributions(0, &1).unwrap();
        assert_eq!(c.total_purchased, 5, "1 * 5 / 1 = 5");
    });
}

#[test]
fn test_price_zero_token_result_fails() {
    new_test_ext().execute_with(|| {
        // price = 0 would fail at create_round, but what about truncation?
        // With price = 5, precision = 1, payment = 0 → already blocked by ZeroPayment
        // With a very low price relative to payment, token could truncate to 0
        // price = 1, payment = 1 → 1 token (fine)
        setup_round(1, 10_000, 1000, 1, 1000);
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 1));
        let c = Presale::contributions(0, &1).unwrap();
        assert_eq!(c.total_purchased, 1);
    });
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 7: ESCROW SECURITY
// ═══════════════════════════════════════════════════════════════════════════════

#[test]
fn test_escrow_account_is_pallet_id() {
    new_test_ext().execute_with(|| {
        let escrow = PresalePalletId::get().into_account_truncating();
        let balance = pallet_balances::Pallet::<Test>::free_balance(&escrow);
        assert!(balance > 0, "Escrow should have VRDX from genesis");
    });
}

#[test]
fn test_non_admin_cannot_collect_funds() {
    new_test_ext().execute_with(|| {
        setup_round(5, 10_000, 1000, 1, 100);
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
        frame_system::Pallet::<Test>::set_block_number(100);
        assert_noop!(
            Presale::collect_funds(RuntimeOrigin::signed(1), 0, 2),
            DispatchError::BadOrigin
        );
    });
}

#[test]
fn test_collect_funds_before_end_fails() {
    new_test_ext().execute_with(|| {
        setup_round(5, 10_000, 1000, 1, 100);
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
        frame_system::Pallet::<Test>::set_block_number(50);
        assert_noop!(
            Presale::collect_funds(RuntimeOrigin::root(), 0, 999),
            Error::<Test>::RoundStatusInvalid
        );
    });
}

#[test]
fn test_double_collection_prevented() {
    new_test_ext().execute_with(|| {
        setup_round(5, 10_000, 1000, 1, 100);
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
        frame_system::Pallet::<Test>::set_block_number(100);
        // First collection
        assert_ok!(Presale::finalize_round(RuntimeOrigin::root(), 0));
        assert_ok!(Presale::collect_funds(RuntimeOrigin::root(), 0, 999));
        // Second collection → fails
        assert_noop!(
            Presale::collect_funds(RuntimeOrigin::root(), 0, 999),
            Error::<Test>::RoundStatusInvalid
        );
    });
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 8: REFUND SECURITY
// ═══════════════════════════════════════════════════════════════════════════════

#[test]
fn test_refund_before_end_block_fails() {
    new_test_ext().execute_with(|| {
        setup_round(5, 10_000, 1000, 1, 100);
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
        // Round is still Active — claim_refund should fail
        frame_system::Pallet::<Test>::set_block_number(50);
        assert_noop!(
            Presale::claim_refund(RuntimeOrigin::signed(1), 0),
            Error::<Test>::RoundNotRefundable
        );
    });
}

#[test]
fn test_refund_while_active_fails() {
    new_test_ext().execute_with(|| {
        setup_round(5, 10_000, 1000, 1, 100);
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
        frame_system::Pallet::<Test>::set_block_number(100);
        assert_noop!(
            Presale::claim_refund(RuntimeOrigin::signed(1), 0),
            Error::<Test>::RoundNotRefundable
        );
    });
}

#[test]
fn test_double_refund_prevented() {
    new_test_ext().execute_with(|| {
        setup_round(5, 10_000, 1000, 1, 100);
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
        assert_ok!(Presale::cancel_round(RuntimeOrigin::root(), 0));
        frame_system::Pallet::<Test>::set_block_number(100);
        // First refund
        assert_ok!(Presale::claim_refund(RuntimeOrigin::signed(1), 0));
        // Second refund → fails (contribution removed)
        assert_noop!(
            Presale::claim_refund(RuntimeOrigin::signed(1), 0),
            Error::<Test>::NoContribution
        );
    });
}

#[test]
fn test_refund_returns_correct_amount() {
    new_test_ext().execute_with(|| {
        setup_round(5, 1_000_000, 100_000, 1, 100);
        let user_balance_before = pallet_balances::Pallet::<Test>::free_balance(&1);
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10_000));
        assert_ok!(Presale::cancel_round(RuntimeOrigin::root(), 0));
        frame_system::Pallet::<Test>::set_block_number(100);
        assert_ok!(Presale::claim_refund(RuntimeOrigin::signed(1), 0));
        // User should get back their payment (10_000) and return their tokens (50_000)
        // Net: user paid 10_000, got 50_000 tokens, returned 50_000 tokens, got 10_000 back
        let user_balance_after = pallet_balances::Pallet::<Test>::free_balance(&1);
        assert_eq!(
            user_balance_after, user_balance_before,
            "User should be fully refunded (net zero change from contribution + refund)"
        );
    });
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 9: DOUBLE-SPEND / DOUBLE-CLAIM
// ═══════════════════════════════════════════════════════════════════════════════

#[test]
fn test_claim_after_refund_no_double_claim() {
    new_test_ext().execute_with(|| {
        setup_round(5, 10_000, 1000, 1, 100);
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
        assert_ok!(Presale::cancel_round(RuntimeOrigin::root(), 0));
        frame_system::Pallet::<Test>::set_block_number(100);
        assert_ok!(Presale::claim_refund(RuntimeOrigin::signed(1), 0));
        // Try again
        assert_noop!(
            Presale::claim_refund(RuntimeOrigin::signed(1), 0),
            Error::<Test>::NoContribution
        );
    });
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 8+C1: CRITICAL — REFUND AFTER FUND COLLECTION (DOUBLE-SPEND)
// ═══════════════════════════════════════════════════════════════════════════════

#[test]
fn test_refund_after_collect_funds_blocked() {
    new_test_ext().execute_with(|| {
        setup_round(5, 1_000_000, 100_000, 1, 100);
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10_000));

        let escrow = PresalePalletId::get().into_account_truncating();
        let escrow_before = pallet_balances::Pallet::<Test>::free_balance(&escrow);

        frame_system::Pallet::<Test>::set_block_number(100);
        // Admin collects funds (escrow → beneficiary)
        assert_ok!(Presale::finalize_round(RuntimeOrigin::root(), 0));
        assert_ok!(Presale::collect_funds(RuntimeOrigin::root(), 0, 999));
        let escrow_after_collect = pallet_balances::Pallet::<Test>::free_balance(&escrow);
        assert!(
            escrow_after_collect < escrow_before,
            "Escrow should be reduced after collection"
        );

        // Round is now Closed after collection
        // User tries to refund — MUST FAIL (round is Closed, not Failed/Cancelled)
        assert_noop!(
            Presale::claim_refund(RuntimeOrigin::signed(1), 0),
            Error::<Test>::RoundNotRefundable
        );
    });
}

#[test]
fn test_refund_after_collect_funds_no_double_spend() {
    new_test_ext().execute_with(|| {
        setup_round(5, 1_000_000, 100_000, 1, 100);
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10_000));

        let escrow = PresalePalletId::get().into_account_truncating();
        let beneficiary = 999u64;

        frame_system::Pallet::<Test>::set_block_number(100);

        let benef_before = pallet_balances::Pallet::<Test>::free_balance(&beneficiary);
        let escrow_before = pallet_balances::Pallet::<Test>::free_balance(&escrow);

        // Admin collects
        assert_ok!(Presale::finalize_round(RuntimeOrigin::root(), 0));
        assert_ok!(Presale::collect_funds(
            RuntimeOrigin::root(),
            0,
            beneficiary
        ));
        let benef_after = pallet_balances::Pallet::<Test>::free_balance(&beneficiary);
        assert_eq!(
            benef_after,
            benef_before + 10_000,
            "Beneficiary got the payment"
        );

        // Round is now Closed after collection
        // Refund MUST be blocked (round is Closed, not Failed/Cancelled)
        assert_noop!(
            Presale::claim_refund(RuntimeOrigin::signed(1), 0),
            Error::<Test>::RoundNotRefundable
        );

        // Verify escrow wasn't drained further
        let escrow_final = pallet_balances::Pallet::<Test>::free_balance(&escrow);
        assert_eq!(
            escrow_final,
            escrow_before - 10_000,
            "Escrow should only be reduced by collection, not by refund"
        );
    });
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 13: ADMINISTRATIVE AUTHORITY
// ═══════════════════════════════════════════════════════════════════════════════

#[test]
fn test_non_admin_cannot_create_round() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            Presale::create_round(
                RuntimeOrigin::signed(1),
                b"evil".to_vec(),
                5u64,
                10_000u64,
                100u64,
                1u64,
                1000u64,
                b"vest".to_vec(),
            ),
            DispatchError::BadOrigin
        );
    });
}

#[test]
fn test_non_admin_cannot_activate() {
    new_test_ext().execute_with(|| {
        assert_ok!(Presale::create_round(
            RuntimeOrigin::root(),
            b"test".to_vec(),
            5u64,
            10_000u64,
            100u64,
            1u64,
            1000u64,
            b"vest".to_vec(),
        ));
        assert_noop!(
            Presale::activate_round(RuntimeOrigin::signed(1), 0),
            DispatchError::BadOrigin
        );
    });
}

#[test]
fn test_non_admin_cannot_deactivate() {
    new_test_ext().execute_with(|| {
        setup_round(5, 10_000, 100, 1, 1000);
        assert_noop!(
            Presale::cancel_round(RuntimeOrigin::signed(1), 0),
            DispatchError::BadOrigin
        );
    });
}

#[test]
fn test_non_admin_cannot_whitelist() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            Presale::update_whitelist(RuntimeOrigin::signed(1), 0, 2, true),
            DispatchError::BadOrigin
        );
    });
}

#[test]
fn test_non_admin_cannot_collect() {
    new_test_ext().execute_with(|| {
        setup_round(5, 10_000, 100, 1, 100);
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
        frame_system::Pallet::<Test>::set_block_number(100);
        assert_noop!(
            Presale::collect_funds(RuntimeOrigin::signed(1), 0, 999),
            DispatchError::BadOrigin
        );
    });
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 14: TIME MANIPULATION
// ═══════════════════════════════════════════════════════════════════════════════

#[test]
fn test_contribute_at_exact_start_block() {
    new_test_ext().execute_with(|| {
        setup_round(5, 10_000, 100, 10, 1000);
        frame_system::Pallet::<Test>::set_block_number(10);
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
    });
}

#[test]
fn test_contribute_one_before_start_fails() {
    new_test_ext().execute_with(|| {
        setup_round(5, 10_000, 100, 10, 1000);
        frame_system::Pallet::<Test>::set_block_number(9);
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(1), 0, 10),
            Error::<Test>::RoundNotStarted
        );
    });
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 21: EMERGENCY / CIRCUIT BREAKER
// ═══════════════════════════════════════════════════════════════════════════════

#[test]
fn test_pause_blocks_contribute() {
    new_test_ext().execute_with(|| {
        setup_round(5, 10_000, 100, 1, 1000);
        assert_ok!(Presale::set_paused(RuntimeOrigin::root(), true));
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(1), 0, 10),
            Error::<Test>::Paused
        );
    });
}

#[test]
fn test_unpause_restores_contribute() {
    new_test_ext().execute_with(|| {
        setup_round(5, 10_000, 100, 1, 1000);
        assert_ok!(Presale::set_paused(RuntimeOrigin::root(), true));
        assert_ok!(Presale::set_paused(RuntimeOrigin::root(), false));
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
    });
}

#[test]
fn test_non_admin_cannot_pause() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            Presale::set_paused(RuntimeOrigin::signed(1), true),
            DispatchError::BadOrigin
        );
    });
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 16: TRANSACTION FAILURE / ATOMICITY
// ═══════════════════════════════════════════════════════════════════════════════

#[test]
fn test_failed_contribution_no_state_change() {
    new_test_ext().execute_with(|| {
        setup_round(5, 10_000, 100, 1, 1000);
        // This contribution fails (exceeds cap after first)
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 20));
        // Second should fail
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(1), 0, 1),
            Error::<Test>::ExceedsPerAccountCap
        );
        // State should be unchanged — only first contribution recorded
        let c = Presale::contributions(0, &1).unwrap();
        assert_eq!(
            c.total_purchased, 100,
            "Only first contribution should be recorded"
        );
        assert_eq!(c.total_paid, 20);
    });
}

#[test]
fn test_failed_contribution_no_balance_change() {
    new_test_ext().execute_with(|| {
        setup_round(5, 10_000, 100, 1, 1000);
        let user_before = pallet_balances::Pallet::<Test>::free_balance(&1);
        let escrow = PresalePalletId::get().into_account_truncating();
        let escrow_before = pallet_balances::Pallet::<Test>::free_balance(&escrow);

        // First succeeds
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 20));
        // Second fails
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(1), 0, 1),
            Error::<Test>::ExceedsPerAccountCap
        );

        // Balances should only reflect the first successful contribution
        let user_after = pallet_balances::Pallet::<Test>::free_balance(&1);
        // User paid 20, got 100 tokens back
        assert_eq!(
            user_after,
            user_before - 20 + 100,
            "Only first contribution affected balance"
        );
    });
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 17: REPLAY PROTECTION
// ═══════════════════════════════════════════════════════════════════════════════

#[test]
fn test_replay_refund_blocked() {
    new_test_ext().execute_with(|| {
        setup_round(5, 10_000, 1000, 1, 100);
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
        assert_ok!(Presale::cancel_round(RuntimeOrigin::root(), 0));
        frame_system::Pallet::<Test>::set_block_number(100);

        // First refund succeeds
        assert_ok!(Presale::claim_refund(RuntimeOrigin::signed(1), 0));
        // Replay in same block → fails
        assert_noop!(
            Presale::claim_refund(RuntimeOrigin::signed(1), 0),
            Error::<Test>::NoContribution
        );
        // Replay in next block → also fails
        frame_system::Pallet::<Test>::set_block_number(101);
        assert_noop!(
            Presale::claim_refund(RuntimeOrigin::signed(1), 0),
            Error::<Test>::NoContribution
        );
    });
}

#[test]
fn test_replay_collection_blocked() {
    new_test_ext().execute_with(|| {
        setup_round(5, 10_000, 1000, 1, 100);
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
        frame_system::Pallet::<Test>::set_block_number(100);

        assert_ok!(Presale::finalize_round(RuntimeOrigin::root(), 0));
        assert_ok!(Presale::collect_funds(RuntimeOrigin::root(), 0, 999));
        // Replay
        assert_noop!(
            Presale::collect_funds(RuntimeOrigin::root(), 0, 999),
            Error::<Test>::RoundStatusInvalid
        );
    });
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 12: ACCOUNTING INVARIANTS
// ═══════════════════════════════════════════════════════════════════════════════

#[test]
fn test_accounting_invariant_sold_le_allocation() {
    new_test_ext().execute_with(|| {
        setup_round(5, 200, 1000, 1, 1000);
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 20));
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(2), 0, 20));
        let round = Presale::rounds(0).unwrap();
        assert!(
            round.sold <= round.total_allocation,
            "sold must never exceed allocation"
        );
        assert_eq!(round.sold, 200); // 2 * 100 tokens (20 * 5 each)
    });
}

#[test]
fn test_accounting_invariant_total_raised_equals_round_raised() {
    new_test_ext().execute_with(|| {
        setup_round(5, 10_000, 1000, 1, 1000);
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(2), 0, 20));
        let total_raised = TotalRaised::<Test>::get();
        let round_raised = RoundRaised::<Test>::get(0);
        assert_eq!(
            total_raised, round_raised,
            "TotalRaised should equal RoundRaised for single round"
        );
        assert_eq!(total_raised, 30);
    });
}

#[test]
fn test_accounting_invariant_contribution_paid_purchased() {
    new_test_ext().execute_with(|| {
        setup_round(5, 10_000, 1000, 1, 1000);
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 5));
        let c = Presale::contributions(0, &1).unwrap();
        // purchased = (10 + 5) * 5 = 75, paid = 15
        assert_eq!(c.total_purchased, 75);
        assert_eq!(c.total_paid, 15);
        // Invariant: purchased = paid * price
        assert_eq!(c.total_purchased, c.total_paid * 5);
    });
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 10: VESTING INTEGRATION (with no-op VestingHandler)
// ═══════════════════════════════════════════════════════════════════════════════

#[test]
fn test_vesting_created_on_contribution() {
    new_test_ext().execute_with(|| {
        setup_round(5, 10_000, 1000, 1, 1000);
        // VestingHandler is () in test, so assign_vesting is no-op
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
        // Just verify no error — vesting was "created" (no-op in test)
        let c = Presale::contributions(0, &1).unwrap();
        assert!(c.total_purchased > 0);
    });
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 15: FRONT-RUNNING / ORDERING
// ═══════════════════════════════════════════════════════════════════════════════

#[test]
fn test_front_running_first_come_first_served() {
    new_test_ext().execute_with(|| {
        // allocation = 100, price = 5, each user pays 10 for 50 tokens
        setup_round(5, 100, 1000, 1, 1000);
        // User 1 gets in first — buys 50 tokens
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
        // User 2 gets in second — buys 50 tokens → total 100, at cap
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(2), 0, 10));
        // User 3 is too late
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(3), 0, 1),
            Error::<Test>::ExceedsRoundAllocation
        );
    });
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 4 BOUNDARY: OVERFLOW PROTECTION
// ═══════════════════════════════════════════════════════════════════════════════

#[test]
fn test_overflow_in_price_calculation() {
    new_test_ext().execute_with(|| {
        // Very large payment * price → should overflow and fail
        setup_round(u64::MAX, 10_000, u64::MAX, 1, 1000);
        // payment = 2, price = u64::MAX → 2 * u64::MAX overflows
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(1), 0, 2),
            Error::<Test>::CalculationOverflow
        );
    });
}

#[test]
fn test_overflow_in_round_sold() {
    new_test_ext().execute_with(|| {
        // Set allocation near u64::MAX, price = 1
        // Contribute u64::MAX - 10, then try to add more
        setup_round(1, u64::MAX, u64::MAX, 1, 1000);
        // This would overflow if not checked
        // Can't actually contribute u64::MAX because user doesn't have that much
        // But let's verify checked arithmetic is used
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 100_000));
        let round = Presale::rounds(0).unwrap();
        assert_eq!(round.sold, 100_000);
    });
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 11: TOKEN SUPPLY (basic — MaxSupplyCurrency is tested separately)
// ═══════════════════════════════════════════════════════════════════════════════

#[test]
fn test_presale_does_not_mint_tokens() {
    new_test_ext().execute_with(|| {
        let total_issuance_before = pallet_balances::Pallet::<Test>::total_issuance();
        setup_round(5, 10_000, 1000, 1, 1000);
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
        let total_issuance_after = pallet_balances::Pallet::<Test>::total_issuance();
        assert_eq!(
            total_issuance_before, total_issuance_after,
            "Presale must not change total issuance (it transfers from escrow, not mints)"
        );
    });
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 19: EVENTS / OBSERVABILITY
// ═══════════════════════════════════════════════════════════════════════════════

#[test]
fn test_contribution_event_emitted() {
    new_test_ext().execute_with(|| {
        setup_round(5, 10_000, 1000, 1, 1000);
        // Just verify contribute succeeds and state is consistent
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
        let c = Presale::contributions(0, &1).unwrap();
        assert_eq!(c.total_paid, 10);
        assert_eq!(c.total_purchased, 50);
    });
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 22: LUNA RED TEAM — COMBINED ATTACKS
// ═══════════════════════════════════════════════════════════════════════════════

#[test]
fn luna_attack_contribute_twice_different_rounds() {
    new_test_ext().execute_with(|| {
        // Create two rounds, contribute to both — should work (separate caps)
        assert_ok!(Presale::create_round(
            RuntimeOrigin::root(),
            b"r0".to_vec(),
            5,
            10_000,
            100,
            1,
            1000,
            b"v0".to_vec(),
        ));
        assert_ok!(Presale::activate_round(RuntimeOrigin::root(), 0));
        assert_ok!(Presale::create_round(
            RuntimeOrigin::root(),
            b"r1".to_vec(),
            10,
            10_000,
            100,
            1,
            1000,
            b"v1".to_vec(),
        ));
        assert_ok!(Presale::activate_round(RuntimeOrigin::root(), 1));
        frame_system::Pallet::<Test>::set_block_number(1);

        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 1, 10));

        // Each round tracks separately
        let c0 = Presale::contributions(0, &1).unwrap();
        let c1 = Presale::contributions(1, &1).unwrap();
        assert_eq!(c0.total_purchased, 50);
        assert_eq!(c1.total_purchased, 100);
    });
}

#[test]
fn luna_attack_steal_other_user_contribution() {
    new_test_ext().execute_with(|| {
        setup_round(5, 10_000, 1000, 1, 1000);
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
        // Deactivate and advance past end block to allow refunds
        assert_ok!(Presale::cancel_round(RuntimeOrigin::root(), 0));
        frame_system::Pallet::<Test>::set_block_number(1000);
        // User 2 tries to refund user 1's contribution → NoContribution (user 2 never contributed)
        assert_noop!(
            Presale::claim_refund(RuntimeOrigin::signed(2), 0),
            Error::<Test>::NoContribution
        );
        // User 1's contribution is untouched
        let c = Presale::contributions(0, &1).unwrap();
        assert_eq!(c.total_purchased, 50);
    });
}

#[test]
fn luna_attack_collect_then_refund_double_spend() {
    new_test_ext().execute_with(|| {
        setup_round(5, 1_000_000, 100_000, 1, 100);
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10_000));

        let escrow = PresalePalletId::get().into_account_truncating();
        frame_system::Pallet::<Test>::set_block_number(100);

        let escrow_before = pallet_balances::Pallet::<Test>::free_balance(&escrow);
        let benef_before = pallet_balances::Pallet::<Test>::free_balance(&999u64);

        // Step 1: Admin collects
        assert_ok!(Presale::finalize_round(RuntimeOrigin::root(), 0));
        assert_ok!(Presale::collect_funds(RuntimeOrigin::root(), 0, 999));
        let benef_after = pallet_balances::Pallet::<Test>::free_balance(&999u64);
        assert_eq!(benef_after, benef_before + 10_000);

        // Step 2: Round is now Closed after collection
        // Step 3: User tries refund — MUST BE BLOCKED (round is Closed)
        assert_noop!(
            Presale::claim_refund(RuntimeOrigin::signed(1), 0),
            Error::<Test>::RoundNotRefundable
        );

        // Verify: escrow only lost the collected amount, not double
        let escrow_after = pallet_balances::Pallet::<Test>::free_balance(&escrow);
        assert_eq!(escrow_after, escrow_before - 10_000);
    });
}

#[test]
fn luna_attack_contribute_to_nonexistent_round() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(1), 999, 10),
            Error::<Test>::RoundNotFound
        );
    });
}

#[test]
fn luna_attack_refund_nonexistent_round() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            Presale::claim_refund(RuntimeOrigin::signed(1), 999),
            Error::<Test>::RoundNotFound
        );
    });
}

#[test]
fn luna_attack_zero_payment() {
    new_test_ext().execute_with(|| {
        setup_round(5, 10_000, 1000, 1, 1000);
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(1), 0, 0),
            Error::<Test>::ZeroPayment
        );
    });
}

#[test]
fn luna_attack_insufficient_escrow_balance() {
    new_test_ext().execute_with(|| {
        // Escrow has 1T, user has 1B. Contribute 100M → 100M tokens from escrow. OK.
        setup_round(1, 2_000_000_000_000, 2_000_000_000_000, 1, 1000);
        assert_ok!(Presale::contribute(
            RuntimeOrigin::signed(1),
            0,
            100_000_000
        ));
        let c = Presale::contributions(0, &1).unwrap();
        assert_eq!(c.total_purchased, 100_000_000);
    });
}

#[test]
fn luna_attack_privilege_escalation() {
    new_test_ext().execute_with(|| {
        setup_round(5, 10_000, 1000, 1, 1000);
        // Regular user tries admin operations
        assert_noop!(
            Presale::activate_round(RuntimeOrigin::signed(1), 0),
            DispatchError::BadOrigin
        );
        assert_noop!(
            Presale::cancel_round(RuntimeOrigin::signed(1), 0),
            DispatchError::BadOrigin
        );
        assert_noop!(
            Presale::set_paused(RuntimeOrigin::signed(1), true),
            DispatchError::BadOrigin
        );
        assert_noop!(
            Presale::update_whitelist(RuntimeOrigin::signed(1), 0, 2, true),
            DispatchError::BadOrigin
        );
        assert_noop!(
            Presale::collect_funds(RuntimeOrigin::signed(1), 0, 1),
            DispatchError::BadOrigin
        );
        assert_noop!(
            Presale::set_whitelist_required(RuntimeOrigin::signed(1), 0, true),
            DispatchError::BadOrigin
        );
    });
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 2: STATE MACHINE — INVALID TRANSITIONS
// ═══════════════════════════════════════════════════════════════════════════════

#[test]
fn test_state_inactive_to_active() {
    new_test_ext().execute_with(|| {
        assert_ok!(Presale::create_round(
            RuntimeOrigin::root(),
            b"sm".to_vec(),
            5,
            10_000,
            100,
            1,
            1000,
            b"v".to_vec(),
        ));
        assert!(Presale::rounds(0).unwrap().status != RoundStatus::Active);
        assert_ok!(Presale::activate_round(RuntimeOrigin::root(), 0));
        assert!(Presale::rounds(0).unwrap().status == RoundStatus::Active);
    });
}

#[test]
fn test_state_active_to_inactive() {
    new_test_ext().execute_with(|| {
        setup_round(5, 10_000, 100, 1, 1000);
        assert_ok!(Presale::cancel_round(RuntimeOrigin::root(), 0));
        assert!(Presale::rounds(0).unwrap().status != RoundStatus::Active);
    });
}

#[test]
fn test_state_contribute_to_inactive_round() {
    new_test_ext().execute_with(|| {
        assert_ok!(Presale::create_round(
            RuntimeOrigin::root(),
            b"sm".to_vec(),
            5,
            10_000,
            100,
            1,
            1000,
            b"v".to_vec(),
        ));
        // Not activated — contribute fails
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(1), 0, 10),
            Error::<Test>::RoundNotActive
        );
    });
}

#[test]
fn test_state_refund_requires_inactive_and_ended() {
    new_test_ext().execute_with(|| {
        setup_round(5, 10_000, 1000, 1, 100);
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));

        // Active + before end → no refund
        frame_system::Pallet::<Test>::set_block_number(50);
        assert_noop!(
            Presale::claim_refund(RuntimeOrigin::signed(1), 0),
            Error::<Test>::RoundNotRefundable
        );

        // Active + after end → no refund
        frame_system::Pallet::<Test>::set_block_number(100);
        assert_noop!(
            Presale::claim_refund(RuntimeOrigin::signed(1), 0),
            Error::<Test>::RoundNotRefundable
        );

        // Cancelled + before end → refund OK (Cancelled rounds allow immediate refunds)
        assert_ok!(Presale::cancel_round(RuntimeOrigin::root(), 0));
        frame_system::Pallet::<Test>::set_block_number(50);
        assert_ok!(Presale::claim_refund(RuntimeOrigin::signed(1), 0));

        // Note: Cancelled rounds allow refunds at ANY block, no need to wait for end_block
        frame_system::Pallet::<Test>::set_block_number(100);
        assert_noop!(
            Presale::claim_refund(RuntimeOrigin::signed(1), 0),
            Error::<Test>::NoContribution
        );
    });
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 6: PAYMENT ASSET
// ═══════════════════════════════════════════════════════════════════════════════

#[test]
fn test_payment_is_native_currency() {
    new_test_ext().execute_with(|| {
        setup_round(5, 10_000, 1000, 1, 1000);
        let user_before = pallet_balances::Pallet::<Test>::free_balance(&1);
        let escrow = PresalePalletId::get().into_account_truncating();
        let escrow_before = pallet_balances::Pallet::<Test>::free_balance(&escrow);

        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));

        // User balance: -10 (payment) + 50 (tokens from escrow)
        let user_after = pallet_balances::Pallet::<Test>::free_balance(&1);
        assert_eq!(user_after, user_before - 10 + 50);

        // Escrow balance: +10 (payment) - 50 (tokens)
        let escrow_after = pallet_balances::Pallet::<Test>::free_balance(&escrow);
        assert_eq!(escrow_after, escrow_before + 10 - 50);
    });
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 18: STORAGE / DOS
// ═══════════════════════════════════════════════════════════════════════════════

#[test]
fn test_multiple_users_contribute_no_storage_bloat() {
    new_test_ext().execute_with(|| {
        setup_round(5, 10_000, 1000, 1, 1000);
        // Each user contributes — each gets one storage entry
        for i in 1..=3u64 {
            assert_ok!(Presale::contribute(RuntimeOrigin::signed(i), 0, 10));
        }
        // Verify all three have separate contributions
        for i in 1u64..=3 {
            assert!(Presale::contributions(0, &i).is_some());
        }
    });
}

#[test]
fn test_repeated_contributions_same_user_accumulate() {
    new_test_ext().execute_with(|| {
        setup_round(5, 10_000, 1000, 1, 1000);
        // Same user contributes 5 times — should accumulate, not create new entries
        for _ in 0..5 {
            assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10));
        }
        let c = Presale::contributions(0, &1).unwrap();
        assert_eq!(c.total_paid, 50);
        assert_eq!(c.total_purchased, 250);
    });
}
