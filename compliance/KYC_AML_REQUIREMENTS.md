# KYC/AML Requirements — Verdis Chain

**Document ID:** COMPLIANCE-KYC-001
**Date:** 2026-08-14
**Status:** Requirements specification (provider not yet selected)
**Approval Required:** Rojs Gordons + Compliance Officer

---

## 1. Purpose

Define the complete KYC/AML requirements for the Verdis Chain token sale (VRDX) and platform operations (DEX, wallet, staking). These requirements govern user onboarding, transaction monitoring, sanctions screening, and regulatory compliance.

**The token sale is currently DISABLED. No KYC system will be activated until legal counsel approves the token offering.**

## 2. Regulatory Framework

| Regulation | Scope | Status |
|-----------|-------|--------|
| EU AMLD5 | EU anti-money laundering | Requires counsel review |
| EU AMLD6 | Enhanced due diligence | Requires counsel review |
| EU MiCA | Crypto-asset regulation | UNDETERMINED — pending classification |
| UAE AML-CFT | UAE anti-money laundering | Requires counsel review |
| FATF Recommendations | International AML standards | Recommended baseline |
| OFAC Sanctions | US sanctions screening | Required for all users |
| EU Sanctions | EU restrictive measures | Required for all users |
| UN Sanctions | UN Security Council | Required for all users |
| GDPR | EU data protection | Required for EU users |
| UAE PDPL | UAE data protection | Requires counsel review |

## 3. Risk Tiers

| Tier | Risk Level | Verification | Monitoring | Limits |
|------|-----------|--------------|------------|--------|
| Tier 1 | Low | Identity document + selfie + liveness | Standard | Up to €10,000/year |
| Tier 2 | Medium | Enhanced KYC (proof of address + source of funds) | Enhanced | Up to €50,000/year |
| Tier 3 | High | Full enhanced due diligence (UBO, financial statements, interview) | Continuous | Case-by-case |
| Blocked | Prohibited | N/A — transaction rejected | N/A | €0 |

### Risk Factors
- **Geographic risk:** High-risk jurisdictions per FATF
- **Transaction risk:** Large or unusual transactions
- **Behavioral risk:** Rapid in-and-out patterns, structuring
- **Adverse media:** Negative news about the individual or entity
- **PEP status:** Politically exposed persons

## 4. Required Capabilities

### 4.1 Identity Verification (KYC)

| Capability | Requirement | Description |
|-----------|-------------|-------------|
| Document verification | Required | Government ID, passport, driver's license |
| Biometric verification | Required | Selfie + liveness detection |
| Data extraction | Required | OCR from document (name, DOB, nationality, document number) |
| Document authenticity | Required | Check for forgery, tampering, template matching |
| Cross-reference | Required | Verify document data against selfie |
| Age verification | Required | Minimum 18 years old |
| Residency verification | Required for Tier 2+ | Proof of address (utility bill, bank statement) |
| Manual review | Required | Human review queue for flagged cases |

### 4.2 Business Verification (KYB)

| Capability | Requirement | Description |
|-----------|-------------|-------------|
| Registry lookup | Required | Company registry verification (number, status, address) |
| UBO identification | Required | Ultimate beneficial owner identification (>25%) |
| Financial statements | Required for Tier 3 | Company financial health check |
| Director verification | Required | ID + role verification for directors |
| Adverse media | Required | Negative news screening for company |
| Sanctions screening | Required | Company + UBO against sanctions lists |

### 4.3 Screening

| List Type | Source | Frequency |
|-----------|--------|-----------|
| OFAC SDN | US Treasury | Real-time + daily refresh |
| EU Consolidated | EU Official Journal | Real-time + daily refresh |
| UN Security Council | UN | Real-time + daily refresh |
| UK HMT | UK Treasury | Real-time + daily refresh |
| PEP lists | Commercial database | Real-time + weekly refresh |
| Adverse media | Commercial database | Real-time + weekly refresh |
| Internal blocklist | Platform-managed | Real-time |

### 4.4 Transaction Monitoring

| Capability | Requirement | Description |
|-----------|-------------|-------------|
| Velocity checks | Required | Detect rapid sequential transactions |
| Structuring detection | Required | Detect smurfing patterns |
| Large transaction flag | Required | Flag transactions above threshold |
| Unusual pattern detection | Required | ML-based anomaly detection |
| Cross-border tracking | Required | Track cross-jurisdiction flows |
| Suspicious activity reports | Required | Generate SAR/STR for compliance team |
| Real-time alerts | Required | Instant alert on suspicious activity |

