import re

path = '/opt/verdis-chain/pallets/evm/src/tests.rs'

with open(path) as f:
    c = f.read()

# Fix run_code to use externalities
old = """fn run_code(code: &[u8], gas: u64) -> ExecResult {
    Evm::execute_code(code, &[], gas)
}"""

new = """fn run_code(code: &[u8], gas: u64) -> ExecResult {
    new_test_ext().execute_with(|| {
        Evm::execute_code(code, &[], gas)
    })
}"""

c = c.replace(old, new)

with open(path, 'w') as f:
    f.write(c)

print('Fixed run_code to use externalities')
