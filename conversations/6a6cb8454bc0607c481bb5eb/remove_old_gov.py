#!/usr/bin/env python3
"""Remove old duplicate governance endpoints from server.js"""

with open('/opt/verdis/app/dist/api/server.js') as f:
    lines = f.readlines()

# Find and remove the old governance section
# It starts with "// === GOVERNANCE ===" and the old "this.proposals = [];"
# and ends before the next section marker

old_start = None
old_end = None

for i, line in enumerate(lines):
    if '// === GOVERNANCE ===' in line and 'this.proposals = []' in ''.join(lines[i:i+3]):
        old_start = i
        break

if old_start is None:
    # Try alternate: find "this.proposals = []" 
    for i, line in enumerate(lines):
        if 'this.proposals = []' in line:
            # Back up to the comment line
            for j in range(i, max(i-5, 0), -1):
                if '// === GOVERNANCE ===' in lines[j]:
                    old_start = j
                    break
            break

if old_start is None:
    print("ERROR: Could not find old governance start")
    exit(1)

# Find the end: look for the next "// ===" section marker after old_start
for i in range(old_start + 1, len(lines)):
    if '// ===' in lines[i] and i > old_start + 5:
        old_end = i
        break

if old_end is None:
    print("ERROR: Could not find old governance end")
    exit(1)

# Print what we're removing
print(f"Removing lines {old_start+1} to {old_end} (old governance)")
print(f"  First: {lines[old_start].strip()}")
print(f"  Last:  {lines[old_end-1].strip()}")
print(f"  Next:  {lines[old_end].strip()}")

# Remove the old section
del lines[old_start:old_end]

with open('/opt/verdis/app/dist/api/server.js', 'w') as f:
    f.writelines(lines)

print(f"Removed {old_end - old_start} lines of old governance code")
