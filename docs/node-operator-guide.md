# Verdis Testnet Node Operator Guide

## Prerequisites
- Linux server (Ubuntu 22.04+ recommended)
- 4GB RAM minimum, 8GB recommended
- 50GB SSD storage
- Open ports: 30333 (P2P), 9944 (RPC), 9615 (Prometheus)

## Quick Start

### Docker
```bash
docker run -d --name verdis-node -p 30333:30333 -p 9944:9944 -p 9615:9615   -v verdis-data:/data verdis-chain:latest   --chain=/chain-spec-raw.json --name=my-node --base-path=/data --port=30333 --rpc-port=9944 --prometheus-external --no-mdns
```

### Binary
```bash
wget https://verdischain.com/verdis-node-linux-x86_64
chmod +x verdis-node-linux-x86_64
wget https://verdischain.com/chain-spec.json
./verdis-node-linux-x86_64 --chain=chain-spec.json --name=my-node --base-path=/opt/verdis-data --port=30333 --rpc-port=9944 --prometheus-external
```

## Network Parameters
| Parameter | Value |
|-----------|-------|
| Chain Name | Verdis Testnet |
| SS58 Format | 909 |
| Token Symbol | VRS |
| Token Decimals | 9 |
| Total Supply | 100B VRS |
| Block Time | 6 seconds |
| Session Length | 600 blocks |
| Consensus | BABE + GRANDPA |
| Validators | 5 (initial) |

## RPC Endpoints
- HTTP RPC: https://verdischain.com/rpc
- WebSocket: wss://verdischain.com/ws
- Faucet: POST https://verdischain.com/faucet (address=your-ss58)
