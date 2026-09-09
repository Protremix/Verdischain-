# DMCC Free Zone Application Template — Verdis Chain Foundation

**Status:** TEMPLATE — Requires completion by UAE legal counsel
**Prepared by:** Arlo (Chief Engineer, Verdis Chain)
**Date:** August 21, 2026
**Classification:** Pre-Formation Document

---

## IMPORTANT NOTICE

> This template is a preparatory document completed with all known technical and operational details. Fields marked `[TO BE COMPLETED BY LEGAL COUNSEL]` require input from a UAE-licensed legal practitioner. This document does NOT constitute a regulatory filing or legal advice. All regulatory classifications are UNDETERMINED pending formal counsel review.

---

## 1. Entity Overview

| Field | Value |
|-------|-------|
| **Proposed Entity Name** | Verdis Chain Foundation |
| **Entity Type** | Non-Profit Foundation (DMCC Free Zone) |
| **Free Zone** | Dubai Multi Commodities Centre (DMCC) |
| **Jurisdiction** | Dubai, United Arab Emirates |
| **Regulatory Authority** | Virtual Assets Regulatory Authority (VARA) |
| **Principal Activity** | Blockchain protocol governance, ecosystem stewardship, token management |
| **Proposed Office** | DMCC Jumeirara Lakes Towers (JLT), Dubai |
| **Entity Status** | Not yet formed |

## 2. Corporate Structure

### 2.1 Proposed Three-Entity Structure

| Entity | Jurisdiction | Role | Status |
|--------|-------------|------|--------|
| **Verdis Chain Foundation** | UAE (DMCC) | Protocol governance, ecosystem grants, brand stewardship | Not yet formed |
| **Token Offering SPV** | TBD by counsel | Token distribution, public sales, presale | Not yet formed |
| **Protremix S.L.** | Spain (EU) | Software engineering, development, technology provider | Exists (Rojs Gordons) |

### 2.2 Foundation Governance

| Role | Count | Responsibility |
|------|-------|----------------|
| Founder | 1 | Rojs Gordons — initial formation, does NOT retain unilateral control |
| Board Members | [TO BE COMPLETED] | [TO BE COMPLETED BY LEGAL COUNSEL] |
| Council Secretary | [TO BE COMPLETED] | [TO BE COMPLETED BY LEGAL COUNSEL] |
| Compliance Officer | [TO BE COMPLETED] | [TO BE COMPLETED BY LEGAL COUNSEL] |

### 2.3 Ownership & Control

- Foundation is non-profit — no shareholders, no dividend rights
- Governance by board with constitution-defined voting thresholds
- Treasury controlled by 3-of-5 multisig (separation of duties per Constitution Article 15)
- No single individual has unilateral treasury access

## 3. Business Activities

### 3.1 Primary Activities (DMCC Category)

| # | Activity | Description | DMCC Category Code |
|---|----------|-------------|-------------------|
| 1 | Blockchain Protocol Stewardship | Core protocol development oversight, network upgrades, governance facilitation | [TO BE COMPLETED BY LEGAL COUNSEL] |
| 2 | Ecosystem Grants | Developer grants, community programs, partnerships | [TO BE COMPLETED BY LEGAL COUNSEL] |
| 3 | Brand & IP Management | Verdis Chain brand assets, trademarks, domain management | [TO BE COMPLETED BY LEGAL COUNSEL] |
| 4 | Token Governance | VRDX token utility management, vesting schedules, allocation oversight | [TO BE COMPLETED BY LEGAL COUNSEL] |

### 3.2 VARA VASP Activities (Separate License Required)

| # | VARA Activity Category | Description | Status |
|---|----------------------|-------------|--------|
| 1 | Virtual Asset Issuance | VRDX token creation, distribution, whitepaper filing | Application pending |
| 2 | Virtual Asset Exchange Services | On-chain AMM DEX operation (pallet-amm-dex) | Application pending |
| 3 | Transfer & Settlement | Transaction relay, wallet infrastructure | Application pending |

### 3.3 Activities NOT Performed

- **Custody:** Verdis Chain does NOT custody user funds or private keys — all wallets are non-custodial
- **Broker-Dealer:** No fiat-to-crypto or crypto-to-fiat brokerage
- **Lending:** No lending or borrowing services
- **Management & Investment:** No fund management or investment advisory

## 4. Technical Architecture Summary

### 4.1 Protocol Parameters

| Parameter | Value |
|-----------|-------|
| Blockchain Framework | Substrate (Rust) |
| Consensus | DPoS with BABE/GRANDPA |
| Native Token | VRDX |
| Total Supply | 100,000,000,000 (100 Billion, hard-capped) |
| Token Precision | 9 decimal places |
| Runtime Pallets | 16 custom pallets |
| Validators | 21 (target for mainnet) |
| Current State | Testnet operational — Block #35,800+ |

### 4.2 Token Allocation (100B VRDX)

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

### 4.3 Non-Custodial Architecture

- User private keys are generated and stored locally on user devices
- No server-side key custody exists anywhere in the ecosystem
- Wallet applications (web, Android, iOS) use client-side cryptographic libraries
- Transaction relay service signs nothing — only relays pre-signed payloads
- DEX operations are peer-to-peer via autonomous AMM pools
- Foundation does not hold, transmit, or store user private keys

## 5. Financial Information

### 5.1 Funding Sources

| Source | Status | Amount |
|--------|--------|--------|
| Protremix S.L. (development) | Active | [TO BE COMPLETED] |
| Token presale (planned) | Not started | [TO BE COMPLETED BY LEGAL COUNSEL] |
| Grants / Partnerships | Not started | [TO BE COMPLETED] |

### 5.2 Estimated Annual Budget

