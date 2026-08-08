#!/usr/bin/env python3
"""Fix the Top Liquidity Pools HTML in DEX page."""

with open("/var/www/verdiscan/dex/index.html", "r") as f:
    lines = f.readlines()

# Replace lines 1195-1213 (0-indexed: 1194-1212) with dynamic container
# Line 1194 is "Top Liquidity Pools" title - keep it
# Lines 1195-1212 are the hardcoded pool items - replace with dynamic container
new_lines = [
    '            <div id="topPoolsList" style="display:flex; flex-direction:column; gap:10px;">\n',
    '              <div style="text-align:center;padding:20px;color:#666;font-size:13px;">Loading on-chain pools...</div>\n',
    '            </div>\n',
]

# Find the exact line range to replace
start_idx = None
end_idx = None
for i, line in enumerate(lines):
    if 'display:flex; flex-direction:column; gap:10px;' in line and start_idx is None:
        start_idx = i
    if start_idx is not None and '$5.0M TVL' in line:
        # Find the closing div after this
        for j in range(i+1, min(i+5, len(lines))):
            if '</div>' in lines[j] and 'pool' not in lines[j].lower():
                end_idx = j
                break
        if end_idx is None:
            end_idx = i + 1
        break

if start_idx is not None and end_idx is not None:
    # Replace the lines
    lines = lines[:start_idx] + new_lines + lines[end_idx+1:]
    print(f"Replaced lines {start_idx+1} to {end_idx+1} with dynamic container")
else:
    print(f"WARNING: Could not find pool list. start={start_idx} end={end_idx}")

with open("/var/www/verdiscan/dex/index.html", "w") as f:
    f.writelines(lines)
print("Done - Top Liquidity Pools fixed")
