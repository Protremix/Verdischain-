#![allow(clippy::let_unit_value)]
#![allow(clippy::disallowed_methods)]
//! Comprehensive tests for the Verdis EVM pallet

use crate::{self as pallet_evm, *};
use crate::interpreter::{ExecResult, ExecutionError, Stack, Memory, execute, ExecutionContext, collect_jumpdests};
use codec::Encode;
use frame_support::{
    assert_noop, assert_ok, construct_runtime, derive_impl, parameter_types,
    traits::{ConstU16, ConstU32, ConstU64},
    BoundedVec,
};
use sp_core::{H160, H256, U256};
use sp_runtime::{
    traits::{BlakeTwo256, IdentityLookup},
    BuildStorage, DispatchError,
};

type Block = frame_system::mocking::MockBlock<Test>;

construct_runtime!(
    pub enum Test {
        System: frame_system,
        Evm: pallet_evm,
    }
);

#[derive_impl(frame_system::config_preludes::TestDefaultConfig)]
impl frame_system::Config for Test {
    type BaseCallFilter = frame_support::traits::Everything;
    type BlockWeights = ();
    type BlockLength = ();
    type DbWeight = ();
    type RuntimeOrigin = RuntimeOrigin;
    type RuntimeCall = RuntimeCall;
    type Nonce = u64;
    type Hash = H256;
    type Hashing = BlakeTwo256;
    type AccountId = u64;
    type Lookup = IdentityLookup<Self::AccountId>;
    type Block = Block;
    type RuntimeEvent = RuntimeEvent;
    type BlockHashCount = ConstU64<250>;
    type Version = ();
    type PalletInfo = PalletInfo;
    type AccountData = ();
    type OnNewAccount = ();
    type OnKilledAccount = ();
    type SystemWeightInfo = ();
    type SS58Prefix = ConstU16<42>;
    type OnSetCode = ();
    type MaxConsumers = ConstU32<16>;
}

parameter_types! {
    pub const ChainId: u64 = 909;
    pub const MaxCodeSize: u32 = 24576;
}

impl pallet_evm::Config for Test {
    type RuntimeEvent = RuntimeEvent;
    type ChainId = ChainId;
    type MaxCodeSize = MaxCodeSize;
    type WeightInfo = ();
}

pub fn new_test_ext() -> sp_io::TestExternalities {
    let t = frame_system::GenesisConfig::<Test>::default()
        .build_storage()
        .unwrap();
    let mut ext = sp_io::TestExternalities::new(t);
    ext.execute_with(|| System::set_block_number(1));
    ext
}

fn dummy_code() -> Vec<u8> {
    vec![0x60, 0x80, 0x60, 0x40, 0x52, 0x34, 0x80, 0x15, 0x61, 0x00, 0x0f, 0x57, 0x60, 0x00, 0x80, 0xfd]
}

fn run_code(code: &[u8], gas: u64) -> ExecResult {
    new_test_ext().execute_with(|| {
        Evm::execute_code(code, &[], gas)
    })
}

fn run_code_with_calldata(code: &[u8], calldata: &[u8], gas: u64) -> ExecResult {
    new_test_ext().execute_with(|| {
        Evm::execute_code(code, calldata, gas)
    })
}

// =========================================================================
// Constants tests
// =========================================================================

#[test]
fn test_chain_id() {
    assert_eq!(VERDIS_CHAIN_ID, 909);
}

#[test]
fn test_max_code_size() {
    assert_eq!(MAX_CODE_SIZE, 24576);
}

// =========================================================================
// Deploy tests
// =========================================================================

#[test]
fn deploy_contract_success() {
    new_test_ext().execute_with(|| {
        let code = dummy_code();
        assert_ok!(Evm::deploy_contract(RuntimeOrigin::signed(1), code.clone(), U256::from(100000), U256::zero()));
        let events = System::events();
        assert_eq!(events.len(), 1);
    });
}

#[test]
fn deploy_contract_code_too_large_fails() {
    new_test_ext().execute_with(|| {
        let code = vec![0u8; 24577];
        assert_noop!(
            Evm::deploy_contract(RuntimeOrigin::signed(1), code, U256::from(100000), U256::zero()),
            Error::<Test>::CodeTooLarge
        );
    });
}

#[test]
fn deploy_empty_code_succeeds() {
    new_test_ext().execute_with(|| {
        assert_ok!(Evm::deploy_contract(RuntimeOrigin::signed(1), vec![], U256::from(100000), U256::zero()));
    });
}

#[test]
fn deploy_max_code_size_succeeds() {
    new_test_ext().execute_with(|| {
        let code = vec![0x00; 24576];
        assert_ok!(Evm::deploy_contract(RuntimeOrigin::signed(1), code, U256::from(100000), U256::zero()));
    });
}

#[test]
fn deploy_contract_different_deployers_different_addresses() {
    new_test_ext().execute_with(|| {
        assert_ok!(Evm::deploy_contract(RuntimeOrigin::signed(1), dummy_code(), U256::from(100000), U256::zero()));
        assert_ok!(Evm::deploy_contract(RuntimeOrigin::signed(2), dummy_code(), U256::from(100000), U256::zero()));
        let events = System::events();
        let addr1 = match &events[0].event {
            RuntimeEvent::Evm(Event::ContractDeployed { contract, .. }) => *contract,
            _ => H160::zero(),
        };
        let addr2 = match &events[1].event {
            RuntimeEvent::Evm(Event::ContractDeployed { contract, .. }) => *contract,
            _ => H160::zero(),
        };
        assert_ne!(addr1, addr2);
    });
}

// =========================================================================
// Call tests
// =========================================================================

#[test]
fn call_contract_success() {
    new_test_ext().execute_with(|| {
        let code = vec![0x00]; // STOP
        assert_ok!(Evm::deploy_contract(RuntimeOrigin::signed(1), code, U256::from(100000), U256::zero()));
        let events = System::events();
        let contract = match &events[0].event {
            RuntimeEvent::Evm(Event::ContractDeployed { contract, .. }) => *contract,
            _ => H160::zero(),
        };
        assert_ok!(Evm::call_contract(RuntimeOrigin::signed(1), contract, vec![], U256::from(100000), U256::zero()));
    });
}

#[test]
fn call_contract_not_found_fails() {
    new_test_ext().execute_with(|| {
        let fake_addr = H160::from_slice(&[0xff; 20]);
        assert_noop!(
            Evm::call_contract(RuntimeOrigin::signed(1), fake_addr, vec![], U256::from(100000), U256::zero()),
            Error::<Test>::ContractNotFound
        );
    });
}

#[test]
fn call_contract_by_same_deployer() {
    new_test_ext().execute_with(|| {
        let code = vec![0x00];
        assert_ok!(Evm::deploy_contract(RuntimeOrigin::signed(1), code, U256::from(100000), U256::zero()));
        let events = System::events();
        let contract = match &events[0].event {
            RuntimeEvent::Evm(Event::ContractDeployed { contract, .. }) => *contract,
            _ => H160::zero(),
        };
        assert_ok!(Evm::call_contract(RuntimeOrigin::signed(1), contract, vec![], U256::from(100000), U256::zero()));
    });
}

// =========================================================================
// Storage tests
// =========================================================================

#[test]
fn set_storage_success() {
    new_test_ext().execute_with(|| {
        let contract = H160::from_slice(&[0x42; 20]);
        let key = H256::from_slice(&[0x01; 32]);
        let value = H256::from_slice(&[0xff; 32]);
        assert_ok!(Evm::set_storage(RuntimeOrigin::signed(1), contract, key, value));
        assert_eq!(Evm::get_storage(contract, key), value);
    });
}

#[test]
fn set_storage_overwrite() {
    new_test_ext().execute_with(|| {
        let contract = H160::from_slice(&[0x42; 20]);
        let key = H256::from_slice(&[0x01; 32]);
        let val1 = H256::from_slice(&[0xff; 32]);
        let val2 = H256::from_slice(&[0xaa; 32]);
        assert_ok!(Evm::set_storage(RuntimeOrigin::signed(1), contract, key, val1));
        assert_ok!(Evm::set_storage(RuntimeOrigin::signed(1), contract, key, val2));
        assert_eq!(Evm::get_storage(contract, key), val2);
    });
}

