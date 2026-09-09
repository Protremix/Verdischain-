# KYC/AML Provider RFP — Verdis Chain

**Document ID:** COMPLIANCE-RFP-001
**Date:** 2026-08-14
**Status:** RFP issued (provider NOT selected)
**Approval Required:** Rojs Gordons + Compliance Officer

---

## 1. Project Overview

Verdis Chain is a Substrate-based Layer-1 blockchain with DPoS consensus, AMM DEX, staking, governance, and eco-friendly validator scoring. The native token is VRDX (100B supply, 9 decimals).

We are seeking a KYC/AML provider to support our planned token offering and ongoing platform compliance. The token sale is currently DISABLED pending legal counsel approval.

## 2. Scope

The selected provider will deliver:

- Identity verification (KYC) for individual users
- Business verification (KYB) for institutional users
- Sanctions screening (OFAC, EU, UN, UK)
- PEP screening (politically exposed persons)
- Adverse media screening
- Jurisdiction screening (geo-compliance)
- Transaction monitoring (for DEX and exchange operations)
- Wallet screening (blockchain address risk scoring)
- Audit logs (immutable, GDPR compliant)
- Case management (manual review queue)
- Data retention controls
- API integration (REST + webhooks)

## 3. Required Capabilities

See `KYC_AML_REQUIREMENTS.md` for the complete requirements specification.

### Minimum Capabilities

| Capability | Required |
|-----------|----------|
| Document verification (passport, ID, license) | YES |
| Biometric liveness detection | YES |
| Sanctions screening (OFAC + EU + UN) | YES |
| PEP screening | YES |
| Adverse media | YES |
| Jurisdiction screening | YES |
| GDPR compliance | YES |
| REST API | YES |
| Webhooks | YES |
| Sandbox environment | YES |
| EU regulatory support | YES |
| UAE regulatory support | YES |

### Preferred Capabilities

| Capability | Preferred |
|-----------|----------|
| Transaction monitoring | YES |
| Wallet/blockchain address screening | YES |
| KYB (business verification) | YES |
| Case management | YES |
| Batch processing | YES |
| SDK (JavaScript/Python) | YES |
| Global coverage (50+ countries) | YES |

## 4. Integration Requirements

| Requirement | Specification |
|-------------|--------------|
| API protocol | REST (JSON) |
| Authentication | Bearer token or API key |
| Rate limit | Minimum 100 requests/minute |
| Webhooks | Real-time status updates |
| Sandbox | Full test environment with test documents |
| Documentation | Complete API docs with code examples |
| SDK | Official SDK for at least one language |
| Uptime SLA | 99.9% minimum |
| Response time | < 30 seconds for automated verification |
| Manual review SLA | < 24 hours |

## 5. Data and Security Requirements

| Requirement | Specification |
|-----------|--------------|
| Encryption at rest | AES-256 |
| Encryption in transit | TLS 1.3 |
| Data residency | EU data in EU; UAE data in UAE (if required) |
| GDPR compliance | Full compliance (access, rectify, erase, portability) |
| Data retention | Configurable per regulatory requirements |
| SOC 2 Type II | Required (current report) |
| ISO 27001 | Preferred |
| Penetration test | Annual (most recent report required) |
| Breach notification | < 72 hours |
| Access logging | Full audit trail of data access |

## 6. Evaluation Criteria

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Regulatory coverage | 15% | EU AMLD5/6, UAE AML-CFT, MiCA, FATF |
| Geographic coverage | 15% | Number of countries supported |
| API quality | 10% | Documentation, SDK, sandbox, response time |
| Compliance features | 15% | Sanctions, PEP, adverse media, transaction monitoring |
| Security | 10% | SOC2, ISO 27001, encryption, penetration tests |
| GDPR compliance | 10% | Data residency, retention, access controls |
| UAE compatibility | 5% | VARA awareness, UAE document support |
| EU compatibility | 5% | MiCA awareness, EEA document support |
| Pricing | 5% | Per-verification, volume discounts, setup fees |
| SLA | 5% | Uptime, response time, manual review time |
| Implementation time | 5% | Time to go-live from contract signing |

## 7. Proposal Format

Proposals should include:

1. **Company overview** — history, funding, team size, offices
2. **Compliance certifications** — SOC 2, ISO 27001, PCI DSS (if applicable)
3. **Regulatory coverage** — supported regulations and jurisdictions
4. **Technical capabilities** — API documentation, SDK, sandbox access
5. **Security posture** — penetration test reports, breach history
6. **Pricing** — per-verification, volume tiers, setup, monthly minimums
7. **SLA** — uptime guarantee, response times, support hours
8. **Implementation** — timeline, onboarding process, dedicated CSM
9. **Case studies** — blockchain/crypto clients, similar projects
10. **References** — at least 3 client references

## 8. Timeline

| Phase | Duration |
|-------|----------|
| RFP issuance | 2026-08-14 |
| Proposal submission deadline | 2026-09-14 (4 weeks) |
| Evaluation period | 2 weeks after deadline |
| Selection decision | 2026-10-01 |
| Contract negotiation | 2 weeks |
| Implementation | 4-8 weeks |
| Go-live | 2026-12-01 (target) |

## 9. Submission Instructions

- Submit proposals to: <TBD — to be provided after entity formation>
- Format: PDF, maximum 50 pages
- Deadline: 2026-09-14
- Questions: Submit via email by 2026-08-28

## 10. Important Notes

- No provider has been selected. This RFP is open.
- Selection requires Rojs Gordons approval.
- Selection requires compliance officer review.
- Provider must not have conflict of interest with Verdis Chain.
- Provider must pass security review of their platform.
- Contract will include data processing agreement (GDPR Article 28).
- Provider must support contract termination and data export.
