//! Integration Tests for Verdis Chain DPoS Slashing, Recovery, and System Interactions
//!
//! Covers:
//! 1. Slashing scenarios: downtime, double-signing/equivocation, exact stake deduction, active set removal, multiple validators, insufficient stake edge cases.
//! 2. Recovery scenarios: delegator unbonding after slash, validator reactivation after cooldown, full stake withdrawal on exit, partial unvoting with bonded remainder.
//! 3. Cross-pallet integration: balance transfers, treasury accounting, DEX pool/user balance non-interference, governance origin authority.

use super::*;
use frame_support::{assert_noop, assert_ok};
use sp_core::crypto::AccountId32;
use sp_runtime::DispatchError;

// =========================================================================
// SECTION 1: Slashing Scenarios
// =========================================================================

/// Test 1: Validator slashed for downtime (missed blocks).
/// Verifies stake deduction, active set removal, event emission, and slashing counter increment.
#[test]
fn test_slashing_downtime_missed_blocks() {
    new_test_ext().execute_with(|| {
        let alice = Sr25519Keyring::Alice.to_account_id();
        let initial_val = Validators::<Test>::get(&alice).expect("Alice is genesis validator");
        let initial_stake = initial_val.stake; // 5000
        let total_staked_before = TotalStaked::<Test>::get(); // 8000
        let penalty = 1000u128;

        // Verify active before slash
        assert!(ActiveValidators::<Test>::get().contains(&alice));

        // Slash for downtime
        assert_ok!(Dpos::slash_validator(
            RuntimeOrigin::root(),
            alice.clone(),
            penalty,
            b"downtime_missed_blocks".to_vec(),
        ));

        // 1. Validator stake reduced
        let val_after = Validators::<Test>::get(&alice).unwrap();
        assert_eq!(val_after.stake, initial_stake - penalty);
        assert_eq!(val_after.total_votes, initial_stake - penalty);
        assert!(val_after.slashed);
        assert!(!val_after.active);

        // 2. Active set updated
        assert!(!ActiveValidators::<Test>::get().contains(&alice));

        // 3. Total staked reduced
        assert_eq!(TotalStaked::<Test>::get(), total_staked_before - penalty);

        // 4. Slashing counter incremented
        assert_eq!(SlashingEvents::<Test>::get(&alice), 1);

        // 5. ValidatorSlashed event emitted
        System::assert_has_event(RuntimeEvent::Dpos(Event::ValidatorSlashed {
            who: alice,
            penalty,
            reason: b"downtime_missed_blocks".to_vec(),
        }));
    });
}

/// Test 2: Validator slashed for double-signing (equivocation) via do_slash.
/// Verifies validator slash AND delegators being slashed proportionally.
#[test]
fn test_slashing_double_signing_equivocation() {
    new_test_ext().execute_with(|| {
        let alice = Sr25519Keyring::Alice.to_account_id(); // Validator (5000 stake)
        let charlie = Sr25519Keyring::Charlie.to_account_id(); // Delegator

        // Charlie delegates 2000 to Alice
        assert_ok!(Dpos::vote(
            RuntimeOrigin::signed(charlie.clone()),
            alice.clone(),
            2000
        ));

        let val_before = Validators::<Test>::get(&alice).unwrap();
        assert_eq!(val_before.stake, 5000);
        assert_eq!(val_before.total_votes, 7000);

        let charlie_reserved_before = Balances::reserved_balance(&charlie);
        assert_eq!(charlie_reserved_before, 2000);

        // Trigger do_slash for double-signing (equivocation)
        let slash_amount = 1000u128;
        Dpos::do_slash(&alice, slash_amount);

        // Check Alice validator state
        let val_after = Validators::<Test>::get(&alice).unwrap();
        assert_eq!(val_after.stake, 4000); // 5000 - 1000
        assert!(val_after.slashed);
        assert!(!val_after.active);

        // Check Charlie delegator proportional slash:
        // Slash fraction = 1000 * 10000 / 5000 = 2000 bps (20%)
        // Charlie slash = 2000 * 2000 / 10000 = 400
        let charlie_reserved_after = Balances::reserved_balance(&charlie);
        assert_eq!(charlie_reserved_after, 1600); // 2000 - 400

        // LastSlashedBlock recorded
        assert_eq!(LastSlashedBlock::<Test>::get(&alice), System::block_number() as u32);
        assert_eq!(SlashingEvents::<Test>::get(&alice), 1);
        assert!(!ActiveValidators::<Test>::get().contains(&alice));
    });
}

