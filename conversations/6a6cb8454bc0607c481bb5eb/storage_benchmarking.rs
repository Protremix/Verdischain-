//! Benchmarking for pallet_storage
#![cfg(feature = "runtime-benchmarks")]

use super::*;
use frame_benchmarking::benchmarks;
use frame_system::RawOrigin;

benchmarks! {
    register_storage {
        let caller: T::AccountId = frame_benchmarking::whitelisted_caller();
        let id: Vec<u8> = b"ipfs://QmTest123".to_vec();
        let backend = StorageBackend::Ipfs;
        let size_bytes: u64 = 1024;
        let blake3_hash: [u8; 32] = [0u8; 32];
    }: _(RawOrigin::Signed(caller), id, backend, size_bytes, blake3_hash)

    verify_storage {
        let caller: T::AccountId = frame_benchmarking::whitelisted_caller();
        let id: Vec<u8> = b"ipfs://QmTest123".to_vec();
        let backend = StorageBackend::Ipfs;
        let size_bytes: u64 = 1024;
        let blake3_hash: [u8; 32] = [0u8; 32];
        Pallet::<T>::register_storage(
            RawOrigin::Signed(caller.clone()).into(),
            id.clone(),
            backend,
            size_bytes,
            blake3_hash,
        )?;
    }: _(RawOrigin::Signed(caller), id, blake3_hash)

    register_provider {
        let caller: T::AccountId = frame_benchmarking::whitelisted_caller();
        let backend = StorageBackend::Ipfs;
        let endpoint: Vec<u8> = b"https://ipfs.protremix.com".to_vec();
    }: _(RawOrigin::Signed(caller), backend, endpoint)

    request_pin {
        let caller: T::AccountId = frame_benchmarking::whitelisted_caller();
        let id: Vec<u8> = b"ipfs://QmTest123".to_vec();
        let backend = StorageBackend::Ipfs;
        let size_bytes: u64 = 1024;
        let blake3_hash: [u8; 32] = [0u8; 32];
        Pallet::<T>::register_storage(
            RawOrigin::Signed(caller.clone()).into(),
            id.clone(),
            backend,
            size_bytes,
            blake3_hash,
        )?;
    }: _(RawOrigin::Signed(caller), id)

    remove_pin {
        let caller: T::AccountId = frame_benchmarking::whitelisted_caller();
        let id: Vec<u8> = b"ipfs://QmTest123".to_vec();
        let backend = StorageBackend::Ipfs;
        let size_bytes: u64 = 1024;
        let blake3_hash: [u8; 32] = [0u8; 32];
        Pallet::<T>::register_storage(
            RawOrigin::Signed(caller.clone()).into(),
            id.clone(),
            backend,
            size_bytes,
            blake3_hash,
        )?;
        Pallet::<T>::request_pin(RawOrigin::Signed(caller.clone()).into(), id.clone())?;
    }: _(RawOrigin::Signed(caller), id)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::tests::Test as T;
    use frame_benchmarking::impl_benchmark_test_suite;
    
    impl_benchmark_test_suite!(Pallet, crate::tests::new_test_ext(), crate::tests::Test);
}
