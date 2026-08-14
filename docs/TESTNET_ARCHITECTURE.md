# Verdis Chain Testnet Architecture

## Overview

Verdis Chain is a Substrate-based blockchain with native DPoS consensus, BABE block production, GRANDPA finality, and custom pallets for DeFi, eco-tracking, and governance.

## Network Topology

```
                    ┌─────────────────┐
                    │  verdischain.com │
                    │    (Nginx 443)   │
                    └────────┬────────┘
                             │
           ┌─────────────────┼─────────────────┐
           │                 │                 │
    ┌──────┴──────┐  ┌──────┴──────┐  ┌──────┴──────┐
    │  Node 1     │  │  Node 2     │  │  Node 3     │
    │  (Alice)    │  │  (Bob)      │  │  (Charlie)  │
    │  RPC: 9933  │  │  RPC: 9934  │  │  RPC: 9935  │
    │  WS:  9944  │  │  WS:  9945  │  │  WS:  9946  │
    │  P2P: 30333 │  │  P2P: 30334 │  │  P2P: 30335 │
    └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
           │                │                 │
           └────────────────┴─────────────────┘
                    P2P Mesh (2 peers)
```

## Consensus Stack

| Layer | Protocol | Role |
|---|---|---|
| Block Production | BABE | Validator rotation, 6-second slots |
| Finality | GRANDPA | BFT finality, 2/3 majority needed |
| Staking | DPoS (custom pallet) | Validator selection, rewards, slashing |
| Session | Substrate Session | Key management, epoch rotation |

## Pallet Architecture

| Pallet | Location | Purpose |
|---|---|---|
| dpos | pallets/dpos/ | DPoS consensus, validator registration, staking, slashing |
| tokenomics | pallets/tokenomics/ | Token supply management, distribution tracking |
| vesting | pallets/vesting/ | Token vesting schedules (seed, presale, team) |
| amm-dex | pallets/amm-dex/ | AMM DEX, liquidity pools, swaps |
| eco | pallets/eco/ | Carbon credits, reforestation, green validator scoring |
| presale | pallets/presale/ | Token presale, whitelist, contributions |
| sealevel | pallets/sealevel/ | Smart contract execution (Sealevel VM) |
| fungible-tokens | pallets/fungible-tokens/ | Custom token creation |
| governance | pallets/governance/ | Democracy, council, treasury governance |
| gulf-stream | pallets/gulf-stream/ | Fast transaction streaming |

## Token Economics

| Parameter | Value |
|---|---|
| Token Symbol | VRDX |
| Decimals | 9 |
| Max Supply | 100,000,000,000 (100B) |
| Circulating Supply | 8,000,000,000 (8B) |
| Block Reward | 16 VRDX |

## Genesis Allocation

| Category | Amount (VRDX) | % |
|---|---|---|
| Ecosystem & Developer Grants | 25B | 25% |
| PoS Staking Rewards | 20B | 20% |
| Treasury | 20B | 20% |
| Development | 10B | 10% |
| Liquidity (DEX) | 10B | 10% |
| Community | 5B | 5% |
| Seed / Strategic | 3B | 3% |
| Public Presale | 2B | 2% |
| Team & Advisors | 5B | 5% |
| **Total** | **100B** | **100%** |

## DEX Pools

| Pool | Reserve A | Reserve B | Fee |
|---|---|---|---|
| VRDX/ECO | 500,000 | 500,000 | 0.3% |
| VRDX/CARBON | 300,000 | 300,000 | 0.3% |
| VRDX/TREE | 200,000 | 200,000 | 0.3% |
| VRDX/GREEN | 200,000 | 200,000 | 0.3% |
| ECO/CARBON | 100,000 | 100,000 | 0.3% |
| VRDX/REDD | 100,000 | 100,000 | 0.3% |

## Services

| Service | Port | Description |
|---|---|---|
| verdis-node | 9933/9944/30333 | Node 1 (Alice) — validator |
| verdis-node2 | 9934/9945/30334 | Node 2 (Bob) — validator |
| verdis-node3 | 9935/9946/30335 | Node 3 (Charlie) — validator |
| TX Relay | 4400 | Transaction relay for wallet signing |
| Governance API | 5020 | Governance web interface |
| Nginx | 80/443 | Web server (verdischain.com) |

## Data Directories

| Node | Path |
|---|---|
| Node 1 | /opt/verdis-node1-data-v6 |
| Node 2 | /opt/verdis-node2-data-v6 |
| Node 3 | /opt/verdis-node3-data-v6 |
