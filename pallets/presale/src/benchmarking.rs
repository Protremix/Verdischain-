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
    fn activate_round() {
        #[extrinsic_call]
        activate_round(RawOrigin::Root, 0);

        // Round may or may not exist depending on genesis
    }

    #[benchmark]
    fn deactivate_round() {
        let _ = Pallet::<T>::activate_round(RawOrigin::Root.into(), 0);

        #[extrinsic_call]
        deactivate_round(RawOrigin::Root, 0);
    }

    #[benchmark]
    fn set_paused() {
        #[extrinsic_call]
        set_paused(RawOrigin::Root, true);

        assert!(Paused::<T>::get());
    }

    impl_benchmark_test_suite!(Pallet, crate::tests::new_test_ext(), crate::tests::Test,);
}
