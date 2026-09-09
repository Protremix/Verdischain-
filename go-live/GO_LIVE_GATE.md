# Verdis Chain Mainnet & Token Sale — Go-Live Gate Specification

**Document Version:** 1.0.0  
**Effective Date:** August 14, 2026  
**System Target:** Verdis Chain Layer-1 Substrate Mainnet & VRDX Public Token Sale  
**Current Gate Decision:** **RED / LAUNCH BLOCKED**  
**Executive Authority:** Rojs (Executive Sponsor)  

---

## 1. Document Control & Governance Framework

| Attribute | Details |
| :--- | :--- |
| **Document Owner** | Verdis Chain Governance & Release Engineering Committee |
| **Approving Body** | Executive Board & Lead Technical Council |
| **Sign-Off Protocol** | Mandatory 4-Way Unanimous Sign-Off (Legal, Security, Technical, Executive) |
| **Review Cycle** | Daily during pre-launch gate phase; per-blocker update upon evidence submission |
| **Classification** | Confidential / Official Mainnet Release Artifact |

---

## 2. Purpose and Gate Authority

### 2.1 Purpose
This document establishes the formal, binding **Go-Live Gate Specification** for the Verdis Chain Substrate Layer-1 Mainnet network instantiation and the concurrent VRDX Public Token Sale. It sets forth the strict operational, legal, cryptographic, technical, and regulatory prerequisites that must be satisfied prior to initializing the genesis block or opening user registration on the token sale platform.

### 2.2 Gate Authority Structure
Launch authorization requires **unanimous 4-Way Sign-Off** across four distinct operational domains:
1. **Legal Sign-Off:** Written regulatory opinions and jurisdictional compliance verification.
2. **Security Sign-Off:** Independent external audit verification with zero remaining critical/high vulnerabilities and completed physical key ceremony.
3. **Technical Sign-Off:** Validator node operational readiness, genesis mapping verification, Substrate runtime test suite compliance, and tokenomics code alignment.
4. **Executive Sign-Off:** Final formal release approval and executive authorization by **Rojs**.

---

## 3. Executive Decision Rules & Mandatory Launch Criteria

### 3.1 Strict Launch Block Rule
> **STRICT GO/NO-GO MANDATE:**  
> **IF ANY P0 BLOCKER REMAINS OPEN, THE GO-LIVE GATE IS AUTOMATICALLY EVALUATED AS RED (LAUNCH BLOCKED). NO PARTY OR AUTOMATION SCRIPT HAS THE AUTHORITY TO OVERRIDE THIS GATE OR RECOMMEND MAINNET LAUNCH OR TOKEN SALE DEPLOYMENT.**

Currently, **7 OUT OF 7 EXTERNAL P0 BLOCKERS REMAIN OPEN**. Therefore, the official decision of this Go-Live Gate is: **DO NOT RECOMMEND LAUNCH**.

---

## 4. Master Hard Blockers Checklist (18 Mandatory Gates)

Every single gate item listed below must be evaluated, supported by verified physical/digital evidence, and formally signed off prior to mainnet launch.

### 1. UAE / VARA Legal Path Approved
* **Requirement:** Written legal opinion from licensed UAE legal counsel confirming regulatory status under VARA rules.
* **Verification Method:** Legal opinion letter review and regulatory filing verification.
* **Evidence Required:** Executed Legal Opinion Document from licensed Dubai law firm.
* **Current Status:** ❌ **OPEN (BLK-01)** — *Waiting for Rojs to select and engage UAE counsel.*

### 2. EU / MiCA Token Classification Approved
* **Requirement:** Formal EU legal opinion classifying VRDX token as a Utility Token under MiCA (Regulation EU 2023/1114).
* **Verification Method:** Analysis of rights, governance, utility mechanisms, and MiCA Title II/III/IV applicability.
* **Evidence Required:** Signed EU Legal Qualification Opinion.
* **Current Status:** ❌ **OPEN (BLK-02)** — *Waiting for EU legal counsel qualification.*

