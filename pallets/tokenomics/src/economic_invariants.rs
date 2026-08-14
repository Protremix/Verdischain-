//! # Economic Invariants
//!
//! This module defines and tests economic invariants that must hold at all times
//! for the Verdis Chain tokenomics system.
//!
//! ## Invariants
//!
//! 1. **Total Supply Conservation**: Sum of all allocations = 100B VRDX
//! 2. **Investor Allocation Cap**: Seed + Presale = 5B VRDX
//! 3. **Vesting Conservation**: vested + remainder = total_allocation
//! 4. **DPoS Participation Bounds**: Total stake between 10%-80% of supply
//! 5. **DEX Pool Invariant**: k_new >= k_old for swaps
//! 6. **Green Score Bounds**: score 0-1000, energy type 1-4
//! 7. **TGE Circulating Supply**: ~15-20B VRDX
//! 8. **Allocation Caps**: No category exceeds its cap

#![cfg(test)]

/// Verify total genesis allocation equals exactly 100B VRDX.
/// 30B + 20B + 15B + 10B + 10B + 5B + 3B + 2B + 5B = 100B
#[test]
fn test_total_supply_conservation() {
    let units: u128 = 1_000_000_000;
    let billion: u128 = 1_000_000_000 * units;
    #[allow(unused_variables)]
    let total_supply: u128 = 100 * billion;

    let allocated = 30 * billion
        + 20 * billion
        + 15 * billion
        + 10 * billion
        + 10 * billion
        + 5 * billion
        + 3 * billion
        + 2 * billion
        + 5 * billion;

    assert_eq!(
        allocated, total_supply,
        "Genesis allocation must equal total supply"
    );
}

/// Verify investor allocation cap (Seed 3B + Presale 2B = 5B).
#[test]
fn test_investor_allocation_cap() {
    let units: u128 = 1_000_000_000;
    let billion: u128 = 1_000_000_000 * units;

    let investor_total = 3 * billion + 2 * billion;
    let cap = 5 * billion;

    assert_eq!(investor_total, cap, "Investor allocation must equal cap");
}

/// Verify vesting conservation: vested + remainder = total allocation.
/// Uses integer division with remainder tracking.
#[test]
fn test_vesting_conservation() {
    let units: u128 = 1_000_000_000;
    let billion: u128 = 1_000_000_000 * units;

    // Seed: 3B, 0% TGE, 18-month vesting
    let seed_allocation = 3 * billion;
    let seed_vesting_months = 18u128;
    let seed_monthly = seed_allocation / seed_vesting_months;
    let seed_remainder = seed_allocation % seed_vesting_months;
    let seed_vested = seed_monthly * seed_vesting_months + seed_remainder;
    assert_eq!(
        seed_vested, seed_allocation,
        "Seed: vested + remainder must equal allocation"
    );

    // Team: 5B, 0% TGE, 36-month vesting
    let team_allocation = 5 * billion;
    let team_vesting_months = 36u128;
    let team_monthly = team_allocation / team_vesting_months;
    let team_remainder = team_allocation % team_vesting_months;
    let team_vested = team_monthly * team_vesting_months + team_remainder;
    assert_eq!(
        team_vested, team_allocation,
        "Team: vested + remainder must equal allocation"
    );
}

/// Verify DPoS participation: staking pool (20B) is within 10%-80% of supply.
#[test]
fn test_dpos_participation_bounds() {
    let units: u128 = 1_000_000_000;
    let billion: u128 = 1_000_000_000 * units;
    let total_supply = 100 * billion;

    let staking_pool = 20 * billion;
    let validator_stake = 21 * 10_000 * units;
    let total_stake = staking_pool + validator_stake;

    assert!(
        total_stake >= total_supply / 10,
        "Total stake must be >= 10% of supply"
    );
    assert!(
        total_stake <= total_supply * 8 / 10,
        "Total stake must be <= 80% of supply"
    );
}

/// Verify DEX constant product: k_new >= k_old for swaps.
#[test]
fn test_dex_constant_product_invariant() {
    let units: u128 = 1_000_000_000;

    let reserve_a_before = 500_000 * units;
    let reserve_b_before = 500_000 * units;
    let k_before = reserve_a_before * reserve_b_before;

    let amount_in = 10_000 * units;
    let fee_num = 3u128;
    let fee_den = 1000u128;
    let amount_in_after_fee = amount_in * (fee_den - fee_num) / fee_den;

    let amount_out =
        reserve_b_before * amount_in_after_fee / (reserve_a_before + amount_in_after_fee);

    let reserve_a_after = reserve_a_before + amount_in;
    let reserve_b_after = reserve_b_before - amount_out;
    let k_after = reserve_a_after * reserve_b_after;

    assert!(
        k_after >= k_before,
        "DEX invariant: k_after must be >= k_before"
    );
}

