# VERDIS CHAIN — PUBLIC SOURCE OF TRUTH

> **This document is the single authoritative source for every material public claim about Verdis Chain.**
> If any website, whitepaper, sale page, GitHub README, or social media post contradicts this document, **this document prevails** until the underlying evidence changes and this document is updated.

**Last updated:** 2026-08-14
**Git commit:** d0718deb
**Verification date:** 2026-08-14
**Owner:** Rojs Gordons (Founder & CEO)
**Classification:** PUBLIC

---

## CLASSIFICATION SYSTEM

Every claim in this document is classified as one of:

| Classification | Meaning |
|---|---|
| **LIVE** | Currently running and verifiable on the live network |
| **TESTNET** | Running on testnet/devnet only, not on mainnet |
| **MAINNET** | Live on mainnet (requires block/hash evidence) |
| **IMPLEMENTED / NOT DEPLOYED** | Code exists but not deployed to any network |
| **PLANNED** | Intended future work, no code yet |
| **TARGET** | A goal or projection, not an achieved fact |
| **SCENARIO / EXAMPLE** | Illustrative, not a factual measurement |
| **INDEPENDENTLY VERIFIED** | Verified by a third party with evidence |
| **NOT VERIFIED** | No evidence available; claim must not be presented as fact |

---

## 1. NETWORK STATUS

| Claim | Value | Status | Evidence |
|---|---|---|---|
| Network is live | Yes, as development chain | **TESTNET** | `system_chain` RPC returns "Verdis Dev"; `system_chainType` returns "Development" |
| Mainnet is live | No | **NOT VERIFIED** | Mainnet chain spec exists (`mainnet_spec()` in `chain_spec.rs`) but is NOT deployed. No mainnet block hash exists. |
| Testnet is live | No separate testnet running | **TESTNET** | Only dev chain ("Verdis Dev") is running. Testnet spec exists but is not deployed as a separate network. |
| Production network | No | **NOT VERIFIED** | Chain type is "Development", not "Live" |
| Current block height | ~1173 | **LIVE** | `chain_getHeader` RPC, block #1173 as of 2026-08-14 |
| Peer count | 0 | **LIVE** | `system_health` RPC returns peers: 0 |
| Runtime version | verdis-chain spec v14 | **LIVE** | `state_getRuntimeVersion` RPC |
| Chain type | Development | **LIVE** | `system_chainType` RPC returns "Development" |

**REQUIRED PUBLIC STATEMENT:**
> VERDISCHAIN IS CURRENTLY RUNNING AS A DEVELOPMENT CHAIN.
> VRDX DEVNET TOKENS HAVE NO MONETARY VALUE.
> DEVNET STATE MAY BE RESET AT ANY TIME.
> MAINNET IS NOT LIVE.
> MAINNET IS PLANNED BUT NOT YET LAUNCHED.

---

## 2. TOKEN SPECIFICATION

| Claim | Value | Status | Evidence |
|---|---|---|---|
| Token symbol | VRDX | **LIVE** | `common_props()` in `chain_spec.rs` sets `tokenSymbol: "VRDX"` |
| Decimals | 9 | **LIVE** | `common_props()` in `chain_spec.rs` sets `tokenDecimals: 9` |
| SS58 format | 909 | **LIVE** | `common_props()` in `chain_spec.rs` sets `ss58Format: 909` |
| Maximum supply | 100,000,000,000 VRDX (100B) | **IMPLEMENTED** | `chain_spec.rs` allocations sum to 100B (verified by code audit) |
| Circulating supply at TGE | 8,000,000,000 VRDX (8B, 8%) | **TARGET** | `CIRCULATING_SUPPLY` constant in `runtime/src/lib.rs:138`. This is a TARGET, not a verified on-chain value, because TGE has not occurred. |
| Current circulating supply | NOT VERIFIED | **NOT VERIFIED** | No TGE has occurred. Devnet tokens have no monetary value. |

---

## 3. TOKENOMICS — ALLOCATION RECONCILIATION

