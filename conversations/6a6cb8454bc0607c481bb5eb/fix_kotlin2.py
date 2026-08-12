#!/usr/bin/env python3
"""Fix the cleaned block in MainActivity.kt"""
import re

filepath = "/opt/verdis-wallet/mobile/android/app/src/main/kotlin/com/verdis/verdis_wallet/MainActivity.kt"

with open(filepath, "r") as f:
    content = f.read()

# Replace the entire cleaned block using regex
# Match from "val cleaned = " to the line before "if (cleaned != null"
pattern = r'val cleaned = resultJson\?.trim\(\).*?\n.*?\n.*?\n.*?\n'

# The correct Kotlin code:
# removeSurrounding("\"")   -> removes " chars
# replace("\\\"", "\"")     -> replaces \" with "
# replace("\\\\", "\\")     -> replaces \\ with \
# replace("\\n", "\n")      -> replaces literal \n with newline
correct_block = 'val cleaned = resultJson?.trim()?.removeSurrounding "\\"")\n                ?.replace("\\\\"", "\\"")\n                ?.replace("\\\\", "\\")\n                ?.replace("\\n", "\\n")\n'

# Actually, let me just write the raw bytes directly to avoid Python escaping issues
# The key insight: in Kotlin source code we need:
# removeSurrounding("\"")
# replace("\\\"", "\"")
# replace("\\\\", "\\")
# replace("\\n", "\n")

# Let me build the string using raw representation
# In the file, we want these exact characters:
# ?.removeSurrounding("\"")
# ?.replace("\\\"", "\"")
# ?.replace("\\\\", "\\")
# ?.replace("\\n", "\n")

lines = content.split('\n')
new_lines = []
i = 0
while i < len(lines):
    if 'val cleaned = resultJson?.trim()' in lines[i]:
        # Replace this line and the next 3 lines (the chained replace calls)
        new_lines.append('            val cleaned = resultJson?.trim()?.removeSurrounding("\\"")')
        new_lines.append('                ?.replace("\\\\\\"", "\\"")')
        new_lines.append('                ?.replace("\\\\\\\\", "\\\\")')
        new_lines.append('                ?.replace("\\\\n", "\\n")')
        # Skip the original lines
        i += 1
        while i < len(lines) and '?.replace' in lines[i] or (i < len(lines) and '?.removeSurrounding' in lines[i]):
            i += 1
        # Don't increment i again - the while already moved past
        continue
    else:
        new_lines.append(lines[i])
        i += 1

content = '\n'.join(new_lines)

with open(filepath, "w") as f:
    f.write(content)

print("Fixed cleaned block in MainActivity.kt")

# Verify
with open(filepath, "r") as f:
    content = f.read()

# Show the fixed lines
for line in content.split('\n'):
    if 'cleaned' in line and 'replace' in line or 'removeSurrounding' in line:
        print(f"  {line.strip()}")
    elif 'val cleaned' in line:
        print(f"  {line.strip()}")
