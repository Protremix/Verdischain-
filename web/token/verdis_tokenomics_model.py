#!/usr/bin/env python3
"""
VERDIS Tokenomics Economic Model Engine
=======================================
Complete mathematical model for VERDIS token (100B max supply)
Part of EvolvixOS + Verdis Blockchain ecosystem
"""

import json
import math
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

# ============================================================================
# CONSTANTS
# ============================================================================
MAX_SUPPLY = 100_000_000_000  # 100B VERDIS
INITIAL_CIRCULATING_TARGET = 8_000_000_000  # 8B at TGE
VALIDATORS_INITIAL = 21
VALIDATORS_EXPANSION = [31, 51, 100, 200]
TGE_UNLOCK_TARGETS = {
    "TGE": 8, "Y1": 18, "Y2": 29, "Y3": 40, "Y4": 51,
    "Y5": 62, "Y6": 72, "Y7": 81, "Y8": 88, "Y9": 95, "Y10": 100
}

# Allocations (provisional)
ALLOCATIONS = {
    "Ecosystem & Developer Grants": {"pct": 25, "tokens": 25_000_000_000},
    "PoS Staking Rewards": {"pct": 20, "tokens": 20_000_000_000},
    "Treasury": {"pct": 15, "tokens": 15_000_000_000},
    "Development": {"pct": 10, "tokens": 10_000_000_000},
    "Liquidity": {"pct": 10, "tokens": 10_000_000_000},
    "Community": {"pct": 5, "tokens": 5_000_000_000},
    "Seed / Strategic": {"pct": 3, "tokens": 3_000_000_000},
    "Public Presale": {"pct": 2, "tokens": 2_000_000_000},
    "Team & Advisors": {"pct": 5, "tokens": 5_000_000_000},
}

# ============================================================================
# 1. SUPPLY MODEL COMPARISON
# ============================================================================
def compare_supply_models():
    """Compare 1B, 5B, 10B, 21B, 100B supply models."""
    models = [1, 5, 10, 21, 100]
    results = {}
    
    for supply_b in models:
        supply = supply_b * 1_000_000_000
        # Staking rewards (20% of supply)
        staking_pool = supply * 0.20
        # Ecosystem (25%)
        ecosystem = supply * 0.25
        # Minimum validator stake (target ~0.01% of supply for decentralization)
        min_validator_stake = supply * 0.0001
        # Token granularity (smallest unit price impact)
        # At $0.001 per token:
        price = 0.001
        fdv = supply * price
        # Staking APR sustainability (20B over 10 years = 2B/year)
        annual_emission = staking_pool / 10
        apr_at_30pct_stake = annual_emission / (supply * 0.30) * 100
        
        results[f"{supply_b}B"] = {
            "supply": supply,
            "fdv_at_001": fdv,
            "staking_pool": staking_pool,
            "ecosystem": ecosystem,
            "min_validator_stake": min_validator_stake,
            "annual_emission_10yr": annual_emission,
            "apr_at_30pct": round(apr_at_30pct_stake, 2),
            "price_per_token": supply_b,  # At $0.001, price per token = supply_b * 0.001
            "granularity_score": 100 / supply_b,  # Higher = more granular
            "psychological_price": 0.001 if supply_b >= 21 else (0.01 if supply_b >= 5 else 0.10),
            "fdv_at_psych_price": supply * (0.001 if supply_b >= 21 else (0.01 if supply_b >= 5 else 0.10)),
        }
    
    return results

# ============================================================================
# 2. SEED / STRATEGIC PRICING ANALYSIS
# ============================================================================
def analyze_seed_pricing():
    """Analyze Seed/Strategic round at multiple price points."""
    seed_tokens = 3_000_000_000  # 3B
    prices = [0.0005, 0.001, 0.002, 0.003]
    tge_price = 0.005  # Assumed TGE price for discount calculation
    
    results = {}
    for price in prices:
        capital_raised = seed_tokens * price
        fdv = MAX_SUPPLY * price
        investor_ownership = (seed_tokens / MAX_SUPPLY) * 100
        discount_to_tge = ((tge_price - price) / tge_price) * 100
        # Vesting: 12-month cliff + 24-month linear = 36 months total
        # TGE unlock: 0%
        vesting_months = 36
        cliff_months = 12
        monthly_unlock = seed_tokens / (vesting_months - cliff_months)
        # Unlock pressure at month 12 (cliff ends): first unlock
        first_unlock = monthly_unlock
        unlock_pct_of_circ = (first_unlock / INITIAL_CIRCULATING_TARGET) * 100
        
        results[f"${price}"] = {
            "price": price,
            "tokens": seed_tokens,
            "capital_raised": capital_raised,
            "fdv": fdv,
            "investor_ownership_pct": round(investor_ownership, 2),
            "discount_to_tge_pct": round(discount_to_tge, 1),
            "cliff_months": cliff_months,
            "vesting_months": vesting_months,
            "monthly_unlock": monthly_unlock,
            "first_unlock_pct_of_circ": round(unlock_pct_of_circ, 2),
            "unlock_start_month": cliff_months + 1,  # Month 13
        }
    
    return results, tge_price

