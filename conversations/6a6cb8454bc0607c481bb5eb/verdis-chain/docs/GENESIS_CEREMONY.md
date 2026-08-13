# Verdis Chain Mainnet Genesis Ceremony Plan

**Document Status:** Draft v1.0
**Date:** August 11, 2026
**Target:** Verdis Chain v2.0.0 Mainnet Launch
**Token:** VRDX | 100B Supply | 9 Decimals | SS58 Prefix 909
**Consensus:** BABE + GRANDPA DPoS | 21 Validators

---

## Overview

This document defines the procedure for generating the Verdis Chain mainnet genesis block in a secure, transparent, and reproducible manner. The ceremony ensures that:

- No single party controls the genesis state
- All validator keys are generated on air-gapped hardware
- Private keys never leave the generating machine
- The final chain spec is cryptographically verified by multiple independent parties
- The genesis hash is published and immutable before launch

### Participants

| Role | Responsibility |
|------|---------------|
| Foundation (Rojs Gordons) | Coordinate ceremony, assemble chain spec, sign genesis hash |
| Validator Operators | Generate keys, submit public keys, verify chain spec |
| Independent Auditor | Witness ceremony, review chain spec, sign-off on correctness |
| multisig Signers (3-of-5) | Verify and co-sign the final chain spec hash |

### Timeline

| Phase | Timing | Duration |
|-------|--------|----------|
| Phase 1: Validator Key Generation | T-8 weeks | 2 weeks |
| Phase 2: Chain Spec Assembly | T-6 weeks | 2 weeks |
| Phase 3: Dry Run & Validation | T-4 weeks | 2 weeks |
| Phase 4: Multi-sig Verification | T-2 weeks | 1 week |
| Phase 5: Genesis Execution | T-0 | Launch day |
| Phase 6: Post-Genesis Verification | T+24h | 24 hours |

---

## Phase 1: Validator Key Generation (T-8 weeks)

### Prerequisites

- Each validator operator has access to an air-gapped machine
- Substrate key generation tool installed (`subkey` or `polkadot-js`)
- PGP key for signed communication with the Foundation

### Procedure

1. **Each validator operator** generates the following key pairs on an air-gapped machine:

   - **Sr25519 controller key** (AccountId) — used for DPoS registration, staking, governance
   - **Sr25519 BABE session key** — block production
   - **Ed25519 GRANDPA session key** — finality voting
   - **Sr25519 ImOnline session key** — heartbeat/availability

2. **Private keys** are backed up securely (encrypted USB, paper backup) and NEVER transmitted electronically.

3. **Public keys** are submitted to the Foundation via:
   - PGP-signed email to a designated address
   - Or sr25519-signed message submitted via a secure portal

4. **The Foundation verifies** each submission's signature and records the public keys.

### Key Submission Template

```
Validator ID: V01
Operator Name: [Legal name or organization]
Controller AccountId (SS58 909): [5... address]
BABE Session Key (sr25519 hex): [0x...]
GRANDPA Session Key (ed25519 hex): [0x...]
ImOnline Session Key (sr25519 hex): [0x...]
Self-Stake Amount: [VRDX amount, e.g. 1_000_000_000_000_000_000]
Green Score (0-100): [e.g. 85]
Energy Source: [solar|wind|hydro|geothermal|nuclear|mixed]
PGP Signature: [-----BEGIN PGP SIGNATURE----- ...]
```

### Deadline

All 21 validator key submissions must be received by T-6 weeks. Late submissions will not be included in genesis.

---

## Phase 2: Chain Spec Assembly (T-6 weeks)

### Prerequisites

- All 21 validator public keys received and verified
- Token allocation spreadsheet approved by Foundation
- Chain spec generator script tested on testnet

### Procedure

1. **Assemble genesis state** using the chain-spec generator:

   ```bash
   ./target/release/verdis-node build-spec \
     --chain mainnet-template \
     --disable-default-bootnode \
     > chain_spec_mainnet.json
   ```

2. **Configure genesis runtime** with:
   - 21 validator session keys (BABE, GRANDPA, ImOnline)
   - Token allocations per approved schedule:
     - Ecosystem & Developer Grants: 25B VRDX
     - PoS Staking Rewards: 20B VRDX
     - Treasury: 15B VRDX
     - Development: 10B VRDX
     - Liquidity: 10B VRDX
     - Community: 5B VRDX
     - Seed/Strategic: 3B VRDX
     - Public Presale: 2B VRDX
     - Team & Advisors: 5B VRDX
   - Vesting schedules for seed, team, and presale allocations
   - DEX liquidity pool initial reserves
   - Governance council members
   - DPoS validator registrations with green scores

