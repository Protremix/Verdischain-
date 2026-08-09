//! Benchmarking for the Verdis AmmDex pallet
#![cfg(feature = "runtime-benchmarks")]

use crate::pallet::{
    AssetId, Config, Pallet as AmmDex, PoolCount, Pools, TokenHandler, TokenPoolCount, TokenPools,
};
use frame_benchmarking::v2::*;
use frame_support::{traits::ConstU32, BoundedVec};
use frame_system::RawOrigin;
use sp_std::vec;

type BalanceOf<T> = <<T as Config>::Currency as frame_support::traits::Currency<
    <T as frame_system::Config>::AccountId,
>>::Balance;

fn make_token_bytes(prefix: u8) -> BoundedVec<u8, ConstU32<32>> {
    let bytes = vec![prefix; 4];
    BoundedVec::try_from(bytes).expect("4 bytes fits in 32")
}

/// Fund the caller with sufficient balance for benchmark operations
fn fund_caller<T: Config>(caller: &T::AccountId) {
    let amount: BalanceOf<T> = 10_000_000_000u128.try_into().unwrap_or_default();
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
        let amount_a: BalanceOf<T> = 1_000_000u32.into();
        let amount_b: BalanceOf<T> = 1_000_000u32.into();

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
            1_000_000u32.into(),
            1_000_000u32.into(),
        );

        let pool_id = PoolCount::<T>::get() - 1;
        let amount_a: BalanceOf<T> = (500_000u32 + n * 10_000).into();
        let amount_b: BalanceOf<T> = (500_000u32 + n * 10_000).into();

        #[extrinsic_call]
        add_liquidity(RawOrigin::Signed(caller), pool_id, amount_a, amount_b);

        let pool = Pools::<T>::get(pool_id).unwrap();
        assert!(pool.total_lp > 1_000_000u32.into());
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
            1_000_000u32.into(),
            1_000_000u32.into(),
        );

        let pool_id = PoolCount::<T>::get() - 1;
        let lp_amount: BalanceOf<T> = 100_000u32.into();

        #[extrinsic_call]
        remove_liquidity(RawOrigin::Signed(caller), pool_id, lp_amount);

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
            1_000_000u32.into(),
            1_000_000u32.into(),
        );

        let pool_id = PoolCount::<T>::get() - 1;
        let amount_in: BalanceOf<T> = 10_000u32.into();
        let min_out: BalanceOf<T> = 0u32.into();

        #[extrinsic_call]
        swap(
            RawOrigin::Signed(caller),
            pool_id,
            token_a.to_vec(),
            amount_in,
            min_out,
        );

        let pool = Pools::<T>::get(pool_id).unwrap();
        assert!(pool.reserve_a > 1_000_000u32.into());
    }

    #[benchmark]
    fn create_token_pool() {
        let caller: T::AccountId = whitelisted_caller();
        fund_caller::<T>(&caller);
        let asset_a = AssetId::Native;
        let asset_b = AssetId::Custom(0);
        let amount_a: BalanceOf<T> = 1_000_000u32.into();
        let amount_b: BalanceOf<T> = 1_000_000u32.into();

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
        // Debug: check caller address and balances

        AmmDex::<T>::create_token_pool(
            RawOrigin::Signed(caller.clone()).into(),
            asset_a,
            asset_b,
            1_000_000u32.into(),
            1_000_000u32.into(),
        )
        .expect("create_token_pool failed in benchmark setup");

        let pool_id = TokenPoolCount::<T>::get() - 1;
        let amount_a: BalanceOf<T> = (500_000u32 + n * 10_000).into();
        let amount_b: BalanceOf<T> = (500_000u32 + n * 10_000).into();

        #[extrinsic_call]
        add_token_liquidity(RawOrigin::Signed(caller), pool_id, amount_a, amount_b);

        let pool = TokenPools::<T>::get(pool_id).unwrap();
        assert!(pool.total_lp > 1_000_000u32.into());
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
            1_000_000u32.into(),
            1_000_000u32.into(),
        )
        .expect("create_token_pool failed in benchmark setup");

        let pool_id = TokenPoolCount::<T>::get() - 1;
        let lp_amount: BalanceOf<T> = 100_000u32.into();

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
            1_000_000u32.into(),
            1_000_000u32.into(),
        )
        .expect("create_token_pool failed in benchmark setup");

        let pool_id = TokenPoolCount::<T>::get() - 1;
        let amount_in: BalanceOf<T> = 10_000u32.into();
        let min_out: BalanceOf<T> = 0u32.into();

        #[extrinsic_call]
        swap_token(
            RawOrigin::Signed(caller),
            pool_id,
            asset_a,
            amount_in,
            min_out,
        );

        let pool = TokenPools::<T>::get(pool_id).unwrap();
        assert!(pool.reserve_a > 1_000_000u32.into());
    }

    impl_benchmark_test_suite!(
        AmmDex,
        crate::tests::new_test_ext_with_tokens(),
        crate::tests::Test,
    );
}
