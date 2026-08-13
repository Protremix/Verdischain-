# VERDIS CHAIN — FUNDRAISING RECONCILIATION

**Created:** 2026-08-14
**Status:** INITIAL — No funds have been verified as received

---

## EXECUTIVE SUMMARY

The Verdis Chain public materials currently display **"Total Raised: $18M"** as if this amount has been received. **There is no evidence that any funds have been received.** The $18M figure represents the **target hard cap** across four planned fundraising rounds, not actual funds received.

This document reconciles every fundraising figure and classifies it as VERIFIED, TARGET, or NOT VERIFIED.

---

## PLANNED FUNDRAISING ROUNDS

### Round 1: Seed

| Field | Value | Status |
|---|---|---|
| Token allocation | 3,000,000,000 VRDX (3B) | **PLANNED** |
| Price per token | $0.0015 | **TARGET** |
| Discount to TGE | 70% | **TARGET** |
| Hard cap | $4,500,000 | **TARGET** |
| Amount sold | 0 | **VERIFIED** (no sale has occurred) |
| Amount received | $0 | **VERIFIED** (no funds received) |
| Vesting | 730-block cliff, 365-block linear | **IMPLEMENTED** (in chain spec) |
| TGE unlock | 0% | **IMPLEMENTED** |
| KYC required | Yes (per sale page) | **PLANNED** |
| Whitelist required | Yes (per sale page) | **PLANNED** |
| Min purchase | $100 | **PLANNED** |
| Max purchase | $25,000 | **PLANNED** |

**Math verification:** 3,000,000,000 × $0.0015 = $4,500,000 ✅

### Round 2: Community

| Field | Value | Status |
|---|---|---|
| Token allocation | 1,000,000,000 VRDX (1B) | **PLANNED** |
| Price per token | $0.003 | **TARGET** |
| Discount to TGE | 40% | **TARGET** |
| Hard cap | $3,000,000 | **TARGET** |
| Amount sold | 0 | **VERIFIED** |
| Amount received | $0 | **VERIFIED** |
| Vesting | 100% at TGE | **IMPLEMENTED** |
| Min purchase | $100 | **PLANNED** |
| Max purchase | $25,000 | **PLANNED** |

**Math verification:** 1,000,000,000 × $0.003 = $3,000,000 ✅

### Round 3: Presale

| Field | Value | Status |
|---|---|---|
| Token allocation | 2,000,000,000 VRDX (2B) | **PLANNED** |
| Price per token | $0.004 | **TARGET** |
| Discount to TGE | 20% | **TARGET** |
| Hard cap | $8,000,000 | **TARGET** |
| Amount sold | 0 | **VERIFIED** |
| Amount received | $0 | **VERIFIED** |
| Vesting | 365-block cliff, 180-block linear, 25% TGE | **IMPLEMENTED** |
| Min purchase | $100 | **PLANNED** |
| Max purchase | $25,000 | **PLANNED** |

**Math verification:** 2,000,000,000 × $0.004 = $8,000,000 ✅

### Round 4: TGE / IDO

| Field | Value | Status |
|---|---|---|
| Token allocation | 500,000,000 VRDX (0.5B) | **PLANNED** |
| Price per token | $0.005 | **TARGET** |
| Hard cap | $2,500,000 | **TARGET** |
| Amount sold | 0 | **VERIFIED** |
| Amount received | $0 | **VERIFIED** |
| Vesting | 100% at TGE | **IMPLEMENTED** |

**Math verification:** 500,000,000 × $0.005 = $2,500,000 ✅

---

## TOTALS RECONCILIATION

| Metric | Value | Status |
|---|---|---|
| Total tokens across rounds | 6,500,000,000 VRDX (6.5B) | **PLANNED** |
| Total target raise | $18,000,000 | **TARGET** |
| Total verified received | $0 | **VERIFIED** |
| Total committed (signed) | $0 | **VERIFIED** (none documented) |
| Total sold | 0 tokens | **VERIFIED** |
| FDV at TGE price | $500,000,000 | **TARGET** (100B × $0.005) |
| Initial market cap at TGE | $40,000,000 | **TARGET** (8B × $0.005) |

---

## CRITICAL DISTINCTIONS

These terms MUST NOT be used interchangeably:

| Term | Current Status | Must Display As |
|---|---|---|
| ALLOCATION | 6.5B tokens planned | "Planned Allocation" |
| HARD CAP | $18M target | "Target Hard Cap: $18M" |
| AMOUNT RAISED | $0 | "Verified Received: $0" |
| COMMITTED | $0 | "Committed: $0" |
| SIGNED | $0 | "Signed: $0" |
| RECEIVED | $0 | "Received: $0" |
| REMAINING | 6.5B tokens | "Remaining: Full Allocation" |

---

## REQUIRED CHANGES TO SALE PAGE

1. Replace "Total Raised: $18M" with "Total Verified Received: $0 / Target: $18M"
2. Replace any "Hard Cap: $4.5M" that implies raised with "Seed Hard Cap (Target): $4.5M"
3. Mark TGE Price as "TARGET TGE PRICE — NOT GUARANTEED"
4. Mark ROI/APY projections as "TARGET — NOT GUARANTEED"
5. Remove any language implying funds have been received
6. Add disclaimer: "All fundraising figures are targets. No funds have been received."

---

## ACCOUNTING EVIDENCE REQUIRED

If and when funds are actually received, the following must be documented:

- Date of receipt
- Legal entity receiving funds
- Currency (fiat, BTC, ETH, USDT, etc.)
- Transaction hash / bank reference
- Round
- Amount (gross and net)
- Whether committed or settled
- Whether refundable
- Allocation of proceeds
- KYC/AML verification status of payer

---

## LEGAL REVIEW STATUS

| Item | Status |
|---|---|
| Sale terms legal review | **NOT PERFORMED** |
| Referral program legal review | **NOT PERFORMED** |
| MiCA compliance review | **NOT PERFORMED** |
| Token classification (security vs utility) | **NOT VERIFIED** |
| Jurisdiction-specific compliance | **NOT VERIFIED** |

**LEGAL STATUS: NOT YET CONFIRMED**
