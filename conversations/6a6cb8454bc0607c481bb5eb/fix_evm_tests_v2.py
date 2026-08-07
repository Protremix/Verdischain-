#!/usr/bin/env python3
"""Fix all 6 failing EVM tests with correct EVM stack semantics"""

path = "/opt/verdis-chain/pallets/evm/src/tests.rs"
with open(path, "r") as f:
    c = f.read()

# 1. sgt_basic_positive: EVM pops top first as first operand
# Want: 5 > 3 = 1. Need 5 on top: PUSH1 3, PUSH1 5, SGT
c = c.replace(
    "// SGT: 5 > 3 => 1\n        // PUSH1 5, PUSH1 3, SGT (0x13)\n        let code = vec![0x60, 0x05, 0x60, 0x03, 0x13, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];",
    "// SGT: 5 > 3 => 1 (EVM: top=first operand, so push 3 then 5)\n        let code = vec![0x60, 0x03, 0x60, 0x05, 0x13, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];"
)

# 2. sgt_equal_values: order doesn't matter for equal values, but fix for consistency
c = c.replace(
    "let code = vec![0x60, 0x05, 0x60, 0x05, 0x13, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];",
    "let code = vec![0x60, 0x05, 0x60, 0x05, 0x13, 0x60, 0x00, 0x52, 0x60, 0x20, 0x60, 0x00, 0xF3];"
)

# 3. sgt_negative_greater_than_positive: -1 > 1 => 0
# Want -1 on top, 1 below: PUSH32(-1), PUSH1 1, SGT => -1 > 1 = false = 0
# Current code: PUSH32(-1), PUSH1 1, SGT — stack [-1, 1], pop a=1, pop b=-1, a>b=1>-1=1... wrong
# Need: PUSH1 1, PUSH32(-1), SGT — stack [1, -1], pop a=-1, pop b=1, a>b=-1>1=0
c = c.replace(
    "// -1 = 0xFFFF...FFFF (all ones in 256 bits)\n        // PUSH32 0xFF...FF, PUSH1 1, SGT\n        let mut code = vec![0x7F];\n        code.extend(vec![0xFF; 32]); // -1 in two's complement\n        code.extend(vec![0x60, 0x01, 0x13]); // PUSH1 1, SGT",
    "// -1 > 1 in signed => false (0). EVM: top=first operand.\n        // Push 1, then push -1, SGT => -1 > 1 = 0\n        let mut code = vec![0x60, 0x01]; // PUSH1 1\n        code.push(0x7F); // PUSH32\n        code.extend(vec![0xFF; 32]); // -1 in two's complement\n        code.extend(vec![0x13]); // SGT"
)

# 4. sgt_positive_greater_than_negative: 1 > -1 => 1
# Want 1 on top, -1 below: PUSH32(-1), PUSH1 1, SGT => 1 > -1 = true = 1
c = c.replace(
    "// SGT: 1 > -1 => 1 (positive is greater than negative in signed)\n        let mut code = vec![0x60, 0x01]; // PUSH1 1\n        code.push(0x7F); // PUSH32\n        code.extend(vec![0xFF; 32]); // -1\n        code.extend(vec![0x13]); // SGT",
    "// SGT: 1 > -1 => 1. EVM: top=first operand. Push -1, then 1, SGT => 1 > -1 = 1\n        let mut code = vec![0x7F]; // PUSH32\n        code.extend(vec![0xFF; 32]); // -1 in two's complement\n        code.extend(vec![0x60, 0x01]); // PUSH1 1\n        code.extend(vec![0x13]); // SGT"
)

# 5. sgt_two_negatives: -3 > -5 => 1
# Want -3 on top, -5 below: PUSH32(-5), PUSH32(-3), SGT => -3 > -5 = 1
c = c.replace(
    "// SGT: -3 > -5 => 1 (less negative is greater)\n        // -3 = 0xFF...FD, -5 = 0xFF...FB\n        let mut code = vec![0x7F];\n        code.extend(vec![0xFF; 31]);\n        code.push(0xFD); // -3\n        code.push(0x7F); // PUSH32\n        code.extend(vec![0xFF; 31]);\n        code.push(0xFB); // -5\n        code.extend(vec![0x13]); // SGT",
    "// SGT: -3 > -5 => 1 (less negative is greater). EVM: top=first operand.\n        // Push -5, then -3, SGT => -3 > -5 = 1\n        let mut code = vec![0x7F]; // PUSH32\n        code.extend(vec![0xFF; 31]);\n        code.push(0xFB); // -5\n        code.push(0x7F); // PUSH32\n        code.extend(vec![0xFF; 31]);\n        code.push(0xFD); // -3\n        code.extend(vec![0x13]); // SGT"
)

# 6. shl_large_shift: 256 = 0x0100, not 0x0001
# PUSH32 256 should be: 30 zeros, 0x01, 0x00
c = c.replace(
    "code.push(0x7F); // PUSH32 256\n        code.extend(vec![0x00; 31]);\n        code.push(0x01);",
    "code.push(0x7F); // PUSH32 256 = 0x0100\n        code.extend(vec![0x00; 30]);\n        code.push(0x01);\n        code.push(0x00);"
)

# 7. combined_arithmetic_chain: fix operand order
# ((3+4)*2-1)/3 = 4
# EVM: top=first operand for SUB and DIV
# Need: push divisor(3) first, then subtrahend(1), then compute up to 13 on top
c = c.replace(
    """// ((3 + 4) * 2 - 1) / 3 = (7 * 2 - 1) / 3 = 13 / 3 = 4
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
            0x52,       // MSTORE at 0
            0x60, 0x20, // PUSH1 32
            0x60, 0x00, // PUSH1 0
            0xF3,       // RETURN 32 bytes from 0
        ];""",
    """// ((3 + 4) * 2 - 1) / 3 = 4
        // EVM: top=first operand. Push operands in reverse order.
        // Stack build: [3(divisor), 1(subtrahend), then compute (3+4)*2=14 on top]
        // SUB: 14-1=13, DIV: 13/3=4
        let code = vec![
            0x60, 0x03, // PUSH1 3 (divisor, bottom)
            0x60, 0x01, // PUSH1 1 (subtrahend)
            0x60, 0x02, // PUSH1 2 (multiplier)
            0x60, 0x04, // PUSH1 4
            0x60, 0x03, // PUSH1 3
            0x01,       // ADD => 3+4=7
            0x02,       // MUL => 7*2=14
            0x03,       // SUB => 14-1=13 (top=14, second=1)
            0x04,       // DIV => 13/3=4 (top=13, second=3)
            0x60, 0x00, // PUSH1 0
            0x52,       // MSTORE at 0
            0x60, 0x20, // PUSH1 32
            0x60, 0x00, // PUSH1 0
            0xF3,       // RETURN 32 bytes from 0
        ];"""
)

with open(path, "w") as f:
    f.write(c)
print("Fixed all 6 failing EVM tests with correct EVM stack semantics")
