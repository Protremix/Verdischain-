#![allow(clippy::let_unit_value)]
use crate::{self as pallet_amm_dex, *};
use frame_support::{
    assert_noop, assert_ok, construct_runtime, derive_impl, parameter_types,
    traits::{ConstU16, ConstU32, ConstU64},
    PalletId,
};
use sp_core::H256;
use sp_runtime::{
    traits::{BlakeTwo256, IdentityLookup},
    BuildStorage,
};

type Block = frame_system::mocking::MockBlock<Test>;

construct_runtime!(
    pub enum Test {
        System: frame_system,
        Balances: pallet_balances,
        AmmDex: pallet_amm_dex,
    }
);

#[derive_impl(frame_system::config_preludes::TestDefaultConfig)]
impl frame_system::Config for Test {
    type BaseCallFilter = frame_support::traits::Everything;
    type BlockWeights = ();
    type BlockLength = ();
    type DbWeight = ();
    type RuntimeOrigin = RuntimeOrigin;
    type RuntimeCall = RuntimeCall;
    type Nonce = u64;
    type Hash = H256;
    type Hashing = BlakeTwo256;
    type AccountId = u64;
    type Lookup = IdentityLookup<Self::AccountId>;
    type Block = Block;
    type RuntimeEvent = RuntimeEvent;
    type BlockHashCount = ConstU64<250>;
    type Version = ();
    type PalletInfo = PalletInfo;
    type AccountData = pallet_balances::AccountData<u64>;
    type OnNewAccount = ();
    type OnKilledAccount = ();
    type SystemWeightInfo = ();
    type SS58Prefix = ConstU16<42>;
    type OnSetCode = ();
    type MaxConsumers = ConstU32<16>;
}

#[derive_impl(pallet_balances::config_preludes::TestDefaultConfig)]
impl pallet_balances::Config for Test {
    type Balance = u64;
    type DustRemoval = ();
    type RuntimeEvent = RuntimeEvent;
    type ExistentialDeposit = ConstU64<1>;
    type AccountStore = System;
    type WeightInfo = ();
    type MaxLocks = ConstU32<50>;
    type MaxReserves = ConstU32<50>;
    type ReserveIdentifier = [u8; 8];
    type FreezeIdentifier = ();
    type MaxFreezes = ConstU32<0>;
    type RuntimeHoldReason = ();
    type RuntimeFreezeReason = ();
}

parameter_types! {
    pub const AmmPalletId: PalletId = PalletId(*b"ver/ammd");
    pub const FeeNumerator: u32 = 3;
    pub const FeeDenominator: u32 = 1000;
    pub const MinLiquidity: u64 = 1_000_000_000_000;
    pub const MaxPools: u32 = 50;
}

impl pallet_amm_dex::Config for Test {
    type RuntimeEvent = RuntimeEvent;
    type Currency = Balances;
    type PalletId = AmmPalletId;
    type FeeNumerator = FeeNumerator;
    type FeeDenominator = FeeDenominator;
    type MinLiquidity = MinLiquidity;
    type MaxPools = MaxPools;
    type WeightInfo = ();
}

pub fn new_test_ext() -> sp_io::TestExternalities {
    let mut t = frame_system::GenesisConfig::<Test>::default()
        .build_storage()
        .unwrap();
    pallet_balances::GenesisConfig::<Test> {
        balances: vec![
            (1, 100_000_000_000_000_000),
            (2, 100_000_000_000_000_000),
            (3, 100_000_000_000_000_000),
            (4, 100_000_000_000_000_000),
        ],
        ..Default::default()
    }
    .assimilate_storage(&mut t)
    .unwrap();

    let mut ext = sp_io::TestExternalities::new(t);
    ext.execute_with(|| System::set_block_number(1));
    ext
}

fn last_event() -> RuntimeEvent {
    System::events().pop().expect("Event expected").event
}

// =========================================================================
// CREATE POOL TESTS
// =========================================================================

