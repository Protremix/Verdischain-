// Cancun opcode tests — TLOAD, TSTORE, MCOPY, BLOBHASH, BLOBBASEFEE
// These are appended to the existing tests.rs

#[cfg(test)]
mod cancun_tests {
    use super::*;
    use crate::interpreter::{execute, ExecutionContext, ExecResult, EvmHost, VerdisHost};

    fn make_ctx<'a>(code: &'a [u8], calldata: &'a [u8]) -> ExecutionContext<'a> {
        ExecutionContext {
            caller: H160::zero(),
            address: H160::zero(),
            origin: H160::zero(),
            callvalue: U256::zero(),
            calldata,
            code,
            gas_limit: 1_000_000,
            gas_used: 0,
            chain_id: 909,
            block_number: 1,
            block_timestamp: 0,
            block_gaslimit: 30_000_000,
            coinbase: H160::zero(),
            gas_price: U256::zero(),
            prev_randao: H256::zero(),
            base_fee: U256::zero(),
            self_balance: U256::zero(),
            balance: U256::zero(),
            return_data: Vec::new(),
        }
    }

    #[test]
    fn tload_default_zero() {
        // TLOAD key 0 — should return 0 (no prior TSTORE)
        // PUSH1 0x00 (key) TLOAD PUSH1 0x00 MSTORE PUSH1 0x20 PUSH1 0x00 RETURN
        let code = vec![0x60, 0x00, 0x5C, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];
        let calldata = vec![];
        let host = VerdisHost::<Test>::new();
        let result = host.execute_code(&code, &calldata, 1_000_000);
        match result {
            ExecResult::Success { return_data, .. } => {
                let val = U256::from_big_endian(&return_data);
                assert_eq!(val, U256::zero(), "TLOAD of unset key should be 0");
            }
            _ => panic!("TLOAD should succeed"),
        }
    }

    #[test]
    fn tstore_tload_roundtrip() {
        // TSTORE key=0x42 val=0x99, then TLOAD key=0x42
        // PUSH1 0x99 PUSH1 0x42 TSTORE
        // PUSH1 0x42 TLOAD
        // PUSH1 0x00 MSTORE PUSH1 0x20 PUSH1 0x00 RETURN
        let code = vec![
            0x60, 0x99, 0x60, 0x42, 0x5D,  // TSTORE
            0x60, 0x42, 0x5C,              // TLOAD
            0x60, 0x00, 0x52,              // MSTORE at 0
            0x60, 0x20, 0x60, 0x00, 0xF3,  // RETURN 32 bytes from 0
        ];
        let calldata = vec![];
        let host = VerdisHost::<Test>::new();
        let result = host.execute_code(&code, &calldata, 1_000_000);
        match result {
            ExecResult::Success { return_data, .. } => {
                let val = U256::from_big_endian(&return_data);
                assert_eq!(val, U256::from(0x99), "TLOAD should return stored value");
            }
            _ => panic!("TSTORE/TLOAD roundtrip should succeed"),
        }
    }

    #[test]
    fn mcopy_basic() {
        // Store 0x42 at memory[0], MCOPY from 0 to 32 (copy 1 byte), read back
        // PUSH1 0x42 PUSH1 0x00 MSTORE8  (store 0x42 at memory[0])
        // PUSH1 0x01 PUSH1 0x00 PUSH1 0x20 MCOPY (copy 1 byte from offset 0 to 32)
        // PUSH1 0x20 MLOAD (load 32 bytes from 32) 
        // PUSH1 0x00 MSTORE PUSH1 0x20 PUSH1 0x00 RETURN
        let code = vec![
            0x60, 0x42, 0x60, 0x00, 0x53,                    // MSTORE8 0x42 at 0
            0x60, 0x01, 0x60, 0x00, 0x60, 0x20, 0x5E,        // MCOPY dest=0x20 src=0 len=1
            0x60, 0x20, 0x51,                                // MLOAD from 0x20
            0x60, 0x00, 0x52,                                // MSTORE at 0
            0x60, 0x20, 0x60, 0x00, 0xF3,                     // RETURN
        ];
        let calldata = vec![];
        let host = VerdisHost::<Test>::new();
        let result = host.execute_code(&code, &calldata, 1_000_000);
        match result {
            ExecResult::Success { return_data, .. } => {
                // The byte at position 31 of the 32-byte return should be 0x42
                assert_eq!(return_data[31], 0x42, "MCOPY should copy byte correctly");
            }
            _ => panic!("MCOPY should succeed"),
        }
    }

    #[test]
    fn blobhash_returns_zero() {
        // BLOBHASH — push index 0, then BLOBHASH, should return 0
        // PUSH1 0x00 BLOBHASH PUSH1 0x00 MSTORE PUSH1 0x20 PUSH1 0x00 RETURN
        let code = vec![
            0x60, 0x00, 0x49,  // PUSH1 0 BLOBHASH
            0x60, 0x00, 0x52,  // MSTORE at 0
            0x60, 0x20, 0x60, 0x00, 0xF3,
        ];
        let calldata = vec![];
        let host = VerdisHost::<Test>::new();
        let result = host.execute_code(&code, &calldata, 1_000_000);
        match result {
            ExecResult::Success { return_data, .. } => {
                let val = U256::from_big_endian(&return_data);
                assert_eq!(val, U256::zero(), "BLOBHASH should return 0 (no blobs)");
            }
            _ => panic!("BLOBHASH should succeed"),
        }
    }

    #[test]
    fn blobbasefee_returns_zero() {
        // BLOBBASEFEE — should return 0
        let code = vec![
            0x4A,              // BLOBBASEFEE
            0x60, 0x00, 0x52,  // MSTORE at 0
            0x60, 0x20, 0x60, 0x00, 0xF3,
        ];
        let calldata = vec![];
        let host = VerdisHost::<Test>::new();
        let result = host.execute_code(&code, &calldata, 1_000_000);
        match result {
            ExecResult::Success { return_data, .. } => {
                let val = U256::from_big_endian(&return_data);
                assert_eq!(val, U256::zero(), "BLOBBASEFEE should return 0");
            }
            _ => panic!("BLOBBASEFEE should succeed"),
        }
    }

    #[test]
    fn tstore_is_transient() {
        // TSTORE in one execution should NOT persist to SLOAD
        // TSTORE key=0x42 val=0x99, then SLOAD key=0x42 should return 0
        // PUSH1 0x99 PUSH1 0x42 TSTORE
        // PUSH1 0x42 SLOAD
        // PUSH1 0x00 MSTORE PUSH1 0x20 PUSH1 0x00 RETURN
        let code = vec![
            0x60, 0x99, 0x60, 0x42, 0x5D,  // TSTORE
            0x60, 0x42, 0x54,              // SLOAD (should be 0, not 0x99)
            0x60, 0x00, 0x52,              // MSTORE at 0
            0x60, 0x20, 0x60, 0x00, 0xF3,  // RETURN
        ];
        let calldata = vec![];
        let host = VerdisHost::<Test>::new();
        let result = host.execute_code(&code, &calldata, 1_000_000);
        match result {
            ExecResult::Success { return_data, .. } => {
                let val = U256::from_big_endian(&return_data);
                assert_eq!(val, U256::zero(), "SLOAD should not see transient storage");
            }
            _ => panic!("Transient storage isolation test should succeed"),
        }
    }
}