# ============================================================================
# 3. TGE / IDO PRICING ANALYSIS
# ============================================================================
def analyze_tge_pricing():
    """Analyze TGE/IDO at multiple price points."""
    prices = [0.0005, 0.001, 0.002, 0.003, 0.005, 0.010]
    initial_circ = INITIAL_CIRCULATING_TARGET  # 8B
    
    results = {}
    for price in prices:
        fdv = MAX_SUPPLY * price
        initial_mcap = initial_circ * price
        # Capital from presale (2B at ~60% of TGE price)
        presale_price = price * 0.60
        presale_capital = 2_000_000_000 * presale_price
        # Seed capital (3B at ~30% of TGE price)
        seed_price = price * 0.30
        seed_capital = 3_000_000_000 * seed_price
        total_raised = seed_capital + presale_capital
        
        results[f"${price}"] = {
            "price": price,
            "fdv": fdv,
            "initial_mcap": initial_mcap,
            "seed_price": seed_price,
            "seed_capital": seed_capital,
            "presale_price": presale_price,
            "presale_capital": presale_capital,
            "total_raised": total_raised,
        }
    
    return results

# ============================================================================
# 4. VESTING MODEL
# ============================================================================
def build_vesting_model():
    """Build complete vesting schedules for all allocation categories."""
    # Vesting schedules
    schedules = {
        "Seed / Strategic": {
            "tokens": 3_000_000_000,
            "cliff_months": 12,
            "vesting_months": 36,  # 24 months linear after cliff
            "tge_unlock_pct": 0,
        },
        "Community": {
            "tokens": 5_000_000_000,
            "cliff_months": 3,
            "vesting_months": 18,  # 15 months linear after 3-month cliff
            "tge_unlock_pct": 10,  # 10% at TGE
        },
        "Public Presale": {
            "tokens": 2_000_000_000,
            "cliff_months": 0,
            "vesting_months": 6,  # 6-month linear vesting
            "tge_unlock_pct": 25,  # 25% at TGE
        },
        "Team & Advisors": {
            "tokens": 5_000_000_000,
            "cliff_months": 12,
            "vesting_months": 48,  # 36 months linear after cliff
            "tge_unlock_pct": 0,
        },
        "Ecosystem & Developer Grants": {
            "tokens": 25_000_000_000,
            "cliff_months": 0,
            "vesting_months": 120,  # 10-year linear release
            "tge_unlock_pct": 4,  # 4% at TGE (1B)
        },
        "PoS Staking Rewards": {
            "tokens": 20_000_000_000,
            "cliff_months": 0,
            "vesting_months": 120,  # 10-year emission
            "tge_unlock_pct": 0,  # Emissions start post-TGE
        },
        "Treasury": {
            "tokens": 15_000_000_000,
            "cliff_months": 0,
            "vesting_months": 120,  # 10-year governance-controlled release
            "tge_unlock_pct": 3.33,  # 0.5B at TGE
        },
        "Development": {
            "tokens": 10_000_000_000,
            "cliff_months": 6,
            "vesting_months": 48,  # 42 months linear after 6-month cliff
            "tge_unlock_pct": 5,  # 0.5B at TGE
        },
        "Liquidity": {
            "tokens": 10_000_000_000,
            "cliff_months": 0,
            "vesting_months": 60,  # 5-year managed release
            "tge_unlock_pct": 40,  # 4B at TGE
        },
    }
    
    # Calculate month-by-month unlocks
    monthly_unlocks = {}
    for category, sched in schedules.items():
        tokens = sched["tokens"]
        tge_unlock = tokens * (sched["tge_unlock_pct"] / 100)
        linear_tokens = tokens - tge_unlock
        linear_months = sched["vesting_months"] - sched["cliff_months"]
        monthly_linear = linear_tokens / linear_months if linear_months > 0 else 0
        
        unlocks = []
        for month in range(0, 121):  # 10 years (120 months)
            if month == 0:
                unlocks.append(tge_unlock)
            elif month > sched["cliff_months"] and month <= sched["vesting_months"]:
                unlocks.append(monthly_linear)
            else:
                unlocks.append(0)
        
        monthly_unlocks[category] = {
            "tge_unlock": tge_unlock,
            "monthly_linear": monthly_linear,
            "cliff_months": sched["cliff_months"],
            "vesting_months": sched["vesting_months"],
            "unlocks": unlocks,
        }
    
    # Calculate cumulative circulating supply
    cumulative = [0] * 121
    for category, data in monthly_unlocks.items():
        for month in range(121):
            cumulative[month] += data["unlocks"][month]
    
    # Convert to cumulative
    running = 0
    cumulative_supply = []
    for month in range(121):
        running += cumulative[month]
        cumulative_supply.append(running)
    
    return schedules, monthly_unlocks, cumulative_supply