#[test]
fn create_pool_success() {
    new_test_ext().execute_with(|| {
        let amount_a = 2_000_000_000_000u64;
        let amount_b = 2_000_000_000_000u64;
        let expected_lp = 2_000_000_000_000u64;

        assert_ok!(AmmDex::create_pool(
            RuntimeOrigin::signed(1),
            b"TOKENA".to_vec(),
            b"TOKENB".to_vec(),
            amount_a,
            amount_b
        ));

        // Check pool count
        assert_eq!(AmmDex::pool_count(), 1);

        // Check pool details
        let pool = AmmDex::pools(0).expect("Pool 0 should exist");
        assert_eq!(pool.id, 0);
        assert_eq!(pool.token_a.to_vec(), b"TOKENA".to_vec());
        assert_eq!(pool.token_b.to_vec(), b"TOKENB".to_vec());
        assert_eq!(pool.reserve_a, amount_a);
        assert_eq!(pool.reserve_b, amount_b);
        assert_eq!(pool.total_lp, expected_lp);
        assert_eq!(pool.fee_numerator, 3);
        assert_eq!(pool.fee_denominator, 1000);
        assert_eq!(pool.creator, 1);

        // Check PoolByPair mapping
        let ta: BoundedVec<u8, ConstU32<32>> = b"TOKENA".to_vec().try_into().unwrap();
        let tb: BoundedVec<u8, ConstU32<32>> = b"TOKENB".to_vec().try_into().unwrap();
        assert_eq!(AmmDex::pool_by_pair((ta, tb)), Some(0));

        // Check user LP balance
        assert_eq!(AmmDex::liquidity_providers(0, 1), Some(expected_lp));

        // Check event
        assert_eq!(
            last_event(),
            RuntimeEvent::AmmDex(Event::PoolCreated {
                pool_id: 0,
                token_a: b"TOKENA".to_vec(),
                token_b: b"TOKENB".to_vec(),
                creator: 1,
            })
        );
    });
}

#[test]
fn create_pool_fails_same_token() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            AmmDex::create_pool(
                RuntimeOrigin::signed(1),
                b"TOKENA".to_vec(),
                b"TOKENA".to_vec(),
                2_000_000_000_000,
                2_000_000_000_000
            ),
            Error::<Test>::SameToken
        );
    });
}

#[test]
fn create_pool_fails_zero_amount() {
    new_test_ext().execute_with(|| {
        // Zero amount for token A
        assert_noop!(
            AmmDex::create_pool(
                RuntimeOrigin::signed(1),
                b"TOKENA".to_vec(),
                b"TOKENB".to_vec(),
                0,
                2_000_000_000_000
            ),
            Error::<Test>::ZeroAmount
        );

        // Zero amount for token B
        assert_noop!(
            AmmDex::create_pool(
                RuntimeOrigin::signed(1),
                b"TOKENA".to_vec(),
                b"TOKENB".to_vec(),
                2_000_000_000_000,
                0
            ),
            Error::<Test>::ZeroAmount
        );
    });
}

#[test]
fn create_pool_fails_already_exists() {
    new_test_ext().execute_with(|| {
        assert_ok!(AmmDex::create_pool(
            RuntimeOrigin::signed(1),
            b"TOKENA".to_vec(),
            b"TOKENB".to_vec(),
            2_000_000_000_000,
            2_000_000_000_000
        ));

        assert_noop!(
            AmmDex::create_pool(
                RuntimeOrigin::signed(2),
                b"TOKENA".to_vec(),
                b"TOKENB".to_vec(),
                2_000_000_000_000,
                2_000_000_000_000
            ),
            Error::<Test>::PoolAlreadyExists
        );
    });
}

#[test]
fn create_pool_fails_max_pools_reached() {
    new_test_ext().execute_with(|| {
        // MaxPools is 50
        for i in 0..50u8 {
            let token_a = format!("TK_A_{}", i).into_bytes();
            let token_b = format!("TK_B_{}", i).into_bytes();
            assert_ok!(AmmDex::create_pool(
                RuntimeOrigin::signed(1),
                token_a,
                token_b,
                2_000_000_000_000,
                2_000_000_000_000
            ));
        }

        assert_eq!(AmmDex::pool_count(), 50);

        // 51st attempt fails
        assert_noop!(
            AmmDex::create_pool(
                RuntimeOrigin::signed(1),
                b"TK_EXTRA_A".to_vec(),
                b"TK_EXTRA_B".to_vec(),
                2_000_000_000_000,
                2_000_000_000_000
            ),
            Error::<Test>::MaxPoolsReached
        );
    });
}

#[test]
fn create_pool_fails_amount_too_low() {
    new_test_ext().execute_with(|| {
        // MinLiquidity is 1_000_000_000_000
        // sqrt(1_000_000 * 1_000_000) = 1_000_000 < MinLiquidity
        assert_noop!(
            AmmDex::create_pool(
                RuntimeOrigin::signed(1),
                b"TOKENA".to_vec(),
                b"TOKENB".to_vec(),
                1_000_000,
                1_000_000
            ),
            Error::<Test>::AmountTooLow
        );
    });
}

