# Verdis Chain Node & Gateway Deployment Guide

This document provides step-by-step instructions for compiling, deploying, securing, and maintaining a **Verdis Chain v2.0.0** node and Nginx gateway server.

---

## 1. System Requirements & Infrastructure Overview

### Recommended Production Hardware Specifications
* **OS:** Ubuntu 22.04 LTS or 24.04 LTS (64-bit x86_64 or ARM64)
* **CPU:** 8 physical cores (AMD EPYC, Intel Xeon, or modern ARM Graviton)
* **RAM:** 32 GB DDR4 / DDR5 ECC Memory
* **Storage:** 1 TB NVMe SSD (High IOPS required for state trie access)
* **Bandwidth:** 1 Gbps redundant network port
* **Production Host IP:** `91.98.160.145`
* **Target Domain:** `verdischain.com`

---

## 2. Prerequisites & Environment Setup

### 2.1. Installing Operating System Dependencies
Update the system and install required build tools and libraries:

```bash
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y \
  build-essential \
  clang \
  curl \
  git \
  libssl-dev \
  llvm \
  libudev-dev \
  make \
  pkg-config \
  protobuf-compiler \
  ufw \
  nginx \
  certbot \
  python3-certbot-nginx
```

### 2.2. Installing Rust & WASM Target
Install the official Rust toolchain via `rustup` and configure the `wasm32-unknown-unknown` compilation target:

```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source $HOME/.cargo/env

# Set nightly toolchain (required for Substrate WASM builder)
rustup default stable
rustup update
rustup target add wasm32-unknown-unknown --toolchain stable
```

---

## 3. Compiling Verdis Chain from Source

Clone the repository and compile the native node binary along with the WASM runtime blob:

```bash
# Clone source code
git clone https://github.com/verdis-chain/verdis-node.git
cd verdis-node

# Check out release version v2.0.0
git checkout tags/v2.0.0

# Compile release binary with substrate-wasm-builder
cargo build --release

# Verify output binary
./target/release/verdis --version
# Expected Output: verdis 2.0.0-a8c1f9e
```

---

## 4. System User & Directory Setup

To adhere to security best practices, run the node under an unprivileged system user (`verdis`):

```bash
# Create verdis system user
sudo useradd -r -m -d /opt/verdis -s /bin/bash verdis

# Create application and chain data directories
sudo mkdir -p /opt/verdis/bin /opt/verdis/data
sudo cp ./target/release/verdis /opt/verdis/bin/

# Set permissions
sudo chown -R verdis:verdis /opt/verdis
sudo chmod 755 /opt/verdis/bin/verdis
```

---

## 5. Node Running Commands & Service Configuration

### 5.1. Command Line Execution Example
Manual execution command example for local validation or node initialization:

```bash
/opt/verdis/bin/verdis \
  --chain dev \
  --base-path ./data \
  --rpc-port 9944 \
  --port 30333 \
  --rpc-methods Safe \
  --validator \
  --alice
```

### 5.2. Setting Up Systemd Service (`verdis.service`)
Create system service file at `/etc/systemd/system/verdis.service`:

```ini
[Unit]
Description=Verdis Blockchain Validator Node (VRDX)
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=verdis
Group=verdis
WorkingDirectory=/opt/verdis
ExecStart=/opt/verdis/bin/verdis \
  --chain mainnet \
  --base-path /opt/verdis/data \
  --port 30333 \
  --rpc-port 9944 \
  --rpc-cors verdischain.com \
  --rpc-methods Safe \
  --validator \
  --name "Verdis-Primary-Node" \
  --telemetry-url "wss://telemetry.verdischain.com/submit 0"

Restart=always
RestartSec=5s
LimitNOFILE=65536
StandardOutput=journal
StandardError=journal
SyslogIdentifier=verdis-node

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable verdis
sudo systemctl start verdis

# Check status and live logs
sudo systemctl status verdis
sudo journalctl -u verdis -f
```

