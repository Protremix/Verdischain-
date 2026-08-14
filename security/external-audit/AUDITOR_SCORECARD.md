# Auditor Selection Scorecard & Evaluation Matrix

**Project:** Verdis Chain — Independent External Security Audit  
**Document Type:** Selection Tool and Evaluation Framework  
**Document Version:** 1.0  
**Date:** August 2026  
**Status:** Confidential — Internal Use Only  

---

## 1. Overview and Purpose

This document outlines the structured scoring criteria, evaluation process, and decision matrix utilized by the Verdis Chain Security Review Committee to objectively select an independent external security auditing firm. 

The evaluation framework ensures that the selected firm is chosen based on technical merit, relevant framework expertise, rigor of methodology, cost efficiency, and absolute independence, avoiding any conflict of interest.

---

## 2. Weighted Scoring Criteria (10 Dimensions)

Each proposal is evaluated across 10 distinct dimensions, with weighted scores calculated to provide a total rating out of 10.0.

```
+-----------------------------------------------------------------------------------+
|                        EVALUATION DIMENSIONS AND WEIGHTS                          |
+-----------------------------------------------------------------------------------+
| 1. Substrate Experience (20%)       | 2. Pallet/Contract Experience (15%)         |
| 3. Cryptography Experience (10%)    | 4. Economic/Game Theory Review (10%)        |
| 5. Infrastructure Security (10%)    | 6. Methodology Quality (10%)                |
| 7. Remediation Re-Test (10%)        | 8. Timeline Commitment (5%)                 |
| 9. Cost & Commercial Value (5%)     | 10. Independence & Conflict Check (5%)      |
+-----------------------------------------------------------------------------------+
```

---

### Dimension 1: Blockchain & Substrate Experience (Weight: 20%)
Evaluation of the firm’s track record in auditing Layer-1 Substrate node structures, Rust system components, runtime configurations, consensus logic, and node networking.
* **Score 9-10 (Superior):** Extensive public registry of completed Substrate runtime and node audits. Deep contribution history to open-source Substrate tools. Assigned auditors possess >5 years of Rust and blockchain engineering experience.
* **Score 7-8 (Strong):** Multiple published audits of Substrate runtimes. Assigned auditors have audited Substrate-based L1 platforms.
* **Score 4-6 (Acceptable):** Proven experience auditing general Rust code and other non-Substrate Layer-1 protocols.
* **Score 0-3 (Poor):** No experience with Rust-based or Substrate-based blockchains.
* **Evidence Required:** Links to published Substrate audit reports, resumes of assigned lead Substrate engineers.

---

### Dimension 2: Smart Contract & Pallet Audit Experience (Weight: 15%)
Evaluation of custom FRAME pallet code evaluation capability. Specifically, looking for experience with pallets implementing complex State Transition Functions (STF) such as AMM DEXs, tokenomics, vesting schedules, and multi-signature operations.
* **Score 9-10 (Superior):** Documented history auditing bespoke AMM protocols, custom tokenomics minting schedules, and parallel execution runtimes. Lead engineers have authored custom FRAME pallets.
* **Score 7-8 (Strong):** Audited several FRAME pallets or EVM/WASM smart contract implementations of similar functional complexity.
* **Score 4-6 (Acceptable):** Audited basic ERC-20, ERC-721 token mechanics or standard Uniswap V2 forks.
* **Score 0-3 (Poor):** Missing core smart contract or state transition system audit portfolio.
* **Evidence Required:** Past reports covering AMM or custom asset-registry logic.

---

### Dimension 3: Cryptography Experience (Weight: 10%)
Expertise in validating advanced cryptographic schemes, including custom Elliptic Curve implementations (secp256k1, sr25519, ed25519), Zero-Knowledge proof structures, and verifiable delay functions (VDFs).
* **Score 9-10 (Superior):** Specialized cryptography audit team. Proven track record validating ZK-rollups, state compression math, and VDF performance.
* **Score 7-8 (Strong):** General cryptographic auditing experience, including elliptic curve mechanics and threshold cryptography.
* **Score 4-6 (Acceptable):** Competent in checking standard signature verification and hashing algorithms.
* **Score 0-3 (Poor):** No demonstrated capabilities in reviewing non-standard or custom cryptographic modules.
* **Evidence Required:** Portfolio of cryptographic library audits, specialist staff credentials.

---

### Dimension 4: Economic & Game Theory Review (Weight: 10%)
Ability to audit tokenomics, incentive design, slashing models, sandwich attacks, MEV protection, front-running, price manipulation vectors, and potential liquidity drain scenarios.
* **Score 9-10 (Superior):** Includes formal mathematical modeling, simulation runs (e.g., CADCAD), and economic vulnerability verification (price manipulation, oracle exploits).
* **Score 7-8 (Strong):** Detailed manual review of game-theoretic incentive structures and attack vector checks.
* **Score 4-6 (Acceptable):** Standard inspection of logic paths for front-running and flash loan vectors.
* **Score 0-3 (Poor):** No economic or incentive-security audit capabilities.
* **Evidence Required:** Verification of math validation frameworks in previous reports.

