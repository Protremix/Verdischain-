// Comprehensive slashing tests for Verdis Chain DPoS pallet
// Covers: equivocation, offline, authority, saturating, events, reactivation, edge cases

use super::*;
use frame_support::{assert_ok, assert_noop};

// === Basic slashing ===

#[test]
fn test_slash_validator_for_equivocation() {
    new_test_ext().execute_with(|| {
        let validator = Sr25519Keyring::Alice.to_account_id();
        let stake_before = Validators::<Test>::get(&validator).unwrap().stake;
        assert!(stake_before > 0, "Validator should have stake");

        let penalty = 500u128;
        assert_ok!(Dpos::slash_validator(
            RuntimeOrigin::root(),
            validator.clone(),
            penalty,
            b"equivocation".to_vec(),
        ));

        let stake_after = Validators::<Test>::get(&validator).unwrap().stake;
        assert!(stake_after < stake_before, "Stake should be reduced after slash");
        assert_eq!(stake_after, stake_before - penalty, "Exact slash amount");
    });
}

#[test]
fn test_slash_validator_for_offline() {
    new_test_ext().execute_with(|| {
        let validator = Sr25519Keyring::Bob.to_account_id();
        let stake_before = Validators::<Test>::get(&validator).unwrap().stake;

        let penalty = 300u128;
        assert_ok!(Dpos::slash_validator(
            RuntimeOrigin::root(),
            validator.clone(),
            penalty,
            b"offline".to_vec(),
        ));

        let stake_after = Validators::<Test>::get(&validator).unwrap().stake;
        assert!(stake_after < stake_before, "Offline validator should be slashed");
    });
}

// === Authority checks ===

#[test]
fn test_slash_only_by_root() {
    new_test_ext().execute_with(|| {
        let validator = Sr25519Keyring::Alice.to_account_id();
        let attacker = Sr25519Keyring::Charlie.to_account_id();

        assert_noop!(
            Dpos::slash_validator(
                RuntimeOrigin::signed(attacker),
                validator,
                100u128,
                b"equivocation".to_vec(),
            ),
            DispatchError::BadOrigin
        );
    });
}

#[test]
fn test_slash_nonexistent_validator_fails() {
    new_test_ext().execute_with(|| {
        let fake_validator = Sr25519Keyring::Dave.to_account_id();

        assert_noop!(
            Dpos::slash_validator(
                RuntimeOrigin::root(),
                fake_validator,
                100u128,
                b"equivocation".to_vec(),
            ),
            Error::<Test>::ValidatorNotFound
        );
    });
}

// === Edge cases ===

#[test]
fn test_slash_amount_never_exceeds_stake() {
    new_test_ext().execute_with(|| {
        let validator = Sr25519Keyring::Alice.to_account_id();
        let stake_before = Validators::<Test>::get(&validator).unwrap().stake;

        // Try to slash more than total stake
        let excessive = stake_before * 2;
        assert_ok!(Dpos::slash_validator(
            RuntimeOrigin::root(),
            validator.clone(),
            excessive,
            b"equivocation".to_vec(),
        ));

        let stake_after = Validators::<Test>::get(&validator).unwrap().stake;
        assert_eq!(stake_after, 0, "Stake should be 0, not negative (saturating)");
    });
}

#[test]
fn test_slash_zero_penalty_fails() {
    new_test_ext().execute_with(|| {
        let validator = Sr25519Keyring::Alice.to_account_id();

        assert_noop!(
            Dpos::slash_validator(
                RuntimeOrigin::root(),
                validator,
                0u128,
                b"equivocation".to_vec(),
            ),
            Error::<Test>::SlashingFailed
        );
    });
}

#[test]
fn test_slash_empty_reason_fails() {
    new_test_ext().execute_with(|| {
        let validator = Sr25519Keyring::Alice.to_account_id();

        assert_noop!(
            Dpos::slash_validator(
                RuntimeOrigin::root(),
                validator,
                100u128,
                b"".to_vec(),
            ),
            Error::<Test>::InvalidSlashReason
        );
    });
}

