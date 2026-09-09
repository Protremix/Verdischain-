# Request for Proposals (RFP): Independent Security Audit

**Project Name:** Verdis Chain  
**Document Type:** Request for Proposals (RFP) — External Security Audit  
**Document Version:** 1.0  
**Target Repository:** `Protremix/Verdischain-`  
**Date:** August 2026  
**Status:** Open for Proposal Submission  

---

## 1. Executive Summary & Project Overview

Verdis Chain is a high-performance, Layer-1 blockchain built on the Substrate framework designed for sustainable decentralized finance (DeFi), carbon credit verification, and scalable smart contracting. The platform integrates high-throughput consensus innovations alongside custom economic models.

### 1.1 Technical Architecture
The core architecture consists of a custom Substrate node, runtime logic composed of 16 bespoke pallets, off-chain transaction relays, web-based cryptographic key management, and containerized deployment infrastructure.

* **Blockchain Framework:** Substrate (Rust)
* **Runtime Codebase Size:** 1,901 Source Lines of Code (SLOC)
* **Node Codebase Size:** 1,916 Source Lines of Code (SLOC)
* **Pallets:** 16 custom pallets with full weight benchmark implementations
* **Automated Test Suite:** 503 passing unit, integration, and pallet benchmark tests
* **Web Wallet:** Non-custodial browser/mobile interface using `@noble/secp256k1`
* **Transaction Relay:** TX Relay v3 utilizing AES-256-GCM symmetric encryption
* **Infrastructure:** Docker containerized services, nginx reverse proxy, and 17 managed `systemd` system services

Verdis Chain is soliciting formal proposals from qualified, independent cybersecurity audit firms to conduct a comprehensive security review and penetration test of the complete Verdis Chain ecosystem prior to mainnet deployment.

---

## 2. Comprehensive Audit Scope

The scope of the security evaluation covers all on-chain runtime logic, node consensus, network protocol layers, off-chain infrastructure, cryptographic modules, and economic attack surfaces.

```
+-----------------------------------------------------------------------------------+
|                            VERDIS CHAIN AUDIT SCOPE                               |
+-----------------------------------------------------------------------------------+
|  1. Node Infrastructure & Networking    |  2. Custom Substrate Pallets (16)       |
|  3. Consensus & Execution Engine        |  4. Off-Chain Infrastructure & Relay    |
|  5. Non-Custodial Web Wallet & SDK      |  6. Deployment & System Security        |
|  7. Cryptographic Primitives & Keys     |  8. Economic & Game Theoretical Models  |
+-----------------------------------------------------------------------------------+
```

### 2.1 Substrate Runtime & Pallets (16 Modules)
The scope includes a thorough source code review of all 16 custom pallets implementing core state transitions:
1. `pallet-dpos`: Delegated Proof-of-Stake consensus state, validator selection, reward distribution.
2. `pallet-amm-dex`: Automated Market Maker exchange, liquidity pool provisioning, automated pricing logic.
3. `pallet-eco`: Ecological score calculation, sustainability verification algorithms.
4. `pallet-tokenomics`: Supply control, dynamic fee burning, minting rules, inflation/deflation schedules.
5. `pallet-vesting`: Linear and schedule-based token vesting releases for team and ecosystem funds.
6. `pallet-presale`: Multi-tier token presale distribution, contribution caps, refund mechanisms.
7. `pallet-fungible-tokens`: Custom token standard implementation, transfers, approvals, allowances.
8. `pallet-ibc`: Inter-Blockchain Communication interface, cross-chain state verification, bridge proofs.
9. `pallet-sealevel`: Parallel transaction execution scheduling and state lock management.
10. `pallet-gulf-stream`: Mempool management and transaction forwarding without block producer state locks.
11. `pallet-storage`: On-chain proof-of-storage, data availability attestation, challenge logic.
12. `pallet-turbine`: Block propagation data shredding and erased-coded transmission protocols.
13. `pallet-zk-compression`: Zero-Knowledge state compression, proof validation, rollup verification.
14. `pallet-poh`: Proof-of-History verifiable delay function (VDF) tick verification.
15. `pallet-circuit-breaker`: Emergency stop mechanism, volume rate limiting, anomaly isolation.
16. `pallet-address-lookup-tables`: On-chain address alias and compact transaction lookup tables.

