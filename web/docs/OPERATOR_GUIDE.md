# Verdis Chain Node Operator Guide

This document provides complete technical instructions for building, running, monitoring, tuning, and maintaining a **Verdis Chain v2.0.0** node.

---

## 1. Node Specifications & Infrastructure Summary

| Parameter | Specification / Value | Notes |
| :--- | :--- | :--- |
| **Node Version** | Verdis Chain v2.0.0 | Built with Rust & Substrate framework |
| **Consensus Engine** | BABE (Block Authoring) + GRANDPA (Finality) | Block time: 6s, Epoch: 600 slots, Session: 600 blocks |
| **Native Token** | VRDX (9 Decimals, SS58 Format: `909`) | Total Supply: 100,000,000,000 VRDX |
| **Server Host IP** | `91.98.160.145` | Primary deployment host |
| **Domain Name** | `verdischain.com` | SSL certificate expires Nov 1, 2026 |
| **Node Binary Path** | `/opt/verdis-chain-rust/target/release/verdis` | Release binary build location |
| **Chain Data Directory** | `/opt/verdis-chain-rust/data` | RocksDB state database & keystore directory |
| **Default Chain Spec** | Dev chain (Single validator: `Alice`) | Chain ID / SS58 Prefix: `909` |
| **Systemd Service** | `verdis-node.service` | Unit file at `/etc/systemd/system/verdis-node.service` |
| **Nginx Config Path** | `/etc/nginx/sites-available/verdischain` | Reverse proxy for HTTPS/WSS |
| **Log Rotation Path** | `/etc/logrotate.d/verdis` | Daily, 100M trigger, 14 days retention |
| **Backup Script Path** | `/opt/verdis-backup.sh` | Automated RocksDB & keystore backup |
| **Health Check Script** | `/opt/verdis-health-check.sh` | Local RPC status & metric monitoring |
| **Network Ports** | `30333` (P2P), `9944` (RPC), `80/443` (HTTP/S) | Protected by UFW firewall |

---

## 2. Prerequisites & Environment Setup

### 2.1. Hardware Requirements

| Resource | Minimum Specification | Recommended Specification |
| :--- | :--- | :--- |
| **CPU** | 4 Cores (x86_64 or AArch64) | 8 Cores (3.0 GHz+ modern x86_64 / ARM) |
| **RAM** | 16 GB DDR4 | 32 GB DDR4/DDR5 ECC |
| **Storage** | 250 GB SSD (SATA III) | 1 TB NVMe SSD (High IOPS required for RocksDB state trie) |
| **Network** | 100 Mbps unmetered | 1 Gbps redundant network connection |

### 2.2. Operating System
* Tested OS: **Ubuntu 22.04 LTS** or **Ubuntu 24.04 LTS** (Linux Kernel 5.15+)
* Architecture: `x86_64` or `aarch64`

### 2.3. System Build Dependencies
Install required toolchain packages, build tools, and cryptographic libraries:

```bash
sudo apt-get update && sudo apt-get install -y \
  build-essential \
  clang \
  cmake \
  curl \
  git \
  libssl-dev \
  pkg-config \
  protobuf-compiler \
  llvm \
  libclang-dev \
  ufw \
  logrotate \
  jq
```

### 2.4. Rust & WebAssembly (WASM) Toolchain
Verdis Chain requires a stable Rust toolchain and the `wasm32-unknown-unknown` target for compiling runtime WebAssembly blobs.

```bash
# Install rustup and Rust toolchain
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source $HOME/.cargo/env

# Ensure stable channel and add WASM build target
rustup default stable
rustup update
rustup target add wasm32-unknown-unknown
```

---

## 3. Build Instructions

### 3.1. Fetching Source Code
Clone the official Verdis repository to `/opt/verdis-chain-rust`:

```bash
sudo mkdir -p /opt/verdis-chain-rust
sudo chown -R $USER:$USER /opt/verdis-chain-rust
cd /opt/verdis-chain-rust
git clone https://github.com/verdis-chain/verdis-chain.git .
```

### 3.2. Linker Configuration & WASM Compilation Flags
The Substrate runtime compilation requires WebAssembly linker settings. Configure `build.rs` or export `RUSTFLAGS` to allow undefined symbols during WASM compilation:

```bash
export RUSTFLAGS="-C link-arg=--allow-undefined"
export WASM_BUILD_TOOLCHAIN=stable
```

Ensure `build.rs` in the runtime crate includes WASM target directives:

```rust
// build.rs
fn main() {
    #[cfg(feature = "std")]
    {
        substrate_wasm_builder::WasmBuilder::new()
            .with_current_project()
            .export_heap_base()
            .import_memory()
            .append_to_rustflags("-C")
            .append_to_rustflags("link-arg=--allow-undefined")
            .build();
    }
}
```

### 3.3. Compiling the Binary
Execute release compilation with cargo:

```bash
cd /opt/verdis-chain-rust
cargo build --release
```

Verify that the compiled binary is located at `/opt/verdis-chain-rust/target/release/verdis`:

```bash
/opt/verdis-chain-rust/target/release/verdis --version
# Expected Output: verdis 2.0.0-x86_64-linux-gnu
```

---

## 4. Node Startup & Systemd Integration

### 4.1. System Service Configuration
Create a dedicated system user `verdis` and data directory `/opt/verdis-chain-rust/data`:

```bash
sudo useradd -r -s /bin/false verdis
sudo mkdir -p /opt/verdis-chain-rust/data
sudo chown -R verdis:verdis /opt/verdis-chain-rust
```

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
  --chain dev \
  --validator \
  --alice \
  --base-path /opt/verdis-chain-rust/data \
  --port 30333 \
  --rpc-port 9944 \
  --rpc-cors all \
  --rpc-methods Safe \
  --name "Verdis-Validator-Alice" \
  --telemetry-url "wss://telemetry.polkadot.io/submit/ 0" \
  --prometheus-port 9615 \
  --prometheus-external

Restart=always
RestartSec=5s
LimitNOFILE=65536
MemoryMax=28G
MemoryHigh=24G
KillMode=process

[Install]
WantedBy=multi-user.target
```

### 4.2. CLI Flags Reference

| CLI Flag | Parameter Value | Explanation |
| :--- | :--- | :--- |
| `--chain` | `dev` | Selects development chain specification |
| `--validator` | N/A | Enables block production & GRANDPA voting |
| `--alice` | N/A | Injects predefined `Alice` development validator keys into keystore |
| `--base-path` | `/opt/verdis-chain-rust/data` | Root path for state DB (`db/`) and keystore (`keystore/`) |
| `--port` | `30333` | P2P listening port |
| `--rpc-port` | `9944` | JSON-RPC / WebSocket backend port (bound to localhost) |
| `--rpc-methods` | `Safe` | Exposes only safe RPC calls; blocks key insertion / admin APIs over public proxies |
| `--rpc-cors` | `all` | CORS handling (restricted upstream by Nginx) |

### 4.3. Service Operations Commands

```bash
# Reload systemd manager configuration
sudo systemctl daemon-reload

# Enable node to start on boot
sudo systemctl enable verdis-node

# Start the node service
sudo systemctl start verdis-node

# Inspect service status
sudo systemctl status verdis-node

# Follow real-time node logs
sudo journalctl -u verdis-node -f -o cat
```

---

## 5. Monitoring & Operational Health

### 5.1. Log File Inspection
Node output is streamed via systemd journal and configured log sink:

```bash
# View last 100 log entries
sudo journalctl -u verdis-node -n 100 --no-pager

# Search for consensus warnings or block authoring events
sudo journalctl -u verdis-node | grep -E "BABE|GRANDPA|Prepared block for proposing"
```

### 5.2. Core Metrics & Key Indicators

1. **Block Production Rate:**
   * Target block time: `6.0 seconds`.
   * Slots per epoch: `600 slots` (~1 hour).
   * Verify block sequence advancement every 6 seconds in logs:
     `✨ Imported #1042 (0x7a3f…8b12)`
2. **GRANDPA Finality Lag:**
   * Calculated as `Current Best Block Number - Finalized Block Number`.
   * Acceptable operational threshold: `< 3 blocks`.
   * Warning threshold: `> 10 blocks` (Indicates voter set offline or network split).

