# Verdis Chain Testnet — Node Join Guide

## Quick Start

```bash
# 1. Download the Verdis Chain binary
# Build from source:
git clone https://github.com/Protremix/Verdischain-.git
cd Verdischain-
cargo build --release

# 2. Download the chain spec
wget https://verdischain.com/chain-specs/testnet-canonical-raw.json

# 3. Start your node (connect to bootnodes)
./target/release/verdis \
  --chain testnet-canonical-raw.json \
  --base-path /path/to/data \
  --port 30333 \
  --rpc-port 9933 \
  --rpc-methods Safe \
  --bootnodes "/ip4/91.98.160.145/tcp/30333/p2p/12D3KooWEyoppNCUx8Yx66oV9fJnriXwCcXwDDUA2kj6vnc6iDEp" \
  --bootnodes "/ip4/91.98.160.145/tcp/30334/p2p/12D3KooWHdiAxVd8uMQR1hGWXccidmfCwLqcMpGwR6QcTP6QRMuD" \
  --bootnodes "/ip4/91.98.160.145/tcp/30335/p2p/12D3KooWSCufgHzV4fCwRijfH2k3abrpAJxTKxEvN1FDuRXA2U9x"
```

## Bootnodes

| Node | Address |
|------|---------|
| Node 1 (Alice) | /ip4/91.98.160.145/tcp/30333/p2p/12D3KooWEyoppNCUx8Yx66oV9fJnriXwCcXwDDUA2kj6vnc6iDEp |
| Node 2 (Bob) | /ip4/91.98.160.145/tcp/30334/p2p/12D3KooWHdiAxVd8uMQR1hGWXccidmfCwLqcMpGwR6QcTP6QRMuD |
| Node 3 (Charlie) | /ip4/91.98.160.145/tcp/30335/p2p/12D3KooWSCufgHzV4fCwRijfH2k3abrpAJxTKxEvN1FDuRXA2U9x |

## Ports
- P2P: 30333 (TCP, must be open to internet)
- RPC: 9933 (can be localhost-only)

## Current State (Aug 15, 2026)
- 6 nodes running on main server
- 5 peers per node
- 21 validators registered
- 6 DEX pools active
- Block production: ~6 second block time

