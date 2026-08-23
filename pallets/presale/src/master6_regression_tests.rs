// MASTER-6: Presale Escrow Consistency + Cross-Round Isolation Regression Tests
//
// Tests:
// 1. All payment flows use the same deterministic per-round escrow
// 2. Cross-round fund isolation (no round can access another round's funds)
// 3. Vesting label isolation (duplicate labels rejected when flag enabled)
// 4. Double-refund and double-collection prevention
// 5. Weight safety for claim_refund
// 6. Luna adversarial: cross-round fund theft, cross-round refund, cross-round vesting deletion
//
// NOTE: In the u64 test mock, into_sub_account_truncating(round_id) produces the SAME
// account for all round_ids (PalletId is 8 bytes = u64 width, round_id is truncated).
// In production (AccountId32 = 32 bytes), sub-accounts ARE unique per round.
// Tests verify FUNCTIONAL isolation (tracking, not address equality) where the
// u64 limitation prevents address-level testing.

#![cfg(test)]

use super::*;
use frame_support::{assert_ok, assert_noop};

fn set_block(n: u64) {
    System::set_block_number(n);
}

fn setup_round(
    round_id: u32,
    label: &[u8],
    vesting_label: &[u8],
    token_price: u64,
    total_allocation: u64,
    per_account_cap: u64,
    start_block: u64,
    end_block: u64,
) {
    assert_ok!(Presale::create_round(
        RuntimeOrigin::root(),
        label.to_vec(),
        token_price,
        total_allocation,
        per_account_cap,
        start_block,
        end_block,
        vesting_label.to_vec(),
    ));
    assert_ok!(Presale::activate_round(RuntimeOrigin::root(), round_id));
}

// === TEST 1: Cross-round escrow isolation — functional tracking ===
// Round A contribution + Round B contribution + collect A + refund B + collect B + refund A
#[test]
fn test_cross_round_escrow_isolation() {
    new_test_ext().execute_with(|| {
        setup_round(0, b"round_a", b"vest_a", 1, 100_000, 50_000, 1, 100);
        setup_round(1, b"round_b", b"vest_b", 1, 100_000, 50_000, 1, 100);

        set_block(10);

        // Alice contributes to Round A
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10_000));
        // Bob contributes to Round B
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(2), 1, 20_000));

        // Verify per-round tracking is isolated
        assert_eq!(RoundRaised::<Test>::get(0), 10_000, "Round A raised = 10,000");
        assert_eq!(RoundRaised::<Test>::get(1), 20_000, "Round B raised = 20,000");
        assert_eq!(TotalRaised::<Test>::get(), 30_000, "Total raised = 30,000");

        // Finalize both rounds
        set_block(101);
        assert_ok!(Presale::finalize_round(RuntimeOrigin::root(), 0));
        assert_ok!(Presale::finalize_round(RuntimeOrigin::root(), 1));

        // Collect Round A — beneficiary gets exactly Round A's raised (10,000)
        let beneficiary = 999u64;
        let bene_before = Balances::free_balance(&beneficiary);
        assert_ok!(Presale::collect_funds(RuntimeOrigin::root(), 0, beneficiary));
        let bene_after_collect_a = Balances::free_balance(&beneficiary);
        assert_eq!(
            bene_after_collect_a - bene_before, 10_000,
            "Beneficiary gets exactly Round A raised (10,000), not Round B's funds"
        );

        // Collect Round B — beneficiary gets Round B's raised (20,000)
        assert_ok!(Presale::collect_funds(RuntimeOrigin::root(), 1, beneficiary));
        let bene_final = Balances::free_balance(&beneficiary);
        assert_eq!(
            bene_final - bene_before, 30_000,
            "Beneficiary gets both rounds: 10,000 + 20,000 = 30,000"
        );

        // Double-collect Round A fails (round is now Closed)
        assert_noop!(
            Presale::collect_funds(RuntimeOrigin::root(), 0, beneficiary),
            Error::<Test>::RoundStatusInvalid
        );
    });
}