### Code Allocations (chain_spec.rs — verified)

| Category | Code Amount | Spec Amount (USER.md) | Match? |
|---|---|---|---|
| Ecosystem & Developer Grants | 25B | 25B | ✅ |
| PoS Staking Rewards | 20B | 20B | ✅ |
| Treasury | **20B** | **15B** | ❌ **DISCREPANCY** |
| Development | 10B | 10B | ✅ |
| Liquidity (DEX) | 10B | 10B | ✅ |
| Community | 5B | 5B | ✅ |
| Seed / Strategic | 3B | 3B | ✅ |
| Public Presale | 2B | 2B | ✅ |
| Team & Advisors | 5B | 5B | ✅ |
| **TOTAL (Code)** | **100B** | | |
| **TOTAL (Spec)** | | **95B** | ❌ Spec sums to 95B, not 100B |

### CRITICAL DISCREPANCY

The code allocates **20B to Treasury** (totaling 100B), but the specification in the project documentation allocates **15B to Treasury** (totaling only 95B).

**Status:** NOT VERIFIED — requires Rojs Gordons to confirm which is correct:
- Option A: Treasury = 20B (code is correct, spec needs updating)
- Option B: Treasury = 15B and there is a missing 5B allocation (spec needs an additional category)

**No public material may state "100B total supply" as verified until this discrepancy is resolved.**

### Automated Invariant

```rust
// This invariant MUST pass:
assert_eq!(
    25 + 20 + 20 + 10 + 10 + 5 + 3 + 2 + 5, // code allocations
    100, // 100B
);
// Spec allocations: 25 + 20 + 15 + 10 + 10 + 5 + 3 + 2 + 5 = 95 (WRONG)
```

---

## 4. FUNDRAISING — RECONCILIATION

### Planned Fundraising Rounds (from sale page)

| Round | Tokens | Price | Hard Cap | Status |
|---|---|---|---|---|
| Seed | 3,000,000,000 VRDX | $0.0015 | $4,500,000 | **PLANNED** |
| Community | 1,000,000,000 VRDX | $0.003 | $3,000,000 | **PLANNED** |
| Presale | 2,000,000,000 VRDX | $0.004 | $8,000,000 | **PLANNED** |
| TGE/IDO | 500,000,000 VRDX | $0.005 | $2,500,000 | **PLANNED** |
| **Total** | **6,500,000,000 VRDX** | | **$18,000,000** | **PLANNED** |

### CRITICAL FINDING — "$18M Total Raised" Claim

The sale page currently displays **"Total Raised: $18M"** as if funds have been received.

**Status:** **NOT VERIFIED — this claim is likely FALSE.**

There is no evidence that any funds have been received. The $18M figure is the **target hard cap** across all rounds, not the actual amount received.

**REQUIRED ACTION:** Replace "Total Raised: $18M" with:
```
TOTAL VERIFIED RECEIVED: $0
TARGET HARD CAP: $18,000,000
```

### Field Definitions

| Field | Definition |
|---|---|
| ALLOCATION | Tokens allocated to this round |
| PRICE | Price per token in this round |
| HARD CAP | Maximum this round intends to raise |
| AMOUNT SOLD | Tokens actually sold (NOT VERIFIED — 0) |
| AMOUNT RECEIVED | Fiat/crypto actually received (NOT VERIFIED — $0) |
| REMAINING | Tokens still available (NOT VERIFIED — full allocation) |
| TARGET | The goal, not an achieved amount |

### TGE Price

| Claim | Value | Status |
|---|---|---|
| TGE Price | $0.005 | **TARGET** — not a guaranteed market price |
| FDV at TGE | $500M | **TARGET** — assumes 100B × $0.005 |
| Initial Market Cap | $40M | **TARGET** — assumes 8B circulating × $0.005 |

**REQUIRED STATEMENT:**
> TARGET TGE PRICE — NOT GUARANTEED
> Market price will be determined by market conditions at listing.

---

## 5. VESTING SCHEDULES (from chain_spec.rs)