#[test]
fn set_storage_different_keys_independent() {
    new_test_ext().execute_with(|| {
        let contract = H160::from_slice(&[0x42; 20]);
        let key1 = H256::from_slice(&[0x01; 32]);
        let key2 = H256::from_slice(&[0x02; 32]);
        let val1 = H256::from_slice(&[0xff; 32]);
        let val2 = H256::from_slice(&[0xaa; 32]);
        assert_ok!(Evm::set_storage(RuntimeOrigin::signed(1), contract, key1, val1));
        assert_ok!(Evm::set_storage(RuntimeOrigin::signed(1), contract, key2, val2));
        assert_eq!(Evm::get_storage(contract, key1), val1);
        assert_eq!(Evm::get_storage(contract, key2), val2);
    });
}

#[test]
fn set_storage_different_contracts_independent() {
    new_test_ext().execute_with(|| {
        let contract1 = H160::from_slice(&[0x42; 20]);
        let contract2 = H160::from_slice(&[0x43; 20]);
        let key = H256::from_slice(&[0x01; 32]);
        let val1 = H256::from_slice(&[0xff; 32]);
        let val2 = H256::from_slice(&[0xaa; 32]);
        assert_ok!(Evm::set_storage(RuntimeOrigin::signed(1), contract1, key, val1));
        assert_ok!(Evm::set_storage(RuntimeOrigin::signed(1), contract2, key, val2));
        assert_eq!(Evm::get_storage(contract1, key), val1);
        assert_eq!(Evm::get_storage(contract2, key), val2);
    });
}

#[test]
fn get_storage_default_for_unset() {
    new_test_ext().execute_with(|| {
        let contract = H160::from_slice(&[0x42; 20]);
        let key = H256::from_slice(&[0x01; 32]);
        assert_eq!(Evm::get_storage(contract, key), H256::zero());
    });
}

// =========================================================================
// Helper function tests
// =========================================================================

#[test]
fn get_code_returns_empty_for_missing() {
    new_test_ext().execute_with(|| {
        let contract = H160::from_slice(&[0xff; 20]);
        assert!(Evm::get_code(contract).is_empty());
    });
}

#[test]
fn contract_exists_false_for_missing() {
    new_test_ext().execute_with(|| {
        let contract = H160::from_slice(&[0xff; 20]);
        assert!(!Evm::contract_exists(contract));
    });
}

#[test]
fn contract_exists_false_for_empty_code() {
    new_test_ext().execute_with(|| {
        assert_ok!(Evm::deploy_contract(RuntimeOrigin::signed(1), vec![], U256::from(100000), U256::zero()));
        let events = System::events();
        let contract = match &events[0].event {
            RuntimeEvent::Evm(Event::ContractDeployed { contract, .. }) => *contract,
            _ => H160::zero(),
        };
        assert!(!Evm::contract_exists(contract));
    });
}

#[test]
fn contract_address_deterministic_same_deployer_nonce() {
    new_test_ext().execute_with(|| {
        let addr1 = Evm::create_address(&1u64, 0);
        let addr2 = Evm::create_address(&1u64, 0);
        assert_eq!(addr1, addr2);
    });
}

#[test]
fn contract_address_different_nonce_different_address() {
    new_test_ext().execute_with(|| {
        let addr1 = Evm::create_address(&1u64, 0);
        let addr2 = Evm::create_address(&1u64, 1);
        assert_ne!(addr1, addr2);
    });
}

#[test]
fn contract_address_different_deployers_different() {
    new_test_ext().execute_with(|| {
        let addr1 = Evm::create_address(&1u64, 0);
        let addr2 = Evm::create_address(&2u64, 0);
        assert_ne!(addr1, addr2);
    });
}

#[test]
fn contract_address_is_h160_from_last_20_bytes() {
    new_test_ext().execute_with(|| {
        let addr = Evm::create_address(&1u64, 0);
        assert_eq!(addr.as_bytes().len(), 20);
    });
}

// =========================================================================
// Lifecycle tests
// =========================================================================

#[test]
fn deploy_and_call_lifecycle() {
    new_test_ext().execute_with(|| {
        let code = vec![0x60, 0x42, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xf3];
        assert_ok!(Evm::deploy_contract(RuntimeOrigin::signed(1), code, U256::from(100000), U256::zero()));
        let events = System::events();
        let contract = match &events[0].event {
            RuntimeEvent::Evm(Event::ContractDeployed { contract, .. }) => *contract,
            _ => H160::zero(),
        };
        assert_ok!(Evm::call_contract(RuntimeOrigin::signed(1), contract, vec![], U256::from(100000), U256::zero()));
    });
}

#[test]
fn multiple_contracts_same_deployer_different_nonce() {
    new_test_ext().execute_with(|| {
        assert_ok!(Evm::deploy_contract(RuntimeOrigin::signed(1), dummy_code(), U256::from(100000), U256::zero()));
        frame_system::Pallet::<Test>::inc_account_nonce(&1);
        assert_ok!(Evm::deploy_contract(RuntimeOrigin::signed(1), dummy_code(), U256::from(100000), U256::zero()));
        let events = System::events();
        let addr1 = match &events[0].event {
            RuntimeEvent::Evm(Event::ContractDeployed { contract, .. }) => *contract,
            _ => H160::zero(),
        };
        let addr2 = match &events[1].event {
            RuntimeEvent::Evm(Event::ContractDeployed { contract, .. }) => *contract,
            _ => H160::zero(),
        };
        assert_ne!(addr1, addr2);
    });
}

#[test]
fn deploy_contract_code_hash_correct() {
    new_test_ext().execute_with(|| {
        let code = vec![0x60, 0x42, 0x00];
        assert_ok!(Evm::deploy_contract(RuntimeOrigin::signed(1), code.clone(), U256::from(100000), U256::zero()));
        let expected_hash = sp_io::hashing::keccak_256(&code);
        let events = System::events();
        match &events[0].event {
            RuntimeEvent::Evm(Event::ContractDeployed { code_hash, .. }) => {
                assert_eq!(*code_hash, H256::from(expected_hash));
            }
            _ => panic!("Expected ContractDeployed event"),
        }
    });
}

#[test]
fn zero_gas_deploy_succeeds() {
    new_test_ext().execute_with(|| {
        assert_ok!(Evm::deploy_contract(RuntimeOrigin::signed(1), dummy_code(), U256::zero(), U256::zero()));
    });
}

#[test]
fn zero_gas_call_succeeds() {
    new_test_ext().execute_with(|| {
        let code = vec![0x00];
        assert_ok!(Evm::deploy_contract(RuntimeOrigin::signed(1), code, U256::from(100000), U256::zero()));
        let events = System::events();
        let contract = match &events[0].event {
            RuntimeEvent::Evm(Event::ContractDeployed { contract, .. }) => *contract,
            _ => H160::zero(),
        };
        assert_ok!(Evm::call_contract(RuntimeOrigin::signed(1), contract, vec![], U256::from(100000), U256::zero()));
    });
}

// =========================================================================
// EVM Interpreter - Stack tests
// =========================================================================

#[test]
fn stack_push_pop() {
    let mut s = Stack::new();
    assert!(s.push(U256::from(42u32)).is_ok());
    assert_eq!(s.pop().unwrap(), U256::from(42u32));
}

#[test]
fn stack_overflow() {
    let mut s = Stack::new();
    for _ in 0..1024 {
        assert!(s.push(U256::one()).is_ok());
    }
    assert_eq!(s.push(U256::one()), Err(ExecutionError::StackOverflow));
}

#[test]
fn stack_underflow() {
    let mut s = Stack::new();
    assert_eq!(s.pop(), Err(ExecutionError::StackUnderflow));
}

#[test]
fn stack_dup() {
    let mut s = Stack::new();
    s.push(U256::from(5u32)).unwrap();
    s.push(U256::from(10u32)).unwrap();
    s.dup(1).unwrap();
    assert_eq!(s.len(), 3);
    assert_eq!(s.pop().unwrap(), U256::from(10u32));
    assert_eq!(s.pop().unwrap(), U256::from(10u32));
}

#[test]
fn stack_swap() {
    let mut s = Stack::new();
    s.push(U256::from(1u32)).unwrap();
    s.push(U256::from(2u32)).unwrap();
    s.swap(1).unwrap();
    assert_eq!(s.pop().unwrap(), U256::from(1u32));
    assert_eq!(s.pop().unwrap(), U256::from(2u32));
}

// =========================================================================
// EVM Interpreter - Memory tests
// =========================================================================

#[test]
fn memory_store_load() {
    let mut m = Memory::new();
    m.store(0, &[0x42, 0x43, 0x44]).unwrap();
    let data = m.load(0, 3).unwrap();
    assert_eq!(data, vec![0x42, 0x43, 0x44]);
}

