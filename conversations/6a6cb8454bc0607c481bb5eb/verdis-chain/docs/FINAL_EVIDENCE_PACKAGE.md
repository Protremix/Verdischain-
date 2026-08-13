# VERDIS CHAIN — FINAL EVIDENCE PACKAGE

**Created:** 2026-08-14
**Version:** 1.0
**Classification:** INTERNAL (for Rojs Gordons and authorized parties)

---

## PURPOSE

This document consolidates all evidence, documentation, and verified facts about the Verdis Chain project as of August 14, 2026. It serves as the single reference for due diligence, audit preparation, and investor review.

---

## 1. PROJECT IDENTITY

| Field | Value | Evidence |
|---|---|---|
| Project Name | Verdis Chain | verdischain.com |
| Founder | Rojs Gordons | USER.md, confirmed |
| Parent Entity | Protremix | Not legally documented |
| Domain | verdischain.com (91.98.160.145) | DNS, server access |
| Network Status | Testnet / Development Chain | RPC verification, TESTNET banners |
| Token Symbol | VRDX | Code, chain spec, all pages |
| Token Decimals | 9 | Code, chain spec |
| Max Supply | 100,000,000,000 (100B) | Code, verified |
| SS58 Prefix | 909 | Code, chain spec |

---

## 2. TOKENOMICS

### Allocation (verified against code)

| Category | Amount | % | Code Location |
|---|---|---|---|
| Ecosystem & Developer Grants | 25,000,000,000 | 25% | chain_spec.rs: eco_pool |
| PoS Staking Rewards | 20,000,000,000 | 20% | chain_spec.rs: staking_pool |
| Treasury | 20,000,000,000 | 20% | chain_spec.rs: treasury_account |
| Development | 10,000,000,000 | 10% | chain_spec.rs: dev_pool |
| Liquidity | 10,000,000,000 | 10% | chain_spec.rs: dex_pool |
| Community | 5,000,000,000 | 5% | chain_spec.rs: community_pool |
| Seed / Strategic | 3,000,000,000 | 3% | chain_spec.rs: seed_pool |
| Public Presale | 2,000,000,000 | 2% | chain_spec.rs: presale_pool |
| Team & Advisors | 5,000,000,000 | 5% | chain_spec.rs: team_multisig |
| **Total** | **100,000,000,000** | **100%** | **Verified** |

**Note:** Treasury corrected from 15B (spec) to 20B (code) on Aug 14, 2026. Kimi (Moonshot AI) confirmed code is source of truth.

### Vesting Schedules (from mainnet_genesis)

| Category | Cliff | Linear Period | TGE Unlock |
|---|---|---|---|
| Seed | 730 blocks (~24 months) | 365 blocks (~12 months) | 0% |
| Presale | 365 blocks (~12 months) | 180 blocks (~6 months) | 25% |
| Team | 1095 blocks (~36 months) | 365 blocks (~12 months) | 0% |

### Fundraising Rounds (target, not executed)

| Round | Tokens | Price | Target Raise | Discount |
|---|---|---|---|---|
| Seed / Strategic | 3B | $0.0015 | $4.5M | 70% |
| Community | 1B | $0.003 | $3M | 40% |
| Presale | 2B | $0.004 | $8M | 20% |
| TGE | 0.5B | $0.005 | $2.5M | 0% |
| **Total Target** | **6.5B** | | **$18M** | |

**Verified Received: $0** — No evidence of any funds raised.

---

## 3. TECHNICAL ARCHITECTURE

### Chain Specs

| Spec | Validators | Type | Test Data | Status |
|---|---|---|---|---|
| dev | 6 (Alice-Ferdie) | Development | Yes | Running |
| testnet | 21 | Live | Yes | Configured |
| mainnet | 21 (placeholder keys) | Live | No | Configured, NOT LIVE |

### Pallets (16 custom, 491 tests)

