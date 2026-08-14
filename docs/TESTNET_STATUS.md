# Verdis Chain Testnet Status

**Last Updated:** 2026-08-14 15:07 UTC  
**Commit SHA:** `2261c82b`  
**Chain Spec:** `testnet-canonical-raw.json`  

## Current State

| Metric | Value |
|---|---|
| Network Status | RUNNING |
| Block Height | #23+ |
| Peer Count | 2 |
| Active Nodes | 3 (verdis-node, verdis-node2, verdis-node3) |
| Active Validators | 3 (Alice, Bob, Charlie) |
| Registered Validators | 6 (Alice, Bob, Charlie, Dave, Eve, Ferdie) |
| Finality | WORKING (GRANDPA) |
| Block Production | WORKING (BABE, 6s slots) |
| Token Symbol | VRDX |
| Decimals | 9 |
| Total Supply | 100,000,000,000 VRDX |
| DEX Pools | 6 |
| Sudo | REMOVED |

## Services

| Service | Port | Status |
|---|---|---|
| verdis-node (Alice) | 9933/9944/30333 | active |
| verdis-node2 (Bob) | 9934/9945/30334 | active |
| verdis-node3 (Charlie) | 9935/9946/30335 | active |
| TX Relay | 4400 | active |
| Governance API | 5020 | active |
| Nginx (verdischain.com) | 80/443 | active |
| Soak Test Monitor | — | active |

## Known Limitations

See TESTNET_KNOWN_LIMITATIONS.md for full list.

## Do NOT Deploy Mainnet

The testnet is NOT complete. Multiple P0 items remain unresolved. See TESTNET_COMPLETION_REPORT.md for details.
