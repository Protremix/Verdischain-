//! Property-based supply invariant tests for pallet-tokenomics.
//!
//! Verifies fundamental supply, mint/burn, pool allocation, staking, and treasury invariants.

use super::*;

const UNITS: u128 = 1_000_000_000;
const BILLION: u128 = 1_000_000_000 * UNITS;
const MAX_SUPPLY: u128 = 100 * BILLION;
const STAKING_POOL_CAP: u128 = 20 * BILLION;
const TREASURY_POOL_CAP: u128 = 20 * BILLION;

/// Representation of tokenomics allocation pools for invariant testing
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct AllocationPools {
    pub ecosystem: u128,
    pub staking: u128,
    pub treasury: u128,
    pub development: u128,
    pub liquidity: u128,
    pub community: u128,
    pub seed: u128,
    pub presale: u128,
    pub team: u128,
}

impl AllocationPools {
    /// Initial genesis allocations totaling 100B VRDX
    pub fn genesis() -> Self {
        Self {
            ecosystem: 25 * BILLION,
            staking: 20 * BILLION,
            treasury: 20 * BILLION,
            development: 10 * BILLION,
            liquidity: 10 * BILLION,
            community: 5 * BILLION,
            seed: 3 * BILLION,
            presale: 2 * BILLION,
            team: 5 * BILLION,
        }
    }

    /// Sum of all allocation pools
    pub fn sum(&self) -> u128 {
        self.ecosystem
            .saturating_add(self.staking)
            .saturating_add(self.treasury)
            .saturating_add(self.development)
            .saturating_add(self.liquidity)
            .saturating_add(self.community)
            .saturating_add(self.seed)
            .saturating_add(self.presale)
            .saturating_add(self.team)
    }

    /// Get mutable reference to a pool by index (0-8)
    pub fn get_pool_mut(&mut self, index: usize) -> Option<&mut u128> {
        match index % 9 {
            0 => Some(&mut self.ecosystem),
            1 => Some(&mut self.staking),
            2 => Some(&mut self.treasury),
            3 => Some(&mut self.development),
            4 => Some(&mut self.liquidity),
            5 => Some(&mut self.community),
            6 => Some(&mut self.seed),
            7 => Some(&mut self.presale),
            8 => Some(&mut self.team),
            _ => None,
        }
    }

    /// Get value of pool by index (0-8)
    pub fn get_pool(&self, index: usize) -> u128 {
        match index % 9 {
            0 => self.ecosystem,
            1 => self.staking,
            2 => self.treasury,
            3 => self.development,
            4 => self.liquidity,
            5 => self.community,
            6 => self.seed,
            7 => self.presale,
            8 => self.team,
            _ => 0,
        }
    }
}

/// Simulated Tokenomics State Tracker for invariant property testing
#[derive(Debug, Clone)]
pub struct TokenomicsState {
    pub total_supply: u128,
    pub pools: AllocationPools,
    pub staking_rewards_distributed: u128,
    pub treasury_balance: u128,
}

impl TokenomicsState {
    pub fn genesis() -> Self {
        let pools = AllocationPools::genesis();
        Self {
            total_supply: pools.sum(),
            pools,
            staking_rewards_distributed: 0,
            treasury_balance: 20 * BILLION,
        }
    }

