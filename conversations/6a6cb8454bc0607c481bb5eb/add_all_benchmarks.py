#!/usr/bin/env python3
"""Append real benchmark tests to each pallet's tests.rs"""
import os

BENCH_TEMPLATE = '''
// ==================== REAL BENCHMARK WEIGHT GENERATION ====================
#[cfg(feature = "runtime-benchmarks")]
mod real_bench {
    use super::*;
    use super::{Test, new_test_ext};
    use std::time::Instant;
    use frame_support::traits::fungible::Mutate;

    fn measure_bench<F: FnMut() -> bool>(name: &str, iters: u32, mut f: F) -> u64 {
        let mut times: Vec<u64> = Vec::new();
        for _ in 0..iters {
            let start = Instant::now();
            let ok = f();
            let elapsed = start.elapsed().as_nanos() as u64;
            if ok { times.push(elapsed); }
        }
        if times.is_empty() {
            println!("  {pallet}::{name} -> FAILED", pallet = PALLET_NAME, name = name);
            return 10_000;
        }
        let avg = times.iter().sum::<u64>() / times.len() as u64;
        let max = *times.iter().max().unwrap();
        let weight = (avg as f64 * 1.25).max(10000.0) as u64;
        println!("  {pallet}::{name} -> avg={avg}ns max={max}ns weight={weight}", pallet = PALLET_NAME, name = name, avg = avg, max = max, weight = weight);
        weight
    }

    const PALLET_NAME: &str = "{pallet_name}";

    #[test]
    #[ignore]
    fn real_bench() {
        new_test_ext().execute_with(|| {{
            use frame_system::Pallet as System;
            System::<Test>::set_block_number(1);
            {body}
        }});
    }
}
'''

# AmmDex benchmark
amm_dex_body = '''
            // Fund accounts
            for i in 1u64..=10u64 {
                <pallet_balances::Pallet<Test> as Mutate<u64>>::set_balance(&i, 100_000_000_000_000_000);
            }
            let mut results: Vec<(&str, u64)> = Vec::new();

            // Benchmark: create_pool
            let mut pool_idx = 0u32;
            let w = measure_bench("create_pool", 50, || {
                pool_idx += 1;
                let token_a = format!("token_a_{}", pool_idx).into_bytes();
                let token_b = format!("token_b_{}", pool_idx).into_bytes();
                AmmDex::create_pool(RuntimeOrigin::signed(1), token_a, token_b, 1_000_000, 2_000_000).is_ok()
            });
            results.push(("create_pool", w));

            // Create a pool for remaining benchmarks
            assert_ok!(AmmDex::create_pool(RuntimeOrigin::signed(1), b"AAA".to_vec(), b"BBB".to_vec(), 1_000_000, 2_000_000));

            // Benchmark: add_liquidity
            let w = measure_bench("add_liquidity", 50, || {
                <pallet_balances::Pallet<Test> as Mutate<u64>>::set_balance(&1, 100_000_000_000_000_000);
                AmmDex::add_liquidity(RuntimeOrigin::signed(1), 100, 500_000, 1_000_000).is_ok()
            });
            results.push(("add_liquidity", w));

            // Benchmark: swap
            let w = measure_bench("swap", 50, || {
                <pallet_balances::Pallet<Test> as Mutate<u64>>::set_balance(&2, 100_000_000_000_000_000);
                AmmDex::swap(RuntimeOrigin::signed(2), 100, b"AAA".to_vec(), 100_000, 1).is_ok()
            });
            results.push(("swap", w));

            println!("\\n//! WeightInfo for pallet-amm-dex (real benchmark)");
            println!("pub struct WeightInfo;");
            for (name, weight) in &results {
                println!("// {}: {} weight units", name, weight);
            }
'''