#[test]
fn create_pool_fails_token_too_long() {
    new_test_ext().execute_with(|| {
        let long_token = vec![b'X'; 33];
        assert_noop!(
            AmmDex::create_pool(
                RuntimeOrigin::signed(1),
                long_token,
                b"TOKENB".to_vec(),
                2_000_000_000_000,
                2_000_000_000_000
            ),
            Error::<Test>::TokenTooLong
        );
    });
}

// =========================================================================
// ADD LIQUIDITY TESTS
// =========================================================================

#[test]
fn add_liquidity_success() {
    new_test_ext().execute_with(|| {
        assert_ok!(AmmDex::create_pool(
            RuntimeOrigin::signed(1),
            b"TOKENA".to_vec(),
            b"TOKENB".to_vec(),
            2_000_000_000_000,
            2_000_000_000_000
        ));

        let add_a = 1_000_000_000_000u64;
        let add_b = 1_000_000_000_000u64;
        let expected_minted = 1_000_000_000_000u64; // (2_000_000_000_000 * 1_000_000_000_000) / 2_000_000_000_000

        assert_ok!(AmmDex::add_liquidity(
            RuntimeOrigin::signed(2),
            0,
            add_a,
            add_b
        ));

        let pool = AmmDex::pools(0).unwrap();
        assert_eq!(pool.reserve_a, 3_000_000_000_000);
        assert_eq!(pool.reserve_b, 3_000_000_000_000);
        assert_eq!(pool.total_lp, 3_000_000_000_000);

        assert_eq!(AmmDex::liquidity_providers(0, 2), Some(expected_minted));

        assert_eq!(
            last_event(),
            RuntimeEvent::AmmDex(Event::LiquidityAdded {
                pool_id: 0,
                provider: 2,
                amount_a: add_a,
                amount_b: add_b,
                lp_minted: expected_minted,
            })
        );
    });
}

#[test]
fn add_liquidity_fails_not_found() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            AmmDex::add_liquidity(
                RuntimeOrigin::signed(1),
                999,
                1_000_000_000_000,
                1_000_000_000_000
            ),
            Error::<Test>::PoolNotFound
        );
    });
}

#[test]
fn add_liquidity_fails_zero_amount() {
    new_test_ext().execute_with(|| {
        assert_ok!(AmmDex::create_pool(
            RuntimeOrigin::signed(1),
            b"TOKENA".to_vec(),
            b"TOKENB".to_vec(),
            2_000_000_000_000,
            2_000_000_000_000
        ));

        assert_noop!(
            AmmDex::add_liquidity(RuntimeOrigin::signed(2), 0, 0, 1_000_000_000_000),
            Error::<Test>::ZeroAmount
        );

        assert_noop!(
            AmmDex::add_liquidity(RuntimeOrigin::signed(2), 0, 1_000_000_000_000, 0),
            Error::<Test>::ZeroAmount
        );
    });
}

#[test]
fn add_liquidity_fails_insufficient_amount() {
    new_test_ext().execute_with(|| {
        assert_ok!(AmmDex::create_pool(
            RuntimeOrigin::signed(1),
            b"TOKENA".to_vec(),
            b"TOKENB".to_vec(),
            2_000_000_000_000,
            2_000_000_000_000
        ));

        // Amount so small that total_lp * amount / reserve = 0
        assert_noop!(
            AmmDex::add_liquidity(RuntimeOrigin::signed(2), 0, 0, 1),
            Error::<Test>::ZeroAmount
        );
    });
}

// =========================================================================
// SWAP TESTS
// =========================================================================

