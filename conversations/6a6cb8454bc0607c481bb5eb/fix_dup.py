#!/usr/bin/env python3
"""Fix duplicate variable declaration in loadExtrinsics."""

path = "/var/www/verdiscan/explorer/index.html"
content = open(path).read()

# Remove the duplicate lines
old = """    const b = allExts[i];
    const exts = b.exts || [];
    const b = blocksData[i];
    const exts = b.exts || [];"""

new = """    const b = allExts[i];
    const exts = b.exts || [];"""

if old in content:
    content = content.replace(old, new)
    open(path, "w").write(content)
    print("OK: Fixed duplicate declaration")
else:
    print("FAIL: Pattern not found")
