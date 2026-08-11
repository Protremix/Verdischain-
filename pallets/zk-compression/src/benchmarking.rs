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
    fn create_tree() {
        let caller: T::AccountId = whitelisted_caller();
        #[extrinsic_call]
        create_tree(RawOrigin::Signed(caller.clone()), 20);

        assert!(ZkTotalTrees::<T>::get() > 0);
    }

    #[benchmark]
    fn compress_account() {
        let caller: T::AccountId = whitelisted_caller();
        let _ = Pallet::<T>::create_tree(RawOrigin::Signed(caller.clone()).into(), 20);

        #[extrinsic_call]
        compress_account(
            RawOrigin::Signed(caller.clone()),
            0,
            1024,
        );

        assert!(ZkTotalCompressed::<T>::get() > 0);
    }

    #[benchmark]
    fn verify_proof() {
        let caller: T::AccountId = whitelisted_caller();
        let _ = Pallet::<T>::create_tree(RawOrigin::Signed(caller.clone()).into(), 20);
        let _ = Pallet::<T>::compress_account(
            RawOrigin::Signed(caller.clone()).into(),
            0,
            1024,
        );

        #[extrinsic_call]
        verify_proof(
            RawOrigin::Signed(caller.clone()),
            0,
            0,
            [0u8; 32],
        );
    }

    impl_benchmark_test_suite!(Pallet, crate::tests::new_test_ext(), crate::tests::Test,);
}