// === State changes ===

#[test]
fn test_slash_sets_validator_inactive_and_slashed() {
    new_test_ext().execute_with(|| {
        let validator = Sr25519Keyring::Alice.to_account_id();

        assert_ok!(Dpos::slash_validator(
            RuntimeOrigin::root(),
            validator.clone(),
            100u128,
            b"equivocation".to_vec(),
        ));

        let val = Validators::<Test>::get(&validator).unwrap();
        assert!(!val.active, "Slashed validator should be inactive");
        assert!(val.slashed, "Slashed flag should be set");
    });
}

#[test]
fn test_slash_removes_from_active_set() {
    new_test_ext().execute_with(|| {
        let validator = Sr25519Keyring::Alice.to_account_id();

        // Alice should be in active set before slashing
        let active = ActiveValidators::<Test>::get();
        assert!(active.contains(&validator), "Alice should be active before slash");

        assert_ok!(Dpos::slash_validator(
            RuntimeOrigin::root(),
            validator.clone(),
            100u128,
            b"equivocation".to_vec(),
        ));

        let active_after = ActiveValidators::<Test>::get();
        assert!(
            !active_after.contains(&validator),
            "Slashed validator should not be in active set"
        );
    });
}

#[test]
fn test_slash_increments_slashing_events_counter() {
    new_test_ext().execute_with(|| {
        let validator = Sr25519Keyring::Alice.to_account_id();

        let count_before = SlashingEvents::<Test>::get(&validator);
        assert_eq!(count_before, 0, "No prior slashing events");

        assert_ok!(Dpos::slash_validator(
            RuntimeOrigin::root(),
            validator.clone(),
            100u128,
            b"equivocation".to_vec(),
        ));

        let count_after = SlashingEvents::<Test>::get(&validator);
        assert_eq!(count_after, 1, "Slashing event counter should increment");
    });
}

#[test]
fn test_multiple_slashes_increment_counter() {
    new_test_ext().execute_with(|| {
        let validator = Sr25519Keyring::Bob.to_account_id();

        // First slash
        assert_ok!(Dpos::slash_validator(
            RuntimeOrigin::root(),
            validator.clone(),
            100u128,
            b"offline".to_vec(),
        ));

        // Second slash
        assert_ok!(Dpos::slash_validator(
            RuntimeOrigin::root(),
            validator.clone(),
            100u128,
            b"equivocation".to_vec(),
        ));

        let count = SlashingEvents::<Test>::get(&validator);
        assert_eq!(count, 2, "Two slashes should increment counter to 2");
    });
}

#[test]
fn test_slash_reduces_total_staked() {
    new_test_ext().execute_with(|| {
        let validator = Sr25519Keyring::Alice.to_account_id();
        let total_before = TotalStaked::<Test>::get();

        assert_ok!(Dpos::slash_validator(
            RuntimeOrigin::root(),
            validator,
            500u128,
            b"equivocation".to_vec(),
        ));

        let total_after = TotalStaked::<Test>::get();
        assert_eq!(
            total_after,
            total_before - 500,
            "Total staked should decrease by slash amount"
        );
    });
}

// === Events ===

#[test]
fn test_slash_emits_event() {
    new_test_ext().execute_with(|| {
        let validator = Sr25519Keyring::Eve.to_account_id();

        // Register Eve as validator first (not in genesis)
        assert_ok!(Dpos::register_validator(
            RuntimeOrigin::signed(validator.clone()),
            3,
            b"solar".to_vec(),
        ));

        System::set_block_number(1);
        assert_ok!(Dpos::slash_validator(
            RuntimeOrigin::root(),
            validator.clone(),
            100u128,
            b"equivocation".to_vec(),
        ));

        let events = System::events();
        assert!(
            events.iter().any(|e| {
                matches!(
                    e.event,
                    RuntimeEvent::Dpos(crate::Event::ValidatorSlashed { .. })
                )
            }),
            "ValidatorSlashed event should be emitted"
        );
    });
}

