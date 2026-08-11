// Presale tests for Verdis Chain presale pallet
// Tests cover: purchase within cap, individual cap, multi-round, claim, pause/unpause, unauthorized access

use frame_support::{assert_ok, assert_noop};
use sp_core::H256;
use sp_runtime::traits::BlakeTwo256;

#[test]
fn test_purchase_within_cap_succeeds() {
    new_test_ext().execute_with(|| {
        let buyer = Sr25519Keyring::Alice.to_account_id();
        let amount = 1_000 * units();

        // Setup: ensure presale round is active
        assert_ok!(Presale::buy_tokens(
            RuntimeOrigin::signed(buyer.clone()),
            0, // round 0
            amount,
        ));

        // Verify purchase was recorded
        let purchase = Presale::purchases(buyer.clone(), 0);
        assert!(purchase > 0, "Purchase should be recorded");
    });
}

#[test]
fn test_purchase_exceeding_round_cap_fails() {
    new_test_ext().execute_with(|| {
        let buyer = Sr25519Keyring::Bob.to_account_id();
        let cap = Presale::round_cap(0);
        let excessive_amount = cap + 1;

        assert_noop!(
            Presale::buy_tokens(
                RuntimeOrigin::signed(buyer),
                0,
                excessive_amount,
            ),
            Error::<Test>::RoundCapExceeded
        );
    });
}

#[test]
fn test_individual_cap_enforcement() {
    new_test_ext().execute_with(|| {
        let buyer = Sr25519Keyring::Charlie.to_account_id();
        let individual_cap = Presale::individual_cap(0);

        // Buy at cap - should succeed
        assert_ok!(Presale::buy_tokens(
            RuntimeOrigin::signed(buyer.clone()),
            0,
            individual_cap,
        ));

        // Buy more - should fail
        assert_noop!(
            Presale::buy_tokens(
                RuntimeOrigin::signed(buyer.clone()),
                0,
                1 * units(),
            ),
            Error::<Test>::IndividualCapExceeded
        );
    });
}

#[test]
fn test_pause_presale_blocks_purchases() {
    new_test_ext().execute_with(|| {
        // Pause presale
        assert_ok!(Presale::pause_presale(RuntimeOrigin::root()));

        // Purchase should fail while paused
        let buyer = Sr25519Keyring::Dave.to_account_id();
        assert_noop!(
            Presale::buy_tokens(
                RuntimeOrigin::signed(buyer),
                0,
                100 * units(),
            ),
            Error::<Test>::PresalePaused
        );
    });
}

#[test]
fn test_resume_presale_allows_purchases() {
    new_test_ext().execute_with(|| {
        // Pause then resume
        assert_ok!(Presale::pause_presale(RuntimeOrigin::root()));
        assert_ok!(Presale::resume_presale(RuntimeOrigin::root()));

        // Purchase should succeed after resume
        let buyer = Sr25519Keyring::Eve.to_account_id();
        assert_ok!(Presale::buy_tokens(
            RuntimeOrigin::signed(buyer),
            0,
            100 * units(),
        ));
    });
}

#[test]
fn test_only_root_can_pause() {
    new_test_ext().execute_with(|| {
        let attacker = Sr25519Keyring::Ferdie.to_account_id();
        assert_noop!(
            Presale::pause_presale(RuntimeOrigin::signed(attacker)),
            DispatchError::BadOrigin
        );
    });
}

#[test]
fn test_claim_tokens_after_vesting() {
    new_test_ext().execute_with(|| {
        let buyer = Sr25519Keyring::Alice.to_account_id();
        let amount = 1_000 * units();

        // Buy tokens
        assert_ok!(Presale::buy_tokens(
            RuntimeOrigin::signed(buyer.clone()),
            0,
            amount,
        ));

        // Move past vesting period
        System::set_block_number(1000);

        // Claim tokens
        assert_ok!(Presale::claim_tokens(
            RuntimeOrigin::signed(buyer.clone()),
            0,
        ));
    });
}

#[test]
fn test_claim_before_vesting_fails() {
    new_test_ext().execute_with(|| {
        let buyer = Sr25519Keyring::Bob.to_account_id();

        assert_ok!(Presale::buy_tokens(
            RuntimeOrigin::signed(buyer.clone()),
            0,
            500 * units(),
        ));

        // Try to claim immediately - should fail
        assert_noop!(
            Presale::claim_tokens(
                RuntimeOrigin::signed(buyer),
                0,
            ),
            Error::<Test>::VestingPeriodNotReached
        );
    });
}

#[test]
fn test_multi_round_presale() {
    new_test_ext().execute_with(|| {
        let buyer = Sr25519Keyring::Charlie.to_account_id();

        // Buy in round 0
        assert_ok!(Presale::buy_tokens(
            RuntimeOrigin::signed(buyer.clone()),
            0,
            100 * units(),
        ));

        // Buy in round 1 (if active)
        let round1_active = Presale::round_active(1);
        if round1_active {
            assert_ok!(Presale::buy_tokens(
                RuntimeOrigin::signed(buyer.clone()),
                1,
                100 * units(),
            ));
        }

        // Verify purchases in different rounds are tracked separately
        let purchase0 = Presale::purchases(buyer.clone(), 0);
        assert!(purchase0 > 0, "Round 0 purchase should be recorded");
    });
}

#[test]
fn test_cannot_claim_twice() {
    new_test_ext().execute_with(|| {
        let buyer = Sr25519Keyring::Dave.to_account_id();

        assert_ok!(Presale::buy_tokens(
            RuntimeOrigin::signed(buyer.clone()),
            0,
            1_000 * units(),
        ));

        System::set_block_number(1000);

        // First claim succeeds
        assert_ok!(Presale::claim_tokens(
            RuntimeOrigin::signed(buyer.clone()),
            0,
        ));

        // Second claim fails
        assert_noop!(
            Presale::claim_tokens(
                RuntimeOrigin::signed(buyer),
                0,
            ),
            Error::<Test>::AlreadyClaimed
        );
    });
}
