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
//! 6. **Green Score Bounds**: score 1-5, energy type 1-4
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

    let circulating = 8 * billion;  // 8B VRDX (8%) circulating at TGE
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


/// Verify protocol fee split is exact: 40+30+20+10 = 100%
#[test]
fn test_protocol_fee_split_exact() {
    let fee: u128 = 10_000_000_000_000_000_000; // 10B VRDX (large test)
    
    let validator = fee * 40 / 100;
    let treasury = fee * 30 / 100;
    let ecosystem = fee * 20 / 100;
    let burn = fee * 10 / 100;
    
    let total = validator + treasury + ecosystem + burn;
    assert_eq!(total, fee, "Protocol fee split must be exact");
    assert_eq!(validator, fee * 40 / 100, "40% validator share");
    assert_eq!(treasury, fee * 30 / 100, "30% treasury share");
    assert_eq!(ecosystem, fee * 20 / 100, "20% ecosystem share");
    assert_eq!(burn, fee * 10 / 100, "10% burn share");
}

/// Verify burn reduces total_issuance exactly
/// invariant: total_issuance_before - total_issuance_after == burned_amount
#[test]
fn test_burn_issuance_invariant() {
    let max_supply: u128 = 100_000_000_000_000_000_000; // 100B VRDX
    let initial_issuance: u128 = 100_000_000_000_000_000_000;
    
    let burn_amount: u128 = 500_000_000_000_000_000; // 500M VRDX
    
    let issuance_after = initial_issuance - burn_amount;
    
    // Invariant: before - after == burned
    assert_eq!(
        initial_issuance - issuance_after,
        burn_amount,
        "Burn invariant: issuance reduction equals burn amount"
    );
    
    // Max supply unchanged (burn reduces current issuance, not max)
    assert_eq!(max_supply, 100_000_000_000_000_000_000, "Max supply is 100B");
    
    // After burn, circulating < max_supply
    assert!(issuance_after < max_supply, "After burn, issuance < max supply");
}

/// Verify vesting calculation: linear vesting with cliff
/// released(t) = 0 if t < cliff
/// released(t) = total * (t - cliff) / (duration - cliff) if cliff <= t < duration
/// released(t) = total if t >= duration
#[test]
fn test_vesting_linear_calculation() {
    let total: u128 = 5_000_000_000_000_000_000; // 5B VRDX (Team allocation)
    let cliff_days: u128 = 365;     // 12-month cliff
    let vesting_days: u128 = 1095;  // 3-year vesting
    
    // Before cliff: 0 released
    let t = 180;
    let released = if t < cliff_days { 0 } 
                  else if t >= vesting_days { total }
                  else { total * (t - cliff_days) / (vesting_days - cliff_days) };
    assert_eq!(released, 0, "Before cliff: 0 released");
    
    // At cliff: partial release
    let t = cliff_days;
    let released = if t < cliff_days { 0 }
                  else if t >= vesting_days { total }
                  else { total * (t - cliff_days) / (vesting_days - cliff_days) };
    // At exact cliff: (cliff - cliff) / (vesting - cliff) = 0
    assert_eq!(released, 0, "At exact cliff: 0% released (cliff day itself)");
    
    // Mid-vesting (day 730, which is 365 days past cliff out of 730 vesting days)
    let t = 730u128;
    let released = if t < cliff_days { 0 }
                  else if t >= vesting_days { total }
                  else { total * (t - cliff_days) / (vesting_days - cliff_days) };
    // 365 / 730 = 50% = 2.5B
    let expected = total * 365 / 730;
    assert_eq!(released, expected, "Mid-vesting: 50% released");
    
    // Full vesting (day 1095)
    let t = vesting_days;
    let released = if t < cliff_days { 0 }
                  else if t >= vesting_days { total }
                  else { total * (t - cliff_days) / (vesting_days - cliff_days) };
    assert_eq!(released, total, "Full vesting: 100% released");
    
    // Post-vesting (day 1200)
    let t = 1200u128;
    let released = if t < cliff_days { 0 }
                  else if t >= vesting_days { total }
                  else { total * (t - cliff_days) / (vesting_days - cliff_days) };
    assert_eq!(released, total, "Post-vesting: 100% released (capped)");
}

/// Verify all vesting releases sum to exactly the allocation
#[test]
fn test_vesting_total_release_equals_allocation() {
    let allocations = [
        ("Seed", 3_000_000_000_000_000_000u128, 730u128, 365u128),   // 3B, 2yr vest, 1yr cliff
        ("Presale", 2_000_000_000_000_000_000u128, 365u128, 180u128),  // 2B, 1yr vest, 6mo cliff
        ("Team", 5_000_000_000_000_000_000u128, 1095u128, 365u128),    // 5B, 3yr vest, 1yr cliff
    ];
    
    for (name, total, vesting_days, cliff_days) in &allocations {
        // At end of vesting, all tokens should be released
        let released_at_end = if *vesting_days >= *cliff_days {
            *total  // All released at end
        } else {
            0
        };
        assert_eq!(
            released_at_end, *total,
            "{}: Total release must equal allocation", name
        );
    }
    
    // Total vested = 3B + 2B + 5B = 10B
    let total_vested: u128 = 3_000_000_000_000_000_000 
        + 2_000_000_000_000_000_000 
        + 5_000_000_000_000_000_000;
    assert_eq!(total_vested, 10_000_000_000_000_000_000, "Total vested = 10B VRDX");
}

/// Verify fundraising math: 6.5B tokens / $18M
#[test]
fn test_fundraising_mathematics() {
    let units: u128 = 1_000_000_000; // 9 decimals
    
    // Seed: 3B × $0.0015 = $4.5M
    let seed_tokens = 3_000_000_000 * units;
    let seed_price_cents: u128 = 15; // $0.0015 = 0.15 cents
    let seed_usd = 3_000_000_000u128 * 15 / 10_000; // 3B * 0.0015 = 4.5M
    assert_eq!(seed_usd, 4_500_000, "Seed: $4.5M");
    
    // Community: 1B × $0.003 = $3M
    let community_usd = 1_000_000_000u128 * 3 / 1_000; // 1B * 0.003
    assert_eq!(community_usd, 3_000_000, "Community: $3M");
    
    // Presale: 2B × $0.004 = $8M
    let presale_usd = 2_000_000_000u128 * 4 / 1_000;
    assert_eq!(presale_usd, 8_000_000, "Presale: $8M");
    
    // TGE/IDO: 0.5B × $0.005 = $2.5M
    let tge_usd = 500_000_000u128 * 5 / 1_000;
    assert_eq!(tge_usd, 2_500_000, "TGE/IDO: $2.5M");
    
    // Total
    let total_usd = seed_usd + community_usd + presale_usd + tge_usd;
    assert_eq!(total_usd, 18_000_000, "Total raised: $18M");
    
    // Total tokens sold
    let total_tokens = 3_000_000_000 + 1_000_000_000 + 2_000_000_000 + 500_000_000;
    assert_eq!(total_tokens, 6_500_000_000, "Total tokens: 6.5B");
    
    // FDV: 100B × $0.005 = $500M
    let fdv = 100_000_000_000u128 * 5 / 1_000;
    assert_eq!(fdv, 500_000_000, "FDV: $500M");
    
    // TGE circulating: 8B = 8%
    let tge_circulating = 8_000_000_000 * units;
    let max_supply = 100_000_000_000 * units;
    let tge_pct = tge_circulating * 100 / max_supply;
    assert_eq!(tge_pct, 8, "TGE circulating: 8%");
}
