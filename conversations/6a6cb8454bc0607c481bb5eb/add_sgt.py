#!/usr/bin/env python3
"""Add SGT opcode (0x13) - signed greater-than comparison"""
import re

path = "/opt/verdis-chain/pallets/evm/src/interpreter.rs"
with open(path, "r") as f:
    c = f.read()

# SGT is the signed version of GT. It compares two values as signed 256-bit integers.
# If both have the same sign, it's the same as unsigned comparison.
# If signs differ, the positive value is greater.
# SGT: returns 1 if a > b (signed), else 0
# Stack: a, b -> a > b (signed)

# Find the SLT block (0x12) and add SGT after it
slt_block = """            0x12 => {
                let a = pop!(); let b = pop!();
                let bn_neg = b >> 255 != U256::zero();
                let an_neg = a >> 255 != U256::zero();
                let result = if bn_neg != an_neg { bn_neg } else { a < b };
                push!(if result { U256::one() } else { U256::zero() });
                pc += 1;
            }"""

sgt_block = """            0x13 => {
                let a = pop!(); let b = pop!();
                let bn_neg = b >> 255 != U256::zero();
                let an_neg = a >> 255 != U256::zero();
                // SGT: a > b (signed). If signs differ, positive (non-neg) is greater.
                let result = if an_neg != bn_neg { !an_neg } else { a > b };
                push!(if result { U256::one() } else { U256::zero() });
                pc += 1;
            }"""

# Insert SGT after SLT
if "0x13 =>" not in c:
    c = c.replace(slt_block, slt_block + "\n" + sgt_block)
    print("Added SGT (0x13) opcode")
else:
    print("SGT already exists")

with open(path, "w") as f:
    f.write(c)