# ============================================================================
# 5. STAKING ECONOMICS
# ============================================================================
def calculate_staking_economics():
    """Calculate staking APR, rewards, and sustainability at different ratios."""
    staking_pool = 20_000_000_000  # 20B
    emission_years = 10
    annual_emission = staking_pool / emission_years  # 2B/year
    monthly_emission = annual_emission / 12
    
    staking_ratios = [0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80]
    results = {}
    
    for ratio in staking_ratios:
        staked_tokens = MAX_SUPPLY * ratio
        apr = (annual_emission / staked_tokens) * 100
        # Validator commission (default 10%)
        commission = 0.10
        validator_rewards = annual_emission * commission
        delegator_rewards = annual_emission * (1 - commission)
        # Per-validator rewards (21 validators)
        per_validator = annual_emission / VALIDATORS_INITIAL
        per_validator_after_commission = per_validator * commission
        # Inflation rate
        # Year 1: 2B emission / circulating supply
        inflation_y1 = (annual_emission / INITIAL_CIRCULATING_TARGET) * 100
        inflation_y5 = (annual_emission / (MAX_SUPPLY * 0.40)) * 100
        inflation_y10 = (annual_emission / (MAX_SUPPLY * 0.72)) * 100
        
        results[f"{int(ratio*100)}%"] = {
            "staking_ratio": ratio,
            "staked_tokens": staked_tokens,
            "apr": round(apr, 2),
            "annual_emission": annual_emission,
            "validator_commission_pct": commission * 100,
            "validator_total_rewards": validator_rewards,
            "delegator_total_rewards": delegator_rewards,
            "per_validator_annual": per_validator,
            "per_validator_commission": per_validator_after_commission,
            "inflation_y1": round(inflation_y1, 2),
            "inflation_y5": round(inflation_y5, 2),
            "inflation_y10": round(inflation_y10, 2),
        }
    
    return results

# ============================================================================
# 6. VALIDATOR ECONOMICS
# ============================================================================
def calculate_validator_economics():
    """Calculate validator economics at different network sizes."""
    staking_pool = 20_000_000_000
    annual_emission = staking_pool / 10  # 2B/year
    
    validator_counts = [21, 31, 51, 100, 200]
    results = {}
    
    for count in validator_counts:
        # Assume 40% staking ratio for base case
        staked_tokens = MAX_SUPPLY * 0.40
        # Minimum stake: enough to be competitive
        # Target: top N validators by stake, min stake = average / 2
        avg_stake = staked_tokens / count
        min_stake = avg_stake * 0.5
        # Per-validator reward
        per_validator_reward = annual_emission / count
        # Commission at 10%
        commission_income = per_validator_reward * 0.10
        delegator_income = per_validator_reward * 0.90
        # Operating costs (estimated)
        # Server: $200/month = $2400/year
        # At TGE price $0.005: 
        tge_price = 0.005
        opex_usd = 2400 + (count * 50)  # Scales slightly with network
        opex_tokens = opex_usd / tge_price
        # Profitability
        profit_tokens = commission_income - opex_tokens
        profit_usd = profit_tokens * tge_price
        # Security threshold (cost to attack: 1/3 of staked)
        attack_cost = staked_tokens * 0.33
        
        results[f"{count}"] = {
            "validator_count": count,
            "staked_tokens": staked_tokens,
            "avg_stake": avg_stake,
            "min_stake": min_stake,
            "per_validator_reward": per_validator_reward,
            "commission_income": commission_income,
            "delegator_income": delegator_income,
            "opex_usd": opex_usd,
            "opex_tokens": opex_tokens,
            "profit_tokens": profit_tokens,
            "profit_usd": round(profit_usd, 2),
            "attack_cost_tokens": attack_cost,
            "attack_cost_usd": attack_cost * tge_price,
        }
    
    return results

