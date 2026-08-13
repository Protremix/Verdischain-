# VERDIS CHAIN — FINAL TOKENOMICS SPECIFICATION

**Created:** 2026-08-14
**Status:** DRAFT — Contains unresolved discrepancy requiring Rojs confirmation

---

## TOKEN OVERVIEW

| Parameter | Value | Status |
|---|---|---|
| Name | Verdis Chain Token | **CONFIRMED** |
| Symbol | VRDX | **CONFIRMED** |
| Decimals | 9 | **CONFIRMED** |
| SS58 Format | 909 | **CONFIRMED** |
| Maximum Supply | 100,000,000,000 VRDX (100B) | **IMPLEMENTED** (code) |

---

## ALLOCATION TABLE

| # | Category | Amount | % of Max | Code | Spec | Match |
|---|---|---|---|---|---|---|
| 1 | Ecosystem & Developer Grants | 25,000,000,000 | 25% | 25B | 25B | ✅ |
| 2 | PoS Staking Rewards | 20,000,000,000 | 20% | 20B | 20B | ✅ |
| 3 | Treasury | 20,000,000,000 | 20% | **20B** | **15B** | ❌ |
| 4 | Development | 10,000,000,000 | 10% | 10B | 10B | ✅ |
| 5 | Liquidity (DEX) | 10,000,000,000 | 10% | 10B | 10B | ✅ |
| 6 | Community | 5,000,000,000 | 5% | 5B | 5B | ✅ |
| 7 | Seed / Strategic | 3,000,000,000 | 3% | 3B | 3B | ✅ |
| 8 | Public Presale | 2,000,000,000 | 2% | 2B | 2B | ✅ |
| 9 | Team & Advisors | 5,000,000,000 | 5% | 5B | 5B | ✅ |
| | **TOTAL (Code)** | **100,000,000,000** | **100%** | | | |
| | **TOTAL (Spec)** | **95,000,000,000** | **95%** | | | ❌ |

## UNRESOLVED DISCREPANCY

The code allocates **20B to Treasury** (total 100B ✅).
The specification allocates **15B to Treasury** (total 95B ❌).

The spec claims 100B total but only sums to 95B. The code is internally consistent (sums to 100B).

**Rojs must confirm:** Is Treasury 20B (code correct) or 15B (spec correct with missing 5B)?

Until resolved, no public material may state "100B verified" without noting this discrepancy.

---

## FUNDRAISING ROUNDS

| Round | Tokens | Price | Hard Cap | Vesting |
|---|---|---|---|---|
| Seed | 3B | $0.0015 | $4.5M | 730 cliff, 365 linear, 0% TGE |
| Community | 1B | $0.003 | $3M | 100% TGE |
| Presale | 2B | $0.004 | $8M | 365 cliff, 180 linear, 25% TGE |
| TGE/IDO | 0.5B | $0.005 | $2.5M | 100% TGE |
| **Total** | **6.5B** | | **$18M** | |

**Status:** ALL FIGURES ARE TARGETS — $0 VERIFIED RECEIVED.

---

## VESTING DETAIL

### Seed (3B)
- Cliff: 730 blocks (~2 years)
- Linear vesting: 365 blocks (~1 year) after cliff
- TGE unlock: 0%
- Monthly release after cliff: 250M VRDX/month

### Presale (2B)
- Cliff: 365 blocks (~1 year)
- Linear vesting: 180 blocks (~6 months) after cliff
- TGE unlock: 25% (500M VRDX)
- Monthly release after cliff: ~278M VRDX/month

### Team (5B)
- Cliff: 1095 blocks (~3 years)
- Linear vesting: 365 blocks (~1 year) after cliff
- TGE unlock: 0%
- Monthly release after cliff: ~417M VRDX/month

---

## STAKING ECONOMICS

| Parameter | Value | Status |
|---|---|---|
| Staking pool | 20B VRDX | **IMPLEMENTED** |
| Block reward | 342 VRDX/block | **IMPLEMENTED** |
| Annual issuance | ~1.8B VRDX (at 6s blocks) | **TARGET** |
| Target APR | 5-6.67% at 30-40% stake rate | **TARGET** |
| Min validator stake | 100M VRDX | **IMPLEMENTED** |
| Max commission | 20% | **IMPLEMENTED** |
| Slashing | Implemented | **IMPLEMENTED** |
| Target validators | 21 (mainnet) | **PLANNED** |
| Current validators | 6 (devnet) | **TESTNET** |

---

## DEX ECONOMICS

| Parameter | Value | Status |
|---|---|---|
| LP fee | 0.25% | **IMPLEMENTED** |
| Protocol fee | 0.05% (to tokenomics) | **IMPLEMENTED** |
| Total swap fee | 0.30% | **IMPLEMENTED** |
| Initial pools (dev) | 6 | **TESTNET** |
| Initial pools (mainnet) | 0 | **NOT DEPLOYED** |
