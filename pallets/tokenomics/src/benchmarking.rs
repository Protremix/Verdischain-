//! Benchmarking for pallet_tokenomics

#![cfg(feature = "runtime-benchmarks")]

use super::*;
use frame_support::traits::Currency;
use frame_benchmarking::{benchmarks, whitelisted_caller};
use frame_system::RawOrigin;

#[allow(dead_code)]
type BalanceOf<T> = <<T as Config>::Currency as Currency<<T as frame_system::Config>::AccountId>>::Balance;

benchmarks! {

    give_consent {
        let caller: T::AccountId = whitelisted_caller();
    }: _(RawOrigin::Signed(caller))

    purchase {
        let caller: T::AccountId = whitelisted_caller();
        let amount = T::Currency::minimum_balance() * 1000u32.into();
        let _ = T::Currency::deposit_creating(&caller, amount * 2u32.into());
        Pallet::<T>::give_consent(RawOrigin::Signed(caller.clone()).into())?;
    }: _(RawOrigin::Signed(caller), amount)

    update_presale_price {
        let price_bps: u32 = 500;
    }: update_presale_price(RawOrigin::Root, price_bps)

    release_distribution {
        let recipient: T::AccountId = whitelisted_caller();
        let category = b"treasury".to_vec();
        let amount = T::Currency::minimum_balance() * 1000u32.into();
        let _ = T::Currency::deposit_creating(&recipient, amount * 2u32.into());
    }: release_distribution(RawOrigin::Root, category, amount)

}