### 5.3. Operational Health Check Script (`/opt/verdis-health-check.sh`)
Create `/opt/verdis-health-check.sh` to automate local health validation:

```bash
#!/usr/bin/env bash
# Verdis Node Health Check Script
set -euo pipefail

RPC_URL="http://127.0.0.1:9944"

# 1. Query system health
HEALTH_JSON=$(curl -s -H "Content-Type: application/json" \
  -d '{"id":1, "jsonrpc":"2.0", "method":"system_health", "params":[]}' "$RPC_URL")

IS_SYNCING=$(echo "$HEALTH_JSON" | jq -r '.result.isSyncing // empty')
PEERS=$(echo "$HEALTH_JSON" | jq -r '.result.peers // 0')

if [ -z "$IS_SYNCING" ]; then
  echo "CRITICAL: Verdis RPC on port 9944 is unreachable!"
  exit 2
fi

# 2. Query Best Header & Finalized Head
BEST_HEADER_JSON=$(curl -s -H "Content-Type: application/json" \
  -d '{"id":1, "jsonrpc":"2.0", "method":"chain_getHeader", "params":[]}' "$RPC_URL")
BEST_BLOCK_HEX=$(echo "$BEST_HEADER_JSON" | jq -r '.result.number')
BEST_BLOCK=$((BEST_BLOCK_HEX))

FINALIZED_HASH_JSON=$(curl -s -H "Content-Type: application/json" \
  -d '{"id":1, "jsonrpc":"2.0", "method":"chain_getFinalizedHead", "params":[]}' "$RPC_URL")
FINALIZED_HASH=$(echo "$FINALIZED_HASH_JSON" | jq -r '.result')

FINALIZED_HEADER_JSON=$(curl -s -H "Content-Type: application/json" \
  -d '{"id":1, "jsonrpc":"2.0", "method":"chain_getHeader", "params":["'$FINALIZED_HASH'"]}' "$RPC_URL")
FINALIZED_BLOCK_HEX=$(echo "$FINALIZED_HEADER_JSON" | jq -r '.result.number')
FINALIZED_BLOCK=$((FINALIZED_BLOCK_HEX))

LAG=$((BEST_BLOCK - FINALIZED_BLOCK))

echo "=== Verdis Chain Node Status ==="
echo "Node Syncing: $IS_SYNCING"
echo "Connected Peers: $PEERS"
echo "Best Block: #$BEST_BLOCK"
echo "Finalized Block: #$FINALIZED_BLOCK"
echo "Finality Lag: $LAG blocks"

if [ "$LAG" -gt 10 ]; then
  echo "WARNING: GRANDPA finality lag exceeds threshold ($LAG > 10)!"
  exit 1
fi

echo "STATUS: OK"
exit 0
```

Make the script executable:

```bash
sudo chmod +x /opt/verdis-health-check.sh
sudo /opt/verdis-health-check.sh
```

---

## 6. Log Rotation Setup

To prevent node logs from consuming system disk space, configure logrotate.

Create `/etc/logrotate.d/verdis`:

```etc
/var/log/verdis/*.log {
    daily
    rotate 14
    size 100M
    missingok
    notifempty
    compress
    delaycompress
    copytruncate
    create 0640 verdis verdis
}
```

Verify and test logrotate configuration:

```bash
sudo mkdir -p /var/log/verdis
sudo chown verdis:verdis /var/log/verdis
sudo logrotate -d /etc/logrotate.d/verdis
```

---

## 7. Performance Tuning

### 7.1. Rust Logging Filter (`RUST_LOG`)
For maximum throughput, avoid excessive trace logging in production. Specify log level filters in `/etc/systemd/system/verdis-node.service` via environment variable:

```ini
Environment="RUST_LOG=info,babe=debug,grandpa=info,runtime=info"
```

### 7.2. Open File Descriptors Limit
Substrate maintains active peer sockets and multiple RocksDB file descriptors. Increase file handle limits in systemd:

```ini
LimitNOFILE=65536
```

Apply system-level limit via `/etc/security/limits.conf`:

```etc
verdis soft nofile 65536
verdis hard nofile 65536
```