# ============================================================================
# 7. ECONOMIC SIMULATION
# ============================================================================
def run_economic_simulation():
    """Run 4-scenario simulation over 1/5/10/20 years."""
    scenarios = {
        "Low": {
            "users_y1": 1_000, "users_growth": 0.30,
            "tx_per_user_month": 10, "tx_growth": 0.15,
            "avg_fee_vrdx": 0.001,
            "staking_ratio": 0.20,
            "validator_count": 21,
        },
        "Base": {
            "users_y1": 10_000, "users_growth": 0.50,
            "tx_per_user_month": 50, "tx_growth": 0.25,
            "avg_fee_vrdx": 0.001,
            "staking_ratio": 0.35,
            "validator_count": 31,
        },
        "High": {
            "users_y1": 50_000, "users_growth": 0.80,
            "tx_per_user_month": 100, "tx_growth": 0.35,
            "avg_fee_vrdx": 0.001,
            "staking_ratio": 0.50,
            "validator_count": 51,
        },
        "Extreme": {
            "users_y1": 200_000, "users_growth": 1.20,
            "tx_per_user_month": 200, "tx_growth": 0.50,
            "avg_fee_vrdx": 0.002,
            "staking_ratio": 0.60,
            "validator_count": 100,
        },
    }
    
    time_horizons = [1, 5, 10, 20]
    results = {}
    
    for scenario_name, params in scenarios.items():
        scenario_results = {}
        for years in time_horizons:
            # Calculate users
            users = params["users_y1"]
            total_users = users
            for y in range(1, years):
                users = int(users * (1 + params["users_growth"]))
                total_users += users
            
            # Calculate transactions
            tx_per_month = params["tx_per_user_month"]
            total_tx = 0
            for y in range(years):
                year_users = int(params["users_y1"] * (1 + params["users_growth"]) ** y)
                monthly_tx = year_users * tx_per_month
                annual_tx = monthly_tx * 12
                total_tx += annual_tx
                tx_per_month = int(tx_per_month * (1 + params["tx_growth"]))
            
            # Fee revenue
            fee_revenue = total_tx * params["avg_fee_vrdx"]
            
            # Staking
            staking_ratio = params["staking_ratio"]
            annual_emission = 20_000_000_000 / 10  # 2B/year
            # After year 10, emissions decrease
            if years > 10:
                remaining_pool = 20_000_000_000 - (annual_emission * 10)
                annual_emission = remaining_pool / max(years - 10, 1)
            
            total_emission = annual_emission * years
            staked = MAX_SUPPLY * staking_ratio
            apr = (annual_emission / staked) * 100 if staked > 0 else 0
            
            # Validators
            validators = params["validator_count"]
            per_validator = annual_emission / validators
            
            # Circulating supply (from vesting model)
            circulating = min(8_000_000_000 + total_emission + (fee_revenue * 0), MAX_SUPPLY)
            
            # Token velocity (transactions / circulating supply)
            velocity = total_tx / circulating if circulating > 0 else 0
            
            scenario_results[f"Y{years}"] = {
                "total_users": total_users,
                "total_transactions": total_tx,
                "fee_revenue_vrdx": round(fee_revenue, 0),
                "fee_revenue_usd": round(fee_revenue * 0.005, 2),  # At $0.005/token
                "staking_ratio": staking_ratio,
                "apr": round(apr, 2),
                "total_emission": total_emission,
                "circulating_supply": circulating,
                "circulating_pct": round((circulating / MAX_SUPPLY) * 100, 1),
                "validators": validators,
                "per_validator_reward": per_validator,
                "token_velocity": round(velocity, 2),
            }
        
        results[scenario_name] = scenario_results
    
    return results

