//! Benchmarking for pallet-poh
#![cfg(feature = "runtime-benchmarks")]
#![allow(unused_imports, clippy::all)]

use super::*;
use frame_benchmarking::v2::*;
use frame_system::RawOrigin;
use crate::Pallet as Poh;

#[benchmarks]
mod benches {
    use super::*;

    #[benchmark]
    fn record_block() {
        let caller: T::AccountId = whitelisted_caller();
        #[extrinsic_call]
        record_block(RawOrigin::Signed(caller));

        let current_block = frame_system::Pallet::<T>::block_number();
        assert!(PohHashes::<T>::contains_key(current_block));
    }

    #[benchmark]
    fn set_config() {
        let seed = [1u8; 32];
        let last_hash = [2u8; 32];
        #[extrinsic_call]
        set_config(RawOrigin::Root, seed, last_hash);

        let config = PohConfigVal::<T>::get();
        assert_eq!(config.seed, seed);
        assert_eq!(config.last_hash, last_hash);
    }

    #[benchmark]
    fn tick_extrinsic() {
        let caller: T::AccountId = whitelisted_caller();
        #[extrinsic_call]
        tick_extrinsic(RawOrigin::Signed(caller));

        assert!(PohTick::<T>::get() > 0);
    }

    impl_benchmark_test_suite!(Poh, crate::tests::new_test_ext(), crate::tests::Test);
}