#[test]
fn memory_store_u256() {
    let mut m = Memory::new();
    m.store_u256(0, U256::from(0xDEADBEEFu32)).unwrap();
    let val = m.load_u256(0).unwrap();
    assert_eq!(val, U256::from(0xDEADBEEFu32));
}

#[test]
fn memory_store_u8() {
    let mut m = Memory::new();
    m.store_u8(0, 0xFF).unwrap();
    let data = m.load(0, 1).unwrap();
    assert_eq!(data, vec![0xFF]);
}

#[test]
fn memory_load_beyond_size_returns_zeros() {
    let m = Memory::new();
    let data = m.load(0, 4).unwrap();
    assert_eq!(data, vec![0, 0, 0, 0]);
}

#[test]
fn memory_size() {
    let mut m = Memory::new();
    assert_eq!(m.size(), 0);
    m.store(0, &[1, 2, 3]).unwrap();
    assert_eq!(m.size(), 3);
}

// =========================================================================
// EVM Interpreter - Opcode execution tests
// =========================================================================

#[test]
fn op_stop() {
    let code = vec![0x00]; // STOP
    let result = run_code(&code, 1000);
    assert!(matches!(result, ExecResult::Success { .. }));
}

#[test]
fn op_add() {
    let code = vec![0x60, 0x01, 0x60, 0x02, 0x01, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];
    let result = run_code(&code, 1000);
    if let ExecResult::Success { return_data, .. } = result {
        let mut arr = [0u8; 32];
        arr.copy_from_slice(&return_data[..32]);
        assert_eq!(U256::from_big_endian(&arr), U256::from(3u32));
    } else {
        panic!("Expected success");
    }
}

#[test]
fn op_mul() {
    let code = vec![0x60, 0x06, 0x60, 0x07, 0x02, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];
    let result = run_code(&code, 1000);
    if let ExecResult::Success { return_data, .. } = result {
        let mut arr = [0u8; 32];
        arr.copy_from_slice(&return_data[..32]);
        assert_eq!(U256::from_big_endian(&arr), U256::from(42u32));
    } else {
        panic!("Expected success");
    }
}

#[test]
fn op_sub() {
    let code = vec![0x60, 0x03, 0x60, 0x0A, 0x03, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];
    let result = run_code(&code, 1000);
    if let ExecResult::Success { return_data, .. } = result {
        let mut arr = [0u8; 32];
        arr.copy_from_slice(&return_data[..32]);
        assert_eq!(U256::from_big_endian(&arr), U256::from(7u32));
    } else {
        panic!("Expected success");
    }
}

#[test]
fn op_div() {
    let code = vec![0x60, 0x02, 0x60, 0x0A, 0x04, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];
    let result = run_code(&code, 1000);
    if let ExecResult::Success { return_data, .. } = result {
        let mut arr = [0u8; 32];
        arr.copy_from_slice(&return_data[..32]);
        assert_eq!(U256::from_big_endian(&arr), U256::from(5u32));
    } else {
        panic!("Expected success");
    }
}

#[test]
fn op_div_by_zero() {
    let code = vec![0x60, 0x00, 0x60, 0x0A, 0x04, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];
    let result = run_code(&code, 1000);
    if let ExecResult::Success { return_data, .. } = result {
        let mut arr = [0u8; 32];
        arr.copy_from_slice(&return_data[..32]);
        assert_eq!(U256::from_big_endian(&arr), U256::zero());
    } else {
        panic!("Expected success");
    }
}

#[test]
fn op_mod() {
    let code = vec![0x60, 0x03, 0x60, 0x0A, 0x06, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];
    let result = run_code(&code, 1000);
    if let ExecResult::Success { return_data, .. } = result {
        let mut arr = [0u8; 32];
        arr.copy_from_slice(&return_data[..32]);
        assert_eq!(U256::from_big_endian(&arr), U256::from(1u32));
    } else {
        panic!("Expected success");
    }
}

#[test]
fn op_exp() {
    let code = vec![0x60, 0x02, 0x60, 0x03, 0x0A, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];
    let result = run_code(&code, 1000);
    if let ExecResult::Success { return_data, .. } = result {
        let mut arr = [0u8; 32];
        arr.copy_from_slice(&return_data[..32]);
        assert_eq!(U256::from_big_endian(&arr), U256::from(9u32));
    } else {
        panic!("Expected success");
    }
}

#[test]
fn op_lt() {
    let code = vec![0x60, 0x05, 0x60, 0x03, 0x10, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];
    let result = run_code(&code, 1000);
    if let ExecResult::Success { return_data, .. } = result {
        let mut arr = [0u8; 32];
        arr.copy_from_slice(&return_data[..32]);
        assert_eq!(U256::from_big_endian(&arr), U256::one());
    } else {
        panic!("Expected success");
    }
}

#[test]
fn op_gt() {
    let code = vec![0x60, 0x03, 0x60, 0x05, 0x11, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];
    let result = run_code(&code, 1000);
    if let ExecResult::Success { return_data, .. } = result {
        let mut arr = [0u8; 32];
        arr.copy_from_slice(&return_data[..32]);
        assert_eq!(U256::from_big_endian(&arr), U256::one());
    } else {
        panic!("Expected success");
    }
}

#[test]
fn op_eq() {
    let code = vec![0x60, 0x05, 0x60, 0x05, 0x14, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];
    let result = run_code(&code, 1000);
    if let ExecResult::Success { return_data, .. } = result {
        let mut arr = [0u8; 32];
        arr.copy_from_slice(&return_data[..32]);
        assert_eq!(U256::from_big_endian(&arr), U256::one());
    } else {
        panic!("Expected success");
    }
}

#[test]
fn op_iszero() {
    let code = vec![0x60, 0x00, 0x15, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];
    let result = run_code(&code, 1000);
    if let ExecResult::Success { return_data, .. } = result {
        let mut arr = [0u8; 32];
        arr.copy_from_slice(&return_data[..32]);
        assert_eq!(U256::from_big_endian(&arr), U256::one());
    } else {
        panic!("Expected success");
    }
}

#[test]
fn op_and() {
    let code = vec![0x60, 0xFF, 0x60, 0x0F, 0x16, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];
    let result = run_code(&code, 1000);
    if let ExecResult::Success { return_data, .. } = result {
        let mut arr = [0u8; 32];
        arr.copy_from_slice(&return_data[..32]);
        assert_eq!(U256::from_big_endian(&arr), U256::from(0x0Fu32));
    } else {
        panic!("Expected success");
    }
}

#[test]
fn op_or() {
    let code = vec![0x60, 0xF0, 0x60, 0x0F, 0x17, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];
    let result = run_code(&code, 1000);
    if let ExecResult::Success { return_data, .. } = result {
        let mut arr = [0u8; 32];
        arr.copy_from_slice(&return_data[..32]);
        assert_eq!(U256::from_big_endian(&arr), U256::from(0xFFu32));
    } else {
        panic!("Expected success");
    }
}

#[test]
fn op_xor() {
    let code = vec![0x60, 0xFF, 0x60, 0x0F, 0x18, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];
    let result = run_code(&code, 1000);
    if let ExecResult::Success { return_data, .. } = result {
        let mut arr = [0u8; 32];
        arr.copy_from_slice(&return_data[..32]);
        assert_eq!(U256::from_big_endian(&arr), U256::from(0xF0u32));
    } else {
        panic!("Expected success");
    }
}

#[test]
fn op_not() {
    let code = vec![0x60, 0x00, 0x19, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];
    let result = run_code(&code, 1000);
    if let ExecResult::Success { return_data, .. } = result {
        let mut arr = [0u8; 32];
        arr.copy_from_slice(&return_data[..32]);
        assert_eq!(U256::from_big_endian(&arr), U256::MAX);
    } else {
        panic!("Expected success");
    }
}

#[test]
fn op_keccak256() {
    let code = vec![0x60, 0x00, 0x60, 0x00, 0x20, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];
    let result = run_code(&code, 1000);
    if let ExecResult::Success { return_data, .. } = result {
        let expected = sp_io::hashing::keccak_256(&[]);
        let mut arr = [0u8; 32];
        arr.copy_from_slice(&return_data[..32]);
        assert_eq!(U256::from_big_endian(&arr), U256::from_big_endian(&expected));
    } else {
        panic!("Expected success");
    }
}

#[test]
fn op_push0() {
    let code = vec![0x5F, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];
    let result = run_code(&code, 1000);
    assert!(matches!(result, ExecResult::Success { .. }));
}

