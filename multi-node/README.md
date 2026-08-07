# Verdis Multi-Node Deployment

Complete deployment package for a 9-node Verdis testnet: 5 validators, 2 RPC nodes, 2 bootnodes.

## Architecture

```
  5 Validators  →  Block production (BABE) + Finality (GRANDPA)
  2 RPC Nodes   →  Public JSON-RPC + WebSocket API
  2 Bootnodes   →  Peer discovery and network bootstrap
```

## Quick Start

### Docker Compose (recommended)

```bash
# 1. Generate keys for all 9 nodes
./generate-keys.sh

# 2. Generate chain spec with 5 authorities
./chain-spec-generator.sh

# 3. Build Docker image
docker build -f Dockerfile -t verdis-chain:latest ..

# 4. Launch all nodes
docker compose up -d

# 5. Verify
docker compose ps
```

### Systemd (bare metal)

```bash
# Provision a validator
./validator-provision.sh 1

# Bootstrap an RPC node
./bootstrap-node.sh rpc 1

# Bootstrap a bootnode
./bootstrap-node.sh bootnode 1
```

### Systemd template services

```bash
# Start validator #3
systemctl start verdis-validator@3

# Start RPC node #2
systemctl start verdis-rpc@2

# Start bootnode #1
systemctl start verdis-bootnode@1
```

## Node Configuration

| Type | Count | P2P Port | RPC Port | RAM | CPU |
|------|-------|----------|----------|-----|-----|
| Validator | 5 | 30333-30337 | - | 4GB | 2 |
| RPC | 2 | 30338-30339 | 19944/29944 | 2GB | 1 |
| Bootnode | 2 | 30340-30341 | - | 2GB | 1 |

## Files

| File | Description |
|------|-------------|
| `docker-compose.yml` | Docker Compose for all 9 nodes |
| `Dockerfile` | Multi-stage build (Rust builder + runtime) |
| `generate-keys.sh` | Generate BABE/GRANDPA/session/node keys for all 9 nodes |
| `chain-spec-generator.sh` | Create raw chain spec with 5 authorities |
| `chain-spec.json` | Plain chain spec (template) |
| `chain-spec-raw.json` | Raw chain spec (for production use) |
| `bootstrap-node.sh` | Bootstrap a single node (validator/RPC/bootnode) |
| `validator-provision.sh` | Full validator provisioning (build + keys + systemd + firewall) |
| `systemd/verdis-validator@.service` | Systemd template for validators |
| `systemd/verdis-rpc@.service` | Systemd template for RPC nodes |
| `systemd/verdis-bootnode@.service` | Systemd template for bootnodes |
| `keys/` | Generated node keys (JSON + libp2p node keys) |

## Network Parameters

- **Chain ID:** 909
- **Token:** VRS (testnet)
- **Supply:** 100,000,000,000 VRS
- **Decimals:** 9
- **SS58:** 909
- **Block Time:** 6 seconds
- **Epoch Length:** 600 blocks (~1 hour)
- **Consensus:** BABE + GRANDPA

## Security

- All nodes run as non-root user (Docker)
- Validator keys stored in encrypted keystore
- RPC nodes behind nginx with rate limiting
- UFW firewall: SSH (22), HTTP (80), HTTPS (443), P2P (30333-30341)
- No unsafe RPC methods exposed

## Monitoring

Each node exposes Prometheus metrics on port 9615. Configure Prometheus to scrape all 9 nodes. See `../monitoring/` for the full monitoring stack.

## Troubleshooting

```bash
# Check node status
docker compose logs -f verdis-validator-1

# Check peer count
curl -s -X POST http://localhost:19944 -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"system_health","params":[]}'

# Check block height
curl -s -X POST http://localhost:19944 -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"chain_getHeader","params":[]}'

# View logs
journalctl -u verdis-validator@1 -f
```