# ============================================================================
# 8. STRESS TESTING
# ============================================================================
def run_stress_tests():
    """Run 12 stress test scenarios."""
    tge_price = 0.005
    initial_circ = 8_000_000_000
    
    tests = [
        {
            "name": "Large Seed Investor Unlock (Month 13)",
            "description": "3B Seed tokens begin linear unlock after 12-month cliff",
            "impact_tokens": 3_000_000_000 / 24,  # Monthly unlock
            "impact_pct": (3_000_000_000 / 24) / initial_circ * 100,
            "sell_pressure": "Medium - 125M/month enters circulating supply",
            "mitigation": "Gradual linear vesting over 24 months prevents sudden dump",
            "severity": "MEDIUM",
        },
        {
            "name": "Large Presale Unlock (TGE + 6 months)",
            "description": "25% of 2B presale at TGE = 500M, remaining 1.5B over 6 months",
            "impact_tokens": 500_000_000,
            "impact_pct": 500_000_000 / initial_circ * 100,
            "sell_pressure": "High at TGE - 500M immediate + 250M/month for 6 months",
            "mitigation": "Whitelist + KYC + purchase limits prevent concentration",
            "severity": "HIGH",
        },
        {
            "name": "Low Staking Participation (10%)",
            "description": "Only 10% of tokens staked, network security weakened",
            "impact_tokens": MAX_SUPPLY * 0.10,
            "impact_pct": 10.0,
            "sell_pressure": "Low sell pressure but HIGH security risk - attack cost only 3.3B tokens",
            "mitigation": "Higher APR incentive, delegation campaigns, minimum staking requirements",
            "severity": "HIGH",
        },
        {
            "name": "High Staking Participation (80%)",
            "description": "80% of circulating tokens staked, low liquidity",
            "impact_tokens": MAX_SUPPLY * 0.80,
            "impact_pct": 80.0,
            "sell_pressure": "Low sell pressure but LOW liquidity - exchange depth reduced",
            "mitigation": "Unbonding period (28 days), liquidity reserves, balanced incentives",
            "severity": "MEDIUM",
        },
        {
            "name": "Low Adoption (Year 1)",
            "description": "Only 1,000 active users, minimal fee revenue",
            "impact_tokens": 0,
            "impact_pct": 0,
            "sell_pressure": "Low sell pressure but ecosystem stunted, treasury drain for operations",
            "mitigation": "Ecosystem grants, developer incentives, marketing campaigns",
            "severity": "MEDIUM",
        },
        {
            "name": "Rapid Adoption (Year 1)",
            "description": "50,000+ users in year 1, high transaction volume",
            "impact_tokens": 0,
            "impact_pct": 0,
            "sell_pressure": "Potential fee market pressure, network congestion if scaling insufficient",
            "mitigation": "Layer 2 readiness, dynamic fee adjustment, validator auto-scaling",
            "severity": "LOW",
        },
        {
            "name": "Large Treasury Expenditure",
            "description": "Treasury spends 2B in a single month on acquisitions/grants",
            "impact_tokens": 2_000_000_000,
            "impact_pct": 2_000_000_000 / initial_circ * 100,
            "sell_pressure": "Medium - if spent on ecosystem (locked) = low; if sold to OTC = medium",
            "mitigation": "Multisig governance, spending limits (max 10% treasury/month), public reporting",
            "severity": "MEDIUM",
        },
        {
            "name": "Liquidity Shortage",
            "description": "DEX liquidity drops below 500M VRDX, high slippage",
            "impact_tokens": 0,
            "impact_pct": 0,
            "sell_pressure": "Price volatility increases, user experience degrades",
            "mitigation": "Liquidity reserve (10B managed), market maker partnerships, CEX listings",
            "severity": "HIGH",
        },
        {
            "name": "Validator Exits (30% of validators leave)",
            "description": "6 of 21 validators go offline simultaneously",
            "impact_tokens": 0,
            "impact_pct": 0,
            "sell_pressure": "Unbonded tokens may be sold, network finality delayed",
            "mitigation": "Slashing penalties, 28-day unbonding, emergency validator recruitment",
            "severity": "HIGH",
        },
        {
            "name": "Large Simultaneous Unlock (Month 13)",
            "description": "Seed cliff ends + Community cliff ends + Development cliff partially overlaps",
            "impact_tokens": (3_000_000_000/24) + (5_000_000_000*0.9/15) + 0,
            "impact_pct": ((3_000_000_000/24) + (5_000_000_000*0.9/15)) / initial_circ * 100,
            "sell_pressure": "High - combined monthly unlock ~425M tokens hitting market",
            "mitigation": "Staggered cliff dates, OTC desks, treasury buyback if severe",
            "severity": "HIGH",
        },
        {
            "name": "Major Network Outage (7 days)",
            "description": "Network halted for 7 days, no transactions processed",
            "impact_tokens": 0,
            "impact_pct": 0,
            "sell_pressure": "Reputation damage, user exodus, staking rewards unaffected but confidence drops",
            "mitigation": "99.9% uptime SLA, failover nodes, emergency recovery procedures, transparent comms",
            "severity": "CRITICAL",
        },
        {
            "name": "Significant Transaction Activity Reduction",
            "description": "Monthly transactions drop 80% due to market downturn",
            "impact_tokens": 0,
            "impact_pct": 0,
            "sell_pressure": "Fee revenue drops 80%, treasury must cover operations, staking APR decreases",
            "mitigation": "Treasury reserve (20B), reduced emissions schedule, ecosystem incentives",
            "severity": "MEDIUM",
        },
    ]
    
    return tests

