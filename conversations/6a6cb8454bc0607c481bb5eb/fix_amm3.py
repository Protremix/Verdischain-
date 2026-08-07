#!/usr/bin/env python3
"""Fix AmmDex benchmark - use pool_id 40, pre-fund accounts, fix add_liquidity"""

path = "/opt/verdis-chain/pallets/amm-dex/src/tests.rs"
with open(path, "r") as f:
    c = f.read()

# Fix pool_id from 41 to 40
c = c.replace(
    'AmmDex::add_liquidity(RuntimeOrigin::signed(1), 41, 500_000_000, 1_000_000_000).is_ok()',
    'AmmDex::add_liquidity(RuntimeOrigin::signed(1), 40, 1_000_000_000_000, 1_000_000_000_000).is_ok()'
)
c = c.replace(
    'AmmDex::swap(RuntimeOrigin::signed(2), 41, b"AAA".to_vec(), 100_000_000, 1).is_ok()',
    'AmmDex::swap(RuntimeOrigin::signed(2), 40, b"AAA".to_vec(), 100_000_000, 1).is_ok()'
)

# Fix the add_liquidity benchmark to reset balance each iteration
c = c.replace(
    '''let w = measure_bench("add_liquidity", 50, || {
                <pallet_balances::Pallet<Test> as Mutate<u64>>::set_balance(&1, 100_000_000_000_000_000);
                AmmDex::add_liquidity(RuntimeOrigin::signed(1), 40, 1_000_000_000_000, 1_000_000_000_000).is_ok()
            });''',
    '''let w = measure_bench("add_liquidity", 30, || {
                <pallet_balances::Pallet<Test> as Mutate<u64>>::set_balance(&1, 100_000_000_000_000_000);
                AmmDex::add_liquidity(RuntimeOrigin::signed(1), 40, 100_000_000, 100_000_000).is_ok()
            });'''
)

# Fix the swap benchmark
c = c.replace(
    '''let w = measure_bench("swap", 50, || {
                <pallet_balances::Pallet<Test> as Mutate<u64>>::set_balance(&2, 100_000_000_000_000_000);
                AmmDex::swap(RuntimeOrigin::signed(2), 40, b"AAA".to_vec(), 100_000_000, 1).is_ok()
            });''',
    '''let w = measure_bench("swap", 30, || {
                <pallet_balances::Pallet<Test> as Mutate<u64>>::set_balance(&2, 100_000_000_000_000_000);
                AmmDex::swap(RuntimeOrigin::signed(2), 40, b"AAA".to_vec(), 10_000_000, 1).is_ok()
            });'''
)

with open(path, "w") as f:
    f.write(c)
print("Fixed AmmDex benchmark pool_id and amounts")
