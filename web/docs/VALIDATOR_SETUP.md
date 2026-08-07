# Verdis Chain Validator Setup Guide

This document provides a comprehensive, step-by-step guide for deploying, configuring, securing, and maintaining a validator node on the **Verdis Chain** network.

---

## 1. Network & Project Overview

Verdis Chain is an eco-centric enterprise blockchain built on Rust and the Substrate framework, utilizing **BABE** for block authoring and **GRANDPA** for deterministic finality.

| Parameter | Value / Details |
| :--- | :--- |
| **Network Name** | Verdis Chain Mainnet / Devnet |
| **Chain ID** | `909` |
| **SS58 Address Format** | `909` |
| **Native Token** | VRDX (100,000,000,000 Total Supply, 9 Decimals) |
| **Primary Node Server IP** | `91.98.160.145` |
| **Domain Name** | `verdischain.com` |
| **Node Binary Path** | `/opt/verdis-chain-rust/target/release/verdis` |
| **Chain Data Directory** | `/opt/verdis-chain-rust/data` |
| **Block Target Time** | `6 seconds` |
| **Epoch Duration** | `600 blocks` (~1 hour) |
| **Session Duration** | `600 blocks` (~1 hour) |
| **Runtime Pallets (17)** | BABE, GRANDPA, Session, Balances, DPoS, EcoPallet, CarbonPallet, DEXPallet, VestingPallet, TokenomicsPallet, Sudo, Timestamp, System, Utility, TransactionPayment, Authorship, ImOnline |

---

## 2. Hardware & Operating System Requirements

### 2.1. Hardware Specifications

| Resource | Minimum Requirement | Recommended Specification |
| :--- | :--- | :--- |
| **CPU** | 4 Cores (x86_64, 2.8+ GHz) | 8+ Cores (3.2+ GHz, AES-NI enabled) |
| **RAM** | 16 GB DDR4 | 32 GB DDR4/DDR5 ECC |
| **Storage** | 250 GB Enterprise NVMe SSD | 1 TB NVMe SSD (High IOPS required for RocksDB state trie) |
| **Network** | 100 Mbps unmetered | 1 Gbps redundant uplink, static IPv4 address |

> **Warning:** Do not run validator nodes on shared hard drives (HDDs) or standard SATA SSDs. RocksDB state reads/writes require sub-millisecond I/O latency to prevent missed block slots in BABE.

### 2.2. Operating System
* **OS:** Ubuntu 22.04 LTS (Jammy Jellyfish) or Ubuntu 24.04 LTS 64-bit Server edition
* **Kernel:** 5.15+ (x86_64 or aarch64)

---

## 3. Prerequisites & Environment Setup

### 3.1. Install System Dependencies

Update apt dependencies and install required C/C++ compilation tools, SSL libraries, and utility packages:

```bash
sudo apt-get update && sudo apt-get install -y \
  build-essential \
  clang \
  cmake \
  git \
  curl \
  wget \
  pkg-config \
  libssl-dev \
  llvm \
  libclang-dev \
  protobuf-compiler \
  ufw \
  fail2ban \
  ca-certificates \
  gnupg \
  lsb-release
```

### 3.2. Install Docker & Docker Compose (Optional / Recommended for Sidecars)

```bash
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update && sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
```

### 3.3. Install Rust Toolchain

Verdis Chain requires Rust 1.78 or higher and the `wasm32-unknown-unknown` target for WebAssembly runtime compilation.

```bash
# Install rustup
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# Source Rust environment
source $HOME/.cargo/env

# Set active toolchain to 1.78+ stable and add WebAssembly compilation target
rustup default 1.78.0
rustup target add wasm32-unknown-unknown
rustup component add rust-src clippy rustfmt

# Verify Rust version
rustc --version
```

---

## 4. Building Verdis Node from Source

### 4.1. Clone Repository & Prepare Directory Structure

```bash
# Clone the repository
sudo mkdir -p /opt/verdis-chain-rust
sudo chown -R $USER:$USER /opt/verdis-chain-rust
git clone https://github.com/verdis-chain/verdis-chain-rust.git /opt/verdis-chain-rust
cd /opt/verdis-chain-rust
```

### 4.2. Compile Release Binary

Compile the release binary with optimizations enabled:

```bash
cd /opt/verdis-chain-rust
cargo build --release

# Verify the binary is produced at the target path
/opt/verdis-chain-rust/target/release/verdis --version
```

---

## 5. Key Generation & Management