### 2.2 Consensus, Staking & Governance
* **Proof-of-History (PoH) & DPoS Integration:** Clock synchronization, leader scheduling, and validator slot rotation.
* **Staking & Slashing:** Bond/unbond mechanisms, slash conditions (double signing, offline duration), reward distribution fairness.
* **Governance & Upgrades:** On-chain runtime upgrade safety (`set_code`), proposal queuing, emergency council overrides, state migration integrity.
* **Genesis Configuration:** Initial state parameters, validator allocations, chain spec validity across `dev`, `testnet`, and `mainnet`.

### 2.3 Off-Chain Services & Web Wallet
* **TX Relay v3:** Off-chain transaction submission proxy using AES-256-GCM encryption, replay protection, rate-limiting, and payload sanitization.
* **Non-Custodial Web Wallet:** Client-side key generation, key storage security, transaction signing via `@noble/secp256k1`, cross-site scripting (XSS) / injection protections.
* **RPC & REST APIs:** Exposure to Denial of Service (DoS), unauthorized RPC invocation, input validation, websocket stability.

### 2.4 Infrastructure & System Security
* **Container Hardening:** Review of Docker builds, non-root user execution, read-only root filesystem policies, `cap_drop ALL` privileges.
* **Nginx Reverse Proxy:** TLS termination, security headers (HSTS, CSP, CORS), rate limits, proxy buffering.
* **System Services:** Security posture of the 17 `systemd` service units managing node processes, monitoring, and relay daemons.

### 2.5 Economic & Cryptographic Attack Surfaces
* **Economic Vectors:** Sandwich attacks, Front-running, MEV exploitation in AMM, pool drainage, oracle/ecological score manipulation, flash-loan vulnerabilities.
* **Cryptographic Primitives:** Implementation of secp256k1, sr25519, ed25519, ZK verification logic, entropy sources, VDF tick checking.

---

## 3. Repository & Source Code Details

Auditors will be provided with full read-only access to the official code repositories and deployment configurations.

* **GitHub Repository:** `Protremix/Verdischain-`
* **Primary Language:** Rust (Substrate / FRAME v2)
* **Off-Chain Languages:** TypeScript / JavaScript (Web Wallet & Relay)
* **Infrastructure Specs:** Dockerfile, Docker Compose, systemd unit files, nginx.conf

### SLOC Breakdown Summary
| Component | Primary Language | SLOC | Scope Priority |
| :--- | :--- | :--- | :--- |
| Custom Pallets (16) | Rust | ~12,400 | Critical |
| Substrate Runtime | Rust | 1,901 | Critical |
| Node Subsystem | Rust | 1,916 | High |
| TX Relay v3 | TypeScript/Node.js | ~1,200 | High |
| Non-Custodial Web Wallet | TypeScript/React | ~2,500 | High |
| Infrastructure Scripts | Bash / Systemd / Docker | ~850 | Medium |

---

## 4. Test Suite & Benchmark Metrics

The codebase includes an extensive suite of unit, integration, and benchmark tests:
* **Passing Test Count:** 503 automated tests passing cleanly without warnings or failures.
* **Coverage:** Pallet storage, dispatchables, error conditions, origin verification, weight limits.
* **Weight Benchmarks:** Every pallet contains dedicated Substrate weight files (`weights.rs`) derived via FRAME benchmarking.

Auditors are expected to execute the test suite, review mock runtimes for coverage gaps, and perform additional fuzz testing or symbolic execution where applicable.

---

## 5. Historical Internal Findings & Required Re-Testing

An internal security review previously identified eight security findings across the runtime and infrastructure layers. All findings have been remediated in the codebase and **require independent re-verification and regression testing** by the auditor.

