#![cfg(feature = "runtime-benchmarks")]
#![allow(unused_variables, unused_imports, unused_must_use, clippy::all)]

use crate::pallet::*;
use frame_benchmarking::v2::*;
use frame_system::RawOrigin;

#[benchmarks]
mod benches {
    use super::*;
    use crate::pallet::*;

    #[benchmark]
    fn create_table() {
        let caller: T::AccountId = whitelisted_caller();
        #[extrinsic_call]
        create_table(RawOrigin::Signed(caller.clone()));

        assert!(AltTotalTables::<T>::get() > 0);
    }

    #[benchmark]
    fn add_address() {
        let caller: T::AccountId = whitelisted_caller();
        let _ = Pallet::<T>::create_table(RawOrigin::Signed(caller.clone()).into());

        #[extrinsic_call]
        add_address(RawOrigin::Signed(caller.clone()), 0);

        assert!(AltTotalAddresses::<T>::get() > 0);
    }

    #[benchmark]
    fn deactivate_table() {
        let caller: T::AccountId = whitelisted_caller();
        let _ = Pallet::<T>::create_table(RawOrigin::Signed(caller.clone()).into());

        #[extrinsic_call]
        deactivate_table(RawOrigin::Signed(caller.clone()), 0);

        assert!(!TableActive::<T>::get(0));
    }

    #[benchmark]
    fn lookup_address() {
        let caller: T::AccountId = whitelisted_caller();
        let _ = Pallet::<T>::create_table(RawOrigin::Signed(caller.clone()).into());

        #[extrinsic_call]
        lookup_address(RawOrigin::Signed(caller.clone()), 0, 0);

        assert!(AltTotalLookups::<T>::get() > 0);
    }

    impl_benchmark_test_suite!(Pallet, crate::tests::new_test_ext(), crate::tests::Test,);
}
