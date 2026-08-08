#!/usr/bin/env python3
"""
VERDIS Tokenomics — Fixed vesting model + comprehensive report generator
"""
import json, math

MAX_SUPPLY = 100_000_000_000

# Fixed vesting schedules (TGE unlocks sum to 8B)
SCHEDULES = {
    "Seed / Strategic": {
        "tokens": 3_000_000_000, "tge_pct": 0, "cliff": 12, "vesting": 36,
    },
    "Community": {
        "tokens": 5_000_000_000, "tge_pct": 20, "cliff": 3, "vesting": 18,  # 20% = 1B at TGE
    },
    "Public Presale": {
        "tokens": 2_000_000_000, "tge_pct": 25, "cliff": 0, "vesting": 6,  # 25% = 0.5B
    },
    "Team & Advisors": {
        "tokens": 5_000_000_000, "tge_pct": 0, "cliff": 12, "vesting": 48,
    },
    "Ecosystem & Developer Grants": {
        "tokens": 25_000_000_000, "tge_pct": 4, "cliff": 0, "vesting": 120,  # 4% = 1B
    },
    "PoS Staking Rewards": {
        "tokens": 20_000_000_000, "tge_pct": 2.5, "cliff": 0, "vesting": 120,  # 2.5% = 0.5B
    },
    "Treasury": {
        "tokens": 15_000_000_000, "tge_pct": 3.33, "cliff": 0, "vesting": 120,  # 3.33% = 0.5B
    },
    "Development": {
        "tokens": 10_000_000_000, "tge_pct": 5, "cliff": 6, "vesting": 48,  # 5% = 0.5B
    },
    "Liquidity": {
        "tokens": 10_000_000_000, "tge_pct": 40, "cliff": 0, "vesting": 60,  # 40% = 4B
    },
}

# Calculate month-by-month unlocks
def calc_unlocks():
    monthly_data = {}
    for cat, s in SCHEDULES.items():
        tge_unlock = s["tokens"] * (s["tge_pct"] / 100)
        linear_tokens = s["tokens"] - tge_unlock
        linear_months = s["vesting"] - s["cliff"]
        monthly_rate = linear_tokens / linear_months if linear_months > 0 else 0
        
        unlocks = []
        for month in range(121):
            if month == 0:
                unlocks.append(tge_unlock)
            elif month > s["cliff"] and month <= s["vesting"]:
                unlocks.append(monthly_rate)
            else:
                unlocks.append(0)
        monthly_data[cat] = {"tge": tge_unlock, "monthly": monthly_rate, "unlocks": unlocks}
    
    # Cumulative
    cumulative = [0] * 121
    for cat, d in monthly_data.items():
        for m in range(121):
            cumulative[m] += d["unlocks"][m]
    
    running = 0
    cum_supply = []
    for m in range(121):
        running += cumulative[m]
        cum_supply.append(running)
    
    return monthly_data, cum_supply

monthly_data, cum_supply = calc_unlocks()

# Verify TGE
tge_total = sum(d["tge"] for d in monthly_data.values())
print(f"TGE circulating: {tge_total:,} ({tge_total/MAX_SUPPLY*100:.1f}%)")

# Print yearly milestones
print("\nCirculating Supply by Year:")
for y in range(11):
    m = y * 12
    supply = cum_supply[m]
    target_pct = [8, 18, 29, 40, 51, 62, 72, 81, 88, 95, 100][y]
    print(f"  Year {y}: {supply/1e9:.2f}B ({supply/MAX_SUPPLY*100:.1f}%) [Target: {target_pct}B]")

# Calculate per-category unlock summary
print("\nPer-Category TGE Unlock:")
for cat, d in monthly_data.items():
    print(f"  {cat}: {d['tge']/1e9:.2f}B")

# Save
with open("vesting_model_fixed.json", "w") as f:
    json.dump({
        "tge_circulating": tge_total,
        "cumulative_supply": cum_supply,
        "monthly_data": {k: {"tge": v["tge"], "monthly": v["monthly"]} for k, v in monthly_data.items()},
    }, f, indent=2)
print("\nSaved to vesting_model_fixed.json")