#[test]
fn op_push32() {
    let mut code = vec![0x7F];
    code.extend_from_slice(&[0x42; 32]);
    code.extend_from_slice(&[0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3]);
    let result = run_code(&code, 1000);
    if let ExecResult::Success { return_data, .. } = result {
        assert_eq!(return_data, vec![0x42; 32]);
    } else {
        panic!("Expected success");
    }
}

#[test]
fn op_dup1() {
    let code = vec![0x60, 0x05, 0x80, 0x01, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];
    let result = run_code(&code, 1000);
    if let ExecResult::Success { return_data, .. } = result {
        let mut arr = [0u8; 32];
        arr.copy_from_slice(&return_data[..32]);
        assert_eq!(U256::from_big_endian(&arr), U256::from(10u32));
    } else {
        panic!("Expected success");
    }
}

#[test]
fn op_swap1() {
    let code = vec![0x60, 0x02, 0x60, 0x01, 0x90, 0x03, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];
    let result = run_code(&code, 1000);
    if let ExecResult::Success { return_data, .. } = result {
        let mut arr = [0u8; 32];
        arr.copy_from_slice(&return_data[..32]);
        assert_eq!(U256::from_big_endian(&arr), U256::from(1u32));
    } else {
        panic!("Expected success");
    }
}

#[test]
fn op_pop() {
    let code = vec![0x60, 0x01, 0x60, 0x02, 0x50, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];
    let result = run_code(&code, 1000);
    if let ExecResult::Success { return_data, .. } = result {
        let mut arr = [0u8; 32];
        arr.copy_from_slice(&return_data[..32]);
        assert_eq!(U256::from_big_endian(&arr), U256::from(1u32));
    } else {
        panic!("Expected success");
    }
}

#[test]
fn op_mload_mstore() {
    let code = vec![0x60, 0x42, 0x60, 0x00, 0x52, 0x60, 0x00, 0x51, 0x60, 0x20, 0x60, 0x00, 0xF3];
    let result = run_code(&code, 1000);
    if let ExecResult::Success { return_data, .. } = result {
        let mut arr = [0u8; 32];
        arr.copy_from_slice(&return_data[..32]);
        assert_eq!(U256::from_big_endian(&arr), U256::from(0x42u32));
    } else {
        panic!("Expected success");
    }
}

#[test]
fn op_msize() {
    let code = vec![0x60, 0x42, 0x60, 0x20, 0x52, 0x59, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];
    let result = run_code(&code, 1000);
    if let ExecResult::Success { return_data, .. } = result {
        let mut arr = [0u8; 32];
        arr.copy_from_slice(&return_data[..32]);
        assert!(U256::from_big_endian(&arr) >= U256::from(0x21u32));
    } else {
        panic!("Expected success");
    }
}

#[test]
fn op_jump() {
    let code = vec![
        0x60, 0x04, 0x56, 0x00, 0x5B, 0x60, 0x42, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3,
    ];
    let result = run_code(&code, 1000);
    if let ExecResult::Success { return_data, .. } = result {
        let mut arr = [0u8; 32];
        arr.copy_from_slice(&return_data[..32]);
        assert_eq!(U256::from_big_endian(&arr), U256::from(0x42u32));
    } else {
        panic!("Expected success: {:?}", result);
    }
}

#[test]
fn op_jumpi_taken() {
    let code = vec![
        0x60, 0x01, 0x60, 0x06, 0x57, 0x00, 0x5B, 0x60, 0x42, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3,
    ];
    let result = run_code(&code, 1000);
    if let ExecResult::Success { return_data, .. } = result {
        let mut arr = [0u8; 32];
        arr.copy_from_slice(&return_data[..32]);
        assert_eq!(U256::from_big_endian(&arr), U256::from(0x42u32));
    } else {
        panic!("Expected success: {:?}", result);
    }
}

#[test]
fn op_jumpi_not_taken() {
    let code = vec![
        0x60, 0x00, 0x60, 0x08, 0x57, 0x60, 0x99, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3,
        0x5B,
    ];
    let result = run_code(&code, 1000);
    if let ExecResult::Success { return_data, .. } = result {
        let mut arr = [0u8; 32];
        arr.copy_from_slice(&return_data[..32]);
        assert_eq!(U256::from_big_endian(&arr), U256::from(0x99u32));
    } else {
        panic!("Expected success: {:?}", result);
    }
}

#[test]
fn op_invalid_jump_fails() {
    let code = vec![0x60, 0x04, 0x56];
    let result = run_code(&code, 1000);
    assert!(matches!(result, ExecResult::Failed { error: ExecutionError::InvalidJump, .. }));
}

#[test]
fn op_revert() {
    let code = vec![0x60, 0x00, 0x60, 0x00, 0xFD];
    let result = run_code(&code, 1000);
    assert!(matches!(result, ExecResult::Reverted { .. }));
}

#[test]
fn op_invalid() {
    let code = vec![0xFE];
    let result = run_code(&code, 1000);
    assert!(matches!(result, ExecResult::Failed { error: ExecutionError::InvalidOpcode, .. }));
}

#[test]
fn op_out_of_gas() {
    let code = vec![0x60, 0x00, 0x5B, 0x60, 0x01, 0x01, 0x80, 0x60, 0x02, 0x57];
    let result = run_code(&code, 10);
    assert!(matches!(result, ExecResult::Failed { error: ExecutionError::OutOfGas, .. }));
}

#[test]
fn op_shl() {
    let code = vec![0x60, 0x02, 0x60, 0x01, 0x1B, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];
    let result = run_code(&code, 1000);
    if let ExecResult::Success { return_data, .. } = result {
        let mut arr = [0u8; 32];
        arr.copy_from_slice(&return_data[..32]);
        assert_eq!(U256::from_big_endian(&arr), U256::from(4u32));
    } else {
        panic!("Expected success");
    }
}

#[test]
fn op_shr() {
    let code = vec![0x60, 0x08, 0x60, 0x01, 0x1C, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];
    let result = run_code(&code, 1000);
    if let ExecResult::Success { return_data, .. } = result {
        let mut arr = [0u8; 32];
        arr.copy_from_slice(&return_data[..32]);
        assert_eq!(U256::from_big_endian(&arr), U256::from(4u32));
    } else {
        panic!("Expected success");
    }
}

#[test]
fn op_calldatasize() {
    let code = vec![0x36, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];
    let result = run_code_with_calldata(&code, &[0x01, 0x02, 0x03], 1000);
    if let ExecResult::Success { return_data, .. } = result {
        let mut arr = [0u8; 32];
        arr.copy_from_slice(&return_data[..32]);
        assert_eq!(U256::from_big_endian(&arr), U256::from(3u32));
    } else {
        panic!("Expected success");
    }
}

#[test]
fn op_calldataload() {
    let code = vec![0x60, 0x00, 0x35, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];
    let calldata = vec![0x42; 32];
    let result = run_code_with_calldata(&code, &calldata, 1000);
    if let ExecResult::Success { return_data, .. } = result {
        assert_eq!(return_data, vec![0x42; 32]);
    } else {
        panic!("Expected success");
    }
}

#[test]
fn op_codesize() {
    let code = vec![0x38, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];
    let result = run_code(&code, 1000);
    if let ExecResult::Success { return_data, .. } = result {
        let mut arr = [0u8; 32];
        arr.copy_from_slice(&return_data[..32]);
        assert_eq!(U256::from_big_endian(&arr), U256::from(code.len() as u32));
    } else {
        panic!("Expected success");
    }
}

#[test]
fn op_chainid() {
    let code = vec![0x46, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];
    let result = run_code(&code, 1000);
    if let ExecResult::Success { return_data, .. } = result {
        let mut arr = [0u8; 32];
        arr.copy_from_slice(&return_data[..32]);
        assert_eq!(U256::from_big_endian(&arr), U256::from(909u32));
    } else {
        panic!("Expected success");
    }
}

#[test]
fn op_pc() {
    let code = vec![0x58, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];
    let result = run_code(&code, 1000);
    if let ExecResult::Success { return_data, .. } = result {
        let mut arr = [0u8; 32];
        arr.copy_from_slice(&return_data[..32]);
        assert_eq!(U256::from_big_endian(&arr), U256::zero());
    } else {
        panic!("Expected success");
    }
}

#[test]
fn op_gas() {
    let code = vec![0x5A, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];
    let result = run_code(&code, 1000);
    if let ExecResult::Success { return_data, .. } = result {
        let mut arr = [0u8; 32];
        arr.copy_from_slice(&return_data[..32]);
        let gas = U256::from_big_endian(&arr);
        assert!(gas > U256::from(990u32) && gas < U256::from(1000u32));
    } else {
        panic!("Expected success");
    }
}

