#![cfg(feature = "runtime-benchmarks")]
#![allow(unused_variables, unused_imports, unused_must_use, clippy::all)]

use crate::pallet::*;
use frame_benchmarking::v2::*;
use frame_support::{traits::ConstU32, BoundedVec};
use frame_system::RawOrigin;

#[benchmarks]
mod benches {
    use super::*;
    use crate::pallet::*;

    #[benchmark]
    fn pause_pallet() {
        let pallet_name = b"Storage".to_vec();
        #[extrinsic_call]
        pause_pallet(RawOrigin::Root, pallet_name.clone());

        let name_bv: BoundedVec<u8, ConstU32<32>> = pallet_name.try_into().unwrap();
        assert!(PausedPallets::<T>::contains_key(&name_bv));
    }

    #[benchmark]
    fn unpause_pallet() {
        let pallet_name = b"Storage".to_vec();
        let _ = Pallet::<T>::pause_pallet(RawOrigin::Root.into(), pallet_name.clone());

        #[extrinsic_call]
        unpause_pallet(RawOrigin::Root, pallet_name.clone());

        let name_bv: BoundedVec<u8, ConstU32<32>> = pallet_name.try_into().unwrap();
        assert!(!PausedPallets::<T>::contains_key(&name_bv));
    }

    impl_benchmark_test_suite!(Pallet, crate::tests::new_test_ext(), crate::tests::Test,);
}
