#!/usr/bin/env python3
with open("/opt/verdis-chain/pallets/dpos/src/tests.rs", "r") as f:
    c = f.read()

old_vote = '''            // Benchmark: vote
            let mut voter_idx = 200u64;
            let w = measure_bench("vote", 50, || {
                voter_idx += 1;
                <pallet_balances::Pallet<Test> as Mutate<u64>>::set_balance(&voter_idx, 100_000 * UNITS);
                Dpos::vote(RuntimeOrigin::signed(voter_idx), 10, 1000 * UNITS).is_ok()
            });
            results.push(("vote", w));'''

new_vote = '''            // Benchmark: vote - pre-fund accounts first
            for i in 200u64..=260u64 {
                <pallet_balances::Pallet<Test> as Mutate<u64>>::set_balance(&i, 100_000 * UNITS);
            }
            let mut voter_idx = 199u64;
            let w = measure_bench("vote", 50, || {
                voter_idx += 1;
                Dpos::vote(RuntimeOrigin::signed(voter_idx), 10, 1000 * UNITS).is_ok()
            });
            results.push(("vote", w));'''

c = c.replace(old_vote, new_vote)
with open("/opt/verdis-chain/pallets/dpos/src/tests.rs", "w") as f:
    f.write(c)
print("Fixed vote benchmark")