# Eco benchmark
eco_body = '''
            let mut results: Vec<(&str, u64)> = Vec::new();

            // Benchmark: mint_carbon_credit
            let mut idx = 0u64;
            let w = measure_bench("mint_carbon_credit", 50, || {
                idx += 1;
                let id = format!("cc_{}", idx).into_bytes();
                Eco::mint_carbon_credit(RuntimeOrigin::signed(1), id, b"Amazon Project".to_vec(), 100).is_ok()
            });
            results.push(("mint_carbon_credit", w));

            // Benchmark: create_reforest_project
            let mut ridx = 0u64;
            let w = measure_bench("create_reforest_project", 50, || {
                ridx += 1;
                let id = format!("rf_{}", ridx).into_bytes();
                Eco::create_reforest_project(RuntimeOrigin::signed(1), id, b"Reforest A".to_vec(), 1000, b"Brazil".to_vec()).is_ok()
            });
            results.push(("create_reforest_project", w));

            // Benchmark: register_green_validator
            let mut vidx = 0u64;
            let w = measure_bench("register_green_validator", 50, || {
                vidx += 1;
                let src = format!("solar_{}", vidx).into_bytes();
                Eco::register_green_validator(RuntimeOrigin::signed(vidx), src, 1000, 500, 90).is_ok()
            });
            results.push(("register_green_validator", w));

            println!("\\n//! WeightInfo for pallet-eco (real benchmark)");
            println!("pub struct WeightInfo;");
            for (name, weight) in &results {
                println!("// {}: {} weight units", name, weight);
            }
'''

# Tokenomics benchmark
tokenomics_body = '''
            use crate::tests::UNITS;
            let mut results: Vec<(&str, u64)> = Vec::new();

            // Benchmark: give_consent
            let mut idx = 10u64;
            let w = measure_bench("give_consent", 50, || {
                idx += 1;
                <pallet_balances::Pallet<Test> as Mutate<u64>>::set_balance(&idx, 100_000);
                Tokenomics::give_consent(RuntimeOrigin::signed(idx)).is_ok()
            });
            results.push(("give_consent", w));

            // Benchmark: purchase (needs consent first)
            <pallet_balances::Pallet<Test> as Mutate<u64>>::set_balance(&5, 100_000);
            assert_ok!(Tokenomics::give_consent(RuntimeOrigin::signed(5)));
            let w = measure_bench("purchase", 50, || {
                <pallet_balances::Pallet<Test> as Mutate<u64>>::set_balance(&5, 100_000);
                Tokenomics::purchase(RuntimeOrigin::signed(5), 100).is_ok()
            });
            results.push(("purchase", w));

            // Benchmark: release_distribution (root only)
            let w = measure_bench("release_distribution", 50, || {
                Tokenomics::release_distribution(RuntimeOrigin::root(), b"team".to_vec(), 1000).is_ok()
            });
            results.push(("release_distribution", w));

            println!("\\n//! WeightInfo for pallet-tokenomics (real benchmark)");
            println!("pub struct WeightInfo;");
            for (name, weight) in &results {
                println!("// {}: {} weight units", name, weight);
            }
'''

# Vesting benchmark
vesting_body = '''
            let mut results: Vec<(&str, u64)> = Vec::new();

            // Benchmark: assign_vesting (root only)
            let mut idx = 10u64;
            let w = measure_bench("assign_vesting", 50, || {
                idx += 1;
                Vesting::assign_vesting(RuntimeOrigin::root(), idx, b"ido_30".to_vec(), 1_000).is_ok()
            });
            results.push(("assign_vesting", w));

            // Benchmark: release_vested (needs time to pass)
            assert_ok!(Vesting::assign_vesting(RuntimeOrigin::root(), 1, b"ido_30".to_vec(), 1_000));
            // Advance block number to simulate time passing
            System::set_block_number(1000);
            let w = measure_bench("release_vested", 50, || {
                Vesting::release_vested(RuntimeOrigin::signed(1)).is_ok()
            });
            results.push(("release_vested", w));

            println!("\\n//! WeightInfo for pallet-vesting (real benchmark)");
            println!("pub struct WeightInfo;");
            for (name, weight) in &results {
                println!("// {}: {} weight units", name, weight);
            }
'''