3. **Generate raw chain spec:**
   ```bash
   ./target/release/verdis-node build-spec \
     --chain=chain_spec_mainnet.json \
     --raw > chain_spec_mainnet_raw.json
   ```

4. **Verify genesis state:**
   - Total supply = 100,000,000,000 * 10^9 (100B VRDX with 9 decimals)
   - All 21 validators present with correct session keys
   - All allocations match approved schedule
   - No duplicate accounts
   - Vesting schedules have correct cliff and duration

### Output

- `chain_spec_mainnet_raw.json` — the raw, deterministic genesis specification
- Genesis hash computed and recorded

---

## Phase 3: Dry Run & Validation (T-4 weeks)

### Procedure

1. **Launch private testnet** using the assembled mainnet chain spec:
   ```bash
   ./target/release/verdis-node --chain=chain_spec_mainnet_raw.json --alice --tmp
   ./target/release/verdis-node --chain=chain_spec_mainnet_raw.json --bob --tmp
   # ... for all 21 validators
   ```

2. **Verify for 72 hours minimum:**
   - Block production at expected rate (6s slots)
   - GRANDPA finality reaching 100%
   - All 21 validators producing blocks in rotation
   - Session transitions occurring correctly
   - No unexpected slashes
   - No consensus stalls
   - DPoS election results match expected validator set

3. **Run `try-runtime` checks:**
   ```bash
   ./target/release/verdis-node try-runtime \
     --chain=chain_spec_mainnet_raw.json \
     --runtime=wasm \
     on-runtime-upgrade live
   ```

4. **Independent auditor** reviews:
   - Chain spec JSON for correctness
   - Genesis state for expected balances and keys
   - Dry-run logs for consensus stability
   - Signs off or reports issues

### Acceptance Criteria

- [ ] 72 hours of stable block production
- [ ] All 21 validators active
- [ ] GRANDPA finality at 100%
- [ ] No consensus stalls or reorganizations
- [ ] No unexpected slashes
- [ ] Auditor sign-off received
- [ ] try-runtime checks pass

---

## Phase 4: Multi-sig Verification (T-2 weeks)

### Procedure

1. **Compute genesis hash:**
   ```bash
   sha256sum chain_spec_mainnet_raw.json
   ```

2. **Distribute hash** to all 5 multisig signers.

3. **Each signer independently verifies:**
   - Downloads the chain spec from the designated source
   - Computes SHA-256 hash locally
   - Compares with the published hash
   - Signs the hash with their PGP key

4. **Publish verified hash** to multiple channels:
   - GitHub repository (signed commit)
   - Verdis Chain website (verdischain.com)
   - Official social media
   - Validator operator private channels

5. **Minimum 3-of-5 signers** must verify and sign. Any signer can veto if discrepancies are found, which aborts the ceremony and restarts from Phase 2.

### Output

- Signed genesis hash with 3+ PGP signatures
- Public publication of hash and signatures

---

## Phase 5: Genesis Execution (T-0)

### Prerequisites

- All 21 validator operators ready with nodes configured
- Signed chain spec distributed to all operators
- Genesis hash verified by 3+ signers
- All web services (explorer, DEX, wallet, faucet) prepared
- DNS configured for bootnodes

### Procedure

1. **Coordinated launch** — all validator operators start nodes simultaneously at an agreed UTC time:
   ```bash
   ./target/release/verdis-node \
     --chain=chain_spec_mainnet_raw.json \
     --validator \
     --name "Verdis Validator V01" \
     --bootnodes /dns/bootnode-1.verdischain.com/tcp/30333/p2p/... \
     --bootnodes /dns/bootnode-2.verdischain.com/tcp/30333/p2p/...
   ```

2. **First block** = genesis block. All nodes verify:
   - Genesis hash matches the signed hash
   - Block #0 contains expected genesis state

3. **Foundation executes initial setup transactions:**
   - Initialize vesting schedules
   - Activate token distribution categories
   - Seed DEX liquidity pools
   - Set initial governance parameters