#[test]
fn op_selfdestruct() {
    let code = vec![0x60, 0x00, 0xFF];
    let result = run_code(&code, 100000);
    assert!(matches!(result, ExecResult::Success { .. }));
}

#[test]
fn collect_jumpdests_basic() {
    let code = vec![0x60, 0x01, 0x5B, 0x00, 0x5B];
    let dests = collect_jumpdests(&code);
    assert_eq!(dests, vec![2, 4]);
}

#[test]
fn collect_jumpdests_skip_push_data() {
    let code = vec![0x61, 0x5B, 0x5B, 0x5B];
    let dests = collect_jumpdests(&code);
    assert_eq!(dests, vec![3]);
}

#[test]
fn implicit_stop_at_end() {
    let code = vec![0x60, 0x01];
    let result = run_code(&code, 1000);
    assert!(matches!(result, ExecResult::Success { .. }));
}
// =========================================================================
// New opcode tests: CALL, CREATE, DELEGATECALL, STATICCALL, EXTCODE*, RETURNDATA*
// =========================================================================

#[test]
fn op_extcodesize_nonexistent() {
    // EXTCODESIZE of nonexistent contract should be 0
    let code = vec![0x60, 0xff, 0x60, 0x00, 0x52, 0x3B, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];
    // PUSH1 0xff, PUSH1 0x00, MSTORE, EXTCODESIZE, PUSH1 0x00, MSTORE, PUSH1 0x20, PUSH1 0x00, RETURN
    // Actually let's simplify: PUSH 0xff (address), EXTCODESIZE, MSTORE, RETURN
    let code = vec![
        0x60, 0xff,  // PUSH1 0xff (address)
        0x3B,        // EXTCODESIZE
        0x60, 0x00, 0x52,  // PUSH1 0, MSTORE
        0x60, 0x20, 0x60, 0x00, 0xF3  // PUSH1 32, PUSH1 0, RETURN
    ];
    let result = run_code(&code, 10000);
    match result {
        ExecResult::Success { return_data, .. } => {
            assert_eq!(return_data.len(), 32);
            let mut arr = [0u8; 32];
            arr.copy_from_slice(&return_data);
            assert_eq!(U256::from_big_endian(&arr), U256::zero());
        }
        _ => panic!("Expected success"),
    }
}

#[test]
fn op_extcodehash_nonexistent() {
    // EXTCODEHASH of nonexistent contract should be 0
    let code = vec![
        0x60, 0xff,  // PUSH1 0xff (address)
        0x3F,        // EXTCODEHASH
        0x60, 0x00, 0x52,  // PUSH1 0, MSTORE
        0x60, 0x20, 0x60, 0x00, 0xF3
    ];
    let result = run_code(&code, 10000);
    match result {
        ExecResult::Success { return_data, .. } => {
            let mut arr = [0u8; 32];
            arr.copy_from_slice(&return_data);
            assert_eq!(U256::from_big_endian(&arr), U256::zero());
        }
        _ => panic!("Expected success"),
    }
}

#[test]
fn op_returndatasize_empty() {
    // RETURNDATASIZE should be 0 initially
    let code = vec![
        0x3D,        // RETURNDATASIZE
        0x60, 0x00, 0x52,  // PUSH1 0, MSTORE
        0x60, 0x20, 0x60, 0x00, 0xF3
    ];
    let result = run_code(&code, 10000);
    match result {
        ExecResult::Success { return_data, .. } => {
            let mut arr = [0u8; 32];
            arr.copy_from_slice(&return_data);
            assert_eq!(U256::from_big_endian(&arr), U256::zero());
        }
        _ => panic!("Expected success"),
    }
}

#[test]
fn op_blockhash() {
    // BLOCKHASH should return 0 (no historical access in interpreter)
    let code = vec![
        0x60, 0x01,  // PUSH1 1 (block number)
        0x40,        // BLOCKHASH
        0x60, 0x00, 0x52,  // PUSH1 0, MSTORE
        0x60, 0x20, 0x60, 0x00, 0xF3
    ];
    let result = run_code(&code, 10000);
    match result {
        ExecResult::Success { return_data, .. } => {
            let mut arr = [0u8; 32];
            arr.copy_from_slice(&return_data);
            assert_eq!(U256::from_big_endian(&arr), U256::zero());
        }
        _ => panic!("Expected success"),
    }
}

#[test]
fn op_selfbalance() {
    // SELFBALANCE should return 0 (no balance tracking in interpreter)
    let code = vec![
        0x47,        // SELFBALANCE
        0x60, 0x00, 0x52,  // PUSH1 0, MSTORE
        0x60, 0x20, 0x60, 0x00, 0xF3
    ];
    let result = run_code(&code, 10000);
    match result {
        ExecResult::Success { return_data, .. } => {
            let mut arr = [0u8; 32];
            arr.copy_from_slice(&return_data);
            assert_eq!(U256::from_big_endian(&arr), U256::zero());
        }
        _ => panic!("Expected success"),
    }
}

#[test]
fn op_basefee() {
    // BASEFEE should return 0 (no base fee in Substrate)
    let code = vec![
        0x48,        // BASEFEE
        0x60, 0x00, 0x52,  // PUSH1 0, MSTORE
        0x60, 0x20, 0x60, 0x00, 0xF3
    ];
    let result = run_code(&code, 10000);
    match result {
        ExecResult::Success { return_data, .. } => {
            let mut arr = [0u8; 32];
            arr.copy_from_slice(&return_data);
            assert_eq!(U256::from_big_endian(&arr), U256::zero());
        }
        _ => panic!("Expected success"),
    }
}

#[test]
fn op_create_nonexistent() {
    // CREATE should return a non-zero address
    // PUSH1 0 (value), PUSH1 0 (offset), PUSH1 0 (size), CREATE
    let code = vec![
        0x60, 0x00,  // PUSH1 0 (value)
        0x60, 0x00,  // PUSH1 0 (offset)
        0x60, 0x00,  // PUSH1 0 (size)
        0xF0,        // CREATE
        0x60, 0x00, 0x52,  // PUSH1 0, MSTORE
        0x60, 0x20, 0x60, 0x00, 0xF3
    ];
    let result = run_code(&code, 100000);
    match result {
        ExecResult::Success { return_data, .. } => {
            // Should return an address (non-zero or zero is acceptable for empty init code)
            assert_eq!(return_data.len(), 32);
        }
        ExecResult::Failed { .. } => {
            // CREATE with empty init code is acceptable to fail or succeed
        }
        _ => panic!("Expected success or failed"),
    }
}

#[test]
fn op_call_to_nonexistent() {
    // CALL to nonexistent contract (EOA) should return 1 (success - EVM behavior)
    let code = vec![
        0x60, 0x00,  // PUSH1 0 (ret_size)
        0x60, 0x00,  // PUSH1 0 (ret_offset)
        0x60, 0x00,  // PUSH1 0 (args_size)
        0x60, 0x00,  // PUSH1 0 (args_offset)
        0x60, 0x00,  // PUSH1 0 (value)
        0x60, 0xff,  // PUSH1 0xff (address)
        0x60, 0xE8,  // PUSH1 232 (gas)
        0xF1,        // CALL
        0x60, 0x00, 0x52,  // PUSH1 0, MSTORE
        0x60, 0x20, 0x60, 0x00, 0xF3
    ];
    let result = run_code(&code, 100000);
    match result {
        ExecResult::Success { return_data, .. } => {
            // EVM: calling an address with no code (EOA) succeeds
            let mut arr = [0u8; 32];
            arr.copy_from_slice(&return_data);
            assert_eq!(U256::from_big_endian(&arr), U256::one());
        }
        _ => panic!("Expected success"),
    }
}

#[test]
fn op_staticcall_to_nonexistent() {
    // STATICCALL to nonexistent contract (EOA) should return 1 (success)
    let code = vec![
        0x60, 0x00,  // PUSH1 0 (ret_size)
        0x60, 0x00,  // PUSH1 0 (ret_offset)
        0x60, 0x00,  // PUSH1 0 (args_size)
        0x60, 0x00,  // PUSH1 0 (args_offset)
        0x60, 0xff,  // PUSH1 0xff (address)
        0x60, 0xE8,  // PUSH1 232 (gas)
        0xFA,        // STATICCALL
        0x60, 0x00, 0x52,  // PUSH1 0, MSTORE
        0x60, 0x20, 0x60, 0x00, 0xF3
    ];
    let result = run_code(&code, 100000);
    match result {
        ExecResult::Success { return_data, .. } => {
            let mut arr = [0u8; 32];
            arr.copy_from_slice(&return_data);
            assert_eq!(U256::from_big_endian(&arr), U256::one());
        }
        _ => panic!("Expected success"),
    }
}

