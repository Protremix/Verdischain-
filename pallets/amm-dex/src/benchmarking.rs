//! Benchmarking for the Verdis AmmDex pallet
#![cfg(feature = "runtime-benchmarks")]
#![allow(unused_must_use, unused_variables, clippy::all)]

use crate::pallet::{
    AssetId, Config, Pallet as AmmDex, PoolCount, Pools, TokenHandler, TokenPoolCount, TokenPools,
};
use frame_benchmarking::v2::*;
use frame_support::{traits::ConstU32, BoundedVec};
use frame_system::pallet_prelude::BlockNumberFor;
use frame_system::RawOrigin;
use sp_runtime::traits::Bounded;
use sp_std::vec;

type BalanceOf<T> = <<T as Config>::Currency as frame_support::traits::Currency<
    <T as frame_system::Config>::AccountId,
>>::Balance;

fn make_token_bytes(prefix: u8) -> BoundedVec<u8, ConstU32<32>> {
    let bytes = vec![prefix; 4];
    BoundedVec::try_from(bytes).expect("4 bytes fits in 32")
}

// Scale constants: UNITS = 10^9, MinLiquidity = 10^3 * UNITS = 10^12
// Pool amounts must produce lp_minted >= MinLiquidity => sqrt(a*b) >= 10^12 => a*b >= 10^24
// Using 10^13 each: sqrt(10^13 * 10^13) = 10^13 > 10^12 ✓
const BENCH_FUND: u128 = 1_000_000_000_000_000_000; // 10^18 — plenty for all operations
const BENCH_AMOUNT: u128 = 10_000_000_000_000; // 10^13 — above MinLiquidity (10^12)
const BENCH_LP_BURN: u128 = 1_000_000_000_000; // 10^12 — minimal LP burn
const BENCH_SWAP_IN: u128 = 100_000_000_000; // 10^11 — swap input

/// Fund the caller with sufficient balance for benchmark operations
fn fund_caller<T: Config>(caller: &T::AccountId) {
    let amount: BalanceOf<T> = BENCH_FUND.try_into().unwrap_or_default();
    <<T as Config>::Currency as frame_support::traits::Currency<_>>::deposit_creating(
        caller, amount,
    );
    // Also fund custom token for token pool benchmarks
    T::TokenHandler::fund_for_benchmark(&AssetId::Custom(0), caller, amount);
}

#[benchmarks]
mod benches {
    use super::*;
    use crate::pallet::*;

    #[benchmark]
    fn create_pool() {
        let caller: T::AccountId = whitelisted_caller();
        fund_caller::<T>(&caller);
        let token_a = make_token_bytes(1u8);
        let token_b = make_token_bytes(2u8);
        let amount_a: BalanceOf<T> = BENCH_AMOUNT.try_into().unwrap_or_default();
        let amount_b: BalanceOf<T> = BENCH_AMOUNT.try_into().unwrap_or_default();

        #[extrinsic_call]
        create_pool(
            RawOrigin::Signed(caller),
            token_a.to_vec(),
            token_b.to_vec(),
            amount_a,
            amount_b,
        );

        assert!(PoolCount::<T>::get() >= 1);
    }

    #[benchmark]
    fn add_liquidity(n: Linear<1, 10>) {
        let caller: T::AccountId = whitelisted_caller();
        fund_caller::<T>(&caller);
        let token_a = make_token_bytes(1u8);
        let token_b = make_token_bytes(2u8);

        let _ = AmmDex::<T>::create_pool(
            RawOrigin::Signed(caller.clone()).into(),
            token_a.to_vec(),
            token_b.to_vec(),
            BENCH_AMOUNT.try_into().unwrap_or_default(),
            BENCH_AMOUNT.try_into().unwrap_or_default(),
        );

        let pool_id = PoolCount::<T>::get() - 1;
        let extra: u128 = n as u128 * 1_000_000_000_000; // n * 10^12
        let amount_a: BalanceOf<T> = (5_000_000_000_000 + extra).try_into().unwrap_or_default();
        let amount_b: BalanceOf<T> = (5_000_000_000_000 + extra).try_into().unwrap_or_default();

        #[extrinsic_call]
        add_liquidity(
            RawOrigin::Signed(caller),
            pool_id,
            amount_a,
            amount_b,
            BlockNumberFor::<T>::max_value(),
        );

        let pool = Pools::<T>::get(pool_id).unwrap();
        assert!(pool.total_lp > 0u32.into());
    }

    #[benchmark]
    fn remove_liquidity() {
        let caller: T::AccountId = whitelisted_caller();
        fund_caller::<T>(&caller);
        let token_a = make_token_bytes(1u8);
        let token_b = make_token_bytes(2u8);

        let _ = AmmDex::<T>::create_pool(
            RawOrigin::Signed(caller.clone()).into(),
            token_a.to_vec(),
            token_b.to_vec(),
            BENCH_AMOUNT.try_into().unwrap_or_default(),
            BENCH_AMOUNT.try_into().unwrap_or_default(),
        );

        let pool_id = PoolCount::<T>::get() - 1;
        let lp_amount: BalanceOf<T> = BENCH_LP_BURN.try_into().unwrap_or_default();

        #[extrinsic_call]
        remove_liquidity(
            RawOrigin::Signed(caller),
            pool_id,
            lp_amount,
            BlockNumberFor::<T>::max_value(),
        );

        assert!(Pools::<T>::get(pool_id).is_some());
    }

