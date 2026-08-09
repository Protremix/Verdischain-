//! Benchmarking for the Verdis Tokenomics pallet
#![cfg(feature = "runtime-benchmarks")]

use super::*;
use crate::pallet::{
    Config, ConsentGiven, Distribution, DistributionCategory, Pallet, PresalePrice, PresaleSold,
};
use frame_benchmarking::v2::*;
use frame_support::{
    traits::{ConstU32, Currency, Get},
    BoundedVec,
};
use frame_system::RawOrigin;
use sp_runtime::traits::AccountIdConversion;
use sp_runtime::traits::TryConvert;

type BalanceOf<T> =
    <<T as Config>::Currency as Currency<<T as frame_system::Config>::AccountId>>::Balance;

#[benchmarks]
mod benches {
    use super::*;

    #[benchmark]
    fn give_consent() {
        let caller: T::AccountId = whitelisted_caller();

        #[extrinsic_call]
        give_consent(RawOrigin::Signed(caller.clone()));

        assert!(ConsentGiven::<T>::get(&caller).unwrap_or(false));
    }

    #[benchmark]
    fn purchase() {
        let caller: T::AccountId = whitelisted_caller();
        ConsentGiven::<T>::insert(&caller, true);

        let treasury: T::AccountId = T::PalletId::get().into_account_truncating();
        // Use proper scale: UNITS = 10^9, ED = 10^9
        // amount = 1000 VRDX = 10^12, treasury needs >= amount + ED
        let amount: BalanceOf<T> = 1_000_000_000_000u128.try_into().unwrap_or_default(); // 10^12
        let treasury_fund: BalanceOf<T> = 10_000_000_000_000u128.try_into().unwrap_or_default(); // 10^13
        let caller_fund: BalanceOf<T> = 1_000_000_000_000_000u128.try_into().unwrap_or_default(); // 10^15

        let _ = T::Currency::make_free_balance_be(&treasury, treasury_fund);
        let _ = T::Currency::make_free_balance_be(&caller, caller_fund);

        PresalePrice::<T>::put(500u32);

        #[extrinsic_call]
        purchase(RawOrigin::Signed(caller), amount);

        assert!(PresaleSold::<T>::get() > 0u32.into());
    }

    #[benchmark]
    fn update_presale_price() {
        let price = 500u32;

        #[extrinsic_call]
        update_presale_price(RawOrigin::Root, price);

        assert_eq!(PresalePrice::<T>::get(), price);
    }

    #[benchmark]
    fn release_distribution() {
        let category_name = b"Community".to_vec();
        let cat_bv: BoundedVec<u8, ConstU32<32>> = category_name.clone().try_into().unwrap();
        let total_cat_amount: BalanceOf<T> = 1_000_000_000_000u128.try_into().unwrap_or_default(); // 10^12

        let cat = DistributionCategory {
            name: cat_bv.clone(),
            amount: total_cat_amount,
            percentage: 35,
            vesting_days: 0,
            cliff_days: 0,
            released: 0u32.into(),
        };
        Distribution::<T>::insert(&cat_bv, cat);

        let release_amount: BalanceOf<T> = 100_000_000_000u128.try_into().unwrap_or_default(); // 10^11

        #[extrinsic_call]
        release_distribution(RawOrigin::Root, category_name, release_amount);

        let updated = Distribution::<T>::get(&cat_bv).unwrap();
        assert_eq!(updated.released, release_amount);
    }

    impl_benchmark_test_suite!(Pallet, crate::tests::new_test_ext(), crate::tests::Test,);
}