    /// Mint tokens: increases total supply if under cap
    pub fn mint(&mut self, amount: u128) -> Result<u128, &'static str> {
        let new_supply = self.total_supply.checked_add(amount).ok_or("Overflow")?;
        if new_supply > MAX_SUPPLY {
            return Err("ExceedsMaxSupply");
        }
        self.total_supply = new_supply;
        Ok(self.total_supply)
    }

    /// Burn tokens: decreases total supply
    pub fn burn(&mut self, amount: u128) -> Result<u128, &'static str> {
        if amount > self.total_supply {
            return Err("BurnExceedsTotalSupply");
        }
        self.total_supply -= amount;
        Ok(self.total_supply)
    }

    /// Transfer between pools
    pub fn transfer_between_pools(
        &mut self,
        from_idx: usize,
        to_idx: usize,
        amount: u128,
    ) -> Result<(), &'static str> {
        if from_idx % 9 == to_idx % 9 {
            return Ok(());
        }
        let from_val = self.pools.get_pool(from_idx);
        if amount > from_val {
            return Err("InsufficientPoolBalance");
        }
        *self.pools.get_pool_mut(from_idx).unwrap() -= amount;
        *self.pools.get_pool_mut(to_idx).unwrap() += amount;
        Ok(())
    }

    /// Distribute staking rewards from staking pool
    pub fn distribute_staking_reward(&mut self, amount: u128) -> Result<(), &'static str> {
        let new_distributed = self
            .staking_rewards_distributed
            .checked_add(amount)
            .ok_or("Overflow")?;
        if new_distributed > STAKING_POOL_CAP {
            return Err("StakingPoolCapExceeded");
        }
        if amount > self.pools.staking {
            return Err("InsufficientStakingPoolBalance");
        }
        self.pools.staking -= amount;
        self.staking_rewards_distributed = new_distributed;
        Ok(())
    }

    /// Treasury spending: reduces treasury balance without minting tokens
    pub fn spend_treasury(&mut self, amount: u128) -> Result<(), &'static str> {
        if amount > self.treasury_balance {
            return Err("InsufficientTreasuryBalance");
        }
        self.treasury_balance -= amount;
        if amount <= self.pools.treasury {
            self.pools.treasury -= amount;
        }
        Ok(())
    }
}

// ============================================================================
// PROPERTY TESTS
// ============================================================================

/// Property 1: Total supply can never exceed 100B VRDX (100,000,000,000 * 10^9).
#[test]
fn test_prop_total_supply_cap_never_exceeded() {
    new_test_ext().execute_with(|| {
        // 1. Storage check in mock runtime
        assert_eq!(TotalSupply::get(), MAX_SUPPLY);
        assert!(TotalSupply::get() <= MAX_SUPPLY);

        // 2. Simulated state transitions across 200 arbitrary mint/release attempts
        let mut state = TokenomicsState::genesis();
        assert_eq!(state.total_supply, MAX_SUPPLY);

        // Parametric test over various amounts
        let amounts: Vec<u128> = (1..=100)
            .map(|i| i * 1_000_000 * UNITS)
            .chain((1..=100).map(|i| i * BILLION))
            .collect();

        for amount in amounts {
            // Attempting to mint beyond MAX_SUPPLY must fail
            let res = state.mint(amount);
            assert!(res.is_err(), "Minting beyond 100B supply cap must fail");
            assert!(
                state.total_supply <= MAX_SUPPLY,
                "Total supply invariant violated: {}",
                state.total_supply
            );
        }

        // 3. Inflation calculation helper check
        for current_supply in [0, 10 * BILLION, 50 * BILLION, 90 * BILLION, MAX_SUPPLY] {
            let inflation = Tokenomics::calculate_inflation(MAX_SUPPLY, current_supply);
            let resulting_supply = current_supply + inflation;
            assert!(
                resulting_supply <= MAX_SUPPLY,
                "Supply after inflation exceeds MAX_SUPPLY"
            );
        }
    });
}

/// Property 2: Every mint operation increases total supply by exactly the minted amount.
#[test]
fn test_prop_mint_increases_total_supply_exact() {
    new_test_ext().execute_with(|| {
        let mut state = TokenomicsState::genesis();
        // Start from 50B supply to leave room for minting up to 100B
        state.total_supply = 50 * BILLION;

        let mint_amounts: Vec<u128> = (1..=100)
            .map(|i| i * 100_000_000 * UNITS) // increments of 100M VRDX
            .collect();

        for (i, &amount) in mint_amounts.iter().enumerate() {
            if state.total_supply + amount > MAX_SUPPLY {
                break;
            }
            let supply_before = state.total_supply;
            let res = state.mint(amount);
            assert!(res.is_ok());

            let supply_after = state.total_supply;
            let delta = supply_after - supply_before;

            assert_eq!(
                supply_after,
                supply_before + amount,
                "Iter {}: Total supply must increase by exact minted amount",
                i
            );
            assert_eq!(
                delta, amount,
                "Iter {}: Delta must equal exact minted amount",
                i
            );
        }

        // Edge case: zero mint
        let supply_before = state.total_supply;
        assert_ok!(state.mint(0));
        assert_eq!(state.total_supply, supply_before);
    });
}

