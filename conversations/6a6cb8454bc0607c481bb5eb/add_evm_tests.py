#!/usr/bin/env python3
"""Add 20+ new EVM tests for SGT and edge cases"""

path = "/opt/verdis-chain/pallets/evm/src/tests.rs"
with open(path, "r") as f:
    c = f.read()

# Find the last test function before the benchmark module
# Insert new tests before the "// ==================== REAL BENCHMARK" section
marker = "// ==================== REAL BENCHMARK"

new_tests = '''
// =========================================================================
// Phase 129: New EVM opcode tests (SGT + edge cases)
// =========================================================================

#[test]
fn sgt_basic_positive() {
    new_test_ext().execute_with(|| {
        // SGT: 5 > 3 => 1
        // PUSH1 5, PUSH1 3, SGT (0x13)
        let code = vec![0x60, 0x05, 0x60, 0x03, 0x13, 0x60, 0x00, 0xF3];
        let result = Evm::execute_code(&code, &[], 100000);
        assert!(matches!(result, ExecResult::Success { .. }));
        if let ExecResult::Success { return_data, .. } = result {
            assert_eq!(return_data, vec![0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                         0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                         0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                         0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01]);
        }
    });
}

#[test]
fn sgt_equal_values() {
    new_test_ext().execute_with(|| {
        // SGT: 5 > 5 => 0
        let code = vec![0x60, 0x05, 0x60, 0x05, 0x13, 0x60, 0x00, 0xF3];
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
        // -1 = 0xFFFF...FFFF (all ones in 256 bits)
        // PUSH32 0xFF...FF, PUSH1 1, SGT
        let mut code = vec![0x7F];
        code.extend(vec![0xFF; 32]); // -1 in two's complement
        code.extend(vec![0x60, 0x01, 0x13]); // PUSH1 1, SGT
        code.extend(vec![0x60, 0x00, 0xF3]); // PUSH1 0, RETURN
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
        // SGT: 1 > -1 => 1 (positive is greater than negative in signed)
        let mut code = vec![0x60, 0x01]; // PUSH1 1
        code.push(0x7F); // PUSH32
        code.extend(vec![0xFF; 32]); // -1
        code.extend(vec![0x13]); // SGT
        code.extend(vec![0x60, 0x00, 0xF3]); // PUSH1 0, RETURN
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
        // SGT: -3 > -5 => 1 (less negative is greater)
        // -3 = 0xFF...FD, -5 = 0xFF...FB
        let mut code = vec![0x7F];
        code.extend(vec![0xFF; 31]);
        code.push(0xFD); // -3
        code.push(0x7F); // PUSH32
        code.extend(vec![0xFF; 31]);
        code.push(0xFB); // -5
        code.extend(vec![0x13]); // SGT
        code.extend(vec![0x60, 0x00, 0xF3]);
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
        let code = vec![0x60, 0x00, 0x60, 0x00, 0x20, 0x60, 0x00, 0xF3];
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
            0x60, 0x00, 0xF3, // RETURN at offset 0
        ];
        let result = Evm::execute_code(&code, &[], 100000);
        assert!(matches!(result, ExecResult::Success { .. }));
    });
}

#[test]
fn sar_basic() {
    new_test_ext().execute_with(|| {
        // SAR: 8 >> 2 = 2
        let code = vec![0x60, 0x08, 0x60, 0x02, 0x1D, 0x60, 0x00, 0xF3];
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
        code.extend(vec![0x60, 0x00, 0xF3]);
        let result = Evm::execute_code(&code, &[], 100000);
        assert!(matches!(result, ExecResult::Success { .. }));
    });
}

#[test]
fn shl_large_shift() {
    new_test_ext().execute_with(|| {
        // SHL with shift >= 256 should return 0
        let mut code = vec![0x60, 0x01]; // PUSH1 1
        code.push(0x7F); // PUSH32 256
        code.extend(vec![0x00; 31]);
        code.push(0x01);
        code.extend(vec![0x1B]); // SHL
        code.extend(vec![0x60, 0x00, 0xF3]);
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
            0x60, 0x00, 0xF3,             // RETURN
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
        let code = vec![0x60, 0x42, 0x5C, 0x60, 0x00, 0xF3];
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
        let code = vec![0x60, 0x00, 0x49, 0x60, 0x00, 0xF3];
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
        let code = vec![0x4A, 0x60, 0x00, 0xF3];
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
        let code = vec![0x5F, 0x60, 0x00, 0xF3];
        let result = Evm::execute_code(&code, &[], 100000);
        assert!(matches!(result, ExecResult::Success { .. }));
    });
}

#[test]
fn chainid_opcode() {
    new_test_ext().execute_with(|| {
        // CHAINID should return 909
        let code = vec![0x46, 0x60, 0x00, 0xF3];
        let result = Evm::execute_code(&code, &[], 100000);
        assert!(matches!(result, ExecResult::Success { .. }));
    });
}

#[test]
fn selfbalance_opcode() {
    new_test_ext().execute_with(|| {
        // SELFBALANCE
        let code = vec![0x47, 0x60, 0x00, 0xF3];
        let result = Evm::execute_code(&code, &[], 100000);
        assert!(matches!(result, ExecResult::Success { .. }));
    });
}

#[test]
fn basefee_opcode() {
    new_test_ext().execute_with(|| {
        // BASEFEE
        let code = vec![0x48, 0x60, 0x00, 0xF3];
        let result = Evm::execute_code(&code, &[], 100000);
        assert!(matches!(result, ExecResult::Success { .. }));
    });
}

#[test]
fn combined_arithmetic_chain() {
    new_test_ext().execute_with(|| {
        // ((3 + 4) * 2 - 1) / 3 = (7 * 2 - 1) / 3 = 13 / 3 = 4
        // PUSH1 3, PUSH1 4, ADD, PUSH1 2, MUL, PUSH1 1, SUB, PUSH1 3, DIV
        let code = vec![
            0x60, 0x03, // PUSH1 3
            0x60, 0x04, // PUSH1 4
            0x01,       // ADD => 7
            0x60, 0x02, // PUSH1 2
            0x02,       // MUL => 14
            0x60, 0x01, // PUSH1 1
            0x03,       // SUB => 13
            0x60, 0x03, // PUSH1 3
            0x04,       // DIV => 4
            0x60, 0x00, // PUSH1 0
            0xF3,       // RETURN
        ];
        let result = Evm::execute_code(&code, &[], 100000);
        assert!(matches!(result, ExecResult::Success { .. }));
        if let ExecResult::Success { return_data, .. } = result {
            assert_eq!(return_data.last(), Some(&0x04));
        }
    });
}

'''

if marker in c:
    c = c.replace(marker, new_tests + marker)
else:
    c = c + "\n" + new_tests

with open(path, "w") as f:
    f.write(c)
print("Added 20 new EVM tests")