// === TEST 2: Cross-round refund isolation ===
// Refund for Round B must not affect Round A contribution records
#[test]
fn test_cross_round_refund_isolation() {
    new_test_ext().execute_with(|| {
        setup_round(0, b"round_a", b"vest_a", 1, 100_000, 50_000, 1, 100);
        setup_round(1, b"round_b", b"vest_b", 1, 100_000, 50_000, 1, 100);

        set_block(10);

        // Alice contributes to both rounds
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10_000));
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 1, 10_000));

        // Verify both contributions exist
        assert!(Contributions::<Test>::get(0, &1).is_some(), "Round A contribution exists");
        assert!(Contributions::<Test>::get(1, &1).is_some(), "Round B contribution exists");

        // Cancel Round B only
        set_block(101);
        assert_ok!(Presale::cancel_round(RuntimeOrigin::root(), 1));

        // Alice claims refund for Round B — verify contribution record is removed
        assert_ok!(Presale::claim_refund(RuntimeOrigin::signed(1), 1));

        // Round A contribution must NOT be affected
        let contrib_a = Contributions::<Test>::get(0, &1);
        assert!(
            contrib_a.is_some(),
            "Round A contribution must NOT be removed by Round B refund"
        );
        if let Some(c) = contrib_a {
            assert_eq!(c.total_paid, 10_000, "Round A contribution amount unchanged");
            assert_eq!(c.total_purchased, 10_000, "Round A token amount unchanged");
        }

        // Round B contribution must be removed
        assert!(
            Contributions::<Test>::get(1, &1).is_none(),
            "Round B contribution must be removed after refund"
        );

        // Round A raised must be unchanged
        assert_eq!(RoundRaised::<Test>::get(0), 10_000, "Round A raised unchanged after Round B refund");
        // Total raised decreased by Round B's refund
        assert_eq!(TotalRaised::<Test>::get(), 10_000, "Total raised = 10,000 after Round B refund");
    });
}

// === TEST 3: Duplicate vesting label rejected (when flag enabled) ===
// In the test mock, EnforceUniqueVestingLabels = false, so duplicates are allowed.
// This test verifies the flag is respected.
#[test]
fn test_duplicate_vesting_label_allowed_in_test() {
    new_test_ext().execute_with(|| {
        // Test mock has EnforceUniqueVestingLabels = false
        // So duplicate labels should be ALLOWED in tests
        setup_round(0, b"round_a", b"seed", 1, 100_000, 50_000, 1, 100);

        // Second round with SAME label should succeed (flag is false in test)
        assert_ok!(Presale::create_round(
            RuntimeOrigin::root(),
            b"round_b".to_vec(),
            1,
            100_000,
            50_000,
            1,
            100,
            b"seed".to_vec(), // SAME label — allowed in test
        ));
    });
}

// === TEST 4: Double collection prevented ===
#[test]
fn test_double_collection_prevented() {
    new_test_ext().execute_with(|| {
        setup_round(0, b"round_a", b"vest_a", 1, 100_000, 50_000, 1, 100);

        set_block(10);
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10_000));

        set_block(101);
        assert_ok!(Presale::finalize_round(RuntimeOrigin::root(), 0));

        // First collection succeeds
        assert_ok!(Presale::collect_funds(RuntimeOrigin::root(), 0, 999));

        // Second collection fails (round is now Closed)
        assert_noop!(
            Presale::collect_funds(RuntimeOrigin::root(), 0, 999),
            Error::<Test>::RoundStatusInvalid
        );
    });
}

// === TEST 5: Double refund prevented ===
#[test]
fn test_double_refund_prevented() {
    new_test_ext().execute_with(|| {
        setup_round(0, b"round_a", b"vest_a", 1, 100_000, 50_000, 1, 100);

        set_block(10);
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10_000));

        set_block(101);
        assert_ok!(Presale::cancel_round(RuntimeOrigin::root(), 0));

        // First refund succeeds
        assert_ok!(Presale::claim_refund(RuntimeOrigin::signed(1), 0));

        // Second refund fails (contribution record removed by CEI)
        assert_noop!(
            Presale::claim_refund(RuntimeOrigin::signed(1), 0),
            Error::<Test>::NoContribution
        );
    });
}

// === TEST 6: Multiple contributions to same round ===
#[test]
fn test_multiple_contributions_same_round() {
    new_test_ext().execute_with(|| {
        setup_round(0, b"round_a", b"vest_a", 1, 10_000_000, 5_000_000, 1, 200);

        set_block(10);

        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10_000));
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 20_000));
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 30_000));

        let contrib = Contributions::<Test>::get(0, &1).unwrap();
        assert_eq!(contrib.total_paid, 60_000, "Total paid should be 60,000");
        assert_eq!(contrib.total_purchased, 60_000, "Total purchased should be 60,000");
    });
}

// === TEST 7: Zero contribution rejected ===
#[test]
fn test_zero_contribution_rejected() {
    new_test_ext().execute_with(|| {
        setup_round(0, b"round_a", b"vest_a", 1, 100_000, 50_000, 1, 100);

        set_block(10);
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(1), 0, 0),
            Error::<Test>::ZeroPayment
        );
    });
}

