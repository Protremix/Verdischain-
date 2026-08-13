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
    fn create_client() {
        let caller: T::AccountId = whitelisted_caller();
        #[extrinsic_call]
        create_client(RawOrigin::Root, 1, 100, 86400);

        assert!(IbcClients::<T>::contains_key(1));
    }

    impl_benchmark_test_suite!(Pallet, crate::tests::new_test_ext(), crate::tests::Test,);
}
