#!/usr/bin/env python3
# Fix the vote benchmark to use genesis-funded accounts
with open("/opt/verdis-chain/pallets/dpos/src/tests.rs", "r") as f:
    c = f.read()

old_vote = '''            // Benchmark: vote - pre-fund accounts first
            for i in 200u64..=260u64 {
                <pallet_balances::Pallet<Test> as Mutate<u64>>::set_balance(&i, 100_000 * UNITS);
            }
            let mut voter_idx = 199u64;
            let w = measure_bench("vote", 50, || {
                voter_idx += 1;
                Dpos::vote(RuntimeOrigin::signed(voter_idx), 10, 1000 * UNITS).is_ok()
            });
            results.push(("vote", w));'''

new_vote = '''            // Benchmark: vote - use genesis-funded accounts (1-5 have 100k UNITS each)
            // Reset balances and re-fund for each iteration
            let mut vote_idx = 0u64;
            let w = measure_bench("vote", 50, || {
                vote_idx += 1;
                let voter = (vote_idx % 5) + 1;
                // Reset balance to ensure funds available
                <pallet_balances::Pallet<Test> as Mutate<u64>>::set_balance(&voter, 100_000 * UNITS);
                Dpos::vote(RuntimeOrigin::signed(voter), 10, 100 * UNITS).is_ok()
            });
            results.push(("vote", w));'''

c = c.replace(old_vote, new_vote)
with open("/opt/verdis-chain/pallets/dpos/src/tests.rs", "w") as f:
    f.write(c)
print("Fixed vote benchmark - using genesis accounts")
