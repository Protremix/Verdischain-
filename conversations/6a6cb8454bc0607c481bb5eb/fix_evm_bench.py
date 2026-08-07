#!/usr/bin/env python3
"""Fix EVM benchmark - use Evm not EVM"""

path = "/opt/verdis-chain/pallets/evm/src/tests.rs"
with open(path, "r") as f:
    c = f.read()

# Replace EVM:: with Evm::
c = c.replace("EVM::deploy_contract", "Evm::deploy_contract")
c = c.replace("EVM::call_contract", "Evm::call_contract")
c = c.replace("EVM::execute_code", "Evm::execute_code")
c = c.replace("EVM::create_address", "Evm::create_address")

# Also fix the U256 gas values to match existing test patterns
c = c.replace("U256::from(1_000_000u64)", "U256::from(100000)")

# Fix the super import - EVM module needs to import from super
c = c.replace(
    "use super::*;\n    use super::{Test, new_test_ext};",
    "use super::*;\n    use super::{Test, new_test_ext, Evm, RuntimeOrigin};"
)

with open(path, "w") as f:
    f.write(c)
print("Fixed EVM benchmark - using Evm struct name")