### 4.5 Wallet Screening

| Capability | Requirement | Description |
|-----------|-------------|-------------|
| Address risk scoring | Required | Score wallet addresses for illicit activity |
| Chain analysis | Required | Trace transaction history to/from flagged addresses |
| Mixer/tumbler detection | Required | Flag addresses associated with mixers |
| Dark market detection | Required | Flag addresses associated with darknet markets |
| Sanctioned address check | Required | Check against OFAC/other sanctioned address lists |
| Exchange address identification | Required | Identify known exchange addresses |

## 5. Data and Privacy

| Requirement | Description |
|-------------|-------------|
| GDPR compliance | Right to access, rectify, erase, portability |
| Data residency | EU data stored in EU; UAE data stored in UAE (if required) |
| Encryption at rest | AES-256 minimum |
| Encryption in transit | TLS 1.3 minimum |
| Access logging | All access to KYC data logged |
| Data retention | Per regulatory requirements (typically 5 years post-relationship) |
| Data minimization | Only collect what is required |
| Consent management | Explicit consent for processing |
| Breach notification | 72-hour notification per GDPR |

## 6. Integration Requirements

| Requirement | Description |
|-------------|-------------|
| REST API | Full programmatic access to all features |
| Webhooks | Real-time status updates (verification complete, rejected, alert) |
| Sandbox | Full testing environment |
| Rate limits | Minimum 100 requests/minute |
| Batch processing | Bulk verification for high-volume periods |
| SDK | Official SDK for at least one language (JavaScript/Python) |
| Documentation | Full API documentation with examples |
| Status page | Provider uptime monitoring |

## 7. Workflow

```
User Signup
    ↓
Email Verification
    ↓
Jurisdiction Check (geo-block restricted/blocked countries)
    ↓
KYC Initiation (Tier 1: document + selfie + liveness)
    ↓
Sanctions/PEP/Adverse Media Screening (real-time)
    ↓
[Auto-Approve] or [Manual Review Queue]
    ↓
Risk Tier Assignment (Tier 1/2/3)
    ↓
Purchase Limits Set
    ↓
Ongoing Monitoring (transactions + periodic re-screening)
    ↓
[SAR/STR if suspicious activity detected]
```

### Rejection Reasons
- Sanctions match → Block + report
- PEP without enhanced due diligence → Manual review
- Adverse media → Manual review
- Jurisdiction blocked → Block
- Age < 18 → Block
- Document forgery → Block + report
- Failed liveness → Manual review

## 8. Geographic Coverage

| Region | Required | Status |
|--------|----------|--------|
| EU/EEA | Required | UNDETERMINED — pending counsel |
| UAE | Required | UNDETERMINED — pending counsel |
| UK | Required | UNDETERMINED — pending counsel |
| USA | Required | UNDETERMINED — pending counsel |
| Canada | Required | UNDETERMINED — pending counsel |
| Australia | Required | UNDETERMINED — pending counsel |
| Singapore | Required | UNDETERMINED — pending counsel |
| Japan | Required | UNDETERMINED — pending counsel |
| Switzerland | Required | UNDETERMINED — pending counsel |
| Other | Best effort | UNDETERMINED — pending counsel |

## 9. Audit and Compliance Reporting

| Report | Frequency | Audience |
|--------|-----------|----------|
| KYC verification summary | Monthly | Compliance Officer + Rojs |
| Sanctions screening log | Monthly | Compliance Officer |
| SAR/STR reports | Per occurrence | Financial Intelligence Unit (per jurisdiction) |
| Risk assessment review | Quarterly | Compliance Officer + Council |
| Provider performance review | Quarterly | Rojs + Compliance Officer |
| Annual compliance audit | Annual | External auditor |

## 10. Responsibilities

| Role | Responsibility |
|------|---------------|
| Rojs Gordons | Final approval, provider selection |
| Compliance Officer | Day-to-day KYC operations, SAR/STR filing |
| Council | Policy oversight, threshold changes |
| KYC Provider | Verification, screening, monitoring (outsourced) |
| Legal Counsel | Regulatory interpretation, obligations |
