#!/usr/bin/env python3
"""
Add execution logic for all missing EVM opcodes:
SDIV, SMOD, SLT, SGT, GASPRICE, EXTCODECOPY, RETURNDATASIZE, RETURNDATACOPY, BASEFEE
Plus PUSH1-PUSH32, DUP1-DUP16, SWAP1-SWAP16, LOG1-LOG4
"""
import re

with open("/opt/verdis/app/dist/core/vm.js", "r") as f:
    vm = f.read()

# Find the main execution switch/if-else chain to add new opcodes
# The opcodes are likely handled in a switch or if-else chain

# First, find where the existing opcodes are handled
# Look for the SUB opcode handler as a reference point
sub_handler = vm.find("case 0x03:")
if sub_handler == -1:
    # Try alternate format
    sub_handler = vm.find("SUB:")
if sub_handler == -1:
    # Search for where ADD is handled
    print("Searching for opcode handlers...")
    for pattern in ["case 0x01", "case 'ADD'", "ADD: 0x01"]:
        idx = vm.find(pattern)
        if idx != -1:
            print(f"Found '{pattern}' at index {idx}")
            break

# Find a good insertion point - after the existing arithmetic opcodes
# Look for the DIV handler (0x04) and add after MOD (0x06)
mod_idx = vm.find("MOD:")  # Find MOD handler
if mod_idx == -1:
    print("Could not find MOD handler, searching for DIV...")
    mod_idx = vm.find("0x04")  # DIV opcode

print(f"MOD handler found at index: {mod_idx}")

# The approach: find the execute method's opcode dispatch and add new handlers
# Look for where opcodes are dispatched (likely a big switch or if-else chain)
# Find where EXP (0x0A) is handled - it's one of the arithmetic opcodes we need to add near

# Let's find the actual execution handler structure
exec_match = re.search(r"(case 0x0A|case 'EXP'|EXP: 0x0A|0x0A:)", vm)
if exec_match:
    print(f"Found EXP handler at index {exec_match.start()}: {vm[exec_match.start():exec_match.start()+50]}")

# Find where SIGNEXTEND (0x0B) is handled - we'll add SDIV, SMOD before the comparison opcodes
signext_idx = vm.find("0x0B")
print(f"SIGNEXTEND (0x0B) found at index: {signext_idx}")

# Look for the comparison section (LT at 0x10)
lt_idx = vm.find("0x10")
print(f"LT (0x10) found at index: {lt_idx}")

# Now let's find the actual opcode dispatch mechanism
# Search for how opcodes are processed (e.g., "this.opcodes" or "OPCODES[")
dispatch_patterns = [
    r"const op\s*=\s*this\.bytecode\[this\.pc\]",
    r"const opcode\s*=\s*this\.bytecode\[this\.pc\]",
    r"const code\s*=\s*this\.bytecode\[this\.pc\]",
    r"switch\s*\(\s*(?:op|opcode|code)\s*\)",
]

for p in dispatch_patterns:
    m = re.search(p, vm)
    if m:
        print(f"Found dispatch: '{m.group()}' at index {m.start()}")
        # Show surrounding context
        start = max(0, m.start() - 20)
        end = min(len(vm), m.start() + 100)
        print(f"Context: {vm[start:end]}")

# Now let's find where to add the new opcode handlers
# We need to add execution logic for: SDIV, SMOD, SLT, SGT, GASPRICE, etc.
# Find where existing arithmetic handlers are

# Search for the DIV handler to understand the pattern
div_search = re.search(r"(case\s+['\"]?DIV['\"]?\s*:|0x04[^a-zA-Z])", vm)
if div_search:
    print(f"\nDIV handler context:")
    start = div_search.start()
    print(vm[start:start+200])

print("\n\n=== File structure analysis ===")
# Count how many case/if blocks exist for opcodes
case_count = len(re.findall(r"(?:case\s+['\"]?\w+['\"]?\s*:|0x[0-9A-Fa-f]+\s*:)", vm))
print(f"Total case/opcode labels: {case_count}")

# Find the execute method
exec_method = re.search(r"execute\s*\(.*?\)\s*\{", vm)
if exec_method:
    print(f"execute method at index {exec_method.start()}")
    # Find the main dispatch loop
    dispatch_area = vm[exec_method.start():exec_method.start()+5000]
    print(f"First 200 chars of execute: {dispatch_area[:200]}")

print("\nScript ready - will add opcode handlers based on the detected dispatch pattern")