---

### Dimension 5: Infrastructure & System Security (Weight: 10%)
Expertise in evaluating deployment hardening, secure service orchestrations (`systemd`), web service reverse proxies (`nginx`), secure transaction relay servers, container permissions, and network APIs.
* **Score 9-10 (Superior):** Certified Kubernetes Security Specialist (CKS) / OSCP staff. Deep competence in container jailbreaking, secure reverse proxy configuration, and AES encryption.
* **Score 7-8 (Strong):** Strong history of reviewing Docker environments, network exposure, and RPC endpoints.
* **Score 4-6 (Acceptable):** Basic system configuration review capabilities.
* **Score 0-3 (Poor):** Audit scope limited strictly to code level; no infrastructure/deployment security capabilities.
* **Evidence Required:** Sample audits of network proxies, container infrastructure, or DevOps setups.

---

### Dimension 6: Methodology Quality & Tooling (Weight: 10%)
Depth and rigor of the audit framework, combining manual reviews with static analysis, custom fuzzers, dynamic binary instrumentation, and mathematical proof validation.
* **Score 9-10 (Superior):** Custom automated Rust/Substrate fuzzing suites. Structured methodology documenting manual, static, and dynamic phases in detail.
* **Score 7-8 (Strong):** Structured manual review supplemented by common open-source static analyzers (e.g., Slither, Securify, Clippy, cargo-audit, Mythril).
* **Score 4-6 (Acceptable):** Manual review with basic compiler/clippy warnings check.
* **Score 0-3 (Poor):** Unstructured manual review with no defined analysis pipeline.
* **Evidence Required:** Methodology section in the RFP proposal; details on internal tooling.

---

### Dimension 7: Remediation & Re-Testing Process (Weight: 10%)
Evaluation of the firm's structure, rigor, and timeline commitment for validating developer code fixes before finalizing the public report.
* **Score 9-10 (Superior):** Full re-evaluation of modified code. Regression testing suite provided. Direct GitHub PR review and approval workflow.
* **Score 7-8 (Strong):** Dedicated second review phase (1-2 weeks) with direct communication with devs and a formal remediation report.
* **Score 4-6 (Acceptable):** Basic re-check of code patches without dedicated regressions tests.
* **Score 0-3 (Poor):** No re-testing offered, or re-testing billed separately as an add-on.
* **Evidence Required:** Standard contract draft or methodology section detailing re-test conditions.

---

### Dimension 8: Timeline Commitment (Weight: 5%)
Ability to complete the audit within the target window of 4-6 weeks without sacrificing depth.
* **Score 9-10 (Superior):** Commits to start date within 10 days of signing. Provides weekly milestone reports. Guarantees 4-5 week full-cycle delivery.
* **Score 7-8 (Strong):** Commits to start date within 2-3 weeks. Delivers within a strict 6-week timeframe.
* **Score 4-6 (Acceptable):** Flexible start date; delivery within 6-8 weeks.
* **Score 0-3 (Poor):** Lead times exceed 6 weeks for commencement, or execution time exceeds 8 weeks.
* **Evidence Required:** Draft schedule with milestones.

---

### Dimension 9: Cost & Commercial Value (Weight: 5%)
Clarity, fairness, and overall value of the pricing structure relative to the depth of the audit.
* **Score 9-10 (Superior):** Highly transparent pricing. Fixed cost covering both core audit and remediation re-test. High ratio of expert-hours per dollar.
* **Score 7-8 (Strong):** Reasonable fixed fee but with structured add-ons (e.g., hourly rate for additional re-test hours).
* **Score 4-6 (Acceptable):** High pricing but justifiable by brand reputation.
* **Score 0-3 (Poor):** Extremely high pricing without clear breakdown, or vague time-and-materials quotes with high risk of cost overrun.
* **Evidence Required:** Commercial proposal and itemized cost schedule.

---

### Dimension 10: Independence & Conflict Check (Weight: 5%)
Absolute independence from Verdis Chain developers, founders, and core entities.
* **Score 9-10 (Superior):** Zero prior association. Signed non-conflict attestation provided. No financial interest or holding of Verdis Chain related ecosystem tokens.
* **Score 7-8 (Strong):** Minor past association (e.g., participated in a general hackathon or general consulting), but zero direct development involvement.
* **Score 4-6 (Acceptable):** Has performed advisory consulting for a partner project, but zero conflict with current codebase.
* **Score 0-3 (Poor):** Previous involvement in drafting code for Verdis Chain or close personal/financial ties to core contributors.
* **Evidence Required:** Completed Conflict of Interest Declaration.

