# Verdis Chain — Request for Proposal (RFP): Independent Security Audit

**Document ID:** ARCH-008  
**Date:** August 14, 2026  
**Project:** Verdis Chain (Substrate / Layer-1 Blockchain)  
**Target Release:** Mainnet Launch (2026 Q3/Q4)  
**Status:** Active RFP  

---

## 1. Audit Scope

The independent security audit for Verdis Chain covers the entire protocol stack, including node binaries, runtime logic, custom pallets, frontend web wallet applications, transaction relay middleware, and deployment/infrastructure configurations.

### Scope Summary Metrics
* **Runtime:** `runtime/src/lib.rs` (1,901 SLOC) + 16 Custom Pallets
* **Node Binary:** `node/src/*.rs` (1,916 SLOC across `chain_spec.rs`, `main.rs`, `rpc.rs`, `service.rs`)
* **Test Suite:** 485 automated workspace test cases + unit & integration benchmarks
* **Frontend Wallet & Web Interface:** Web wallet JS & HTML (`web/wallet/`, `web/wallet.html`, `web/js/verdis.js`)
* **Middleware & Services:** Transaction Relay (`tx_relay_v3.py`, encrypted relay logic)

### Detailed Subsystem Breakdown

1. **Node Implementation**
   - Consensus engine integration (`BABE`, `GRANDPA`, custom `DPoS`)
   - Networking layer (p2p stream handling, peer discovery, message routing)
   - RPC endpoints (`node/src/rpc.rs`) and node service initialization (`node/src/service.rs`)

2. **Runtime & Pallets (All 16 Custom Pallets)**
   - `runtime/src/lib.rs`: Pallet wiring, origin definitions, executive dispatch, call indexes
   - `pallets/address-lookup-tables`: Address lookup compression & account batching
   - `pallets/amm-dex`: Automated Market Maker (swaps, liquidity provision, constant-product math, fee calculations, flash loan hooks, overflow prevention)
   - `pallets/circuit-breaker`: Volatility caps, volume thresholds, emergency pause triggers
   - `pallets/dpos`: Validator election, stake delegation, reward distribution, slashing rules
   - `pallets/eco`: Carbon/energy metric tracking and validator incentive logic
   - `pallets/fungible-tokens`: Multi-asset token issuance, balance management, transfers, approvals
   - `pallets/gulf-stream`: Mempool-less transaction forwarding and block inclusion logic
   - `pallets/ibc`: Inter-blockchain communication protocols and cross-chain packet routing
   - `pallets/poh`: Proof-of-History timestamp sequence generator and verification
   - `pallets/presale`: Token presale contribution handling, allocations, cap enforcement
   - `pallets/sealevel`: Parallel transaction execution and conflict detection logic
   - `pallets/storage`: Decentralized proof-of-storage and data availability challenge mechanisms
   - `pallets/tokenomics`: Supply control, dynamic inflation/deflation, fee burn engine
   - `pallets/turbine`: Block propagation tree routing and sharded block distribution
   - `pallets/vesting`: Token unlock schedules, cliff enforcement, linear distribution rules
   - `pallets/zk-compression`: Zero-knowledge transaction compression and proof verification

3. **Consensus Mechanisms**
   - Integration of BABE block production, GRANDPA finality gadget, and DPoS validator management
   - Slot timing, epoch transitions, validator set rotation, and equivocation handling

4. **Automated Market Maker DEX (`pallet-amm-dex`)**
   - Token swaps, liquidity pool creation, fee collection
   - Math precision (fixed-point arithmetic, overflow/underflow protection)
   - Flash loan security (atomic execution, single-transaction repayment verification, arbitrage protection)

5. **Web Wallet & Client Applications (`web/wallet/`)**
   - Client-side key management (mnemonic generation, key derivation via secp256k1/sr25519)
   - Extrinsic signing and transaction construction
   - Browser security controls: Content Security Policy (CSP), XSS defenses, CORS, origin isolation

6. **Transaction Relay Middleware (`tx_relay_v3.py`)**
   - AES-256-GCM transport encryption between client and relay node
   - Authentication, HMAC signature verification, nonce anti-replay guarantees
   - Rate limiting, DoS protection, and raw extrinsic pass-through validation

7. **APIs and Communication Channels**
   - REST API endpoints (`/api/v1/...`, faucet, relay endpoints)
   - Substrate RPC & WebSocket endpoints (`ws://` and `wss://` RPC interface)
   - Input validation, serialization/deserialization, error handling

8. **Deployment & Infrastructure**
   - Containerization (`Docker`, `Docker Compose`)
   - Reverse proxy (`nginx` configurations, SSL/TLS setup)
   - Process supervision (`systemd` service units)
   - Network security (ufw/firewall rules, exposed ports, SSH hardening)