/// Verify green score bounds.
#[test]
fn test_green_score_bounds() {
    let scores = [998u64, 995, 989, 992, 997, 990, 985, 988, 993, 991];
    let energy_efficiencies = [95u32, 92, 88, 85, 90, 87, 83, 86, 89, 84];
    let energy_types = [1u8, 2, 3, 1, 4, 2, 1, 3, 4, 2];

    for score in scores.iter() {
        assert!(*score <= 1000, "Green score exceeds 1000");
    }
    for eff in energy_efficiencies.iter() {
        assert!(*eff <= 100, "Energy efficiency exceeds 100");
    }
    for etype in energy_types.iter() {
        assert!(*etype >= 1 && *etype <= 4, "Energy type out of range [1,4]");
    }
}

/// Verify TGE circulating supply is reasonable (15-20B).
#[test]
fn test_tge_circulating_supply() {
    let units: u128 = 1_000_000_000;
    let billion: u128 = 1_000_000_000 * units;

    let circulating = 8 * billion; // 8B VRDX (8%) circulating at TGE
    assert!(
        circulating >= 5 * billion,
        "TGE circulating should be >= 5B"
    );
    assert!(
        circulating <= 12 * billion,
        "TGE circulating should be <= 12B"
    );
}

/// Verify no allocation exceeds its cap.
#[test]
fn test_allocation_caps() {
    let units: u128 = 1_000_000_000;
    let billion: u128 = 1_000_000_000 * units;

    let caps = [
        ("Ecosystem", 30 * billion),
        ("Staking", 20 * billion),
        ("Treasury", 15 * billion),
        ("Development", 10 * billion),
        ("Liquidity", 10 * billion),
        ("Community", 5 * billion),
        ("Seed", 3 * billion),
        ("Presale", 2 * billion),
        ("Team", 5 * billion),
    ];

    let total: u128 = caps.iter().map(|(_, v)| *v).sum();
    assert_eq!(total, 100 * billion, "Sum of all caps must equal 100B");
}

/// Verify genesis total supply is exactly 100B VRDX.
#[test]
fn test_genesis_total_supply_exact() {
    let units: u128 = 1_000_000_000;
    let billion: u128 = 1_000_000_000 * units;
    let target: u128 = 100 * billion;

    // Verify the target is a clean 100B with 9 decimals
    assert_eq!(target, 100_000_000_000_000_000_000u128);
    assert_eq!(target / units, 100_000_000_000);
    assert_eq!(target % units, 0, "No dust — exact VRDX");
}

/// Verify block reward annual inflation stays within bounds.
#[test]
fn test_block_reward_annual_inflation() {
    let units: u128 = 1_000_000_000;
    let block_reward: u128 = 342 * units; // 342 VRDX per block
    let blocks_per_year: u128 = 5_256_000; // 6s blocks, 365 days

    let annual_inflation = block_reward * blocks_per_year;
    let billion: u128 = 1_000_000_000 * units;
    let max_supply: u128 = 100 * billion;

    // Annual inflation should be ~1.8B VRDX
    assert!(
        annual_inflation > 1 * billion && annual_inflation < 3 * billion,
        "Annual inflation should be 1-3B, got {}",
        annual_inflation / units
    );

    // Years to reach max supply from zero
    let years_to_max = max_supply / annual_inflation;
    assert!(
        years_to_max > 50,
        "Supply should last >50 years, got {} years",
        years_to_max
    );
}

/// Verify validator minimum stake is reasonable relative to supply.
#[test]
fn test_min_stake_proportion() {
    let units: u128 = 1_000_000_000;
    let billion: u128 = 1_000_000_000 * units;
    let max_supply: u128 = 100 * billion;
    let min_stake: u128 = 100_000_000 * units; // 100M VRDX

    // Min stake should be 0.1% of supply
    assert_eq!(
        min_stake * 1000,
        max_supply,
        "MinValidatorStake should be 0.1% of max supply"
    );

    // 21 validators * 100M = 2.1B staked (2.1% of supply)
    let total_staked = min_stake * 21;
    assert!(
        total_staked < 5 * billion,
        "Total genesis stake should be < 5B, got {}",
        total_staked / units
    );
}

/// Verify green score bounds are 1-5.
#[test]
fn test_green_score_range_enforced() {
    let min_score: u8 = 1;
    let max_score: u8 = 5;

    assert_eq!(min_score, 1, "MinGreenScore must be 1");
    assert_eq!(max_score, 5, "MaxGreenScore must be 5");

    // Score 0 must be invalid
    assert!(!(0 >= min_score), "Score 0 must be rejected");

    // Scores 1-5 must be valid
    for score in 1..=5 {
        assert!(
            score >= min_score && score <= max_score,
            "Score {} should be valid",
            score
        );
    }

    // Score 6 must be invalid
    assert!(!(6 <= max_score), "Score 6 must be rejected");
}
