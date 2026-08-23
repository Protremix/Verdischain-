#!/usr/bin/env python3
import sys

with open("/opt/verdis-chain-rust/pallets/presale/src/lib.rs") as f:
    c = f.read()

# Check if the type was already added
if "EnforceUniqueVestingLabels" not in c:
    # Add to Config trait
    old = "        type Treasury: Get<Self::AccountId>;\n    }"
    new = "        type Treasury: Get<Self::AccountId>;\n        /// Enforce globally unique vesting labels per round (enable for mainnet)\n        type EnforceUniqueVestingLabels: Get<bool>;\n    }"
    c = c.replace(old, new)
    with open("/opt/verdis-chain-rust/pallets/presale/src/lib.rs", "w") as f:
        f.write(c)
    print("EnforceUniqueVestingLabels added to Config trait")
else:
    print("EnforceUniqueVestingLabels already present")
