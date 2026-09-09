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
    fn create_batch() {
        let caller: T::AccountId = whitelisted_caller();
        #[extrinsic_call]
        create_batch(RawOrigin::Signed(caller.clone()), 10, false);

        assert!(SealevelTotalBatches::<T>::get() > 0);
    }

    #[benchmark]
    fn report_execution() {
        let caller: T::AccountId = whitelisted_caller();
        let _ = Pallet::<T>::create_batch(RawOrigin::Signed(caller.clone()).into(), 10, false);

        #[extrinsic_call]
        report_execution(RawOrigin::Signed(caller.clone()), 0, 1000, 10);

        assert!(SealevelTotalTxs::<T>::get() > 0);
    }

    #[benchmark]
    fn report_conflict() {
        let caller: T::AccountId = whitelisted_caller();
        let _ = Pallet::<T>::create_batch(RawOrigin::Signed(caller.clone()).into(), 10, true);

        #[extrinsic_call]
        report_conflict(RawOrigin::Signed(caller.clone()), 0, 0, 1);

        assert!(SealevelConflicts::<T>::get() > 0);
    }

    impl_benchmark_test_suite!(Pallet, crate::tests::new_test_ext(), crate::tests::Test,);
}