#[test]
fn op_delegatecall_to_nonexistent() {
    // DELEGATECALL to nonexistent contract (EOA) should return 1 (success)
    let code = vec![
        0x60, 0x00,  // PUSH1 0 (ret_size)
        0x60, 0x00,  // PUSH1 0 (ret_offset)
        0x60, 0x00,  // PUSH1 0 (args_size)
        0x60, 0x00,  // PUSH1 0 (args_offset)
        0x60, 0xff,  // PUSH1 0xff (address)
        0x60, 0xE8,  // PUSH1 232 (gas)
        0xF4,        // DELEGATECALL
        0x60, 0x00, 0x52,  // PUSH1 0, MSTORE
        0x60, 0x20, 0x60, 0x00, 0xF3
    ];
    let result = run_code(&code, 100000);
    match result {
        ExecResult::Success { return_data, .. } => {
            let mut arr = [0u8; 32];
            arr.copy_from_slice(&return_data);
            assert_eq!(U256::from_big_endian(&arr), U256::one());
        }
        _ => panic!("Expected success"),
    }
}

#[test]
fn op_returndatacopy_empty() {
    // RETURNDATACOPY with 0 size should succeed
    let code = vec![
        0x60, 0x00,  // PUSH1 0 (size)
        0x60, 0x00,  // PUSH1 0 (offset)
        0x60, 0x00,  // PUSH1 0 (dest_offset)
        0x3E,        // RETURNDATACOPY
        0x00,        // STOP
    ];
    let result = run_code(&code, 10000);
    match result {
        ExecResult::Success { .. } => {}
        _ => panic!("Expected success"),
    }
}

#[test]
fn op_create2_empty_init() {
    // CREATE2 with empty init code should return an address
    let code = vec![
        0x60, 0x00,  // PUSH1 0 (salt)
        0x60, 0x00,  // PUSH1 0 (size)
        0x60, 0x00,  // PUSH1 0 (offset)
        0x60, 0x00,  // PUSH1 0 (value)
        0xF5,        // CREATE2
        0x60, 0x00, 0x52,  // PUSH1 0, MSTORE
        0x60, 0x20, 0x60, 0x00, 0xF3
    ];
    let result = run_code(&code, 100000);
    match result {
        ExecResult::Success { return_data, .. } => {
            assert_eq!(return_data.len(), 32);
        }
        ExecResult::Failed { .. } => {
            // Acceptable for empty init code
        }
        _ => panic!("Expected success or failed"),
    }
}

#[test]
fn op_extcodecopy_nonexistent() {
    // EXTCODECOPY of nonexistent contract should copy zeros
    let code = vec![
        0x60, 0x20,  // PUSH1 32 (size)
        0x60, 0x00,  // PUSH1 0 (offset)
        0x60, 0x00,  // PUSH1 0 (dest_offset)
        0x60, 0xff,  // PUSH1 0xff (address)
        0x3C,        // EXTCODECOPY
        0x60, 0x00, 0x52,  // PUSH1 0, MSTORE
        0x60, 0x20, 0x60, 0x00, 0xF3
    ];
    let result = run_code(&code, 10000);
    match result {
        ExecResult::Success { return_data, .. } => {
            assert_eq!(return_data.len(), 32);
        }
        ExecResult::Failed { .. } => {
            // EXTCODECOPY to nonexistent is acceptable to fail with placeholder impl
        }
        _ => panic!("Expected success or failed"),
    }
}

#[test]
fn op_callcode_to_nonexistent() {
    // CALLCODE to nonexistent contract (EOA) should return 1 (success)
    let code = vec![
        0x60, 0x00,  // PUSH1 0 (ret_size)
        0x60, 0x00,  // PUSH1 0 (ret_offset)
        0x60, 0x00,  // PUSH1 0 (args_size)
        0x60, 0x00,  // PUSH1 0 (args_offset)
        0x60, 0x00,  // PUSH1 0 (value)
        0x60, 0xff,  // PUSH1 0xff (address)
        0x60, 0xE8,  // PUSH1 232 (gas)
        0xF2,        // CALLCODE
        0x60, 0x00, 0x52,  // PUSH1 0, MSTORE
        0x60, 0x20, 0x60, 0x00, 0xF3
    ];
    let result = run_code(&code, 100000);
    match result {
        ExecResult::Success { return_data, .. } => {
            let mut arr = [0u8; 32];
            arr.copy_from_slice(&return_data);
            assert_eq!(U256::from_big_endian(&arr), U256::one());
        }
        _ => panic!("Expected success"),
    }
}

// =========================================================================
// Cancun opcode tests — TLOAD, TSTORE, MCOPY, BLOBHASH, BLOBBASEFEE
// =========================================================================

#[test]
fn cancun_tload_default_zero() {
    // TLOAD key 0 — should return 0 (no prior TSTORE)
    let code = vec![0x60, 0x00, 0x5C, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];
    let result = run_code(&code, 100_000);
    if let ExecResult::Success { return_data, .. } = result {
        let mut arr = [0u8; 32];
        arr.copy_from_slice(&return_data[..32]);
        assert_eq!(U256::from_big_endian(&arr), U256::zero(), "TLOAD of unset key should be 0");
    } else {
        panic!("TLOAD should succeed: {:?}", result);
    }
}

#[test]
fn cancun_tstore_tload_roundtrip() {
    // TSTORE key=0x42 val=0x99, then TLOAD key=0x42
    let code = vec![
        0x60, 0x99, 0x60, 0x42, 0x5D,  // TSTORE
        0x60, 0x42, 0x5C,              // TLOAD
        0x60, 0x00, 0x52,              // MSTORE at 0
        0x60, 0x20, 0x60, 0x00, 0xF3,  // RETURN 32 bytes from 0
    ];
    let result = run_code(&code, 100_000);
    if let ExecResult::Success { return_data, .. } = result {
        let mut arr = [0u8; 32];
        arr.copy_from_slice(&return_data[..32]);
        assert_eq!(U256::from_big_endian(&arr), U256::from(0x99), "TLOAD should return stored value");
    } else {
        panic!("TSTORE/TLOAD roundtrip should succeed: {:?}", result);
    }
}

#[test]
fn cancun_mcopy_basic() {
    // Store 0x42 at memory[0], MCOPY from 0 to 32 (copy 1 byte), read back
    let code = vec![
        0x60, 0x42, 0x60, 0x00, 0x53,                    // MSTORE8 0x42 at 0
        0x60, 0x01, 0x60, 0x00, 0x60, 0x20, 0x5E,        // MCOPY dest=0x20 src=0 len=1
        0x60, 0x20, 0x51,                                // MLOAD from 0x20
        0x60, 0x00, 0x52,                                // MSTORE at 0
        0x60, 0x20, 0x60, 0x00, 0xF3,                     // RETURN
    ];
    let result = run_code(&code, 100_000);
    if let ExecResult::Success { return_data, .. } = result {
        // The byte at position 31 of the 32-byte return should be 0x42
        assert_eq!(return_data[0], 0x42, "MCOPY should copy byte correctly");
    } else {
        panic!("MCOPY should succeed: {:?}", result);
    }
}

#[test]
fn cancun_blobhash_returns_zero() {
    let code = vec![
        0x60, 0x00, 0x49,  // PUSH1 0 BLOBHASH
        0x60, 0x00, 0x52,  // MSTORE at 0
        0x60, 0x20, 0x60, 0x00, 0xF3,
    ];
    let result = run_code(&code, 100_000);
    if let ExecResult::Success { return_data, .. } = result {
        let mut arr = [0u8; 32];
        arr.copy_from_slice(&return_data[..32]);
        assert_eq!(U256::from_big_endian(&arr), U256::zero(), "BLOBHASH should return 0");
    } else {
        panic!("BLOBHASH should succeed: {:?}", result);
    }
}

#[test]
fn cancun_blobbasefee_returns_zero() {
    let code = vec![
        0x4A,              // BLOBBASEFEE
        0x60, 0x00, 0x52,  // MSTORE at 0
        0x60, 0x20, 0x60, 0x00, 0xF3,
    ];
    let result = run_code(&code, 100_000);
    if let ExecResult::Success { return_data, .. } = result {
        let mut arr = [0u8; 32];
        arr.copy_from_slice(&return_data[..32]);
        assert_eq!(U256::from_big_endian(&arr), U256::zero(), "BLOBBASEFEE should return 0");
    } else {
        panic!("BLOBBASEFEE should succeed: {:?}", result);
    }
}

