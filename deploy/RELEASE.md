# Verdis Chain v2.0.0 — Production Release Package Manifest

**Release Version:** v2.0.0  
**Target Architecture:** `x86_64-unknown-linux-gnu`  
**License:** Apache-2.0  
**Release Date:** August 3, 2026  

---

## 1. Overview & Chain Specifications

Verdis Chain v2.0.0 is a high-performance Substrate-based Layer-1 blockchain runtime and node built in Rust. It utilizes BABE block production and GRANDPA finality with high-throughput smart contract and asset capabilities.

| Parameter | Specification / Value |
| :--- | :--- |
| **Node Version** | `v2.0.0` |
| **Spec Version** | `200` |
| **Impl Version** | `1` |
| **Native Token** | VRS |
| **Total Supply** | 100,000,000,000 VRS (100B) |
| **Decimals** | 9 |
| **SS58 Prefix** | 909 |
| **Block Time** | 6 seconds |
| **Epoch Duration** | 600 slots (1 hour) |
| **Consensus Engine** | BABE (Block Authoring) + GRANDPA (Finality) |
| **Binary Size** | ~94 MB (`verdis`) |
| **Data Directory** | `/opt/verdis-chain-rust/data` |
| **Target OS/Arch** | `x86_64-unknown-linux-gnu` (Linux x86_64) |

---

## 2. Release Artifacts Manifest

This release directory contains production deployment scripts, container definitions, specifications, and build manifests:

1. **`verdis` (Binary)**
   - Compiled release binary (~94MB, x86_64-unknown-linux-gnu) with embedded WASM runtime.
2. **`verdis_runtime.compact.compressed.wasm` (WASM Blob)**
   - Compact and compressed on-chain WASM runtime built via `substrate-wasm-builder`.
3. **`Dockerfile`**
   - Multi-stage build definition:
     - **Stage 1**: Rust 1.78 toolchain, `wasm32-unknown-unknown` target, `--allow-undefined` link flags.
     - **Stage 2**: Minimal `debian:bookworm-slim` runtime image, non-root system user `verdis` (UID 10001), healthcheck against RPC.
4. **`docker-compose.yml`**
   - Single-node production setup. Exposes RPC (`127.0.0.1:9944:9944` - localhost bound) and P2P (`30333:30333` - public), volume persistence, log rotation, and ulimit configuration (`LimitNOFILE=10000`).
5. **`docker-compose.multi.yml`**
   - 5-validator local/testnet cluster (`alice`, `bob`, `charlie`, `dave`, `eve`) with static P2P bootnode routing, key injection, healthchecks, and internal bridge networking (`verdis-net`).
6. **`version-manifest.json`**
   - Structured JSON manifest detailing runtime metadata, tokenomics, consensus parameters, and build toolchain dependencies.
7. **`checksums.sh`**
   - Executable bash script for generating and verifying SHA256 integrity hashes (`SHA256SUMS`).
8. **`Makefile`**
   - Operations Makefile providing automated targets for building, testing, Docker containerization, packaging, and checksum verification.

---

## 3. Hardware & System Requirements

### Recommended Validator Specifications
* **CPU:** 4+ cores (x86_64 with AES-NI support)
* **RAM:** 16 GB DDR4/DDR5
* **Storage:** 500 GB+ NVMe SSD (high IOPS required for state storage)
* **Network:** 100 Mbps minimum symmetric bandwidth
* **System File Limits:** `LimitNOFILE=10000` minimum (default Substrate file descriptor consumption for open peers & RocksDB handles).

---

## 4. Build Instructions

To build the release binary manually from source code:

```bash
# 1. Install WASM toolchain target
rustup target add wasm32-unknown-unknown

# 2. Build release binary in workspace root
cd /opt/verdis-chain-rust
RUSTFLAGS="-C link-arg=-Wl,--allow-undefined" cargo build --release

# 3. Binary location
ls -lh target/release/verdis
```

---

## 5. Deployment Guide

### Option A: Direct Binary Execution

```bash
/usr/local/bin/verdis \
  --chain dev \
  --base-path /opt/verdis-chain-rust/data \
  --rpc-port 9944 \
  --port 30333 \
  --rpc-methods Safe \
  --validator \
  --alice
```

### Option B: Single Node Docker Deployment

```bash
cd deploy/
make docker-build
make docker-run
```

Verify service status:
```bash
docker logs -f verdis-node
```

### Option C: 5-Node Validator Network

```bash
cd deploy/
make docker-build
make docker-multi
```

---

## 6. Verification and Health Checks

### 1. SHA256 Checksum Verification
```bash
cd deploy/
./checksums.sh --verify
```

### 2. Node RPC System Health Check
Query the local node via JSON-RPC:
```bash
curl -H "Content-Type: application/json" \
  -d '{"id":1, "jsonrpc":"2.0", "method":"system_health", "params":[]}' \
  http://127.0.0.1:9944
```
*Expected Output:*
```json
{"jsonrpc":"2.0","result":{"peers":0,"isSyncing":false,"shouldHavePeers":false},"id":1}
```

### 3. Check System Version
```bash
curl -H "Content-Type: application/json" \
  -d '{"id":1, "jsonrpc":"2.0", "method":"system_version", "params":[]}' \
  http://127.0.0.1:9944
```

---

## 7. Security Hardening & Best Practices

1. **Non-Root Execution:** The Docker container operates as dedicated non-root system user `verdis` (`UID 10001`).
2. **RPC Binding:** RPC port `9944` is explicitly bound to `127.0.0.1` on host interface. **Never** expose raw unauthenticated JSON-RPC ports publicly.
3. **Reverse Proxy:** HTTPS (ports 80/443) should be routed through Nginx with rate limiting and TLS termination before forwarding to RPC services.
4. **Log Management:** Docker containers use `json-file` log driver with `max-size: "50m"` and `max-file: "5"` to prevent disk exhaustion.
