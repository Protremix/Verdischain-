// === P1 DEX SECURITY TESTS ===
// Appended to pallets/amm-dex/src/tests.rs

/// Test: K-invariant holds after swap (constant product)
/// k = reserve_a * reserve_b must be maintained (modulo fees)
#[test]
fn test_k_invariant_after_swap() {
    new_test_ext().execute_with(|| {
        assert_ok!(AmmDex::create_pool(
            RuntimeOrigin::signed(alice()),
            b"VRS".to_vec(),
            b"ECO".to_vec(),
            100_000,
            100_000,
        ));

        let pool = Pools::<Test>::get(0).unwrap();
        let k_before = pool.reserve_a * pool.reserve_b;

        assert_ok!(AmmDex::swap(
            RuntimeOrigin::signed(bob()),
            0,
            b"VRS".to_vec(),
            10_000,
            0,
        ));

        let pool = Pools::<Test>::get(0).unwrap();
        let k_after = pool.reserve_a * pool.reserve_b;

        // K should increase (fees add to reserves), never decrease
        assert!(
            k_after >= k_before,
            "K-invariant violated: k_after ({}) < k_before ({})",
            k_after,
            k_before
        );
    });
}

/// Test: K-invariant holds after multiple swaps (flash loan resistance)
#[test]
fn test_k_invariant_after_multiple_swaps() {
    new_test_ext().execute_with(|| {
        assert_ok!(AmmDex::create_pool(
            RuntimeOrigin::signed(alice()),
            b"VRS".to_vec(),
            b"ECO".to_vec(),
            1_000_000,
            1_000_000,
        ));

        // Alternate swaps back and forth
        for i in 0..10 {
            let token_in = if i % 2 == 0 { b"VRS".to_vec() } else { b"ECO".to_vec() };
            assert_ok!(AmmDex::swap(
                RuntimeOrigin::signed(bob()),
                0,
                token_in,
                10_000,
                0,
            ));
        }

        let pool = Pools::<Test>::get(0).unwrap();
        let k = pool.reserve_a * pool.reserve_b;
        // K must be >= initial (1M * 1M = 1T)
        assert!(
            k >= 1_000_000_000_000u128,
            "K-invariant violated after multiple swaps: {}",
            k
        );
    });
}

/// Test: Swap with zero amount is rejected
#[test]
fn test_swap_zero_amount_rejected() {
    new_test_ext().execute_with(|| {
        assert_ok!(AmmDex::create_pool(
            RuntimeOrigin::signed(alice()),
            b"VRS".to_vec(),
            b"ECO".to_vec(),
            100_000,
            100_000,
        ));

        assert_noop!(
            AmmDex::swap(
                RuntimeOrigin::signed(bob()),
                0,
                b"VRS".to_vec(),
                0,
                0,
            ),
            Error::<Test>::ZeroAmount
        );
    });
}

/// Test: Slippage protection — min_amount_out enforced
#[test]
fn test_slippage_protection_enforced() {
    new_test_ext().execute_with(|| {
        assert_ok!(AmmDex::create_pool(
            RuntimeOrigin::signed(alice()),
            b"VRS".to_vec(),
            b"ECO".to_vec(),
            100_000,
            100_000,
        ));

        // Swap 10,000 VRS for ECO with min_amount_out of 999,999 (unrealistic)
        // Should fail because actual output will be much less
        assert_noop!(
            AmmDex::swap(
                RuntimeOrigin::signed(bob()),
                0,
                b"VRS".to_vec(),
                10_000,
                99_999,
            ),
            Error::<Test>::SlippageExceeded
        );
    });
}

/// Test: Price impact circuit breaker — large swap rejected
#[test]
fn test_price_impact_circuit_breaker() {
    new_test_ext().execute_with(|| {
        assert_ok!(AmmDex::create_pool(
            RuntimeOrigin::signed(alice()),
            b"VRS".to_vec(),
            b"ECO".to_vec(),
            100_000,
            100_000,
        ));

        // MaxPriceImpact is 10%, so max swap = 100,000 * 10% = 10,000
        // Try to swap 50,000 (50% of pool) — should be rejected
        assert_noop!(
            AmmDex::swap(
                RuntimeOrigin::signed(bob()),
                0,
                b"VRS".to_vec(),
                50_000,
                0,
            ),
            Error::<Test>::PriceImpactTooHigh
        );
    });
}

