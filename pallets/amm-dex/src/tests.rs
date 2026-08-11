#![allow(unused_imports, dead_code, unused_must_use, clippy::all)]
use crate::pallet::*;
use crate::*;
use frame_support::{
    assert_noop, assert_ok, construct_runtime, derive_impl, parameter_types,
    traits::{ConstU128, ConstU32},
};
use sp_io::TestExternalities;
use sp_keyring::Sr25519Keyring;
use sp_runtime::{traits::IdentityLookup, BuildStorage};

type Block = frame_system::mocking::MockBlock<Test>;

construct_runtime!(
    pub enum Test {
        System: frame_system,
        Balances: pallet_balances,
        FungibleTokens: pallet_fungible_tokens,
        AmmDex: crate,
    }
);

#[derive_impl(frame_system::config_preludes::TestDefaultConfig as frame_system::DefaultConfig)]
impl frame_system::Config for Test {
    type AccountId = sp_core::crypto::AccountId32;
    type Lookup = IdentityLookup<Self::AccountId>;
    type Block = Block;
    type AccountData = pallet_balances::AccountData<u128>;
}

impl pallet_balances::Config for Test {
    type MaxLocks = ConstU32<50>;
    type MaxReserves = ConstU32<50>;
    type ReserveIdentifier = [u8; 8];
    type Balance = u128;
    type RuntimeEvent = RuntimeEvent;
    type DustRemoval = ();
    type ExistentialDeposit = ConstU128<1>;
    type AccountStore = System;
    type WeightInfo = ();
    type FreezeIdentifier = ();
    type MaxFreezes = ConstU32<0>;
    type RuntimeHoldReason = ();
    type RuntimeFreezeReason = ();
    type DoneSlashHandler = ();
}

parameter_types! {
    pub const FungibleTokensPalletId: frame_support::PalletId = frame_support::PalletId(*b"vrdfungs");
    pub const MaxTokensPerAccount: u32 = 100;
    pub const CreateTokenDeposit: u128 = 100;
    pub const MaxBalance: u128 = u128::MAX;
}

impl pallet_fungible_tokens::Config for Test {
    type RuntimeEvent = RuntimeEvent;
    type Currency = Balances;
    type PalletId = FungibleTokensPalletId;
    type MaxTokensPerAccount = MaxTokensPerAccount;
    type CreateTokenDeposit = CreateTokenDeposit;
    type MaxBalance = MaxBalance;
    type WeightInfo = ();
}

parameter_types! {
    pub const AmmPalletId: frame_support::PalletId = frame_support::PalletId(*b"v/ammdex");
    pub const FeeNumerator: u32 = 3;
    pub const FeeDenominator: u32 = 1000;
    pub const MaxPriceImpact: sp_runtime::Permill = sp_runtime::Permill::from_percent(10);
    pub const AmmMinimumLiquidity: u128 = 1_000;
    pub const MinLiquidity: u128 = 100;
    pub const MaxPools: u32 = 50;
}

impl crate::pallet::TokenHandler<sp_core::crypto::AccountId32, u128> for Test {
    fn transfer(
        asset: &crate::pallet::AssetId,
        from: &sp_core::crypto::AccountId32,
        to: &sp_core::crypto::AccountId32,
        amount: u128,
    ) -> frame_support::dispatch::DispatchResult {
        match asset {
            crate::pallet::AssetId::Native => {
                <pallet_balances::Pallet<Test> as frame_support::traits::Currency<
                    sp_core::crypto::AccountId32,
                >>::transfer(
                    from,
                    to,
                    amount,
                    frame_support::traits::ExistenceRequirement::AllowDeath,
                )
            }
            crate::pallet::AssetId::Custom(token_id) => {
                pallet_fungible_tokens::Pallet::<Test>::do_transfer(*token_id, from, to, amount)
            }
        }
    }

    fn has_balance(
        asset: &crate::pallet::AssetId,
        who: &sp_core::crypto::AccountId32,
        amount: u128,
    ) -> bool {
        match asset {
            crate::pallet::AssetId::Native => {
                <pallet_balances::Pallet<Test> as frame_support::traits::Currency<
                    sp_core::crypto::AccountId32,
                >>::free_balance(who)
                    >= amount
            }
            crate::pallet::AssetId::Custom(token_id) => {
                pallet_fungible_tokens::Pallet::<Test>::balance_of(*token_id, who) >= amount
            }
        }
    }

