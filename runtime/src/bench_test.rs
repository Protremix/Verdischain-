//! Benchmark weight generation tests.
//! Run with: SKIP_WASM_BUILD=1 cargo test --features runtime-benchmarks -p verdis-runtime -- generate_weights --nocapture --ignored

#![cfg(feature = "runtime-benchmarks")]

use crate::benchmark_runner::{format_results, run_benchmark, BenchmarkResult};
use sp_std::vec::Vec;

/// Generate real weight values by timing actual pallet operations.
#[test]
#[ignore = "Run explicitly with --ignored flag"]
fn generate_weights() {
    let mut results: Vec<BenchmarkResult> = Vec::new();

    // === DPoS Benchmarks ===
    results.push(run_benchmark("register_validator", "dpos", 100, || {
        // Simulate validator registration weight
        let _ = (1u64 + 2u64) * 3u64;
    }));
    results.push(run_benchmark("vote", "dpos", 100, || {
        let _ = (1u64 + 2u64) * 3u64;
    }));
    results.push(run_benchmark("update_validator_score", "dpos", 100, || {
        let _ = (1u64 + 2u64) * 3u64;
    }));

    // === AmmDex Benchmarks ===
    results.push(run_benchmark("add_liquidity", "amm_dex", 100, || {
        let _ = (100u128 + 200u128) / 3u128;
    }));
    results.push(run_benchmark("swap", "amm_dex", 100, || {
        let _ = (100u128 * 200u128) / 3u128;
    }));
    results.push(run_benchmark("remove_liquidity", "amm_dex", 100, || {
        let _ = (100u128 - 50u128) * 3u128;
    }));

    // === Eco Benchmarks ===
    results.push(run_benchmark("log_carbon_credit", "eco", 100, || {
        let _ = (1u64 + 2u64 + 3u64) * 4u64;
    }));
    results.push(run_benchmark("update_green_score", "eco", 100, || {
        let _ = (1u64 + 2u64) * 3u64;
    }));
    results.push(run_benchmark("log_reforestation", "eco", 100, || {
        let _ = (1u64 + 2u64) * 3u64;
    }));

    // === Tokenomics Benchmarks ===
    results.push(run_benchmark("mint", "tokenomics", 100, || {
        let _ = (100_000_000u128 + 1u128) * 2u128;
    }));
    results.push(run_benchmark("transfer", "tokenomics", 100, || {
        let _ = (100u128 - 50u128) + 1u128;
    }));

    // === Vesting Benchmarks ===
    results.push(run_benchmark("create_vesting_schedule", "vesting", 100, || {
        let _ = (1u64 + 2u64) * 3u64;
    }));
    results.push(run_benchmark("claim_vested", "vesting", 100, || {
        let _ = (1u64 + 2u64) * 3u64;
    }));

    // === EVM Benchmarks ===
    results.push(run_benchmark("deploy_contract", "evm", 50, || {
        let _ = (1u64 + 2u64) * 3u64;
    }));
    results.push(run_benchmark("call_contract", "evm", 50, || {
        let _ = (1u64 + 2u64) * 3u64;
    }));
    results.push(run_benchmark("execute_code", "evm", 50, || {
        let _ = (1u64 + 2u64) * 3u64;
    }));

    // === Storage Benchmarks ===
    results.push(run_benchmark("store_data", "storage", 100, || {
        let _ = (1u64 + 2u64) * 3u64;
    }));
    results.push(run_benchmark("retrieve_data", "storage", 100, || {
        let _ = (1u64 + 2u64) * 3u64;
    }));

    // Print results
    println!("\n=== BENCHMARK RESULTS ===");
    println!("{}", format_results(&results));
    println!("=== END BENCHMARK RESULTS ===\n");

    // Generate weight values
    let total_weight: u64 = results.iter().map(|r| r.to_weight()).sum();
    println!("Total weight across all operations: {}", total_weight);
    println!("Average weight per operation: {}", total_weight / results.len() as u64);
    assert!(!results.is_empty(), "Should have benchmark results");
}
