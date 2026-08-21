# Verdis Chain — Dependency Security Policy & Framework

**Document Version:** 1.0.0  
**Effective Date:** August 2026  
**Target Architecture:** Verdis Chain Substrate Node, Pallets, & Supporting Tooling  
**Compliance Standard:** Verdis Chain Engineering Constitution (Article 11 — Dependency Security)

---

## 1. Executive Summary & Scope

Verdis Chain relies on a robust open-source ecosystem spanning Rust core primitives, Substrate FRAME pallets, cryptographic libraries, and Python/JavaScript client SDKs. Maintaining strict security over upstream software dependencies is paramount to preventing supply chain attacks, cryptographic vulnerabilities, and node desynchronization risks.

This document establishes the official **Dependency Security Policy** for Verdis Chain. It governs version tracking, lockfile management, continuous vulnerability monitoring, patch management cadences, and mandatory review checklists for all code introduced into the repository.

### Scope
This policy applies to all dependencies across the repository:
- **Rust Core & Pallets:** Cargo crates, Substrate FRAME dependencies, `sp-*` and `pallet-*` libraries, cryptographic implementations.
- **Python Infrastructure:** `substrate-interface`, `scalecodec`, REST API dependencies, tx relays, and automated test scripts.
- **Node/JavaScript Utilities:** Polkadot JS bundles, web explorer UI, and webhooks.
- **CI/CD & Operational Tooling:** GitHub Actions, Docker base images, and deployment scripts.

---

## 2. Key Dependencies & Technical Stack

Verdis Chain categorizes its core third-party dependencies into six mission-critical technology pillars:

```
+---------------------------------------------------------------------------------+
|                                 VERDIS CHAIN                                    |
+---------------------------------------------------------------------------------+
| 1. Substrate / Polkadot SDK  | Core FRAME runtime, consensus (BABE/GRANDPA), primitives |
| 2. Scale Codec               | parity-scale-codec (Rust) & scalecodec (Python)          |
| 3. Cryptographic Signatures  | sr25519 / sr25519-dna, schnorrkel, ed25519               |
| 4. Secp256k1 & EVM Cryptography| libsecp256k1, secp256k1 ECDSA bindings                   |
| 5. Hashing & Primitives      | sha2, sha3, blake2, keccak-256                            |
| 6. Client & RPC Interfaces   | substrate-interface (Python SDK), Polkadot JS API         |
+---------------------------------------------------------------------------------+
```

### Dependency Deep-Dive

#### 1. Substrate / Polkadot SDK
* **Purpose:** Core runtime infrastructure, storage models, state transition logic, consensus engines (`sp-consensus-babe`, `sp-consensus-grandpa`), and system primitives (`sp-core`, `sp-runtime`, `sp-io`, `sp-std`).
* **Rust Packages:** `frame-support` (v48.0.0), `frame-system` (v48.0.0), `sp-core` (v43.0.0), `sp-runtime` (v48.0.0), `sp-io` (v48.0.0).
* **Risk Profile:** **Critical**. Vulnerabilities in consensus or FRAME storage can cause chain halts, state corruption, or remote consensus divergence.

#### 2. Scale Codec (`parity-scale-codec` & `scalecodec`)
* **Purpose:** Lightweight, bit-efficient serialization and deserialization for all Substrate types, storage keys, extrinsics, and RPC payloads.
* **Rust Package:** `parity-scale-codec` (v3.7.5, `codec` alias).
* **Python Package:** `scalecodec` (for off-chain transaction relays, indexing, governance API).
* **Risk Profile:** **Critical**. Parsing vulnerabilities or buffer overflows in serialization decoders can be exploited via malicious extrinsic payloads to crash validator nodes (DoS).

#### 3. Cryptographic Signatures (`sr25519` / `sr25519-dna`)
* **Purpose:** Schnorr signatures over Ristretto25519 curves (`schnorrkel`) used for transaction signing, session keys, BABE block production, and GRANDPA finality voting.
* **Rust Package:** `sp-core` / `schnorrkel` / `sr25519-dna` bindings.
* **Kotlin/Mobile Package:** `Sr25519Service.kt` native bindings.
* **Risk Profile:** **Critical**. Weaknesses in key generation, nonces, or signature verification allow key theft, transaction forgery, or validator impersonation.

