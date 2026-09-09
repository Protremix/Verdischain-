# External Audit Data Room & Documentation Index

**Project:** Verdis Chain  
**Document Type:** Audit Data Room Specification and Asset Inventory  
**Document Version:** 1.0  
**Target Repository:** `Protremix/Verdischain-`  
**Date:** August 2026  
**Access Classification:** Confidential — Authorized Audit Personnel Only  

---

## 1. Overview & Data Room Access Protocol

This Data Room serves as the centralized repository of source code, technical documentation, operational specifications, testing suites, and deployment assets prepared for the independent external security audit of Verdis Chain.

```
+-----------------------------------------------------------------------------------+
|                           AUDIT DATA ROOM ARCHITECTURE                            |
+-----------------------------------------------------------------------------------+
|  1. Source Code (Node, Runtime, 16 Pallets) |  2. Test Suite & Benchmarks (503)   |
|  3. Weight Files & Chain Specifications      |  4. Genesis Configuration           |
|  5. Deployment & Systemd Configurations     |  6. TX Relay v3 & Web Wallet        |
|  7. Verdis Client SDK                       |  8. Technical & Security Docs       |
|  9. Historical Audit Reports                | 10. CI/CD & Pipeline Configs        |
+-----------------------------------------------------------------------------------+
```

### Access Eligibility & Security Requirements
Access to the assets detailed in this document is strictly restricted to contracted audit firms upon completion of the following onboarding steps:
1. Executed Mutual Non-Disclosure Agreement (MNDA).
2. Registration of verified auditor PGP public keys for encrypted communication.
3. Submission of auditor IP addresses for RPC and SSH access whitelisting.

---

## 2. Complete Asset Inventory

### 2.1 On-Chain Source Code Repositories
* **GitHub Repository:** `Protremix/Verdischain-`
* **Substrate Runtime SLOC:** 1,901 SLOC (`/runtime`)
* **Substrate Node Subsystem SLOC:** 1,916 SLOC (`/node`)
* **Custom FRAME Pallets (16 Pallets located in `/pallets`):**
  1. `pallet-dpos` — Delegated Proof-of-Stake consensus, validator set management, slashing routines.
  2. `pallet-amm-dex` — Automated Market Maker exchange, liquidity pool math, swap executions.
  3. `pallet-eco` — Eco score tracking, sustainability metrics evaluation algorithms.
  4. `pallet-tokenomics` — Dynamic supply minting, token burning schedules, dynamic transaction fees.
  5. `pallet-vesting` — Vesting schedule enforcement, lockup release schedules.
  6. `pallet-presale` — Whitelisted presale contributions, cap checks, allocation delivery.
  7. `pallet-fungible-tokens` — Multi-asset token balance tracking and transfer approvals.
  8. `pallet-ibc` — Inter-Blockchain Communication state proofs, relay client handlers.
  9. `pallet-sealevel` — Parallel account execution locking and dependency mapping.
  10. `pallet-gulf-stream` — Leaderless transaction pool forwarding and validation logic.
  11. `pallet-storage` — Proof-of-Storage challenges, sector attestation verification.
  12. `pallet-turbine` — Block data shredding, erasure coding chunk validation.
  13. `pallet-zk-compression` — Zero-Knowledge state compression proof verification.
  14. `pallet-poh` — Proof-of-History VDF sequence verification.
  15. `pallet-circuit-breaker` — Automated circuit breakers, volume throttling.
  16. `pallet-address-lookup-tables` — Address alias indexing for transaction payload reduction.

---

### 2.2 Test Suite & Benchmarks
* **Automated Unit & Integration Tests:** 503 passing tests (`cargo test --all`).
* **Test Coverage:**
  * Pallet unit tests covering dispatchable success and error paths.
  * Mock runtime environment (`mock.rs`) for state simulation.
  * Edge-case regression tests for historical bug fixes.
* **Benchmark Files:** Dedicated `weights.rs` files for all 16 pallets in `/runtime/src/weights/`, generated using Substrate FRAME benchmarking CLI tool.

---

### 2.3 Chain Specs & Genesis Configurations
Located in `/node/chain-specs/`:
* `dev-spec.json`: Development chain spec for single-node local testing.
* `testnet-spec.json`: Testnet spec including multi-validator bootstrap nodes and pre-funded balances.
* `mainnet-spec.json`: Production spec candidate defining initial validator key sets, genesis balances, eco-treasury seed parameters, and governance origins.
* `genesis.rs`: Hardcoded genesis build logic validating genesis state invariant properties.

---

### 2.4 Infrastructure & Deployment Configurations
Located in `/deploy/` and `/infra/`:
* **Docker Configuration:**
  * `Dockerfile`: Multi-stage Rust build producing a minimal scratch/debian-slim production image. Hardened with non-root user (`uid 10001`), read-only root filesystem, and `cap_drop: ALL`.
  * `docker-compose.yml`: Local multi-validator container orchestration.
* **Nginx Reverse Proxy:** `nginx.conf` defining TLS 1.3 termination, rate-limiting directives, CORS policies, and WebSocket proxying for Substrate RPC (`ws://`).
* **Systemd Services (17 Service Units in `/infra/systemd/`):**
  * `verdis-node.service`: Main node service daemon.
  * `verdis-relay.service`: TX Relay service controller.
  * `verdis-monitor.service`: Node health and RPC monitoring agent.
  * 14 supporting system monitoring, telemetry, and log-forwarding service units.

