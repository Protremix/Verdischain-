# Verdis Chain — Knowledge Base

**Project:** Verdis Chain (Evolvix Ecosystem)
**Document Owner:** Arlo (Chief Engineer & Technical Security Authority)
**Last Updated:** August 21, 2026, 22:28 Madrid
**Classification:** Internal Knowledge Base
**Git HEAD:** da29b831

---

## 1. Network Status

| Metric | Value | Last Verified |
|--------|-------|---------------|
| Network Type | TESTNET | Aug 21, 2026 |
| Block Height | #37,424 | Aug 21, 2026 |
| Active Validators | 21/21 | Aug 21, 2026 |
| Peers | 5 | Aug 21, 2026 |
| Nodes | 6 | Aug 21, 2026 |
| Consensus | BABE + GRANDPA (DPoS) | Aug 21, 2026 |
| Runtime Version | v2.0.0 | Aug 21, 2026 |
| Pallet Sudo | REMOVED | Aug 14, 2026 |
| SS58 Prefix | 909 | Aug 21, 2026 |
| Web Status | 7/7 pages HTTP 200 | Aug 21, 2026 |
| Services | 17 running, 0 failed | Aug 21, 2026 |
| RPC Latency | <1ms | Aug 21, 2026 |
| Security Score | 100/100 (internal) | Aug 21, 2026 |
| Server IP | 91.98.160.145 (Hetzner) | Aug 21, 2026 |
| Domain | verdischain.com | Aug 21, 2026 |

## 2. Token (VRDX)

| Parameter | Value |
|-----------|-------|
| Ticker | VRDX (NOT VERDIS) |
| Total Supply | 100,000,000,000 (100B) VRDX |
| Decimals | 9 |
| Hard Cap Enforcement | MaxSupplyCurrency wrapper (atomic checked arithmetic) |
| Currency Interfaces Replaced | 17 (all runtime Currency bindings) |
| Circulating at TGE | 8,000,000,000 (8B) VRDX (planned) |

### Token Allocation (100B Total)

| Category | Amount | Percentage |
|----------|--------|-----------|
| Ecosystem & Developer Grants | 25,000,000,000 | 25% |
| PoS Staking Rewards | 20,000,000,000 | 20% |
| Treasury | 20,000,000,000 | 20% |
| Development | 10,000,000,000 | 10% |
| Liquidity | 10,000,000,000 | 10% |
| Community | 5,000,000,000 | 5% |
| Seed / Strategic | 3,000,000,000 | 3% |
| Public Presale | 2,000,000,000 | 2% |
| Team & Advisors | 5,000,000,000 | 5% |
| **Total** | **100,000,000,000** | **100%** |

## 3. Pallets (16 Custom)

| # | Pallet | Purpose | Security Status |
|---|--------|---------|-----------------|
| 1 | dpos | DPoS consensus — validator selection, delegation, slashing, epoch rotation | Audited (Luna) |
| 2 | amm-dex | AMM DEX — liquidity pools, swaps, LP tokens, protocol fees | Audited (Luna) |
| 3 | eco | Eco-tracking — green scoring, carbon credits, reforestation | Audited (Luna) |
| 4 | fungible-tokens | Custom token issuance, mint, burn, transfer, metadata | Audited |
| 5 | tokenomics | Supply enforcement, allocation tracking, reward distribution | Audited |
| 6 | vesting | Token vesting — cliff, linear, multi-beneficiary, timestamp-based | Audited (Luna) |
| 7 | presale | Token presale — contribution, hard cap, whitelist, refund, claim | Audited (Luna, C1 fix) |
| 8 | governance | Referenda, council, treasury proposals, voting | Audited |
| 9 | ibc | Inter-Blockchain Communication — packet send/recv, channels | Audited (Luna) |
| 10 | circuit-breaker | Emergency pause — pallet freeze, global halt, auto triggers | Audited (Luna) |
| 11 | address-lookup-tables | Address optimization for tx size reduction | Infrastructure |
| 12 | gulf-stream | Transaction mempool management and propagation | Infrastructure |
| 13 | poh | Proof of History — transaction ordering and timestamps | Infrastructure |
| 14 | sealevel | Parallel transaction execution runtime | Infrastructure |
| 15 | storage | On-chain storage management and rent | Infrastructure |
| 16 | turbine | Block propagation and network sharding | Infrastructure |
| 17 | zk-compression | ZK proof compression for state verification | Infrastructure |

