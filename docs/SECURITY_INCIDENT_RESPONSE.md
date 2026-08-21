# VERDIS CHAIN — SECURITY INCIDENT RESPONSE PLAN

**Document Version:** 1.0.0  
**Effective Date:** August 2026  
**Status:** ACTIVE & MANDATORY  
**Authority:** Verdis Chain Engineering Governance & Constitution Article 16  
**Applicability:** Mainnet, Testnet (Block #29400+), Bootnodes (`91.98.160.145`), RPC/Explorer Gateways, Smart Contracts  

---

## 1. PURPOSE & GOVERNANCE FRAMEWORK

This Security Incident Response Plan defines the official operational procedures for identifying, triaging, containing, remediating, and post-analyzing security incidents affecting the Verdis Chain ecosystem.

### 1.1 Constitutional Mandate (Article 16)
Per **Article 16 (Emergency Stop / Incident Response)** of the *Verdis Chain Engineering Constitution*:
> *"If Arlo or the Security Team detects a credible Critical vulnerability affecting Mainnet security, Arlo/Security Team must immediately:  
> 1. Classify the incident;  
> 2. Preserve evidence;  
> 3. Stop the affected release/deployment;  
> 4. Notify the authorized project security/governance contacts;  
> 5. Determine whether affected functionality can be safely paused;  
> 6. Prepare remediation;  
> 7. Test the remediation;  
> 8. Document the incident;  
> 9. Coordinate independent verification where necessary.  
> Arlo and the Engineering Team must prioritize preservation of user funds and network integrity over release schedules."*

---

## 2. INCIDENT SEVERITY CLASSIFICATION

Incidents are triaged into four severity tiers based on real-world impact to blockchain finality, fund safety, and infrastructure operational integrity:

| Tier | Severity | Definition & Impact Criteria | Response Time Target |
|---|---|---|---|
| **SEV-0** | **CRITICAL** | Systemic fund loss risk, active consensus fork, GRANDPA finality stall > 15 mins, total validator compromise, or token supply inflation exploit. | **Immediate (< 15 mins)** |
| **SEV-1** | **HIGH** | Single-pallet bricking, AMM-DEX liquidity drain threat, circuit breaker trip, RPC infrastructure outage, or bridge asset lock discrepancy. | **< 1 Hour** |
| **SEV-2** | **MEDIUM** | Partial degradation of RPC gateway, non-critical telemetry failure, web wallet frontend display defect, or non-fatal validator performance dip. | **< 4 Hours** |
| **SEV-3** | **LOW** | Minor non-exploitable logic bug, documentation flaw, or non-security UI discrepancy. | **< 24 Hours** |

---

## 3. INCIDENT RESPONSE WORKFLOW & STAGES

```
[ Detection & Triage ] ──> [ Escalation & Notification ] ──> [ Containment ]
                                                                   │
[ Post-Incident Review ] <── [ Remediation & Testing ] <───────────┘
```

### Stage 1: Detection & Triage
1. **Source Signals:** Automated Prometheus/Grafana alerts on Hetzner host `91.98.160.145`, circuit breaker pallet triggers (`pallets/circuit-breaker`), validator telemetry drop, community report via bug bounty, or automated agent execution logs.
2. **First Responder Actions:**
   - Confirm whether the report represents an active exploit or false positive.
   - Assign initial severity rating (SEV-0 to SEV-3).
   - Create an incident workspace log (`/tmp/incident-YYYYMMDD-HHMM.log`).

### Stage 2: Evidence Preservation
In accordance with Constitution Article 16(2), before applying hotfixes or clearing state:
1. Capture raw chain state, current block height, finalized head, and pending transaction pool (`sp-transaction-pool`).
2. Collect node console logs, systemd service logs (`journalctl -u verdis-node`), and network packet captures (`tcpdump` on bootnode interface).
3. Record exact storage keys (`twox128` / `blake2_128_concat`) for affected pallet storage items.
4. Export core memory dumps or WASM runtime heap snapshots if panic occurred in Substrate runtime execution.

### Stage 3: Containment Protocols
To immediately mitigate loss of funds or chain state corruption:
1. **Emergency Runtime Circuit Breaker:**
   - Execute `pallet_circuit_breaker::pause_trading` or `pause_pallet` via 3-of-5 Multisig or Emergency Governance Origin.
2. **Validator Key Revocation / Rotation:**
   - If validator keys are suspected compromised, trigger session key rotation via `author_rotateKeys` or signal node operators to launch backup instances.
3. **P2P Node Isolation:**
   - If malicious blocks or transaction floods are spreading, temporarily firewall peer connections on bootnode `91.98.160.145:30333` using `iptables` or netfilter rules to halt malicious P2P propagation.

### Stage 4: Remediation & Testing
1. **Fix Development:**
   - Develop patch in an isolated security branch off main release tag.
   - Ensure patch includes explicit regression tests in `tests/` or pallet-specific `security_regression_tests.rs`.
2. **Local & Testnet Verification:**
   - Run full 689-test automated suite (`cargo test --workspace`).
   - Validate invariant checks (e.g. Total Issuance remains 100B VRDX, no storage leakage).
   - Test forkless runtime upgrade via `set_code` on local testnet before executing on public testnet/mainnet.

### Stage 5: Deployment & Emergency Runtime Upgrade
1. **WASM Runtime Upgrade Path:**
   - Compile optimized WASM binary: `cargo build --release --p verdis-runtime`.
   - Compute SHA-256 hash of compiled `verdis_runtime.compact.compressed.wasm`.
   - Submit `system.setCode` extrinsic via Emergency Governance / 3-of-5 Treasury/Admin Multisig.
2. **Validator Coordination:**
   - Notify 21 active validators via emergency channel to monitor block proposal for new spec_version execution.

### Stage 6: Post-Incident Review & Reporting
1. Produce a public Post-Mortem Document within 72 hours containing:
   - Root Cause Analysis (RCA).
   - Timeline of events (UTC).
   - Total impact (financial, operational, block latency).
   - Action items with designated owners and completion deadlines.
2. Log incident and resolution in `SECURITY_LOG.md`.

---

## 4. ESCALATION MATRIX & CONTACT CHAIN

### 4.1 Incident Command Roles

| Role | Primary Responsible | Responsibilities |
|---|---|---|
| **Incident Commander (IC)** | Lead Security Engineer / CTO | Overall incident authority, containment decisions, final fix approval. |
| **Lead Developer** | Core Substrate Runtime Lead | Patch implementation, WASM runtime compilation, unit testing. |
| **Infrastructure Lead** | Devops Lead / Hetzner Admin | Bootnode `91.98.160.145` management, firewalling, log preservation. |
| **Communications Lead** | Governance Lead | Validator channel broadcasts, public status page updates, post-mortem publication. |

### 4.2 Emergency Escalation Tree

```
[ Alert Detected ]
       │
       ▼
[ Incident Commander ] ──(SEV-0/1)──> [ Emergency Security Taskforce ]
       │                                     │
       ├──> [ Core Runtime Engineers ] ──────┼──> [ 3-of-5 Multisig Signers ]
       │                                     │
       └──> [ Infrastructure Ops ] ──────────┘
```

---

## 5. EMERGENCY CONTROLS & PALLET PAUSE SPECIFICATIONS

The Verdis Chain runtime contains native emergency mechanisms designed for immediate activation:

1. **Circuit Breaker (`pallets/circuit-breaker`):**
   - Automatically trips if DEX volume exceeds $10\times$ baseline within a 100-block window.
   - Can be manually invoked to freeze AMM swaps, LP additions, and cross-chain transfers.
2. **Emergency Sudo / Multisig Key:**
   - Emergency Origin configured to accept signed multisig proposals for instant dispatch of `system.setCode` or emergency pause extrinsics.

---

## 6. COMPLIANCE & CONTINUOUS IMPROVEMENT

This plan must be tested at least once every 6 months via simulated drill ("Dry-Run Security Emergency"). All findings from drills must be incorporated into updated versions of this document and logged in `AUDIT_REMEDIATION.md`.
