# Verdis Chain Disaster Recovery Guide

This document outlines emergency procedures, incident response workflows, and disaster recovery (DR) protocols for **Verdis Chain v2.0.0**.

---

## 1. Executive Summary & Recovery Objectives

| Metric | Target Objective | Definition |
| :--- | :--- | :--- |
| **Recovery Point Objective (RPO)** | `< 1 hour` (Max data loss window) | RocksDB state & keystore snapshots taken hourly/daily |
| **Recovery Time Objective (RTO)** | `< 15 minutes` for single-node crash | Automated systemd service self-healing |
| **RTO (Catastrophic DB Corruption)**| `< 1 hour` | Full database restore or genesis state re-synchronization |
| **Consensus Engine** | BABE + GRANDPA | Block time: 6s, Epoch: 600 slots, Session: 600 blocks |
| **Primary Node Host** | `91.98.160.145` (`verdischain.com`) | Systemd unit: `verdis-node.service` |
| **Data Root Directory** | `/opt/verdis-chain-rust/data` | DB: `chains/dev/db`, Keystore: `chains/dev/keystore` |
| **Backup Path** | `/var/backups/verdis/` | Script: `/opt/verdis-backup.sh` |

---

## 2. Chain Data Backup Strategy

### 2.1. Snapshot Components & Directory Hierarchy
To restore node state completely, backups must encapsulate two primary directories within `/opt/verdis-chain-rust/data/`:
1. **Keystore Directory (`chains/dev/keystore/`):** Contains node session keys (BABE `61757468` and GRANDPA `6772616e`).
2. **RocksDB Database Directory (`chains/dev/db/`):** Contains block storage, state trie history, and transaction indices.

### 2.2. Automated Backup Execution
The automated script `/opt/verdis-backup.sh` executes daily (or on demand) and retains backups for 14 days:

```bash
#!/usr/bin/env bash
# Verdis Chain Disaster Recovery Snapshot Script
set -euo pipefail

BACKUP_ROOT="/var/backups/verdis"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ARCHIVE_PATH="${BACKUP_ROOT}/verdis_snapshot_${TIMESTAMP}.tar.gz"
DATA_DIR="/opt/verdis-chain-rust/data"

mkdir -p "$BACKUP_ROOT"

# Stop service to safely release RocksDB write lock
systemctl stop verdis-node || true

# Compress keystore and database
tar -czf "$ARCHIVE_PATH" \
  -C "$DATA_DIR" chains/dev/keystore chains/dev/db

# Restart service immediately
systemctl start verdis-node

# Enforce 14-day retention policy
find "$BACKUP_ROOT" -type f -name "verdis_snapshot_*.tar.gz" -mtime +14 -delete

echo "Snapshot generated successfully: $ARCHIVE_PATH"
```

---

## 3. Key Backup & Secret Management

### 3.1. Key Classification & Storage Protocol

| Key Type | Key ID Header | Crypto Scheme | Primary Storage Location | Security Protocol |
| :--- | :--- | :--- | :--- | :--- |
| **BABE Session Key** | `61757468` (`auth`) | `sr25519` | `/opt/verdis-chain-rust/data/chains/dev/keystore` | Local node filesystem & encrypted backup |
| **GRANDPA Session Key** | `6772616e` (`gran`) | `ed25519` | `/opt/verdis-chain-rust/data/chains/dev/keystore` | Local node filesystem & encrypted backup |
| **Sudo Key (Alice Dev)** | N/A | `sr25519` | Cold storage / Injected via `--alice` | Hardware wallet / Air-gapped offline storage |
| **Node Network Key** | `secret_ed25519` | `ed25519` | `/opt/verdis-chain-rust/data/chains/dev/network` | Node p2p identity key |

### 3.2. Secure Key Backup Procedure
Execute encrypted backup of validator keys prior to system upgrades or maintenance:

```bash
sudo mkdir -p /var/backups/verdis/keys
sudo tar -czf - /opt/verdis-chain-rust/data/chains/dev/keystore | \
  gpg --symmetric --cipher-algo AES256 -o /var/backups/verdis/keys/keystore_backup_$(date +%Y%m%d).tar.gz.gpg
```

---

## 4. Node Recovery from Crash

### 4.1. Automated Service Restart
`verdis-node.service` is configured with auto-restart mechanisms:
* `Restart=always`
* `RestartSec=5s`

If the node binary terminates abnormally, systemd attempts recovery every 5 seconds automatically.

### 4.2. Manual Crash Inspection & Recovery Workflow
When automatic restart fails, execute the following diagnostic steps:

