//! Halborn pre-audit security tests for presale refund → vesting cleanup.
//!
//! These tests verify the critical security properties:
//! 1. collect_funds() CANNOT run on Failed or Cancelled rounds
//! 2. claim_refund() works correctly with multiple contributions (vesting cleanup)
//! 3. cancel_round() enables immediate refunds without waiting for end_block
//! 4. finalize_round() correctly determines Success vs Failure based on min_allocation
//! 5. Admin cannot drain escrow from a round where users deserve refunds

#![allow(unused_imports)]
use super::*;
use crate::*;
use frame_support::{assert_noop, assert_ok};
use sp_runtime::traits::AccountIdConversion;

fn escrow_account() -> u64 {
    PresalePalletId::get().into_account_truncating()
}

fn get_balance(who: u64) -> u64 {
    Balances::free_balance(who)
}

fn get_round(round_id: u32) -> SaleRound<u64, u64> {
    Rounds::<Test>::get(round_id).unwrap()
}

fn create_round(price: u64, allocation: u64, cap: u64, start: u64, end: u64) {
    assert_ok!(Presale::create_round(
        RuntimeOrigin::root(),
        b"halborn".to_vec(),
        price,
        allocation,
        cap,
        start,
        end,
        b"vest".to_vec(),
    ));
}

fn activate(round_id: u32) {
    assert_ok!(Presale::activate_round(RuntimeOrigin::root(), round_id));
}

fn finalize(round_id: u32) {
    assert_ok!(Presale::finalize_round(RuntimeOrigin::root(), round_id));
}

fn cancel(round_id: u32) {
    assert_ok!(Presale::cancel_round(RuntimeOrigin::root(), round_id));
}

fn contribute(who: u64, round_id: u32, amount: u64) {
    assert_ok!(Presale::contribute(RuntimeOrigin::signed(who), round_id, amount));
}

fn set_min(round_id: u32, min: u64) {
    assert_ok!(Presale::set_min_allocation(RuntimeOrigin::root(), round_id, min));
}

// ============================================================
// TEST 1: collect_funds() CANNOT run on Failed rounds
// ============================================================
#[test]
fn halborn_collect_funds_on_failed_round_rejected() {
    new_test_ext().execute_with(|| {
        create_round(5, 10000, 5000, 1, 100);
        set_min(0, 1000);
        activate(0);
        set_block(10);

        let initial = get_balance(1);
        contribute(1, 0, 20); // 100 tokens (below min 1000)

        set_block(100);
        finalize(0);
        assert_eq!(get_round(0).status, RoundStatus::Failed);

        // CRITICAL: collect_funds MUST be rejected on Failed rounds
        assert_noop!(
            Presale::collect_funds(RuntimeOrigin::root(), 0, 999),
            Error::<Test>::RoundStatusInvalid
        );

        // But refunds SHOULD work — user returns to initial balance
        assert_ok!(Presale::claim_refund(RuntimeOrigin::signed(1), 0));
        assert_eq!(get_balance(1), initial);
    });
}

// ============================================================
// TEST 2: collect_funds() CANNOT run on Cancelled rounds
// ============================================================
#[test]
fn halborn_collect_funds_on_cancelled_round_rejected() {
    new_test_ext().execute_with(|| {
        create_round(5, 10000, 5000, 1, 100);
        activate(0);
        set_block(10);

        let initial = get_balance(1);
        contribute(1, 0, 20);

        cancel(0);
        assert_eq!(get_round(0).status, RoundStatus::Cancelled);

        assert_noop!(
            Presale::collect_funds(RuntimeOrigin::root(), 0, 999),
            Error::<Test>::RoundStatusInvalid
        );

        // Refunds work immediately — user returns to initial balance
        assert_ok!(Presale::claim_refund(RuntimeOrigin::signed(1), 0));
        assert_eq!(get_balance(1), initial);
    });
}

// ============================================================
// TEST 3: claim_refund() CANNOT run on Successful rounds
// ============================================================
#[test]
fn halborn_refund_on_successful_round_rejected() {
    new_test_ext().execute_with(|| {
        create_round(5, 10000, 5000, 1, 100);
        activate(0);
        set_block(10);

        contribute(1, 0, 20); // 100 tokens

        set_block(100);
        finalize(0);
        assert_eq!(get_round(0).status, RoundStatus::Successful);

        assert_noop!(
            Presale::claim_refund(RuntimeOrigin::signed(1), 0),
            Error::<Test>::RoundNotRefundable
        );

        // But collect_funds SHOULD work
        assert_ok!(Presale::collect_funds(RuntimeOrigin::root(), 0, 999));
    });
}

