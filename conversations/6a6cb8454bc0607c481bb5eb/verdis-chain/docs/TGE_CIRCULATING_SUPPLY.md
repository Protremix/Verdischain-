# VERDIS CHAIN — TGE CIRCULATING SUPPLY CALCULATION

**Created:** 2026-08-14
**Status:** TARGET — TGE has not occurred. All figures are projections.

---

## MAXIMUM SUPPLY

| Metric | Value | Status |
|---|---|---|
| Maximum supply | 100,000,000,000 VRDX (100B) | **IMPLEMENTED** (chain spec) |
| Decimals | 9 | **IMPLEMENTED** |
| Token symbol | VRDX | **IMPLEMENTED** |

---

## TGE CIRCULATING SUPPLY: 8B VRDX (8%)

This is a **TARGET** calculation. TGE has not occurred.

### Calculation

| Category | Total Allocation | Unlocked at TGE | In Circulating Supply? | Reason |
|---|---|---|---|---|
| Ecosystem & Grants | 25B | 0 | No | Grants vesting per milestone |
| PoS Staking Rewards | 20B | 0 | No | Released via block rewards |
| Treasury | 20B* | 0 | No | Governance-controlled |
| Development | 10B | 0 | No | Vesting per dev milestones |
| Liquidity (DEX) | 10B | 1B | Yes (partial) | Initial DEX liquidity |
| Community | 5B | 1B | Yes | 100% at TGE (community round) |
| Seed | 3B | 0 | No | 730-block cliff, 0% at TGE |
| Presale | 2B | 0.5B | Yes | 25% TGE unlock |
| TGE/IDO | 0.5B | 0.5B | Yes | 100% at TGE |
| Team | 5B | 0 | No | 1095-block cliff |

**Total circulating at TGE:** ~8B (8%) **TARGET**

*Note: Treasury allocation is 20B in code but 15B in spec. This discrepancy must be resolved before TGE.*

---

## UNLOCK SCHEDULE (10-YEAR PROJECTION)

| Time After TGE | Circulating Supply | % of Max |
|---|---|---|
| TGE (Day 0) | 8B | 8% |
| Year 1 | 20B | 20% |
| Year 2 | 35B | 35% |
| Year 3 | 50B | 50% |
| Year 5 | 75B | 75% |
| Year 10 | 95B | 95% |

**Status:** ALL FIGURES ARE TARGETS — not verified.

---

## REPRODUCIBILITY

The circulating supply calculation can be reproduced using:

1. Chain spec allocations (`chain_spec.rs`)
2. Vesting schedules (`pallet_vesting::GenesisConfig`)
3. Block reward rate (`BlockReward = 342 VRDX/block`)
4. TGE unlock percentages per category

However, the actual circulating supply at TGE depends on:
- Whether TGE actually occurs
- Actual token sale results (currently $0 received)
- Actual block time and epoch duration
- Whether vesting parameters are changed before TGE

---

## REQUIRED PUBLIC STATEMENT

> CIRCULATING SUPPLY AT TGE: 8,000,000,000 VRDX (8%) — TARGET
> This is a projection based on planned allocations and vesting schedules.
> TGE has not occurred. Actual circulating supply will depend on actual TGE execution.
> This figure is NOT VERIFIED and should not be presented as a fact.
