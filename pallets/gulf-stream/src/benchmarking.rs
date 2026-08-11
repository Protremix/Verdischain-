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
    fn forward_transaction() {
        let caller: T::AccountId = whitelisted_caller();
        let tx_hash = [1u8; 32];

        #[extrinsic_call]
        forward_transaction(
            RawOrigin::Signed(caller.clone()),
            tx_hash,
            b"validator-1".to_vec(),
            1024,
        );

        assert!(PendingForwards::<T>::contains_key(&tx_hash));
    }

    #[benchmark]
    fn mark_included() {
        let caller: T::AccountId = whitelisted_caller();
        let tx_hash = [1u8; 32];

        let _ = Pallet::<T>::forward_transaction(
            RawOrigin::Signed(caller.clone()).into(),
            tx_hash,
            b"validator-1".to_vec(),
            1024,
        );

        #[extrinsic_call]
        mark_included(RawOrigin::Signed(caller.clone()), tx_hash, 1, 100);

        assert!(!PendingForwards::<T>::contains_key(&tx_hash));
    }

    #[benchmark]
    fn expire_transaction() {
        let caller: T::AccountId = whitelisted_caller();
        let tx_hash = [1u8; 32];

        let _ = Pallet::<T>::forward_transaction(
            RawOrigin::Signed(caller.clone()).into(),
            tx_hash,
            b"validator-1".to_vec(),
            1024,
        );

        #[extrinsic_call]
        expire_transaction(RawOrigin::Signed(caller.clone()), tx_hash);

        assert!(!PendingForwards::<T>::contains_key(&tx_hash));
    }

    impl_benchmark_test_suite!(Pallet, crate::tests::new_test_ext(), crate::tests::Test,);
}