| Category | Total | Cliff (blocks) | Vesting (blocks) | Status |
|---|---|---|---|---|
| Seed | 3B | 730 | 365 | **IMPLEMENTED** |
| Presale | 2B | 365 | 180 | **IMPLEMENTED** |
| Team | 5B | 1095 | 365 | **IMPLEMENTED** |
| Community | 1B | 0 | 0 | **IMPLEMENTED** (100% at TGE) |
| TGE/IDO | 0.5B | 0 | 0 | **IMPLEMENTED** (100% at TGE) |

**Note:** Block counts are approximate day equivalents. Exact unlock schedule requires chain block time verification.

---

## 6. CIRCULATING SUPPLY CALCULATION

### Target TGE Circulating Supply: 8B VRDX (8%)

| Category | Unlocked at TGE | Reason |
|---|---|---|
| Ecosystem & Grants | 0 | Vesting per grant terms |
| Staking Rewards | 0 | Released via block rewards over time |
| Treasury | 0 | Governance-controlled |
| Development | 0 | Vesting per dev milestones |
| Liquidity (DEX) | 1B (partial) | Initial DEX liquidity |
| Community | 1B | 100% at TGE (community round) |
| Seed | 0 | 730-block cliff, 0% at TGE |
| Presale | 0.5B | 25% TGE unlock |
| TGE/IDO | 0.5B | 100% at TGE |
| Team | 0 | 1095-block cliff |
| Validator stakes | 5B | Active in consensus (not freely circulating) |

**Total at TGE:** ~8B (8%) — **TARGET, NOT VERIFIED**

**Status:** This calculation is a TARGET. Actual circulating supply depends on actual TGE execution, which has not occurred.

---

## 7. VALIDATORS

| Claim | Value | Status | Evidence |
|---|---|---|---|
| Validator count (dev chain) | 6 active (Alice-Ferdie) | **TESTNET** | Dev chain spec uses well-known test keys |
| Validator count (mainnet spec) | 21 (6 active + 15 standby) | **IMPLEMENTED / NOT DEPLOYED** | `mainnet_spec()` in `chain_spec.rs` |
| Active validator count | 6 | **TESTNET** | Dev chain running with 6 session keys |
| Consensus | BABE/GRANDPA + DPoS | **TESTNET** | Runtime config + pallet-dpos |
| Validator keys (mainnet) | Placeholder keys | **NOT VERIFIED** | `//MAINNET_VALIDATOR_1` through `//MAINNET_VALIDATOR_21` — MUST be replaced via air-gapped ceremony |
| Staking rewards | 342 VRDX/block | **IMPLEMENTED** | `BlockReward` constant in runtime |
| Target APR | 5-6.67% at 30-40% stake | **TARGET** | Not benchmarked on mainnet |
| Slashing | Implemented | **IMPLEMENTED** | pallet-dpos slashing logic |
| Green validators | 10 (on dev chain) | **TESTNET** | `eco_getGreenValidatorCount` RPC |

---

## 8. DEX STATUS

| Claim | Value | Status | Evidence |
|---|---|---|---|
| DEX exists in runtime | Yes — pallet-amm-dex | **TESTNET** | In `construct_runtime!`, active on dev chain |
| DEX pools (dev) | 6 pools | **TESTNET** | Dev chain spec seeds 6 pools |
| DEX pools (mainnet) | 0 | **IMPLEMENTED / NOT DEPLOYED** | Mainnet spec has empty pools (`initial_pools: vec![]`) |
| Swaps work | Yes, on dev chain | **TESTNET** | Verified via TX Relay API |
| Liquidity provision | Yes, on dev chain | **TESTNET** | add_liquidity/remove_liquidity extrinsics |
| Protocol fee | 0.05% to tokenomics | **IMPLEMENTED** | ProtocolFeeBps = 5 in pallet config |
| LP fee | 0.25% | **IMPLEMENTED** | Fee config in pallet-amm-dex |
| TVL displayed | $2.94M (dev) | **TESTNET** | Live from on-chain reserves — NOT production value |
| Fabricated TVL | None | **VERIFIED** | Previous hardcoded $32.4M was fixed to live data |

