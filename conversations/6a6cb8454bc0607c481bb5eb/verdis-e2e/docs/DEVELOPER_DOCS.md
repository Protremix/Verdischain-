# Verdis Chain — Developer Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Quick Start](#quick-start)
4. [Web Wallet Guide](#web-wallet-guide)
5. [DEX Swap Guide](#dex-swap-guide)
6. [RPC API Reference](#rpc-api-reference)
7. [Pallet Reference](#pallet-reference)
8. [Validator Guide](#validator-guide)
9. [SDK Integration](#sdk-integration)
10. [Security](#security)
11. [Monitoring](#monitoring)
12. [Deployment](#deployment)

---

## Overview

Verdis Chain is a Substrate-based blockchain with native DPoS consensus, an AMM DEX, and eco-friendly features including carbon credit tracking and green validator scoring.

**Token:** VRDX (100B total supply, 12 decimals)  
**Chain ID:** 909  
**SS58 Format:** 909  
**Consensus:** DPoS (Delegated Proof of Stake)  
**Network:** Testnet  

---

## Architecture

### Pallets (7)
| Pallet | Index | Purpose |
|--------|-------|---------|
| DPoS | 10 | Delegated proof of stake consensus, validator election, reward distribution |
| AmmDex | 20 | AMM-based decentralized exchange, liquidity pools, token swaps |
| Eco | 30 | Carbon credits, green validator scoring, reforestation logging |
| Tokenomics | 40 | Token supply, inflation, burn mechanisms |
| Vesting | 50 | Token vesting schedules for investors and team |
| EVM | 60 | Ethereum Virtual Machine compatibility (143 opcodes) |
| Storage | 70 | On-chain data storage |

### Infrastructure
- **Node:** Substrate-based, 5 validators + 2 RPC nodes + 2 boot nodes
- **Web:** Nginx reverse proxy, 12 pages, WebSocket at `/ws`
- **Monitoring:** Prometheus + Grafana + Node Exporter
- **Security:** UFW firewall, Fail2Ban, SSH key-only, TLS 1.2/1.3

---

## Quick Start

### Access the Web Interface
- **Landing:** https://verdischain.com
- **Explorer:** https://verdischain.com/explorer/
- **Wallet:** https://verdischain.com/wallet/
- **DEX:** https://verdischain.com/dex/
- **Faucet:** https://verdischain.com/faucet/
- **Status:** https://verdischain.com/status/
- **Grafana:** https://verdischain.com/grafana/ (admin/verdis2026)

### Connect via polkadot.js
```javascript
const { ApiPromise, WsProvider } = require('@polkadot/api');
const wsProvider = new WsProvider('wss://verdischain.com/ws');
const api = await ApiPromise.create({ provider: wsProvider });
console.log('Connected to', await api.rpc.system.chain());
```

### Dev Accounts
| Account | Seed | Use |
|---------|------|-----|
| Alice | `//Alice` | Primary test account (10,000+ VRDX) |
| Bob | `//Bob` | Secondary test account |
| Charlie | `//Charlie` | Test account |
| Dave | `//Dave` | Test account |
| Eve | `//Eve` | Test account |

---

## Web Wallet Guide

### Create a New Wallet
1. Navigate to https://verdischain.com/wallet/
2. Click "Create New Wallet"
3. Save your mnemonic seed phrase securely
4. Your account address and balance will appear

### Import a Wallet
1. Click "Import Wallet"
2. Enter your mnemonic seed phrase (or dev seed like `//Alice`)
3. Your account will load with live balance

### Send VRDX
1. Enter the recipient address in the "Recipient Address" field
2. Enter the amount in VRDX
3. Select your signing account from the dropdown
4. Click "Send Transaction"
5. The transaction will be signed and broadcast on-chain

### How It Works
The wallet uses `@polkadot/api` browser bundles loaded via `<script>` tags:
- `@polkadot/util` → `window.polkadotUtil`
- `@polkadot/util-crypto` → `window.polkadotUtilCrypto`
- `@polkadot/keyring` → `window.polkadotKeyring`
- `@polkadot/types` → `window.polkadotTypes`
- `@polkadot/api` → `window.polkadotApi`

Keys are stored in localStorage (mnemonic + address). The wallet connects via WebSocket to `wss://verdischain.com/ws`.

---

## DEX Swap Guide

### View Pools
The DEX page at https://verdischain.com/dex/ shows 7 live AMM pools:
- VRDX/ECO, VRDX/CARBON, VRDX/TREE, VRDX/GREEN, ECO/CARBON, VRDX/REDD, VRDX/USDC

### Swap Tokens
1. Select "From Token" from the dropdown
2. Enter the amount to swap
3. Select "To Token"
4. The expected output is calculated using the AMM formula: `x * y = k`
5. Select your signing account
6. Click "Execute Swap"

### AMM Formula
The swap uses the constant product formula with 0.3% fee:
```
amountOut = (reserveOut * amountIn * 997) / (reserveIn * 1000 + amountIn * 997)
```

### Add Liquidity
1. Click the "Add Liquidity" tab
2. Select a pool from the dropdown
3. Enter amounts for both tokens
4. Select your signing account
5. Click "Add Liquidity"

---

## RPC API Reference

### Base URL
```
POST https://verdischain.com/rpc
Content-Type: application/json
```

### Chain Methods
```json
// Get latest block header
{"jsonrpc":"2.0","method":"chain_getHeader","params":[],"id":1}

// Get block by hash
{"jsonrpc":"2.0","method":"chain_getBlock","params":["0x..."],"id":2}

// Get finalized head
{"jsonrpc":"2.0","method":"chain_getFinalizedHead","params":[],"id":3}
```

### System Methods
```json
// System health
{"jsonrpc":"2.0","method":"system_health","params":[],"id":4}

// Chain name
{"jsonrpc":"2.0","method":"system_chain","params":[],"id":5}

// Node version
{"jsonrpc":"2.0","method":"system_version","params":[],"id":6}
```

### AMM DEX Methods
```json
// Pool count
{"jsonrpc":"2.0","method":"amm_dex_getPoolCount","params":[],"id":7}

// All pools
{"jsonrpc":"2.0","method":"amm_dex_getAllPools","params":[],"id":8}

// Pool response structure:
{
  "id": 0,
  "token_a": [86, 82, 68, 88],  // ASCII bytes → "VRDX"
  "token_b": [69, 67, 79],      // ASCII bytes → "ECO"
  "reserve_a": 500000000000000, // in Planck (12 decimals)
  "reserve_b": 500000000000000,
  "total_lp": 500000000000000,
  "fee_numerator": 3,
  "fee_denominator": 1000,
  "creator": "5EYCAe5jvYuP4RdW6J9S8N8aeY2XE615FLmBM19PyQtCkc4x"
}
```

### DPoS Methods
```json
// Active validators
{"jsonrpc":"2.0","method":"dpos_activeValidators","params":[],"id":9}

// Green scores
{"jsonrpc":"2.0","method":"dpos_greenScores","params":[],"id":10}
```

### WebSocket
```
wss://verdischain.com/ws
```
Subscribe to new blocks:
```json
{"jsonrpc":"2.0","method":"chain_subscribeNewHeads","params":[],"id":11}
```

---

## Pallet Reference

### DPoS Pallet
- `dpos_register_validator()` — Register as a validator
- `dpos_vote(candidate)` — Vote for a validator candidate
- `dpos_active_validators()` — Get active validator set
- `dpos_green_scores()` — Get green energy scores

### AmmDex Pallet
- `amm_dex.create_pool(token_a, token_b, fee)` — Create a new liquidity pool
- `amm_dex.add_liquidity(token_a, token_b, amount_a, amount_b)` — Add liquidity
- `amm_dex.swap(token_in, token_out, amount_in)` — Execute a token swap
- `amm_dex.remove_liquidity(pool_id, lp_amount)` — Remove liquidity

### Eco Pallet
- `eco.mint_carbon_credit(amount, metadata)` — Mint carbon credits
- `eco.log_reforestation(trees_planted, location)` — Log reforestation data
- `eco.update_green_score(validator, score)` — Update validator green score

### EVM Pallet
- Chain ID: 909
- Max code size: 24,576 bytes
- 143 opcodes supported
- Gas metering enabled

---

## Validator Guide

### Current Validators
14 active DPoS validators running on the testnet. Each validator:
- Runs as a systemd service on 91.98.160.145
- Produces blocks in round-robin order
- Earns VRDX rewards for block production
- Has a green energy score (0-100)

### Become a Validator
1. Generate a sr25519 keypair using the wallet
2. Fund your account with VRDX (use the faucet)
3. Call `dpos.registerValidator()` extrinsic
4. Wait for election round (every 100 blocks)
5. If elected, start your validator node

### Validator Node Setup
```bash
# Clone the repository
git clone https://github.com/Protremix/Verdischain-.git
cd Verdischain-

# Build the node
cargo build --release

# Run as validator
./target/release/verdis-node \
  --chain testnet \
  --validator \
  --bootnodes /ip4/91.98.160.145/tcp/30333/p2p/12D3KooW... \
  --rpc-port 9948
```

---

## SDK Integration

### JavaScript SDK (51 methods)
```javascript
const { VerdisSDK } = require('./sdk/verdis-sdk.js');
const sdk = new VerdisSDK('wss://verdischain.com/ws');

// Get block height
const block = await sdk.getBlockHeight();

// Get balance
const balance = await sdk.getBalance(address);

// Send VRDX
const tx = await sdk.transfer(toAddress, amount);

// Get AMM pools
const pools = await sdk.getAMMPools();

// Swap tokens
const swapTx = await sdk.swap(tokenIn, tokenOut, amountIn);
```

### Browser Integration
```html
<script src="https://unpkg.com/@polkadot/api@10.9.1/bundle-polkadot-api.js"></script>
<script>
const { ApiPromise, WsProvider } = window.polkadotApi;
const api = await ApiPromise.create({ provider: new WsProvider('wss://verdischain.com/ws') });
</script>
```

---

## Security

### Server Hardening
- SSH: Key-only authentication (password auth disabled)
- Fail2Ban: Active, monitoring SSH and nginx
- UFW Firewall: Only ports 22, 80, 443, 30333-30341 open
- TLS: 1.2/1.3 only, HSTS preload enabled
- SSL Certificate: Valid until November 2026

### Security Headers
- `X-Frame-Options: SAMEORIGIN`
- `X-Content-Type-Options: nosniff`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: geolocation=(), microphone=(), camera=()`
- `Content-Security-Policy: default-src 'self' ...`

### Rate Limiting
5 nginx rate limit zones:
- `rpc`: 10 req/s (RPC endpoint)
- `ws`: 20 connections/s (WebSocket)
- `api`: 20 req/s (API endpoints)
- `faucet`: 1 req/min (Faucet)
- `web`: 50 req/s (General web)

### Pallet Security Fixes Applied
1. AMM-DEX: Division by zero in `remove_liquidity` (Critical)
2. DPoS: Self-scoring prevention in `update_green_score` (High)
3. Eco: Authorization check in `mint_carbon_credit` (High)
4. AMM-DEX: LP token overflow protection (High)
5. DPoS: Validator bond slashing math (Medium)
6. Eco: Reforestation data validation (Medium)

---

## Monitoring

### Prometheus
- URL: http://localhost:9090 (internal only)
- Scrape interval: 15s
- Targets: Node Exporter, Verdis RPC, Nginx

### Grafana
- URL: https://verdischain.com/grafana/
- Login: admin / verdis2026
- Datasource: Prometheus
- Dashboard: Verdis Chain Overview

### Metrics Tracked
- Block height (real-time)
- Peer count
- CPU usage
- Memory usage
- Disk usage
- Network I/O (RX/TX)

### Alert Rules
- `NodeDown` — Critical (1m downtime)
- `HighCPU` — Warning (>80% for 5m)
- `HighDisk` — Warning (>85% for 5m)
- `HighMemory` — Warning (>90% for 5m)

### Health Monitor
Systemd service `verdis-health-monitor` checks every 60s:
- Block height
- Peer count
- Service status (13 services)
- Disk usage
- Memory usage
- Logs to `/var/log/verdis-health.log`

### Status Page
- URL: https://verdischain.com/status/
- Auto-refresh: 30s
- Shows: Block height, peers, AMM pools, services, validators, network

---

## Deployment

### Server
- **IP:** 91.98.160.145
- **Domain:** verdischain.com
- **OS:** Ubuntu 26.04 LTS
- **CPU:** 8-core AMD EPYC
- **RAM:** 32GB
- **Disk:** 225GB

### Services (13 active)
```
verdis-val-1.service      — Validator node 1
verdis-val-2.service      — Validator node 2
verdis-val-3.service      — Validator node 3
verdis-val-4.service      — Validator node 4
verdis-val-5.service      — Validator node 5
verdis-rpc-1.service      — RPC node 1
verdis-rpc-2.service      — RPC node 2
verdis-boot-1.service     — Boot node 1
verdis-boot-2.service     — Boot node 2
verdis-faucet.service     — Faucet service
verdis-rpc-filter.service — RPC filter proxy
verdis-tx-bot.service     — Transaction bot
verdis-transfer-bot.service — Transfer bot
verdis-health-monitor.service — Health monitor
nginx.service             — Web server
prometheus.service        — Monitoring
grafana-server.service    — Dashboards
node-exporter.service     — System metrics
```

### Nginx Configuration
- RPC proxy: `/rpc` → `localhost:9948`
- WebSocket: `/ws` → `localhost:9948` (upgrade)
- Grafana: `/grafana/` → `localhost:3001`
- Static pages: `/var/www/verdiscan/`
- Rate limiting on 5 zones
- SSL termination with Let's Encrypt

### GitHub
- Repository: https://github.com/Protremix/Verdischain-
- CI/CD: GitHub Actions (automated tests on every push)
- E2E Tests: Cypress (runs every 6 hours via cron)

---

## E2E Test Suite

### Running Tests
```bash
cd verdis-e2e
npm install
npx cypress run                    # All tests
npx cypress run --spec cypress/e2e/wallet.cy.js  # Wallet only
npx cypress run --spec cypress/e2e/dex.cy.js    # DEX only
npm run test:mobile                 # Mobile viewport (375px)
```

### Test Coverage
| Suite | Tests | Coverage |
|-------|-------|----------|
| Landing | 7 | Page load, navigation, SEO, viewport |
| Wallet | 9 | Create, import, balance, send, export |
| DEX | 12 | Pools, swap calc, liquidity, tabs |
| Explorer | 4 | Block height, peers, validators |
| API | 15 | RPC methods, WebSocket, security headers |
| Mobile | 5 | Responsive at 375/768/1024/1280px |
| **Total** | **52** | Full E2E coverage |

### CI/CD Integration
Tests run automatically via GitHub Actions:
- On every push to master
- On every pull request
- Every 6 hours via cron schedule
- Results uploaded as artifacts (30-day retention)

---

## Token Economics

### VRDX Token
- **Total Supply:** 100,000,000,000 (100B)
- **Investor Allocation:** 12,000,000,000 (12B)
- **Decimals:** 12
- **Ticker:** VRDX
- **SS58 Format:** 909

### Token Sale Phases
1. **Seed Phase** — Early investors (vesting: 24 months)
2. **Private Sale** — Strategic partners (vesting: 12 months)
3. **Public Sale** — Community (vesting: 3 months)

### Vesting
Vesting schedules are enforced on-chain via the Vesting pallet:
- Linear vesting with cliff periods
- Beneficiary claims available after cliff
- On-chain enforcement (no bypass possible)

---

## Eco Features

### Carbon Credits
- Minted on-chain via the Eco pallet
- Each credit represents 1 tonne CO2 offset
- Metadata includes project type, location, verification

### Green Validator Scoring
- Validators earn green scores (0-100)
- Higher scores = more rewards
- Based on renewable energy usage
- Self-scoring prevented (security fix applied)

### Reforestation Logging
- Tree planting events logged on-chain
- Includes location, species count, date
- Immutable proof of reforestation
