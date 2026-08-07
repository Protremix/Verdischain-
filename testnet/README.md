# Verdis Testnet Launch Package

Complete package for launching the Verdis public testnet.

## Contents

```
testnet/
├── launch-testnet.sh       # Main launch script (orchestrates all steps)
├── bootstrap-nodes.txt     # Public bootstrap node list for peer discovery
├── chain-spec.json         # Raw chain specification for testnet
├── faucet.sh               # Testnet faucet (1000 VRS per address per 24h)
└── README.md              # This file
```

## Prerequisites

- Docker + Docker Compose installed
- Verdis node binary (`/opt/verdis-chain-rust/target/release/verdis`)
- Node keys generated (`../multi-node/generate-keys.sh`)
- Domain: `testnet.verdischain.com` pointing to server
- SSL certificate (Let's Encrypt)
- UFW firewall configured (ports 22/80/443/30333-30336)

## Quick Start

```bash
# 1. Generate keys for all 9 nodes
cd ../multi-node
./generate-keys.sh

# 2. Generate chain spec with 5 authorities
./chain-spec-generator.sh

# 3. Build Docker image
cd ..
docker build -f multi-node/Dockerfile -t verdis-chain:latest .

# 4. Launch the network
cd ../testnet
./launch-testnet.sh
```

## Network Configuration

| Parameter | Value |
|-----------|-------|
| Chain Name | Verdis Testnet |
| Chain ID | 909 |
| Token | VRS (testnet) |
| Total Supply | 100,000,000,000 VRS |
| Decimals | 9 |
| SS58 Prefix | 909 |
| Block Time | 6 seconds |
| Epoch Length | 600 blocks (~1 hour) |
| Session Length | 600 blocks |
| Consensus | BABE + GRANDPA |
| Validators | 5 |
| RPC Nodes | 2 (load balanced) |
| Bootnodes | 2 (primary + secondary) |

## Node Architecture

```
                    ┌─────────────┐
                    │  Nginx (443) │
                    │  testnet.    │
                    │  verdischain │
                    │  .com        │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
        ┌─────▼─────┐ ┌───▼───┐ ┌─────▼─────┐
        │  RPC-1    │ │ RPC-2 │ │  Explorer │
        │  :19944   │ │:29944 │ │  + Faucet │
        └─────┬─────┘ └───┬───┘ └───────────┘
              │            │
        ┌─────┴────────────┴─────────────────┐
        │                                      │
  ┌─────▼─────┐ ┌─────▼─────┐ ┌─────▼─────┐  ┌──▼──────┐
  │ Validator │ │ Validator │ │ Validator │  │ Bootnode │
  │     1     │ │     2     │ │     3     │  │    1     │
  └───────────┘ └───────────┘ └───────────┘  └──────────┘
  ┌───────────┐ ┌───────────┐                ┌──────────┐
  │ Validator │ │ Validator │                │ Bootnode │
  │     4     │ │     5     │                │    2     │
  └───────────┘ └───────────┘                └──────────┘
```

## Public Endpoints

- **RPC:** `https://testnet.verdischain.com/rpc`
- **WebSocket:** `wss://testnet.verdischain.com/ws`
- **Explorer:** `https://testnet.verdischain.com`
- **Faucet:** `https://testnet.verdischain.com/faucet`
- **Chain Spec:** `https://testnet.verdischain.com/chain-spec.json`

## Faucet

The faucet distributes 1000 VRS per address per 24 hours.

```bash
# Request tokens
curl -X POST https://testnet.verdischain.com/faucet -d '{"address":"YOUR_ADDRESS"}'
```

## Monitoring

Prometheus (port 9090), Grafana (port 3000), Alertmanager (port 9093).

Dashboards:
- Verdis Overview (block production, finality, peers)
- Verdis Validator (active validators, BABE authorship)
- Verdis Consensus (epoch progress, GRANDPA rounds)

## Security

- RPC nodes behind nginx with rate limiting (30 r/s)
- P2P ports open on firewall (30333-30336)
- Validator keys stored in encrypted keystore
- SSL via Let's Encrypt
- CORS restricted to `testnet.verdischain.com`

## Connecting

### Using Polkadot.js

1. Open https://polkadot.js.org/apps
2. Go to Settings → Developer
3. Add custom endpoint: `wss://testnet.verdischain.com/ws`
4. Set SS58 prefix to 909
5. Set token symbol to VRS, decimals to 9

### Using CLI

```bash
./verdis --chain testnet --bootnodes "/dns/bootnode1.verdischain.com/tcp/30333/p2p/NODE_KEY" --rpc-cors all
```

### Using Web Wallet

Navigate to `https://testnet.verdischain.com/wallet.html` and connect with your seed phrase.

## Genesis Allocation

| Category | Amount (VRS) | % |
|----------|-------------|---|
| Team | 15,000,000,000 | 15% |
| Treasury + Staking | 30,000,000,000 | 30% |
| Community (Eco) | 35,000,000,000 | 35% |
| Investors | 10,000,000,000 | 10% |
| Liquidity (DEX) | 5,000,000,000 | 5% |
| Advisors + Airdrop | 5,000,000,000 | 5% |
| **Total** | **100,000,000,000** | **100%** |
