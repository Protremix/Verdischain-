//! Benchmarking for pallet_evm
#![cfg(feature = "runtime-benchmarks")]

use super::*;
use frame_benchmarking::benchmarks;
use frame_system::RawOrigin;
use sp_core::H160;

benchmarks! {
    deploy_contract {
        let caller: T::AccountId = frame_benchmarking::whitelisted_caller();
        // Minimal valid bytecode: PUSH1 0x00 PUSH1 0x00 RETURN (4 bytes)
        let code: Vec<u8> = vec![0x60, 0x00, 0x60, 0x00, 0xF3];
        let gas_limit = sp_core::U256::from(1_000_000u64);
        let gas_price = sp_core::U256::zero();
    }: _(RawOrigin::Signed(caller), code, gas_limit, gas_price)

    call_contract {
        let caller: T::AccountId = frame_benchmarking::whitelisted_caller();
        // Deploy a simple contract first
        let deploy_code: Vec<u8> = vec![0x60, 0x00, 0x60, 0x00, 0xF3];
        let gas_limit = sp_core::U256::from(1_000_000u64);
        let gas_price = sp_core::U256::zero();
        let nonce: u64 = frame_system::Pallet::<T>::account_nonce(&caller)
            .try_into()
            .unwrap_or(0);
        let contract_address = Pallet::<T>::create_address(&caller, nonce);
        let bounded_code: BoundedVec<u8, T::MaxCodeSize> =
            BoundedVec::try_from(deploy_code).map_err(|_| Error::<T>::CodeExceedsMaxSize)?;
        ContractCodes::<T>::insert(contract_address, bounded_code);
        let input: Vec<u8> = vec![];
    }: _(RawOrigin::Signed(caller), contract_address, input, gas_limit, gas_price)

    execute_code {
        let code: Vec<u8> = vec![0x60, 0x01, 0x60, 0x00, 0xF3];
        let calldata: Vec<u8> = vec![];
        let gas: u64 = 1_000_000;
    }: {
        Pallet::<T>::execute_code(&code, &calldata, gas);
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::tests::Test as T;
    use frame_benchmarking::impl_benchmark_test_suite;
    
    impl_benchmark_test_suite!(Pallet, crate::tests::new_test_ext(), crate::tests::Test);
}