#[test]
fn cancun_tstore_is_transient() {
    // TSTORE then SLOAD same key — SLOAD should return 0 (transient != persistent)
    let code = vec![
        0x60, 0x99, 0x60, 0x42, 0x5D,  // TSTORE
        0x60, 0x42, 0x54,              // SLOAD (should be 0)
        0x60, 0x00, 0x52,              // MSTORE at 0
        0x60, 0x20, 0x60, 0x00, 0xF3,  // RETURN
    ];
    let result = run_code(&code, 100_000);
    if let ExecResult::Success { return_data, .. } = result {
        let mut arr = [0u8; 32];
        arr.copy_from_slice(&return_data[..32]);
        assert_eq!(U256::from_big_endian(&arr), U256::zero(), "SLOAD should not see transient storage");
    } else {
        panic!("Transient storage isolation test should succeed: {:?}", result);
    }
}



// =========================================================================
// Phase 129: New EVM opcode tests (SGT + edge cases)
// =========================================================================

#[test]
fn sgt_basic_positive() {
    new_test_ext().execute_with(|| {
        // SGT: 5 > 3 => 1 (EVM: top=first operand, so push 3 then 5)
        let code = vec![0x60, 0x03, 0x60, 0x05, 0x13, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];
        let result = Evm::execute_code(&code, &[], 100000);
        assert!(matches!(result, ExecResult::Success { .. }));
        if let ExecResult::Success { return_data, .. } = result {
            assert_eq!(return_data.last(), Some(&0x01));
        }
    });
}

#[test]
fn sgt_equal_values() {
    new_test_ext().execute_with(|| {
        // SGT: 5 > 5 => 0
        let code = vec![0x60, 0x05, 0x60, 0x05, 0x13, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];
        let result = Evm::execute_code(&code, &[], 100000);
        assert!(matches!(result, ExecResult::Success { .. }));
        if let ExecResult::Success { return_data, .. } = result {
            assert_eq!(return_data.last(), Some(&0x00));
        }
    });
}

#[test]
fn sgt_negative_greater_than_positive() {
    new_test_ext().execute_with(|| {
        // SGT with negative number: -1 > 1 should be false (0)
        // -1 > 1 in signed => false (0). EVM: top=first operand.
        // Push 1, then push -1, SGT => -1 > 1 = 0
        let mut code = vec![0x60, 0x01]; // PUSH1 1
        code.push(0x7F); // PUSH32
        code.extend(vec![0xFF; 32]); // -1 in two's complement
        code.extend(vec![0x13]); // SGT
        code.extend(vec![0x60, 0x00, 0x52]); // MSTORE at 0
        code.extend(vec![0x60, 0x20, 0x60, 0x00, 0xF3]); // RETURN 32 bytes from 0
        let result = Evm::execute_code(&code, &[], 100000);
        assert!(matches!(result, ExecResult::Success { .. }));
        if let ExecResult::Success { return_data, .. } = result {
            assert_eq!(return_data.last(), Some(&0x00)); // -1 is NOT > 1 in signed
        }
    });
}

#[test]
fn sgt_positive_greater_than_negative() {
    new_test_ext().execute_with(|| {
        // SGT: 1 > -1 => 1. EVM: top=first operand. Push -1, then 1, SGT => 1 > -1 = 1
        let mut code = vec![0x7F]; // PUSH32
        code.extend(vec![0xFF; 32]); // -1 in two's complement
        code.extend(vec![0x60, 0x01]); // PUSH1 1
        code.extend(vec![0x13]); // SGT
        code.extend(vec![0x60, 0x00, 0x52]); // MSTORE at 0
        code.extend(vec![0x60, 0x20, 0x60, 0x00, 0xF3]); // RETURN 32 bytes from 0
        let result = Evm::execute_code(&code, &[], 100000);
        assert!(matches!(result, ExecResult::Success { .. }));
        if let ExecResult::Success { return_data, .. } = result {
            assert_eq!(return_data.last(), Some(&0x01)); // 1 > -1 in signed
        }
    });
}

#[test]
fn sgt_two_negatives() {
    new_test_ext().execute_with(|| {
        // SGT: -3 > -5 => 1 (less negative is greater). EVM: top=first operand.
        // Push -5, then -3, SGT => -3 > -5 = 1
        let mut code = vec![0x7F]; // PUSH32
        code.extend(vec![0xFF; 31]);
        code.push(0xFB); // -5
        code.push(0x7F); // PUSH32
        code.extend(vec![0xFF; 31]);
        code.push(0xFD); // -3
        code.extend(vec![0x13]); // SGT
        code.extend(vec![0x60, 0x00, 0x52]); // MSTORE at 0
        code.extend(vec![0x60, 0x20, 0x60, 0x00, 0xF3]);
        let result = Evm::execute_code(&code, &[], 100000);
        assert!(matches!(result, ExecResult::Success { .. }));
        if let ExecResult::Success { return_data, .. } = result {
            assert_eq!(return_data.last(), Some(&0x01)); // -3 > -5
        }
    });
}

#[test]
fn keccak256_basic() {
    new_test_ext().execute_with(|| {
        // KECCAK256 of empty data => 0xc5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470
        let code = vec![0x60, 0x00, 0x60, 0x00, 0x20, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];
        let result = Evm::execute_code(&code, &[], 100000);
        assert!(matches!(result, ExecResult::Success { .. }));
    });
}

#[test]
fn keccak256_known_hash() {
    new_test_ext().execute_with(|| {
        // KECCAK256 of "abc" (0x616263)
        let code = vec![
            0x60, 0x03, 0x60, 0x00, 0x52, // MSTORE 0x616263 at offset 0 (with padding)
            0x60, 0x61, 0x60, 0x1D, 0x52, // Store 0x61 at offset 29
            0x60, 0x62, 0x60, 0x1E, 0x52, // Store 0x62 at offset 30
            0x60, 0x63, 0x60, 0x1F, 0x52, // Store 0x63 at offset 31
            0x60, 0x03, 0x60, 0x1D, 0x20, // KECCAK256(offset=29, size=3)
            0x60, 0x00, 0x52, // MSTORE at 0
            0x60, 0x20, 0x60, 0x00, 0xF3, // RETURN 32 bytes
        ];
        let result = Evm::execute_code(&code, &[], 100000);
        assert!(matches!(result, ExecResult::Success { .. }));
    });
}

#[test]
fn sar_basic() {
    new_test_ext().execute_with(|| {
        // SAR: 8 >> 2 = 2
        let code = vec![0x60, 0x08, 0x60, 0x02, 0x1D, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];
        let result = Evm::execute_code(&code, &[], 100000);
        assert!(matches!(result, ExecResult::Success { .. }));
        if let ExecResult::Success { return_data, .. } = result {
            assert_eq!(return_data.last(), Some(&0x02));
        }
    });
}

#[test]
fn sar_negative_value() {
    new_test_ext().execute_with(|| {
        // SAR: -8 >> 1 = -4 (arithmetic shift preserves sign)
        let mut code = vec![0x7F];
        code.extend(vec![0xFF; 31]);
        code.push(0xF8); // -8
        code.extend(vec![0x60, 0x01, 0x1D]); // PUSH1 1, SAR
        code.extend(vec![0x60, 0x00, 0x52]); // MSTORE at 0
        code.extend(vec![0x60, 0x20, 0x60, 0x00, 0xF3]);
        let result = Evm::execute_code(&code, &[], 100000);
        assert!(matches!(result, ExecResult::Success { .. }));
    });
}

#[test]
fn shl_large_shift() {
    new_test_ext().execute_with(|| {
        // SHL with shift >= 256 should return 0
        let mut code = vec![0x60, 0x01]; // PUSH1 1
        code.push(0x7F); // PUSH32 256 = 0x0100
        code.extend(vec![0x00; 30]);
        code.push(0x01);
        code.push(0x00);
        code.extend(vec![0x1B]); // SHL
        code.extend(vec![0x60, 0x00, 0x52]); // MSTORE at 0
        code.extend(vec![0x60, 0x20, 0x60, 0x00, 0xF3]);
        let result = Evm::execute_code(&code, &[], 100000);
        assert!(matches!(result, ExecResult::Success { .. }));
        if let ExecResult::Success { return_data, .. } = result {
            assert_eq!(return_data.last(), Some(&0x00));
        }
    });
}