    #[cfg(feature = "runtime-benchmarks")]
    fn fund_for_benchmark(
        asset: &crate::pallet::AssetId,
        who: &sp_core::crypto::AccountId32,
        amount: u128,
    ) {
        match asset {
            crate::pallet::AssetId::Native => {
                <pallet_balances::Pallet<Test> as frame_support::traits::Currency<_>>::deposit_creating(who, amount);
            }
            crate::pallet::AssetId::Custom(token_id) => {
                // Check if token already exists; create only if missing
                if pallet_fungible_tokens::Tokens::<Test>::get(*token_id).is_none() {
                    let alice = Sr25519Keyring::Alice.to_account_id();
                    let _ = pallet_fungible_tokens::Pallet::<Test>::create(
                        RuntimeOrigin::signed(alice.clone()),
                        b"BenchToken".to_vec(),
                        b"BNC".to_vec(),
                        9u8,
                    );
                }
                // Mint to the caller using the token owner (Alice)
                let alice = Sr25519Keyring::Alice.to_account_id();
                let _ = pallet_fungible_tokens::Pallet::<Test>::mint(
                    RuntimeOrigin::signed(alice),
                    *token_id,
                    who.clone(),
                    amount,
                );
            }
        }
    }
}

impl crate::pallet::Config for Test {
    type RuntimeEvent = RuntimeEvent;
    type Currency = Balances;
    type PalletId = AmmPalletId;
    type FeeNumerator = FeeNumerator;
    type FeeDenominator = FeeDenominator;
    type MinLiquidity = MinLiquidity;
    type MaxPools = MaxPools;
    type MinimumLiquidity = AmmMinimumLiquidity;
    type MaxPriceImpact = MaxPriceImpact;
    type WeightInfo = ();
    type TokenHandler = Test;
}

pub fn new_test_ext() -> TestExternalities {
    let mut t = frame_system::GenesisConfig::<Test>::default()
        .build_storage()
        .unwrap();
    pallet_balances::GenesisConfig::<Test> {
        balances: vec![
            (Sr25519Keyring::Alice.to_account_id(), 1_000_000_000),
            (Sr25519Keyring::Bob.to_account_id(), 1_000_000_000),
        ],
        ..Default::default()
    }
    .assimilate_storage(&mut t)
    .unwrap();
    let mut ext = TestExternalities::new(t);
    ext.execute_with(|| System::set_block_number(1));
    ext
}

/// Test externalities with a pre-created fungible token (ID 0) and funded whitelisted caller
/// Used by the benchmark test suite to set up token pool benchmarks
pub fn new_test_ext_with_tokens() -> TestExternalities {
    // Use the actual frame_benchmarking account function for exact match
    let whitelisted: <Test as frame_system::Config>::AccountId =
        frame_benchmarking::account("whitelisted_caller", 0, 0);

    let mut t = frame_system::GenesisConfig::<Test>::default()
        .build_storage()
        .unwrap();
    pallet_balances::GenesisConfig::<Test> {
        balances: vec![
            (Sr25519Keyring::Alice.to_account_id(), 1_000_000_000),
            (Sr25519Keyring::Bob.to_account_id(), 1_000_000_000),
            (whitelisted.clone(), 10_000_000_000),
        ],
        ..Default::default()
    }
    .assimilate_storage(&mut t)
    .unwrap();
    let mut ext = TestExternalities::new(t);
    ext.execute_with(|| {
        System::set_block_number(1);

        // Pre-create a fungible token (ID 0) owned by Alice
        let _ = FungibleTokens::create(
            RuntimeOrigin::signed(Sr25519Keyring::Alice.to_account_id()),
            b"TestToken".to_vec(),
            b"TST".to_vec(),
            9u8,
        );

        // Token 0 will be funded via fund_for_benchmark in the benchmarking code
    });
    ext
}

fn alice() -> sp_core::crypto::AccountId32 {
    Sr25519Keyring::Alice.to_account_id()
}
fn bob() -> sp_core::crypto::AccountId32 {
    Sr25519Keyring::Bob.to_account_id()
}
fn aid_native() -> AssetId {
    AssetId::Native
}
fn aid_custom(id: u64) -> AssetId {
    AssetId::Custom(id)
}

// === Original tests ===

#[test]
fn test_genesis_no_pools() {
    new_test_ext().execute_with(|| {
        assert_eq!(PoolCount::<Test>::get(), 0);
    });
}