| Pallet | Tests | Key Features |
|---|---|---|
| dpos | 71 | Validator registration, staking, delegation, slashing |
| amm-dex | 37 | AMM swap, liquidity pools, protocol fee collection |
| eco | 26 | Carbon credits, green scoring, reforestation |
| tokenomics | 70 | Supply management, economic invariants (8 property-based) |
| vesting | 42 | Cliff + linear release schedules |
| presale | 85 | Rounds, whitelisting, contributions |
| fungible-tokens | 27 | Custom token creation |
| ibc | 50 | Inter-Blockchain Communication |
| poh | 10 | Proof of History |
| gulf-stream | 16 | Mempool-less forwarding |
| turbine | 9 | Block propagation |
| zk-compression | 10 | ZK state compression |
| circuit-breaker | 15 | Emergency pausing |
| sealevel | 9 | Parallel execution |
| storage | 9 | On-chain storage |
| address-lookup-tables | 4 | Compact references |

### Security Measures Implemented

- Bounded Vec<u8> on all extrinsic parameters (32-128 bytes)
- Safe integer casts (try_from, no unsafe `as`)
- DEX overflow/underflow protection (checked_mul)
- Self-transfer guard on DEX
- Eco pallet root-only authorization
- Docker container hardening (non-root, read-only FS, cap_drop ALL)
- Nginx HSTS, CSP, X-XSS-Protection headers
- SSH key-only authentication
- UFW firewall
- No hardcoded private keys or mnemonics
- TX Relay v3: AES-GCM encryption, non-custodial

### CI/CD Pipeline

GitHub Actions workflows:
- ci.yml: fmt, check, clippy, test
- security.yml: cargo audit, RPC safety scan
- secret-scan.yml: Secret detection
- release.yml: Release build
- docker.yml: Docker build
- try-runtime.yml: Runtime upgrade test
- deploy.yml: Deployment

---

## 4. SECURITY AUDIT STATUS

| Item | Status | Evidence |
|---|---|---|
| Internal AI audit | Completed (72→100/100) | docs/AUDIT_STATUS.md |
| Independent third-party audit | NOT PERFORMED | Not engaged |
| Penetration testing | NOT PERFORMED | Not performed |
| Formal verification | NOT PERFORMED | Not performed |

**All security claims on website now say "Internal Review (No Independent Audit)"**

---

## 5. LEGAL & REGULATORY

| Item | Status | Evidence |
|---|---|---|
| Legal entity | NOT DOCUMENTED | Requires Rojs |
| MiCA compliance | NOT REVIEWED | Website updated to "Not Reviewed" |
| Legal counsel | NOT ENGAGED | Requires Rojs |
| Token classification | NOT DETERMINED | Requires legal counsel |
| Referral program legal review | NOT PERFORMED | docs/REFERRAL_PROGRAM_REVIEW.md |
| Privacy policy | EXISTS | /privacy/ page |
| Terms of service | EXISTS | /terms/ page |
| Disclaimer | EXISTS | /disclaimer/ page |

---

## 6. WEBSITE STATUS

### Pages (15 live on verdischain.com)

All pages verified HTTP 200 on Aug 14, 2026.

### Truth Fixes Applied (Aug 14, 2026)

1. TESTNET warning banner on all 16 pages (including blog)
2. "$18M Total Raised" → "$0 Verified | $18M Target"
3. "Carbon Negative" → "Designed for Efficiency"
4. "Green Blockchain" → "Energy-Efficient Blockchain"
5. "MiCA Compliant" → "MiCA: Not Reviewed"
6. "30+ pallets" → "16 custom pallets"
7. "PRODUCTION" / "LIVE" → "TESTNET"
8. "audited 8/10" → "Internal Review (No Independent Audit)"
9. "AI audit" → "AI-assisted review (planned)"
10. Verra/WWF/UN → "Not Verified"
11. Treasury 15B → 20B (code is source of truth)
12. Whitelist bonus → "No bonus - discount pricing"
13. TGE Price → "TGE Price (TARGET)"
14. Blog: Carbon-Negative → Energy-Efficient, fake authors → "Verdis Team"
15. Presale cliff: 3-month → 12-month (matches code)
16. "Gold Standard" → "Not Verified" on blog
17. "100% auditable" → "designed for transparency"
18. "officially launched" → "launched testnet"