# ============================================================================
# 9. FUNDRAISING REQUIREMENTS
# ============================================================================
def calculate_fundraising_requirements():
    """Calculate minimum, target, and maximum raise."""
    # Cost estimates (USD, 3-year runway)
    costs = {
        "Development (15 engineers × 3 years)": 15 * 150_000 * 3,  # $6.75M
        "Security Audits (3 rounds)": 300_000,  # $300K
        "Infrastructure (3 years)": 500_000,  # $500K
        "AI Infrastructure": 1_000_000,  # $1M
        "Blockchain Infrastructure": 800_000,  # $800K
        "Legal / Compliance": 500_000,  # $500K
        "Operations (3 years)": 1_200_000,  # $1.2M
        "Liquidity Provisioning": 2_000_000,  # $2M
        "Emergency Reserve": 1_000_000,  # $1M
        "Marketing / Community": 1_000_000,  # $1M
    }
    
    total = sum(costs.values())
    
    minimum_raise = total * 0.5  # Minimum: 50% of total (critical path only)
    target_raise = total  # Target: full runway
    maximum_raise = total * 2.5  # Maximum: 2.5x (avoid over-dilution)
    
    return {
        "costs": costs,
        "total_costs": total,
        "minimum_raise": minimum_raise,
        "target_raise": target_raise,
        "maximum_raise": maximum_raise,
        "minimum_raise_vrdx": minimum_raise / 0.0015,  # At seed price
        "target_raise_vrdx": target_raise / 0.0015,
        "maximum_raise_vrdx": maximum_raise / 0.0015,
    }

# ============================================================================
# 10. FINAL PRICING TABLE
# ============================================================================
def build_final_pricing():
    """Build the final pricing table with all calculations."""
    # Selected prices (from economic model)
    seed_price = 0.0015  # $0.0015 per VERDIS
    community_price = 0.003  # $0.003
    presale_price = 0.004  # $0.004
    tge_price = 0.005  # $0.005
    
    # Allocations
    seed_tokens = 3_000_000_000  # 3B
    community_tokens = 1_000_000_000  # 1B from community allocation
    presale_tokens = 2_000_000_000  # 2B
    tge_tokens = 500_000_000  # 0.5B (rest of public allocation at TGE)
    
    rounds = [
        {
            "round": "Seed / Strategic",
            "price": seed_price,
            "tokens": seed_tokens,
            "capital_raised": seed_tokens * seed_price,
            "fdv": MAX_SUPPLY * seed_price,
            "discount_to_tge": ((tge_price - seed_price) / tge_price) * 100,
            "tge_unlock_pct": 0,
            "vesting": "12-month cliff + 24-month linear",
        },
        {
            "round": "Community",
            "price": community_price,
            "tokens": community_tokens,
            "capital_raised": community_tokens * community_price,
            "fdv": MAX_SUPPLY * community_price,
            "discount_to_tge": ((tge_price - community_price) / tge_price) * 100,
            "tge_unlock_pct": 10,
            "vesting": "3-month cliff + 15-month linear",
        },
        {
            "round": "Public Presale",
            "price": presale_price,
            "tokens": presale_tokens,
            "capital_raised": presale_tokens * presale_price,
            "fdv": MAX_SUPPLY * presale_price,
            "discount_to_tge": ((tge_price - presale_price) / tge_price) * 100,
            "tge_unlock_pct": 25,
            "vesting": "25% TGE + 6-month linear",
        },
        {
            "round": "IDO / TGE",
            "price": tge_price,
            "tokens": tge_tokens,
            "capital_raised": tge_tokens * tge_price,
            "fdv": MAX_SUPPLY * tge_price,
            "discount_to_tge": 0,
            "tge_unlock_pct": 100,
            "vesting": "100% liquid at TGE",
        },
    ]
    
    total_raised = sum(r["capital_raised"] for r in rounds)
    
    return {
        "rounds": rounds,
        "total_raised": total_raised,
        "tge_fdv": MAX_SUPPLY * tge_price,
        "tge_initial_mcap": INITIAL_CIRCULATING_TARGET * tge_price,
    }