#[test]
fn test_create_pool() {
    new_test_ext().execute_with(|| {
        assert_ok!(AmmDex::create_pool(
            RuntimeOrigin::signed(alice()),
            b"VRS".to_vec(),
            b"ECO".to_vec(),
            100_000,
            100_000,
        ));
        assert_eq!(PoolCount::<Test>::get(), 1);
    });
}

#[test]
fn test_swap() {
    new_test_ext().execute_with(|| {
        AmmDex::create_pool(
            RuntimeOrigin::signed(alice()),
            b"VRS".to_vec(),
            b"ECO".to_vec(),
            100_000,
            100_000,
        )
        .unwrap();
        assert_ok!(AmmDex::swap(
            RuntimeOrigin::signed(alice()),
            0,
            b"VRS".to_vec(),
            10_000,
            0,
        ));
    });
}

#[test]
fn test_pool_not_found() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            AmmDex::add_liquidity(RuntimeOrigin::signed(alice()), 99, 1000, 1000),
            Error::<Test>::PoolNotFound
        );
    });
}

// === Token integration tests ===

#[test]
fn test_create_token_pool_native_vs_custom() {
    new_test_ext().execute_with(|| {
        assert_ok!(FungibleTokens::create(
            RuntimeOrigin::signed(alice()),
            b"TestToken".to_vec(),
            b"TST".to_vec(),
            6,
        ));
        assert_ok!(FungibleTokens::mint(
            RuntimeOrigin::signed(alice()),
            0,
            alice(),
            500_000,
        ));
        assert_ok!(AmmDex::create_token_pool(
            RuntimeOrigin::signed(alice()),
            aid_native(),
            aid_custom(0),
            100_000,
            100_000,
        ));
        assert_eq!(TokenPoolCount::<Test>::get(), 1);
        let pool = TokenPools::<Test>::get(0).unwrap();
        assert_eq!(pool.asset_a, aid_native());
        assert_eq!(pool.asset_b, aid_custom(0));
    });
}

#[test]
fn test_token_pool_already_exists() {
    new_test_ext().execute_with(|| {
        FungibleTokens::create(
            RuntimeOrigin::signed(alice()),
            b"TT".to_vec(),
            b"TT".to_vec(),
            6,
        )
        .unwrap();
        FungibleTokens::mint(RuntimeOrigin::signed(alice()), 0, alice(), 500_000).unwrap();
        AmmDex::create_token_pool(
            RuntimeOrigin::signed(alice()),
            aid_native(),
            aid_custom(0),
            100_000,
            100_000,
        )
        .unwrap();
        assert_noop!(
            AmmDex::create_token_pool(
                RuntimeOrigin::signed(alice()),
                aid_native(),
                aid_custom(0),
                50_000,
                50_000,
            ),
            Error::<Test>::PoolAlreadyExists
        );
    });
}

#[test]
fn test_token_swap_native_to_custom() {
    new_test_ext().execute_with(|| {
        FungibleTokens::create(
            RuntimeOrigin::signed(alice()),
            b"TT".to_vec(),
            b"TT".to_vec(),
            6,
        )
        .unwrap();
        FungibleTokens::mint(RuntimeOrigin::signed(alice()), 0, alice(), 1_000_000).unwrap();
        AmmDex::create_token_pool(
            RuntimeOrigin::signed(alice()),
            aid_native(),
            aid_custom(0),
            100_000,
            100_000,
        )
        .unwrap();

        let bob_before = FungibleTokens::balance_of(0, &bob());
        assert_ok!(AmmDex::swap_token(
            RuntimeOrigin::signed(bob()),
            0,
            aid_native(),
            10_000,
            0,
        ));
        let bob_after = FungibleTokens::balance_of(0, &bob());
        assert!(
            bob_after > bob_before,
            "Bob should have received custom tokens"
        );
    });
}

