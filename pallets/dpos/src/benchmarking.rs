//! Benchmarking for the Verdis DPoS pallet.
#![cfg(feature = "runtime-benchmarks")]

use crate::pallet::*;
use frame_benchmarking::v2::*;
use frame_support::traits::{Currency, Get};
use frame_system::RawOrigin;
use sp_runtime::traits::Saturating;
use sp_std::vec;

type BalanceOf<T> =
    <<T as Config>::Currency as Currency<<T as frame_system::Config>::AccountId>>::Balance;

fn fund<T: Config>(who: &T::AccountId, amount: BalanceOf<T>) {
    let _ = T::Currency::make_free_balance_be(who, amount);
}

fn register<T: Config>(who: &T::AccountId) {
    let funding = T::MinStake::get().saturating_mul(100u32.into());
    fund::<T>(who, funding);
    assert!(Pallet::<T>::register_validator(
        RawOrigin::Signed(who.clone()).into(),
        95,
        vec![b'S'; 64],
    )
    .is_ok());
}

#[benchmarks]
mod benches {
    use super::*;

    #[benchmark]
    fn register_validator() {
        let caller: T::AccountId = whitelisted_caller();
        let funding = T::MinStake::get().saturating_mul(100u32.into());
        fund::<T>(&caller, funding);

        #[extrinsic_call]
        register_validator(RawOrigin::Signed(caller.clone()), 95, vec![b'S'; 64]);

        assert!(Validators::<T>::contains_key(&caller));
    }

    #[benchmark]
    fn unregister_validator() {
        let caller: T::AccountId = whitelisted_caller();
        register::<T>(&caller);

        #[extrinsic_call]
        unregister_validator(RawOrigin::Signed(caller.clone()));

        assert!(!Validators::<T>::contains_key(&caller));
    }

    #[benchmark]
    fn vote() {
        let validator: T::AccountId = account("validator", 0, 0);
        let voter: T::AccountId = whitelisted_caller();
        register::<T>(&validator);
        let amount = T::MinStake::get();
        fund::<T>(&voter, amount.saturating_mul(100u32.into()));

        #[extrinsic_call]
        vote(RawOrigin::Signed(voter.clone()), validator.clone(), amount);

        assert_eq!(Votes::<T>::get(&voter).map(|v| v.len()), Some(1));
    }

    #[benchmark]
    fn unvote() {
        let validator: T::AccountId = account("validator", 0, 0);
        let voter: T::AccountId = whitelisted_caller();
        register::<T>(&validator);
        let amount = T::MinStake::get();
        fund::<T>(&voter, amount.saturating_mul(100u32.into()));
        assert!(Pallet::<T>::vote(
            RawOrigin::Signed(voter.clone()).into(),
            validator.clone(),
            amount,
        )
        .is_ok());

        #[extrinsic_call]
        unvote(RawOrigin::Signed(voter.clone()), validator.clone());

        assert!(Votes::<T>::get(&voter)
            .map(|v| v.is_empty())
            .unwrap_or(true));
        assert_eq!(UnbondingQueue::<T>::get(&voter).map(|q| q.len()), Some(1));
    }

    #[benchmark]
    fn withdraw_unbonded() {
        let validator: T::AccountId = account("validator", 0, 0);
        let voter: T::AccountId = whitelisted_caller();
        register::<T>(&validator);
        let amount = T::MinStake::get();
        fund::<T>(&voter, amount.saturating_mul(100u32.into()));
        assert!(Pallet::<T>::vote(
            RawOrigin::Signed(voter.clone()).into(),
            validator.clone(),
            amount,
        )
        .is_ok());
        assert!(Pallet::<T>::unvote(RawOrigin::Signed(voter.clone()).into(), validator,).is_ok());
        let unlock = T::UnbondingPeriod::get().saturating_add(1);
        frame_system::Pallet::<T>::set_block_number(unlock.into());

        #[extrinsic_call]
        withdraw_unbonded(RawOrigin::Signed(voter.clone()));

        assert!(!UnbondingQueue::<T>::contains_key(&voter));
    }

    #[benchmark]
    fn slash_validator() {
        let validator: T::AccountId = account("validator", 0, 0);
        register::<T>(&validator);
        let penalty = T::MinStake::get();

        #[extrinsic_call]
        slash_validator(RawOrigin::Root, validator.clone(), penalty, vec![b'M'; 64]);

        assert!(Validators::<T>::get(&validator)
            .map(|v| v.slashed)
            .unwrap_or(false));
    }

    #[benchmark]
    fn update_green_score() {
        let validator: T::AccountId = whitelisted_caller();
        register::<T>(&validator);

        #[extrinsic_call]
        update_green_score(RawOrigin::Signed(validator.clone()), 100);

        assert_eq!(
            Validators::<T>::get(&validator).map(|v| v.green_score),
            Some(100)
        );
    }

    impl_benchmark_test_suite!(Pallet, crate::tests::new_test_ext(), crate::tests::Test,);
}
