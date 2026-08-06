import re

path = '/opt/verdis-chain/pallets/evm/src/tests.rs'

with open(path) as f:
    c = f.read()

# Fix CALL test - calling nonexistent address (EOA) returns 1 (success)
c = c.replace(
    """#[test]
fn op_call_to_nonexistent() {
    // CALL to nonexistent contract should return 0 (failure)
    // PUSH1 1000 (gas), PUSH1 0xff (addr), PUSH1 0 (value), PUSH1 0 (args_off), PUSH1 0 (args_sz), PUSH1 0 (ret_off), PUSH1 0 (ret_sz), CALL
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
            // CALL to nonexistent returns 0 (failure) on stack
            let mut arr = [0u8; 32];
            arr.copy_from_slice(&return_data);
            assert_eq!(U256::from_big_endian(&arr), U256::zero());
        }
        _ => panic!("Expected success"),
    }
}""",
    """#[test]
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
}"""
)

# Fix STATICCALL test similarly
c = c.replace(
    """#[test]
fn op_staticcall_to_nonexistent() {
    // STATICCALL to nonexistent contract should return 0
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
            assert_eq!(U256::from_big_endian(&arr), U256::zero());
        }
        _ => panic!("Expected success"),
    }
}""",
    """#[test]
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
}"""
)

# Fix DELEGATECALL test similarly
c = c.replace(
    """#[test]
fn op_delegatecall_to_nonexistent() {
    // DELEGATECALL to nonexistent contract should return 0
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
            assert_eq!(U256::from_big_endian(&arr), U256::zero());
        }
        _ => panic!("Expected success"),
    }
}""",
    """#[test]
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
}"""
)

# Fix CALLCODE test similarly
c = c.replace(
    """#[test]
fn op_callcode_to_nonexistent() {
    // CALLCODE to nonexistent contract should return 0
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
            assert_eq!(U256::from_big_endian(&arr), U256::zero());
        }
        _ => panic!("Expected success"),
    }
}""",
    """#[test]
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
}"""
)

# Fix EXTCODECOPY test - check the actual failure
# The EXTCODECOPY might be returning different data than expected
# Let me check - the issue might be with operand order
# EXTCODECOPY pops: address, dest_offset, offset, size (in EVM spec)
# But my implementation pops: addr, dest_offset, offset, size
# Actually, EVM spec says: EXTCODECOPY pops (addr, destOffset, offset, size) from stack
# Let me check the test code order

# The test code pushes: size(0x20), offset(0x00), addr(0xff), dest_offset(0x00)
# So the stack is: dest_offset, addr, offset, size (top to bottom)
# EXTCODECOPY pops: addr (top), dest_offset, offset, size (per EVM)
# Wait, no. EVM pops in order: address, destOffset, offset, size
# Stack is LIFO. Push order: size, offset, addr, dest_offset
# Stack top to bottom: dest_offset, addr, offset, size
# Pop 1 (addr): dest_offset... that's wrong

# Actually, EVM spec: EXTCODECOPY pops address, destOffset, offset, size from stack
# Stack top is the last pushed. Push order: 0x20(size), 0x00(offset), 0xff(addr), 0x00(dest)
# Stack: [0x00(dest), 0xff(addr), 0x00(offset), 0x20(size)]
# Pop order: addr=0x00(dest)?? No...

# Actually the push order in the test is:
# PUSH1 0x20 (size) -> stack: [0x20]
# PUSH1 0x00 (offset) -> stack: [0x20, 0x00]  Wait, PUSH adds to top
# So after all pushes: stack top is 0x00 (dest_offset), then 0xff (addr), then 0x00 (offset), then 0x20 (size)
# EXTCODECOPY pops: addr=0x00, dest_offset=0xff, offset=0x00, size=0x20
# That's wrong! The address is 0x00 not 0xff!

# The fix: reorder the pushes in the test
# We need: addr on top, then dest_offset, then offset, then size
# Push order should be: size, offset, dest_offset, addr

old_extcodecopy = """    let code = vec![
        0x60, 0x20,  // PUSH1 32 (size)
        0x60, 0x00,  // PUSH1 0 (offset)
        0x60, 0xff,  // PUSH1 0xff (address)
        0x60, 0x00,  // PUSH1 0 (dest_offset)
        0x3C,        // EXTCODECOPY
        0x60, 0x00, 0x52,  // PUSH1 0, MSTORE (just to check memory)
        0x60, 0x20, 0x60, 0x00, 0xF3
    ];"""

new_extcodecopy = """    let code = vec![
        0x60, 0x20,  // PUSH1 32 (size)
        0x60, 0x00,  // PUSH1 0 (offset)
        0x60, 0x00,  // PUSH1 0 (dest_offset)
        0x60, 0xff,  // PUSH1 0xff (address)
        0x3C,        // EXTCODECOPY
        0x60, 0x00, 0x52,  // PUSH1 0, MSTORE
        0x60, 0x20, 0x60, 0x00, 0xF3
    ];"""

c = c.replace(old_extcodecopy, new_extcodecopy)

with open(path, 'w') as f:
    f.write(c)
print('Fixed test expectations for EVM call opcodes')