---

## 9. SMART CONTRACTS

| Claim | Value | Status | Evidence |
|---|---|---|---|
| Contracts pallet enabled | Yes — pallet-contracts | **TESTNET** | In `construct_runtime!` |
| Users can upload Wasm | Yes | **TESTNET** | `contracts::upload_code` extrinsic |
| Users can instantiate | Yes | **TESTNET** | `contracts::instantiate` extrinsic |
| Gas works | Yes | **TESTNET** | Runtime config with gas metering |
| Storage deposits work | Yes | **TESTNET** | StorageBaseDeposit + StorageDepositPerByte configured |
| Explorer indexes contracts | No | **NOT VERIFIED** | No contract indexing in explorer UI |
| Wallet supports deployment | Partial | **NOT VERIFIED** | Web wallet has no contract deployment UI |
| Security tests complete | No | **NOT VERIFIED** | No smart contract security tests |
| End-to-end verified | No | **NOT VERIFIED** | Full lifecycle not demonstrated |

---

## 10. IBC (Inter-Blockchain Communication)

| Claim | Value | Status | Evidence |
|---|---|---|---|
| IBC pallet exists | Yes — pallet-ibc | **IMPLEMENTED** | In `construct_runtime!`, 10 extrinsics |
| IBC tests | 50 tests | **IMPLEMENTED** | 50 tests in `pallets/ibc/src/tests.rs` |
| IBC deployed on mainnet | No | **NOT VERIFIED** | No mainnet deployment |
| IBC live on devnet | Yes (pallet enabled) | **TESTNET** | Pallet is in runtime, but no counterparty chain connected |
| Cross-chain transfers | Implemented, not deployed | **IMPLEMENTED / NOT DEPLOYED** | `transfer()` extrinsic exists, no live cross-chain traffic |

---

## 11. SECURITY — AUDIT STATUS

| Claim | Value | Status | Evidence |
|---|---|---|---|
| External security audit | None | **NOT VERIFIED** | No third-party audit report exists |
| Internal security audit | Partial | **IMPLEMENTED** | `docs/AUDIT_REPORT.md`, `docs/security-audit-phase2.md` — these are internal automated scans, NOT independent audits |
| Automated scanning | Yes | **IMPLEMENTED** | Security scanning scripts, code review |
| Code review by Claude/Kimi | Yes | **IMPLEMENTED** | Dual AI auditor system — NOT an independent audit |
| "Audited" claim | FALSE | **NOT VERIFIED** | No independent audit has been performed |
| "Fully audited" claim | FALSE | **NOT VERIFIED** | No independent audit has been performed |
| "100% secure" claim | FALSE | **NOT VERIFIED** | Impossible to verify; no system is "100% secure" |
| Security score | 100/100 (server config) | **IMPLEMENTED** | Server security hardening score — this is server config quality, NOT code security audit |
| Slashing logic | Implemented | **IMPLEMENTED** | pallet-dpos slashing |
| Overflow protection | Implemented | **IMPLEMENTED** | checked_mul/checked_add across pallets |
| Bounded inputs | Implemented | **IMPLEMENTED** | Vec<u8> length checks on extrinsic params |

**REQUIRED STATEMENT:**
> VERDIS CHAIN HAS NOT BEEN INDEPENDENTLY AUDITED.
> Internal security reviews have been performed using automated tools and AI-assisted code review.
> An external security audit is PLANNED but has not been conducted.
> No security claim should be presented as verified without an independent audit report.

---

## 12. ENVIRONMENTAL / CARBON CLAIMS

