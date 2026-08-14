# Protremix Independence Test (ARCH-005)

**Date:** 2026-08-14
**Approved by:** Rojs Gordons
**Policy:** Protremix-controlled stake must not exceed 33% of total network stake

---

## 1. Production Dependency Inventory

### Infrastructure Controlled by Protremix

| Component | Owner | Location | Independence Risk |
|-----------|-------|----------|-------------------|
| Server 91.98.160.145 | Protremix (Hetzner) | Germany | HIGH — single server |
| Server 62.238.61.145 | Protremix | Netherlands | HIGH — single server |
| DNS verdischain.com | Protremix | Registrar TBD | MEDIUM |
| DNS evolvixos.com | Protremix | Registrar TBD | MEDIUM |
| GitHub repo (Protremix/Verdischain-) | Protremix | GitHub | MEDIUM — repo can be forked |
| CI/CD (12 workflows) | Protremix | GitHub Actions | LOW — reproducible |
| Nginx (14 site configs) | Protremix | Server | MEDIUM — configs in repo |
| RPC endpoint | Protremix | rpc.verdischain.com | HIGH — single provider |

### Services Controlled by Protremix (17 systemd services)

| Service | Criticality | Independent Alternative |
|---------|------------|--------------------------|
| verdis-node (Alice) | CRITICAL | Any validator can produce blocks |
| verdis-node2 (Bob) | CRITICAL | Any validator |
| verdis-node3 (Charlie) | CRITICAL | Any validator |
| verdis-val-2 (Bob) | HIGH | Independent validators |
| verdis-val-4 (Dave) | HIGH | Independent validators |
| verdis-val-5 (Eve) | HIGH | Independent validators |
| verdis-relay (TX Relay v3) | MEDIUM | Open source — any operator can run |
| verdis-api | MEDIUM | Can be run by anyone |
| verdis-faucet | LOW | Any operator |
| verdis-governance | MEDIUM | Can be run by anyone |
| verdis-rpc-filter | MEDIUM | Open source |
| verdis-health-monitor | LOW | Any operator |
| verdis-validator-monitor | LOW | Any operator |
| verdis-finality-monitor | LOW | Any operator |
| verdis-price-collector | LOW | Any operator |
| verdis-soak-test | LOW | Testing only |
| verdis-txbot | LOW | Testing only |

### Keys Controlled by Protremix

| Key Type | Current Holder | Risk |
|----------|---------------|------|
| Alice (validator session keys) | Protremix server | HIGH — controls block production |
| Bob (validator session keys) | Protremix server | HIGH |
| Charlie (validator session keys) | Protremix server | HIGH |
| Dave (validator session keys) | Protremix server | HIGH |
| Eve (validator session keys) | Protremix server | HIGH |
| Treasury (PalletId placeholder) | Protocol (code-defined) | MEDIUM — needs 3-of-5 multisig |
| GitHub repo admin | Protremix | MEDIUM — can be transferred |

---

## 2. Dependency Map

### Validators & Consensus
- 6 active validators, ALL operated by Protremix on one server
- Session keys: Alice, Bob, Charlie, Dave, Eve, Ferdie (all well-known test keys)
- **CRITICAL RISK: 100% of validators are Protremix-controlled**

### Keys
- All validator keys are Substrate development keys (not air-gapped)
- Treasury uses PalletId placeholder (not real multisig)
- No air-gapped keys exist yet

### Repositories
- GitHub: Protremix/Verdischain- (Protremix-owned org)
- CI/CD: GitHub Actions (tied to Protremix org)
- No mirror repository exists

### DNS
- verdischain.com → Protremix
- evolvixos.com → Protremix
- No Foundation control over DNS

### Treasury
- PalletId(*b"verdist0") — code-defined, not multisig
- Spend origin: Council 2/3 (EnsureCouncilSpend)
- Needs: 3-of-5 cold storage multisig replacement

### Governance
- Council: 8 members (all development keys)
- Democracy: 0 proposals
- No independent governance participants

### Upgrades
- Runtime upgrade via SET_CODE — requires root (pallet_sudo removed)
- Council can authorize upgrades
- No superuser backdoor

