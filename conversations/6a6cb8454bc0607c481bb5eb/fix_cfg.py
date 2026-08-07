#!/usr/bin/env python3
import sys

path = "/opt/verdis-chain/pallets/dpos/src/lib.rs"
with open(path, "r") as f:
    c = f.read()
c = c.replace(
    '#[cfg(feature = "runtime-benchmarks")]\nmod dpos_bench;',
    '#[cfg(all(test, feature = "runtime-benchmarks"))]\nmod dpos_bench;'
)
with open(path, "w") as f:
    f.write(c)
print("Fixed dpos_bench cfg")
