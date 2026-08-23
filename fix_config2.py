#!/usr/bin/env python3
import sys

with open("/opt/verdis-chain-rust/pallets/presale/src/lib.rs") as f:
    lines = f.readlines()

in_config = False
added = False
for i, line in enumerate(lines):
    if "pub trait Config:" in line:
        in_config = True
    if in_config and "type Treasury: Get<Self::AccountId>;" in line:
        if i + 1 < len(lines) and "EnforceUniqueVestingLabels" in lines[i + 1]:
            added = True
            break
        lines.insert(i + 1, "        /// Enforce globally unique vesting labels per round (enable for mainnet)\n        type EnforceUniqueVestingLabels: Get<bool>;\n")
        added = True
        break

if added:
    with open("/opt/verdis-chain-rust/pallets/presale/src/lib.rs", "w") as f:
        f.writelines(lines)
    print("Added EnforceUniqueVestingLabels to Config trait")
else:
    print("ERROR: Could not find insertion point")
