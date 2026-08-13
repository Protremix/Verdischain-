# VRDX Circulating Supply Forecast

**Status:** Computed from approved tokenomics specification  
**Last Updated:** 2026-08-13  
**Max Supply:** 100,000,000,000 VRDX (100B, 9 decimals)

## Methodology

Circulating supply = Total tokens unlocked and transferable at each time point.

Formula per allocation (matching pallet vesting logic):
```
vested(t) = 0                          if t < cliff_days  (cliff-gated, 0 release)
vested(t) = total * t / vesting_days   if cliff_days <= t < vesting_days  (linear from day 0)
vested(t) = total                        if t >= vesting_days  (fully vested)
```

**Note:** Vesting is linear from day 0, but release is gated by cliff. At the cliff moment, all accrued linear vesting becomes releasable.

## Allocation Vesting Schedules

| Category | Amount (VRDX) | Cliff (days) | Vesting (days) | TGE Unlock |
|----------|---------------|-------------|----------------|------------|
| Ecosystem & Grants | 25B | 0 | 0 | 25B (100%) |
| PoS Staking Rewards | 20B | 0 | 0 | 20B (100%) |
| Treasury | 20B | 0 | 0 | 20B (100%) |
| Development | 10B | 0 | 365 | 0 |
| Liquidity | 10B | 0 | 0 | 10B (100%) |
| Community | 5B | 90 | 365 | 0 |
| Seed | 3B | 365 | 730 | 0 |
| Presale | 2B | 180 | 365 | 0 |
| Team & Advisors | 5B | 365 | 1095 | 0 |

## Forecast Table

| Time | Days | Ecosystem | Staking | Treasury | Dev | Liquidity | Community | Seed | Presale | Team | **Total Circ** | **% 100B** |
|------|------|-----------|---------|----------|-----|-----------|-----------|------|---------|------|----------------|------------|
| TGE | 0 | 25.0B | 20.0B | 20.0B | 0 | 10.0B | 0 | 0 | 0 | 0 | **75.0B** | **75.0%** |
| Mo 1 | 30 | 25.0B | 20.0B | 20.0B | 0.8B | 10.0B | 0 | 0 | 0 | 0 | **75.8B** | **75.8%** |
| Mo 3 | 90 | 25.0B | 20.0B | 20.0B | 2.5B | 10.0B | 1.2B | 0 | 0 | 0 | **78.7B** | **78.7%** |
| Mo 6 | 180 | 25.0B | 20.0B | 20.0B | 4.9B | 10.0B | 2.5B | 0 | 2.0B | 0 | **84.4B** | **84.4%** |
| Mo 9 | 270 | 25.0B | 20.0B | 20.0B | 7.4B | 10.0B | 3.7B | 0 | 2.0B | 0 | **88.1B** | **88.1%** |
| Yr 1 | 365 | 25.0B | 20.0B | 20.0B | 10.0B | 10.0B | 5.0B | 1.5B | 2.0B | 1.7B | **95.2B** | **95.2%** |
| Yr 2 | 730 | 25.0B | 20.0B | 20.0B | 10.0B | 10.0B | 5.0B | 3.0B | 2.0B | 3.3B | **98.3B** | **98.3%** |
| Yr 3 | 1095 | 25.0B | 20.0B | 20.0B | 10.0B | 10.0B | 5.0B | 3.0B | 2.0B | 5.0B | **100.0B** | **100.0%** |

## Invariants

1. Circulating at TGE = 75B <= 100B
2. Circulating at full vesting (Yr 3) = 100B exactly
3. Monotonic increase (never decreases)
4. No category exceeds its allocation
5. Investor tokens (Seed+Presale) = 5B, within 12B cap
6. Team vesting is longest: 1095 days, 365-day cliff

## Burn Impact

When `Tokenomics::burn()` is called:
- `total_issuance` decreases by burned amount
- Max supply constant stays 100B
- Circulating = total_issuance - locked_vesting
- Burn creates permanent deflation

## Property Tests

Verified in `pallets/tokenomics/src/economic_invariants.rs`:
- `test_vesting_linear_calculation` - cliff gating, linear accrual, monotonicity
- `test_vesting_total_release_equals_allocation` - sum of releases = allocation
- `test_fundraising_mathematics` - 6.5B tokens, $18M, FDV $500M, 8% TGE
- `test_burn_issuance_invariant` - before - after == burned
- `test_protocol_fee_split_exact` - 40+30+20+10 = 100%