| Claim | Value | Status | Evidence |
|---|---|---|---|
| "Carbon Negative" | Not verified | **NOT VERIFIED** | No independent measurement or certification |
| "Green Blockchain" | Design objective | **TARGET** | DPoS is energy-efficient by design, but "green" is not independently verified |
| "99.9% less energy" | Not verified | **NOT VERIFIED** | No benchmark or measurement against any baseline |
| Carbon credit tracking | Implemented in pallet-eco | **IMPLEMENTED** | pallet-eco with carbon credits, reforest projects, green scoring |
| Carbon credits on dev chain | 6 credits (test data) | **TESTNET** | Dev chain has test eco data |
| Reforestation logging | Implemented | **IMPLEMENTED** | pallet-eco reforest_projects storage |
| Green validator scoring | Implemented | **IMPLEMENTED** | pallet-eco green score system |
| Independent verification | None | **NOT VERIFIED** | No third-party environmental audit |

**REQUIRED STATEMENT:**
> VERDIS CHAIN IS DESIGNED TO BE ENERGY-EFFICIENT THROUGH DPoS CONSENSUS.
> CARBON CREDIT TRACKING IS IMPLEMENTED BUT NOT INDEPENDENTLY VERIFIED.
> "CARBON NEGATIVE" AND "GREEN BLOCKCHAIN" ARE DESIGN OBJECTIVES, NOT CERTIFIED FACTS.
> ENVIRONMENTAL CLAIMS HAVE NOT BEEN INDEPENDENTLY VERIFIED.

---

## 13. AI / EVOLVIXOS CLAIMS

| Claim | Value | Status | Evidence |
|---|---|---|---|
| "AI audits every contract" | Not verified | **NOT VERIFIED** | No AI system performs automated contract auditing |
| EvolvixOS platform | Planned | **PLANNED** | EvolvixOS is a separate project; no live AI analysis system exists |
| AI-assisted analysis | Not implemented | **NOT VERIFIED** | No AI analysis of smart contracts exists in the codebase |
| AI security checks | Not implemented | **NOT VERIFIED** | No AI-based security checking system |

**REQUIRED STATEMENT:**
> AI-ASSISTED CONTRACT ANALYSIS IS PLANNED FOR THE FUTURE.
> NO AI SYSTEM CURRENTLY AUDITS, VERIFIES, OR SECURES SMART CONTRACTS ON VERDIS CHAIN.
> ALL SECURITY REVIEW IS PERFORMED BY HUMAN DEVELOPERS AND AI CODING ASSISTANTS DURING DEVELOPMENT, NOT AS AN ON-CHAIN FEATURE.

---

## 14. REFERRAL PROGRAM

| Claim | Value | Status | Evidence |
|---|---|---|---|
| Referral program exists | Yes (web page) | **PLANNED** | `/referral/` page exists on website |
| Tier 1 (direct) | 10% commission | **PLANNED** | Displayed on referral page |
| Tier 2 (indirect) | 5% commission | **PLANNED** | Displayed on referral page |
| Tier 3 (deep) | 2.5% commission | **PLANNED** | Displayed on referral page |
| Max total commission | 17.5% | **PLANNED** | Sum of all tiers |
| Paid in | VRDX (implied) | **NOT VERIFIED** | Not specified whether VRDX or fiat |
| Source of funds | Not specified | **NOT VERIFIED** | Not specified whether from sale proceeds, treasury, or ecosystem allocation |
| KYC/AML | Not specified | **NOT VERIFIED** | No KYC/AML policy documented for referral program |
| Legal review | Not performed | **NOT VERIFIED** | No legal review of referral structure |
| Geographic restrictions | Not specified | **NOT VERIFIED** | No geo-blocking or eligibility checks documented |
| Anti-abuse | Not specified | **NOT VERIFIED** | No anti-abuse controls documented |

### RISK ASSESSMENT

The 3-tier referral structure (10%/5%/2.5%) may be classified as a multi-level marketing (MLM) scheme in some jurisdictions. This creates:
- **Legal risk:** May require regulatory compliance in EU (MiCA), US (SEC), and other jurisdictions
- **Reputational risk:** MLM-style referral programs are viewed negatively by many investors
- **Regulatory risk:** May affect token classification (security vs. utility)

**REQUIRED ACTION:** The referral program must be reviewed by qualified legal counsel before activation. Until reviewed, it should be marked as "PLANNED — PENDING LEGAL REVIEW."