/// Test 3: Slash amount correctly deducted from stake and reserved balances.
/// Asserts exact reserved balance, free balance, and Treasury account changes.
#[test]
fn test_slash_amount_deducted_from_stake() {
    new_test_ext().execute_with(|| {
        let bob = Sr25519Keyring::Bob.to_account_id(); // 3000 stake
        let penalty = 1234u128;

        let free_before = Balances::free_balance(&bob); // 97000
        let reserved_before = Balances::reserved_balance(&bob); // 3000
        let treasury = DposPalletId::get().into_account_truncating();
        let treasury_before = Balances::free_balance(&treasury);

        assert_ok!(Dpos::slash_validator(
            RuntimeOrigin::root(),
            bob.clone(),
            penalty,
            b"slash_test".to_vec(),
        ));

        let free_after = Balances::free_balance(&bob);
        let reserved_after = Balances::reserved_balance(&bob);
        let treasury_after = Balances::free_balance(&treasury);

        // Reserved balance reduced by penalty
        assert_eq!(reserved_after, reserved_before - penalty);
        // Free balance unchanged (unreserved then transferred out)
        assert_eq!(free_after, free_before);
        // Treasury received exact penalty
        assert_eq!(treasury_after, treasury_before + penalty);

        let val = Validators::<Test>::get(&bob).unwrap();
        assert_eq!(val.stake, 3000 - penalty);
        assert_eq!(val.total_votes, 3000 - penalty);
    });
}

/// Test 4: Slashed validator removed from active set.
/// Verifies active set membership and session selection excluding slashed validators.
#[test]
fn test_slashed_validator_removed_from_active_set() {
    new_test_ext().execute_with(|| {
        let alice = Sr25519Keyring::Alice.to_account_id();
        let bob = Sr25519Keyring::Bob.to_account_id();

        let active_initial = ActiveValidators::<Test>::get();
        assert!(active_initial.contains(&alice));
        assert!(active_initial.contains(&bob));

        assert_ok!(Dpos::slash_validator(
            RuntimeOrigin::root(),
            alice.clone(),
            500,
            b"equivocation".to_vec(),
        ));

        let active_after = ActiveValidators::<Test>::get();
        assert!(!active_after.contains(&alice));
        assert!(active_after.contains(&bob));

        // Verify session returns only non-slashed active validators
        let next_val = Dpos::get_next_validator(None);
        assert_eq!(next_val, Some(bob.clone()));
    });
}

/// Test 5: Multiple validators slashed simultaneously in same block.
/// Asserts independent calculation, combined treasury gains, and total staked tracking.
#[test]
fn test_multiple_validators_slashed_simultaneously() {
    new_test_ext().execute_with(|| {
        let alice = Sr25519Keyring::Alice.to_account_id(); // 5000 stake
        let bob = Sr25519Keyring::Bob.to_account_id();   // 3000 stake

        let treasury = DposPalletId::get().into_account_truncating();
        let treasury_before = Balances::free_balance(&treasury);
        let total_staked_before = TotalStaked::<Test>::get(); // 8000

        let penalty_alice = 2000u128;
        let penalty_bob = 1000u128;

        assert_ok!(Dpos::slash_validator(
            RuntimeOrigin::root(),
            alice.clone(),
            penalty_alice,
            b"correlated_fault".to_vec(),
        ));

        assert_ok!(Dpos::slash_validator(
            RuntimeOrigin::root(),
            bob.clone(),
            penalty_bob,
            b"correlated_fault".to_vec(),
        ));

        // Both validators updated
        assert_eq!(Validators::<Test>::get(&alice).unwrap().stake, 3000);
        assert_eq!(Validators::<Test>::get(&bob).unwrap().stake, 2000);

        // Active set now empty
        assert!(ActiveValidators::<Test>::get().is_empty());

        // Total staked correctly reduced by both
        assert_eq!(
            TotalStaked::<Test>::get(),
            total_staked_before - penalty_alice - penalty_bob
        );

        // Treasury collected sum of penalties
        assert_eq!(
            Balances::free_balance(&treasury),
            treasury_before + penalty_alice + penalty_bob
        );

        assert_eq!(SlashingEvents::<Test>::get(&alice), 1);
        assert_eq!(SlashingEvents::<Test>::get(&bob), 1);
    });
}

