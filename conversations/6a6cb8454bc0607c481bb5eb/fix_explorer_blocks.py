#!/usr/bin/env python3
"""Fix the explorer Blocks tab - loadBlocks uses 4200 as fallback which is way past current chain height."""

with open("/var/www/verdiscan/explorer/index.html") as f:
    c = f.read()

# Fix: Replace the fallback 4200 with a dynamic fetch of the latest block
old_line = "const start = blockNum || 4200;"

new_code = """// Fetch current block height if not set
  if (!blockNum || blockNum === 0) {
    const hdr = await rpc('chain_getHeader', []);
    if (hdr && hdr.number) blockNum = parseInt(hdr.number, 16);
  }
  const start = blockNum || 100;
  if (start === 0) { tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:var(--text-3)">No blocks yet</td></tr>'; return; }"""

if old_line in c:
    c = c.replace(old_line, new_code)
    print("Fixed: loadBlocks fallback 4200 -> dynamic fetch")
else:
    print("ERROR: Could not find the fallback line")
    import sys; sys.exit(1)

with open("/var/www/verdiscan/explorer/index.html", "w") as f:
    f.write(c)
print("Done - explorer Blocks tab fixed")
