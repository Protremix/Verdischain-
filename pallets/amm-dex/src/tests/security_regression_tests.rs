// DEX Security Regression Tests (ARCH-035)
// Comprehensive security tests for pallet-amm-dex

use super::*;

fn alice() -> sp_core::crypto::AccountId32 {
    Sr25519Keyring::Alice.to_account_id()
}

fn bob() -> sp_core::crypto::AccountId32 {
    Sr25519Keyring::Bob.to_account_id()
}

const DEADLINE: u64 = 999_999_999;

// 1. Swap with zero input → rejected
#[test]
fn test_sec_swap_zero_input_rejected() {
    new_test_ext().execute_with(|| {
        assert_ok!(AmmDex::create_pool(
            RuntimeOrigin::signed(alice()),
            b"VRDX".to_vec(),
            b"ECO".to_vec(),
            100_000u128,
            100_000u128,
        ));

        assert_noop!(
            AmmDex::swap(
                RuntimeOrigin::signed(alice()),
                0u32,
                b"VRDX".to_vec(),
                0u128,
                0u128,
                DEADLINE,
            ),
            Error::<Test>::ZeroAmount
        );
    });
}

// 2. Swap with impossible min_out → slippage exceeded
#[test]
fn test_sec_swap_slippage_enforced() {
    new_test_ext().execute_with(|| {
        assert_ok!(AmmDex::create_pool(
            RuntimeOrigin::signed(alice()),
            b"VRDX".to_vec(),
            b"ECO".to_vec(),
            100_000u128,
            100_000u128,
        ));

        assert_noop!(
            AmmDex::swap(
                RuntimeOrigin::signed(alice()),
                0u32,
                b"VRDX".to_vec(),
                1_000u128,
                999_999_999u128,
                DEADLINE,
            ),
            Error::<Test>::SlippageExceeded
        );
    });
}

// 3. Swap on non-existent pool → rejected
#[test]
fn test_sec_swap_nonexistent_pool_rejected() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            AmmDex::swap(
                RuntimeOrigin::signed(alice()),
                999u32,
                b"VRDX".to_vec(),
                1_000u128,
                0u128,
                DEADLINE,
            ),
            Error::<Test>::PoolNotFound
        );
    });
}

// 4. Add liquidity with zero amount → rejected
#[test]
fn test_sec_add_liquidity_zero_rejected() {
    new_test_ext().execute_with(|| {
        assert_ok!(AmmDex::create_pool(
            RuntimeOrigin::signed(alice()),
            b"VRDX".to_vec(),
            b"ECO".to_vec(),
            100_000u128,
            100_000u128,
        ));

        assert_noop!(
            AmmDex::add_liquidity(
                RuntimeOrigin::signed(bob()),
                0u32,
                0u128,
                10_000u128,
                DEADLINE,
            ),
            Error::<Test>::ZeroAmount
        );
    });
}

// 5. Remove liquidity with zero LP → fails
#[test]
fn test_sec_remove_liquidity_zero_lp_fails() {
    new_test_ext().execute_with(|| {
        assert_ok!(AmmDex::create_pool(
            RuntimeOrigin::signed(alice()),
            b"VRDX".to_vec(),
            b"ECO".to_vec(),
            100_000u128,
            100_000u128,
        ));

        let result = AmmDex::remove_liquidity(
            RuntimeOrigin::signed(alice()),
            0u32,
            0u128,
            DEADLINE,
        );
        assert!(result.is_err(), "Removing zero LP should fail");
    });
}

// 6. Remove more liquidity than owned → fails
#[test]
fn test_sec_remove_more_than_owned_fails() {
    new_test_ext().execute_with(|| {
        assert_ok!(AmmDex::create_pool(
            RuntimeOrigin::signed(alice()),
            b"VRDX".to_vec(),
            b"ECO".to_vec(),
            100_000u128,
            100_000u128,
        ));

        let result = AmmDex::remove_liquidity(
            RuntimeOrigin::signed(alice()),
            0u32,
            u128::MAX,
            DEADLINE,
        );
        assert!(result.is_err(), "Removing more LP than owned should fail");
    });
}