```bash
# Step 1: Check service status and error codes
sudo systemctl status verdis-node -l

# Step 2: Inspect recent panic output or error logs
sudo journalctl -u verdis-node -n 100 --no-pager | grep -iE "panic|error|corrupt|fatal"

# Step 3: Check for stale RocksDB lock files
ls -la /opt/verdis-chain-rust/data/chains/dev/db/full/LOCK

# Step 4: If process crashed while holding lock, ensure process is terminated and remove lock file if stale
sudo systemctl stop verdis-node
sudo rm -f /opt/verdis-chain-rust/data/chains/dev/db/full/LOCK
sudo systemctl start verdis-node
```

---

## 5. Consensus Halt Procedures

### 5.1. Identifying Consensus Stalls
A consensus halt occurs when:
1. Block production halts (BABE slot assignment failure or clock drift).
2. GRANDPA finality stops advancing (`Best Block` continues incrementing, but `Finalized Block` remains fixed).

### 5.2. Epoch Transition Diagnostics
Verdis Chain operates on **600-slot epochs** (~1 hour). Consensus halts frequently occur during epoch boundary transitions if validator session keys fail to rotate or epoch data is corrupted in state trie.

* **Check Epoch Log Warnings:**
```bash
sudo journalctl -u verdis-node | grep -E "BABE: epoch|GRANDPA: voter|Session: new session"
```

### 5.3. Step-by-Step Consensus Stall Recovery

1. **Verify Clock Synchronization:**
   Substrate consensus requires tight NTP clock bounds (< 1000ms drift).
   ```bash
   sudo timedatectl set-ntp true
   sudo systemctl restart systemd-timesyncd
   timedatectl status
   ```

2. **Restart Node with Detailed Consensus Logging:**
   ```bash
   sudo systemctl stop verdis-node
   # Temporarily adjust log level to debug consensus modules
   sudo RUST_LOG="info,babe=debug,grandpa=debug" /opt/verdis-chain-rust/target/release/verdis \
     --chain dev --validator --alice --base-path /opt/verdis-chain-rust/data
   ```

3. **Force Block Production on Single Validator (Alice):**
   If dev single-validator state is stalled due to missed slots:
   ```bash
   sudo systemctl restart verdis-node
   ```

---

## 6. Emergency Contacts & Escalation Protocol

### 6.1. Incident Severity Levels

| Level | Classification | Trigger Condition | Target Response Time |
| :--- | :--- | :--- | :--- |
| **P1 - Critical** | Network Outage | Chain halted, block height not advancing for > 5 mins | `< 15 minutes` |
| **P2 - Major** | Finality Failure | GRANDPA lag > 100 blocks or RPC API down | `< 30 minutes` |
| **P3 - Minor** | Performance Degradation | High RPC latency, non-critical peer drop | `< 2 hours` |
| **P4 - Low** | Informational | Warning logs, non-blocking cert renewal notice | `< 24 hours` |

### 6.2. Escalation & Communication Flow
1. **Infrastructure On-Call:** Automated health check (`/opt/verdis-health-check.sh`) triggers alert.
2. **Core Engineers:** Core developers notified via internal incident escalation channel.
3. **GitHub Issue Tracking:** Create an official incident issue under `https://github.com/verdis-chain/verdis-chain/issues`.
4. *Note: All communications must be logged via official GitHub repository channels.*

---

## 7. Rollback Procedures

If a consensus fork or unrecoverable runtime state mutation occurs on the development chain, follow these rollback procedures.

### 7.1. Full Chain Purge & Reset
To purge chain state and restart from genesis block:

```bash
# 1. Stop node service
sudo systemctl stop verdis-node

# 2. Execute Substrate purge-chain
/opt/verdis-chain-rust/target/release/verdis purge-chain \
  --dev \
  --base-path /opt/verdis-chain-rust/data \
  -y

# 3. Restart node service to re-initialize genesis
sudo systemctl start verdis-node
```

### 7.2. Restoring Database State to Last Valid Snapshot

```bash
# 1. Stop node service
sudo systemctl stop verdis-node

# 2. Clear corrupted database directory
sudo rm -rf /opt/verdis-chain-rust/data/chains/dev/db

# 3. Unpack trusted backup archive
sudo tar -xzf /var/backups/verdis/verdis_snapshot_20260803_180000.tar.gz \
  -C /opt/verdis-chain-rust/data/

# 4. Enforce permissions
sudo chown -R verdis:verdis /opt/verdis-chain-rust/data

# 5. Start node
sudo systemctl start verdis-node
```

### 7.3. Genesis Re-Generation Protocol
If chain specification or genesis configuration requires alteration:

```bash
cd /opt/verdis-chain-rust

# 1. Export standard chain spec
./target/release/verdis build-spec --chain dev > plain-chain-spec.json

# 2. Generate raw chain spec
./target/release/verdis build-spec --chain plain-chain-spec.json --raw > raw-chain-spec.json

# 3. Launch node with new raw chain spec
./target/release/verdis --chain raw-chain-spec.json --validator --alice --base-path /opt/verdis-chain-rust/data
```

---

## 8. Validator Key Compromise Response

