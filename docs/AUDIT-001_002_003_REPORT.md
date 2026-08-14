# AUDIT-001, AUDIT-002, AUDIT-003 — Evidence-Based Audit Report

**Branch:** agent/go-live-readiness-2026-08-14
**Date:** 2026-08-14
**Auditor:** Claude (EvolvixOS autonomous audit)
**Scope:** DPoS validator count vs Session configuration, placeholder URIs, tokenomics genesis

---

# AUDIT-001 RESULT

**Status:** CONFIRMED
**Severity:** HIGH

## Evidence

### File: runtime/src/lib.rs
- **Line 583:**  — comment says 6 active validators matching 6 running nodes (STALE/CONTRADICTORY)
- **Line 584:** 
- **Line 596:**  — ActiveValidatorCount = 21
- **Configured value:** ActiveValidatorCount = **21**

### File: node/src/chain_spec.rs
- **Lines 146-152:**  returns 21 URIs:  through 
- **Lines 814-815:**  — creates 21 session key entries
- **Line 823:** BABE authorities:  — only 6 initial BABE authorities (computed but NOT USED — BabeConfig.authorities = vec![])
- **Line 828:** GRANDPA authorities:  — only 6 initial GRANDPA authorities (computed but NOT USED — GrandpaConfig.authorities = vec![])
- **Line 903:**  — **only 6 session keys provided to Session pallet**
- **Line 908:**  — DPoS genesis registers 21 validators
- **Configured value:** SessionConfig keys = **6**, DPoS validator_count = **21**

### File: pallets/dpos/src/lib.rs
- **Lines 1055-1076:**  — returns  (21) validators from 
- **Lines 1078-1089:**  — calls  then returns 
- **Lines 925-970:**  — selects  (21) validators by effective votes
- **Configured value:** DPoS returns **21** validators to Session pallet

### Dead Code
-  (lines 821-824): computed with  but **never used** — BabeConfig.authorities = 
-  (lines 826-829): computed with  but **never used** — GrandpaConfig.authorities = 

## Flow Analysis



## Technical Impact

1. **Chain CAN start** — 6 validators > MinimumValidatorCount (4). No startup failure.
2. **15 of 21 DPoS validators are non-functional** — registered in DPoS, counted as active, but cannot produce blocks or finalize because they have no session keys.
3. **False decentralization** — mainnet claims 21 validators but only 6 are operational at genesis.
4. **Epoch rotation does not fix the issue** —  selects 21 validators, but the 15 without session keys still cannot participate in consensus.
5. **No consensus failure** — the chain produces blocks with 6 validators. BABE/GRANDPA authorities come from the Session pallet's key owners, not from BabeConfig.authorities (which is empty).
6. **Potential governance issue** — if a validator without session keys is selected as a council member (council_members takes 8 URIs, but only 6 have session keys), they cannot participate in consensus but can participate in governance.

## Root Cause

The  constant was changed from 6 to 21 (to satisfy the 21 validators in genesis requirement), but the  in SessionConfig was NOT updated. The stale comment on line 583 (6 active validators matching 6 running nodes) confirms this was originally configured for 6 validators.

The  and  variables were also not updated and are dead code — BabeConfig.authorities and GrandpaConfig.authorities are both .

## Tests Reviewed

| Test | File | Tests 21-validator? | Tests session mismatch? |
|------|------|---------------------|-------------------------|
|  | pallets/dpos/src/lib.rs:1758 | NO (2 validators, AVC=3) | NO |
|  | pallets/dpos/src/lib.rs:1527 | NO (2 validators) | NO |
|  | pallets/dpos/src/lib.rs:1772 | NO (3 validators) | NO |
|  | pallets/dpos/src/lib.rs:1801 | NO (2 validators) | NO |
|  | pallets/dpos/src/lib.rs:2326 | NO (3 validators) | NO |
| Chain spec tests | node/src/chain_spec.rs | NONE EXIST | NONE EXIST |

**No tests cover:**
- 21-validator genesis configuration
- Session initialization with 21 validators
- Validator rotation with 21 validators
-  with 21 validators
- Mismatch between configured DPoS validators and SessionConfig keys

## Recommended Fix

**Minimal patch (Option A — all 21 validators participate at genesis):**

File: , function , line 903:


File: , line 583:


**Alternative (Option B — only 6 initial validators, others join later):**
If only 6 validators will actually run at mainnet launch, keep  but change ActiveValidatorCount to match:


**Recommendation: Option A** — the mainnet spec already has 21 validators in DPoS genesis with stakes. All 21 should have session keys. The  is an artifact of the original 6-validator configuration.

**Note:** The  and  dead code should also be removed or used. Currently they are computed but never referenced.

## Required Regression Tests

