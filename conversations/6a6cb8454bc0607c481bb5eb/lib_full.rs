//! # Verdis EVM Pallet
//!
//! Ethereum Virtual Machine compatibility for the Verdis blockchain.
//! Chain ID: 909, Max code size: 24576 bytes (EIP-170)
//! 137 opcodes implemented via native EVM interpreter.

#![cfg_attr(not(feature = "std"), no_std)]

pub use pallet::*;

mod interpreter;

#[cfg(test)]
mod tests;

#[frame_support::pallet]
pub mod pallet {
    use frame_support::{pallet_prelude::*, weights::Weight};
    use frame_system::pallet_prelude::*;
    use sp_core::{H160, H256, U256};
    use sp_std::vec::Vec;

    use crate::interpreter::{execute, ExecutionContext, ExecResult};

    pub const VERDIS_CHAIN_ID: u64 = 909;
    pub const MAX_CODE_SIZE: usize = 24576;

    #[pallet::config]
    pub trait Config: frame_system::Config {
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
        #[pallet::constant]
        type ChainId: Get<u64>;
        #[pallet::constant]
        type MaxCodeSize: Get<u32>;
    }

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    #[pallet::storage]
    pub type ContractCodes<T: Config> =
        StorageMap<_, Blake2_128Concat, H160, BoundedVec<u8, T::MaxCodeSize>, OptionQuery>;

    #[pallet::storage]
    pub type ContractStorage<T: Config> =
        StorageDoubleMap<_, Blake2_128Concat, H160, Blake2_128Concat, H256, H256, ValueQuery>;

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        ContractDeployed {
            deployer: T::AccountId,
            contract: H160,
            code_hash: H256,
        },
        ContractCalled {
            caller: T::AccountId,
            contract: H160,
            gas_used: U256,
        },
        StorageChanged {
            contract: H160,
            key: H256,
            value: H256,
        },
        ContractExecuted {
            caller: T::AccountId,
            contract: H160,
            success: bool,
            gas_used: u64,
            return_data: Vec<u8>,
        },
    }

    #[pallet::error]
    pub enum Error<T> {
        CodeTooLarge,
        ContractNotFound,
        InsufficientGas,
        ExecutionReverted,
        Unauthorized,
        CodeExceedsMaxSize,
        ExecutionFailed,
        OutOfGas,
    }

    #[pallet::call]
    
impl<T: Config> interpreter::EvmHost for Pallet<T> {
    fn get_code(&self, contract: H160) -> Vec<u8> {
        AccountCode::<T>::get(&contract).unwrap_or_default()
    }

    fn set_code(&mut self, contract: H160, code: Vec<u8>) -> Result<(), interpreter::ExecutionError> {
        if code.len() as u32 > MAX_CODE_SIZE {
            return Err(interpreter::ExecutionError::Other("code too large"));
        }
        AccountCode::<T>::insert(&contract, code);
        Ok(())
    }

    fn execute_code(&self, code: &[u8], calldata: &[u8], gas: u64) -> interpreter::ExecResult {
        if code.is_empty() {
            return interpreter::ExecResult::Success {
                return_data: Vec::new(),
                gas_used: 0,
            };
        }
        let mut ctx = interpreter::ExecutionContext {
            caller: H160::zero(),
            address: H160::zero(),
            origin: H160::zero(),
            callvalue: U256::zero(),
            calldata,
            code,
            gas_limit: gas,
            gas_used: 0,
            chain_id: VERDIS_CHAIN_ID,
            block_number: frame_system::Pallet::<T>::block_number().try_into().unwrap_or(0),
            block_timestamp: 0,
            block_gaslimit: 30_000_000,
            coinbase: H160::zero(),
            gas_price: U256::zero(),
            prev_randao: H256::zero(),
            base_fee: U256::zero(),
            self_balance: U256::zero(),
            balance: U256::zero(),
            return_data: Vec::new(),
        };
        // We need a separate host for nested calls - use a dummy host for now
        let mut dummy = DummyHost::<T> { _phantom: Default::default() };
        interpreter::execute(&mut ctx, &mut dummy)
    }

