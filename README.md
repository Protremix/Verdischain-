# Verdis Chain

**The carbon-negative DPoS blockchain powering the Evolvix ecosystem.**

Verdis Chain is a Substrate-based blockchain implementing Delegated Proof of Stake (DPoS) consensus with BABE/GRANDPA finality, a native AMM decentralized exchange (DEX), eco-friendly carbon credit tracking, and AI-native tooling.

---

## Key Facts

| Property | Value |
|---|---|
| Node Version | `verdis-node 2.0.0` |
| Token Symbol | VRDX |
| Token Decimals | 9 |
| Max Supply | 100,000,000,000 VRDX (100B) |
| SS58 Prefix | 909 |
| Consensus | DPoS + BABE / GRANDPA |
| Active Validators | 6 (target: 21 → 200+) |
| Chain Specs | dev, testnet, mainnet |
| Domain | [verdischain.com](https://verdischain.com) |

---

## Tokenomics

| Allocation | Amount | % |
|---|---|---|
| Ecosystem & Developer Grants | 25B | 25% |
| PoS Staking Rewards | 20B | 20% |
| Treasury | 15B | 15% |
| Development | 10B | 10% |
| Liquidity | 10B | 10% |
| Community | 5B | 5% |
| Seed / Strategic | 3B | 3% |
| Public Presale | 2B | 2% |
| Team & Advisors | 5B | 5% |
| **Total** | **100B** | **100%** |

---

## Architecture

### Pallets (16)

| Pallet | Description |
|---|---|
| `dpos` | Delegated Proof of Stake — validator registration, staking, delegation, slashing |
| `amm-dex` | Native AMM decentralized exchange — swap, add/remove liquidity, pool management |
| `eco` | Carbon credit tracking, green validator scoring, reforestation logging |
| `tokenomics` | Token allocation, distribution schedule, supply management |
| `vesting` | Token vesting schedules with cliffs and linear release |
| `presale` | Token presale rounds, whitelisting, contribution tracking |
| `fungible-tokens` | Custom token creation and management |
| `poh` | Proof of History — verifiable delay function for sequencing |
| `gulf-stream` | Mempool-less transaction forwarding (Solana-inspired) |
| `turbine` | Block propagation optimization (Solana-inspired) |
| `zk-compression` | Zero-knowledge compression for state |
| `ibc` | Inter-Blockchain Communication protocol |
| `address-lookup-tables` | ALT for compact account references |
| `circuit-breaker` | Automated pausing on anomalous conditions |
| `sealevel` | Parallel smart contract execution model |
| `storage` | On-chain data storage primitives |

### Node

- **Binary**: `verdis-node` (100MB, Substrate-based)
- **Runtime**: Custom runtime with 16 pallets integrated via `construct_runtime!`
- **RPC**: HTTP (9933), WebSocket (9944), P2P (30333)
- **Chain Specs**: `chain-specs/dev`, `chain-specs/testnet`, `chain-specs/mainnet`

### Tests

- **444 test functions** across all pallets
- **2 dedicated test files** in `tests/`
- Tests cover: staking, delegation, slashing, DEX swap/liquidity, vesting, presale, eco credits, PoH, IBC, and more

---

## Web Components

### 28 Live Pages on [verdischain.com](https://verdischain.com)

| Page | URL | Description |
|---|---|---|
| Landing | `/` | Homepage with gradient-ui-ux template |
| Explorer | `/explorer/` | Block explorer (Verdiscan) with live RPC data |
| Transactions | `/transactions/` | Solscan-style transaction explorer |
| DEX | `/dex/` | AMM decentralized exchange UI |
| Wallet | `/wallet/` | Non-custodial web wallet (@noble/secp256k1) |
| Validators | `/validators/` | Validator dashboard with green scores |
| Governance | `/governance/` | Referendums, proposals, council, treasury |
| Eco | `/eco/` | Carbon credits, green scoring, reforestation |
| Whitepaper | `/whitepaper/` | Technical whitepaper |
| Tokenomics | `/tokenomics/` | Token allocation, vesting, staking APR |
| Sale | `/sale/` | Token sale information |
| Faucet | `/faucet/` | Testnet token faucet |
| Docs | `/docs/` | Developer documentation |
| Developers | `/developers/` | Developer portal — SDKs, APIs, RPC reference |
| API | `/api/` | REST API documentation |
| Analytics | `/analytics/` | Network analytics dashboard |
| Monitoring | `/monitoring/` | System monitoring dashboard |
| Blog | `/blog/` | Project blog |
| Download | `/download/` | Wallet download (Android APK) |
| Contact | `/contact/` | Contact information |
| Status | `/status/` | Network status page |
| + 7 more | | Privacy, Terms, Cookies, Disclaimer, Security, Referral, Incentives |

### JavaScript SDK

- 51 methods
- Native WebSocket support
- Zero dependencies
- Located at `sdk/verdis-sdk.js`

### Wallets

- **Web Wallet**: Non-custodial, @noble/secp256k1 + @noble/hashes, SS58 prefix 909
- **Android APK**: Flutter-based, BIP39 mnemonics, server-derived sr25519 addresses

---

## Infrastructure

### Services (20+ systemd units)

```
verdis-node1     — Blockchain node (Alice, port 30333/9933)
verdis-node2-6   — Additional validator nodes
verdis-tx-relay  — Non-custodial TX relay v3 (port 5001)
verdis-api       — REST API gateway (port 4400)
verdis-faucet    — Testnet faucet
verdis-governance — Governance API (port 5020)
verdis-txbot     — Transaction bot for network activity
verdis-health-monitor — Health monitoring
verdis-finality-monitor — Finality monitoring
verdis-backup    — Automated backup service
nginx            — Reverse proxy + TLS
```

### Monitoring Stack

- **Prometheus** — Metrics collection (port 9090, localhost only)
- **Grafana** — Dashboards (port 3000, localhost only)
- **AlertManager** — Alert routing (port 9093, localhost only)
- **Node Exporter** — System metrics (port 9100, localhost only)

### Deployment

- **Docker**: Multi-stage build, non-root user, read-only FS, capability dropping
- **Docker Compose**: Single-node and multi-node configurations
- **Nginx**: TLS, HSTS, CSP, X-XSS-Protection headers
- **Server**: Hetzner Cloud, 32GB RAM, 228GB disk

---

## Directory Structure

```
verdis-chain-rust/
├── node/               # Substrate node implementation
│   ├── src/
│   │   ├── main.rs
│   │   ├── chain_spec.rs
│   │   ├── service.rs
│   │   └── rpc.rs
│   └── Cargo.toml
├── runtime/            # Runtime configuration
│   ├── src/lib.rs
│   └── Cargo.toml
├── pallets/            # 16 custom pallets
│   ├── dpos/
│   ├── amm-dex/
│   ├── eco/
│   ├── tokenomics/
│   ├── vesting/
│   ├── presale/
│   ├── fungible-tokens/
│   ├── poh/
│   ├── gulf-stream/
│   ├── turbine/
│   ├── zk-compression/
│   ├── ibc/
│   ├── address-lookup-tables/
│   ├── circuit-breaker/
│   ├── sealevel/
│   └── storage/
├── chain-specs/         # Chain specification files
│   ├── dev-plain.json
│   ├── dev-raw.json
│   ├── testnet/
│   └── mainnet/
├── web/                # 28 web pages (verdischain.com)
├── docs/               # 24 documentation files
├── deploy/             # Docker, release artifacts
├── ci-cd/              # CI/CD pipeline scripts
├── monitoring/         # Prometheus, Grafana, AlertManager
├── scripts/            # Backup, health check, TPS measurement
├── sdk/                # JavaScript SDK
├── tests/              # Integration tests
└── Cargo.toml          # Workspace configuration
```

---

## Quick Start

### Build

```bash
cargo build --release
```

### Run Node (Dev Mode)

```bash
./target/release/verdis --dev
```

### Run Node (Testnet)

```bash
./target/release/verdis \
  --chain testnet \
  --base-path /opt/verdis-node1-data \
  --alice \
  --port 30333 \
  --rpc-port 9933 \
  --rpc-external \
  --rpc-methods=Unsafe \
  --rpc-cors=all \
  --validator \
  --no-telemetry
```

### Run Tests

```bash
cargo test
```

### Access RPC

```bash
curl -X POST http://localhost:9933 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"chain_getHeader","params":[],"id":1}'
```

---

## Documentation

Full documentation is in the `docs/` directory:

- [ARCHITECTURE.md](docs/ARCHITECTURE.md) — System architecture
- [VALIDATOR_GUIDE.md](docs/VALIDATOR_GUIDE.md) — Validator setup
- [DEPLOYMENT.md](docs/DEPLOYMENT.md) — Deployment guide
- [RPC.md](docs/RPC.md) — RPC API reference
- [MAINNET_READINESS.md](docs/MAINNET_READINESS.md) — Mainnet checklist
- [AUDIT_REPORT.md](docs/AUDIT_REPORT.md) — Security audit report
- [GENESIS_CEREMONY.md](docs/GENESIS_CEREMONY.md) — Genesis ceremony plan
- [MONITORING_GUIDE.md](docs/MONITORING_GUIDE.md) — Monitoring setup

---

## Security

- All extrinsic parameters bounded with length checks
- Safe integer casts (no unsafe `as` conversions)
- TX Relay v3: AES-GCM encryption, non-custodial, server-side key derivation only
- SSH key-only authentication
- UFW firewall (SSH 22, HTTP 80/443, P2P 30333)
- Docker container hardening (non-root, read-only FS, cap drop ALL)
- Nginx HSTS, CSP, X-XSS-Protection headers
- No hardcoded private keys, mnemonics, or backdoors

---

## Ecosystem

Verdis Chain is the blockchain layer of the **Evolvix ecosystem**:

- **EvolvixOS** — AI Engineering OS at [evolvixos.com](https://evolvixos.com)
- **AI Platform** — AI models, agents, and services
- **Smart Contract Platform** — Create, test, deploy, manage
- **Developer Ecosystem** — SDKs, APIs, tools, documentation

---

## Links

- **Website**: [verdischain.com](https://verdischain.com)
- **GitHub**: [Protremix/Verdischain-](https://github.com/Protremix/Verdischain-)
- **Explorer**: [verdischain.com/explorer](https://verdischain.com/explorer/)
- **DEX**: [verdischain.com/dex](https://verdischain.com/dex/)
- **Wallet**: [verdischain.com/wallet](https://verdischain.com/wallet/)

---

## License

Proprietary — © Verdis Chain / Protremix. All rights reserved.

---

**Built by [Protremix](https://protremix.com) for the Evolvix ecosystem.**