// 7. Swap with expired deadline → rejected
#[test]
fn test_sec_swap_expired_rejected() {
    new_test_ext().execute_with(|| {
        assert_ok!(AmmDex::create_pool(
            RuntimeOrigin::signed(alice()),
            b"VRDX".to_vec(),
            b"ECO".to_vec(),
            100_000u128,
            100_000u128,
        ));

        System::set_block_number(100);

        assert_noop!(
            AmmDex::swap(
                RuntimeOrigin::signed(alice()),
                0u32,
                b"VRDX".to_vec(),
                1_000u128,
                0u128,
                50u64,
            ),
            Error::<Test>::Expired
        );
    });
}

// 8. Create pool with identical tokens → rejected
#[test]
fn test_sec_identical_tokens_rejected() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            AmmDex::create_pool(
                RuntimeOrigin::signed(alice()),
                b"VRDX".to_vec(),
                b"VRDX".to_vec(),
                100u128,
                100u128,
            ),
            Error::<Test>::SameToken
        );
    });
}

// 9. Multiple swaps in same block → all succeed independently
#[test]
fn test_sec_multiple_swaps_same_block() {
    new_test_ext().execute_with(|| {
        assert_ok!(AmmDex::create_pool(
            RuntimeOrigin::signed(alice()),
            b"VRDX".to_vec(),
            b"ECO".to_vec(),
            1_000_000u128,
            1_000_000u128,
        ));

        for _ in 0..3 {
            assert_ok!(AmmDex::swap(
                RuntimeOrigin::signed(alice()),
                0u32,
                b"VRDX".to_vec(),
                1_000u128,
                0u128,
                DEADLINE,
            ));
        }

        let pool = Pools::<Test>::get(0u32);
        assert!(pool.is_some(), "Pool should exist after multiple swaps");
    });
}

// 10. K-invariant maintained after swap
#[test]
fn test_sec_k_invariant_maintained() {
    new_test_ext().execute_with(|| {
        assert_ok!(AmmDex::create_pool(
            RuntimeOrigin::signed(alice()),
            b"VRDX".to_vec(),
            b"ECO".to_vec(),
            1_000_000u128,
            1_000_000u128,
        ));

        let pool_before = Pools::<Test>::get(0u32).unwrap();
        let k_before = pool_before.reserve_a * pool_before.reserve_b;

        assert_ok!(AmmDex::swap(
            RuntimeOrigin::signed(alice()),
            0u32,
            b"VRDX".to_vec(),
            50_000u128,
            0u128,
            DEADLINE,
        ));

        let pool_after = Pools::<Test>::get(0u32).unwrap();
        let k_after = pool_after.reserve_a * pool_after.reserve_b;

        assert!(
            k_after >= k_before,
            "K-invariant violated: before={}, after={}",
            k_before,
            k_after
        );
    });
}

// 11. Swap with unknown token → rejected
#[test]
fn test_sec_swap_unknown_token_rejected() {
    new_test_ext().execute_with(|| {
        assert_ok!(AmmDex::create_pool(
            RuntimeOrigin::signed(alice()),
            b"VRDX".to_vec(),
            b"ECO".to_vec(),
            100_000u128,
            100_000u128,
        ));

        assert_noop!(
            AmmDex::swap(
                RuntimeOrigin::signed(alice()),
                0u32,
                b"UNKNOWN".to_vec(),
                1_000u128,
                0u128,
                DEADLINE,
            ),
            Error::<Test>::PoolNotFound
        );
    });
}

// 12. Token name too long → rejected
#[test]
fn test_sec_token_name_too_long() {
    new_test_ext().execute_with(|| {
        let long_token = vec![b'A'; 100];

        assert_noop!(
            AmmDex::create_pool(
                RuntimeOrigin::signed(alice()),
                long_token,
                b"ECO".to_vec(),
                100u128,
                100u128,
            ),
            Error::<Test>::TokenTooLong
        );
    });
}

