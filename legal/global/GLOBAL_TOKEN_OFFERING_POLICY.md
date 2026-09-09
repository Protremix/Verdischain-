# VERDIS CHAIN GLOBAL TOKEN OFFERING POLICY

**Document Version:** 1.0  
**Effective Date:** August 14, 2026  
**Status:** DRAFT / PENDING LEGAL COUNSEL REVIEW  
**Approval Requirement:** Rojs Approval Required for Status Changes or Policy Revisions  

---

## 1. PROJECT CONTEXT & ECOSYSTEM OVERVIEW

- **Protocol Description:** Verdis Chain is a high-performance Substrate Layer-1 blockchain network designed for decentralized finance, smart contract execution, and enterprise interoperability.
- **Native Token:** VRDX
  - **Total Supply:** 100,000,000,000 (100 Billion) VRDX
  - **Decimals:** 9
- **Core Product Modules:**
  - Non-Custodial Wallet (client-side seed management and interface)
  - Automated Market Maker (AMM) DEX (decentralized liquidity pools and token swaps)
  - Delegated Proof-of-Stake (DPoS) Staking (validator delegation and consensus security)
  - On-Chain Governance (community proposals and protocol parameter upgrades)
  - Ecosystem Treasury (on-chain resource management)
- **Current Lifecycle Stage:** TESTNET (Pre-Mainnet / Pre-Token Generation Event).
- **Corporate Entities & Structure:**
  - **Operating Entity:** Protremix (Spain)
  - **Ecosystem Foundation:** Foundation Entity (UAE - Planned / In Progress)
  - **Offering Entity:** Token Issuance Entity (TBD pending legal counsel structuration)

---

## 2. PURPOSE AND SCOPE

### 2.1 Purpose
This Global Token Offering Policy ("Policy") establishes the legal, compliance, and risk management framework governing the issuance, offering, distribution, marketing, sale, and operational enablement of the VRDX token across global jurisdictions. The purpose is to ensure strict compliance with applicable international and local financial regulations, protect the project entities and team from legal liabilities, and prevent unauthorized public offerings or unlicensed financial activities.

### 2.2 Scope
This Policy applies to:
- All token issuance events, token sales (private, presale, public sale, Token Generation Event / TGE), liquidity allocations, airdrops, and secondary market enablement.
- All core ecosystem modules including the Non-Custodial Wallet, AMM DEX, DPoS Staking, Governance, and Ecosystem Treasury interactions.
- All marketing, communications, promotional campaigns, social media outreach, and investor relations globally.
- All entities, directors, officers, advisors, employees, and software interface deployments affiliated with Verdis Chain (including Protremix, planned UAE Foundation, and Offering Entity).

---

## 3. DEFINITIONS

- **Token (VRDX):** The native cryptographic digital asset of the Verdis Chain Layer-1 blockchain, configured with a 100 Billion fixed supply and 9 decimals.
- **Offering:** Any public or private issuance, presale, initial coin offering (ICO), token generation event (TGE), launchpad allocation, distribution, or sales campaign of VRDX tokens to investors, participants, or the public.
- **Sale:** The transfer of VRDX tokens to a counterparty in exchange for fiat currencies, stablecoins, virtual assets, or other valuable consideration.
- **Exchange / CASP / VASP:** Any centralized digital asset exchange (CEX), broker-dealer, or Crypto-Asset Service Provider / Virtual Asset Service Provider facilitating secondary market trading, custody, or fiat gateway access for VRDX.
- **Decentralized Exchange (DEX):** Peer-to-peer automated market maker smart contracts and liquidity pools operating on Verdis Chain allowing automated swaps without centralized intermediaries.
- **Non-Custodial Wallet:** Open-source or proprietary client-side software interfaces enabling users to hold, manage, and interact with VRDX tokens and Verdis Chain smart contracts while maintaining sole possession of their private keys.
- **Staking:** The Delegated Proof-of-Stake (DPoS) consensus mechanism where VRDX holders delegate or stake tokens to active network validators to secure network consensus and receive protocol rewards.
- **Governance:** On-chain voting and proposal protocols enabling VRDX holders to participate in network parameter adjustments, upgrade proposals, and treasury disbursements.

---

## 4. JURISDICTION CLASSIFICATION SYSTEM