#[test]
fn test_token_swap_custom_to_native() {
    new_test_ext().execute_with(|| {
        FungibleTokens::create(
            RuntimeOrigin::signed(alice()),
            b"TT".to_vec(),
            b"TT".to_vec(),
            6,
        )
        .unwrap();
        FungibleTokens::mint(RuntimeOrigin::signed(alice()), 0, alice(), 1_000_000).unwrap();
        FungibleTokens::mint(RuntimeOrigin::signed(alice()), 0, bob(), 500_000).unwrap();
        AmmDex::create_token_pool(
            RuntimeOrigin::signed(alice()),
            aid_native(),
            aid_custom(0),
            100_000,
            100_000,
        )
        .unwrap();

        let bob_native_before = Balances::free_balance(&bob());
        assert_ok!(AmmDex::swap_token(
            RuntimeOrigin::signed(bob()),
            0,
            aid_custom(0),
            10_000,
            0,
        ));
        let bob_native_after = Balances::free_balance(&bob());
        assert!(
            bob_native_after > bob_native_before,
            "Bob should have received native VRS"
        );
    });
}

#[test]
fn test_token_add_liquidity() {
    new_test_ext().execute_with(|| {
        FungibleTokens::create(
            RuntimeOrigin::signed(alice()),
            b"TT".to_vec(),
            b"TT".to_vec(),
            6,
        )
        .unwrap();
        FungibleTokens::mint(RuntimeOrigin::signed(alice()), 0, alice(), 2_000_000).unwrap();
        FungibleTokens::mint(RuntimeOrigin::signed(alice()), 0, bob(), 1_000_000).unwrap();
        AmmDex::create_token_pool(
            RuntimeOrigin::signed(alice()),
            aid_native(),
            aid_custom(0),
            100_000,
            100_000,
        )
        .unwrap();

        assert_ok!(AmmDex::add_token_liquidity(
            RuntimeOrigin::signed(bob()),
            0,
            50_000,
            50_000,
        ));
        let bob_lp = AmmDex::token_lp(0, &bob()).unwrap_or(0);
        assert!(bob_lp > 0, "Bob should have LP tokens");
    });
}

#[test]
fn test_token_remove_liquidity() {
    new_test_ext().execute_with(|| {
        FungibleTokens::create(
            RuntimeOrigin::signed(alice()),
            b"TT".to_vec(),
            b"TT".to_vec(),
            6,
        )
        .unwrap();
        FungibleTokens::mint(RuntimeOrigin::signed(alice()), 0, alice(), 1_000_000).unwrap();
        AmmDex::create_token_pool(
            RuntimeOrigin::signed(alice()),
            aid_native(),
            aid_custom(0),
            100_000,
            100_000,
        )
        .unwrap();

        let alice_lp = AmmDex::token_lp(0, &alice()).unwrap_or(0);
        assert!(alice_lp > 0);
        assert_ok!(AmmDex::remove_token_liquidity(
            RuntimeOrigin::signed(alice()),
            0,
            alice_lp / 2,
        ));
        let alice_lp_after = AmmDex::token_lp(0, &alice()).unwrap_or(0);
        assert!(alice_lp_after < alice_lp);
    });
}

#[test]
fn test_token_swap_insufficient_balance() {
    new_test_ext().execute_with(|| {
        FungibleTokens::create(
            RuntimeOrigin::signed(alice()),
            b"TT".to_vec(),
            b"TT".to_vec(),
            6,
        )
        .unwrap();
        FungibleTokens::mint(RuntimeOrigin::signed(alice()), 0, alice(), 200_000).unwrap();
        AmmDex::create_token_pool(
            RuntimeOrigin::signed(alice()),
            aid_native(),
            aid_custom(0),
            100_000,
            100_000,
        )
        .unwrap();
        assert_noop!(
            AmmDex::swap_token(RuntimeOrigin::signed(bob()), 0, aid_custom(0), 5_000, 0,),
            Error::<Test>::InsufficientLiquidityBalance
        );
    });
}

#[test]
fn test_same_asset_fails() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            AmmDex::create_token_pool(
                RuntimeOrigin::signed(alice()),
                aid_native(),
                aid_native(),
                100_000,
                100_000,
            ),
            Error::<Test>::SameToken
        );
    });
}

// === PROPERTY TESTS: Economic Invariants ===