### 3. Global Jurisdiction Policy Approved
* **Requirement:** Cross-border legal matrix specifying allowed, restricted, and prohibited investor jurisdictions.
* **Verification Method:** International regulatory counsel review of geo-fencing rules and sanctions laws.
* **Evidence Required:** Signed Global Jurisdiction Policy Document & Country Matrix.
* **Current Status:** ❌ **OPEN (BLK-03)** — *Waiting for international legal counsel sign-off.*

### 4. Offering Entity Formed & Operational
* **Requirement:** Formal corporate entity registered, with operational corporate bank account and institutional custody setup.
* **Verification Method:** Certificate of Incorporation and banking confirmation review.
* **Evidence Required:** Certificate of Incorporation, M&A, active corporate bank/custody statements.
* **Current Status:** ❌ **OPEN (BLK-06)** — *Waiting for Rojs & corporate counsel entity registration.*

### 5. KYC/AML Provider Approved & Integrated
* **Requirement:** Contracted enterprise KYC/AML vendor integrated into sale portal with automated OFAC/UN screening.
* **Verification Method:** End-to-end integration testing in staging environment.
* **Evidence Required:** Executed Vendor MSA/SLA & Staging Integration Test Report.
* **Current Status:** ❌ **OPEN (BLK-07)** — *Waiting for Rojs to select provider and sign agreement.*

### 6. Independent Security Audit Completed
* **Requirement:** Full security audit of all 16 Substrate pallets, weights, runtime, EVM layer, and bridge contracts by a top-tier security firm.
* **Verification Method:** Comprehensive manual code review, dynamic testing, and fuzzing by external security experts.
* **Evidence Required:** Executed Audit Contract & SOW; Formal Audit Report.
* **Current Status:** ❌ **OPEN (BLK-04)** — *Waiting for Rojs to contract audit firm.*

### 7. Critical Security Findings = 0
* **Requirement:** Verification that zero Critical and zero High severity findings remain unmitigated in the release codebase.
* **Verification Method:** Re-audit re-testing and signature of audit firm lead lead.
* **Evidence Required:** Final Audit Re-test Report confirming **0 Critical / 0 High** findings.
* **Current Status:** ❌ **OPEN (BLK-04)** — *Pending audit completion and re-test.*

### 8. Air-Gapped Key Ceremony Completed
* **Requirement:** Key generation ceremony performed on offline machines for 21 validator keys and 5 treasury multisig keys in front of 4 witnesses.
* **Verification Method:** Physical witness observation, cryptographic hash validation, video audit trail.
* **Evidence Required:** Signed Witness Affidavits (4), Public Key Registry, Ceremony Audit Log.
* **Current Status:** ❌ **OPEN (BLK-05)** — *Waiting for physical ceremony execution.*

### 9. 21 Validator Keys Verified On-Chain
* **Requirement:** 21 validator consensus public keys correctly formatted (sr25519/ed25519) and configured to produce blocks in test genesis.
* **Verification Method:** Automated RPC check validating session keys and block authoring in dry-run testnet.
* **Evidence Required:** Testnet Genesis Block Verification Log showing 21 active validators.
* **Current Status:** ⚠️ **PENDING KEY CEREMONY** — *Awaiting BLK-05 key generation.*

### 10. 5 Multisig Treasury Keys Verified
* **Requirement:** 5 multi-signature root keys verified for governance and treasury management (3-of-5 threshold configuration).
* **Verification Method:** Test transaction signing and threshold execution on Substrate multisig pallet.
* **Evidence Required:** Multisig Pallet Configuration Export & Staging Execution Proof.
* **Current Status:** ⚠️ **PENDING KEY CEREMONY** — *Awaiting BLK-05 key generation.*