    fn get_storage(&self, contract: H160, key: H256) -> H256 {
        ContractStorage::<T>::get(&contract, &key).unwrap_or_default()
    }

    fn set_storage_value(&mut self, contract: H160, key: H256, value: H256) {
        ContractStorage::<T>::insert(&contract, &key, value);
    }
}

/// Dummy host for nested calls (reads from storage, no writes)
struct DummyHost<T: Config> {
    _phantom: sp_std::marker::PhantomData<T>,
}

impl<T: Config> interpreter::EvmHost for DummyHost<T> {
    fn get_code(&self, contract: H160) -> Vec<u8> {
        AccountCode::<T>::get(&contract).unwrap_or_default()
    }

    fn set_code(&mut self, _contract: H160, _code: Vec<u8>) -> Result<(), interpreter::ExecutionError> {
        Err(interpreter::ExecutionError::Other("cannot set code in nested call"))
    }

    fn execute_code(&self, code: &[u8], calldata: &[u8], gas: u64) -> interpreter::ExecResult {
        if code.is_empty() {
            return interpreter::ExecResult::Success {
                return_data: Vec::new(),
                gas_used: 0,
            };
        }
        let mut ctx = interpreter::ExecutionContext {
            caller: H160::zero(),
            address: H160::zero(),
            origin: H160::zero(),
            callvalue: U256::zero(),
            calldata,
            code,
            gas_limit: gas,
            gas_used: 0,
            chain_id: VERDIS_CHAIN_ID,
            block_number: frame_system::Pallet::<T>::block_number().try_into().unwrap_or(0),
            block_timestamp: 0,
            block_gaslimit: 30_000_000,
            coinbase: H160::zero(),
            gas_price: U256::zero(),
            prev_randao: H256::zero(),
            base_fee: U256::zero(),
            self_balance: U256::zero(),
            balance: U256::zero(),
            return_data: Vec::new(),
        };
        let mut dummy = DummyHost::<T> { _phantom: Default::default() };
        interpreter::execute(&mut ctx, &mut dummy)
    }

    fn get_storage(&self, contract: H160, key: H256) -> H256 {
        ContractStorage::<T>::get(&contract, &key).unwrap_or_default()
    }

    fn set_storage_value(&mut self, _contract: H160, _key: H256, _value: H256) {
        // No-op in nested calls
    }
}

impl<T: Config> Pallet<T> {
        #[pallet::call_index(0)]
        #[pallet::weight(10_000)]
        pub fn deploy_contract(
            origin: OriginFor<T>,
            code: Vec<u8>,
            _gas_limit: U256,
            _gas_price: U256,
        ) -> DispatchResult {
            let deployer = ensure_signed(origin)?;
            ensure!(code.len() <= MAX_CODE_SIZE, Error::<T>::CodeTooLarge);
            let bounded_code: BoundedVec<u8, T::MaxCodeSize> =
                BoundedVec::try_from(code).map_err(|_| Error::<T>::CodeExceedsMaxSize)?;
            let nonce: u64 = frame_system::Pallet::<T>::account_nonce(&deployer)
                .try_into()
                .unwrap_or(0);
            let contract_address = Self::create_address(&deployer, nonce);
            let code_hash = sp_io::hashing::keccak_256(&bounded_code);
            ContractCodes::<T>::insert(contract_address, bounded_code);
            Self::deposit_event(Event::ContractDeployed {
                deployer,
                contract: contract_address,
                code_hash: H256::from(code_hash),
            });
            Ok(())
        }

