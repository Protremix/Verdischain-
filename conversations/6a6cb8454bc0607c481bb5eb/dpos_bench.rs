//! Real benchmark weight generation for DPoS pallet.
//! Run with: SKIP_WASM_BUILD=1 cargo test --features runtime-benchmarks -p pallet-dpos -- real_bench --nocapture --ignored

#![cfg(feature = "runtime-benchmarks")]

use std::time::Instant;
use crate::tests::{Test, new_test_ext, UNITS, RuntimeOrigin};
use crate::{self as pallet_dpos, *};
use frame_support::assert_ok;
use frame_support::traits::fungible::Mutate;

fn measure<F: FnMut() -> bool>(name: &str, iters: u32, mut f: F) -> u64 {
    let mut times = Vec::new();
    for _ in 0..iters {
        let start = Instant::now();
        let ok = f();
        let elapsed = start.elapsed().as_nanos() as u64;
        if ok { times.push(elapsed); }
    }
    if times.is_empty() {
        println!("  dpos::{} -> FAILED", name);
        return 10_000;
    }
    let avg = times.iter().sum::<u64>() / times.len() as u64;
    let max = *times.iter().max().unwrap();
    let weight = (avg as f64 * 1.25).max(10000.0) as u64;
    println!("  dpos::{} -> avg={}ns max={}ns weight={}", name, avg, max, weight);
    weight
}

#[test]
#[ignore]
fn real_bench_dpos() {
    new_test_ext().execute_with(|| {
        use frame_system::Pallet as System;
        System::<Test>::set_block_number(1);

        // Setup: fund accounts using the Mutate trait
        for i in 1u64..=300u64 {
            <pallet_balances::Pallet<Test> as Mutate<u64>>::set_balance(&i, 100_000 * UNITS);
        }

        let mut results = Vec::new();

        // Benchmark: register_validator
        let mut idx = 100u64;
        let w = measure("register_validator", 50, || {
            idx += 1;
            Dpos::register_validator(RuntimeOrigin::signed(idx), 80, b"Wind".to_vec()).is_ok()
        });
        results.push(("register_validator", w));

        // Register a validator for vote benchmark
        assert_ok!(Dpos::register_validator(RuntimeOrigin::signed(10), 80, b"Solar".to_vec()));

        // Benchmark: vote
        let mut voter_idx = 200u64;
        let w = measure("vote", 50, || {
            voter_idx += 1;
            <pallet_balances::Pallet<Test> as Mutate<u64>>::set_balance(&voter_idx, 100_000 * UNITS);
            Dpos::vote(RuntimeOrigin::signed(voter_idx), 10, 1000 * UNITS).is_ok()
        });
        results.push(("vote", w));

        // Benchmark: update_green_score (caller must be a validator)
        assert_ok!(Dpos::register_validator(RuntimeOrigin::signed(20), 85, b"Geothermal".to_vec()));
        let w = measure("update_green_score", 50, || {
            Dpos::update_green_score(RuntimeOrigin::signed(20), 95).is_ok()
        });
        results.push(("update_green_score", w));

        // Print weight file
        println!("\n//! WeightInfo for pallet-dpos (real benchmark)");
        println!("pub struct WeightInfo;");
        for (name, weight) in &results {
            println!("// {}: {} weight units", name, weight);
        }
    });
}