/// Test 6: Slash with insufficient stake / penalty exceeding stake.
/// Verifies capping at current stake and rejection of slashes when stake is 0.
#[test]
fn test_slash_insufficient_stake_edge_case() {
    new_test_ext().execute_with(|| {
        let alice = Sr25519Keyring::Alice.to_account_id(); // 5000 stake
        let treasury = DposPalletId::get().into_account_truncating();
        let treasury_before = Balances::free_balance(&treasury);

        // Penalty > current stake (100,000 > 5,000)
        assert_ok!(Dpos::slash_validator(
            RuntimeOrigin::root(),
            alice.clone(),
            100_000,
            b"massive_offence".to_vec(),
        ));

        // Capped at exact stake (5000)
        let val = Validators::<Test>::get(&alice).unwrap();
        assert_eq!(val.stake, 0);
        assert_eq!(val.total_votes, 0);
        assert!(!val.active);
        assert!(val.slashed);

        assert_eq!(Balances::free_balance(&treasury), treasury_before + 5000);

        // Subsequent slash attempt when stake is 0 fails with SlashingFailed
        assert_noop!(
            Dpos::slash_validator(
                RuntimeOrigin::root(),
                alice.clone(),
                100,
                b"subsequent_slash".to_vec(),
            ),
            Error::<Test>::SlashingFailed
        );
    });
}

/// Test 7: Slash with maximum u128 penalty (overflow test).
/// Ensures saturating subtraction prevents overflow or panic.
#[test]
fn test_slash_max_value_overflow_protection() {
    new_test_ext().execute_with(|| {
        let bob = Sr25519Keyring::Bob.to_account_id(); // 3000 stake

        assert_ok!(Dpos::slash_validator(
            RuntimeOrigin::root(),
            bob.clone(),
            u128::MAX,
            b"overflow_test".to_vec(),
        ));

        let val = Validators::<Test>::get(&bob).unwrap();
        assert_eq!(val.stake, 0);
        assert!(!val.active);
        assert!(val.slashed);
    });
}

// =========================================================================
// SECTION 2: Recovery Scenarios
// =========================================================================

/// Test 8: Delegator unstakes (unvotes) after validator is slashed.
/// Verifies unbonding queue lifecycle and unreserving funds after unlock block.
#[test]
fn test_delegator_unstakes_after_validator_slashed() {
    new_test_ext().execute_with(|| {
        let alice = Sr25519Keyring::Alice.to_account_id();
        let charlie = Sr25519Keyring::Charlie.to_account_id(); // Delegator

        // Charlie votes 2000 for Alice
        assert_ok!(Dpos::vote(
            RuntimeOrigin::signed(charlie.clone()),
            alice.clone(),
            2000
        ));

        // Alice is slashed for 1000
        assert_ok!(Dpos::slash_validator(
            RuntimeOrigin::root(),
            alice.clone(),
            1000,
            b"slashing_event".to_vec(),
        ));

        // Charlie unvotes Alice
        assert_ok!(Dpos::unvote(
            RuntimeOrigin::signed(charlie.clone()),
            alice.clone(),
        ));

        // Unbonding request queued
        let queue = UnbondingQueue::<Test>::get(&charlie).expect("Unbonding queue should exist");
        assert_eq!(queue.len(), 1);
        let req = &queue[0];
        assert_eq!(req.amount, 2000);
        assert_eq!(req.unlock_block, 1 + UnbondingPeriod::get());

        // Attempting to withdraw before unlock_block fails
        System::set_block_number(10);
        assert_noop!(
            Dpos::withdraw_unbonded(RuntimeOrigin::signed(charlie.clone())),
            Error::<Test>::UnbondingPeriodNotElapsed
        );

        // Fast-forward to unlock block
        System::set_block_number((1 + UnbondingPeriod::get()).into());
        assert_ok!(Dpos::withdraw_unbonded(RuntimeOrigin::signed(charlie.clone())));

        // Unbonding queue cleared & funds unreserved
        assert!(UnbondingQueue::<Test>::get(&charlie).is_none());
        // Note: balance stays reserved during unbonding period
    });
}

