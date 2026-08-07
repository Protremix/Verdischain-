//! Benchmarking for pallet_dpos

#![cfg(feature = "runtime-benchmarks")]

use super::*;
use frame_support::traits::Currency;
use frame_benchmarking::{benchmarks, whitelisted_caller};
use frame_system::RawOrigin;

#[allow(dead_code)]
type BalanceOf<T> = <<T as Config>::Currency as Currency<<T as frame_system::Config>::AccountId>>::Balance;

benchmarks! {

    register_validator {
        let caller: T::AccountId = whitelisted_caller();
        let _ = T::Currency::deposit_creating(&caller, T::MinStake::get() * 2u32.into());
    }: _(RawOrigin::Signed(caller), 80u8, b"Solar".to_vec())

    unregister_validator {
        let caller: T::AccountId = whitelisted_caller();
        let _ = T::Currency::deposit_creating(&caller, T::MinStake::get() * 2u32.into());
        Pallet::<T>::register_validator(RawOrigin::Signed(caller.clone()).into(), 80u8, b"Solar".to_vec())?;
    }: _(RawOrigin::Signed(caller))

    vote {
        let caller: T::AccountId = whitelisted_caller();
        let validator: T::AccountId = whitelisted_caller();
        let _ = T::Currency::deposit_creating(&validator, T::MinStake::get() * 2u32.into());
        let _ = T::Currency::deposit_creating(&caller, T::MinStake::get() * 10u32.into());
        Pallet::<T>::register_validator(RawOrigin::Signed(validator.clone()).into(), 80u8, b"Solar".to_vec())?;
    }: _(RawOrigin::Signed(caller), validator, T::MinStake::get())

    unvote {
        let caller: T::AccountId = whitelisted_caller();
        let validator: T::AccountId = whitelisted_caller();
        let _ = T::Currency::deposit_creating(&validator, T::MinStake::get() * 2u32.into());
        let _ = T::Currency::deposit_creating(&caller, T::MinStake::get() * 10u32.into());
        Pallet::<T>::register_validator(RawOrigin::Signed(validator.clone()).into(), 80u8, b"Solar".to_vec())?;
        Pallet::<T>::vote(RawOrigin::Signed(caller.clone()).into(), validator.clone(), T::MinStake::get())?;
    }: _(RawOrigin::Signed(caller), validator)

    slash_validator {
        let validator: T::AccountId = whitelisted_caller();
        let _ = T::Currency::deposit_creating(&validator, T::MinStake::get() * 2u32.into());
        Pallet::<T>::register_validator(RawOrigin::Signed(validator.clone()).into(), 80u8, b"Solar".to_vec())?;
    }: _(RawOrigin::Root, validator, T::MinStake::get() / 2u32.into(), b"Misbehavior".to_vec())

    update_green_score {
        let caller: T::AccountId = whitelisted_caller();
        let _ = T::Currency::deposit_creating(&caller, T::MinStake::get() * 2u32.into());
        Pallet::<T>::register_validator(RawOrigin::Signed(caller.clone()).into(), 80u8, b"Solar".to_vec())?;
    }: _(RawOrigin::Signed(caller), 90u8)

}