---

### 2.5 Off-Chain Services & Web Clients
Located in `/off-chain/`:
* **TX Relay v3 (`/off-chain/tx-relay/`):**
  * Express/Node.js service managing off-chain transaction encryption.
  * Security Features: AES-256-GCM encryption, timestamp-based anti-replay verification, origin sanitization.
* **Non-Custodial Web Wallet (`/off-chain/web-wallet/`):**
  * React/TypeScript web client.
  * Cryptography: `@noble/secp256k1` library for client-side transaction signing and key generation.
  * Security Features: Local encrypted key storage, zero private-key network transmission.
* **Verdis Client SDK (`/sdks/js/`):** Client interface library wrapping Substrate RPC calls and custom pallet transactions.

---

### 2.6 Documentation Suite
Located in `/docs/`:
* **Whitepaper v2.1:** Full theoretical foundation, consensus mechanisms, and eco-scoring algorithms.
* **Tokenomics Specification:** Detailed formulas for validator rewards, inflation schedules, and liquidity incentives.
* **Architecture Design Document (ADD):** Comprehensive breakdown of parallel execution, state lock mechanisms, and cross-chain IBC verification.
* **Security & Operational Standard Operating Procedures (SOPs):** Node key management policies, validator operational guidelines, emergency circuit-breaker activation protocols.

---

### 2.7 Historical Audit & Remediation Logs
Located in `/security/historical-findings/`:
* **Internal Audit Report (July 2026):** Details the 8 initial internal security findings (SEC-01 through SEC-08).
* **Patch & Remediation Commit Diff Log:** Full code diffs verifying fixes for:
  * Division by zero in `remove_liquidity`
  * Arithmetic overflow in LP calculations (`checked_mul`)
  * Origin verification gaps in `update_green_score` and `mint_carbon_credit` (`ensure_root`)
  * Pool bricking prevention rules
  * Storage bounding with `BoundedVec`
  * Safe numeric casts (`try_from`)
  * Docker security policy enforcement

---

### 2.8 CI/CD & Pipeline Configurations
Located in `.github/workflows/`:
* `cargo-audit.yml`: Automated dependency security advisory checks.
* `clippy-lint.yml`: Static code analysis for Rust code quality and safety warnings.
* `test-suite.yml`: Automated test runner executing the 503 tests on every pull request.
* `benchmarking.yml`: Automated weight recalculation verification.

---

## 3. Access Instructions & Repository Details

Auditors will be granted read-only access via GitHub organization permissions and SSH key authentication.

### GitHub Access Setup
1. Submit the GitHub usernames of all participating audit engineers.
2. Accept the invitation to the private repository `Protremix/Verdischain-`.
3. Clone the target repository:
   ```bash
   git clone git@github.com:Protremix/Verdischain-.git
   cd Verdischain-
   ```

### Staging & Testnet RPC Access
* **Testnet RPC Endpoint:** `https://rpc.testnet.verdischain.org` (Requires IP Whitelisting)
* **WebSocket Endpoint:** `wss://rpc.testnet.verdischain.org/ws`
* **Telemetry Server:** `https://telemetry.verdischain.org`

---

## 4. Audit Scope Freeze & Target Commit Hash

To maintain consistency during the audit process, code changes will be frozen prior to audit commencement.

* **Target Branch:** `release/v1.0-audit`
* **Target Commit Hash:** `TBD` *(Commit hash will be locked and tagged on the day of engagement kickoff).*
* **Freeze Policy:** No new feature commits will be pushed to the audit branch during the review window. Emergency security patches required during the audit will be delivered in separate feature branches and logged transparently.

---

## 5. Security & Communication Protocols

### Primary Communication Channels
* **Urgent / High-Severity Vulnerabilities:** Immediate notification via PGP-encrypted email to `security-escalation@verdischain.org`.
* **Day-to-Day Technical Queries:** Private, dedicated communication channel (Matrix / Slack / Telegram) established between auditor leads and core developers.

### Emergency Response Escrow
If a Critical vulnerability is discovered that impacts live testnet funds or chain stability, auditors should follow the Emergency Escalation Procedure outlined in `/docs/SECURITY_ESCALATION.md`.

---

## 6. Issue Tracking & Remediation Process

Auditors should log findings continuously using the provided Issue Tracking Sheet template:

```
+-----------------------------------------------------------------------------------+
|                            FINDING TEMPLATE STRUCTURE                             |
+-----------------------------------------------------------------------------------+
| Finding ID    : VERDIS-AUDIT-2026-0XX                                             |
| Title         : Short descriptive title                                           |
| Severity      : Critical / High / Medium / Low / Informational                    |
| Component     : Affected Pallet / Node / Relay / Wallet component                 |
| Location      : File path and line numbers                                        |
| Description   : Detailed vulnerability walkthrough                                |
| Reproduction  : Step-by-step reproduction guide or test case                      |
| Impact        : Potential exploit consequences                                    |
| Recommendation: Suggested code patch or architectural adjustment                  |
+-----------------------------------------------------------------------------------+
```

---
*End of Document — Verdis Chain Audit Data Room Specification*
