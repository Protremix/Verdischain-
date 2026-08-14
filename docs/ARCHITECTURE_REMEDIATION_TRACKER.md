# Verdis Chain — Architecture & Decentralization Remediation Tracker

**Source:** VerdisChain_Target_Architecture_and_Decentralization_TZ_2026-08-14.xlsx
**Created:** 2026-08-14
**Total Tasks:** 75 (13 P0, 44 P1, 18 P2)
**Mainnet Gates:** 22 (all OPEN)

---

## Summary

| Priority | Total | Done | Partial | Open |
|----------|-------|------|---------|------|
| P0       | 13    | 6    | 1       | 6    |
| P1       | 44    | 0    | 6       | 38   |
| P2       | 18    | 0    | 0       | 18   |
| **Total** | **75** | **6** | **7** | **62** |

---

## P0 Tasks (13)

### DONE (6)

| ID | Area | Description | Evidence |
|----|------|-------------|----------|
| ARCH-006 | Licensing | Protocol license resolved — MIT references removed, Proprietary across all pages | commit bbdbe97c |
| ARCH-009 | Transparency | Canonical facts file created | docs/CANONICAL_FACTS.md |
| ARCH-011 | Website | Misleading claims removed — 8M raised→target, Carbon Negative→Energy-Efficient, audit claims corrected | commit bbdbe97c, 35 pages |
| ARCH-012 | Website | Global environment status — VERDIS_NETWORK config + TESTNET banner on all pages | verdis.js, all pages verified |
| ARCH-047 | Marketing | Unverified partnership claims removed (Verra/WWF/UN) | commit bbdbe97c |
| ARCH-065 | SEO/UX | Environment banner from one config source | VERDIS_NETWORK in verdis.js |

### PARTIAL (1)

| ID | Area | Description | What's Done | What's Left |
|----|------|-------------|-------------|-------------|
| ARCH-025 | Repositories | Remove conversation/development artifacts from public repo | .github/workflows/repo-hygiene.yml created | Full repo audit needed |

### OPEN — Needs Legal/Rojs (6)

| ID | Area | Description | Owner | Blocker |
|----|------|-------------|-------|---------|
| ARCH-001 | Legal/Corporate | Separate Protocol, Foundation, Protremix entities | Founder + counsel | Legal memo required |
| ARCH-002 | Legal/Corporate | Dubai/UAE entity + VARA regulatory structure | Legal | Signed UAE legal memo |
| ARCH-003 | Legal/EU | VRDX MiCA classification + territorial scope opinion | EU counsel | Signed legal opinion |
| ARCH-004 | Legal/Global | Country-by-country allow/restrict/block framework | Legal + Compliance | Approved matrix |
| ARCH-005 | Protocol | Protremix Independence Test — protocol must not require Protremix | Architecture lead | Dependency map |
| ARCH-007 | Token Sale | Separate token offering entity with KYC/AML/geo controls | Legal + Product | Approved sale architecture |
| ARCH-008 | Security | Independent third-party security audit | Security lead | Published audit report |
| ARCH-010 | Tokenomics | Freeze canonical allocations — genesis as source of truth | Tokenomics lead | Hash + consistency report |
| ARCH-075 | Mainnet | Mainnet launch gate — do not launch until all gates pass | Executive | All gates closed |

---

## P1 Tasks — Technical (Can Action Now)

### PARTIAL (6)

| ID | Area | What's Done | What's Left |
|----|------|-------------|-------------|
| ARCH-027 | CI/CD | fmt/check/test/clippy/release/WASM pipelines exist | Formalize release gates, block deploy on failure |
| ARCH-030 | Consensus | Manual genesis consistency check | Automated CI check for authority-set mismatch |
| ARCH-031 | Consensus | 76 DPoS slashing tests pass | Adversarial integration tests |
| ARCH-040 | Tokenomics | 8 economic invariant tests | Property-based supply invariant tests |
| ARCH-041 | Tokenomics | 7 vesting edge-case tests | Full edge-case coverage |
| ARCH-046 | Marketing | CANONICAL_FACTS.md created | Formal claims register with evidence links |

### OPEN — Technical Tasks (28)