/// Test: Remove liquidity with insufficient LP balance
#[test]
fn test_remove_liquidity_insufficient_lp() {
    new_test_ext().execute_with(|| {
        assert_ok!(AmmDex::create_pool(
            RuntimeOrigin::signed(alice()),
            b"VRS".to_vec(),
            b"ECO".to_vec(),
            100_000,
            100_000,
        ));

        // Bob has no LP tokens, tries to remove liquidity
        assert_noop!(
            AmmDex::remove_liquidity(
                RuntimeOrigin::signed(bob()),
                0,
                10_000,
            ),
            Error::<Test>::InsufficientLpBalance
        );
    });
}

/// Test: Add liquidity with zero amount is rejected
#[test]
fn test_add_liquidity_zero_amount_rejected() {
    new_test_ext().execute_with(|| {
        assert_ok!(AmmDex::create_pool(
            RuntimeOrigin::signed(alice()),
            b"VRS".to_vec(),
            b"ECO".to_vec(),
            100_000,
            100_000,
        ));

        assert_noop!(
            AmmDex::add_liquidity(
                RuntimeOrigin::signed(bob()),
                0,
                0,
                10_000,
            ),
            Error::<Test>::ZeroAmount
        );
    });
}

/// Test: Create pool with same token fails
#[test]
fn test_create_pool_same_token_rejected() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            AmmDex::create_pool(
                RuntimeOrigin::signed(alice()),
                b"VRS".to_vec(),
                b"VRS".to_vec(),
                100_000,
                100_000,
            ),
            Error::<Test>::SameToken
        );
    });
}

/// Test: Create pool with zero amount fails
#[test]
fn test_create_pool_zero_amount_rejected() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            AmmDex::create_pool(
                RuntimeOrigin::signed(alice()),
                b"VRS".to_vec(),
                b"ECO".to_vec(),
                0,
                100_000,
            ),
            Error::<Test>::ZeroAmount
        );
    });
}

/// Test: Duplicate pool creation fails
#[test]
fn test_duplicate_pool_rejected() {
    new_test_ext().execute_with(|| {
        assert_ok!(AmmDex::create_pool(
            RuntimeOrigin::signed(alice()),
            b"VRS".to_vec(),
            b"ECO".to_vec(),
            100_000,
            100_000,
        ));

        // Try to create the same pool again
        assert_noop!(
            AmmDex::create_pool(
                RuntimeOrigin::signed(bob()),
                b"VRS".to_vec(),
                b"ECO".to_vec(),
                100_000,
                100_000,
            ),
            Error::<Test>::PoolAlreadyExists
        );
    });
}

/// Test: Swap on non-existent pool fails
#[test]
fn test_swap_nonexistent_pool() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            AmmDex::swap(
                RuntimeOrigin::signed(alice()),
                999,
                b"VRS".to_vec(),
                10_000,
                0,
            ),
            Error::<Test>::PoolNotFound
        );
    });
}

/// Test: Swap with invalid token (not in pool) fails
#[test]
fn test_swap_invalid_token_rejected() {
    new_test_ext().execute_with(|| {
        assert_ok!(AmmDex::create_pool(
            RuntimeOrigin::signed(alice()),
            b"VRS".to_vec(),
            b"ECO".to_vec(),
            100_000,
            100_000,
        ));

        assert_noop!(
            AmmDex::swap(
                RuntimeOrigin::signed(bob()),
                0,
                b"UNKNOWN".to_vec(),
                10_000,
                0,
            ),
            Error::<Test>::PoolNotFound
        );
    });
}

/// Test: Max pools limit enforced
#[test]
fn test_max_pools_limit_enforced() {
    new_test_ext().execute_with(|| {
        // MaxPools = 50, create 50 pools
        for i in 0..50 {
            let token_a = format!("T{}", i * 2);
            let token_b = format!("T{}", i * 2 + 1);
            assert_ok!(AmmDex::create_pool(
                RuntimeOrigin::signed(alice()),
                token_a.as_bytes().to_vec(),
                token_b.as_bytes().to_vec(),
                100_000,
                100_000,
            ));
        }

        // Try to create the 51st pool — should fail
        assert_noop!(
            AmmDex::create_pool(
                RuntimeOrigin::signed(alice()),
                b"TOO".to_vec(),
                b"MANY".to_vec(),
                100_000,
                100_000,
            ),
            Error::<Test>::MaxPoolsReached
        );
    });
}

/// Test: Token name too long is rejected
#[test]
fn test_token_name_too_long_rejected() {
    new_test_ext().execute_with(|| {
        let long_token = vec![b'X'; 33]; // Max is 32 bytes

        assert_noop!(
            AmmDex::create_pool(
                RuntimeOrigin::signed(alice()),
                long_token,
                b"ECO".to_vec(),
                100_000,
                100_000,
            ),
            Error::<Test>::TokenTooLong
        );
    });
}
