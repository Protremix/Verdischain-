#!/usr/bin/env python3
"""Fix EVM benchmark - execute_code returns ExecResult, not Result"""

path = "/opt/verdis-chain/pallets/evm/src/tests.rs"
with open(path, "r") as f:
    c = f.read()

# execute_code returns ExecResult enum, not Result
# Check for Success variant
c = c.replace(
    "Evm::execute_code(&[0x60, 0x01, 0x60, 0x00, 0xF3], &[], 1_000_000).is_ok()",
    "matches!(Evm::execute_code(&[0x60, 0x01, 0x60, 0x00, 0xF3], &[], 100000), crate::interpreter::ExecResult::Success { .. })"
)

with open(path, "w") as f:
    f.write(c)
print("Fixed EVM execute_code benchmark")