A Verdis validator node requires keys for block production, finality voting, and node identification:
1. **BABE Key (`babe`):** `sr25519` key for block authoring slots.
2. **GRANDPA Key (`gran`):** `ed25519` key for deterministic finality voting.
3. **ImOnline Key (`imon`):** `sr25519` key for liveness reporting.
4. **Stash & Controller Accounts:** Cold/warm accounts holding VRDX stake and submitting governance/staking extrinsics.

### 5.1. Installing Subkey

`subkey` is Substrate's key generation utility:

```bash
cargo install --force --git https://github.com/paritytech/polkadot-sdk subkey
```

### 5.2. Generate Account & Session Keys via Subkey

Generate Stash and Controller accounts using SS58 prefix 909:

```bash
# Generate Stash keypair
subkey generate --scheme sr25519 --network 909

# Generate GRANDPA keypair
subkey generate --scheme ed25519 --network 909
```

Alternatively, use the Verdis node built-in key generator:

```bash
/opt/verdis-chain-rust/target/release/verdis key generate --scheme sr25519
/opt/verdis-chain-rust/target/release/verdis key generate --scheme ed25519
```

### 5.3. Injecting Keys into Node Keystore

Store session keys directly into the local keystore directory `/opt/verdis-chain-rust/data/chains/verdis_chain/keystore`:

```bash
# Create keystore directory
mkdir -p /opt/verdis-chain-rust/data/chains/verdis_chain/keystore
chmod 700 /opt/verdis-chain-rust/data/chains/verdis_chain/keystore

# Insert BABE Key (sr25519)
/opt/verdis-chain-rust/target/release/verdis key insert \
  --base-path /opt/verdis-chain-rust/data \
  --chain /opt/verdis-chain-rust/customSpecRaw.json \
  --suri "YOUR_SECRET_SEED_PHRASE" \
  --key-type babe \
  --scheme sr25519

# Insert GRANDPA Key (ed25519)
/opt/verdis-chain-rust/target/release/verdis key insert \
  --base-path /opt/verdis-chain-rust/data \
  --chain /opt/verdis-chain-rust/customSpecRaw.json \
  --suri "YOUR_SECRET_SEED_PHRASE" \
  --key-type gran \
  --scheme ed25519

# Insert ImOnline Key (sr25519)
/opt/verdis-chain-rust/target/release/verdis key insert \
  --base-path /opt/verdis-chain-rust/data \
  --chain /opt/verdis-chain-rust/customSpecRaw.json \
  --suri "YOUR_SECRET_SEED_PHRASE" \
  --key-type imon \
  --scheme sr25519
```

---

## 6. Chain Specification & Network Join Configuration

### 6.1. Running Single-Node Development Chain (Alice)

For local development or testing, use the pre-baked `--dev` chain spec running as standard validator Alice:

```bash
/opt/verdis-chain-rust/target/release/verdis \
  --dev \
  --base-path /opt/verdis-chain-rust/data \
  --port 30333 \
  --rpc-port 9944 \
  --validator
```

### 6.2. Generating Custom Multi-Node Chain Spec

For multi-node production or testnet deployment, build and customize the spec:

```bash
# Export standard specification template
/opt/verdis-chain-rust/target/release/verdis build-spec --chain dev > /opt/verdis-chain-rust/customSpec.json

# Convert plain JSON spec into raw binary spec (enforces determinism)
/opt/verdis-chain-rust/target/release/verdis build-spec --chain /opt/verdis-chain-rust/customSpec.json --raw > /opt/verdis-chain-rust/customSpecRaw.json
```

---

## 7. Node Configuration & Execution Parameters

### 7.1. Validator CLI Flag Breakdown

When running as an active validator, run with mandatory consensus and RPC security flags:

```bash
/opt/verdis-chain-rust/target/release/verdis \
  --validator \
  --chain /opt/verdis-chain-rust/customSpecRaw.json \
  --base-path /opt/verdis-chain-rust/data \
  --name "Verdis-Primary-Validator" \
  --port 30333 \
  --rpc-port 9944 \
  --rpc-methods Safe \
  --rpc-cors all \
  --prometheus-port 9615 \
  --prometheus-external \
  --telemetry-url "wss://telemetry.verdischain.com/submit/ 0" \
  --bootnodes /ip4/91.98.160.145/tcp/30333/p2p/12D3KooWVerdisBootstrapPeerId
```