---

## 3. Score Sheet Template

This scoring sheet must be completed individually by each member of the selection committee for every proposing firm.

### Candidate Information
* **Proposing Auditing Firm Name:** ________________________
* **Date of Evaluation:** ________________________
* **Evaluator Name/ID:** ________________________

### Individual Score Sheet

| Dimension | Raw Score (0-10) [A] | Weight [B] | Weighted Score [A × B] | Evaluator Notes / Findings |
| :--- | :---: | :---: | :---: | :--- |
| 1. Blockchain / Substrate Exp | | 0.20 | | |
| 2. Pallet / Contract Exp | | 0.15 | | |
| 3. Cryptography Experience | | 0.10 | | |
| 4. Economic / Game Theory | | 0.10 | | |
| 5. Infrastructure Security | | 0.10 | | |
| 6. Methodology Quality | | 0.10 | | |
| 7. Remediation Re-test Process | | 0.10 | | |
| 8. Timeline Commitment | | 0.05 | | |
| 9. Cost & Commercial Value | | 0.05 | | |
| 10. Independence / Non-Conflict | | 0.05 | | |
| **TOTAL SCORE (out of 10.0)** | — | **1.00** | | |

*Calculation Formula:*  
$$	ext{Total Score} = \sum_{i=1}^{10} (	ext{Raw Score}_i 	imes 	ext{Weight}_i)$$

---

## 4. Auditor Comparison Template (3+ Candidates)

This comparison table aggregates the average evaluation scores from the committee to rank the top three shortlisted candidates.

*(Note: Candidates listed below represent illustrative profiles for comparative evaluation prior to selection decision).*

| Dimension | Weight | Candidate A (Substrate Specialist) | Candidate B (Tier-1 Global Firm) | Candidate C (Boutique Security Firm) |
| :--- | :---: | :---: | :---: | :---: |
| **1. Substrate Experience** | 20% | 10.0 | 8.0 | 6.0 |
| **2. Pallet / Contract Exp** | 15% | 9.0 | 8.0 | 7.0 |
| **3. Cryptography Experience** | 10% | 8.0 | 9.0 | 5.0 |
| **4. Economic / Game Theory** | 10% | 9.0 | 7.0 | 6.0 |
| **5. Infrastructure Security** | 10% | 7.0 | 9.0 | 8.0 |
| **6. Methodology Quality** | 10% | 8.0 | 8.0 | 7.0 |
| **7. Remediation Re-test** | 10% | 9.0 | 8.0 | 7.0 |
| **8. Timeline Commitment** | 5% | 8.0 | 7.0 | 9.0 |
| **9. Cost & Commercial Value** | 5% | 8.0 | 5.0 | 10.0 |
| **10. Independence / Conflict**| 5% | 10.0 | 10.0 | 10.0 |
| **Weighted Score Sum** | **100%** | **8.85** | **7.95** | **6.85** |
| **Rank** | — | **1** | **2** | **3** |

---

## 5. Decision Matrix & Selection Workflow

To ensure a high standard of security, the final selection must follow a strict policy framework:

### 5.1 Minimum Qualification Thresholds
A candidate must satisfy the following minimum scores to be eligible for selection:
* **Minimum Substrate Experience Score:** 7.0 / 10.0
* **Minimum Independence / Non-Conflict Score:** 9.0 / 10.0
* **Minimum Total Weighted Score:** 7.5 / 10.0

### 5.2 Scenario-Based Decision Matrix

```
+-------------------------------------------------------------------------------+
|                        DECISION PATHWAY MATRIX                                |
+-------------------------------------------------------------------------------+
| Scenario                           | Recommendation / Action                  |
+------------------------------------+------------------------------------------+
| Highest Weighted Score >= 8.5      | Award contract directly.                 |
| Close scores (within 0.3 delta)    | Host interview / code review round.      |
| Top firm fails Substrate threshold | Reject and move to 2nd rank candidate.   |
| All candidates fail minimum score  | Revise RFP and reopen submissions.       |
+-------------------------------------------------------------------------------+
```

### 5.3 Approval Workflow
1. **Proposal Intake:** RFP responses are registered and logged by the security coordinator.
2. **Technical Screening:** Internal engineering team reviews technical case studies to filter out non-Substrate firms.
3. **Scorecard Evaluation:** Security Review Committee members score shortlisted candidates.
4. **Weighted Score Consolidation:** Scores are averaged and compiled into the comparison template.
5. **Interview Round (Optional):** Conducted if the top two candidates are within a 0.3 score margin.
6. **Selection Recommendation:** Committee generates a recommendation memorandum.
7. **Executive Sign-off:** Sign-off by the CTO and Chief of Security to release budget and issue the engagement contract.

---
*End of Document — Auditor Selection Scorecard*