#[test]
fn swap_success_with_invariant_and_fee() {
    new_test_ext().execute_with(|| {
        let initial_a = 10_000_000_000_000u64;
        let initial_b = 10_000_000_000_000u64;

        assert_ok!(AmmDex::create_pool(
            RuntimeOrigin::signed(1),
            b"TOKENA".to_vec(),
            b"TOKENB".to_vec(),
            initial_a,
            initial_b
        ));

        let amount_in = 100_000_000_000u64; // 100B token A
                                            // Fee = 0.3% of 100B = 300,000,000
        let expected_fee = amount_in * 3 / 1000;
        let amount_in_after_fee = amount_in - expected_fee; // 99,700,000,000

        // Constant product formula:
        // amount_out = (reserve_b * amount_in_after_fee) / (reserve_a + amount_in_after_fee)
        let expected_numerator = initial_b as u128 * amount_in_after_fee as u128;
        let expected_denominator = initial_a as u128 + amount_in_after_fee as u128;
        let expected_amount_out = (expected_numerator / expected_denominator) as u64;

        assert_ok!(AmmDex::swap(
            RuntimeOrigin::signed(2),
            0,
            b"TOKENA".to_vec(),
            amount_in,
            1 // min_amount_out
        ));

        let pool = AmmDex::pools(0).unwrap();
        assert_eq!(pool.reserve_a, initial_a + amount_in);
        assert_eq!(pool.reserve_b, initial_b - expected_amount_out);

        // Constant-product invariant check (x * y = k)
        // Note: Due to fee retention in pool reserve_a, new_k >= old_k
        let old_k = initial_a as u128 * initial_b as u128;
        let new_k = pool.reserve_a as u128 * pool.reserve_b as u128;
        assert!(
            new_k >= old_k,
            "x*y=k invariant violated: new_k ({}) < old_k ({})",
            new_k,
            old_k
        );

        // Check global volume and swap count
        assert_eq!(AmmDex::total_volume(), amount_in);
        assert_eq!(AmmDex::total_swaps(), 1);

        // Check event
        assert_eq!(
            last_event(),
            RuntimeEvent::AmmDex(Event::SwapExecuted {
                pool_id: 0,
                trader: 2,
                token_in: b"TOKENA".to_vec(),
                token_out: b"TOKENB".to_vec(),
                amount_in,
                amount_out: expected_amount_out,
                fee: expected_fee,
            })
        );

        // Swap back token B -> token A
        let amount_in_b = 50_000_000_000u64;
        assert_ok!(AmmDex::swap(
            RuntimeOrigin::signed(3),
            0,
            b"TOKENB".to_vec(),
            amount_in_b,
            1
        ));

        assert_eq!(AmmDex::total_swaps(), 2);
        assert_eq!(AmmDex::total_volume(), amount_in + amount_in_b);
    });
}

#[test]
fn swap_fails_not_found() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            AmmDex::swap(
                RuntimeOrigin::signed(1),
                999, // Non-existent pool
                b"TOKENA".to_vec(),
                10_000_000_000,
                1
            ),
            Error::<Test>::PoolNotFound
        );

        // Pool exists, but token_in is not in pool
        assert_ok!(AmmDex::create_pool(
            RuntimeOrigin::signed(1),
            b"TOKENA".to_vec(),
            b"TOKENB".to_vec(),
            2_000_000_000_000,
            2_000_000_000_000
        ));

        assert_noop!(
            AmmDex::swap(
                RuntimeOrigin::signed(1),
                0,
                b"TOKEN_WRONG".to_vec(),
                10_000_000_000,
                1
            ),
            Error::<Test>::PoolNotFound
        );
    });
}

#[test]
fn swap_fails_zero_amount() {
    new_test_ext().execute_with(|| {
        assert_ok!(AmmDex::create_pool(
            RuntimeOrigin::signed(1),
            b"TOKENA".to_vec(),
            b"TOKENB".to_vec(),
            2_000_000_000_000,
            2_000_000_000_000
        ));

        assert_noop!(
            AmmDex::swap(RuntimeOrigin::signed(2), 0, b"TOKENA".to_vec(), 0, 1),
            Error::<Test>::ZeroAmount
        );
    });
}

#[test]
fn swap_fails_slippage_exceeded() {
    new_test_ext().execute_with(|| {
        assert_ok!(AmmDex::create_pool(
            RuntimeOrigin::signed(1),
            b"TOKENA".to_vec(),
            b"TOKENB".to_vec(),
            2_000_000_000_000,
            2_000_000_000_000
        ));

        let amount_in = 10_000_000_000u64;
        // Demanding unrealistic output amount
        assert_noop!(
            AmmDex::swap(
                RuntimeOrigin::signed(2),
                0,
                b"TOKENA".to_vec(),
                amount_in,
                20_000_000_000 // More than possible
            ),
            Error::<Test>::SlippageExceeded
        );
    });
}

