#!/usr/bin/env python3
import sys

with open("/opt/verdis-chain-rust/pallets/presale/src/tests.rs") as f:
    c = f.read()

old = '#[path = "luna_regression_tests.rs"]\nmod luna_regression_tests;'
new = '#[path = "luna_regression_tests.rs"]\nmod luna_regression_tests;\n#[path = "master6_regression_tests.rs"]\nmod master6_regression_tests;'

c = c.replace(old, new)

with open("/opt/verdis-chain-rust/pallets/presale/src/tests.rs", "w") as f:
    f.write(c)

print("master6_regression_tests module added to tests.rs")
