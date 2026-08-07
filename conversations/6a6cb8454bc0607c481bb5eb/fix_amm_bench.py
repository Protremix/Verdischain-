#!/usr/bin/env python3
"""Fix benchmark amounts for AmmDex pallet"""

path = "/opt/verdis-chain/pallets/amm-dex/src/tests.rs"
with open(path, "r") as f:
    c = f.read()

# Find the benchmark section and fix the amounts
old = '''AmmDex::create_pool(RuntimeOrigin::signed(1), token_a, token_b, 1_000_000, 2_000_000).is_ok()'''
new = '''AmmDex::create_pool(RuntimeOrigin::signed(1), token_a, token_b, 2_000_000_000_000, 2_000_000_000_000).is_ok()'''
c = c.replace(old, new)

old2 = '''assert_ok!(AmmDex::create_pool(RuntimeOrigin::signed(1), b"AAA".to_vec(), b"BBB".to_vec(), 1_000_000, 2_000_000));'''
new2 = '''assert_ok!(AmmDex::create_pool(RuntimeOrigin::signed(1), b"AAA".to_vec(), b"BBB".to_vec(), 2_000_000_000_000, 2_000_000_000_000));'''
c = c.replace(old2, new2)

old3 = '''AmmDex::add_liquidity(RuntimeOrigin::signed(1), 100, 500_000, 1_000_000).is_ok()'''
new3 = '''AmmDex::add_liquidity(RuntimeOrigin::signed(1), 100, 500_000_000, 1_000_000_000).is_ok()'''
c = c.replace(old3, new3)

old4 = '''AmmDex::swap(RuntimeOrigin::signed(2), 100, b"AAA".to_vec(), 100_000, 1).is_ok()'''
new4 = '''AmmDex::swap(RuntimeOrigin::signed(2), 100, b"AAA".to_vec(), 100_000_000, 1).is_ok()'''
c = c.replace(old4, new4)

with open(path, "w") as f:
    f.write(c)
print("Fixed AmmDex benchmark amounts")