### Emergency Powers
- No sudo (removed)
- Council can emergency proposals
- No single-key emergency control

---

## 3. Measurable Independence Criteria

| # | Criterion | Current Status | Target |
|---|-----------|---------------|--------|
| 1 | Network produces blocks without Protremix validators | FAIL | PASS (21+ independent validators) |
| 2 | Independent operator deploys validator from public docs | FAIL | PASS (validator setup guide published) |
| 3 | Independent RPC provider serves network | FAIL | PASS (1+ independent RPC) |
| 4 | Source/artifacts available independently | PARTIAL (GitHub only) | PASS (Foundation mirror) |
| 5 | No single Protremix key can upgrade runtime | FAIL (Council majority) | PASS (multisig + governance) |
| 6 | Emergency authority bounded by scope/time/multisig | PARTIAL | PASS |
| 7 | Tokenomics enforced by code/genesis | PASS | PASS (CI verified) |
| 8 | Public explorer not only way to read chain state | FAIL (only Protremix RPC) | PASS (independent RPC) |
| 9 | Critical secrets not held by one person/company | FAIL | PASS (air-gapped ceremony) |
| 10 | Documented recovery if Protremix unavailable | FAIL | PASS (DR plan tested) |

**Current Score: 1/10 PASS. Target: 10/10 PASS before mainnet.**

---

## 4. Failure Simulation: Protremix Unavailable for 30 Days

### Scenario: Protremix server (91.98.160.145) goes offline permanently on Day 0

| Function | Continues? | Impact | Mitigation Required |
|----------|-----------|--------|---------------------|
| Block production | NO — all 6 validators on this server | Chain halts | Independent validators on separate servers |
| Block finality | NO — GRANDPA validators offline | No finality | Independent GRANDPA keys |
| RPC access | NO — only RPC is on this server | No queries | Independent RPC providers |
| TX Relay | NO — runs on this server | No transactions | Open source — can be redeployed |
| Web wallet | NO — hosted on this server | No wallet | Can be self-hosted from GitHub |
| Explorer | NO — hosted on this server | No explorer | Can be redeployed from GitHub |
| Governance | NO — no API, no council | No governance | Independent governance infra |
| Treasury | NO — no spend possible | Funds frozen | Multisig on independent keys |
| DNS resolution | NO — DNS points to dead server | Domain unreachable | Foundation DNS control |
| Source code | YES — GitHub is independent | No impact | Already independent |
| CI/CD | YES — GitHub Actions is independent | No impact | Already independent |

### Simulation Result

**If Protremix becomes unavailable TODAY:**
- Chain halts immediately (0 independent validators)
- All web services go down
- No recovery possible without Protremix
- **VERDICT: 100% Protremix-dependent — NOT ACCEPTABLE for mainnet**

### Required Remediation Before Mainnet

1. Deploy 21+ validators on independent servers (3+ countries, 3+ ASNs)
2. Generate air-gapped keys (21 validator + 5 multisig)
3. Foundation takes control of DNS records
4. Foundation has GitHub repo mirror
5. At least 1 independent RPC provider
6. TX Relay deployed by independent operator
7. DR exercise: simulate Protremix failure, verify chain continues

---

## 5. Independence Roadmap

### Phase 1: Key Independence (Weeks 1-3)
- Air-gapped key ceremony: 21 validator keypairs + 5 multisig keys
- Import keys to 21 independent validator servers
- Replace PalletId treasury with 3-of-5 multisig
- Verify chain produces blocks with independent validators

### Phase 2: Infrastructure Independence (Weeks 3-6)
- Foundation takes DNS control
- Foundation creates GitHub repo mirror
- Independent RPC provider deployed
- TX Relay deployed by independent operator
- Explorer deployed by independent operator

### Phase 3: Governance Independence (Weeks 6-8)
- Independent council members (not development keys)
- Democracy proposals from community
- No Protremix majority on council
- Stake concentration < 33% Protremix

### Phase 4: DR Exercise (Weeks 8-10)
- Simulate Protremix server failure
- Verify chain continues with independent validators
- Verify all critical functions accessible
- Publish DR test report
- Score 10/10 on independence criteria