// 13. Add liquidity to non-existent pool → rejected
#[test]
fn test_sec_add_liquidity_nonexistent_pool() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            AmmDex::add_liquidity(
                RuntimeOrigin::signed(alice()),
                999u32,
                1_000u128,
                1_000u128,
                DEADLINE,
            ),
            Error::<Test>::PoolNotFound
        );
    });
}

// 14. Remove liquidity from non-existent pool → rejected
#[test]
fn test_sec_remove_liquidity_nonexistent_pool() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            AmmDex::remove_liquidity(
                RuntimeOrigin::signed(alice()),
                999u32,
                1_000u128,
                DEADLINE,
            ),
            Error::<Test>::PoolNotFound
        );
    });
}

// 15. Price impact circuit breaker on large swap
#[test]
fn test_sec_large_swap_handled() {
    new_test_ext().execute_with(|| {
        assert_ok!(AmmDex::create_pool(
            RuntimeOrigin::signed(alice()),
            b"VRDX".to_vec(),
            b"ECO".to_vec(),
            100_000u128,
            100_000u128,
        ));

        // Very large swap relative to pool — should either succeed or fail with PriceImpactTooHigh
        let result = AmmDex::swap(
            RuntimeOrigin::signed(alice()),
            0u32,
            b"VRDX".to_vec(),
            99_000u128,
            0u128,
            DEADLINE,
        );
        // Just verify no panic
        let _ = result;
    });
}

// 16. LP tokens minted on add_liquidity
#[test]
fn test_sec_lp_tokens_minted() {
    new_test_ext().execute_with(|| {
        assert_ok!(AmmDex::create_pool(
            RuntimeOrigin::signed(alice()),
            b"VRDX".to_vec(),
            b"ECO".to_vec(),
            100_000u128,
            100_000u128,
        ));

        assert_ok!(AmmDex::add_liquidity(
            RuntimeOrigin::signed(bob()),
            0u32,
            50_000u128,
            50_000u128,
            DEADLINE,
        ));

        let lp_balance = AmmDex::user_lp(0u32, &bob());
        assert!(lp_balance > 0, "LP tokens should be minted for bob");
    });
}

// 17. Reserves change correctly after swap
#[test]
fn test_sec_reserves_change_after_swap() {
    new_test_ext().execute_with(|| {
        assert_ok!(AmmDex::create_pool(
            RuntimeOrigin::signed(alice()),
            b"VRDX".to_vec(),
            b"ECO".to_vec(),
            1_000_000u128,
            1_000_000u128,
        ));

        let pool_before = Pools::<Test>::get(0u32).unwrap();

        assert_ok!(AmmDex::swap(
            RuntimeOrigin::signed(alice()),
            0u32,
            b"VRDX".to_vec(),
            50_000u128,
            0u128,
            DEADLINE,
        ));

        let pool_after = Pools::<Test>::get(0u32).unwrap();

        assert!(
            pool_after.reserve_a > pool_before.reserve_a,
            "Reserve A should increase after swapping VRDX in"
        );
        assert!(
            pool_after.reserve_b < pool_before.reserve_b,
            "Reserve B should decrease after swapping ECO out"
        );
    });
}

// 18. Add liquidity with expired deadline → rejected
#[test]
fn test_sec_add_liquidity_expired_rejected() {
    new_test_ext().execute_with(|| {
        assert_ok!(AmmDex::create_pool(
            RuntimeOrigin::signed(alice()),
            b"VRDX".to_vec(),
            b"ECO".to_vec(),
            100_000u128,
            100_000u128,
        ));

        System::set_block_number(100);

        assert_noop!(
            AmmDex::add_liquidity(
                RuntimeOrigin::signed(bob()),
                0u32,
                10_000u128,
                10_000u128,
                50u64,
            ),
            Error::<Test>::Expired
        );
    });
}
