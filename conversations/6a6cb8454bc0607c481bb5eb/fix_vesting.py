#!/usr/bin/env python3
"""Fix vesting benchmark - add type annotation for set_block_number"""

path = "/opt/verdis-chain/pallets/vesting/src/tests.rs"
with open(path, "r") as f:
    c = f.read()

c = c.replace(
    "System::set_block_number(1000);",
    "System::<Test>::set_block_number(1000);"
)

with open(path, "w") as f:
    f.write(c)
print("Fixed vesting benchmark type annotation")