---

## 15. LEGAL ENTITY

| Claim | Value | Status | Evidence |
|---|---|---|---|
| Legal entity name | Not publicly documented | **NOT VERIFIED** | No legal entity is identified on any public page |
| Registration number | Not available | **NOT VERIFIED** | |
| Jurisdiction | Not documented | **NOT VERIFIED** | |
| Registered address | Not available | **NOT VERIFIED** | |
| Official domain | verdischain.com | **LIVE** | Domain registered and active |
| Relationship with Protremix | Not documented | **NOT VERIFIED** | Rojs Gordons is Founder & CEO of both Verdis Chain and Protremix, but the legal relationship is not publicly documented |
| Token sale entity | Not specified | **NOT VERIFIED** | |
| Treasury owner | PalletId (code) | **IMPLEMENTED** | Team multisig uses `PalletId(*b"verdistm")` — not a real multisig |
| MiCA compliance | Not verified | **NOT VERIFIED** | No MiCA compliance review has been performed |

**REQUIRED STATEMENT:**
> THE LEGAL ENTITY RESPONSIBLE FOR VERDIS CHAIN IS NOT PUBLICLY DOCUMENTED.
> THE RELATIONSHIP BETWEEN VERDIS CHAIN AND PROTREMIX IS NOT PUBLICLY DOCUMENTED.
> NO REGULATORY COMPLIANCE (INCLUDING MiCA) HAS BEEN VERIFIED.
> LEGAL STATUS: NOT YET CONFIRMED.

---

## 16. TEAM

| Claim | Value | Status | Evidence |
|---|---|---|---|
| Team page | Not verified | **NOT VERIFIED** | Team information on website has not been independently verified |
| Rojs Gordons | Founder & CEO | **CONFIRMED** | User identity confirmed via USER.md |
| Other team members | Not verified | **NOT VERIFIED** | No independent verification of team credentials |
| Advisers | Not verified | **NOT VERIFIED** | No adviser agreements publicly documented |
| Auditors | None engaged | **NOT VERIFIED** | No external auditor has been engaged |

---

## 17. CODE / GITHUB TRANSPARENCY

| Claim | Value | Status | Evidence |
|---|---|---|---|
| Repository | github.com/Protremix/Verdischain- | **LIVE** | GitHub repository exists |
| Latest commit | d0718deb | **LIVE** | Git log verified 2026-08-14 |
| Test count | 689 tests | **LIVE** | `grep -rc '#[test]'` across pallets |
| Test status | Not CI-verified | **NOT VERIFIED** | No CI/CD pipeline; tests not run on every commit |
| Runtime version | verdis-chain spec v14 | **LIVE** | `state_getRuntimeVersion` RPC |
| Pallet count | 42 pallets in construct_runtime | **LIVE** | Code audit |
| WASM build | Works with --no-default-features | **IMPLEMENTED** | Binary ~1.2MB |
| Known limitations | 0 peers, dev chain only, no mainnet, no external audit | **VERIFIED** | This document |
| Benchmark status | Not performed | **NOT VERIFIED** | No performance benchmarks |
| try-runtime status | Not tested | **NOT VERIFIED** | No try-runtime tests |

---

## 18. WEBSITE PAGES — CURRENT STATUS

| Page | URL | HTTP | Status |
|---|---|---|---|
| Homepage | / | 200 | LIVE (testnet) |
| Explorer | /explorer/ | 200 | LIVE (testnet) |
| DEX | /dex/ | 200 | LIVE (testnet) |
| Whitepaper | /whitepaper/ | 200 | LIVE |
| Wallet | /wallet/ | 200 | LIVE |
| Sale | /sale/ | 200 | LIVE (contains unverified claims) |
| Tokenomics | /tokenomics/ | 200 | LIVE |
| Faucet | /faucet/ | 200 | LIVE (testnet) |
| Validators | /validators/ | 200 | LIVE (testnet) |
| Eco | /eco/ | 200 | LIVE (testnet) |
| Docs | /docs/ | 200 | LIVE |
| Analytics | /analytics/ | 200 | LIVE (testnet) |
| Monitoring | /monitoring/ | 200 | LIVE (testnet) |
| Transactions | /transactions/ | 200 | LIVE (testnet) |
| Governance | /governance/ | 200 | LIVE (testnet) |
| Referral | /referral/ | 200 | LIVE (pending legal review) |

