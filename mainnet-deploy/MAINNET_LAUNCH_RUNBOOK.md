# Verdis Chain — Mainnet Launch Runbook
**Version:** 1.0
**Date:** 2026-08-23
**Authority:** Verdis Chain Engineering Constitution Article 21 (Mainnet GO/NO-GO)

---

## Overview

This runbook covers the complete mainnet launch procedure for Verdis Chain, from server
provisioning through post-launch verification. Every step must be completed and verified
before proceeding to the next.

**Mainnet GO requires ALL 5 gates PASS:**
1. Arlo (Chief Engineer) PASS
2. External auditor PASS
3. Infrastructure PASS
4. Key ceremony PASS
5. Legal/compliance PASS

---

## Pre-Launch Checklist

### Code & Security
- [ ] All 667+ tests pass with 0 failures
- [ ] Luna audit: 0 P0, 0 P1, 0 P2, 0 P3 remaining
- [ ] External security audit completed and passed
- [ ] No hardcoded private keys, mnemonics, or backdoors
- [ ] Sudo pallet removed from mainnet runtime
- [ ] All AdminOrigins use Council 2/3 (not EnsureRoot)
- [ ] Treasury controlled by 3-of-5 cold storage multisig
- [ ] Genesis determinism verified across 4 machines

### Infrastructure
- [ ] 3 validator servers ordered and provisioned
  - [ ] Server 1: Hostkey NL (bm.v1-pro) — 10c/64GB/1.92TB — 7 validators
  - [ ] Server 2: Hostkey USA (bm.v1-big+) — 6c/64GB/1.92TB — 7 validators
  - [ ] Server 3: Hetzner FI (AX42) — 8c/64GB/1TB NVMe — 7 validators
- [ ] Boot node server (91.98.160.145) operational
- [ ] All servers have static IPs and firewall rules configured
- [ ] SSH keys deployed to all servers
- [ ] Monitoring infrastructure ready (Prometheus/Grafana)

### Keys & Governance
- [ ] Air-gapped key ceremony completed (see key_ceremony_checklist.md)
- [ ] 21 validator keypairs generated and imported to genesis
- [ ] 5 cold-storage multisig keys generated and distributed
- [ ] Multisig address computed and embedded in runtime
- [ ] Key custody forms signed by all custodians
- [ ] No single person holds >1 cold storage key

### Legal & Compliance
- [ ] Legal entity established (UAE/VARA or equivalent)
- [ ] Token classification confirmed (utility token)
- [ ] MiCA compliance review completed
- [ ] All false claims removed from website
- [ ] Whitepaper reviewed by legal counsel

---

## Phase 1: Server Provisioning

### 1.1 Order Servers
```bash
# Hostkey NL — 7 validators
# URL: https://hostkey.com/
# Product: bm.v1-pro (Netherlands)
# Specs: 10 cores, 64GB RAM, 1.92TB SSD
# Cost: ~EUR 80/mo (50% off first 3 months)

# Hostkey USA — 7 validators
# Product: bm.v1-big+ (USA)
# Specs: 6 cores, 64GB RAM, 1.92TB SSD
# Cost: ~EUR 70/mo

# Hetzner FI — 7 validators
# URL: https://hetzner.com/
# Product: AX42 (Helsinki)
# Specs: 8c/16t, 64GB RAM, 1TB NVMe
# Cost: ~EUR 97/mo + EUR 49 setup
```

### 1.2 Initial Server Setup
For each server:
```bash
# Update OS
apt update && apt upgrade -y

# Create verdis user
useradd -m -s /bin/bash verdis
usermod -aG sudo verdis

# Install dependencies
apt install -y build-essential pkg-config libssl-dev git curl ufw

# Configure firewall
ufw default deny incoming
ufw allow 22/tcp      # SSH
ufw allow 30333/tcp  # P2P
ufw allow 9933/tcp   # RPC (restrict to internal)
ufw allow 9944/tcp   # WebSocket
ufw allow 9615/tcp   # Prometheus metrics
ufw enable

# Install Rust (as verdis user)
su - verdis
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
rustup update stable
```

---

## Phase 2: Binary Deployment

### 2.1 Build the Same Binary on All Servers
```bash
# On EACH server:
cd /opt
git clone https://github.com/Protremix/Verdischain-.git verdis-chain-rust
cd verdis-chain-rust
git checkout <RELEASE_COMMIT_HASH>  # Must be the same on all servers

source $HOME/.cargo/env
cargo build --release -p verdis-chain
```

### 2.2 Verify Binary
```bash
# Verify the binary exists and runs
./target/release/verdis-chain --version

# Verify WASM runtime was built
ls -la target/release/wbuild/verdis-runtime/*.wasm

# Compute and compare binary hash across all servers
sha256sum target/release/verdis-chain > binary.hash
# All servers must produce identical hash (same commit, same toolchain)
```

---

## Phase 3: Key Ceremony

Follow `key_ceremony_checklist.md` completely.