## 4. Luna Adversarial Audit (Round 5 — Complete)

| Metric | Value |
|--------|-------|
| Findings Identified | 33 |
| Findings Resolved | 33/33 (100%) |
| Critical (P0) | 1 — Presale C1 double-spend vulnerability |
| High (P1) | 5 — MaxSupplyCurrency bypass, DPoS auth, IBC auth, Vesting cliff |
| Medium (P2) | 14 |
| Low (P3) | 13 |
| Adversarial Tests Added | 60 (presale/vesting/escrow lifecycle) |
| Total Tests | 621 (0 failures) |
| Commit | dee18881 (C1 fix), 97126610 (33 findings fix) |

### Critical Fixes Applied

1. **C1: Presale double-spend** — simultaneous contributions could be counted twice. Fixed with atomic storage updates + 60 adversarial tests.
2. **H1-H2: MaxSupplyCurrency bypass** — AMM read-only routes bypassed supply cap. Fixed by routing all transfers through wrapper.
3. **H3-H4: DPoS commission/slashing** — missing origin checks. Fixed with ensure_signed/ensure_root.
4. **H5: Vesting cliff** — off-by-one in timestamp comparison. Fixed.
5. **IBC C1-C3: Packet authentication** — missing root-origin verification. Fixed with ensure_root checks.
6. **Slash destination** — slash funds now route to governance treasury instead of DPoS reward pool.

## 5. Ceremony Script Review (Aug 21, 2026)

| Finding | Severity | Status |
|---------|----------|--------|
| SS58 prefix mismatch (42→909) | P0 | FIXED |
| Missing ImOnline key generation | P1 | FIXED |
| No duplicate key check | P1 | FIXED |
| Multisig address not computed | P1 | FIXED |
| Outdated test count (446→621) | P2 | FIXED |
| No PGP signing of output | P2 | FIXED |
| Insufficient air-gap check | P2 | FIXED |
| Missing authority discovery keys | P3 | FIXED |
| Low entropy check | P3 | FIXED |
| Script in non-canonical path | P3 | FIXED (moved to /scripts/) |

Updated ceremony script (v2, 409 lines) saved to `/scripts/air-gapped-key-ceremony.sh`.

## 6. Mainnet Status — 5-Gate Requirement

**Current Verdict:** NO-GO (1/5 gates passing)

| Gate | Description | Status | Lead Time | Cost |
|------|-------------|--------|-----------|------|
| 1. Arlo (Internal) | Code audit, security, tests | **PASS** ✅ | Complete | €0 |
| 2. External Auditor | Halborn / Sigma Prime | NOT STARTED | 8-14 weeks | $50K-$150K |
| 3. Infrastructure | 3-location, 21 validators | NOT STARTED | 3-4 weeks | €247/mo |
| 4. Key Ceremony | Air-gapped key generation | NOT STARTED | 2-3 weeks | <€1K |
| 5. Legal/Compliance | UAE/VARA entity | NOT STARTED | 4-6 months | $90K-$245K Y1 |

### Critical Path
Gate 5 (Legal, 4-6 months) → Gate 2 (Audit, 8-14 weeks) → Gate 3 (Infra, 3-4 weeks) → Gate 4 (Ceremony, 2-3 weeks)

Gates 2, 3, and 5 can start immediately in parallel. Gate 4 depends on Gate 3.

