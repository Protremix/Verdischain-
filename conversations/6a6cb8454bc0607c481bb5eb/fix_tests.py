import re

with open('/dev/stdin', 'r') as f:
    lines = f.readlines()

# We need to fix specific lines. Let's find and fix them.
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # Fix 1: user1_before - user1_after assertion (overflow)
    if 'user1_before - user1_after' in line:
        # Replace this block (assert_eq! spanning multiple lines)
        # Skip until we find the closing );
        new_lines.append('        let user1_change = user1_after as i64 - user1_before as i64;\n')
        new_lines.append('        assert_eq!(user1_change, -10i64 + 50, "User net: -10 payment + 50 tokens = +40");\n')
        # Skip the next few lines until )
        i += 1
        while i < len(lines) and ');' not in lines[i]:
            i += 1
        i += 1  # skip the ); line
        continue
    
    # Fix 2: escrow_after - escrow_before assertion (overflow)
    if 'escrow_after - escrow_before' in line and 'escrow_change' not in line:
        new_lines.append('        let escrow_change = escrow_after as i64 - escrow_before as i64;\n')
        new_lines.append('        assert_eq!(escrow_change, 10i64 - 50, "Escrow: +10 payment, -50 tokens = -40 net");\n')
        # Skip until )
        i += 1
        while i < len(lines) and ');' not in lines[i]:
            i += 1
        i += 1
        continue
    
    new_lines.append(line)
    i += 1

import sys
sys.stdout.writelines(new_lines)