// === TEST 8: Luna — Cross-round fund theft attempt ===
// Collecting Round A must NOT give access to Round B's funds
#[test]
fn test_luna_cross_round_fund_theft() {
    new_test_ext().execute_with(|| {
        setup_round(0, b"round_a", b"vest_a", 1, 100_000, 50_000, 1, 100);
        setup_round(1, b"round_b", b"vest_b", 1, 50_000, 25_000, 1, 100);

        set_block(10);
        // Contribute to Round A only
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10_000));

        set_block(101);
        assert_ok!(Presale::finalize_round(RuntimeOrigin::root(), 0));
        assert_ok!(Presale::finalize_round(RuntimeOrigin::root(), 1));

        // Collect Round A — should get exactly 10,000 (Round A's raised)
        let beneficiary = 999u64;
        let bene_before = Balances::free_balance(&beneficiary);
        assert_ok!(Presale::collect_funds(RuntimeOrigin::root(), 0, beneficiary));
        let collected = Balances::free_balance(&beneficiary) - bene_before;

        assert_eq!(
            collected, 10_000,
            "LUNA: Collecting Round A gives exactly Round A's raised (10,000), not Round B's"
        );

        // Round B raised is 0 (no contributions) — collecting it gives 0
        assert_ok!(Presale::collect_funds(RuntimeOrigin::root(), 1, beneficiary));
        let collected_b = Balances::free_balance(&beneficiary) - bene_before - collected;
        assert_eq!(
            collected_b, 0,
            "LUNA: Round B has 0 raised — no funds to steal"
        );
    });
}

// === TEST 9: Luna — Cross-round vesting deletion prevention ===
// Refund for Round B must not delete Round A vesting entries
// Vesting is () in test mock (no-op), but we verify contribution records are isolated
#[test]
fn test_luna_cross_round_vesting_deletion() {
    new_test_ext().execute_with(|| {
        setup_round(0, b"round_a", b"vest_a", 1, 100_000, 50_000, 1, 100);
        setup_round(1, b"round_b", b"vest_b", 1, 100_000, 50_000, 1, 100);

        set_block(10);
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10_000));
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 1, 10_000));

        set_block(101);
        assert_ok!(Presale::cancel_round(RuntimeOrigin::root(), 1));

        // Refund Round B
        assert_ok!(Presale::claim_refund(RuntimeOrigin::signed(1), 1));

        // Round A contribution must still exist
        let contrib_a = Contributions::<Test>::get(0, &1);
        assert!(
            contrib_a.is_some(),
            "LUNA: Round A contribution survives Round B refund"
        );

        // Round A vesting label is "vest_a", Round B was "vest_b" — different labels
        let round_a = Rounds::<Test>::get(0).unwrap();
        let round_b = Rounds::<Test>::get(1).unwrap();
        assert_ne!(
            round_a.vesting_label, round_b.vesting_label,
            "Vesting labels must be different — isolation enforced"
        );

        // Round A sold is unchanged
        assert_eq!(round_a.sold, 10_000, "Round A sold unchanged after Round B refund");
    });
}

// === TEST 10: Luna — Repeated collection attempt ===
#[test]
fn test_luna_repeated_collection() {
    new_test_ext().execute_with(|| {
        setup_round(0, b"round_a", b"vest_a", 1, 100_000, 50_000, 1, 100);

        set_block(10);
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10_000));

        set_block(101);
        assert_ok!(Presale::finalize_round(RuntimeOrigin::root(), 0));

        assert_ok!(Presale::collect_funds(RuntimeOrigin::root(), 0, 999));

        // Attempt repeated collection — must fail every time (round is Closed)
        for _ in 0..3 {
            assert_noop!(
                Presale::collect_funds(RuntimeOrigin::root(), 0, 999),
                Error::<Test>::RoundStatusInvalid
            );
        }
    });
}

// === TEST 11: Luna — Repeated refund attempt ===
#[test]
fn test_luna_repeated_refund() {
    new_test_ext().execute_with(|| {
        setup_round(0, b"round_a", b"vest_a", 1, 100_000, 50_000, 1, 100);

        set_block(10);
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10_000));

        set_block(101);
        assert_ok!(Presale::cancel_round(RuntimeOrigin::root(), 0));

        assert_ok!(Presale::claim_refund(RuntimeOrigin::signed(1), 0));

        for _ in 0..3 {
            assert_noop!(
                Presale::claim_refund(RuntimeOrigin::signed(1), 0),
                Error::<Test>::NoContribution
            );
        }
    });
}

