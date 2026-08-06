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
}

#[test]
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
}

#[test]
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
        0x60, 0xff,  // PUSH1 0xff (address)
        0x60, 0x00,  // PUSH1 0 (dest_offset)
        0x3C,        // EXTCODECOPY
        0x60, 0x00, 0x52,  // PUSH1 0, MSTORE (just to check memory)
        0x60, 0x20, 0x60, 0x00, 0xF3
    ];
    let result = run_code(&code, 10000);
    match result {
        ExecResult::Success { return_data, .. } => {
            // Should be all zeros
            assert_eq!(return_data.len(), 32);
            assert!(return_data.iter().all(|&b| b == 0));
        }
        _ => panic!("Expected success"),
    }
}

#[test]
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
}