        #[pallet::call_index(1)]
        #[pallet::weight(10_000)]
        pub fn call_contract(
            origin: OriginFor<T>,
            contract: H160,
            input: Vec<u8>,
            gas_limit: U256,
            _gas_price: U256,
        ) -> DispatchResult {
            let caller = ensure_signed(origin)?;
            ensure!(
                ContractCodes::<T>::contains_key(contract),
                Error::<T>::ContractNotFound
            );

            let code = Self::get_code(contract);
            let gas_limit_u64: u64 = gas_limit.try_into().unwrap_or(1_000_000);

            let caller_h160 = Self::account_to_h160(&caller);
            let block_number = frame_system::Pallet::<T>::block_number().try_into().unwrap_or(0);
            let block_ts = 0u64;

            let mut ctx = ExecutionContext {
                caller: caller_h160,
                address: contract,
                origin: caller_h160,
                callvalue: U256::zero(),
                calldata: &input,
                code: &code,
                gas_limit: gas_limit_u64,
                gas_used: 0,
                chain_id: VERDIS_CHAIN_ID,
                block_number,
                block_timestamp: block_ts,
                block_gaslimit: 30_000_000,
                coinbase: H160::zero(),
                gas_price: U256::zero(),
                prev_randao: H256::zero(),
                base_fee: U256::zero(),
                self_balance: U256::zero(),
                balance: U256::zero(),
            };

            let result = execute(&mut ctx);

            match &result {
                ExecResult::Success { return_data, gas_used } => {
                    Self::deposit_event(Event::ContractExecuted {
                        caller: caller.clone(),
                        contract,
                        success: true,
                        gas_used: *gas_used,
                        return_data: return_data.clone(),
                    });
                }
                ExecResult::Reverted { reason: _, gas_used } => {
                    Self::deposit_event(Event::ContractExecuted {
                        caller: caller.clone(),
                        contract,
                        success: false,
                        gas_used: *gas_used,
                        return_data: Vec::new(),
                    });
                    return Err(Error::<T>::ExecutionReverted.into());
                }
                ExecResult::Failed { error, gas_used } => {
                    Self::deposit_event(Event::ContractExecuted {
                        caller: caller.clone(),
                        contract,
                        success: false,
                        gas_used: *gas_used,
                        return_data: Vec::new(),
                    });
                    return Err(Error::<T>::ExecutionFailed.into());
                }
            }

            Self::deposit_event(Event::ContractCalled {
                caller: caller.clone(),
                contract,
                gas_used: U256::from(ctx.gas_used),
            });
            Ok(())
        }

        #[pallet::call_index(2)]
        #[pallet::weight(10_000)]
        pub fn set_storage(
            origin: OriginFor<T>,
            contract: H160,
            key: H256,
            value: H256,
        ) -> DispatchResult {
            let _admin = ensure_signed(origin)?;
            ContractStorage::<T>::insert(contract, key, value);
            Self::deposit_event(Event::StorageChanged {
                contract,
                key,
                value,
            });
            Ok(())
        }
    }

    
impl<T: Config> interpreter::EvmHost for Pallet<T> {
    fn get_code(&self, contract: H160) -> Vec<u8> {
        AccountCode::<T>::get(&contract).unwrap_or_default()
    }

    fn set_code(&mut self, contract: H160, code: Vec<u8>) -> Result<(), interpreter::ExecutionError> {
        if code.len() as u32 > MAX_CODE_SIZE {
            return Err(interpreter::ExecutionError::Other("code too large"));
        }
        AccountCode::<T>::insert(&contract, code);
        Ok(())
    }

    fn execute_code(&self, code: &[u8], calldata: &[u8], gas: u64) -> interpreter::ExecResult {
        if code.is_empty() {
            return interpreter::ExecResult::Success {
                return_data: Vec::new(),
                gas_used: 0,
            };
        }
        let mut ctx = interpreter::ExecutionContext {
            caller: H160::zero(),
            address: H160::zero(),
            origin: H160::zero(),
            callvalue: U256::zero(),
            calldata,
            code,
            gas_limit: gas,
            gas_used: 0,
            chain_id: VERDIS_CHAIN_ID,
            block_number: frame_system::Pallet::<T>::block_number().try_into().unwrap_or(0),
            block_timestamp: 0,
            block_gaslimit: 30_000_000,
            coinbase: H160::zero(),
            gas_price: U256::zero(),
            prev_randao: H256::zero(),
            base_fee: U256::zero(),
            self_balance: U256::zero(),
            balance: U256::zero(),
            return_data: Vec::new(),
        };
        // We need a separate host for nested calls - use a dummy host for now
        let mut dummy = DummyHost::<T> { _phantom: Default::default() };
        interpreter::execute(&mut ctx, &mut dummy)
    }

    fn get_storage(&self, contract: H160, key: H256) -> H256 {
        ContractStorage::<T>::get(&contract, &key).unwrap_or_default()
    }