### Infrastructure Plan
| Server | Location | Specs | Validators | Cost |
|--------|----------|-------|-----------|------|
| Hostkey NL | Netherlands | 10c/64GB/1.92TB | 7 | €80/mo |
| Hostkey USA | USA | 6c/64GB/1.92TB | 7 | €70/mo |
| Hetzner FI | Helsinki | 8c/64GB/1TB | 7 | €97/mo |
| Current (boot) | Hetzner | 8c/30GB/225GB | 0 (boot+explorer) | existing |
| **Total** | **3 locations** | | **21** | **€247/mo** |

## 7. Mobile Deployment Status

| Platform | Status | Version | Notes |
|----------|--------|---------|-------|
| Android | ✅ Uploaded to Google Play internal testing | 2.1.11 (code 36) | Track: internal testing |
| iOS | ⏳ Build verification in progress | 2.1.11+52 | ExportOptions.plist configured, Team ID 84399KX4RA |
| Web Wallet | ✅ Operational | — | verdischain.com/wallet/ |

## 8. Testnet Stability Test

| Metric | Value |
|--------|-------|
| Start Date | August 18, 2026 |
| End Date | September 1, 2026 |
| Duration | 14 days |
| Daily Health Check | 9:00 AM Madrid (14 runs) |
| TX Generator | Every 4 hours (84 runs) |
| Day 1 Baseline | Block #668, 21 validators, 5 peers, 6 pools |
| Current Day | Day 4 (Aug 21) |
| Status | Running — stable |

## 9. Engineering Constitution

- **Version:** 1.0 (Adopted Aug 21, 2026, commit 7f841578)
- **Articles:** 22
- **Chief Engineer:** Arlo
- **Key Rules:**
  - P0 = immediate Mainnet block
  - P1 = Mainnet block until resolved
  - Every vulnerability gets regression test
  - No silent changes
  - Separation of duties (no unilateral key custody)
  - Mainnet GO requires all 5 gates PASS
  - 10 mandatory documents

### 10 Mandatory Documents (Article 18)
1. SECURITY_LOG ✅
2. SECURITY_INCIDENT_RESPONSE ✅
3. MAINNET_READINESS ✅
4. RELEASE_CANDIDATE ✅
5. ARCHITECTURE ✅
6. THREAT_MODEL ✅
7. KEY_MANAGEMENT ✅
8. TREASURY_SECURITY ✅
9. DEPENDENCY_SECURITY ✅
10. AUDIT_REMEDIATION ✅

All 10 committed (9418943e).

## 10. Prepared Documents (Aug 21, 2026)

| Document | Path | Status |
|----------|------|--------|
| Halborn scoping email (draft) | /docs/audit/halborn_scoping_email_draft.md | DRAFT — not sent |
| DMCC application template | /docs/legal/dmcc_application_template.md | TEMPLATE — needs counsel |
| Ceremony script review | /docs/CEREMONY_SCRIPT_REVIEW.md | Complete |
| Updated ceremony script | /scripts/air-gapped-key-ceremony.sh | v2, 409 lines |
| Server deployment script | /docs/infrastructure/deploy_3_servers.sh | Ready (IPs TBD) |
| Knowledge base (this file) | /docs/knowledge-base/project1-verdis-chain.md | Updated |

## 11. Key Decisions (Active)

1. Token ticker remains VRDX (not VERDIS) — Rojs confirmed Aug 8
2. Treasury allocation: 20B per code (not 15B from spec) — corrected Aug 14
3. UAE/VARA jurisdiction approved — Rojs confirmed Aug 14 (ARCH-002)
4. 3-entity structure: Protremix S.L. (dev) + Verdis Chain Foundation (UAE) + Token Offering SPV
5. 3-of-5 multisig for Treasury (no single signer control)
6. 21 active validators (not 6 active + 15 standby)
7. MaxSupplyCurrency wrapper enforces 100B hard cap across all 17 currency interfaces
8. Mainnet verdict: NO-GO until all 5 gates pass

---

*This knowledge base is the single source of truth for Verdis Chain project state. Updated by Arlo (Chief Engineer). All metrics verified against live infrastructure.*