| Flag | Purpose |
| :--- | :--- |
| `--validator` | Enables BABE slot authoring and GRANDPA finality voting |
| `--chain` | Path to custom raw specification file |
| `--base-path` | Root directory for RocksDB blockchain state & keystore |
| `--port 30333` | P2P gossip protocol port |
| `--rpc-port 9944` | Local JSON-RPC / WebSocket communication port |
| `--rpc-methods Safe` | Restricts dangerous admin/unsafe RPC endpoints from external access |
| `--prometheus-port 9615` | Exposes Substrate Prometheus metrics |
| `--prometheus-external` | Binds Prometheus metrics endpoint to `0.0.0.0` |

---

## 8. Systemd Service Configuration

Set up `verdis-node.service` for automatic daemon lifecycle management and persistence across reboots.

### 8.1. Create Dedicated Service User

```bash
sudo useradd -r -s /bin/false verdis
sudo mkdir -p /opt/verdis-chain-rust/data
sudo chown -R verdis:verdis /opt/verdis-chain-rust
```

### 8.2. Systemd Unit File Creation

Create `/etc/systemd/system/verdis-node.service`:

```ini
[Unit]
Description=Verdis Chain Validator Node
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=verdis
Group=verdis
WorkingDirectory=/opt/verdis-chain-rust
ExecStart=/opt/verdis-chain-rust/target/release/verdis \
  --validator \
  --chain /opt/verdis-chain-rust/customSpecRaw.json \
  --base-path /opt/verdis-chain-rust/data \
  --name Verdis-Validator-01 \
  --port 30333 \
  --rpc-port 9944 \
  --rpc-methods Safe \
  --rpc-cors all \
  --prometheus-port 9615 \
  --prometheus-external

Restart=always
RestartSec=10
LimitNOFILE=65536
LimitNPROC=65536

# Security Hardening Settings
ProtectSystem=full
ProtectHome=true
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

### 8.3. Enable and Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable verdis-node.service
sudo systemctl start verdis-node.service

# Check service status
sudo systemctl status verdis-node.service

# Stream realtime logs
journalctl -u verdis-node.service -f -o cat
```

---

## 9. Network Firewall & Nginx Reverse Proxy Setup

### 9.1. Firewall Configuration (UFW)

Secure the host firewall, allowing external P2P traffic while binding RPC and internal metrics appropriately.

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH management
sudo ufw allow 22/tcp

# Allow Web traffic for Nginx SSL proxying
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow Substrate P2P Gossip protocol
sudo ufw allow 30333/tcp

# Enable Firewall
sudo ufw --force enable
sudo ufw status verbose
```

### 9.2. Nginx Reverse Proxy & SSL Setup

Create `/etc/nginx/sites-available/verdischain` to proxy public WSS/HTTPS RPC queries to port 9944:

```nginx
server {
    listen 80;
    server_name verdischain.com www.verdischain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name verdischain.com www.verdischain.com;

    ssl_certificate /etc/letsencrypt/live/verdischain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/verdischain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://127.0.0.1:9944;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 86400;
    }
}
```

Enable link and reload Nginx:

```bash
sudo ln -sf /etc/nginx/sites-available/verdischain /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 10. Log Rotation Setup

Configure `/etc/logrotate.d/verdis` to manage node logs:

```text
/opt/verdis-chain-rust/data/node.log {
    daily
    rotate 14
    maxsize 100M
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
}
```

---

## 11. Monitoring Integration

Ensure Prometheus (port `9615`) can collect Substrate performance data:

```yaml
# /etc/prometheus/prometheus.yml snippet
scrape_configs:
  - job_name: 'verdis_validator'
    scrape_interval: 5s
    static_configs:
      - targets: ['127.0.0.1:9615']
        labels:
          role: 'validator'
          node_id: 'validator-01'
```

Key Substrate metrics:
* `substrate_block_height{status="best"}`
* `substrate_block_height{status="finalized"}`
* `substrate_sub_libp2p_peers_count`
* `substrate_process_start_time_seconds`

---

## 12. Key Backup & Disaster Recovery Setup

### 12.1. Automated Keystore & Chain Backup Script

Set up daily automated backup scheduled at 02:00 AM UTC with retention policies (7 daily, 4 weekly, 12 monthly).