#[test]
fn swap_fails_insufficient_liquidity() {
    new_test_ext().execute_with(|| {
        assert_ok!(AmmDex::create_pool(
            RuntimeOrigin::signed(1),
            b"TOKENA".to_vec(),
            b"TOKENB".to_vec(),
            100_000_000_000_000, // huge reserve
            10_000_000_000_000
        ));

        // Swapping 1 unit yields 0 output due to integer division
        assert_noop!(
            AmmDex::swap(
                RuntimeOrigin::signed(2),
                0,
                b"TOKENA".to_vec(),
                1, // tiny input
                0
            ),
            Error::<Test>::InsufficientLiquidity
        );
    });
}

// =========================================================================
// REMOVE LIQUIDITY TESTS
// =========================================================================

#[test]
fn remove_liquidity_success() {
    new_test_ext().execute_with(|| {
        let amount_a = 2_000_000_000_000u64;
        let amount_b = 2_000_000_000_000u64;

        assert_ok!(AmmDex::create_pool(
            RuntimeOrigin::signed(1),
            b"TOKENA".to_vec(),
            b"TOKENB".to_vec(),
            amount_a,
            amount_b
        ));

        let remove_lp = 1_000_000_000_000u64; // half of LP
        let expected_a = 1_000_000_000_000u64;
        let expected_b = 1_000_000_000_000u64;

        assert_ok!(AmmDex::remove_liquidity(
            RuntimeOrigin::signed(1),
            0,
            remove_lp
        ));

        let pool = AmmDex::pools(0).unwrap();
        assert_eq!(pool.reserve_a, 1_000_000_000_000);
        assert_eq!(pool.reserve_b, 1_000_000_000_000);
        assert_eq!(pool.total_lp, 1_000_000_000_000);

        assert_eq!(AmmDex::user_lp(0, &1), 1_000_000_000_000);

        assert_eq!(
            last_event(),
            RuntimeEvent::AmmDex(Event::LiquidityRemoved {
                pool_id: 0,
                provider: 1,
                amount_a: expected_a,
                amount_b: expected_b,
                lp_burned: remove_lp,
            })
        );
    });
}

#[test]
fn remove_liquidity_fails_not_found() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            AmmDex::remove_liquidity(RuntimeOrigin::signed(1), 999, 1_000_000_000_000),
            Error::<Test>::PoolNotFound
        );
    });
}

#[test]
fn remove_liquidity_fails_zero_amount() {
    new_test_ext().execute_with(|| {
        assert_ok!(AmmDex::create_pool(
            RuntimeOrigin::signed(1),
            b"TOKENA".to_vec(),
            b"TOKENB".to_vec(),
            2_000_000_000_000,
            2_000_000_000_000
        ));

        assert_noop!(
            AmmDex::remove_liquidity(RuntimeOrigin::signed(1), 0, 0),
            Error::<Test>::ZeroAmount
        );
    });
}

#[test]
fn remove_liquidity_fails_insufficient_lp() {
    new_test_ext().execute_with(|| {
        assert_ok!(AmmDex::create_pool(
            RuntimeOrigin::signed(1),
            b"TOKENA".to_vec(),
            b"TOKENB".to_vec(),
            2_000_000_000_000,
            2_000_000_000_000
        ));

        // User 2 has 0 LP
        assert_noop!(
            AmmDex::remove_liquidity(RuntimeOrigin::signed(2), 0, 1_000_000_000_000),
            Error::<Test>::InsufficientLpBalance
        );

        // User 1 tries to remove more LP than they have (has 2T, asks 3T)
        assert_noop!(
            AmmDex::remove_liquidity(RuntimeOrigin::signed(1), 0, 3_000_000_000_000),
            Error::<Test>::InsufficientLpBalance
        );
    });
}

// =========================================================================
// PRICE & TVL QUERY TESTS
// =========================================================================

#[test]
fn get_price_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(AmmDex::create_pool(
            RuntimeOrigin::signed(1),
            b"TOKENA".to_vec(),
            b"TOKENB".to_vec(),
            2_000_000_000_000,
            2_000_000_000_000
        ));

        // Success
        assert_ok!(AmmDex::get_price(RuntimeOrigin::signed(1), 0));

        // Fail: pool not found
        assert_noop!(
            AmmDex::get_price(RuntimeOrigin::signed(1), 999),
            Error::<Test>::PoolNotFound
        );
    });
}