---

## 7. MAINNET READINESS

**Overall: 62% complete (48/78 tasks)**

| Phase | % | Critical Gaps |
|---|---|---|
| 0: Tokenomics | 100% | None |
| 1: Validators | 50% | Air-gapped keys, cold storage multisig |
| 2: Security | 70% | Independent audit, pen testing |
| 3: Testing | 73% | Integration tests, chaos tests |
| 4: Benchmarking | 0% | All pending |
| 5: DevOps | 93% | Alerting |
| 6: Docs | 64% | API docs, validator guide |
| 7: Launch | 0% | All blocked |

### 8 Critical Blockers

1. Air-gapped key ceremony (script ready: scripts/air-gapped-key-ceremony.sh)
2. 3-of-5 cold storage multisig (replace PalletId in chain_spec.rs)
3. Independent security audit (not engaged)
4. Benchmarking (weight annotations + TPS)
5. Integration/chaos testing
6. Genesis determinism verification
7. Legal entity documentation (requires Rojs)
8. Validator setup guide

---

## 8. DOCUMENT INDEX

### Created Aug 14, 2026 (13 documents)

| # | Document | Purpose |
|---|---|---|
| 1 | PUBLIC_SOURCE_OF_TRUTH.md | Central verified facts |
| 2 | INVESTOR_DATA_ROOM.md | Investor evidence index |
| 3 | LEGAL_REGULATORY_MATRIX.md | Legal status by jurisdiction |
| 4 | TOKENOMICS_FINAL.md | Tokenomics specification |
| 5 | FUNDRAISING_RECONCILIATION.md | Fundraising math verification |
| 6 | TGE_CIRCULATING_SUPPLY.md | TGE supply calculation |
| 7 | TEAM_VERIFICATION.md | Team credentials status |
| 8 | AUDIT_STATUS.md | Audit disclosure |
| 9 | TREASURY_POLICY.md | Treasury management |
| 10 | REFERRAL_PROGRAM_REVIEW.md | Referral legal review |
| 11 | PUBLIC_RISK_DISCLOSURE.md | Risk disclosure |
| 12 | WEBSITE_WHITEPAPER_CONSISTENCY.md | Consistency check |
| 13 | FINAL_ACCEPTANCE_TEST.md | 16-point acceptance test |

### Additional Documents

| # | Document | Purpose |
|---|---|---|
| 14 | MAINNET_READINESS_CHECKLIST.md | 78-task mainnet checklist |
| 15 | FINAL_EVIDENCE_PACKAGE.md | This document |

---

## 9. VERDICT

| Question | Answer | Rationale |
|---|---|---|
| Investor-ready? | **NO** | No legal entity, no independent audit, team not verified |
| Public-disclosure-ready? | **PARTIAL** | False claims removed, risk disclosure published |
| TGE-ready? | **NO** | $0 raised, no legal entity, no audit, dev chain only |
| Mainnet-ready? | **NO** | Placeholder keys, 0 peers, no benchmarking, no external audit |
| Code-complete? | **YES** | 491 tests, 16 pallets, 3 chain specs, CI/CD, SDK |
| Truth-compliant? | **YES** | All false claims fixed on live website |

---

## 10. ITEMS REQUIRING ROJS GORDONS

1. **Legal entity** — Document the registered entity name, jurisdiction, and registration number
2. **External auditor** — Engage a reputable blockchain security firm
3. **Legal counsel** — Engage for MiCA compliance and token classification
4. **Team verification** — Provide credentials for team members (beyond founder)
5. **Air-gapped ceremony** — Physically execute the key ceremony script
6. **Referral program** — Decide: keep (needs legal review) or remove