// ============================================================
// TEST 4: Multiple contributions → refund works correctly
// ============================================================
#[test]
fn halborn_multiple_contributions_refund() {
    new_test_ext().execute_with(|| {
        create_round(5, 10000, 5000, 1, 100);
        activate(0);
        set_block(10);

        let initial = get_balance(1);
        contribute(1, 0, 10); // 50 tokens, payment=10
        contribute(1, 0, 20); // 100 tokens, payment=20
        contribute(1, 0, 30); // 150 tokens, payment=30

        let contribution = Contributions::<Test>::get(0, &1).unwrap();
        assert_eq!(contribution.total_purchased, 300);
        assert_eq!(contribution.total_paid, 60);

        set_block(50);
        cancel(0);

        assert_ok!(Presale::claim_refund(RuntimeOrigin::signed(1), 0));
        assert_eq!(get_balance(1), initial);

        assert!(Contributions::<Test>::get(0, &1).is_none());
    });
}

// ============================================================
// TEST 5: finalize with min_allocation → Failed
// ============================================================
#[test]
fn halborn_finalize_below_min_allocation_failed() {
    new_test_ext().execute_with(|| {
        create_round(5, 10000, 5000, 1, 100);
        set_min(0, 1000);
        activate(0);
        set_block(10);

        contribute(1, 0, 10); // 50 tokens
        set_block(100);

        finalize(0);
        assert_eq!(get_round(0).status, RoundStatus::Failed);
    });
}

// ============================================================
// TEST 6: finalize with min_allocation → Successful
// ============================================================
#[test]
fn halborn_finalize_above_min_allocation_successful() {
    new_test_ext().execute_with(|| {
        create_round(5, 10000, 5000, 1, 100);
        set_min(0, 40);
        activate(0);
        set_block(10);

        contribute(1, 0, 10); // 50 tokens (above min 40)
        set_block(100);

        finalize(0);
        assert_eq!(get_round(0).status, RoundStatus::Successful);
    });
}

// ============================================================
// TEST 7: cancel only works on Active rounds
// ============================================================
#[test]
fn halborn_cancel_only_active_round() {
    new_test_ext().execute_with(|| {
        create_round(5, 10000, 5000, 1, 100);

        assert_noop!(
            Presale::cancel_round(RuntimeOrigin::root(), 0),
            Error::<Test>::RoundStatusInvalid
        );

        activate(0);
        assert_ok!(Presale::cancel_round(RuntimeOrigin::root(), 0));
        assert_eq!(get_round(0).status, RoundStatus::Cancelled);

        assert_noop!(
            Presale::cancel_round(RuntimeOrigin::root(), 0),
            Error::<Test>::RoundStatusInvalid
        );
    });
}

// ============================================================
// TEST 8: finalize requires Active + past end_block
// ============================================================
#[test]
fn halborn_finalize_requires_active_and_past_end() {
    new_test_ext().execute_with(|| {
        create_round(5, 10000, 5000, 1, 100);
        activate(0);
        set_block(50);

        assert_noop!(
            Presale::finalize_round(RuntimeOrigin::root(), 0),
            Error::<Test>::RoundNotEnded
        );

        set_block(100);
        assert_ok!(Presale::finalize_round(RuntimeOrigin::root(), 0));
    });
}

// ============================================================
// TEST 9: set_min_allocation only works on Pending rounds
// ============================================================
#[test]
fn halborn_set_min_allocation_only_pending() {
    new_test_ext().execute_with(|| {
        create_round(5, 10000, 5000, 1, 100);

        assert_ok!(Presale::set_min_allocation(RuntimeOrigin::root(), 0, 5000));
        assert_eq!(get_round(0).min_allocation, 5000);

        activate(0);
        assert_noop!(
            Presale::set_min_allocation(RuntimeOrigin::root(), 0, 1000),
            Error::<Test>::RoundStatusInvalid
        );

        // min_allocation > total_allocation fails
        create_round(5, 10000, 5000, 1, 100);
        assert_noop!(
            Presale::set_min_allocation(RuntimeOrigin::root(), 1, 20000),
            Error::<Test>::InvalidMinAllocation
        );
    });
}

// ============================================================
// TEST 10: zero sold + zero min_allocation → Successful
// ============================================================
#[test]
fn halborn_zero_sold_zero_min_successful() {
    new_test_ext().execute_with(|| {
        create_round(5, 10000, 5000, 1, 100);
        activate(0);
        set_block(100);

        finalize(0);
        assert_eq!(get_round(0).status, RoundStatus::Successful);

        assert_ok!(Presale::collect_funds(RuntimeOrigin::root(), 0, 999));
    });
}