// === Post-slash operations ===

#[test]
fn test_unregister_after_slash() {
    new_test_ext().execute_with(|| {
        let validator = Sr25519Keyring::Alice.to_account_id();
        let stake = Validators::<Test>::get(&validator).unwrap().stake;

        // Slash all stake
        assert_ok!(Dpos::slash_validator(
            RuntimeOrigin::root(),
            validator.clone(),
            stake,
            b"equivocation".to_vec(),
        ));

        // Should still be able to unregister
        assert_ok!(Dpos::unregister_validator(
            RuntimeOrigin::signed(validator)
        ));
    });
}

#[test]
fn test_reactivate_after_slash_requires_cooldown() {
    new_test_ext().execute_with(|| {
        let validator = Sr25519Keyring::Alice.to_account_id();

        assert_ok!(Dpos::slash_validator(
            RuntimeOrigin::root(),
            validator.clone(),
            100u128,
            b"equivocation".to_vec(),
        ));

        // Try to reactivate immediately — should fail (cooldown not elapsed)
        assert_noop!(
            Dpos::reactivate_validator(
                RuntimeOrigin::signed(validator.clone()),
                validator.clone(),
            ),
            Error::<Test>::ReactivationCooldownNotElapsed
        );

        // Advance past cooldown (10 blocks)
        System::set_block_number(11);

        // Now reactivation should succeed
        assert_ok!(Dpos::reactivate_validator(
            RuntimeOrigin::signed(validator.clone()),
            validator,
        ));
    });
}

#[test]
fn test_reactivate_non_slashed_validator_fails() {
    new_test_ext().execute_with(|| {
        let validator = Sr25519Keyring::Alice.to_account_id();

        // Alice is registered but not slashed — reactivation should fail
        assert_noop!(
            Dpos::reactivate_validator(
                RuntimeOrigin::signed(validator.clone()),
                validator,
            ),
            Error::<Test>::ValidatorNotSlashed
        );
    });
}

#[test]
fn test_reactivate_by_non_owner_fails() {
    new_test_ext().execute_with(|| {
        let validator = Sr25519Keyring::Alice.to_account_id();
        let attacker = Sr25519Keyring::Charlie.to_account_id();

        assert_ok!(Dpos::slash_validator(
            RuntimeOrigin::root(),
            validator.clone(),
            100u128,
            b"equivocation".to_vec(),
        ));

        System::set_block_number(11);

        // Charlie cannot reactivate Alice's validator
        assert_noop!(
            Dpos::reactivate_validator(
                RuntimeOrigin::signed(attacker),
                validator,
            ),
            Error::<Test>::NotValidator
        );
    });
}

// === Slashing with delegations ===

#[test]
fn test_slash_does_not_affect_other_validators() {
    new_test_ext().execute_with(|| {
        let alice = Sr25519Keyring::Alice.to_account_id();
        let bob = Sr25519Keyring::Bob.to_account_id();

        let alice_stake_before = Validators::<Test>::get(&alice).unwrap().stake;
        let bob_stake_before = Validators::<Test>::get(&bob).unwrap().stake;

        // Slash Alice
        assert_ok!(Dpos::slash_validator(
            RuntimeOrigin::root(),
            alice,
            200u128,
            b"equivocation".to_vec(),
        ));

        // Bob's stake should be unchanged
        let bob_stake_after = Validators::<Test>::get(&bob).unwrap().stake;
        assert_eq!(
            bob_stake_after, bob_stake_before,
            "Bob's stake should not be affected by Alice's slash"
        );

        // Alice's stake should be reduced
        let alice_stake_after = Validators::<Test>::get(&alice).unwrap().stake;
        assert!(alice_stake_after < alice_stake_before, "Alice's stake should be reduced");
    });
}