4. **Verify within first 30 minutes:**
   - All 21 validators producing blocks
   - GRANDPA finality working
   - No error logs on any node
   - Block height progressing at expected rate

### Abort Conditions

- Genesis hash mismatch → STOP ALL NODES, investigate, restart from Phase 2
- <15 validators online at launch → wait 30 minutes, if still <15, abort
- Consensus stall within first 100 blocks → STOP, investigate, fix, re-schedule

---

## Phase 6: Post-Genesis Verification (T+24h)

### Checklist

- [ ] All 21 validators active and producing blocks
- [ ] GRANDPA finality at 100% for the last 1000 blocks
- [ ] No unexpected slashes in the first 24 hours
- [ ] Block height progressing at expected rate (14,400 blocks/day at 6s slots)
- [ ] All web services connected and syncing:
  - [ ] Explorer (verdischain.com/explorer/)
  - [ ] DEX (verdischain.com/dex/)
  - [ ] Wallet (verdischain.com/wallet/)
  - [ ] Faucet (if applicable for testnet only)
- [ ] DEX liquidity pools initialized and functional
- [ ] Vesting schedules active and unlocking correctly
- [ ] Governance council operational
- [ ] No critical errors in node logs
- [ ] Network has >50 peers from external sources (if applicable)

### Post-Genesis Report

A post-genesis verification report shall be published within 48 hours of launch, documenting:
- Final genesis hash
- List of active validators
- Block height at T+24h
- Any incidents or anomalies
- Network health metrics (peers, TPS, finality)
- Confirmation that all acceptance criteria were met

---

## Security Requirements

1. **Air-gapped key generation** — all private keys generated on machines with no network connectivity
2. **No private key transmission** — private keys never leave the generating machine, are never emailed, stored in cloud, or shared
3. **Signed key submissions** — all public key submissions must be cryptographically signed (PGP or sr25519)
4. **Multi-party verification** — genesis hash verified by minimum 3 independent parties
5. **Public hash publication** — genesis hash published to multiple channels before launch
6. **Ceremony recording** — all phases documented with timestamps and participant signatures
7. **No server-side custody** — the Foundation does not hold, store, or transmit any validator private keys

## Emergency Procedures

| Scenario | Action |
|----------|--------|
| <21 validators ready at T-6 weeks | Proceed with minimum 15 validators; activate remaining post-launch |
| Chain spec errors found in Phase 3 | Abort dry run, fix spec, restart from Phase 2 |
| Genesis hash mismatch at T-0 | STOP ALL NODES, investigate, re-schedule launch |
| <15 validators online at T-0 | Wait 30 min; if still <15, abort and re-schedule |
| Consensus stall in first 100 blocks | STOP, investigate, apply fix, re-schedule from Phase 3 |
| Validator drops post-launch | Wait for next session; activate backup validator |
| Security vulnerability discovered | Emergency runtime upgrade via governance; if pre-launch, abort and fix |

---

## Appendix A: Bootnode Configuration

Minimum 4 bootnodes across different regions:

```
bootnode-1.verdischain.com  [Region: EU]  TCP 30333
bootnode-2.verdischain.com  [Region: US]  TCP 30333
bootnode-3.verdischain.com  [Region: ASIA] TCP 30333
bootnode-4.verdischain.com  [Region: EU]  TCP 30333
```

Each bootnode must have:
- Static IP address
- Static libp2p peer ID
- DNS TXT record: `_dnsaddr.bootnode-N.verdischain.com`
- 99.9% uptime SLA
- No validator role (bootnode only, no session keys)

## Appendix B: Token Allocation Verification Script

```python
#!/usr/bin/env python3
import json, sys

with open(sys.argv[1]) as f:
    spec = json.load(f)

runtime = spec["genesis"]["runtime"]
balances = runtime.get("Balances", {}).get("balances", [])

total = 0
for account, balance in balances:
    total += balance

expected = 100_000_000_000 * 10**9  # 100B with 9 decimals
assert total == expected, f"Total supply {total} != expected {expected}"

validators = runtime.get("Session", {}).get("keys", [])
assert len(validators) == 21, f"Expected 21 validators, got {len(validators)}"

print("✅ Genesis state verified: 100B supply, 21 validators")
```

---

*This document is a living specification. Updates require Foundation approval and version increment.*
