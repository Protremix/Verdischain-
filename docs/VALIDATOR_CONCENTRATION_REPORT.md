# Validator Concentration Report

**Date:** 2026-08-14
**Network:** Testnet (block #1126+)

## Summary

| Metric | Value |
|---|---|
| Total Validators | 21 |
| Total Staked | 75,000,000,000 VRDX (75B) |
| Nakamoto Coefficient (>33%) | 3 |
| Top 1 Validator | 13.3% |
| Top 3 Validators | 40.0% |
| Top 5 Validators | 66.7% |

## Stake Distribution

| Tier | Validators | Stake Each | Total | % |
|---|---|---|---|---|
| High-stake (test accounts) | 6 | 10,000,000,000 VRDX | 60,000,000,000 | 80.0% |
| Standard (registered) | 15 | 1,000,000,000 VRDX | 15,000,000,000 | 20.0% |

## Assessment

**Current testnet concentration is HIGH** -- 6 test accounts (Alice-Ferdie) hold 80% of total stake. This is expected for a testnet with known development keys.

**Mainnet requirement:** No single validator controls >10% of total stake. Nakamoto coefficient >= 7 (minimum 7 validators needed to control >33%).

**Mainnet plan:** Air-gapped key ceremony will generate 21 independent validator keys with equal stakes. The high-stake test accounts will be replaced with production validators holding minimum stakes (100M VRDX each).

## Treasury

| Item | Value |
|---|---|
| Treasury PalletId | verdist0 |
| Green Treasury PalletId | vrds/trs |
| Team Multisig (placeholder) | verdistm |
| Treasury Balance | See on-chain query |
| Council Members | 0 (not configured on testnet) |
| Multisig Scheme | 3-of-5 (spec, pending key ceremony) |

## Conclusion

Testnet concentration is acceptable for testing. Mainnet requires the air-gapped key ceremony to generate independent validator keys with distributed stake. The 3-of-5 treasury multisig must replace the placeholder PalletId.