#### 4. Elliptic Curve Cryptography (`libsecp256k1`)
* **Purpose:** Secp256k1 ECDSA signature verification for Ethereum-compatible operations, EVM address derivation, cross-chain bridge validation, and presale claims.
* **Rust Package:** `libsecp256k1` / `k256` / `secp256k1`.
* **Risk Profile:** **High**. Non-constant-time scalar multiplication or signature malleability could expose private key bits or enable replay attacks.

#### 5. Cryptographic Hash Functions (`sha2` / `sha3` / `blake2`)
* **Purpose:** Digest generation for block headers, Proof-of-History (PoH) sequence generation, state tries (Blake2b-256, Twox128), and transaction hashing (SHA-256, Keccak-256, SHA-3).
* **Rust Packages:** `sha2`, `sha3`, `blake2`, `tiny-keccak`.
* **Risk Profile:** **Critical**. Hash collisions or implementation bugs directly invalidate consensus proofs and block integrity.

#### 6. Client & RPC Interfaces (`substrate-interface`)
* **Purpose:** Python client library facilitating RPC connection, extrinsic construction, metadata parsing, keypair management, and SS58 address conversion.
* **Python Package:** `substrate-interface` (>= 1.7.0).
* **Risk Profile:** **Medium**. Client-side vulnerabilities affect relayers, automated tools, and monitoring infrastructure, but do not directly compromise on-chain consensus.

---

### Key Dependency Inventory Table

| Component / Crate | Ecosystem | Version / Pin | Purpose in Verdis Chain | Risk Level |
|-------------------|-----------|---------------|-------------------------|------------|
| `parity-scale-codec` | Rust | `3.7.5` | SCALE serialization for runtime & pallets | **Critical** |
| `frame-support` | Rust | `48.0.0` | Substrate FRAME macros & storage definitions | **Critical** |
| `frame-system` | Rust | `48.0.0` | Base system extrinsics, accounts, nonces | **Critical** |
| `sp-core` | Rust | `43.0.0` | Cryptographic primitives (sr25519, ed25519, secp256k1) | **Critical** |
| `sp-runtime` | Rust | `48.0.0` | Consensus primitives, multi-signatures, weights | **Critical** |
| `sp-consensus-babe` | Rust | `0.49.0` | Block authoring consensus engine | **Critical** |
| `sp-consensus-grandpa` | Rust | `30.0.0` | Block finality gadget primitives | **Critical** |
| `libsecp256k1` | Rust | `0.7.x` | Secp256k1 ECDSA signatures (EVM compatibility) | **High** |
| `sha2` / `sha3` | Rust | `0.10.x` | Standard cryptographic hashing algorithms | **High** |
| `substrate-interface` | Python | `>=1.7.0` | Off-chain relayer, test harness, governance API | **Medium** |
| `scalecodec` | Rust/Python| System / Lib | SCALE decoding for off-chain services & tooling | **High** |
| `serde` / `serde_json` | Rust | `1.0.x` | JSON serialization for node RPC & genesis specs | **Medium** |

---

## 3. Version Tracking & Lockfile Enforcement

To ensure strict reproducible builds and eliminate supply chain poisoning via transitive updates, Verdis Chain enforces rigorous version tracking rules.

### Lockfile Management Rules
1. **Repository Enforcement:** `Cargo.lock` must be committed to git and tracked under strict version control.
2. **Deterministic Builds:** All release builds and CI checks must execute using `--locked` (e.g., `cargo check --locked`, `cargo test --locked`, `cargo build --release --locked`).
3. **No Wildcard Pinning:** Wildcard version specifications (e.g., `*`, `^`, `~`) in production `Cargo.toml` or `requirements.txt` files are prohibited for critical dependencies.
4. **Substrate Version Alignment:** All Substrate crates (`sp-*`, `pallet-*`, `frame-*`) must belong to the exact same release family (e.g., Polkadot SDK / Substrate frame version set) to avoid runtime type layout mismatches.

---

## 4. Vulnerability Monitoring Process

Verdis Chain implements a multi-layered, automated vulnerability detection and triage process.

```
+-----------------------------------------------------------------------------------+
|                        VULNERABILITY DETECTION & TRIAGE                           |
+-----------------------------------------------------------------------------------+
|  1. Daily Automated CI Scan (cargo audit, cargo deny, pip-audit, gitleaks)       |
|  2. Upstream Advisory Tracking (RustSec, Parity Security Bulletins, PyPI Advisory) |
|  3. Severity Categorization (P0 Critical, P1 High, P2 Medium, P3 Low)             |
|  4. Triage & Hotfix SLA Enforcement                                               |
+-----------------------------------------------------------------------------------+
```