In the event of key compromise or security breach:

### Step 1: Immediate Network Isolation
Isolate affected node via UFW firewall rules to prevent unauthorized extrinsics or block propagation:

```bash
sudo ufw deny 30333/tcp
sudo ufw deny 9944/tcp
```

### Step 2: Rotate Session Keys via Local RPC
Generate new BABE (`sr25519`) and GRANDPA (`ed25519`) keypairs using RPC:

```bash
curl -s -X POST http://127.0.0.1:9944 \
  -H "Content-Type: application/json" \
  -d '{"id":1, "jsonrpc":"2.0", "method":"author_rotateKeys", "params":[]}'
```
*Output returns public key hex string.*

### Step 3: Update On-Chain Session Keys
Submit `session.setKeys(keys, proof)` extrinsic via controller account or Sudo key to register newly rotated session keys on-chain.

### Step 4: Restart Node with New Keystore Configuration
```bash
sudo systemctl restart verdis-node
sudo ufw allow 30333/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

---

## 9. Network Partition Recovery

### 9.1. Fork Resolution Strategy
* **BABE Fork Choice Rule:** Selects the chain with the most cumulative weight (longest valid chain).
* **GRANDPA Finality Rule:** Finalizes the highest block header that has received votes from > 2/3 of validator weight.

### 9.2. GRANDPA Catch-Up Mechanism
When a partitioned validator reconnects:
1. Node downloads missing block headers via BABE peer syncing.
2. GRANDPA voter set requests missing commit messages via GRANDPA catch-up protocol (`grandpa_justification`).
3. If node fails to sync automatically, add explicit bootstrap peers via RPC:

```bash
curl -s -X POST http://127.0.0.1:9944 \
  -H "Content-Type: application/json" \
  -d '{"id":1, "jsonrpc":"2.0", "method":"system_addReservedPeer", "params":["/ip4/91.98.160.145/tcp/30333/p2p/12D3KooW..."]}'
```

---

## 10. Data Corruption Recovery

### 10.1. Identifying RocksDB State Corruption
Symptoms of state database corruption:
* Node fails to start with error: `Corruption: SST file read error` or `Bad block magic number`.
* Substrate state trie error: `Trie lookup error: Missing key in state database`.

### 10.2. RocksDB State Directory Cleaning & Repair
To clean corrupted transient state or repair RocksDB tables:

```bash
sudo systemctl stop verdis-node

# Backup keystore before touch operations
sudo cp -r /opt/verdis-chain-rust/data/chains/dev/keystore /tmp/keystore_safe

# Remove corrupted database directory
sudo rm -rf /opt/verdis-chain-rust/data/chains/dev/db

# Restore keystore
sudo mkdir -p /opt/verdis-chain-rust/data/chains/dev
sudo cp -r /tmp/keystore_safe /opt/verdis-chain-rust/data/chains/dev/keystore
sudo chown -R verdis:verdis /opt/verdis-chain-rust/data

# Restart node to rebuild state from genesis or sync peers
sudo systemctl start verdis-node
```

---

## 11. Post-Incident Checklist & RCA Standard

Following any P1 or P2 incident resolution, complete the post-incident checklist within 24 hours:

### 11.1. Service Restoration Checklist
- [ ] Node systemd service is active (`systemctl status verdis-node`).
- [ ] Local RPC endpoint responding on port 9944 (`curl http://127.0.0.1:9944`).
- [ ] Nginx HTTPS reverse proxy operational (`https://verdischain.com/rpc`).
- [ ] Block production advancing steadily at 6s intervals.
- [ ] GRANDPA finality lag is `< 3 blocks`.
- [ ] Backup snapshot script `/opt/verdis-backup.sh` executed successfully.
- [ ] Health check script `/opt/verdis-health-check.sh` returns `STATUS: OK`.

### 11.2. Root Cause Analysis (RCA) Document Template
Document incident findings in GitHub Issues using the template below:

```markdown
# Incident Post-Mortem (RCA): [Incident Title]

**Date & Time:** YYYY-MM-DD HH:MM UTC  
**Incident Severity:** P1 - Critical / P2 - Major  
**Affected Systems:** Verdis Node (91.98.160.145) / verdischain.com  

## 1. Executive Summary
Brief high-level description of what happened, duration, and user impact.

## 2. Timeline (UTC)
* **HH:MM** - Incident triggered / detected by monitoring.
* **HH:MM** - Incident triage started by infrastructure team.
* **HH:MM** - Root cause identified.
* **HH:MM** - Fix applied / service restored.

## 3. Root Cause
Detailed technical explanation of failure cause.

## 4. Resolution & Recovery
Steps taken to restore network state and operational stability.

## 5. Preventative Measures & Action Items
- [ ] Action item 1 (GitHub Issue #)
- [ ] Action item 2 (GitHub Issue #)
```