### Security Headers

| Header | Status |
|---|---|
| Content-Security-Policy | ACTIVE |
| Strict-Transport-Security | ACTIVE |
| X-Frame-Options (DENY) | ACTIVE |
| X-Content-Type-Options (nosniff) | ACTIVE |
| Permissions-Policy | ACTIVE |
| Referrer-Policy | ACTIVE |

---

## 19. CLAIMS THAT MUST BE REMOVED OR CORRECTED

### P0 — Must Fix Immediately

1. **"Total Raised: $18M"** on sale page → Replace with "Total Verified Received: $0 / Target: $18M"
2. **"Live" / "LIVE"** network status on all pages → Must state "TESTNET/DEVNET — NOT MAINNET"
3. **"Mainnet"** references implying it's live → Must state "MAINNET PLANNED — NOT LIVE"
4. **"Production" / "PRODUCTION"** on multiple pages → Must state "DEVELOPMENT/TESTNET"
5. **"Carbon Negative"** on multiple pages → Must state "DESIGNED TO BE CARBON-EFFICIENT — NOT INDEPENDENTLY VERIFIED"
6. **"Green Blockchain"** → Must state "DESIGNED FOR ENERGY EFFICIENCY — NOT CERTIFIED"
7. **"Compliant" / "MiCA compliant"** → Must state "LEGAL STATUS: NOT YET CONFIRMED"
8. **"audited" / "AI audit"** on whitepaper → Must state "INTERNAL REVIEW ONLY — NO INDEPENDENT AUDIT"
9. **"99.9% less energy"** (if present) → Must state "TARGET — NOT MEASURED"
10. **"guaranteed"** (if present) → Must remove or qualify as "TARGET — NOT GUARANTEED"

### P1 — Must Fix Before Investor-Facing Materials

1. Treasury allocation discrepancy (20B in code vs 15B in spec) — requires Rojs confirmation
2. Referral program must be reviewed by legal counsel
3. Legal entity must be publicly documented
4. Team credentials must be independently verified
5. TGE price must be clearly marked as TARGET, not guaranteed
6. ROI/profit claims must be removed or qualified

---

## 20. CONSISTENCY CHECKLIST

The following values must be IDENTICAL across all public surfaces (website, whitepaper, sale page, GitHub README, explorer):

| Value | Source of Truth | Must Match On |
|---|---|---|
| Max supply | 100,000,000,000 VRDX | All pages |
| Token symbol | VRDX | All pages |
| Decimals | 9 | All pages |
| Network status | TESTNET/DEVNET | All pages |
| Mainnet status | PLANNED — NOT LIVE | All pages |
| Total raised | $0 (verified) / $18M (target) | Sale page, whitepaper |
| TGE price | $0.005 (TARGET) | Sale page, tokenomics |
| Treasury allocation | PENDING RESOLUTION | Tokenomics, whitepaper |
| Validators (mainnet) | 21 (planned) | Validators page, whitepaper |
| Audit status | NOT INDEPENDENTLY AUDITED | All pages |
| Carbon status | DESIGNED FOR EFFICIENCY — NOT VERIFIED | All pages |
| AI claims | PLANNED — NOT IMPLEMENTED | Whitepaper, docs |

---

## DOCUMENT CONTROL

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-08-14 | EvolvixOS Agent | Initial creation — comprehensive audit of all public claims |

**This document must be updated whenever:**
- A public claim changes
- New evidence becomes available
- Mainnet launches (requires block hash evidence)
- An independent audit is completed
- A funding round actually closes
- Legal review is completed
- Team members are verified

**Next review date:** When any P0 item is resolved or within 7 days, whichever is first.