### Automated Scanning Tools in CI Pipeline

* **`cargo audit`:** Scans `Cargo.lock` daily against the official [RustSec Advisory Database](https://rustsec.org).
* **`cargo deny`:** Enforces dependency licenses, checks for duplicate crates, and blocks unverified git sources.
* **`pip-audit` / `safety`:** Scans Python requirements against known PyPI security vulnerabilities.
* **`gitleaks`:** Scans codebase and history to prevent accidental committing of API keys, private keys, or seed phrases.

### Severity Levels & Response SLAs

| Severity | Definition / Impact | SLA Response Time | Action Required |
|----------|---------------------|-------------------|-----------------|
| **P0 — Critical** | Remote Code Execution (RCE), consensus break, loss of funds, signature bypass, or denial of service in production dependencies. | **< 24 Hours** | Immediate emergency patch release; pause deployments; invoke emergency response protocol. |
| **P1 — High** | Denial of Service in non-consensus RPC, memory leak in core pallet, or severe transitive vulnerability. | **< 72 Hours** | Expedited hotfix branch; patch release; trigger full regression test suite. |
| **P2 — Medium** | Local privilege escalation, moderate vulnerability in build/CI tools or off-chain scripts. | **< 7 Days** | Scheduled minor release fix; update lockfile during regular development cycle. |
| **P3 — Low** | Informational advisories, minor unmaintained non-runtime dependencies, low-impact dev tools. | **Next Cycle** | Triage during monthly dependency review. |

---

## 5. Update Cadence & Lifecycle Management

Verdis Chain balances stability with proactive security updates across three release cadences:

### Cadence Schedule

1. **Emergency Security Hotfixes (Ad-hoc / < 24 Hours):**
   * Triggered immediately upon detection of P0/P1 advisories in any production crate or dependency.
   * Minimal code delta: only bump affected crate version or apply patch.
   * Requires mandatory testing via local dev chain, unit tests, and testnet deployment before mainnet application.

2. **Monthly Dependency Review & Patch Bumps (Every 30 Days):**
   * Review all non-critical patch updates (`cargo update`).
   * Audit unused dependencies (`cargo machete`).
   * Verify cargo dependency tree for duplicate crates (`cargo tree -d`).

3. **Quarterly Substrate / Polkadot SDK Upgrades (Every 90 Days):**
   * Major upgrade of Substrate/Polkadot SDK framework dependencies.
   * Requires full runtime benchmark recalculation (`frame-benchmarking`).
   * Mandatory full test suite verification across all 16 pallets (446+ unit tests).
   * Deployment to Verdis Testnet for minimum 14-day bake period prior to Mainnet runtime upgrade proposal.

---

## 6. Pre-Merge Dependency Review Checklist

Before any PR modifying `Cargo.toml`, `Cargo.lock`, `requirements.txt`, or project dependencies is merged, the PR reviewer must complete the following checklist:

- [ ] **1. Lockfile Updated & Locked:** `Cargo.lock` is updated correctly and builds cleanly with `cargo check --locked`.
- [ ] **2. Vulnerability Scan Passing:** `cargo audit` returns **0 vulnerabilities** found.
- [ ] **3. License Compliance Verified:** `cargo deny check licenses` confirms all new crates use OSI-approved licenses (MIT, Apache-2.0, BSD-3-Clause). No copyleft GPL/AGPL contamination.
- [ ] **4. Minimal Dependency Principle:** Verify if the functionality can be achieved using existing Substrate primitives (`sp-core`, `sp-std`) without introducing external crates.
- [ ] **5. No Unsafe Crate Additions:** Inspect new crates for `unsafe` code usage or unmaintained repositories (no commits in >12 months).
- [ ] **6. No Duplicate Crates:** Ran `cargo tree -d` to confirm no duplicate versions of core libraries (e.g., multiple versions of `syn`, `quote`, or `parity-scale-codec`).
- [ ] **7. Supply Chain Integrity:** Crate author and download history verified on crates.io or GitHub source.

---

*Policy Maintained by Verdis Chain Core Security Team & Arlo AI Security Assistant.*