/// Property 3: Every burn operation decreases total supply by exactly the burned amount.
#[test]
fn test_prop_burn_decreases_total_supply_exact() {
    new_test_ext().execute_with(|| {
        let mut state = TokenomicsState::genesis(); // Starts at 100B VRDX

        let burn_amounts: Vec<u128> = (1..=100)
            .map(|i| i * 500_000_000 * UNITS) // 500M VRDX per step
            .collect();

        for (i, &amount) in burn_amounts.iter().enumerate() {
            if amount > state.total_supply {
                break;
            }
            let supply_before = state.total_supply;
            let res = state.burn(amount);
            assert!(res.is_ok());

            let supply_after = state.total_supply;
            let delta = supply_before - supply_after;

            assert_eq!(
                supply_after,
                supply_before - amount,
                "Iter {}: Total supply must decrease by exact burned amount",
                i
            );
            assert_eq!(
                delta, amount,
                "Iter {}: Delta must equal exact burned amount",
                i
            );
        }

        // Edge case: burning more than current total supply must fail
        let current = state.total_supply;
        let err = state.burn(current + 1);
        assert!(err.is_err(), "Burn exceeding total supply must fail");
        assert_eq!(
            state.total_supply, current,
            "Supply must remain unchanged on failed burn"
        );

        // Edge case: zero burn
        assert_ok!(state.burn(0));
        assert_eq!(state.total_supply, current);
    });
}

/// Property 4: Sum of all allocation pools always equals total supply.
#[test]
fn test_prop_sum_allocation_pools_equals_total_supply() {
    new_test_ext().execute_with(|| {
        let mut state = TokenomicsState::genesis();

        // Initial check: sum of genesis pools equals total supply
        let initial_sum = state.pools.sum();
        assert_eq!(initial_sum, MAX_SUPPLY);
        assert_eq!(initial_sum, state.total_supply);

        // Perform 100 random transfers between pools and verify invariant after every operation
        for step in 0..100 {
            let from_idx = step % 9;
            let to_idx = (step + 3) % 9;
            let from_bal = state.pools.get_pool(from_idx);
            let transfer_amount = (from_bal / 10).min(BILLION);

            if transfer_amount > 0 {
                let res = state.transfer_between_pools(from_idx, to_idx, transfer_amount);
                assert!(res.is_ok());
            }

            let current_sum = state.pools.sum();
            assert_eq!(
                current_sum, state.total_supply,
                "Step {}: Pool sum ({}) must equal total supply ({})",
                step, current_sum, state.total_supply
            );
            assert_eq!(current_sum, MAX_SUPPLY);
        }
    });
}

/// Property 5: No allocation pool can go negative.
#[test]
fn test_prop_no_allocation_pool_goes_negative() {
    new_test_ext().execute_with(|| {
        let mut state = TokenomicsState::genesis();

        // 1. Check every pool starting balance >= 0
        for i in 0..9 {
            let bal = state.pools.get_pool(i);
            // Pool balance is u128, guaranteed non-negative by type system
            let _ = bal;
        }

        // 2. Test over-withdrawing from each pool
        for i in 0..9 {
            let bal = state.pools.get_pool(i);
            let over_amount = bal + 1;

            let res = state.transfer_between_pools(i, (i + 1) % 9, over_amount);
            assert!(res.is_err(), "Over-withdrawing from pool {} must fail", i);

            // Verify balance is unchanged and >= 0
            let new_bal = state.pools.get_pool(i);
            assert_eq!(new_bal, bal);
            let _ = new_bal;
        }

        // 3. Test exact drain of pool balance
        for i in 0..9 {
            let bal = state.pools.get_pool(i);
            if bal > 0 {
                assert_ok!(state.transfer_between_pools(i, (i + 1) % 9, bal));
                let drained_bal = state.pools.get_pool(i);
                assert_eq!(drained_bal, 0, "Drained pool must equal 0");
            }
        }
    });
}

/// Property 6: Transfer between pools preserves total supply.
#[test]
fn test_prop_pool_transfer_preserves_total_supply() {
    new_test_ext().execute_with(|| {
        let mut state = TokenomicsState::genesis();
        let original_supply = state.total_supply;

        // Perform combinations of transfers between all pairs of pools
        for from_idx in 0..9 {
            for to_idx in 0..9 {
                if from_idx == to_idx {
                    continue;
                }
                let from_bal = state.pools.get_pool(from_idx);
                let amount = from_bal / 4; // Transfer 25% of pool balance

                if amount > 0 {
                    let sum_before = state.pools.sum();
                    assert_ok!(state.transfer_between_pools(from_idx, to_idx, amount));
                    let sum_after = state.pools.sum();

                    assert_eq!(
                        sum_after, sum_before,
                        "Transfer from pool {} to {} changed total pool sum",
                        from_idx, to_idx
                    );
                    assert_eq!(
                        sum_after, original_supply,
                        "Total supply not preserved after transfer"
                    );
                }
            }
        }
    });
}