    #[benchmark]
    fn swap() {
        let caller: T::AccountId = whitelisted_caller();
        fund_caller::<T>(&caller);
        let token_a = make_token_bytes(1u8);
        let token_b = make_token_bytes(2u8);

        let _ = AmmDex::<T>::create_pool(
            RawOrigin::Signed(caller.clone()).into(),
            token_a.to_vec(),
            token_b.to_vec(),
            BENCH_AMOUNT.try_into().unwrap_or_default(),
            BENCH_AMOUNT.try_into().unwrap_or_default(),
        );

        let pool_id = PoolCount::<T>::get() - 1;
        let amount_in: BalanceOf<T> = BENCH_SWAP_IN.try_into().unwrap_or_default();
        let min_out: BalanceOf<T> = 0u32.into();

        #[extrinsic_call]
        swap(
            RawOrigin::Signed(caller),
            pool_id,
            token_a.to_vec(),
            amount_in,
            min_out,
            BlockNumberFor::<T>::max_value(),
        );

        let pool = Pools::<T>::get(pool_id).unwrap();
        assert!(pool.reserve_a > 0u32.into());
    }

    #[benchmark]
    fn create_token_pool() {
        let caller: T::AccountId = whitelisted_caller();
        fund_caller::<T>(&caller);
        let asset_a = AssetId::Native;
        let asset_b = AssetId::Custom(0);
        let amount_a: BalanceOf<T> = BENCH_AMOUNT.try_into().unwrap_or_default();
        let amount_b: BalanceOf<T> = BENCH_AMOUNT.try_into().unwrap_or_default();

        #[extrinsic_call]
        create_token_pool(
            RawOrigin::Signed(caller),
            asset_a,
            asset_b,
            amount_a,
            amount_b,
        );

        assert!(TokenPoolCount::<T>::get() >= 1);
    }

    #[benchmark]
    fn add_token_liquidity(n: Linear<1, 10>) {
        let caller: T::AccountId = whitelisted_caller();
        fund_caller::<T>(&caller);
        let asset_a = AssetId::Native;
        let asset_b = AssetId::Custom(0);

        AmmDex::<T>::create_token_pool(
            RawOrigin::Signed(caller.clone()).into(),
            asset_a,
            asset_b,
            BENCH_AMOUNT.try_into().unwrap_or_default(),
            BENCH_AMOUNT.try_into().unwrap_or_default(),
            u64::MAX,
        )
        .expect("create_token_pool failed in benchmark setup");

        let pool_id = TokenPoolCount::<T>::get() - 1;
        let extra: u128 = n as u128 * 1_000_000_000_000; // n * 10^12
        let amount_a: BalanceOf<T> = (5_000_000_000_000 + extra).try_into().unwrap_or_default();
        let amount_b: BalanceOf<T> = (5_000_000_000_000 + extra).try_into().unwrap_or_default();

        #[extrinsic_call]
        add_token_liquidity(RawOrigin::Signed(caller), pool_id, amount_a, amount_b);

        let pool = TokenPools::<T>::get(pool_id).unwrap();
        assert!(pool.total_lp > 0u32.into());
    }

    #[benchmark]
    fn remove_token_liquidity() {
        let caller: T::AccountId = whitelisted_caller();
        fund_caller::<T>(&caller);
        let asset_a = AssetId::Native;
        let asset_b = AssetId::Custom(0);

        AmmDex::<T>::create_token_pool(
            RawOrigin::Signed(caller.clone()).into(),
            asset_a,
            asset_b,
            BENCH_AMOUNT.try_into().unwrap_or_default(),
            BENCH_AMOUNT.try_into().unwrap_or_default(),
            u64::MAX,
        )
        .expect("create_token_pool failed in benchmark setup");

        let pool_id = TokenPoolCount::<T>::get() - 1;
        let lp_amount: BalanceOf<T> = BENCH_LP_BURN.try_into().unwrap_or_default();

        #[extrinsic_call]
        remove_token_liquidity(RawOrigin::Signed(caller), pool_id, lp_amount);

        assert!(TokenPools::<T>::get(pool_id).is_some());
    }

    #[benchmark]
    fn swap_token() {
        let caller: T::AccountId = whitelisted_caller();
        fund_caller::<T>(&caller);
        let asset_a = AssetId::Native;
        let asset_b = AssetId::Custom(0);

        AmmDex::<T>::create_token_pool(
            RawOrigin::Signed(caller.clone()).into(),
            asset_a,
            asset_b,
            BENCH_AMOUNT.try_into().unwrap_or_default(),
            BENCH_AMOUNT.try_into().unwrap_or_default(),
            u64::MAX,
        )
        .expect("create_token_pool failed in benchmark setup");

        let pool_id = TokenPoolCount::<T>::get() - 1;
        let amount_in: BalanceOf<T> = BENCH_SWAP_IN.try_into().unwrap_or_default();
        let min_out: BalanceOf<T> = 0u32.into();

        #[extrinsic_call]
        swap_token(
            RawOrigin::Signed(caller),
            pool_id,
            asset_a,
            amount_in,
            min_out,
            BlockNumberFor::<T>::max_value(),
        );

        let pool = TokenPools::<T>::get(pool_id).unwrap();
        assert!(pool.reserve_a > 0u32.into());
    }

    impl_benchmark_test_suite!(
        AmmDex,
        crate::tests::new_test_ext_with_tokens(),
        crate::tests::Test,
    );
}
