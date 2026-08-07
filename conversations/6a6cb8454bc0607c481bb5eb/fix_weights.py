#!/usr/bin/env python3
"""Fix trailing commas in weight files"""

import os

PALLET_DIRS = [
    "dpos", "amm-dex", "eco", "tokenomics", "vesting", "evm", "storage"
]

for pallet_dir in PALLET_DIRS:
    path = f"/opt/verdis-chain/pallets/{pallet_dir}/src/weights.rs"
    if not os.path.exists(path):
        continue
    with open(path, "r") as f:
        c = f.read()
    # Remove trailing commas after method closing braces
    c = c.replace("    },\n    pub fn", "    }\n    pub fn")
    c = c.replace("    },\n}", "    }\n}")
    with open(path, "w") as f:
        f.write(c)
    print(f"Fixed {pallet_dir}/weights.rs")

print("\nAll weight files fixed!")