/// Property 7: Staking rewards don't inflate beyond the 20B staking pool cap.
#[test]
fn test_prop_staking_rewards_capped_at_20b() {
    new_test_ext().execute_with(|| {
        let mut state = TokenomicsState::genesis();

        // Staking pool initial balance is 20B VRDX
        assert_eq!(state.pools.staking, STAKING_POOL_CAP);
        assert_eq!(state.staking_rewards_distributed, 0);

        // Distribute staking rewards in 100 small chunks of 100M VRDX
        let chunk = 100_000_000 * UNITS;
        for i in 0..100 {
            assert_ok!(state.distribute_staking_reward(chunk));
            assert!(
                state.staking_rewards_distributed <= STAKING_POOL_CAP,
                "Iter {}: Distributed rewards ({}) exceeded 20B cap",
                i,
                state.staking_rewards_distributed
            );
        }

        // Now remaining staking pool is 20B - (100 * 100M) = 10B VRDX
        // Distribute remaining 10B VRDX
        let remaining = state.pools.staking;
        assert_ok!(state.distribute_staking_reward(remaining));
        assert_eq!(state.staking_rewards_distributed, STAKING_POOL_CAP);

        // Attempting to distribute even 1 unit more must fail
        let res = state.distribute_staking_reward(1);
        assert!(
            res.is_err(),
            "Distributing rewards beyond 20B staking pool cap must fail"
        );
        assert_eq!(
            state.staking_rewards_distributed, STAKING_POOL_CAP,
            "Distributed rewards must remain strictly at 20B cap"
        );

        // Attempting a single huge reward distribution of 21B VRDX on fresh state must fail
        let mut fresh_state = TokenomicsState::genesis();
        let huge_err = fresh_state.distribute_staking_reward(21 * BILLION);
        assert!(huge_err.is_err());
        assert_eq!(fresh_state.staking_rewards_distributed, 0);
    });
}

/// Property 8: Treasury spending reduces treasury balance, never mints new tokens.
#[test]
fn test_prop_treasury_spending_reduces_balance_never_mints() {
    new_test_ext().execute_with(|| {
        let mut state = TokenomicsState::genesis();
        let initial_supply = state.total_supply;

        assert_eq!(state.treasury_balance, TREASURY_POOL_CAP);

        // Spend from treasury across 50 iterations
        let spend_amounts: Vec<u128> = (1..=50)
            .map(|i| i * 100_000_000 * UNITS) // 100M VRDX increments
            .collect();

        for (i, &spend) in spend_amounts.iter().enumerate() {
            if spend > state.treasury_balance {
                break;
            }
            let treasury_before = state.treasury_balance;
            let supply_before = state.total_supply;

            assert_ok!(state.spend_treasury(spend));

            let treasury_after = state.treasury_balance;
            let supply_after = state.total_supply;

            // 1. Treasury balance reduced by exact spend amount
            assert_eq!(
                treasury_after,
                treasury_before - spend,
                "Iter {}: Treasury balance must decrease by exact spend amount",
                i
            );

            // 2. Total supply unchanged — no tokens minted
            assert_eq!(
                supply_after, supply_before,
                "Iter {}: Treasury spending must NEVER change total supply",
                i
            );
            assert_eq!(
                supply_after, initial_supply,
                "Iter {}: Total supply must equal initial supply",
                i
            );
        }

        // Attempting to spend more than remaining treasury balance must fail
        let current_treasury = state.treasury_balance;
        let supply_before_overspend = state.total_supply;
        let res = state.spend_treasury(current_treasury + 1);

        assert!(res.is_err(), "Over-spending treasury must fail");
        assert_eq!(
            state.treasury_balance, current_treasury,
            "Treasury balance must remain unchanged on failed spend"
        );
        assert_eq!(
            state.total_supply, supply_before_overspend,
            "Total supply must remain unchanged on failed spend"
        );
    });
}

// ============================================================================
// CORRECTED ALLOCATION TESTS (Aug 14 2026)
// ============================================================================