1. **Test: 21-validator genesis session keys** — verify SessionConfig has 21 keys
2. **Test: DPoS new_session_genesis returns 21** — verify all 21 validators are returned
3. **Test: Session keys match DPoS validators** — verify every DPoS validator has a session key
4. **Test: ActiveValidatorCount == SessionConfig.keys.len()** — consistency check
5. **Test: rotate_epoch selects validators with session keys** — verify no validator without keys is selected
6. **Test: Chain spec integration** — verify genesis config consistency (validator_count == session keys == ActiveValidatorCount)

---

# AUDIT-002 RESULT

**Status:** CONFIRMED
**Severity:** CRITICAL (if launched as-is), mitigated by explicit replacement requirement

## Evidence

### File: node/src/chain_spec.rs
- **Lines 146-152:**


- **Line 814:**  — called by 
- **Line 815:** 
- **Line 816:**  — generates session keys from placeholder URIs
- **Lines 846-858:** DPoS validators created from these URIs with stakes
- **Lines 860-868:** Validator names set to URI strings
- **Lines 873-877:** Council members taken from these URIs ()

### Usage in mainnet_genesis():
The placeholder URIs  through  are used to derive:
1. **Session keys** (BABE, GRANDPA, ImOnline) via 
2. **DPoS validators** with stakes (6 active × 10M + 15 standby × 1M)
3. **Balance allocations** (6 × 10.001M + 15 × 1.001M)
4. **Validator names** (URI string as bytes)
5. **Council members** (first 8 URIs)

### Security concern:
These are well-known Substrate development URIs. Anyone who knows the URI (e.g., ) can derive the corresponding private key using . Using these on mainnet would allow anyone to impersonate validators, produce blocks, and potentially finalize malicious transactions.

### Mitigation:
The comment explicitly states CRITICAL: PLACEHOLDER URIs - MUST be replaced before mainnet launch. The  file documents this requirement. The key ceremony script () exists for generating real keys. This is a known placeholder, not an oversight.

## Impact

If mainnet launches with these placeholder URIs:
- **Catastrophic security failure** — anyone can derive all 21 validator private keys
- **Network takeover** — attacker can produce blocks, finalize malicious transactions, double-spend
- **Treasury drain** — attacker can approve treasury spends via council majority (8 of 8 council members are placeholder URIs)
- **Complete loss of network integrity**

**Mitigated by:** explicit documentation, key ceremony script, and mainnet launch gate requiring key replacement before launch.

---

# AUDIT-003 RESULT

**Status:** CONFIRMED
**Severity:** MEDIUM

## Evidence

### File: node/src/chain_spec.rs
- **Line 352 (dev):** 
- **Line 700 (testnet):** 
- **Line 912 (mainnet):** 

### File: pallets/tokenomics/src/lib.rs
- **Lines 260-267:** GenesisConfig struct:


- **Lines 271-289:**  implementation:


- **Note:**  and  fields exist in GenesisConfig but are NOT written to storage by .  is a Config trait constant (), not a storage item — it returns 12B regardless.

### Resulting mainnet on-chain state:
| Storage item | Value at genesis |
|---|---|
|  | 0 |
|  | 0 |
|  | empty (no categories) |
|  | 0 |
|  | 0 (ValueQuery default) |
|  | 0 (ValueQuery default) |
|  (Config const) | 12,000,000,000 × 10^9 (correct, from runtime constant) |

### Comparison with Balances pallet:
The Balances pallet DOES allocate 100B VRDX across 9 pools:
- Ecosystem 25B, Staking 20B, Treasury 20B, Development 10B, Liquidity 10B, Community 5B, Seed 3B, Presale 2B, Team 5B

So the token supply EXISTS in the Balances pallet, but the Tokenomics pallet doesn't track it.

## Impact

1. **Tokenomics queries return incorrect values** — any RPC call to  returns 0, not 100B
2. **Presale price = 0** — if presale is enabled, tokens would be sold at price 0, which is economically nonsensical
3. **No distribution categories on-chain** — the 9-category tokenomics allocation is not tracked in the Tokenomics pallet
4. **Circulating supply = 0** — any circulating supply calculation using the Tokenomics pallet returns 0
5. **Presale raised/sold = 0** — presale tracking starts from zero (may be intentional if presale hasn't started)

**Not a security vulnerability** — the Balances pallet correctly allocates tokens. The issue is that the Tokenomics pallet's tracking/metadata is not initialized.

**Functional impact:** any feature relying on , , , or  from the Tokenomics pallet will produce incorrect results.

### Recommended fix (for mainnet):


---

## Summary

| Audit | Status | Severity | Action Required |
|---|---|---|---|
| AUDIT-001 | CONFIRMED | HIGH | Fix  → remove take (all 21 keys) or reduce ActiveValidatorCount to 6 |
| AUDIT-002 | CONFIRMED | CRITICAL (if launched) | Replace placeholder URIs before mainnet launch (documented requirement) |
| AUDIT-003 | CONFIRMED | MEDIUM | Initialize tokenomics GenesisConfig with proper values for mainnet |

**No code changes have been made. This is an audit report only. All fixes require explicit approval before implementation.**