Create `/opt/verdis-backup.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

BACKUP_ROOT="/var/backups/verdis"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="${BACKUP_ROOT}/daily/backup_${DATE}"
KEYSTORE_SRC="/opt/verdis-chain-rust/data/chains/verdis_chain/keystore"

mkdir -p "${BACKUP_DIR}"

# 1. Backup Session Keystore
if [ -d "${KEYSTORE_SRC}" ]; then
    cp -r "${KEYSTORE_SRC}" "${BACKUP_DIR}/keystore"
fi

# 2. Backup System Configuration & Specs
cp /opt/verdis-chain-rust/customSpecRaw.json "${BACKUP_DIR}/" || true

# 3. Create Archive
tar -czf "${BACKUP_ROOT}/daily/verdis_backup_${DATE}.tar.gz" -C "${BACKUP_DIR}" .
rm -rf "${BACKUP_DIR}"

# Retention cleanup (keep 7 daily, 4 weekly, 12 monthly)
find "${BACKUP_ROOT}/daily" -type f -mtime +7 -delete
```

Set executable permissions and configure cron job:

```bash
sudo chmod +x /opt/verdis-backup.sh
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/verdis-backup.sh >> /var/log/verdis-backup.log 2>&1") | crontab -
```

---

## 13. Validator On-Chain Registration & Session Keys

### 13.1. Rotate & Fetch Session Keys via Local RPC

Execute the `author_rotateKeys` RPC call against your local running node:

```bash
curl -H "Content-Type: application/json" \
  -d '{"id":1, "jsonrpc":"2.0", "method": "author_rotateKeys", "params":[]}' \
  http://localhost:9944
```

Example Result Output:
```json
{
  "jsonrpc": "2.0",
  "result": "0x9c3d4f1e5a8b7c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
  "id": 1
}
```

### 13.2. Submitting Session Keys On-Chain

1. Open the Verdis Explorer / Polkadot.js Apps UI connected to `wss://verdischain.com`.
2. Navigate to **Developer → Extrinsics**.
3. Select Controller account.
4. Choose **session → setKeys(keys, proof)**.
5. Paste the hex output returned by `author_rotateKeys`.
6. Submit and sign extrinsic.

### 13.3. Registering as Validator Authority via Sudo / Governance

In dev or initial network bootstrapping:
1. Navigate to **Extrinsics → sudo(opaqueCall)**.
2. Select **dpos / validatorSet → addValidator(validator_account_id)** or **session → setKeys**.
3. Submit extrinsic. The node will join the validator set at the next Session boundary (`600 blocks`).

---

## 14. Session Key Rotation Procedure

To update or cycle validator session keys:

1. Send `author_rotateKeys` RPC call to local node host.
2. Capture the returned raw hex payload.
3. Submit the hex payload via `session.setKeys` extrinsic from the Controller account.
4. Wait 1 Session epoch (`600 blocks` / ~1 hour) for key changes to take effect in consensus block authoring.

---

## 15. Security Hardening Guidelines

1. **Non-Root Execution:** Always run `verdis-node.service` under unprivileged user `verdis`.
2. **Keystore Permissions:** Ensure `/opt/verdis-chain-rust/data/chains/verdis_chain/keystore` is owned exclusively by `verdis:verdis` with `chmod 700`.
3. **SSH Hardening:** Edit `/etc/ssh/sshd_config`:
   ```text
   PermitRootLogin no
   PasswordAuthentication no
   PubkeyAuthentication yes
   Port 22
   ```
4. **Fail2ban Protection:** Configure `/etc/fail2ban/jail.local`:
   ```ini
   [sshd]
   enabled = true
   maxretry = 3
   bantime = 86400
   ```

---

## 16. Operational Troubleshooting

| Symptom | Root Cause | Solution |
| :--- | :--- | :--- |
| **Node not syncing (0 peers)** | Firewall blocking P2P port 30333 or bad bootnodes | Verify `ufw status`. Test TCP connectivity: `nc -zv 91.98.160.145 30333`. |
| **Node non-finalizing** | GRANDPA key missing or insufficient finality votes | Ensure GRANDPA (`gran`) key is injected in keystore and valid in session set. |
| **Missing BABE slots** | System clock drift or excessive CPU load | Sync system clock via ntp/chrony (`timedatectl set-ntp true`). Verify high IOPS storage. |
| **RPC Connection Refused** | RPC port 9944 not listening or bound to 127.0.0.1 | Verify `verdis-node.service` parameters and Nginx proxy settings. |

---

## 17. Upgrading Validator Binary

To perform standard client binary updates:

```bash
# 1. Stop service
sudo systemctl stop verdis-node.service

# 2. Pull updated repository code
cd /opt/verdis-chain-rust
git fetch origin
git checkout tags/v2.1.0

# 3. Rebuild release binary
cargo build --release

# 4. Restart service
sudo systemctl start verdis-node.service

# 5. Monitor logs and finality
journalctl -u verdis-node.service -f -o cat
```