9. **Tokenomics & Economic Mechanics**
   - Max total supply invariants enforcement (100,000,000 VERD hard cap)
   - Vesting schedules, cliff releases, presale allocations
   - Staking yield calculations and slashing percentage bounds

10. **Governance & Multi-Sig Controls**
    - Technical Council and Democracy referendum dispatch
    - Treasury multisig threshold management and fund release workflows

---

## 2. Repository & Commit Freeze Procedure

To guarantee audit determinism and audit report integrity, Verdis Chain strictly adheres to the following freeze procedure:

1. **Tag the Audit Commit:**
   - Prior to audit kickoff, the repository commit will be tagged: `git tag audit-freeze-2026-08`.
   - All auditing firms must perform code reviews strictly against this frozen commit tag.

2. **No Code Changes During Audit:**
   - No changes to audited code during the active audit period are permitted on the master/release branch.
   - Any emergency security patches or test adjustments during the audit phase must be staged on an isolated branch (`audit-staging-patch`).

3. **Remediation Tracker:**
   - All findings identified in auditor preliminary reports will be systematically tracked in `docs/ARCHITECTURE_REMEDIATION_TRACKER.md`.

4. **Re-Audit Post-Audit Changes:**
   - Re-audit is strictly required for any code changes post-audit prior to mainnet deployment sign-off.

---

## 3. Evidence & Data-Room Checklist

The following items are provided in the repository data room for auditor inspection:

- [x] **Architecture Overview Document:** `docs/ARCHITECTURE.md`
- [x] **Pallet-by-Pallet Documentation:** `docs/RUNTIME.md` and pallet specifications
- [x] **Chain Specifications:** `node/src/chain_spec.rs` (Testnet and Mainnet specs)
- [x] **Genesis Configuration:** `docs/GENESIS_CEREMONY.md` & `docs/GENESIS_CEREMONY_PLAN.md`
- [x] **All Test Results:** Output logs from 485 workspace unit/integration tests
- [x] **Previous Security Audit Reports:** `docs/AUDIT_REPORT.md`, `docs/security-audit-phase2.md`, `docs/whitepaper_code_consistency_audit.md`
- [x] **Dependency List with Versions:** `docs/DEPENDENCY_INVENTORY.md` and `Cargo.lock`
- [x] **Deployment Configuration:** `docs/DEPLOYMENT.md`, `docs/OPERATOR_GUIDE.md`, `docs/production-infra-checklist.md`
- [x] **Threat Model:** `docs/TX_RELAY_THREAT_MODEL.md`

---

## 4. Auditor Questions

Prospective auditing firms must answer the following technical and operational questions in their RFP proposal:

1. **Substrate Experience:** What is your experience auditing Substrate-based blockchains and FRAME pallets?
2. **Consensus Review Methodology:** What is your methodology for consensus mechanism review (BABE/GRANDPA/DPoS integration and slot timing)?
3. **Economic/DEX Testing:** How do you test for economic and flash loan attacks on AMM DEX pallets (slippage, price oracle manipulation, sandwiching)?
4. **Rust Analysis Tools:** What tools do you use for Rust static analysis (e.g., Clippy, Cargo Audit, MIRI, custom AST analyzers)?
5. **Infrastructure Security:** Do you review deployment/infrastructure security (Docker, Nginx, systemd, firewall, RPC/WS exposed interfaces)?
6. **Timeline & Pricing:** What is your proposed timeline and cost structure for this scope?
7. **Remediation Support:** Do you provide remediation support and re-testing post-audit included in the engagement?

---

## 5. Scoring Matrix

The security audit evaluation and mainnet release criteria are governed by the following matrix:

| Category | Weight | Pass Criteria |
|---------|--------|---------------|
| Consensus/Validator | 20% | 0 critical, 0 high |
| Token/DEX | 15% | 0 critical, 0 high |
| Wallet/Key Management | 15% | 0 critical, 0 high |
| Governance/Treasury | 10% | 0 critical |
| Infrastructure | 10% | 0 critical |
| TX Relay/API | 10% | 0 critical |
| Tokenomics/Vesting | 10% | 0 critical |
| Documentation | 5% | Complete and accurate |
| Supply Chain | 5% | All deps audited |

---

## 6. Remediation Tracker

All findings discovered during the independent security audit must be logged, assigned, and tracked to resolution in:

👉 **`docs/ARCHITECTURE_REMEDIATION_TRACKER.md`**

No issue marked Critical or High may remain open at the conclusion of the audit remediation period prior to mainnet genesis.