// ============================================================
// TEST 11: Full successful lifecycle
// ============================================================
#[test]
fn halborn_full_successful_lifecycle() {
    new_test_ext().execute_with(|| {
        create_round(5, 10000, 5000, 1, 100);
        assert_eq!(get_round(0).status, RoundStatus::Pending);

        activate(0);
        assert_eq!(get_round(0).status, RoundStatus::Active);

        set_block(10);
        contribute(1, 0, 20); // 100 tokens

        set_block(100);
        finalize(0);
        assert_eq!(get_round(0).status, RoundStatus::Successful);

        let treasury_before = get_balance(999);
        assert_ok!(Presale::collect_funds(RuntimeOrigin::root(), 0, 999));
        assert_eq!(get_round(0).status, RoundStatus::Closed);
        assert_eq!(get_balance(999), treasury_before + 20); // payment of 20 collected

        assert_noop!(
            Presale::collect_funds(RuntimeOrigin::root(), 0, 999),
            Error::<Test>::RoundStatusInvalid
        );
    });
}

// ============================================================
// TEST 12: Full failed lifecycle with multiple users
// ============================================================
#[test]
fn halborn_full_failed_lifecycle() {
    new_test_ext().execute_with(|| {
        create_round(5, 10000, 5000, 1, 100);
        set_min(0, 500);
        activate(0);

        let init1 = get_balance(1);
        let init2 = get_balance(2);
        set_block(10);
        contribute(1, 0, 10); // 50 tokens
        contribute(2, 0, 10); // 50 tokens (total 100, below 500)

        set_block(100);
        finalize(0);
        assert_eq!(get_round(0).status, RoundStatus::Failed);

        assert_ok!(Presale::claim_refund(RuntimeOrigin::signed(1), 0));
        assert_ok!(Presale::claim_refund(RuntimeOrigin::signed(2), 0));

        assert_eq!(get_balance(1), init1);
        assert_eq!(get_balance(2), init2);

        assert!(Contributions::<Test>::get(0, &1).is_none());
        assert!(Contributions::<Test>::get(0, &2).is_none());
    });
}

// ============================================================
// TEST 13: Full cancelled lifecycle (cancel before end_block)
// ============================================================
#[test]
fn halborn_full_cancelled_lifecycle() {
    new_test_ext().execute_with(|| {
        create_round(5, 10000, 5000, 1, 100);
        activate(0);
        set_block(10);

        let initial = get_balance(1);
        contribute(1, 0, 20);
        contribute(2, 0, 10);

        cancel(0);
        assert_eq!(get_round(0).status, RoundStatus::Cancelled);

        // Refunds work immediately (block is 10, end_block is 100)
        assert_ok!(Presale::claim_refund(RuntimeOrigin::signed(1), 0));
        assert_eq!(get_balance(1), initial);
    });
}

// ============================================================
// TEST 14: THE critical Halborn test — admin cannot drain failed round
// ============================================================
#[test]
fn halborn_admin_cannot_drain_failed_round() {
    new_test_ext().execute_with(|| {
        create_round(5, 10000, 5000, 1, 100);
        set_min(0, 1000);
        activate(0);
        set_block(10);

        let init1 = get_balance(1);
        let init2 = get_balance(2);
        let init3 = get_balance(3);
        contribute(1, 0, 50); // 250 tokens
        contribute(2, 0, 30); // 150 tokens
        contribute(3, 0, 20); // 100 tokens
        // Total: 500 tokens, min=1000 → FAILED

        set_block(100);
        finalize(0);
        assert_eq!(get_round(0).status, RoundStatus::Failed);

        // Admin tries to collect funds — MUST FAIL
        assert_noop!(
            Presale::collect_funds(RuntimeOrigin::root(), 0, 999),
            Error::<Test>::RoundStatusInvalid
        );

        // All users can still get refunds
        assert_ok!(Presale::claim_refund(RuntimeOrigin::signed(1), 0));
        assert_ok!(Presale::claim_refund(RuntimeOrigin::signed(2), 0));
        assert_ok!(Presale::claim_refund(RuntimeOrigin::signed(3), 0));

        assert_eq!(get_balance(1), init1);
        assert_eq!(get_balance(2), init2);
        assert_eq!(get_balance(3), init3);
    });
}

// ============================================================
// TEST 15: Admin cannot skip finalize and collect directly
// ============================================================
#[test]
fn halborn_admin_cannot_collect_without_finalize() {
    new_test_ext().execute_with(|| {
        create_round(5, 10000, 5000, 1, 100);
        activate(0);
        set_block(10);
        contribute(1, 0, 20); // 100 tokens

        set_block(100);

        // Without finalize_round, status is still Active
        // collect_funds MUST fail (status != Successful)
        assert_noop!(
            Presale::collect_funds(RuntimeOrigin::root(), 0, 999),
            Error::<Test>::RoundStatusInvalid
        );

        // After finalize, it works
        finalize(0);
        assert_ok!(Presale::collect_funds(RuntimeOrigin::root(), 0, 999));
    });
}
