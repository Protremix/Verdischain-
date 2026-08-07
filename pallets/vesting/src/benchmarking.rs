//! Benchmarking for pallet_vesting

#![cfg(feature = "runtime-benchmarks")]

use super::*;
use frame_support::traits::Currency;
use frame_benchmarking::{benchmarks, whitelisted_caller};
use frame_system::RawOrigin;

#[allow(dead_code)]
type BalanceOf<T> = <<T as Config>::Currency as Currency<<T as frame_system::Config>::AccountId>>::Balance;

benchmarks! {

    assign_vesting {
        let recipient: T::AccountId = whitelisted_caller();
        let label = b"team".to_vec();
        let amount = T::Currency::minimum_balance() * 1000u32.into();
        let _ = T::Currency::deposit_creating(&recipient, amount * 2u32.into());
    }: assign_vesting(RawOrigin::Root, recipient, label, amount)

    release_vested {
        let caller: T::AccountId = whitelisted_caller();
        let label = b"team".to_vec();
        let amount = T::Currency::minimum_balance() * 1000u32.into();
        let _ = T::Currency::deposit_creating(&caller, amount * 2u32.into());
        Pallet::<T>::assign_vesting(RawOrigin::Root.into(), caller.clone(), label, amount)?;
    }: _(RawOrigin::Signed(caller))

    check_transfer {
        let caller: T::AccountId = whitelisted_caller();
        let from: T::AccountId = whitelisted_caller();
        let label = b"team".to_vec();
        let amount = T::Currency::minimum_balance() * 1000u32.into();
        let _ = T::Currency::deposit_creating(&from, amount * 2u32.into());
        Pallet::<T>::assign_vesting(RawOrigin::Root.into(), from.clone(), label, amount / 2u32.into())?;
    }: _(RawOrigin::Signed(caller), from, amount / 4u32.into())

}
