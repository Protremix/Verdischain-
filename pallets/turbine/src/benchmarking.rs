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
    fn register_shard() {
        let caller: T::AccountId = whitelisted_caller();
        #[extrinsic_call]
        register_shard(
            RawOrigin::Signed(caller.clone()),
            1,
            0,
            4,
        );

        assert!(TurbineTotalShards::<T>::get() > 0);
    }

    #[benchmark]
    fn rebuild_tree() {
        #[extrinsic_call]
        rebuild_tree(RawOrigin::Root, 21);

        assert_eq!(TurbineValidatorCount::<T>::get(), 21);
    }

    #[benchmark]
    fn mark_block_propagated() {
        let caller: T::AccountId = whitelisted_caller();
        #[extrinsic_call]
        mark_block_propagated(RawOrigin::Signed(caller.clone()), 1);

        assert!(TurbineTotalBlocks::<T>::get() > 0);
    }

    impl_benchmark_test_suite!(Pallet, crate::tests::new_test_ext(), crate::tests::Test,);
}
