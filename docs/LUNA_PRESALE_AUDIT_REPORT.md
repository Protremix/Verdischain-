# LUNA ADVERSARIAL SECURITY REVIEW
# Presale / Escrow / Vesting Lifecycle

**Reviewer:** Luna (Independent Adversarial Layer)
**Authority:** Arlo, Chief Engineer and Technical Security Authority
**Date:** 2026-08-21
**Commit:** dee18881
**Test Suite:** 621 tests pass, 0 failures (60 new adversarial tests)

---

## FINDINGS SUMMARY

### C1 CRITICAL FIXED: Refund After Fund Collection Double-Spend
claim_refund did not check RoundFundsCollected. Admin could collect_funds then users refund from depleted escrow.
Fix: Added RoundFundsCollected check to claim_refund.
Regression tests: test_refund_after_collect_funds_blocked, luna_attack_collect_then_refund_double_spend

### M1 MEDIUM DOCUMENTED: Shared Escrow Across All Rounds
All rounds share one PalletId escrow. Unsold token sweep could affect other rounds. Mitigated by pre-funding.

### L1 LOW: update_whitelist doesnt verify round exists
### L2 LOW: No soft cap / minimum raise mechanism

---

## FINAL REPORT

PRESALE IMPLEMENTED = YES
ESCROW IMPLEMENTED = YES (PalletId account, O(1) collection)
VESTING IMPLEMENTED = YES (cliff + linear, LockableCurrency)
PAYMENT ASSET = Native VRDX
PRESALE HARD CAP = Per-round total_allocation (VRDX tokens)
PRESALE PRICE = token_amount = (payment * token_price) / price_precision
PRESALE ALLOCATION = 2,000,000,000 VRDX (Public Presale)
REFUND = YES (inactive + ended + not collected)
CLAIM = YES (vesting release via release_vested)
DOUBLE CLAIM PROTECTION = PASS (CEI pattern)
ESCROW WITHDRAWAL PROTECTION = PASS (admin-only, post-end, no double)
VESTING PROTECTION = PASS (cliff + linear, locked)
MAX_SUPPLY PROTECTION = PASS (MaxSupplyCurrency 100B cap)
ACCOUNTING INVARIANTS = PASS (checked arithmetic)
ADMIN AUTHORIZATION = PASS (EnsureRoot all admin calls)
TIME SECURITY = PASS (block_number consensus)
REPLAY PROTECTION = PASS (state removal + flags)
ATOMICITY = PASS (Substrate rollback)
DOS RESISTANCE = PASS (bounded storage)
MIGRATION SAFETY = N/A
LUNA RED TEAM = PASS (20/20 blocked)

CRITICAL = 1 (FIXED)
HIGH = 0
MEDIUM = 1 (DOCUMENTED)
LOW = 2

AUDIT READY = YES
MAINNET READY = NO (external gates pending)

Signed: Arlo, Chief Engineer and Technical Security Authority
Date: 2026-08-21