| ID | Title / Vulnerability Area | Historical Severity | Fix Applied | Auditor Re-Verification Task |
| :--- | :--- | :--- | :--- | :--- |
| **SEC-01** | Division by Zero in `remove_liquidity` | **Critical** | Added zero-check checks before liquidity calculation. | Verify arithmetic safety under zero-liquidity or edge ratio inputs. |
| **SEC-02** | Integer Overflow in LP Calculation | **High** | Replaced standard arithmetic with `checked_mul` & `checked_div`. | Audit all math operations in `pallet-amm-dex` for unhandled overflow/underflow. |
| **SEC-03** | Self-Scoring in `update_green_score` | **High** | Restricted origin to `ensure_root` / governance dispatch. | Confirm non-authorized origins cannot dispatch or bypass origin checks. |
| **SEC-04** | Unauthorized `mint_carbon_credit` | **High** | Enforced `ensure_root` requirement on minting extrinsic. | Test extrinsic calls with signed origins, mock accounts, and root privileges. |
| **SEC-05** | Liquidity Pool Bricking via Token Imbalance | **High** | Implemented minimum reserve constraints and safe state reset. | Attempt to brick pools via extreme token ratio transfers or zero-supply attacks. |
| **SEC-06** | Unbounded Vector Length Checks | **Medium** | Replaced unbounded `Vec` with Substrate `BoundedVec`. | Validate storage limit enforcement and gas/weight consumption bounded guarantees. |
| **SEC-07** | Unsafe Integer Casts (`as u128`) | **Medium** | Migrated numeric conversions to fallible `try_from` / `try_into`. | Ensure no loss of precision, truncation, or signedness bugs exist in type conversions. |
| **SEC-08** | Docker Container Privilege Escalation | **Medium** | Hardened container runtime: non-root user, read-only FS, `cap_drop ALL`. | Perform container breakout and privilege escalation tests on container images. |

---

## 6. Auditor Qualifications & Requirements

Proposing firms must satisfy the following baseline qualifications to be considered:

1. **Independence & Zero Conflict:** Total organizational and financial independence from the Verdis Chain core development team, founders, and investors. No prior involvement in drafting Verdis Chain runtime code.
2. **Substrate & Rust Expertise:** Demonstrated track record of auditing Substrate runtimes, FRAME pallets, and Rust core logic.
3. **Cryptographic & Economic Proficiency:** Proven ability to audit custom cryptographic implementations (secp256k1, ZK proofs) and decentralized economic models (DEX AMMs, tokenomics, staking).
4. **Transparent Methodology:** Documented audit process combining manual code inspection, static analysis, fuzz testing, and mathematical validation.
5. **Standardized Severity Classification:** Adoption of a standard vulnerability framework (e.g., CVSS v3.1 / OWASP / Substrate-specific severity matrix).
6. **Mandatory Remediation Re-Testing:** Inclusion of a secondary re-testing phase to evaluate developer fixes prior to final report freeze.
7. **Git Commitment Tagging:** Final public report must explicitly reference the exact git commit hash and tag audited and verified.

---

## 7. Expected Deliverables

The engaged audit firm will deliver the following artifacts:

1. **Initial Draft Audit Report:** Comprehensive document listing all discovered vulnerabilities, code smells, architecture risks, and severity ratings.
2. **Vulnerability Tracking Register:** Structured issue list detailing reproduction steps, code locations, impact analysis, and remediation recommendations.
3. **Remediation Review & Re-Test Report:** Updated report documenting the status of each fix (Verified Fixed, Partially Fixed, Acknowledged Risk, Unresolved).
4. **Final Security Audit Report:** Formal publication-ready report suitable for public release to the Verdis Chain community and institutional partners, tied to the release commit hash.
5. **Executive Summary Presentation:** Briefing session with the core engineering leadership to review findings and security architecture.

---

## 8. RFP Timeline & Engagement Milestones

The engagement is projected to run across a **4 to 6 week period** according to the following schedule:

```
+-----------------------------------------------------------------------------------+
| PHASE 1: RFP & Selection  | PHASE 2: Core Audit Review | PHASE 3: Fix & Re-Test   |
| Weeks 1 - 2               | Weeks 3 - 5                | Weeks 5 - 6              |
| RFP Submission & Award    | Deep Inspection & Draft    | Remediation & Final Report|
+-----------------------------------------------------------------------------------+
```