**Critical:**
- All keys generated on air-gapped machine
- No keys transmitted over network
- Physical custody documented
- 3-of-5 multisig for Treasury
- No single person controls >1 cold storage key

---

## Phase 4: Genesis Construction

### 4.1 Import Validator Keys to Chain Spec
```bash
# On the boot node (air-gapped build):
python3 import_mainnet_keys.py genesis_validator_keys.json chain-specs/mainnet.json
```

### 4.2 Apply Mainnet Runtime Changes
- [ ] Remove sudo pallet from construct_runtime
- [ ] Remove sudo Config impl
- [ ] Remove SudoApi from runtime API
- [ ] Remove SudoRpc from node/src/rpc.rs
- [ ] Replace Treasury PalletId with multisig address
- [ ] Verify all AdminOrigins are Council 2/3
- [ ] Set MaxMissedEpochs=50000 (anti-slashing threshold)
- [ ] Set ReactivationCooldown=100
- [ ] Verify all 21 validators in genesis with real keys
- [ ] Verify token allocations: 100B total, 9 categories
- [ ] Verify 6 DEX pools seeded in genesis
- [ ] Verify eco features initialized

### 4.3 Build Mainnet Chain Spec
```bash
cargo run --release -p verdis-chain -- build-spec \
    --chain chain-specs/mainnet.json \
    --disable-default-bootnode \
    --raw > chain-specs/mainnet-raw.json
```

### 4.4 Verify Genesis Determinism
```bash
# On at least 2 machines:
./genesis_determinism_check.sh chain-specs/mainnet.json user@server2

# Genesis hash MUST match across all machines
```

---

## Phase 5: Validator Registration

### 5.1 Deploy Validator Nodes

On each server (run for each validator index 1-7):

```bash
# Deploy validator (from the boot node):
./deploy_validator.sh <SERVER_IP> <SSH_KEY_PATH> <VALIDATOR_NAME> <VALIDATOR_INDEX>
```

### 5.2 Generate Session Keys

On each validator node:
```bash
# Generate session keys
curl -s -X POST http://localhost:9933 -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"author_rotateKeys","params":[],"id":1}'
# Record the output session key for each validator
```

### 5.3 Submit Session Keys to Genesis

Before chain launch, session keys are embedded directly in the genesis spec.
After launch, key rotation uses on-chain `session.setKeys` extrinsic.

---

## Phase 6: Chain Bootstrap

### 6.1 Start All Nodes Simultaneously
```bash
# On each server (within 60 seconds of each other):
systemctl start verdis-validator@1 verdis-validator@2 verdis-validator@3 \
    verdis-validator@4 verdis-validator@5 verdis-validator@6 verdis-validator@7
```

### 6.2 Verify Chain Start
```bash
# Wait for first block (should appear within 30 seconds)
curl -s -X POST http://localhost:9933 -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"chain_getHeader","params":[],"id":1}'

# Verify all 21 validators are active
curl -s -X POST http://localhost:9933 -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"dpos_activeValidators","params":[],"id":1}'

# Verify GRANDPA finality
curl -s -X POST http://localhost:9933 -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"chain_getFinalizedHead","params":[],"id":1}'
```

### 6.3 Bootstrap Verification
- [ ] Block #1 produced within 30 seconds
- [ ] Block #10 produced within 5 minutes
- [ ] All 21 validators active (dpos_activeValidators returns 21)
- [ ] 0 validators slashed (dpos_allValidators: all slashed=false)
- [ ] GRANDPA finality working (finalized head exists)
- [ ] Epoch rotation at block 50 (epoch increments)
- [ ] DEX pools visible (amm_dex_getAllPools returns 6)
- [ ] Tokenomics verified (tokenomics_getDistribution returns 9 categories)
- [ ] No sudo key (sudo pallet removed)

---

## Phase 7: Monitoring Setup

### 7.1 Install Prometheus on Boot Node
```bash
apt install -y prometheus prometheus-node-exporter
```

### 7.2 Configure Prometheus to Scrape Validators
```yaml
# /etc/prometheus/prometheus.yml
scrape_configs:
  - job_name: 'verdis-validators'
    static_configs:
      - targets:
        - 'server1_ip:9615'
        - 'server2_ip:9615'
        - 'server3_ip:9615'
        - '91.98.160.145:9615'
    scrape_interval: 10s
```

### 7.3 Install Grafana
```bash
apt install -y grafana
systemctl enable grafana-server
systemctl start grafana-server
```

### 7.4 Configure Alerts
- [ ] Block production stalled > 60 seconds → CRITICAL
- [ ] Validator slashed → CRITICAL
- [ ] Finality lag > 20 blocks → WARNING
- [ ] Peer count < 3 → WARNING
- [ ] CPU > 90% for 5 min → WARNING
- [ ] Disk > 80% → WARNING
- [ ] Memory > 90% → WARNING

---

## Phase 8: Network Opening