---

## 6. Nginx Gateway & SSL Configuration

Reverse proxy public HTTP (`/rpc`) and WebSocket (`/ws`) requests on port 80/443 to the internal JSON-RPC server listening on `127.0.0.1:9944`.

### 6.1. Nginx Site Configuration (`/etc/nginx/sites-available/verdischain`)

```nginx
# Rate limiting zone definition
limit_req_zone $binary_remote_addr zone=verdis_limit:10m rate=30r/s;

server {
    listen 80;
    server_name verdischain.com www.verdischain.com rpc.verdischain.com;

    # Redirect all HTTP traffic to HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name verdischain.com www.verdischain.com;

    ssl_certificate /etc/letsencrypt/live/verdischain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/verdischain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;

    root /opt/verdis/web;
    index index.html explorer.html wallet.html;

    # Static Web Files & Explorer
    location / {
        try_files $uri $uri/ /index.html;
    }

    # JSON-RPC Proxy Endpoint
    location /rpc {
        limit_req zone=verdis_limit burst=20 nodelay;
        proxy_pass http://127.0.0.1:9944;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # CORS Enforcement
        add_header Access-Control-Allow-Origin "https://verdischain.com" always;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Content-Type, Authorization" always;
        if ($request_method = OPTIONS) { return 204; }
    }

    # WebSocket Proxy Endpoint
    location /ws {
        proxy_pass http://127.0.0.1:9944;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 86400s;
        proxy_send_timeout 86400s;
    }
}
```

Enable the configuration and reload Nginx:

```bash
sudo ln -sf /etc/nginx/sites-available/verdischain /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

### 6.2. SSL Provisioning via Let's Encrypt

```bash
sudo certbot --nginx -d verdischain.com -d www.verdischain.com -d rpc.verdischain.com \
  --non-interactive --agree-tos --email admin@verdischain.com
```

---

## 7. Firewall Rules (UFW)

Configure UFW firewall to strictly permit only essential ports:

```bash
# Set default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH, Web, and P2P communication
sudo ufw allow 22/tcp comment 'SSH'
sudo ufw allow 80/tcp comment 'HTTP'
sudo ufw allow 443/tcp comment 'HTTPS'
sudo ufw allow 30333/tcp comment 'Verdis P2P Libp2p'

# Enable firewall
sudo ufw enable
sudo ufw status verbose
```

---

## 8. Chain Data Management & Pruning

* **Base Path Directory:** `/opt/verdis/data/chains/verdis_mainnet/`
* **Pruning Configuration Options:**
  * Archive Node: `--pruning archive` (Retains complete historical state tries, required for full explorer nodes).
  * Validator / Light Node: `--pruning 256` (Default: retains last 256 state tries to conserve disk space).

To clear or reset chain data (Testnet or recovery scenario):

```bash
sudo systemctl stop verdis
sudo -u verdis /opt/verdis/bin/verdis purge-chain --chain mainnet -y
sudo systemctl start verdis
```

---

## 9. Forkless On-Chain Runtime Upgrade Process

Verdis Chain runtime upgrades are executed seamlessly on-chain without restarting host binaries or causing chain splits.

```
+-----------------------------------------------------------------------------------+
| FORKLESS RUNTIME UPGRADE WORKFLOW                                                 |
+-----------------------------------------------------------------------------------+
| 1. Increment spec_version in runtime/src/lib.rs (e.g., 200 -> 201)                |
| 2. Recompile WASM: cargo build --release                                          |
| 3. Extract WASM blob: ./target/release/wbuild/verdis-runtime/verdis_runtime.compact.compressed.wasm |
| 4. Submit Preimage: pallet_preimage::note_preimage(bytes)                         |
| 5. Execute Code Set: system::setCode(code) via Governance / Sudo                 |
| 6. Network Enacts New Runtime WASM Code At Next Block                             |
+-----------------------------------------------------------------------------------+
```