### 7.3. Memory Allocation & RocksDB State Tuning
* **Memory Limits:** Set `MemoryHigh=24G` and `MemoryMax=28G` in systemd unit file to prevent out-of-memory kernel panics.
* **Database Pruning:** For non-archive operator nodes, run with `--pruning 256` to keep state trie size manageable.
* **WASM Runtime Execution:** Use compiled execution strategy `--wasm-execution Compiled`.

### 7.4. Kernel Network Stack Tuning (`sysctl`)
Append the following parameters to `/etc/sysctl.d/99-verdis.conf`:

```ini
net.core.somaxconn = 8192
net.ipv4.tcp_rmem = 4096 87380 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216
net.core.netdev_max_backlog = 10000
```

Apply settings:
```bash
sudo sysctl --system
```

---

## 8. Common Issues & Troubleshooting

### 8.1. Node Not Producing Blocks
* **Symptom:** Logs show `0 blocks produced` and slot numbers increment without importing new blocks.
* **Causes:**
  1. Keystore missing validator keys (BABE `61757468` / GRANDPA `6772616e`).
  2. System clock skew or NTP drift (> 1000ms out of sync).
  3. Node started without `--validator` flag.
* **Resolution:**
  ```bash
  # Check system clock synchronization
  timedatectl status
  sudo systemctl restart systemd-timesyncd

  # Verify keystore content
  ls -la /opt/verdis-chain-rust/data/chains/dev/keystore
  ```

### 8.2. Public RPC Unreachable (`502 Bad Gateway` or Timeout)
* **Symptom:** `https://verdischain.com/rpc` fails, but `curl http://127.0.0.1:9944` responds locally.
* **Causes:**
  1. Nginx proxy service stopped or configuration error.
  2. Firewall blocking ports 80/443.
* **Resolution:**
  ```bash
  # Check Nginx service
  sudo systemctl status nginx
  sudo nginx -t

  # Check UFW firewall status
  sudo ufw status verbose
  # Ensure 22, 80, 443, 30333 are ALLOWED
  sudo ufw allow 80/tcp
  sudo ufw allow 443/tcp
  sudo ufw allow 30333/tcp
  ```

