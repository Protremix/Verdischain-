# VERDIS CHAIN — TREASURY POLICY

**Created:** 2026-08-14
**Status:** DRAFT — Treasury management is not publicly documented

---

## TREASURY ALLOCATION

| Item | Value | Status |
|---|---|---|
| Treasury allocation (code) | 20,000,000,000 VRDX (20B) | **IMPLEMENTED** |
| Treasury allocation (spec) | 15,000,000,000 VRDX (15B) | **DISCREPANCY** |
| Treasury account type | PalletId (*b"verdistm") | **IMPLEMENTED** — NOT a real multisig |
| Planned account type | 3-of-5 cold storage multisig | **PLANNED** |

## CURRENT TREASURY CONTROL

The treasury is controlled by a PalletId — a code-derived account. Treasury funds are controlled by governance (council + referendum). This is NOT a real multisig.

## PLANNED TREASURY CONTROL

Air-gapped ceremony script generates 5 cold-storage keys for 3-of-5 multisig. Status: PLANNED — not executed.

## TREASURY GOVERNANCE

| Rule | Status |
|---|---|
| Who can propose spending | Council (2/3 majority) |
| Who approves spending | Referendum (token holders) |
| Maximum spend per proposal | NOT DOCUMENTED |
| Transparency requirements | NOT DOCUMENTED |
| Audit requirements | NOT DOCUMENTED |

## TAX/ACCOUNTING TREATMENT

No tax treatment has been confirmed. Tax treatment varies by jurisdiction and requires professional confirmation.