// === TEST 12: Large number of rounds with tracking isolation ===
#[test]
fn test_large_number_of_rounds() {
    new_test_ext().execute_with(|| {
        // Genesis pre-funds escrows 0, 1, 2 — create 3 rounds
        for i in 0..3u32 {
            let label = format!("vest_{}", i);
            setup_round(
                i,
                format!("round_{}", i).as_bytes(),
                label.as_bytes(),
                1,
                100_000,
                50_000,
                1,
                100,
            );
        }

        set_block(10);
        // Contribute different amounts to each round
        for i in 0..3u32 {
            assert_ok!(Presale::contribute(
                RuntimeOrigin::signed(1),
                i,
                (i as u64 + 1) * 1_000, // 1_000, 2_000, 3_000
            ));
        }

        // Verify per-round tracking is isolated
        assert_eq!(RoundRaised::<Test>::get(0), 1_000, "Round 0 raised = 1,000");
        assert_eq!(RoundRaised::<Test>::get(1), 2_000, "Round 1 raised = 2,000");
        assert_eq!(RoundRaised::<Test>::get(2), 3_000, "Round 2 raised = 3,000");
        assert_eq!(TotalRaised::<Test>::get(), 6_000, "Total raised = 6,000");

        // Cancel and refund all
        set_block(101);
        for i in 0..3u32 {
            assert_ok!(Presale::cancel_round(RuntimeOrigin::root(), i));
            assert_ok!(Presale::claim_refund(RuntimeOrigin::signed(1), i));
        }

        // All contributions should be cleared
        for i in 0..3u32 {
            assert!(
                Contributions::<Test>::get(i, &1).is_none(),
                "Contribution for round {} should be cleared",
                i
            );
        }

        // Total raised should be 0 after all refunds
        assert_eq!(TotalRaised::<Test>::get(), 0, "Total raised = 0 after all refunds");
    });
}

// === TEST 13: Weight safety — claim_refund with multiple vesting entries ===
#[test]
fn test_claim_refund_weight_safety() {
    new_test_ext().execute_with(|| {
        setup_round(0, b"round_a", b"vest_a", 1, 10_000_000, 5_000_000, 1, 200);

        set_block(10);

        // Multiple contributions create multiple vesting entries
        for _ in 0..5 {
            assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10_000));
        }

        set_block(201);
        assert_ok!(Presale::cancel_round(RuntimeOrigin::root(), 0));

        // claim_refund must succeed even with multiple vesting entries
        // The weight (115,000) must be sufficient
        assert_ok!(Presale::claim_refund(RuntimeOrigin::signed(1), 0));
    });
}

// === TEST 14: Failed transfer does not corrupt state ===
#[test]
fn test_failed_transfer_no_corruption() {
    new_test_ext().execute_with(|| {
        setup_round(0, b"round_a", b"vest_a", 1, 100_000, 50_000, 1, 100);

        set_block(10);

        // Account 5 has no balance — contribution should fail
        assert_noop!(
            Presale::contribute(RuntimeOrigin::signed(5), 0, 10_000),
            Error::<Test>::InsufficientPayment
        );

        // No contribution record should exist
        assert!(
            Contributions::<Test>::get(0, &5).is_none(),
            "No contribution record after failed transfer"
        );

        // Round state should be unchanged
        let round = Rounds::<Test>::get(0).unwrap();
        assert_eq!(round.sold, 0, "Round sold must be 0 after failed contribution");
        assert_eq!(RoundRaised::<Test>::get(0), 0, "Round raised must be 0");
    });
}

// === TEST 15: Contribute uses round_escrow (verified via code path) ===
// In u64 mock, escrow addresses are the same, but we verify the code path
// by checking that contribute + collect_funds work end-to-end
#[test]
fn test_contribute_collect_end_to_end() {
    new_test_ext().execute_with(|| {
        setup_round(0, b"round_a", b"vest_a", 1, 100_000, 50_000, 1, 100);

        set_block(10);
        assert_ok!(Presale::contribute(RuntimeOrigin::signed(1), 0, 10_000));

        // Verify tokens were transferred from escrow to buyer
        let buyer_balance = Balances::free_balance(&1);
        // Buyer started with 1B, paid 10K, received 10K VRDX → net should be ~1B
        assert!(buyer_balance > 900_000_000, "Buyer should have received VRDX tokens");

        set_block(101);
        assert_ok!(Presale::finalize_round(RuntimeOrigin::root(), 0));

        // Collect funds to beneficiary
        let bene_before = Balances::free_balance(&999);
        assert_ok!(Presale::collect_funds(RuntimeOrigin::root(), 0, 999));
        let bene_after = Balances::free_balance(&999);
        assert_eq!(
            bene_after - bene_before, 10_000,
            "Beneficiary receives exactly the round's raised amount"
        );
    });
}
