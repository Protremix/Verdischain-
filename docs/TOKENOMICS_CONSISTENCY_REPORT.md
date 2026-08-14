# Verdis Chain Tokenomics Consistency Report (ARCH-010)

**Generated:** 2026-08-14
**Source of Truth:** node/src/chain_spec.rs mainnet_genesis() function
**CI Check:** scripts/check_genesis_consistency.py + .github/workflows/genesis-consistency.yml
**Status:** FROZEN

## Genesis Allocations (Verified by CI)

| # | Allocation | PalletId | Amount | Pct |
|---|-----------|----------|--------|-----|
| 1 | Ecosystem and Developer Grants | verdisec | 25B | 25% |
| 2 | PoS Staking Rewards | verdisdp | 20B | 20% |
| 3 | Treasury | verdist0 | 20B | 20% |
| 4 | Development | verdisdv | 10B | 10% |
| 5 | Liquidity (DEX) | verdisdx | 10B | 10% |
| 6 | Community | verdiscm | 5B | 5% |
| 7 | Seed / Strategic | verdisvs | 3B | 3% |
| 8 | Public Presale | verdisps | 2B | 2% |
| 9 | Team and Advisors | verdistm | 5B | 5% |
| **Total** | | | **100B** | **100%** |

## Vesting Schedules (from code)

| Schedule | Amount | Cliff (blocks) | Duration (blocks) |
|----------|--------|----------------|-------------------|
| Seed | 3B | 730 (12mo) | 365 (6mo linear) |
| Presale | 2B | 365 (6mo) | 180 (3mo linear) |
| Team | 5B | 1095 (18mo) | 365 (6mo linear) |

## Consistency Check Result

CI check: ALL CONSISTENT (9/9 allocations match, total = 100B)

## Genesis Hash

NOT FINAL - placeholder validator keys in use. Hash will be computed and published after air-gapped key ceremony.

## Discrepancies Fixed

1. Treasury 15B to 20B (fixed Aug 14, commit bbdbe97c)
2. Total Raised to Funding Target (fixed Aug 14)
3. Carbon Negative to Energy-Efficient (fixed Aug 14)
4. MIT to Proprietary (fixed Aug 14)
