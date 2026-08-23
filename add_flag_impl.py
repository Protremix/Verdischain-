#!/usr/bin/env python3
import sys

# 1. Add to test mock (disabled)
with open("/opt/verdis-chain-rust/pallets/presale/src/tests.rs") as f:
    c = f.read()
old = "    type Treasury = TestTreasury;\n}"
new = "    type Treasury = TestTreasury;\n    type EnforceUniqueVestingLabels = frame_support::traits::ConstBool<false>;\n}"
c = c.replace(old, new)
with open("/opt/verdis-chain-rust/pallets/presale/src/tests.rs", "w") as f:
    f.write(c)
print("Test mock: EnforceUniqueVestingLabels = false")

# 2. Add to production runtime (enabled)
with open("/opt/verdis-chain-rust/runtime/src/lib.rs") as f:
    c = f.read()
old = "    type Vesting = PresaleVestingHandler;\n    type WeightInfo = pallet_presale::SubstrateWeight<Runtime>;\n    type Treasury = TreasuryAccount;\n}"
new = "    type Vesting = PresaleVestingHandler;\n    type WeightInfo = pallet_presale::SubstrateWeight<Runtime>;\n    type Treasury = TreasuryAccount;\n    type EnforceUniqueVestingLabels = frame_support::traits::ConstBool<true>;\n}"
c = c.replace(old, new)
with open("/opt/verdis-chain-rust/runtime/src/lib.rs", "w") as f:
    f.write(c)
print("Production runtime: EnforceUniqueVestingLabels = true")