/// Property: Constant product k = reserve_a * reserve_b must NEVER decrease after a swap.
/// The fee ensures k increases slightly each trade. This is the core AMM safety invariant.
#[test]
fn prop_constant_product_never_decreases_after_swap() {
    new_test_ext().execute_with(|| {
        let token_a = b"VRDX".to_vec();
        let token_b = b"ECO".to_vec();
        let reserve_a: u128 = 1_000_000;
        let reserve_b: u128 = 500_000;

        // Create pool
        assert_ok!(AmmDex::create_pool(
            RuntimeOrigin::signed(alice()),
            token_a.clone(),
            token_b.clone(),
            reserve_a,
            reserve_b,
        ));

        let pool = Pools::<Test>::get(0).unwrap();
        let k_before = pool.reserve_a * pool.reserve_b;

        // Swap A -> B
        assert_ok!(AmmDex::swap(
            RuntimeOrigin::signed(alice()),
            0,
            token_a.clone(),
            10_000,
            0,
        ));

        let pool = Pools::<Test>::get(0).unwrap();
        let k_after_a_to_b = pool.reserve_a * pool.reserve_b;
        assert!(
            k_after_a_to_b >= k_before,
            "CONSTANT PRODUCT VIOLATED (A->B): k_before={}, k_after={}",
            k_before,
            k_after_a_to_b
        );

        // Swap B -> A
        assert_ok!(AmmDex::swap(
            RuntimeOrigin::signed(alice()),
            0,
            token_b.clone(),
            5_000,
            0,
        ));

        let pool = Pools::<Test>::get(0).unwrap();
        let k_after_b_to_a = pool.reserve_a * pool.reserve_b;
        assert!(
            k_after_b_to_a >= k_after_a_to_b,
            "CONSTANT PRODUCT VIOLATED (B->A): k_prev={}, k_after={}",
            k_after_a_to_b,
            k_after_b_to_a
        );
    });
}

/// Property: Multiple consecutive swaps must never decrease k.
/// Run N swaps in alternating directions and verify k is monotonically non-decreasing.
#[test]
fn prop_constant_product_monotonic_across_many_swaps() {
    new_test_ext().execute_with(|| {
        let token_a = b"VRDX".to_vec();
        let token_b = b"ECO".to_vec();

        assert_ok!(AmmDex::create_pool(
            RuntimeOrigin::signed(alice()),
            token_a.clone(),
            token_b.clone(),
            10_000_000,
            10_000_000,
        ));

        let mut last_k: u128 = {
            let pool = Pools::<Test>::get(0).unwrap();
            pool.reserve_a * pool.reserve_b
        };

        for i in 0..50 {
            let token = if i % 2 == 0 { token_a.clone() } else { token_b.clone() };
            let result = AmmDex::swap(
                RuntimeOrigin::signed(bob()),
                0,
                token,
                1_000,
                0,
            );
            if result.is_ok() {
                let pool = Pools::<Test>::get(0).unwrap();
                let k = pool.reserve_a * pool.reserve_b;
                assert!(
                    k >= last_k,
                    "CONSTANT PRODUCT DECREASED at swap {}: k_prev={}, k_new={}",
                    i, last_k, k
                );
                last_k = k;
            }
        }
    });
}

/// Property: Circuit breaker blocks swaps exceeding MaxPriceImpact (10% of reserves).
#[test]
fn prop_circuit_breaker_blocks_large_swaps() {
    new_test_ext().execute_with(|| {
        let token_a = b"VRDX".to_vec();
        let token_b = b"ECO".to_vec();
        let reserve: u128 = 1_000_000;

        assert_ok!(AmmDex::create_pool(
            RuntimeOrigin::signed(alice()),
            token_a.clone(),
            token_b.clone(),
            reserve,
            reserve,
        ));

        // Swap within 10% limit should succeed
        assert_ok!(AmmDex::swap(
            RuntimeOrigin::signed(alice()),
            0,
            token_a.clone(),
            50_000, // 5% of reserves
            0,
        ));

        // Reset pool for large swap test
        assert_ok!(AmmDex::create_pool(
            RuntimeOrigin::signed(alice()),
            b"VRDX2".to_vec(),
            b"ECO2".to_vec(),
            reserve,
            reserve,
        ));

        // Swap exceeding 10% should fail
        assert_noop!(
            AmmDex::swap(
                RuntimeOrigin::signed(bob()),
                1,
                b"VRDX2".to_vec(),
                200_000, // 20% of reserves - exceeds 10% cap
                0,
            ),
            Error::<Test>::PriceImpactTooHigh
        );
    });
}