* **RFP Issuance Date:** August 14, 2026
* **Proposal Submission Deadline:** August 28, 2026
* **Auditor Selection & Scope Freeze:** September 4, 2026
* **Audit Execution Window:** September 7, 2026 – October 2, 2026 (4 weeks)
* **Remediation & Re-Testing Period:** October 5, 2026 – October 16, 2026 (2 weeks)
* **Final Report Publication:** October 20, 2026

---

## 9. Shortlist Evaluation Methodology

Submissions will be evaluated by the Verdis Chain Security Review Committee using a structured evaluation process. Firm selection will strictly adhere to objective performance standards:

* **Technical Competence:** Evidence of auditing complex Rust/Substrate runtimes, L1 consensus, and cryptoeconomic protocols.
* **Audit Rigor:** Quality of proposed methodology, combination of manual and automated tooling.
* **Team Depth:** Specific qualifications of the assigned senior audit personnel (CVs/resumes required).
* **Communication & Support:** Timeliness of daily/weekly updates and clear issue escalation paths.
* **Value & Schedule Alignment:** Ability to execute within the target 4-6 week timeframe at a competitive rate.

*(Note: Specific firm names will be evaluated objectively during proposal intake according to the AUDITOR_SCORECARD evaluation matrix).*

---

## 10. Evaluation Scoring Matrix Overview

Proposals will be evaluated out of 100 possible points across 10 distinct dimensions:

| Dimension | Weight | Primary Focus |
| :--- | :---: | :--- |
| **1. Blockchain & Substrate Experience** | 20% | Prior audit history with Substrate runtimes and Rust L1 nodes. |
| **2. Pallet & Smart Contract Audit Experience** | 15% | Depth in FRAME pallets, AMM DEX, tokenomics logic. |
| **3. Cryptography Experience** | 10% | Expertise in secp256k1, ZK proof compression, and VDFs. |
| **4. Economic & Game Theory Review** | 10% | AMM attack vectors, MEV, front-running, staking yield safety. |
| **5. Infrastructure Security** | 10% | Docker container hardening, systemd, nginx, network RPC. |
| **6. Methodology Quality** | 10% | Formal verification, fuzzing, static analysis, manual review depth. |
| **7. Remediation Re-Test Process** | 10% | Structure and rigor of the re-testing and fix verification phase. |
| **8. Delivery Timeline** | 5% | Execution speed within the target 4-6 week schedule. |
| **9. Cost & Commercial Terms** | 5% | Total cost clarity and value for engagement scope. |
| **10. Independence & Conflict Check** | 5% | Verified absence of developer or financial conflicts of interest. |

---

## 11. Confidentiality, NDA & Data Room Protocols

1. **Non-Disclosure Agreement (NDA):** A signed mutual NDA must be executed prior to granting access to private repositories, internal historical reports, and staging environments.
2. **Data Room Access:** Qualified auditors will receive read-only access to the Verdis Chain Audit Data Room containing full codebases, chain specs, and internal architecture documentation.
3. **Secure Communications:** All vulnerability disclosures during the audit must be transmitted via PGP-encrypted communication channels or secure private channels.

---

## 12. Conflict of Interest Declaration Form

Proposing firms must include the following attestation in their proposal response:

```
CONFLICT OF INTEREST ATTESTATION

We, [Auditing Firm Name], hereby certify that:
1. We maintain complete independence from Verdis Chain, its core contributors, and funding entities.
2. Neither our organization nor any assigned auditor has contributed code to the Verdis Chain repository.
3. We hold no financial position or material commercial interest that would bias our security findings.
4. We will immediately disclose any potential conflict of interest that arises during the engagement.

Authorized Signature: ___________________________
Title: __________________________________________
Date: ___________________________________________
```

---

## 13. Proposal Submission Instructions

Proposals must be submitted in PDF format to `security-rfp@verdischain.org` prior to the submission deadline. Submissions must include:
* Executive Summary & Firm Background
* Audit Approach & Methodology
* Assigned Auditor Profiles & CVs
* Case Studies of Past Substrate/Rust Audits
* Detailed Cost Breakdown & Timeline Commitment
* Completed Conflict of Interest Attestation

---
*End of Document — Verdis Chain Security Audit RFP*