| Category | Estimated Annual Cost |
|----------|----------------------|
| Server infrastructure (3 locations) | €2,964/year (~$3,200) |
| Legal & compliance | $55,000–$140,000 |
| Personnel | [TO BE COMPLETED] |
| Office (DMCC virtual) | $3,000–$8,000 |
| Audit & security | $50,000–$150,000 (one-time) |
| **Total** | [TO BE COMPLETED BY LEGAL COUNSEL] |

## 6. Compliance Framework

### 6.1 AML/KYC

| Requirement | Status |
|-------------|--------|
| AML policy | [TO BE COMPLETED BY LEGAL COUNSEL] |
| KYC procedure for token sale | [TO BE COMPLETED BY LEGAL COUNSEL] |
| Transaction monitoring tool | [TO BE COMPLETED — recommend Chainalysis or Elliptic] |
| Travel rule compliance | [TO BE COMPLETED BY LEGAL COUNSEL] |
| Suspicious activity reporting | [TO BE COMPLETED BY LEGAL COUNSEL] |

### 6.2 Data Protection

| Requirement | Status |
|-------------|--------|
| UAE Data Protection Law compliance | [TO BE COMPLETED BY LEGAL COUNSEL] |
| GDPR compliance (EU users) | [TO BE COMPLETED BY LEGAL COUNSEL] |
| Privacy policy | Published at https://verdischain.com/privacy |
| Data retention policy | [TO BE COMPLETED BY LEGAL COUNSEL] |

### 6.3 VARA-Specific Requirements

| Requirement | Status |
|-------------|--------|
| Whitepaper filing | [TO BE COMPLETED BY LEGAL COUNSEL] |
| Risk disclosure | [TO BE COMPLETED BY LEGAL COUNSEL] |
| Corporate governance framework | [TO BE COMPLETED BY LEGAL COUNSEL] |
| Compliance officer appointment | [TO BE COMPLETED BY LEGAL COUNSEL] |
| Prudential requirements | [TO BE COMPLETED BY LEGAL COUNSEL] |
| Market conduct rules | [TO BE COMPLETED BY LEGAL COUNSEL] |
| Technology governance | [TO BE COMPLETED BY LEGAL COUNSEL] |

## 7. Key Personnel

### 7.1 Current Team

| Name | Role | Nationality | Background |
|------|------|-------------|------------|
| Rojs Gordons | Founder & CEO | [TO BE COMPLETED] | Founder of Protremix S.L., built Anerium fintech platform, 15+ years fintech/payment systems |
| [TO BE COMPLETED] | Compliance Officer | [TO BE COMPLETED] | [TO BE COMPLETED] |
| [TO BE COMPLETED] | Board Member | [TO BE COMPLETED] | [TO BE COMPLETED] |

### 7.2 Required Hires

| Role | Timeline | Notes |
|------|----------|-------|
| UAE Compliance Officer | Before VARA filing | Must be UAE-resident, relevant experience |
| Registered Agent | Immediate | DMCC-registered agent |
| Legal Counsel (retainer) | Immediate | UAE-licensed, VARA experience |

## 8. Documents Required for DMCC Application

| # | Document | Status |
|---|----------|--------|
| 1 | Application Form (DMCC standard) | [TO BE COMPLETED BY LEGAL COUNSEL] |
| 2 | Business Plan | [TO BE COMPLETED BY LEGAL COUNSEL — this template serves as basis] |
| 3 | Memorandum of Association | [TO BE COMPLETED BY LEGAL COUNSEL] |
| 4 | Articles of Association | [TO BE COMPLETED BY LEGAL COUNSEL] |
| 5 | Passport copies of shareholders/directors | [TO BE COMPLETED — Rojs + board members] |
| 6 | Proof of address (directors) | [TO BE COMPLETED] |
| 7 | Bank reference letter | [TO BE COMPLETED] |
| 8 | CV / Resume of directors | [TO BE COMPLETED] |
| 9 | DMCC lease agreement (office space) | [TO BE COMPLETED — virtual office acceptable] |
| 10 | VARA pre-approval (if applicable) | [TO BE COMPLETED BY LEGAL COUNSEL] |

## 9. Timeline

| Phase | Duration | Target Completion |
|-------|----------|-------------------|
| Engage UAE legal counsel | 1-2 weeks | September 2026 |
| DMCC entity formation | 2-4 weeks | October 2026 |
| VARA VASP license application | 3-6 months | December 2026 – February 2027 |
| Corporate bank account | 1-3 months | February – April 2027 |
| AML/KYC framework | 2-4 weeks | November 2026 |
| **Total critical path** | **4-6 months** | **December 2026 – February 2027** |

## 10. Existing Documentation Available

The following documents are already prepared and available for counsel review:

- `legal/uae/VARA_COUNSEL_BRIEF.md` — 10,000+ word formal briefing for UAE legal counsel
- `legal/uae/VARA_DOCUMENT_INDEX.md` — Document checklist
- `legal/uae/VARA_ACTIVITY_MATRIX.md` — Activity-to-regulatory mapping
- `docs/ARCHITECTURAL_DECISIONS.md` — Approved executive decisions (ARCH-001 through ARCH-075)
- `docs/CORPORATE_REGULATORY_BRIEFING_PACK.md` — Corporate structure briefing
- `docs/EXECUTIVE_DECISIONS_2026_08_14.md` — Rojs's approval of all 8 executive decisions
- `docs/CANONICAL_FACTS.md` — Verified project facts
- `docs/CLAIMS_REGISTER.md` — Public claims register
- `docs/TREASURY_SECURITY.md` — Treasury security specification (3-of-5 multisig)

---

**END OF TEMPLATE — LEGAL COUNSEL MUST COMPLETE ALL [TO BE COMPLETED] FIELDS BEFORE FILING**