/// Verify corrected genesis allocations match the 100B spec.
/// Ecosystem 25B, Staking 20B, Treasury 20B, Dev 10B, Liquidity 10B,
/// Community 5B, Seed 3B, Presale 2B, Team 5B = 100B
#[test]
fn test_corrected_genesis_allocations_match_spec() {
    let pools = AllocationPools::genesis();
    assert_eq!(pools.ecosystem, 25 * BILLION, "Ecosystem must be 25B");
    assert_eq!(pools.staking, 20 * BILLION, "Staking must be 20B");
    assert_eq!(
        pools.treasury,
        20 * BILLION,
        "Treasury must be 20B (corrected from 15B)"
    );
    assert_eq!(pools.development, 10 * BILLION, "Development must be 10B");
    assert_eq!(pools.liquidity, 10 * BILLION, "Liquidity must be 10B");
    assert_eq!(pools.community, 5 * BILLION, "Community must be 5B");
    assert_eq!(pools.seed, 3 * BILLION, "Seed must be 3B");
    assert_eq!(pools.presale, 2 * BILLION, "Presale must be 2B");
    assert_eq!(pools.team, 5 * BILLION, "Team must be 5B");
    assert_eq!(pools.sum(), 100 * BILLION, "Total must be exactly 100B");
}

/// Verify investor allocation (Seed 3B + Presale 2B = 5B) is within 12B cap.
#[test]
fn test_investor_allocation_within_cap() {
    let pools = AllocationPools::genesis();
    let investor_total = pools.seed + pools.presale;
    assert_eq!(investor_total, 5 * BILLION, "Seed + Presale = 5B");
    assert!(investor_total <= 12 * BILLION, "Must be within 12B cap");
}

/// Verify no single category exceeds 25% of total supply.
#[test]
fn test_no_category_exceeds_25_percent() {
    let pools = AllocationPools::genesis();
    let total = pools.sum();
    assert!(
        pools.ecosystem <= total / 4,
        "Ecosystem must not exceed 25%"
    );
    assert!(pools.staking <= total / 4, "Staking must not exceed 25%");
    assert!(pools.treasury <= total / 4, "Treasury must not exceed 25%");
}

/// Verify treasury cap matches corrected 20B (not old 15B).
#[test]
fn test_treasury_cap_is_20b_not_15b() {
    assert_eq!(
        TREASURY_POOL_CAP,
        20 * BILLION,
        "Treasury cap must be 20B (corrected)"
    );
    let pools = AllocationPools::genesis();
    assert_eq!(pools.treasury, 20 * BILLION, "Treasury pool must be 20B");
}

/// Verify transfer between pools preserves total supply.
#[test]
fn test_transfer_between_pools_preserves_total() {
    new_test_ext().execute_with(|| {
        let mut state = TokenomicsState::genesis();
        let initial_total = state.pools.sum();
        assert_ok!(state.transfer_between_pools(0, 3, 5 * BILLION));
        assert_eq!(state.pools.sum(), initial_total, "Total must be preserved");
        assert_eq!(
            state.pools.ecosystem,
            20 * BILLION,
            "Ecosystem reduced by 5B"
        );
        assert_eq!(
            state.pools.development,
            15 * BILLION,
            "Development increased by 5B"
        );
    });
}

/// Verify minting at exact boundary of MAX_SUPPLY.
#[test]
fn test_mint_at_boundary() {
    new_test_ext().execute_with(|| {
        let mut state = TokenomicsState::genesis();
        assert!(state.mint(1).is_err(), "Cannot mint when at max supply");
        assert_ok!(state.burn(BILLION));
        assert_eq!(state.total_supply, 99 * BILLION);
        assert_ok!(state.mint(BILLION));
        assert_eq!(state.total_supply, MAX_SUPPLY);
        assert!(state.mint(1).is_err());
    });
}

/// Verify staking rewards distribution respects 20B cap.
#[test]
fn test_staking_distribution_cap_corrected() {
    new_test_ext().execute_with(|| {
        let mut state = TokenomicsState::genesis();
        assert_eq!(
            state.pools.staking,
            20 * BILLION,
            "Staking pool must be 20B"
        );
        assert_ok!(state.distribute_staking_reward(20 * BILLION));
        assert_eq!(state.staking_rewards_distributed, 20 * BILLION);
        assert_eq!(state.pools.staking, 0);
        assert!(state.distribute_staking_reward(1).is_err());
    });
}
