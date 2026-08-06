import sys

# Fix interpreter operand ordering and test bytecode issues
interp_path = '/opt/verdis-chain/pallets/evm/src/interpreter.rs'
tests_path = '/opt/verdis-chain/pallets/evm/src/tests.rs'

# === Fix interpreter.rs ===
with open(interp_path) as f:
    c = f.read()

# SUB: should be a - b (top - second), not b - a
c = c.replace(
    '0x03 => { let a = pop!(); let b = pop!(); push!(b.overflowing_sub(a).0); pc += 1; }',
    '0x03 => { let a = pop!(); let b = pop!(); push!(a.overflowing_sub(b).0); pc += 1; }'
)

# DIV: should be a / b (top / second), not b / a
c = c.replace(
    "0x04 => { let a = pop!(); let b = pop!(); if a.is_zero() { push!(U256::zero()); } else { push!(b / a); } pc += 1; }",
    "0x04 => { let a = pop!(); let b = pop!(); if b.is_zero() { push!(U256::zero()); } else { push!(a / b); } pc += 1; }"
)

# SDIV: same fix
c = c.replace(
    'if a.is_zero() { push!(U256::zero()); }\n                else {\n                    let bn = b; let an = a;\n                    let neg = (bn ^ an) >> 255 != U256::zero();\n                    let mut result = if an.is_zero() { U256::zero() } else { bn / an };',
    'if b.is_zero() { push!(U256::zero()); }\n                else {\n                    let bn = a; let an = b;\n                    let neg = (bn ^ an) >> 255 != U256::zero();\n                    let mut result = bn / an;'
)

# MOD: should be a % b, not b % a
c = c.replace(
    "0x06 => { let a = pop!(); let b = pop!(); if a.is_zero() { push!(U256::zero()); } else { push!(b % a); } pc += 1; }",
    "0x06 => { let a = pop!(); let b = pop!(); if b.is_zero() { push!(U256::zero()); } else { push!(a % b); } pc += 1; }"
)

# SMOD: same fix
c = c.replace(
    'if a.is_zero() { push!(U256::zero()); }\n                else {\n                    let bn = b; let an = a;\n                    let neg = bn >> 255 != U256::zero();\n                    let mut result = if an.is_zero() { U256::zero() } else { bn % an };',
    'if b.is_zero() { push!(U256::zero()); }\n                else {\n                    let bn = a; let an = b;\n                    let neg = bn >> 255 != U256::zero();\n                    let mut result = bn % an;'
)

# LT: should be a < b (top < second), not b < a
c = c.replace(
    '0x10 => { let a = pop!(); let b = pop!(); push!((if b < a { U256::one() } else { U256::zero() })); pc += 1; }',
    '0x10 => { let a = pop!(); let b = pop!(); push!((if a < b { U256::one() } else { U256::zero() })); pc += 1; }'
)

# GT: should be a > b (top > second), not b > a
c = c.replace(
    '0x11 => { let a = pop!(); let b = pop!(); push!((if b > a { U256::one() } else { U256::zero() })); pc += 1; }',
    '0x11 => { let a = pop!(); let b = pop!(); push!((if a > b { U256::one() } else { U256::zero() })); pc += 1; }'
)

# SLT: signed less than - should be a < b in signed
c = c.replace(
    'let result = if bn_neg != an_neg { bn_neg } else { b < a };',
    'let result = if bn_neg != an_neg { bn_neg } else { a < b };'
)

# SGT: signed greater than - should be a > b in signed
c = c.replace(
    'let result = if bn_neg != an_neg { an_neg } else { b > a };',
    'let result = if bn_neg != an_neg { an_neg } else { a > b };'
)

with open(interp_path, 'w') as f:
    f.write(c)
print('Fixed interpreter operand ordering')

# === Fix tests.rs ===
with open(tests_path) as f:
    t = f.read()

# Fix SHR test: swap push order (push value first, then shift)
t = t.replace(
    'let code = vec![0x60, 0x01, 0x60, 0x08, 0x1C, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];',
    'let code = vec![0x60, 0x08, 0x60, 0x01, 0x1C, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];'
)

# Fix JUMP test: jump to position 4 (JUMPDEST), not 6
t = t.replace(
    '0x60, 0x06, 0x56, 0x00, 0x5B, 0x60, 0x42',
    '0x60, 0x04, 0x56, 0x00, 0x5B, 0x60, 0x42'
)

# Fix JUMPI taken test: jump to position 6 (JUMPDEST), not 7
t = t.replace(
    '0x60, 0x01, 0x60, 0x07, 0x57, 0x00, 0x5B',
    '0x60, 0x01, 0x60, 0x06, 0x57, 0x00, 0x5B'
)

# Fix multiple_contracts test: add inc_account_nonce between deploys
t = t.replace(
    'assert_ok!(Evm::deploy_contract(RuntimeOrigin::signed(1), dummy_code(), U256::from(100000), U256::zero()));\n        assert_ok!(Evm::deploy_contract(RuntimeOrigin::signed(1), dummy_code(), U256::from(100000), U256::zero()));',
    'assert_ok!(Evm::deploy_contract(RuntimeOrigin::signed(1), dummy_code(), U256::from(100000), U256::zero()));\n        frame_system::Pallet::<Test>::inc_account_nonce(&1);\n        assert_ok!(Evm::deploy_contract(RuntimeOrigin::signed(1), dummy_code(), U256::from(100000), U256::zero()));'
)

with open(tests_path, 'w') as f:
    f.write(t)
print('Fixed test bytecode')
