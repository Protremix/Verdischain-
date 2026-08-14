# Verdis Chain Testnet Runbook

## Quick Start

### Start All Nodes
```bash
systemctl start verdis-node verdis-node2 verdis-node3
```

### Stop All Nodes
```bash
systemctl stop verdis-node verdis-node2 verdis-node3
```

### Check Status
```bash
systemctl status verdis-node verdis-node2 verdis-node3
```

### Check Block Height
```bash
curl -s http://localhost:9933 -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"chain_getHeader","params":[],"id":1}'
```

### Check Finality
```bash
curl -s http://localhost:9933 -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"chain_getFinalizedHead","params":[],"id":1}'
```

### Check Peers
```bash
curl -s http://localhost:9933 -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"system_health","params":[],"id":1}'
```

### Check Validators
```bash
curl -s http://localhost:9933 -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"dpos_allValidators","params":[],"id":1}'
```

### Check DEX Pools
```bash
curl -s http://localhost:9933 -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"amm_dex_getAllPools","params":[],"id":1}'
```

## Node Configuration

| Node | Role | RPC | WS | P2P | Data Dir |
|---|---|---|---|---|---|
| verdis-node | Alice | 9933 | 9944 | 30333 | /opt/verdis-node1-data-v6 |
| verdis-node2 | Bob | 9934 | 9945 | 30334 | /opt/verdis-node2-data-v6 |
| verdis-node3 | Charlie | 9935 | 9946 | 30335 | /opt/verdis-node3-data-v6 |

## Purge and Restart (DESTRUCTIVE)

```bash
systemctl stop verdis-node verdis-node2 verdis-node3
find /opt/verdis-node1-data-v6/chains -type f -delete
find /opt/verdis-node2-data-v6/chains -type f -delete
find /opt/verdis-node3-data-v6/chains -type f -delete
systemctl start verdis-node && sleep 5
systemctl start verdis-node2 && sleep 5
systemctl start verdis-node3
```

## Rebuild Binary

```bash
cd /opt/verdis-chain-rust && source ~/.cargo/env
cargo build --release
```

## Regenerate Chain Spec

```bash
cd /opt/verdis-chain-rust
./target/release/verdis build-spec --chain=testnet --raw 2>/dev/null > chain-specs/testnet-canonical-raw.json
```

## Log Inspection

```bash
journalctl -u verdis-node --no-pager -n 50
journalctl -u verdis-node --no-pager -n 500 | grep "finalized"
journalctl -u verdis-node --no-pager -n 500 | grep "failed to load session"
```

## Troubleshooting

### Node not producing blocks
1. Check if node is active: `systemctl is-active verdis-node`
2. Check logs: `journalctl -u verdis-node --no-pager -n 20`
3. Verify chain spec is valid JSON
4. Verify data dir is clean

### Finality stuck
1. Check if enough validators are online (need 2/3 of active set)
2. Check GRANDPA votes: `journalctl -u verdis-node | grep "GRANDPA"`
3. Restart the node: `systemctl restart verdis-node`

### Node2/Node3 crashing
1. Check logs: `journalctl -u verdis-node2 --no-pager -n 30`
2. Verify same chain spec: compare genesis hash across nodes
3. Purge and restart if data is corrupted