| ID | Area | Description | Status |
|----|------|-------------|--------|
| ARCH-018 | Validators | Validator roadmap 6→21→50+→100+ | Needs published roadmap doc |
| ARCH-019 | Validators | Nakamoto coefficient + top-5/top-10 stake tracking | Needs dashboard |
| ARCH-020 | Validators | Protremix stake policy ≤33% | Needs approved policy doc |
| ARCH-021 | Validators | Permissionless validator onboarding | Needs docs + sunset whitelist plan |
| ARCH-022 | Validators | Geographic diversity tracking | Needs reporting |
| ARCH-023 | Validators | ASN/cloud diversity tracking | Needs reporting |
| ARCH-026 | Repositories | Split into clean monorepo modules or separate repos | Architecture decision needed |
| ARCH-028 | Builds | Reproducible build evidence | Needs build script + verification |
| ARCH-029 | Runtime | Runtime upgrade lifecycle formalization | Needs try-runtime + migration docs |
| ARCH-032 | Governance | Separate protocol governance from corporate | Needs governance docs |
| ARCH-033 | Governance | Bound emergency authority | Needs emergency controls docs |
| ARCH-034 | DEX | DEX as ecosystem app, not protocol control | Needs separation docs |
| ARCH-035 | DEX | Independent DEX security/economic testing | Needs test suite |
| ARCH-036 | Wallet | Wallet as ecosystem product | Needs separation docs |
| ARCH-037 | Wallet | Client-side key handling verification | Needs security review |
| ARCH-038 | Wallet | Hardware wallet integration roadmap | Post-mainnet |
| ARCH-039 | Crypto | TX Relay cryptographic threat model documentation | Needs threat model doc |
| ARCH-042 | Token Sale | KYC/AML implementation | Before sale (needs vendor) |
| ARCH-043 | Token Sale | Geo-blocking implementation | Before sale (needs legal matrix) |
| ARCH-044 | Token Sale | Eligibility engine | Before sale (needs legal policy) |
| ARCH-045 | Token Sale | Policy versioning | Before sale |
| ARCH-048 | Docs | Sanitized public evidence package | Needs cleanup |
| ARCH-049 | Docs | Team transparency — roles + relevant experience | Team page exists, needs credentials |
| ARCH-050 | Privacy | Align privacy policy with final legal entity | Needs legal entity first |
| ARCH-051 | Infra | Verify public attack surface (runtime, not source) | Needs live pentest |
| ARCH-052 | Infra | Docker hardening runtime evidence | Needs runtime verification |
| ARCH-053 | Security | Incident response process | Needs IR plan doc |
| ARCH-054 | Security | Bug bounty program | Needs public disclosure program |
| ARCH-055 | Observability | Independent monitoring stack | Needs setup |
| ARCH-056 | DR | Disaster recovery testing | Needs recovery exercise |

---

## P2 Tasks (18) — Post-Mainnet Roadmap

ARCH-057 through ARCH-074 — Ecosystem, transparency dashboards, accessibility, performance, SEO, governance social layer, protocol specification, dependency inventory, release signing.

---

## Mainnet Gates (22 — ALL OPEN)

### Legal (3)
1. Dubai/UAE structure complete → Signed UAE/VARA legal memo
2. EU/MiCA classification complete → Signed VRDX classification opinion
3. Global jurisdiction matrix approved → Versioned allow/restrict/block policy

### Security (3)
4. Independent audit complete → Third-party report; critical findings = 0
5. Pentest complete → External infrastructure/web/API report
6. Wallet review complete → Wallet security audit

### Technical (6)
7. 21+ independent testnet validators → Validator evidence + failure tests
8. Genesis consistency verified → Automated CI + signed genesis
9. Runtime upgrades tested → try-runtime + migration evidence
10. Consensus/slashing tested → Adversarial integration tests
11. DEX tested → Security/economic audit + regression suite
12. Vesting tested → Edge-case test report
13. Supply invariants tested → Property-test report

### Decentralization (3)
14. Company/Foundation stake below policy limit → On-chain evidence
15. Validator concentration acceptable → Nakamoto/top-stake report
16. Provider/geographic concentration acceptable → ASN/cloud/geo report

### Transparency (3)
17. Canonical tokenomics published → Code/genesis/docs consistency report
18. Treasury transparency live → Addresses, balances, signers, transactions
19. Status/evidence page live → Public status page

### Operations (2)
20. Incident response exercised → Tabletop/technical recovery exercise
21. Disaster recovery exercised → Restore/recovery report

### Launch (1)
22. Executive sign-off → Legal + Security + Tech + Operations approvals

---

## Target Structure (8 Layers)

| Layer | Target | Must NOT Control |
|-------|--------|------------------|
| Verdis Protocol | Independent public L1 | Marketing, corporate sales, commercial SaaS |
| Verdis Foundation | Independent public-goods org | Unilateral protocol control or arbitrary treasury spending |
| Protremix | Commercial development company | Permanent majority validator/stake control |
| Ecosystem DEXs | Independent applications | Protocol governance |
| Wallets | Ecosystem products | Protocol control |
| Validators | Independent operators | Dependence on Protremix approval |
| Treasury | Transparent controlled funds | Unilateral movement by one party |
| Token Offering Entity | Legally responsible offering layer | Direct control over protocol consensus |

---

## Decentralization KPIs (10)

1. Independent validators — Increase
2. Protremix + Foundation stake — Decrease (≤33%)
3. Nakamoto coefficient — Increase
4. Top-10 stake concentration — Decrease
5. Geographic concentration — Decrease
6. ASN/cloud diversity — Increase
7. Validator uptime — Maintain >99%
8. Governance participation — Increase
9. Client diversity — Increase (post-mainnet)
10. RPC/infrastructure independence — Increase

---

## Next Actions (Technical — Can Do Now)

1. **ARCH-010**: Freeze canonical tokenomics — generate consistency report from genesis/runtime
2. **ARCH-027**: Formalize CI/CD release gates — block deploy on test/security failure
3. **ARCH-030**: Automated genesis consistency CI check
4. **ARCH-040**: Property-based supply invariant tests
5. **ARCH-041**: Comprehensive vesting edge-case tests
6. **ARCH-025**: Full repository audit — remove all conversation/workspace artifacts
7. **ARCH-046**: Formal claims register with evidence links
8. **ARCH-062**: Public status/evidence page
9. **ARCH-018**: Published validator roadmap document
10. **ARCH-039**: TX Relay cryptographic threat model doc
