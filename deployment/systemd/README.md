# Verdis Chain Deployment - Systemd Services

## verdis-node.service
Primary block-producing node (--dev mode, port 9933 RPC, 30333 P2P)

## verdis-node2-sync.service
Sync-only peer node. Uses shared chain spec (not --dev) to properly sync with node1.
- Export chain spec: `verdis build-spec --dev --raw > /opt/verdis-chain-rust/verdis-dev-raw.json`
- Connects to node1 via bootnodes
- Does NOT produce blocks (sync-only, not an authority)
