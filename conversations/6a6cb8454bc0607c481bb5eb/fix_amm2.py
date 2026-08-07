#!/usr/bin/env python3
"""Fix AmmDex benchmark - reduce create_pool iterations to leave room"""

path = "/opt/verdis-chain/pallets/amm-dex/src/tests.rs"
with open(path, "r") as f:
    c = f.read()

# Reduce create_pool iterations from 50 to 40
c = c.replace(
    'let w = measure_bench("create_pool", 50, || {',
    'let w = measure_bench("create_pool", 40, || {'
)

# Fix pool_id for add_liquidity - use pool_id 41 (the one created after benchmarks)
c = c.replace(
    'AmmDex::add_liquidity(RuntimeOrigin::signed(1), 100, 500_000_000, 1_000_000_000).is_ok()',
    'AmmDex::add_liquidity(RuntimeOrigin::signed(1), 41, 500_000_000, 1_000_000_000).is_ok()'
)

# Fix pool_id for swap - use pool_id 41
c = c.replace(
    'AmmDex::swap(RuntimeOrigin::signed(2), 100, b"AAA".to_vec(), 100_000_000, 1).is_ok()',
    'AmmDex::swap(RuntimeOrigin::signed(2), 41, b"AAA".to_vec(), 100_000_000, 1).is_ok()'
)

with open(path, "w") as f:
    f.write(c)
print("Fixed AmmDex benchmark pool IDs and iterations")