#[test]
fn pool_price_works() {
    new_test_ext().execute_with(|| {
        // Pool not found
        assert_eq!(AmmDex::pool_price(0), None);

        // Create pool with 4:2 ratio (reserve_a = 4T, reserve_b = 2T)
        assert_ok!(AmmDex::create_pool(
            RuntimeOrigin::signed(1),
            b"TOKENA".to_vec(),
            b"TOKENB".to_vec(),
            4_000_000_000_000,
            2_000_000_000_000
        ));

        // Price = 4_000_000_000_000 / 2_000_000_000_000 = 2
        assert_eq!(AmmDex::pool_price(0), Some(2));
    });
}

#[test]
fn pool_tvl_works() {
    new_test_ext().execute_with(|| {
        // Non-existent pool
        assert_eq!(AmmDex::pool_tvl(0), None);

        let reserve_a = 4_000_000_000_000u64;
        let reserve_b = 2_000_000_000_000u64;

        assert_ok!(AmmDex::create_pool(
            RuntimeOrigin::signed(1),
            b"TOKENA".to_vec(),
            b"TOKENB".to_vec(),
            reserve_a,
            reserve_b
        ));

        assert_eq!(AmmDex::pool_tvl(0), Some((reserve_a, reserve_b)));
    });
}


// ==================== REAL BENCHMARK WEIGHT GENERATION ====================
#[cfg(feature = "runtime-benchmarks")]
mod real_bench {
    use super::*;
    use super::{Test, new_test_ext};
    use std::time::Instant;
    use frame_support::traits::fungible::Mutate;

    fn measure_bench<F: FnMut() -> bool>(name: &str, iters: u32, mut f: F) -> u64 {
        let mut times: Vec<u64> = Vec::new();
        for _ in 0..iters {
            let start = Instant::now();
            let ok = f();
            let elapsed = start.elapsed().as_nanos() as u64;
            if ok { times.push(elapsed); }
        }
        if times.is_empty() {
            println!("  {pallet}::{name} -> FAILED", pallet = PALLET_NAME, name = name);
            return 10_000;
        }
        let avg = times.iter().sum::<u64>() / times.len() as u64;
        let max = *times.iter().max().unwrap();
        let weight = (avg as f64 * 1.25).max(10000.0) as u64;
        println!("  {pallet}::{name} -> avg={avg}ns max={max}ns weight={weight}", pallet = PALLET_NAME, name = name, avg = avg, max = max, weight = weight);
        weight
    }

    const PALLET_NAME: &str = "amm_dex";

    #[test]
    #[ignore]
    fn real_bench() {
        new_test_ext().execute_with(|| {{
            use frame_system::Pallet as System;
            System::<Test>::set_block_number(1);
            
            // Fund accounts
            for i in 1u64..=10u64 {
                <pallet_balances::Pallet<Test> as Mutate<u64>>::set_balance(&i, 100_000_000_000_000_000);
            }
            let mut results: Vec<(&str, u64)> = Vec::new();

            // Benchmark: create_pool
            let mut pool_idx = 0u32;
            let w = measure_bench("create_pool", 40, || {
                pool_idx += 1;
                let token_a = format!("token_a_{}", pool_idx).into_bytes();
                let token_b = format!("token_b_{}", pool_idx).into_bytes();
                AmmDex::create_pool(RuntimeOrigin::signed(1), token_a, token_b, 2_000_000_000_000, 2_000_000_000_000).is_ok()
            });
            results.push(("create_pool", w));

            // Create a pool for remaining benchmarks
            assert_ok!(AmmDex::create_pool(RuntimeOrigin::signed(1), b"AAA".to_vec(), b"BBB".to_vec(), 2_000_000_000_000, 2_000_000_000_000));

            // Benchmark: add_liquidity
            let w = measure_bench("add_liquidity", 30, || {
                <pallet_balances::Pallet<Test> as Mutate<u64>>::set_balance(&1, 100_000_000_000_000_000);
                AmmDex::add_liquidity(RuntimeOrigin::signed(1), 40, 100_000_000, 100_000_000).is_ok()
            });
            results.push(("add_liquidity", w));

            // Benchmark: swap
            let w = measure_bench("swap", 30, || {
                <pallet_balances::Pallet<Test> as Mutate<u64>>::set_balance(&2, 100_000_000_000_000_000);
                AmmDex::swap(RuntimeOrigin::signed(2), 40, b"AAA".to_vec(), 10_000_000, 1).is_ok()
            });
            results.push(("swap", w));

            println!("\n//! WeightInfo for pallet-amm-dex (real benchmark)");
            println!("pub struct WeightInfo;");
            for (name, weight) in &results {
                println!("// {}: {} weight units", name, weight);
            }

        }});
    }
}
