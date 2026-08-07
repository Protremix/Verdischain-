//! Benchmarking for pallet_amm-dex

#![cfg(feature = "runtime-benchmarks")]

use super::*;
use frame_support::traits::Currency;
use frame_benchmarking::{benchmarks, whitelisted_caller};
use frame_system::RawOrigin;

type BalanceOf<T> = <<T as Config>::Currency as Currency<<T as frame_system::Config>::AccountId>>::Balance;

benchmarks! {

    create_pool {
        let caller: T::AccountId = whitelisted_caller();
        let token_a = b"TOKEN_A".to_vec();
        let token_b = b"TOKEN_B".to_vec();
        let amount_a = T::Currency::minimum_balance() * 1000u32.into();
        let amount_b = T::Currency::minimum_balance() * 2000u32.into();
        let _ = T::Currency::deposit_creating(&caller, amount_a + amount_b);
    }: _(RawOrigin::Signed(caller), token_a, token_b, amount_a, amount_b)

    add_liquidity {
        let caller: T::AccountId = whitelisted_caller();
        let token_a = b"TOKEN_A".to_vec();
        let token_b = b"TOKEN_B".to_vec();
        let amount_a = T::Currency::minimum_balance() * 1000u32.into();
        let amount_b = T::Currency::minimum_balance() * 2000u32.into();
        let _ = T::Currency::deposit_creating(&caller, (amount_a + amount_b) * 2u32.into());
        Pallet::<T>::create_pool(RawOrigin::Signed(caller.clone()).into(), token_a, token_b, amount_a, amount_b)?;
    }: _(RawOrigin::Signed(caller), 0u32, amount_a, amount_b)

    remove_liquidity {
        let caller: T::AccountId = whitelisted_caller();
        let token_a = b"TOKEN_A".to_vec();
        let token_b = b"TOKEN_B".to_vec();
        let amount_a = T::Currency::minimum_balance() * 1000u32.into();
        let amount_b = T::Currency::minimum_balance() * 2000u32.into();
        let _ = T::Currency::deposit_creating(&caller, (amount_a + amount_b) * 2u32.into());
        Pallet::<T>::create_pool(RawOrigin::Signed(caller.clone()).into(), token_a, token_b, amount_a, amount_b)?;
        Pallet::<T>::add_liquidity(RawOrigin::Signed(caller.clone()).into(), 0u32, amount_a, amount_b)?;
    }: _(RawOrigin::Signed(caller), 0u32, amount_a)

    swap {
        let caller: T::AccountId = whitelisted_caller();
        let token_a = b"TOKEN_A".to_vec();
        let token_b = b"TOKEN_B".to_vec();
        let amount_a = T::Currency::minimum_balance() * 1000u32.into();
        let amount_b = T::Currency::minimum_balance() * 2000u32.into();
        let _ = T::Currency::deposit_creating(&caller, (amount_a + amount_b) * 2u32.into());
        Pallet::<T>::create_pool(RawOrigin::Signed(caller.clone()).into(), token_a.clone(), token_b, amount_a, amount_b)?;
    }: _(RawOrigin::Signed(caller), 0u32, token_a, amount_a / 10u32.into(), BalanceOf::<T>::zero())

    get_price {
        let caller: T::AccountId = whitelisted_caller();
        let token_a = b"TOKEN_A".to_vec();
        let token_b = b"TOKEN_B".to_vec();
        let amount_a = T::Currency::minimum_balance() * 1000u32.into();
        let amount_b = T::Currency::minimum_balance() * 2000u32.into();
        let _ = T::Currency::deposit_creating(&caller, (amount_a + amount_b) * 2u32.into());
        Pallet::<T>::create_pool(RawOrigin::Signed(caller.clone()).into(), token_a, token_b, amount_a, amount_b)?;
    }: _(RawOrigin::Signed(caller), 0u32)

}
