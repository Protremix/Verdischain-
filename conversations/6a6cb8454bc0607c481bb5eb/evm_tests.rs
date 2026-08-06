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
    Evm::execute_code(code, &[], gas)
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
        assert_eq!(U256::from_big_endian(&arr), U256::from(&expected[..]));
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
    let code = vec![0x60, 0x01, 0x60, 0x02, 0x90, 0x03, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];
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
        0x60, 0x06, 0x56, 0x00, 0x5B, 0x60, 0x42, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3,
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
        0x60, 0x01, 0x60, 0x07, 0x57, 0x00, 0x5B, 0x60, 0x42, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3,
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
    let code = vec![0x60, 0x01, 0x60, 0x08, 0x1C, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];
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
    let result = Evm::execute_code(&code, &[0x01, 0x02, 0x03], 1000);
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
    let result = Evm::execute_code(&code, &calldata, 1000);
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