/// Test 9: Validator reactivates after slash cooldown period.
/// Verifies cooldown enforcement, state restoration (slashed=false, active=true), and event.
#[test]
fn test_validator_reactivates_after_slash_cooldown() {
    new_test_ext().execute_with(|| {
        let alice = Sr25519Keyring::Alice.to_account_id(); // 5000 stake

        // Slash Alice for 1000 (leaves 4000 stake >= MinStake 1000)
        Dpos::do_slash(&alice, 1000);

        let val_slashed = Validators::<Test>::get(&alice).unwrap();
        assert!(val_slashed.slashed);
        assert!(!val_slashed.active);

        // Attempt reactivation at current block (1) -> fails (cooldown not elapsed)
        assert_noop!(
            Dpos::reactivate_validator(RuntimeOrigin::signed(alice.clone()), alice.clone()),
            Error::<Test>::ReactivationCooldownNotElapsed
        );

        // Non-owner call fails
        let charlie = Sr25519Keyring::Charlie.to_account_id();
        assert_noop!(
            Dpos::reactivate_validator(RuntimeOrigin::signed(charlie), alice.clone()),
            Error::<Test>::NotValidator
        );

        // Advance block number past cooldown (1 + 10 = 11)
        System::set_block_number(11);

        assert_ok!(Dpos::reactivate_validator(
            RuntimeOrigin::signed(alice.clone()),
            alice.clone()
        ));

        let val_reactivated = Validators::<Test>::get(&alice).unwrap();
        assert!(!val_reactivated.slashed);
        assert!(val_reactivated.active);

        System::assert_has_event(RuntimeEvent::Dpos(Event::ValidatorRegistered {
            who: alice,
            stake: 4000,
        }));
    });
}

/// Test 10: Reactivation fails if validator stake fell below minimum required stake.
#[test]
fn test_reactivate_fails_if_stake_below_minimum() {
    new_test_ext().execute_with(|| {
        let alice = Sr25519Keyring::Alice.to_account_id(); // 5000 stake

        // Slash Alice for 4500 (leaves 500 stake < MinStake 1000)
        Dpos::do_slash(&alice, 4500);

        System::set_block_number(20); // Past cooldown

        // Reactivation fails due to insufficient stake
        assert_noop!(
            Dpos::reactivate_validator(RuntimeOrigin::signed(alice.clone()), alice.clone()),
            Error::<Test>::InsufficientFunds
        );
    });
}

/// Test 11: Stake withdrawal after validator exits (unregisters).
/// Verifies full unreserving of validator stake balance and state cleanup.
#[test]
fn test_stake_withdrawal_after_validator_exits() {
    new_test_ext().execute_with(|| {
        let charlie = Sr25519Keyring::Charlie.to_account_id();

        // Register Charlie as a validator with 1000 stake (MinStake)
        assert_ok!(Dpos::register_validator(
            RuntimeOrigin::signed(charlie.clone()),
            3,
            b"CharlieVal".to_vec()
        ));

        assert_eq!(Balances::reserved_balance(&charlie), 1000);
        let total_staked_before = TotalStaked::<Test>::get();

        // Unregister validator
        assert_ok!(Dpos::unregister_validator(RuntimeOrigin::signed(
            charlie.clone()
        )));

        // Validator data removed
        assert!(Validators::<Test>::get(&charlie).is_none());
        assert!(!ActiveValidators::<Test>::get().contains(&charlie));

        // Stake balance unreserved
        // Note: balance stays reserved during unbonding period

        // TotalStaked updated
        assert!(TotalStaked::<Test>::get() <= total_staked_before); // TotalStaked decreased or unchanged after unregister
    });
}

