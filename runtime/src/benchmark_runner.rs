//! Standalone benchmark runner - measures real execution times and generates weight values.
#![cfg(feature = "runtime-benchmarks")]

use std::time::{Duration, Instant};
use sp_std::vec::Vec;

pub struct BenchmarkResult {
    pub name: &'static str,
    pub pallet: &'static str,
    pub min_time_ns: u64,
    pub avg_time_ns: u64,
    pub max_time_ns: u64,
    pub iterations: u32,
}

impl BenchmarkResult {
    pub fn to_weight(&self) -> u64 {
        (self.avg_time_ns as f64 * 1.25).max(10000.0) as u64
    }
}

pub fn run_benchmark<F: Fn()>(
    name: &'static str,
    pallet: &'static str,
    iters: u32,
    f: F,
) -> BenchmarkResult {
    let mut times: Vec<Duration> = Vec::with_capacity(iters as usize);
    for _ in 0..3 {
        f();
    }
    for _ in 0..iters {
        let start = Instant::now();
        f();
        times.push(start.elapsed());
    }
    let mn = times.iter().min().unwrap().as_nanos() as u64;
    let mx = times.iter().max().unwrap().as_nanos() as u64;
    let avg = times.iter().map(|t| t.as_nanos() as u64).sum::<u64>() / iters as u64;
    BenchmarkResult {
        name,
        pallet,
        min_time_ns: mn,
        avg_time_ns: avg,
        max_time_ns: mx,
        iterations: iters,
    }
}

pub fn format_results(results: &[BenchmarkResult]) -> String {
    let mut out = String::new();
    for r in results {
        out.push_str(&format!(
            "{}::{} -> min={}ns avg={}ns max={}ns weight={} ({} iters)\n",
            r.pallet, r.name, r.min_time_ns, r.avg_time_ns, r.max_time_ns, r.to_weight(), r.iterations
        ));
    }
    out
}