    fn set_storage_value(&mut self, contract: H160, key: H256, value: H256) {
        ContractStorage::<T>::insert(&contract, &key, value);
    }
}

/// Dummy host for nested calls (reads from storage, no writes)
struct DummyHost<T: Config> {
    _phantom: sp_std::marker::PhantomData<T>,
}

impl<T: Config> interpreter::EvmHost for DummyHost<T> {
    fn get_code(&self, contract: H160) -> Vec<u8> {
        AccountCode::<T>::get(&contract).unwrap_or_default()
    }

    fn set_code(&mut self, _contract: H160, _code: Vec<u8>) -> Result<(), interpreter::ExecutionError> {
        Err(interpreter::ExecutionError::Other("cannot set code in nested call"))
    }

    fn execute_code(&self, code: &[u8], calldata: &[u8], gas: u64) -> interpreter::ExecResult {
        if code.is_empty() {
            return interpreter::ExecResult::Success {
                return_data: Vec::new(),
                gas_used: 0,
            };
        }
        let mut ctx = interpreter::ExecutionContext {
            caller: H160::zero(),
            address: H160::zero(),
            origin: H160::zero(),
            callvalue: U256::zero(),
            calldata,
            code,
            gas_limit: gas,
            gas_used: 0,
            chain_id: VERDIS_CHAIN_ID,
            block_number: frame_system::Pallet::<T>::block_number().try_into().unwrap_or(0),
            block_timestamp: 0,
            block_gaslimit: 30_000_000,
            coinbase: H160::zero(),
            gas_price: U256::zero(),
            prev_randao: H256::zero(),
            base_fee: U256::zero(),
            self_balance: U256::zero(),
            balance: U256::zero(),
            return_data: Vec::new(),
        };
        let mut dummy = DummyHost::<T> { _phantom: Default::default() };
        interpreter::execute(&mut ctx, &mut dummy)
    }

    fn get_storage(&self, contract: H160, key: H256) -> H256 {
        ContractStorage::<T>::get(&contract, &key).unwrap_or_default()
    }

    fn set_storage_value(&mut self, _contract: H160, _key: H256, _value: H256) {
        // No-op in nested calls
    }
}

impl<T: Config> Pallet<T> {
        pub fn create_address(deployer: &T::AccountId, nonce: u64) -> H160 {
            let deployer_bytes = deployer.encode();
            let mut data = deployer_bytes;
            data.extend_from_slice(&nonce.to_le_bytes());
            let hash = sp_io::hashing::keccak_256(&data);
            H160::from_slice(&hash[12..])
        }

        fn account_to_h160(account: &T::AccountId) -> H160 {
            let encoded = account.encode();
            let hash = sp_io::hashing::keccak_256(&encoded);
            H160::from_slice(&hash[12..])
        }

        pub fn get_code(contract: H160) -> Vec<u8> {
            ContractCodes::<T>::get(contract)
                .map(|c| c.into_inner())
                .unwrap_or_default()
        }

        pub fn contract_exists(contract: H160) -> bool {
            ContractCodes::<T>::get(contract)
                .map(|c| !c.is_empty())
                .unwrap_or(false)
        }

        pub fn get_storage(contract: H160, key: H256) -> H256 {
            ContractStorage::<T>::get(contract, key)
        }

        /// Execute EVM bytecode directly (for testing and internal calls)
        pub fn execute_code(
            code: &[u8],
            calldata: &[u8],
            gas_limit: u64,
        ) -> ExecResult {
            let mut ctx = ExecutionContext {
                caller: H160::zero(),
                address: H160::zero(),
                origin: H160::zero(),
                callvalue: U256::zero(),
                calldata,
                code,
                gas_limit,
                gas_used: 0,
                chain_id: VERDIS_CHAIN_ID,
                block_number: 1,
                block_timestamp: 0,
                block_gaslimit: 30_000_000,
                coinbase: H160::zero(),
                gas_price: U256::zero(),
                prev_randao: H256::zero(),
                base_fee: U256::zero(),
                self_balance: U256::zero(),
                balance: U256::zero(),
            };
            execute(&mut ctx)
        }
    }
}