### 11. Genesis / Key Mapping Independently Verified
* **Requirement:** Deterministic verification that the genesis specification JSON file matches exact key hashes from key ceremony.
* **Verification Method:** Independent cryptographic SHA-256 hash calculation and cross-check script.
* **Evidence Required:** Deterministic Genesis Verification Log & Hash Comparison Report.
* **Current Status:** ⚠️ **PENDING KEY CEREMONY** — *Awaiting BLK-05 output.*

### 12. Tokenomics Consistent with Code & Genesis
* **Requirement:** Initial supply allocations, inflation parameters, vesting schedules, and pallet storage constants match approved Tokenomics Spec v2.1.
* **Verification Method:** Automated CI integration test suite (`audit_genesis.py` / `audit_supply.py`).
* **Evidence Required:** CI Tokenomics Verification Pass Log (100% parameter match).
* **Current Status:** 🟢 **INTERNAL READY** — *Verified internally; pending final mainnet genesis JSON generation.*

### 13. Website Claims Verified Against Technical Evidence
* **Requirement:** All marketing claims on the public website and lightpaper audited and matched to test suite evidence.
* **Verification Method:** Claims Register audit (`audit_whitepaper_docs.txt` and `audit_homepage_sale.txt`).
* **Evidence Required:** Signed Website Claims Audit Matrix.
* **Current Status:** 🟢 **INTERNAL READY** — *Claims register prepared; pending final legal review.*

### 14. Sale Eligibility Engine Tested
* **Requirement:** Geo-fencing, IP blocking, KYC verification, and sanctions filtering engine end-to-end load tested.
* **Verification Method:** Simulated user onboarding tests across restricted and permitted IP/country ranges.
* **Evidence Required:** Sale Engine Staging Test Log showing 100% compliance with blocking rules.
* **Current Status:** ⚠️ **PENDING KYC VENDOR & LEGAL MATRIX** — *Awaiting BLK-03 & BLK-07.*

### 15. Legal Sign-Off
* **Requirement:** Formal written authorization to launch from Legal Counsel based on resolved legal blockers.
* **Verification Method:** Formal legal clearance certificate.
* **Evidence Required:** Executed Legal Go-Live Sign-Off Certificate.
* **Current Status:** ❌ **BLOCKED** — *Awaiting resolution of BLK-01, BLK-02, BLK-03, BLK-06.*

### 16. Security Sign-Off
* **Requirement:** Formal written authorization to launch from External Audit Firm Lead and Security Lead.
* **Verification Method:** External audit report sign-off.
* **Evidence Required:** Executed Security Go-Live Sign-Off Certificate.
* **Current Status:** ❌ **BLOCKED** — *Awaiting resolution of BLK-04, BLK-05.*

### 17. Technical Sign-Off
* **Requirement:** Technical sign-off from Lead Engineer confirming all 503 tests pass, validator nodes ready, and weights configured.
* **Verification Method:** CI/CD test suite execution and testnet stability verification.
* **Evidence Required:** Executed Technical Go-Live Sign-Off Certificate & Automated CI Pass Log.
* **Current Status:** 🟢 **INTERNAL READY** — *503 tests passing; pending mainnet key integration.*

### 18. Rojs Executive Sign-Off
* **Requirement:** Final executive order and signature authorizing Mainnet Genesis generation and Public Token Sale launch.
* **Verification Method:** Executive decision record signed by Rojs.
* **Evidence Required:** Signed Executive Launch Authorization Order.
* **Current Status:** ❌ **BLOCKED** — *Pending resolution of all 7 P0 blockers.*

---

## 5. Go-Live Gate Verification Procedure

The gate verification procedure follows a mandatory 5-stage sequential workflow:

```
+---------------------------------------------------------------------------------+
| STAGE 1: EXTERNAL EVIDENCE SUBMISSION                                          |
| External legal opinions, audit reports, vendor contracts, witness affidavits   |
+---------------------------------------------------------------------------------+
                                        │
                                        ▼
+---------------------------------------------------------------------------------+
| STAGE 2: INDEPENDENT DOMAIN REVIEW                                             |
| Legal, Security, Technical, and Compliance leads review submitted artifacts     |
+---------------------------------------------------------------------------------+
                                        │
                                        ▼
+---------------------------------------------------------------------------------+
| STAGE 3: AUTOMATED CI/CD VERIFICATION GATE                                     |
| Re-run 503 Substrate tests, weight checks, supply & genesis hash validation    |
+---------------------------------------------------------------------------------+
                                        │
                                        ▼
+---------------------------------------------------------------------------------+
| STAGE 4: FORMAL 4-WAY SIGN-OFF EXECUTION                                        |
| Legal, Security, Technical, and Executive leads execute digital signatures     |
+---------------------------------------------------------------------------------+
                                        │
                                        ▼
+---------------------------------------------------------------------------------+
| STAGE 5: MAINNET & TOKEN SALE RELEASE TRIGGER                                   |
| Rojs issues final executive order; genesis deployed; sale platform opened      |
+---------------------------------------------------------------------------------+
```

---

## 6. Post-Launch Emergency Halt Procedure

In the event of a critical post-launch anomaly (e.g., zero-day vulnerability in runtime, consensus fork, bridge exploit, or regulatory emergency), the following emergency halt protocol shall be executed immediately:

### 6.1 Emergency Triggers
1. **Critical Vulnerability Discovery:** Any unpatched exploit threatening network state integrity or user funds.
2. **Consensus Breakdown:** Unintended chain split or >33% validator offline rate.
3. **Bridge Anomaly:** Divergence in locked asset backing on cross-chain bridge.
4. **Legal / Regulatory Injunction:** Formal cease-and-desist order from primary regulator.

### 6.2 Execution Playbook
1. **Validator Consensus Pause:**
   * Executive / Security Lead triggers Emergency On-Chain Circuit Breaker via 3-of-5 Multi-Sig Root key.
   * Pause extrinsic halts state transitions across non-essential pallets.
2. **Bridge Freeze:**
   * Automated circuit breaker freezes cross-chain token wrapping and bridge contracts immediately.
3. **Token Sale Halt:**
   * Sale launchpad frontend switches instantly to Maintenance Mode via global flag.
   * Automated API stops accepting deposits and processing transactions.
4. **Incident Command Mobilization:**
   * Incident Response Team mobilizes within 15 minutes per established Incident Response Playbook.

---

## 7. Sign-Off Matrix Table

*Note: Sign-off fields must remain unexecuted until ALL 18 hard blockers are fully resolved.*

| Sign-Off Type | Authorized Person | Date | Required Evidence Artifact | Status / Signature |
| :--- | :--- | :--- | :--- | :--- |
| **Legal Sign-Off** | Lead Legal Counsel | *PENDING* | VARA Opinion, MiCA Qualification, Jurisdiction Matrix | ❌ **BLOCKED** (Awaiting BLK-01, BLK-02, BLK-03, BLK-06) |
| **Security Sign-Off** | Lead Security Auditor & Security Eng | *PENDING* | Audit Report (0 Critical/High), Key Ceremony Witness Affidavits | ❌ **BLOCKED** (Awaiting BLK-04, BLK-05) |
| **Technical Sign-Off** | Lead Substrate Architect | *PENDING* | 503 Passing Test Logs, Genesis Hash Verification, Validator Node Readiness | ⚠️ **PROVISIONAL** (Internal Ready; Pending Keys) |
| **Executive Sign-Off** | **Rojs** (Executive Sponsor) | *PENDING* | Resolved Master Blocker Register (0 Open P0s), Final 4-Way Compliance Package | ❌ **BLOCKED** (DO NOT LAUNCH) |

---

**FINAL GATE EVALUATION RESULT:**  
🔴 **RED / LAUNCH BLOCKED — DO NOT LAUNCH MAINNET OR TOKEN SALE**  
*Reason: 7 out of 7 external P0 blockers remain open. Resolution of external dependencies and formal Rojs sign-off required.*