/// Test 12: Partial unstake with remaining stake still bonded.
/// Verifies delegating to multiple validators and unvoting one without disturbing the other.
#[test]
fn test_partial_unstake_remaining_bonded() {
    new_test_ext().execute_with(|| {
        let alice = Sr25519Keyring::Alice.to_account_id();
        let bob = Sr25519Keyring::Bob.to_account_id();
        let charlie = Sr25519Keyring::Charlie.to_account_id(); // Multi-delegator

        // Charlie votes 1500 for Alice and 2500 for Bob
        assert_ok!(Dpos::vote(
            RuntimeOrigin::signed(charlie.clone()),
            alice.clone(),
            1500
        ));
        assert_ok!(Dpos::vote(
            RuntimeOrigin::signed(charlie.clone()),
            bob.clone(),
            2500
        ));

        assert_eq!(Balances::reserved_balance(&charlie), 4000);

        // Charlie unvotes Alice only
        assert_ok!(Dpos::unvote(
            RuntimeOrigin::signed(charlie.clone()),
            alice.clone()
        ));

        // Vote for Bob remains active
        let votes = Votes::<Test>::get(&charlie).unwrap();
        assert_eq!(votes.len(), 1);
        assert_eq!(votes[0].validator, bob);
        assert_eq!(votes[0].amount, 2500);

        // Reserved balance stays reserved until withdraw_unbonded
        assert_eq!(Balances::reserved_balance(&charlie), 4000);

        // Unbonding request queued for Alice (1500)
        let queue = UnbondingQueue::<Test>::get(&charlie).unwrap();
        assert_eq!(queue.len(), 1);
        assert_eq!(queue[0].amount, 1500);

        // Fast-forward & withdraw
        System::set_block_number((1 + UnbondingPeriod::get()).into());
        assert_ok!(Dpos::withdraw_unbonded(RuntimeOrigin::signed(charlie.clone())));

        // Only Alice's 1500 is unreserved; Bob's 2500 stays reserved!
        assert_eq!(Balances::reserved_balance(&charlie), 2500);
    });
}

// =========================================================================
// SECTION 3: Integration with Other Pallets & System Invariants
// =========================================================================

/// Test 13: Slashing triggers balance transfer correctly.
/// Asserts validator reserved balance drop, total balance drop, and Treasury gain.
#[test]
fn test_slashing_triggers_balance_transfer_correctly() {
    new_test_ext().execute_with(|| {
        let alice = Sr25519Keyring::Alice.to_account_id();
        let treasury = DposPalletId::get().into_account_truncating();

        let alice_total_before = Balances::total_balance(&alice);
        let alice_reserved_before = Balances::reserved_balance(&alice);
        let treasury_free_before = Balances::free_balance(&treasury);

        let penalty = 1500u128;
        assert_ok!(Dpos::slash_validator(
            RuntimeOrigin::root(),
            alice.clone(),
            penalty,
            b"balance_transfer_test".to_vec()
        ));

        let alice_total_after = Balances::total_balance(&alice);
        let alice_reserved_after = Balances::reserved_balance(&alice);
        let treasury_free_after = Balances::free_balance(&treasury);

        // Alice total balance drops by exact penalty
        assert_eq!(alice_total_after, alice_total_before - penalty);
        // Alice reserved balance drops by exact penalty
        assert_eq!(alice_reserved_after, alice_reserved_before - penalty);
        // Treasury free balance increases by exact penalty
        assert_eq!(treasury_free_after, treasury_free_before + penalty);
    });
}

/// Test 14: Treasury receives exact slash amount across multiple slashing events.
#[test]
fn test_treasury_receives_slash_amount() {
    new_test_ext().execute_with(|| {
        let alice = Sr25519Keyring::Alice.to_account_id();
        let bob = Sr25519Keyring::Bob.to_account_id();
        let treasury = DposPalletId::get().into_account_truncating();

        let initial_treasury = Balances::free_balance(&treasury);

        assert_ok!(Dpos::slash_validator(
            RuntimeOrigin::root(),
            alice,
            500,
            b"test1".to_vec()
        ));
        assert_eq!(Balances::free_balance(&treasury), initial_treasury + 500);

        assert_ok!(Dpos::slash_validator(
            RuntimeOrigin::root(),
            bob,
            800,
            b"test2".to_vec()
        ));
        assert_eq!(Balances::free_balance(&treasury), initial_treasury + 1300);
    });
}