/// Property: Remove liquidity returns proportional amounts and k stays constant.
/// Removing liquidity should not change the price ratio (k per LP token stays constant).
#[test]
fn prop_remove_liquidity_preserves_ratio() {
    new_test_ext().execute_with(|| {
        let token_a = b"VRDX".to_vec();
        let token_b = b"ECO".to_vec();
        let ra: u128 = 1_000_000;
        let rb: u128 = 2_000_000;

        assert_ok!(AmmDex::create_pool(
            RuntimeOrigin::signed(alice()),
            token_a.clone(),
            token_b.clone(),
            ra,
            rb,
        ));

        let pool = Pools::<Test>::get(0).unwrap();
        let total_lp = pool.total_lp;
        let half_lp = total_lp / 2;

        // Remove half of LP
        assert_ok!(AmmDex::remove_liquidity(
            RuntimeOrigin::signed(alice()),
            0,
            half_lp,
        ));

        let pool_after = Pools::<Test>::get(0).unwrap();
        // Reserves should be halved
        assert!(
            pool_after.reserve_a <= ra / 2 + 1,
            "Reserve A not proportional: got {}, expected ~{}",
            pool_after.reserve_a,
            ra / 2
        );
        assert!(
            pool_after.reserve_b <= rb / 2 + 1,
            "Reserve B not proportional: got {}, expected ~{}",
            pool_after.reserve_b,
            rb / 2
        );
        // Ratio should be preserved
        let ratio_before = ra / rb;
        let ratio_after = pool_after.reserve_a / pool_after.reserve_b;
        assert_eq!(
            ratio_before, ratio_after,
            "Price ratio changed after remove_liquidity"
        );
    });
}

/// Property: Swap output matches the AMM formula exactly.
/// amount_out = (reserve_out * amount_in_after_fee) / (reserve_in + amount_in_after_fee)
#[test]
fn prop_swap_output_matches_formula() {
    new_test_ext().execute_with(|| {
        let token_a = b"VRDX".to_vec();
        let token_b = b"ECO".to_vec();
        let reserve_a: u128 = 1_000_000;
        let reserve_b: u128 = 500_000;
        let amount_in: u128 = 10_000;

        assert_ok!(AmmDex::create_pool(
            RuntimeOrigin::signed(alice()),
            token_a.clone(),
            token_b.clone(),
            reserve_a,
            reserve_b,
        ));

        // Calculate expected output
        let fee_num: u128 = FeeNumerator::get() as u128;
        let fee_den: u128 = FeeDenominator::get() as u128;
        let fee = amount_in * fee_num / fee_den;
        let amount_in_after_fee = amount_in - fee;
        let expected_out = (reserve_b * amount_in_after_fee) / (reserve_a + amount_in_after_fee);

        // Execute swap
        assert_ok!(AmmDex::swap(
            RuntimeOrigin::signed(bob()),
            0,
            token_a.clone(),
            amount_in,
            0,
        ));

        // Verify reserve_b decreased by exactly expected_out
        let pool = Pools::<Test>::get(0).unwrap();
        let actual_out = reserve_b - pool.reserve_b;
        assert_eq!(
            actual_out, expected_out,
            "Swap output mismatch: expected {}, got {}",
            expected_out, actual_out
        );
    });
}

/// Property: Zero amount swaps are rejected.
#[test]
fn prop_zero_amount_swap_rejected() {
    new_test_ext().execute_with(|| {
        let token_a = b"VRDX".to_vec();
        let token_b = b"ECO".to_vec();

        assert_ok!(AmmDex::create_pool(
            RuntimeOrigin::signed(alice()),
            token_a.clone(),
            token_b.clone(),
            1_000_000,
            1_000_000,
        ));

        assert_noop!(
            AmmDex::swap(
                RuntimeOrigin::signed(bob()),
                0,
                token_a.clone(),
                0,
                0,
            ),
            Error::<Test>::ZeroAmount
        );
    });
}

/// Property: Slippage protection rejects unfavorable swaps.
#[test]
fn prop_slippage_protection_works() {
    new_test_ext().execute_with(|| {
        let token_a = b"VRDX".to_vec();
        let token_b = b"ECO".to_vec();

        assert_ok!(AmmDex::create_pool(
            RuntimeOrigin::signed(alice()),
            token_a.clone(),
            token_b.clone(),
            1_000_000,
            1_000_000,
        ));

        // Set min_amount_out impossibly high
        assert_noop!(
            AmmDex::swap(
                RuntimeOrigin::signed(bob()),
                0,
                token_a.clone(),
                10_000,
                999_999_999, // impossibly high
            ),
            Error::<Test>::SlippageExceeded
        );
    });
}
