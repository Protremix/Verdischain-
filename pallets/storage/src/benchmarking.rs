#![cfg(feature = "runtime-benchmarks")]
#![allow(unused_variables, unused_imports, unused_must_use, clippy::all)]

use crate::pallet::*;
use frame_benchmarking::v2::*;
use frame_support::{traits::ConstU32, BoundedVec};
use frame_system::RawOrigin;
use sp_std::vec;

#[benchmarks]
mod benches {
    use super::*;
    use crate::pallet::*;

    #[benchmark]
    fn register_storage() {
        let caller: T::AccountId = whitelisted_caller();
        let id = b"doc-1".to_vec();
        let hash = [1u8; 32];

        #[extrinsic_call]
        register_storage(
            RawOrigin::Signed(caller.clone()),
            id.clone(),
            StorageBackend::Ipfs,
            1024,
            hash,
        );

        let id_bv: BoundedVec<u8, ConstU32<64>> = id.try_into().unwrap();
        assert!(StorageRecords::<T>::contains_key(&id_bv));
    }

    #[benchmark]
    fn verify_storage() {
        let caller: T::AccountId = whitelisted_caller();
        let id = b"doc-1".to_vec();
        let hash = [1u8; 32];

        let _ = Pallet::<T>::register_storage(
            RawOrigin::Signed(caller.clone()).into(),
            id.clone(),
            StorageBackend::Ipfs,
            1024,
            hash,
        );

        #[extrinsic_call]
        verify_storage(RawOrigin::Signed(caller.clone()), id.clone(), hash);

        let id_bv: BoundedVec<u8, ConstU32<64>> = id.try_into().unwrap();
        assert!(StorageRecords::<T>::contains_key(&id_bv));
    }

    #[benchmark]
    fn register_provider() {
        let caller: T::AccountId = whitelisted_caller();

        #[extrinsic_call]
        register_provider(
            RawOrigin::Signed(caller.clone()),
            StorageBackend::Ipfs,
            b"https://pinata.cloud".to_vec(),
        );

        assert!(StorageProviders::<T>::contains_key(&caller));
    }

    #[benchmark]
    fn request_pin() {
        let caller: T::AccountId = whitelisted_caller();
        let id = b"doc-1".to_vec();
        let hash = [1u8; 32];

        let _ = Pallet::<T>::register_storage(
            RawOrigin::Signed(caller.clone()).into(),
            id.clone(),
            StorageBackend::Ipfs,
            1024,
            hash,
        );

        #[extrinsic_call]
        request_pin(RawOrigin::Signed(caller.clone()), id.clone());

        let id_bv: BoundedVec<u8, ConstU32<64>> = id.try_into().unwrap();
        assert!(PinRequests::<T>::contains_key(&id_bv));
    }

    #[benchmark]
    fn remove_pin() {
        let caller: T::AccountId = whitelisted_caller();
        let id = b"doc-1".to_vec();
        let hash = [1u8; 32];

        let _ = Pallet::<T>::register_storage(
            RawOrigin::Signed(caller.clone()).into(),
            id.clone(),
            StorageBackend::Ipfs,
            1024,
            hash,
        );
        let _ = Pallet::<T>::request_pin(
            RawOrigin::Signed(caller.clone()).into(),
            id.clone(),
        );

        #[extrinsic_call]
        remove_pin(RawOrigin::Signed(caller.clone()), id.clone());

        let id_bv: BoundedVec<u8, ConstU32<64>> = id.try_into().unwrap();
        assert!(!PinRequests::<T>::contains_key(&id_bv));
    }

    #[benchmark]
    fn delete_record() {
        let caller: T::AccountId = whitelisted_caller();
        let id = b"doc-1".to_vec();
        let hash = [1u8; 32];

        let _ = Pallet::<T>::register_storage(
            RawOrigin::Signed(caller.clone()).into(),
            id.clone(),
            StorageBackend::Ipfs,
            1024,
            hash,
        );

        #[extrinsic_call]
        delete_record(RawOrigin::Signed(caller.clone()), id.clone());

        let id_bv: BoundedVec<u8, ConstU32<64>> = id.try_into().unwrap();
        assert!(!StorageRecords::<T>::contains_key(&id_bv));
    }

    #[benchmark]
    fn cleanup_expired() {
        let caller: T::AccountId = whitelisted_caller();
        let id = b"doc-1".to_vec();
        let hash = [1u8; 32];

        let _ = Pallet::<T>::register_storage(
            RawOrigin::Signed(caller.clone()).into(),
            id.clone(),
            StorageBackend::Ipfs,
            1024,
            hash,
        );

        #[extrinsic_call]
        cleanup_expired(RawOrigin::Signed(caller.clone()), vec![id.clone()]);

        let id_bv: BoundedVec<u8, ConstU32<64>> = id.try_into().unwrap();
        assert!(!StorageRecords::<T>::contains_key(&id_bv));
    }

    impl_benchmark_test_suite!(Pallet, crate::tests::new_test_ext(), crate::tests::Test,);
}