# EVM benchmark
evm_body = '''
            use sp_core::U256;
            let mut results: Vec<(&str, u64)> = Vec::new();

            // Benchmark: deploy_contract
            let code = vec![0x60u8, 0x80, 0x60, 0x40, 0x52];
            let w = measure_bench("deploy_contract", 30, || {
                EVM::deploy_contract(RuntimeOrigin::signed(1), code.clone(), U256::from(1_000_000u64), U256::zero()).is_ok()
            });
            results.push(("deploy_contract", w));

            // Benchmark: call_contract (needs a deployed contract)
            assert_ok!(EVM::deploy_contract(RuntimeOrigin::signed(2), vec![0x60, 0x00, 0x60, 0x00, 0xF3], U256::from(1_000_000u64), U256::zero()));
            let contract_addr = EVM::create_address(&2, 0);
            let w = measure_bench("call_contract", 30, || {
                EVM::call_contract(RuntimeOrigin::signed(3), contract_addr, vec![], U256::from(1_000_000u64), U256::zero()).is_ok()
            });
            results.push(("call_contract", w));

            // Benchmark: execute_code (internal)
            let w = measure_bench("execute_code", 30, || {
                EVM::execute_code(&[0x60, 0x01, 0x60, 0x00, 0xF3], &[], 1_000_000).is_ok()
            });
            results.push(("execute_code", w));

            println!("\\n//! WeightInfo for pallet-evm (real benchmark)");
            println!("pub struct WeightInfo;");
            for (name, weight) in &results {
                println!("// {}: {} weight units", name, weight);
            }
'''

# Storage benchmark
storage_body = '''
            let mut results: Vec<(&str, u64)> = Vec::new();

            // Benchmark: register_provider
            let mut idx = 0u64;
            let w = measure_bench("register_provider", 50, || {
                idx += 1;
                Storage::register_provider(RuntimeOrigin::signed(idx), crate::StorageBackend::Ipfs, b"https://ipfs.io".to_vec()).is_ok()
            });
            results.push(("register_provider", w));

            // Benchmark: register_storage
            let mut sidx = 0u64;
            let w = measure_bench("register_storage", 50, || {
                sidx += 1;
                let id = format!("rec_{}", sidx).into_bytes();
                Storage::register_storage(RuntimeOrigin::signed(1), id, crate::StorageBackend::Ipfs, 1024, [0xab; 32]).is_ok()
            });
            results.push(("register_storage", w));

            // Benchmark: verify_storage (root only)
            assert_ok!(Storage::register_storage(RuntimeOrigin::signed(1), b"rec_v".to_vec(), crate::StorageBackend::Ipfs, 1024, [0xcd; 32]));
            let w = measure_bench("verify_storage", 50, || {
                Storage::verify_storage(RuntimeOrigin::root(), b"rec_v".to_vec(), [0xcd; 32]).is_ok()
            });
            results.push(("verify_storage", w));

            println!("\\n//! WeightInfo for pallet-storage (real benchmark)");
            println!("pub struct WeightInfo;");
            for (name, weight) in &results {
                println!("// {}: {} weight units", name, weight);
            }
'''

pallets = [
    ("amm-dex", "amm_dex", "amm_dex", amm_dex_body, "AmmDex"),
    ("eco", "eco", "eco", eco_body, "Eco"),
    ("tokenomics", "tokenomics", "tokenomics", tokenomics_body, "Tokenomics"),
    ("vesting", "vesting", "vesting", vesting_body, "Vesting"),
    ("evm", "evm", "evm", evm_body, "EVM"),
    ("storage", "storage", "storage", storage_body, "Storage"),
]

for pallet_dir, pallet_crate, pallet_name, body, pallet_struct in pallets:
    test_file = f"/opt/verdis-chain/pallets/{pallet_dir}/src/tests.rs"

    # Read existing content
    with open(test_file, "r") as f:
        content = f.read()

    # Remove old benchmark append if exists
    marker = "// ==================== REAL BENCHMARK WEIGHT GENERATION"
    if marker in content:
        idx = content.index(marker)
        # Find the line before the marker
        cut_idx = content.rfind("\n", 0, idx)
        if cut_idx == -1:
            cut_idx = idx
        content = content[:cut_idx]

    # Generate benchmark module
    bench_code = BENCH_TEMPLATE.replace("{pallet_name}", pallet_name).replace("{body}", body)

    # Append
    content = content + "\n" + bench_code

    with open(test_file, "w") as f:
        f.write(content)

    print(f"Added benchmark to {pallet_dir}/tests.rs")
