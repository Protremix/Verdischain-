//! Benchmarking for the Verdis Vesting pallet
#![cfg(feature = "runtime-benchmarks")]

use super::*;
use frame_benchmarking::v2::*;
use frame_support::{
    traits::{tokens::WithdrawReasons, Currency, LockableCurrency},
    BoundedVec,
};
use frame_system::RawOrigin;
use sp_runtime::traits::Saturating;
use sp_std::vec;

type BalanceOf<T> =
    <<T as Config>::Currency as Currency<<T as frame_system::Config>::AccountId>>::Balance;

#[benchmarks]
mod benches {
    use super::*;

    #[benchmark]
    fn add_schedule(s: Linear<1, 64>) {
        let label = vec![b'a'; s as usize];
        let total_amount: BalanceOf<T> = 1_000_000u32.into();
        let vesting_days = 60u32;
        let cliff_days = 30u32;

        #[extrinsic_call]
        add_schedule(
            RawOrigin::Root,
            label.clone(),
            total_amount,
            vesting_days,
            cliff_days,
        );

        let label_bv: BoundedVec<u8, ConstU32<64>> = label.try_into().unwrap();
        assert!(Schedules::<T>::contains_key(&label_bv));
    }

    #[benchmark]
    fn assign_vesting(s: Linear<1, 15>) {
        let target: T::AccountId = account("target", 0, 0);
        let schedule_label = b"schedule_for_assign".to_vec();
        let amount: BalanceOf<T> = 1_000_000u32.into();

        let label_bv: BoundedVec<u8, ConstU32<64>> = schedule_label.clone().try_into().unwrap();
        let schedule = VestingSchedule {
            label: label_bv.clone(),
            total_amount: amount,
            vesting_days: 60,
            cliff_days: 30,
        };
        Schedules::<T>::insert(label_bv.clone(), schedule);

        // Fund the target account so the lock can be set
        let funding = amount.saturating_mul(100u32.into());
        let _ = T::Currency::make_free_balance_be(&target, funding);

        let mut vestings = BoundedVec::default();
        for _ in 0..(s - 1) {
            let entry = UserVestingEntry {
                schedule: label_bv.clone(),
                total_amount: amount,
                released: BalanceOf::<T>::zero(),
                start_block: frame_system::Pallet::<T>::block_number(),
                vested: BalanceOf::<T>::zero(),
            };
            assert!(vestings.try_push(entry).is_ok());
        }
        UserVestings::<T>::insert(&target, vestings);

        #[extrinsic_call]
        assign_vesting(RawOrigin::Root, target.clone(), schedule_label, amount);

        assert_eq!(UserVestings::<T>::get(&target).unwrap().len(), s as usize);
    }

    #[benchmark]
    fn release_vested(s: Linear<1, 16>) {
        let caller: T::AccountId = whitelisted_caller();
        let schedule_label = b"release_schedule".to_vec();
        let label_bv: BoundedVec<u8, ConstU32<64>> = schedule_label.clone().try_into().unwrap();
        let amount: BalanceOf<T> = 1_000_000u32.into();

        let schedule = VestingSchedule {
            label: label_bv.clone(),
            total_amount: amount,
            vesting_days: 60,
            cliff_days: 30,
        };
        Schedules::<T>::insert(label_bv.clone(), schedule);

        let mut vestings = BoundedVec::default();
        let mut total_locked = BalanceOf::<T>::zero();
        for _ in 0..s {
            let entry = UserVestingEntry {
                schedule: label_bv.clone(),
                total_amount: amount,
                released: BalanceOf::<T>::zero(),
                start_block: 0u32.into(),
                vested: BalanceOf::<T>::zero(),
            };
            assert!(vestings.try_push(entry).is_ok());
            total_locked = total_locked.saturating_add(amount);
        }
        // Fund the caller account so the lock can be set
        let funding = total_locked.saturating_mul(100u32.into());
        let _ = T::Currency::make_free_balance_be(&caller, funding);
        UserVestings::<T>::insert(&caller, vestings);
        LockedBalances::<T>::insert(&caller, total_locked);
        T::Currency::set_lock(
            VESTING_LOCK_ID,
            &caller,
            total_locked,
            WithdrawReasons::TRANSFER,
        );

        let blocks_per_day = 86_400_000u32 / 5000u32;
        let target_block = 45u32 * blocks_per_day;
        frame_system::Pallet::<T>::set_block_number(target_block.into());

        #[extrinsic_call]
        release_vested(RawOrigin::Signed(caller.clone()));

        assert!(LockedBalances::<T>::get(&caller) < total_locked);
    }

    impl_benchmark_test_suite!(Pallet, crate::tests::new_test_ext(), crate::tests::Test,);
}