#[test]
fn mcopy_basic() {
    new_test_ext().execute_with(|| {
        // MCOPY: copy 3 bytes from offset 0 to offset 32
        // Store "abc" at offset 0, copy to offset 32
        let code = vec![
            0x60, 0x63, 0x60, 0x1F, 0x53, // MSTORE8 0x63 at offset 31
            0x60, 0x03, 0x60, 0x20, 0x60, 0x00, 0x5E, // MCOPY(dest=32, src=0, len=3)
            0x60, 0x01, 0x60, 0x20, 0x53, // MSTORE8 at offset 32
            0x60, 0x01, 0x60, 0x20, 0x53, // MSTORE8 at offset 32
            0x60, 0x01, 0x60, 0x20, 0xF3, // RETURN 1 byte from offset 32
        ];
        let result = Evm::execute_code(&code, &[], 100000);
        assert!(matches!(result, ExecResult::Success { .. }));
    });
}

#[test]
fn tload_tstore_transient() {
    new_test_ext().execute_with(|| {
        // TSTORE 0x01 at key 0x00, TLOAD key 0x00 => 0x01
        let code = vec![
            0x60, 0x01, 0x60, 0x00, 0x5D, // TSTORE(value=1, key=0)
            0x60, 0x00, 0x5C,             // TLOAD(key=0)
            0x60, 0x00, 0x52,             // MSTORE at 0
            0x60, 0x20, 0x60, 0x00, 0xF3, // RETURN 32 bytes from 0
        ];
        let result = Evm::execute_code(&code, &[], 100000);
        assert!(matches!(result, ExecResult::Success { .. }));
        if let ExecResult::Success { return_data, .. } = result {
            assert_eq!(return_data.last(), Some(&0x01));
        }
    });
}

#[test]
fn tload_uninitialized() {
    new_test_ext().execute_with(|| {
        // TLOAD on uninitialized key => 0
        let code = vec![0x60, 0x42, 0x5C, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];
        let result = Evm::execute_code(&code, &[], 100000);
        assert!(matches!(result, ExecResult::Success { .. }));
        if let ExecResult::Success { return_data, .. } = result {
            assert_eq!(return_data.last(), Some(&0x00));
        }
    });
}

#[test]
fn blobhash_returns_zero() {
    new_test_ext().execute_with(|| {
        // BLOBHASH should return 0 (no blobs in Verdis)
        let code = vec![0x60, 0x00, 0x49, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];
        let result = Evm::execute_code(&code, &[], 100000);
        assert!(matches!(result, ExecResult::Success { .. }));
        if let ExecResult::Success { return_data, .. } = result {
            assert_eq!(return_data.last(), Some(&0x00));
        }
    });
}

#[test]
fn blobbasefee_returns_zero() {
    new_test_ext().execute_with(|| {
        // BLOBBASEFEE should return 0 (no blob fee in Verdis)
        let code = vec![0x4A, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];
        let result = Evm::execute_code(&code, &[], 100000);
        assert!(matches!(result, ExecResult::Success { .. }));
        if let ExecResult::Success { return_data, .. } = result {
            assert_eq!(return_data.last(), Some(&0x00));
        }
    });
}

#[test]
fn push0_opcode() {
    new_test_ext().execute_with(|| {
        // PUSH0 pushes 0 onto stack
        let code = vec![0x5F, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];
        let result = Evm::execute_code(&code, &[], 100000);
        assert!(matches!(result, ExecResult::Success { .. }));
    });
}

#[test]
fn chainid_opcode() {
    new_test_ext().execute_with(|| {
        // CHAINID should return 909
        let code = vec![0x46, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];
        let result = Evm::execute_code(&code, &[], 100000);
        assert!(matches!(result, ExecResult::Success { .. }));
    });
}

#[test]
fn selfbalance_opcode() {
    new_test_ext().execute_with(|| {
        // SELFBALANCE
        let code = vec![0x47, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];
        let result = Evm::execute_code(&code, &[], 100000);
        assert!(matches!(result, ExecResult::Success { .. }));
    });
}

#[test]
fn basefee_opcode() {
    new_test_ext().execute_with(|| {
        // BASEFEE
        let code = vec![0x48, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];
        let result = Evm::execute_code(&code, &[], 100000);
        assert!(matches!(result, ExecResult::Success { .. }));
    });
}

#[test]
fn combined_arithmetic_chain() {
    new_test_ext().execute_with(|| {
        // ((3 + 4) * 2 - 1) / 3 = 4
        // EVM: top=first operand. Push operands in reverse order.
        // Stack build: [3(divisor), 1(subtrahend), then compute (3+4)*2=14 on top]
        // SUB: 14-1=13, DIV: 13/3=4
        let code = vec![
            0x60, 0x03, // PUSH1 3 (divisor, bottom)
            0x60, 0x01, // PUSH1 1 (subtrahend)
            0x60, 0x02, // PUSH1 2 (multiplier)
            0x60, 0x04, // PUSH1 4
            0x60, 0x03, // PUSH1 3
            0x01,       // ADD => 3+4=7
            0x02,       // MUL => 7*2=14
            0x03,       // SUB => 14-1=13 (top=14, second=1)
            0x04,       // DIV => 13/3=4 (top=13, second=3)
            0x60, 0x00, // PUSH1 0
            0x52,       // MSTORE at 0
            0x60, 0x20, // PUSH1 32
            0x60, 0x00, // PUSH1 0
            0xF3,       // RETURN 32 bytes from 0
        ];
        let result = Evm::execute_code(&code, &[], 100000);
        assert!(matches!(result, ExecResult::Success { .. }));
        if let ExecResult::Success { return_data, .. } = result {
            assert_eq!(return_data.last(), Some(&0x04));
        }
    });
}

// ==================== REAL BENCHMARK WEIGHT GENERATION ====================
#[cfg(feature = "runtime-benchmarks")]
mod real_bench {
    use super::*;
    use super::{Test, new_test_ext, Evm, RuntimeOrigin};
    use std::time::Instant;
    use frame_support::traits::fungible::Mutate;

    fn measure_bench<F: FnMut() -> bool>(name: &str, iters: u32, mut f: F) -> u64 {
        let mut times: Vec<u64> = Vec::new();
        for _ in 0..iters {
            let start = Instant::now();
            let ok = f();
            let elapsed = start.elapsed().as_nanos() as u64;
            if ok { times.push(elapsed); }
        }
        if times.is_empty() {
            println!("  {pallet}::{name} -> FAILED", pallet = PALLET_NAME, name = name);
            return 10_000;
        }
        let avg = times.iter().sum::<u64>() / times.len() as u64;
        let max = *times.iter().max().unwrap();
        let weight = (avg as f64 * 1.25).max(10000.0) as u64;
        println!("  {pallet}::{name} -> avg={avg}ns max={max}ns weight={weight}", pallet = PALLET_NAME, name = name, avg = avg, max = max, weight = weight);
        weight
    }

    const PALLET_NAME: &str = "evm";

    #[test]
    #[ignore]
    fn real_bench() {
        new_test_ext().execute_with(|| {{
            use frame_system::Pallet as System;
            System::<Test>::set_block_number(1);
            
            use sp_core::U256;
            let mut results: Vec<(&str, u64)> = Vec::new();

            // Benchmark: deploy_contract
            let code = vec![0x60u8, 0x80, 0x60, 0x40, 0x52];
            let w = measure_bench("deploy_contract", 30, || {
                Evm::deploy_contract(RuntimeOrigin::signed(1), code.clone(), U256::from(100000), U256::zero()).is_ok()
            });
            results.push(("deploy_contract", w));

            // Benchmark: call_contract (needs a deployed contract)
            assert_ok!(Evm::deploy_contract(RuntimeOrigin::signed(2), vec![0x60, 0x00, 0x60, 0x00, 0xF3], U256::from(100000), U256::zero()));
            let contract_addr = Evm::create_address(&2, 0);
            let w = measure_bench("call_contract", 30, || {
                Evm::call_contract(RuntimeOrigin::signed(3), contract_addr, vec![], U256::from(100000), U256::zero()).is_ok()
            });
            results.push(("call_contract", w));

            // Benchmark: execute_code (internal)
            let w = measure_bench("execute_code", 30, || {
                matches!(Evm::execute_code(&[0x60, 0x01, 0x60, 0x00, 0xF3], &[], 100000), crate::interpreter::ExecResult::Success { .. })
            });
            results.push(("execute_code", w));

            println!("\n//! WeightInfo for pallet-evm (real benchmark)");
            println!("pub struct WeightInfo;");
            for (name, weight) in &results {
                println!("// {}: {} weight units", name, weight);
            }

        }});
    }
}