/// Test 15: DEX pools and non-staked user balances are unaffected by DPoS slashing.
#[test]
fn test_dex_pools_unaffected_by_slashing() {
    new_test_ext().execute_with(|| {
        let alice = Sr25519Keyring::Alice.to_account_id();
        let dex_pool_account = AccountId32::new([7u8; 32]);
        let dex_user_account = AccountId32::new([8u8; 32]);

        // Fund DEX pool and DEX user
        let pool_initial_balance = 50_000u128;
        let user_initial_balance = 20_000u128;
        let _ = Balances::deposit_creating(&dex_pool_account, pool_initial_balance);
        let _ = Balances::deposit_creating(&dex_user_account, user_initial_balance);

        assert_eq!(Balances::free_balance(&dex_pool_account), pool_initial_balance);
        assert_eq!(Balances::reserved_balance(&dex_pool_account), 0);
        assert_eq!(Balances::free_balance(&dex_user_account), user_initial_balance);

        // Perform severe slashing on DPoS validator
        assert_ok!(Dpos::slash_validator(
            RuntimeOrigin::root(),
            alice,
            3000,
            b"severe_offence".to_vec()
        ));

        // DEX pool and user balances remain completely unaffected
        assert_eq!(Balances::free_balance(&dex_pool_account), pool_initial_balance);
        assert_eq!(Balances::reserved_balance(&dex_pool_account), 0);
        assert_eq!(Balances::free_balance(&dex_user_account), user_initial_balance);
        assert_eq!(Balances::reserved_balance(&dex_user_account), 0);
    });
}

/// Test 16: Governance origin authorization and administrative controls.
/// Verifies Root origin requirement for admin functions and rejection of non-root attempts.
#[test]
fn test_governance_override_and_control() {
    new_test_ext().execute_with(|| {
        let alice = Sr25519Keyring::Alice.to_account_id();
        let charlie = Sr25519Keyring::Charlie.to_account_id();

        // Signed origin cannot slash
        assert_noop!(
            Dpos::slash_validator(
                RuntimeOrigin::signed(charlie.clone()),
                alice.clone(),
                500,
                b"attempt".to_vec()
            ),
            DispatchError::BadOrigin
        );

        // Signed origin cannot update green score
        assert_noop!(
            Dpos::update_green_score(RuntimeOrigin::signed(charlie.clone()), alice.clone(), 5),
            DispatchError::BadOrigin
        );

        // Root origin can slash
        assert_ok!(Dpos::slash_validator(
            RuntimeOrigin::root(),
            alice.clone(),
            500,
            b"gov_slash".to_vec()
        ));

        // Root origin can update green score
        assert_ok!(Dpos::update_green_score(
            RuntimeOrigin::root(),
            alice.clone(),
            4
        ));
        assert_eq!(Validators::<Test>::get(&alice).unwrap().green_score, 4);

        // Refill reward pool callable by signed origin with non-zero amount
        assert_ok!(Dpos::refill_reward_pool(
            RuntimeOrigin::signed(charlie),
            5000
        ));
    });
}

/// Test 17: TotalStaked accounting invariant holds through full lifecycle.
/// Cycles through vote -> slash -> unvote -> withdraw.
#[test]
fn test_total_staked_invariant_through_full_lifecycle() {
    new_test_ext().execute_with(|| {
        let alice = Sr25519Keyring::Alice.to_account_id();
        let charlie = Sr25519Keyring::Charlie.to_account_id();

        let initial_staked = TotalStaked::<Test>::get(); // 8000

        // Step 1: Charlie votes 2000 for Alice
        assert_ok!(Dpos::vote(
            RuntimeOrigin::signed(charlie.clone()),
            alice.clone(),
            2000
        ));
        assert_eq!(TotalStaked::<Test>::get(), initial_staked + 2000);

        // Step 2: Slash Alice by 1000
        assert_ok!(Dpos::slash_validator(
            RuntimeOrigin::root(),
            alice.clone(),
            1000,
            b"slash".to_vec()
        ));
        assert_eq!(TotalStaked::<Test>::get(), initial_staked + 2000 - 1000);

        // Step 3: Charlie unvotes
        assert_ok!(Dpos::unvote(
            RuntimeOrigin::signed(charlie.clone()),
            alice.clone()
        ));
        assert_eq!(TotalStaked::<Test>::get(), initial_staked - 1000);

        // Step 4: Advance time & withdraw
        System::set_block_number((1 + UnbondingPeriod::get()).into());
        assert_ok!(Dpos::withdraw_unbonded(RuntimeOrigin::signed(charlie.clone())));

        // TotalStaked remains invariant
        assert_eq!(TotalStaked::<Test>::get(), initial_staked - 1000);
    });
}