Every jurisdiction globally is assigned one of four strict operational statuses within the Verdis Chain Jurisdiction Matrix:

1. **ALLOW:**
   - **Definition:** Jurisdictions where formal written legal opinions from qualified local legal counsel confirm that VRDX token offerings, marketing, and ecosystem participation comply with local legal and regulatory frameworks without requiring licensing or where all mandatory licenses/registrations have been obtained.
   - **Operational Impact:** Unrestricted access across UI, API, and transaction layers, subject to standard Terms of Service and user verification.

2. **RESTRICT:**
   - **Definition:** Jurisdictions where offering, marketing, or interacting with VRDX is permitted only under specified regulatory conditions (e.g., restricted strictly to Accredited/Institutional Investors, specific volume limits, mandatory prospectus exemptions, or modified feature sets).
   - **Operational Impact:** Access gated by mandatory identity verification (KYC/AML), accredited investor status verification, and tailored disclosure agreements.

3. **BLOCK:**
   - **Definition:** Jurisdictions strictly prohibited due to legal bans on digital asset offerings, high-risk AML/CFT designations (FATF blacklist), comprehensive international sanctions (e.g., OFAC, EU, UN, UK Sanctions List), or severe regulatory enforcement environments.
   - **Operational Impact:** Absolute restriction across UI layer (geo-blocking), API layer (IP blocking), and transaction layer (address blacklisting/ACL checks).

4. **LEGAL_REVIEW_REQUIRED:**
   - **Definition:** The mandatory default classification for any jurisdiction that has not undergone complete legal analysis by qualified legal counsel or where regulatory status remains pending formal opinion.
   - **Operational Impact:** Strictly prohibited from active token offerings, targeted marketing, or proactive user onboarding until formal review and executive approval occur.

---

## 5. DEFAULT RULE & CONSERVATIVE LEGAL MANDATE

- **Default Rule:** Any jurisdiction NOT explicitly classified as ALLOW, RESTRICT, or BLOCK in the official Jurisdiction Matrix defaults automatically to **LEGAL_REVIEW_REQUIRED**.
- **No Legal Conclusions Pre-Counsel:** Neither technical staff, management, nor operational personnel may invent legal conclusions, assume regulatory exemptions, or extrapolate permissions from neighboring jurisdictions.
- **Zero-Uncertainty Principle:** **Never convert uncertainty into ALLOW.** In all cases of regulatory ambiguity, missing legal opinion, or evolving legal frameworks, the jurisdiction MUST remain classified as `LEGAL_REVIEW_REQUIRED` or `BLOCK`. All token classifications remain `UNDETERMINED` pending formal legal counsel engagement.

---

## 6. ENFORCEMENT ARCHITECTURE & TECHNICAL CONTROLS