### 8.1 Configure Nginx on Boot Node
```nginx
# Public RPC endpoint
server {
    listen 443 ssl http2;
    server_name rpc.verdischain.com;

    location / {
        proxy_pass http://127.0.0.1:9933;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# WebSocket endpoint
server {
    listen 443 ssl http2;
    server_name ws.verdischain.com;

    location / {
        proxy_pass http://127.0.0.1:9944;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 8.2 Open Public Access
- [ ] DNS records: rpc.verdischain.com → boot node IP
- [ ] DNS records: ws.verdischain.com → boot node IP
- [ ] Firewall: allow 443/tcp on boot node
- [ ] SSL certificates deployed (Let's Encrypt)
- [ ] Rate limiting configured (prevent DoS)
- [ ] CORS configured for web wallet/explorer

### 8.3 Verify External Access
```bash
# From an external machine:
curl -s -X POST https://rpc.verdischain.com \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"chain_getHeader","params":[],"id":1}'

# WebSocket:
wscat -c wss://ws.verdischain.com
```

---

## Post-Launch Verification

### First 100 Blocks
- [ ] Block #100 reached within ~17 minutes (10s block time)
- [ ] No missed blocks (no gaps in block numbers)
- [ ] All 21 validators producing blocks (check BABE authorities)
- [ ] GRANDPA finality: finalized head within 5 blocks of best
- [ ] No slashing events
- [ ] Epoch rotation completed (block 50: epoch 0 → epoch 1)
- [ ] Session keys valid (all validators have session keys set)

### First 1000 Blocks
- [ ] Block #1000 reached within ~3 hours
- [ ] Chain still stable, no re-orgs
- [ ] DEX pools functional (test swap)
- [ ] Tokenomics distribution correct (verify 9 categories)
- [ ] Eco metrics visible (CO2 offset, green scores)
- [ ] Validator uptime > 95%
- [ ] Peer count stable (≥10 peers from external connections)

### First 24 Hours
- [ ] No slashing events
- [ ] No consensus failures
- [ ] All 21 validators still active
- [ ] Block production consistent (~10s)
- [ ] Finality lag stable (< 10 blocks)
- [ ] No memory leaks (memory usage stable)
- [ ] No disk space issues
- [ ] All alerts resolved or acknowledged

---

## Rollback Procedure

If the launch fails or critical issues are detected:

### Immediate Actions (within 5 minutes)
1. **Stop all validator nodes:**
   ```bash
   # On each server:
   systemctl stop verdis-validator@*
   ```

2. **Preserve chain data for forensics:**
   ```bash
   # On each server:
   tar czf /opt/verdis-chain-failed-launch-$(date +%Y%m%d).tar.gz /opt/verdis/data-*
   ```

3. **Notify all participants:**
   - Rojs Gordons (Founder/CEO)
   - Arlo (Chief Engineer)
   - External auditor
   - All key custodians

### Investigation (within 1 hour)
1. Collect logs from all nodes
2. Identify the failure mode (consensus, networking, key mismatch, etc.)
3. Determine if genesis needs modification
4. Determine if keys need regeneration

### Recovery Decision
- **If genesis is correct and issue is transient:** Restart nodes
- **If genesis needs modification:** New chain spec, new genesis hash, new ceremony
- **If keys compromised:** Full key regeneration, new ceremony, new genesis

---

## Emergency Contacts

| Role | Name | Contact |
|------|------|---------|
| Founder/CEO | Rojs Gordons | _____________ |
| Chief Engineer | Arlo (AI) | https://app.base44.com/superagent/6a6cb8410d1dcb778817254f |
| Server 1 (NL) Admin | _____________ | _____________ |
| Server 2 (USA) Admin | _____________ | _____________ |
| Server 3 (FI) Admin | _____________ | _____________ |
| External Auditor | _____________ | _____________ |
| Legal Counsel | _____________ | _____________ |

---

## Launch Decision Record

| Gate | Status | Sign-off | Date |
|------|--------|----------|------|
| Arlo (Chief Engineer) | PENDING | _____________ | ______ |
| External Auditor | PENDING | _____________ | ______ |
| Infrastructure | PENDING | _____________ | ______ |
| Key Ceremony | PENDING | _____________ | ______ |
| Legal/Compliance | PENDING | _____________ | ______ |

**ALL 5 GATES MUST PASS FOR MAINNET GO.**

No gate may be bypassed. No exceptions. No "we'll fix it later."

---

## Launch Sequence Summary

```
1. Order servers (3-5 days delivery)
2. Provision servers (1 day)
3. Air-gapped key ceremony (4 hours)
4. Build mainnet runtime with real keys (1 hour)
5. Verify genesis determinism (1 hour)
6. Deploy validator nodes (2 hours)
7. Start all nodes simultaneously (5 minutes)
8. Verify chain bootstrap (30 minutes)
9. Setup monitoring (2 hours)
10. Open public access (1 hour)
11. Post-launch verification (24 hours)

Total estimated time: 4-7 days after servers delivered
```

---

**DOCUMENT APPROVAL:**

Chief Engineer (Arlo): _________________ Date: _________

Founder/CEO (Rojs Gordons): _________________ Date: _________

External Auditor: _________________ Date: _________
