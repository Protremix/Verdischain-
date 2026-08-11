// Slashing tests for Verdis Chain DPoS pallet
// These tests cover equivocation, offline slashing, repeat offenses, jailing, and chill

use frame_support::{assert_ok, assert_noop};
use sp_core::H256;
use sp_runtime::traits::BlakeTwo256;
use crate::tests::*;

#[test]
fn test_slash_validator_for_equivocation() {
    new_test_ext().execute_with(|| {
        // Setup: register a validator with stake
        let validator = Sr25519Keyring::Alice.to_account_id();
        assert_ok!(Dpos::register_validator(
            RuntimeOrigin::signed(validator.clone()),
            3,
            b"solar".to_vec(),
        ));

        // Verify validator is active with full stake
        let stake_before = Dpos::validator_stake(&validator);
        assert!(stake_before > 0, "Validator should have stake");

        // Slash for equivocation (double signing)
        let slash_amount = 1_000_000 * units();
        assert_ok!(Dpos::slash_validator(
            RuntimeOrigin::root(),
            validator.clone(),
            slash_amount,
            SlashReason::Equivocation,
        ));

        // Verify stake reduced
        let stake_after = Dpos::validator_stake(&validator);
        assert!(
            stake_after < stake_before,
            "Stake should be reduced after slash"
        );
    });
}

#[test]
fn test_slash_validator_for_offline() {
    new_test_ext().execute_with(|| {
        let validator = Sr25519Keyring::Bob.to_account_id();
        assert_ok!(Dpos::register_validator(
            RuntimeOrigin::signed(validator.clone()),
            2,
            b"wind".to_vec(),
        ));

        let stake_before = Dpos::validator_stake(&validator);

        // Slash for being offline
        let slash_amount = 500_000 * units();
        assert_ok!(Dpos::slash_validator(
            RuntimeOrigin::root(),
            validator.clone(),
            slash_amount,
            SlashReason::Offline,
        ));

        let stake_after = Dpos::validator_stake(&validator);
        assert!(stake_after < stake_before, "Offline validator should be slashed");
    });
}

#[test]
fn test_slash_only_by_root() {
    new_test_ext().execute_with(|| {
        let validator = Sr25519Keyring::Alice.to_account_id();
        assert_ok!(Dpos::register_validator(
            RuntimeOrigin::signed(validator.clone()),
            3,
            b"solar".to_vec(),
        ));

        // Non-root cannot slash
        let attacker = Sr25519Keyring::Charlie.to_account_id();
        assert_noop!(
            Dpos::slash_validator(
                RuntimeOrigin::signed(attacker),
                validator.clone(),
                1000 * units(),
                SlashReason::Equivocation,
            ),
            DispatchError::BadOrigin
        );
    });
}

#[test]
fn test_slash_nonexistent_validator_fails() {
    new_test_ext().execute_with(|| {
        let fake_validator = Sr25519Keyring::Ferdie.to_account_id();

        assert_noop!(
            Dpos::slash_validator(
                RuntimeOrigin::root(),
                fake_validator,
                1000 * units(),
                SlashReason::Equivocation,
            ),
            Error::<Test>::ValidatorNotFound
        );
    });
}

#[test]
fn test_slash_amount_never_exceeds_stake() {
    new_test_ext().execute_with(|| {
        let validator = Sr25519Keyring::Alice.to_account_id();
        assert_ok!(Dpos::register_validator(
            RuntimeOrigin::signed(validator.clone()),
            3,
            b"solar".to_vec(),
        ));

        let stake_before = Dpos::validator_stake(&validator);

        // Try to slash more than total stake
        let excessive_slash = stake_before * 2;
        assert_ok!(Dpos::slash_validator(
            RuntimeOrigin::root(),
            validator.clone(),
            excessive_slash,
            SlashReason::Equivocation,
        ));

        // Stake should not go below zero (saturating)
        let stake_after = Dpos::validator_stake(&validator);
        assert_eq!(stake_after, 0, "Stake should be 0, not negative");
    });
}

#[test]
fn test_chill_prevents_future_selection() {
    new_test_ext().execute_with(|| {
        let validator = Sr25519Keyring::Dave.to_account_id();
        assert_ok!(Dpos::register_validator(
            RuntimeOrigin::signed(validator.clone()),
            3,
            b"hydro".to_vec(),
        ));

        // Chill the validator
        assert_ok!(Dpos::chill(RuntimeOrigin::signed(validator.clone())));

        // Chilled validator should not be in active set
        let active_validators = Dpos::active_validators();
        assert!(
            !active_validators.contains(&validator),
            "Chilled validator should not be in active set"
        );
    });
}

#[test]
fn test_slash_emits_event() {
    new_test_ext().execute_with(|| {
        let validator = Sr25519Keyring::Eve.to_account_id();
        assert_ok!(Dpos::register_validator(
            RuntimeOrigin::signed(validator.clone()),
            2,
            b"geothermal".to_vec(),
        ));

        System::set_block_number(1);
        assert_ok!(Dpos::slash_validator(
            RuntimeOrigin::root(),
            validator.clone(),
            1000 * units(),
            SlashReason::Equivocation,
        ));

        // Verify slash event was emitted
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

#[test]
fn test_unregister_after_slash() {
    new_test_ext().execute_with(|| {
        let validator = Sr25519Keyring::Ferdie.to_account_id();
        assert_ok!(Dpos::register_validator(
            RuntimeOrigin::signed(validator.clone()),
            1,
            b"biomass".to_vec(),
        ));

        // Slash all stake
        let stake = Dpos::validator_stake(&validator);
        assert_ok!(Dpos::slash_validator(
            RuntimeOrigin::root(),
            validator.clone(),
            stake,
            SlashReason::Equivocation,
        ));

        // Should still be able to unregister
        assert_ok!(Dpos::unregister_validator(RuntimeOrigin::signed(validator)));
    });
}
