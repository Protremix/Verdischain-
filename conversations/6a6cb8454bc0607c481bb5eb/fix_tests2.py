import re

path = '/opt/verdis-chain/pallets/evm/src/tests.rs'

with open(path) as f:
    c = f.read()

# 1. Add run_code_with_calldata helper after run_code
old_run_code = """fn run_code(code: &[u8], gas: u64) -> ExecResult {
    new_test_ext().execute_with(|| {
        Evm::execute_code(code, &[], gas)
    })
}"""

new_run_code = """fn run_code(code: &[u8], gas: u64) -> ExecResult {
    new_test_ext().execute_with(|| {
        Evm::execute_code(code, &[], gas)
    })
}

fn run_code_with_calldata(code: &[u8], calldata: &[u8], gas: u64) -> ExecResult {
    new_test_ext().execute_with(|| {
        Evm::execute_code(code, calldata, gas)
    })
}"""

c = c.replace(old_run_code, new_run_code)

# 2. Fix op_calldatasize to use run_code_with_calldata
old_calldatasize = """    let result = Evm::execute_code(&code, &[0x01, 0x02, 0x03], 1000);"""
new_calldatasize = """    let result = run_code_with_calldata(&code, &[0x01, 0x02, 0x03], 1000);"""
c = c.replace(old_calldatasize, new_calldatasize)

# 3. Fix op_calldataload to use run_code_with_calldata
old_calldataload = """    let result = Evm::execute_code(&code, &calldata, 1000);"""
new_calldataload = """    let result = run_code_with_calldata(&code, &calldata, 1000);"""
c = c.replace(old_calldataload, new_calldataload)

with open(path, 'w') as f:
    f.write(c)
print('Fixed test helpers')