Compliance is enforced programmatically across three defensive layers:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. UI LAYER (GEO-BLOCKING)                                  │
│ Client-side IP Geolocation, CDN Edge Blocks, UI Banners     │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│ 2. API LAYER (IP FILTERING & KYC/AML)                      │
│ Edge Gateway Validation, Sanctions API, KYC Verification   │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│ 3. TRANSACTION LAYER (ON-CHAIN ELIGIBILITY)                 │
│ Smart Contract ACLs, Substrate Pallet Permissions, Vesting  │
└─────────────────────────────────────────────────────────────┘
```

### 6.1 UI Layer (Front-End & Interface Control)
- **Geolocation Filtering:** Cloudflare/CDN edge nodes automatically inspect incoming requests and block web interface access from IPs originating in `BLOCK` or unapproved `LEGAL_REVIEW_REQUIRED` jurisdictions.
- **Restricted Access Banners:** Clear statutory disclaimers and blocking notifications displayed to users from restricted regions.
- **Non-Custodial Interface Fencing:** DApp frontends (AMM DEX UI, Staking Portal, Governance Dashboard) block transaction submission controls for restricted IP origins.

### 6.2 API Layer (Gateway & Middleware Control)
- **IP & Request Validation:** API Gateway endpoints validate client source IPs against dynamic geolocation databases and block REST/RPC calls from prohibited regions.
- **KYC/AML & Sanctions Screening:** Integration with accredited identity verification providers (e.g., Sumsub, Onfido) to perform mandatory sanctions screening (OFAC, UN, EU, UK), PEP checks, and proof-of-address verification prior to TGE participation or token purchase.
- **Token Offering Gating:** API endpoints servicing presales or token distribution verify approved KYC tokens before releasing purchase addresses or signing off-chain allocations.

### 6.3 Transaction Layer (On-Chain Protocol Control)
- **Whitelisting & Access Control Lists (ACL):** Substrate pallets and smart contracts enforce address eligibility for restricted sales and vesting contracts.
- **On-Chain Eligibility Verification:** Tokens from regulated distribution rounds are locked in vesting/permissioned pallets that require cryptographic signatures derived from verified KYC credentials prior to release.
- **Sanctions Address Blacklisting:** Automated ingestion of OFAC and regulatory blocked wallet address lists to restrict token transfers at the bridge/pallet level where applicable.

---

## 7. JURISDICTION STATUS REVIEW & RECLASSIFICATION PROCESS

To transition any jurisdiction from `LEGAL_REVIEW_REQUIRED` to `ALLOW`, `RESTRICT`, or `BLOCK`, the following mandatory workflow must be executed:

```
┌────────────────────────┐     ┌────────────────────────┐     ┌────────────────────────┐
│ 1. Formal Counsel      │ ──► │ 2. Comprehensive Legal │ ──► │ 3. Compliance & Tech   │
│ Engagement             │     │ Opinion Delivered      │     │ Risk Assessment        │
└────────────────────────┘     └────────────────────────┘     └────────────────────────┘
                                                                           │
┌────────────────────────┐     ┌────────────────────────┐                  │
│ 5. Matrix & System     │ ◄── │ 4. Executive Approval  │ ◄────────────────┘
│ Production Update      │     │ (ROJS APPROVAL REQ.)   │
└────────────────────────┘     └────────────────────────┘
```

1. **Counsel Engagement:** Formal engagement of reputable law firms specialized in financial regulation and digital assets within the target jurisdiction.
2. **Legal Opinion Delivery:** Legal counsel provides a formal, signed Legal Opinion addressing:
   - VRDX token classification (Utility Token, Security/Financial Instrument, Payment Asset, E-Money, etc.).
   - Public offering and presale registration requirements or exemptions.
   - Financial promotion and marketing restriction compliance.
   - Exchange / CASP / VASP licensing triggers for DEX and wallet operations.
   - Local KYC/AML and travel rule mandates.
3. **Compliance Assessment:** Legal & Risk team evaluates technical feasibility, KYC/AML overhead, and operational requirements.
4. **Executive Approval (Mandatory Gate):** The final evaluation package is submitted to executive management. **Rojs approval is strictly required for any status change.**
5. **Production System Update:** Upon written approval from Rojs, the Jurisdiction Matrix CSV, UI geo-blocking rules, API gatekeepers, and smart contract ACLs are updated simultaneously.

---

## 8. ONGOING REGULATORY MONITORING & AUDITING

- **Continuous Horizon Scanning:** Legal and compliance personnel monitor legislative updates, regulatory guidance, enforcement trends, and FATF publications monthly.
- **Triggered Re-Evaluation:** Immediate ad-hoc policy review is triggered upon major regulatory events (e.g., MiCA enforcement milestones, VARA rulebook circulars, SEC litigation developments).
- **Quarterly Audit:** Comprehensive quarterly audit of all jurisdiction classifications, active counsel engagements, and technical enforcement mechanisms.

---

## 9. GOVERNANCE, VERSION CONTROL & APPROVAL REQUIREMENT

### 9.1 Policy Governance
- **Policy Owner:** Legal & Compliance Department
- **Policy Version:** 1.0
- **Effective Date:** August 14, 2026
- **Review Cycle:** Quarterly or upon material regulatory/project changes.

### 9.2 Mandatory Approval Rule
**ROJS APPROVAL IS STRICTLY REQUIRED FOR ANY STATUS CHANGE IN THE JURISDICTION MATRIX OR ANY AMENDMENT TO THIS POLICY.** No jurisdiction may be reclassified from `LEGAL_REVIEW_REQUIRED` to `ALLOW` or `RESTRICT` without explicit, documented written authorization from Rojs.