### 8.3. SSL Certificate Expiry Handling
* **Domain:** `verdischain.com`
* **Certificate Expiry Date:** Nov 1, 2026 (Let's Encrypt TLS)
* **Renewal Verification:**
  ```bash
  # Test dry-run renewal
  sudo certbot renew --dry-run

  # Check certificate expiration date
  sudo openssl x509 -in /etc/letsencrypt/live/verdischain.com/fullchain.pem -noout -dates
  ```

### 8.4. Disk Space Exhaustion
* **Symptom:** Node panics with `IO error: No space left on device` or RocksDB write failure.
* **Resolution:**
  ```bash
  # Check disk usage
  df -h /opt/verdis-chain-rust/data

  # Clean old journal files
  sudo journalctl --vacuum-time=3d

  # Compress or prune database if needed
  ```

### 8.5. Out Of Memory (OOM) Kill
* **Symptom:** Node crashes abruptly; `dmesg -T` shows `Out of memory: Kill process (verdis)`.
* **Resolution:**
  Ensure systemd memory limits (`MemoryMax=28G`) are active and swap space (4GB+) is configured:
  ```bash
  sudo fallocate -l 4G /swapfile
  sudo chmod 600 /swapfile
  sudo mkswap /swapfile
  sudo swapon /swapfile
  ```

---

## 9. Upgrade Procedure

Follow this zero-data-corruption upgrade protocol when updating `verdis` node binary versions:

### Step 1: Stop Running Node Service
```bash
sudo systemctl stop verdis-node
```

### Step 2: Backup Current State & Keys
```bash
sudo /opt/verdis-backup.sh
```

### Step 3: Fetch Updated Code & Rebuild Binary
```bash
cd /opt/verdis-chain-rust
git fetch origin
git checkout v2.0.0 # Or target tag
RUSTFLAGS="-C link-arg=--allow-undefined" cargo build --release
```

### Step 4: Perform Chain Purge (Optional for Hard Resets / Dev Chain)
If updating to an incompatible spec or resetting dev chain state:
```bash
/opt/verdis-chain-rust/target/release/verdis purge-chain --dev -y --base-path /opt/verdis-chain-rust/data
```

### Step 5: Restart Node & Verify
```bash
sudo systemctl start verdis-node
sudo journalctl -u verdis-node -f -o cat
```

---

## 10. Backup & Restore Procedures

### 10.1. What to Backup
1. **Keystore Directory:** `/opt/verdis-chain-rust/data/chains/dev/keystore/`
2. **RocksDB State Database:** `/opt/verdis-chain-rust/data/chains/dev/db/`
3. **Configuration & Service Files:**
   * `/etc/systemd/system/verdis-node.service`
   * `/etc/nginx/sites-available/verdischain`

### 10.2. Automated Backup Script (`/opt/verdis-backup.sh`)
Create `/opt/verdis-backup.sh`:

```bash
#!/usr/bin/env bash
# Verdis Chain Backup Script
set -euo pipefail

BACKUP_DIR="/var/backups/verdis"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
TARGET_ARCHIVE="${BACKUP_DIR}/verdis_backup_${TIMESTAMP}.tar.gz"
DATA_PATH="/opt/verdis-chain-rust/data"

mkdir -p "$BACKUP_DIR"

echo "[1/4] Stopping verdis-node service..."
systemctl stop verdis-node || true

echo "[2/4] Archiving chain state database and keystore..."
tar -czf "$TARGET_ARCHIVE" \
  -C "$DATA_PATH" chains/dev/keystore chains/dev/db

echo "[3/4] Restarting verdis-node service..."
systemctl start verdis-node

echo "[4/4] Cleaning backups older than 14 days..."
find "$BACKUP_DIR" -type f -name "verdis_backup_*.tar.gz" -mtime +14 -delete

echo "Backup completed successfully: $TARGET_ARCHIVE"
```

Make backup script executable:
```bash
sudo chmod +x /opt/verdis-backup.sh
```

### 10.3. Restoration Workflow

```bash
# 1. Stop node service
sudo systemctl stop verdis-node

# 2. Extract backup file to data directory
sudo tar -xzf /var/backups/verdis/verdis_backup_20260803_180000.tar.gz -C /opt/verdis-chain-rust/data/

# 3. Fix ownership
sudo chown -R verdis:verdis /opt/verdis-chain-rust/data

# 4. Start node service
sudo systemctl start verdis-node
```

---

## 11. Health Check Endpoints & RPC Reference

All endpoints can be queried via JSON-RPC 2.0 at `http://127.0.0.1:9944` or public gateway `https://verdischain.com/rpc`.

### 11.1. `system_health`
Returns current sync status, connected peer count, and operational state.

* **Request:**
```bash
curl -s -X POST http://127.0.0.1:9944 \
  -H "Content-Type: application/json" \
  -d '{"id":1, "jsonrpc":"2.0", "method":"system_health", "params":[]}'
```

* **Response Format:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "peers": 0,
    "isSyncing": false,
    "shouldHavePeers": false
  },
  "id": 1
}
```

### 11.2. `chain_getHeader`
Retrieves header parameters (block number, state root, parent hash, extrinsics root) for target or best block.

* **Request:**
```bash
curl -s -X POST http://127.0.0.1:9944 \
  -H "Content-Type: application/json" \
  -d '{"id":1, "jsonrpc":"2.0", "method":"chain_getHeader", "params":[]}'
```

* **Response Format:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "parentHash": "0x1d4a...8e92",
    "number": "0x412",
    "stateRoot": "0x9f8c...3b11",
    "extrinsicsRoot": "0x0312...7a4e",
    "digest": { "logs": [] }
  },
  "id": 1
}
```

### 11.3. `chain_getFinalizedHead`
Returns the block hash of the latest block finalized by GRANDPA consensus.

* **Request:**
```bash
curl -s -X POST http://127.0.0.1:9944 \
  -H "Content-Type: application/json" \
  -d '{"id":1, "jsonrpc":"2.0", "method":"chain_getFinalizedHead", "params":[]}'
```

* **Response Format:**
```json
{
  "jsonrpc": "2.0",
  "result": "0x6f91a283c749102b48e3d2197f261907e4d2a104f2910d8a571f3029a0293112",
  "id": 1
}
```
