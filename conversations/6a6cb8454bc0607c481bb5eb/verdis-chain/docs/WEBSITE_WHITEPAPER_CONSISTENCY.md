# VERDIS CHAIN — WEBSITE / WHITEPAPER CONSISTENCY CHECK

**Created:** 2026-08-14
**Status:** INITIAL — Multiple inconsistencies found

---

## CONSISTENCY MATRIX

| Value | Homepage | Sale Page | Tokenomics | Whitepaper | Docs | Explorer | Code | Consistent? |
|---|---|---|---|---|---|---|---|---|
| Max supply | 100B | 100B | 100B | 100B | - | - | 100B | ✅ |
| Token symbol | VRDX | VRDX | VRDX | VRDX | VRDX | VRDX | VRDX | ✅ |
| Decimals | 9 | 9 | 9 | 9 | 9 | - | 9 | ✅ |
| Network status | "Testnet Live" | - | - | "Live testnet" | "Live" | "Live" | Dev chain | ❌ Misleading |
| Total raised | - | "$18M" | "$18M" | - | - | - | $0 | ❌ FALSE |
| TGE price | $0.005 | $0.005 | $0.005 | - | - | - | - | ✅ (but TARGET) |
| Pallet count | "30+" | - | - | "30+" | "15" | - | 16 custom | ❌ |
| Validators | - | - | - | "21 registered" | - | 6 active | 6 dev / 21 spec | ❌ |
| DEX fee | - | - | 0.30% | 0.30% | - | - | 0.30% | ✅ |
| Treasury | - | - | - | - | - | - | 20B (code) / 15B (spec) | ❌ |
| Carbon claim | "Carbon Negative" | - | - | "Carbon Negative" | "Carbon Negative" | "Carbon Negative" | Implemented | ❌ Not verified |
| Audit claim | - | - | - | "8/10 score" | - | - | Internal only | ❌ FALSE |
| Presale vesting | "3-mo cliff" | "No cliff, 25% TGE" | "25% TGE, 6mo" | - | - | - | 365 cliff, 180 linear | ❌ Contradicts |

---

## INCONSISTENCIES FOUND

### 1. "Total Raised: $18M" — FALSE

- **Sale page:** Displays "Total Raised: $18M" prominently
- **Tokenomics page:** Also shows "$18M"
- **Reality:** $0 verified received. $18M is the TARGET hard cap.
- **Action:** Replace with "Total Verified Received: $0 / Target: $18M"

### 2. Pallet Count — Contradictory

- **Homepage/Whitepaper:** "30+ pallets"
- **Docs page:** "15 runtime pallets"
- **Code:** 16 custom pallet directories, 42 entries in construct_runtime! (including frame pallets)
- **Action:** State "16 custom pallets + frame system pallets" consistently

### 3. Network Status — Misleading

- **Homepage:** "Testnet Live" with "Block ##" placeholder
- **Whitepaper:** "Live testnet"
- **Explorer:** "LIVE"
- **Reality:** Development chain (ChainType::Development), not a proper testnet
- **Action:** All pages must say "DEVELOPMENT CHAIN — NOT MAINNET"

### 4. Presale Vesting — Contradictory

- **Homepage:** "3-month cliff" for Public Presale
- **Sale page card:** "25% TGE + 6mo" (no cliff mentioned)
- **Sale page FAQ:** "25% TGE, 3-month cliff, 6.25%/month for 12 months"
- **Code:** 365-block cliff, 180-block linear, 25% TGE unlock
- **Action:** Reconcile all presale vesting descriptions to match code

### 5. Whitelist Bonus — Contradictory

- **Sale page FAQ:** "No bonus tokens are offered"
- **Sale page whitelist modal:** "Additional 5% bonus tokens"
- **Action:** Remove whitelist bonus or remove "no bonus" statement — they contradict

### 6. Audit Claim — FALSE

- **Whitepaper:** Claims security audit completed Q3 2026 with "8/10" score
- **Reality:** No independent audit exists. Score is self-assessed.
- **Action:** Remove audit claim or replace with "Internal review only — no independent audit"

### 7. Environmental Claims — Not Verified

- **Multiple pages:** "12,847t CO2 Offset", "47,392 Trees", "-142% Carbon Negative"
- **Multiple pages:** Partnership claims with Verra, Gold Standard, UN, WWF
- **Reality:** Simulated testnet numbers. No independent verification. No verified partnerships.
- **Action:** Mark as "SIMULATED TESTNET DATA — NOT VERIFIED"

### 8. Template Placeholders Visible

- **Homepage:** "Block ##", "#---", "--/14 Peers", "0 Runtime Pallets", "0 Production Pallets"
- **Action:** Fix live data integration or remove placeholder displays

---

## REQUIRED CONSISTENCY ACTIONS

1. Fix "Total Raised" on all pages ($0 verified / $18M target)
2. Fix network status on all pages (DEVELOPMENT CHAIN)
3. Fix pallet count to "16 custom pallets" consistently
4. Reconcile presale vesting description across all pages
5. Remove whitelist bonus contradiction
6. Remove false audit claim from whitepaper
7. Mark environmental claims as "SIMULATED — NOT VERIFIED"
8. Remove or verify partnership claims (Verra, Gold Standard, UN, WWF)
9. Fix template placeholders on homepage
10. Add "TARGET" qualifier to all TGE/financial projections