# ============================================================================
# MAIN EXECUTION
# ============================================================================
if __name__ == "__main__":
    print("=" * 80)
    print("VERDIS TOKENOMICS ECONOMIC MODEL")
    print("=" * 80)
    
    # 1. Supply Comparison
    print("\n1. SUPPLY MODEL COMPARISON")
    print("-" * 40)
    supply = compare_supply_models()
    for model, data in supply.items():
        print(f"\n  {model} Supply:")
        print(f"    FDV at $0.001: ${data['fdv_at_001']:,.0f}")
        print(f"    Staking Pool: {data['staking_pool']:,.0f}")
        print(f"    APR at 30% stake: {data['apr_at_30pct']}%")
        print(f"    Psychological price: ${data['psychological_price']}")
        print(f"    FDV at psych price: ${data['fdv_at_psych_price']:,.0f}")
    
    print("\n  RECOMMENDATION: 100B supply")
    print("  - Allows granular token pricing ($0.001-$0.005 range)")
    print("  - Staking rewards (20B) provide 10 years of sustainable emissions")
    print("  - Low per-token price is psychologically accessible")
    print("  - Ecosystem grants (25B) can support thousands of projects")
    print("  - vs 1B: Too few tokens, prices would be $0.10+ (less accessible)")
    print("  - vs 21B: Moderate, but staking pool too small for 10-year emissions")
    print("  - 100B enables microtransactions for AI services and developer tools")
    
    # 2. Seed Pricing
    print("\n\n2. SEED / STRATEGIC PRICING")
    print("-" * 40)
    seed, tge_price = analyze_seed_pricing()
    for price, data in seed.items():
        print(f"\n  {price}:")
        print(f"    Capital raised: ${data['capital_raised']:,.0f}")
        print(f"    FDV: ${data['fdv']:,.0f}")
        print(f"    Investor ownership: {data['investor_ownership_pct']}%")
        print(f"    Discount to TGE: {data['discount_to_tge_pct']}%")
        print(f"    Monthly unlock (post-cliff): {data['monthly_unlock']:,.0f}")
        print(f"    First unlock as % of circ: {data['first_unlock_pct_of_circ']}%")
    
    print(f"\n  SELECTED: $0.0015 (between $0.001 and $0.002)")
    print(f"    Capital: $4,500,000 | FDV: $150,000,000 | Discount: 70%")
    print(f"    Vesting: 12-month cliff + 24-month linear")
    print(f"    Rationale: Raises sufficient capital ($4.5M) while maintaining")
    print(f"    70% discount justified by 3-year vesting commitment")
    
    # 3. TGE Pricing
    print("\n\n3. TGE / IDO PRICING")
    print("-" * 40)
    tge = analyze_tge_pricing()
    for price, data in tge.items():
        print(f"\n  {price}:")
        print(f"    FDV: ${data['fdv']:,.0f}")
        print(f"    Initial MCap (8B): ${data['initial_mcap']:,.0f}")
        print(f"    Total raised (seed+presale): ${data['total_raised']:,.0f}")
    
    print(f"\n  SELECTED: $0.005")
    print(f"    FDV: $500,000,000 | Initial MCap: $40,000,000")
    print(f"    Rationale: $500M FDV is reasonable for a blockchain with 15 pallets,")
    print(f"    AMM DEX, eco-features, EVM, and 21+ validators. Not overvalued.")
    
    # 4. Vesting
    print("\n\n4. VESTING MODEL")
    print("-" * 40)
    schedules, unlocks, cumulative = build_vesting_model()
    for cat, sched in schedules.items():
        tge_u = sched["tokens"] * (sched["tge_unlock_pct"] / 100)
        print(f"\n  {cat}:")
        print(f"    Tokens: {sched['tokens']:,}")
        print(f"    TGE unlock: {tge_u:,} ({sched['tge_unlock_pct']}%)")
        print(f"    Cliff: {sched['cliff_months']} months")
        print(f"    Vesting: {sched['vesting_months']} months total")
    
    print("\n  CUMULATIVE CIRCULATING SUPPLY:")
    year_marks = [0, 12, 24, 36, 48, 60, 72, 84, 96, 108, 120]
    for m in year_marks:
        year = m // 12
        print(f"    Year {year}: {cumulative[m]:,.0f} ({cumulative[m]/MAX_SUPPLY*100:.1f}%)")
    
    # 5. Staking
    print("\n\n5. STAKING ECONOMICS")
    print("-" * 40)
    staking = calculate_staking_economics()
    for ratio, data in staking.items():
        print(f"\n  {ratio} staking:")
        print(f"    APR: {data['apr']}%")
        print(f"    Inflation Y1: {data['inflation_y1']}%")
        print(f"    Per validator: {data['per_validator_annual']:,.0f}/yr")
    
    # 6. Validator Economics
    print("\n\n6. VALIDATOR ECONOMICS")
    print("-" * 40)
    validators = calculate_validator_economics()
    for count, data in validators.items():
        print(f"\n  {count} validators:")
        print(f"    Avg stake: {data['avg_stake']:,.0f}")
        print(f"    Min stake: {data['min_stake']:,.0f}")
        print(f"    Per-validator reward: {data['per_validator_reward']:,.0f}/yr")
        print(f"    Profit: ${data['profit_usd']:,.2f}/yr")
        print(f"    Attack cost: ${data['attack_cost_usd']:,.0f}")
    
    # 7. Simulation
    print("\n\n7. ECONOMIC SIMULATION")
    print("-" * 40)
    sim = run_economic_simulation()
    for scenario, years_data in sim.items():
        print(f"\n  {scenario} Adoption:")
        for year, data in years_data.items():
            print(f"    {year}: {data['total_users']:,} users, {data['total_transactions']:,} tx, "
                  f"APR {data['apr']}%, circ {data['circulating_pct']}%")
    
    # 8. Stress Tests
    print("\n\n8. STRESS TESTS")
    print("-" * 40)
    stress = run_stress_tests()
    for test in stress:
        print(f"\n  [{test['severity']}] {test['name']}")
        print(f"    {test['sell_pressure']}")
        print(f"    Mitigation: {test['mitigation']}")
    
    # 9. Fundraising
    print("\n\n9. FUNDRAISING REQUIREMENTS")
    print("-" * 40)
    fund = calculate_fundraising_requirements()
    for cost, amount in fund["costs"].items():
        print(f"  {cost}: ${amount:,.0f}")
    print(f"\n  Total costs: ${fund['total_costs']:,.0f}")
    print(f"  Minimum raise: ${fund['minimum_raise']:,.0f}")
    print(f"  Target raise: ${fund['target_raise']:,.0f}")
    print(f"  Maximum raise: ${fund['maximum_raise']:,.0f}")
    
    # 10. Final Pricing
    print("\n\n10. FINAL PRICING TABLE")
    print("-" * 40)
    pricing = build_final_pricing()
    print(f"  {'Round':<20} {'Price':<10} {'Tokens':<15} {'Capital':<15} {'FDV':<15} {'Discount':<10}")
    for r in pricing["rounds"]:
        print(f"  {r['round']:<20} ${r['price']:<8} {r['tokens']:,}    ${r['capital_raised']:,.0f}    ${r['fdv']:,.0f}    {r['discount_to_tge']:.0f}%")
    print(f"\n  Total raised: ${pricing['total_raised']:,.0f}")
    print(f"  TGE FDV: ${pricing['tge_fdv']:,.0f}")
    print(f"  TGE Initial MCap: ${pricing['tge_initial_mcap']:,.0f}")
    
    # Save all results as JSON
    all_results = {
        "supply_comparison": {k: {kk: vv for kk, vv in v.items()} for k, v in supply.items()},
        "seed_pricing": {k: {kk: vv for kk, vv in v.items()} for k, v in seed.items()},
        "tge_pricing": {k: {kk: vv for kk, vv in v.items()} for k, v in tge.items()},
        "staking": {k: {kk: vv for kk, vv in v.items()} for k, v in staking.items()},
        "validators": {k: {kk: vv for kk, vv in v.items()} for k, v in validators.items()},
        "simulation": sim,
        "stress_tests": stress,
        "fundraising": fund,
        "final_pricing": {k: v for k, v in pricing.items() if k != "rounds"},
        "pricing_rounds": pricing["rounds"],
    }
    
    with open("verdis_tokenomics_results.json", "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    
    print("\n\nResults saved to verdis_tokenomics_results.json")
    print("=" * 80)
