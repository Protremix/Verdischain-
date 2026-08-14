<p align="center">
  <img src="web/assets/verdis-logo-full.png" alt="Verdis Chain" width="200">
</p>

<h1 align="center">Verdis Chain</h1>

<p align="center">
  <strong>The energy-efficient DPoS blockchain powering the Evolvix ecosystem.</strong>
</p>

<p align="center">
  <a href="https://verdischain.com">Website</a> ·
  <a href="https://verdischain.com/explorer/">Explorer</a> ·
  <a href="https://verdischain.com/dex/">DEX</a> ·
  <a href="https://verdischain.com/wallet/">Wallet</a> ·
  <a href="https://verdischain.com/docs/">Docs</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/node-2.0.0-16a34a" alt="Node Version">
  <img src="https://img.shields.io/badge/token-VRDX-16a34a" alt="Token">
  <img src="https://img.shields.io/badge/consensus-DPoS%20%2B%20BABE%2FGRANDPA-16a34a" alt="Consensus">
  <img src="https://img.shields.io/badge/SS58-909-16a34a" alt="SS58">
  <img src="https://img.shields.io/badge/tests-489%20passing-22c55e" alt="Tests">
  <img src="https://img.shields.io/badge/pages-31%20live-22c55e" alt="Pages">
  <img src="https://img.shields.io/badge/status-TESTNET-f59e0b" alt="Status">
  <img src="https://img.shields.io/badge/license-Proprietary-red" alt="License">
</p>

---

Verdis Chain is a Substrate-based blockchain implementing Delegated Proof of Stake (DPoS) consensus with BABE/GRANDPA finality, a native AMM decentralized exchange (DEX), energy-efficient carbon credit tracking, and AI-native tooling.

## Key Facts

| Property | Value |
|---|---|
| Node Version |  |
| Token Symbol | VRDX |
| Token Decimals | 9 |
| Max Supply | 100,000,000,000 VRDX (100B) |
| SS58 Prefix | 909 |
| Consensus | DPoS + BABE / GRANDPA |
| Active Validators | 6 (target: 21 → 200+) |
| Chain Specs | dev, testnet, mainnet |
| Block Time | 6 seconds |
| DEX Fee | 0.3% (3/1000) |
| Domain | [verdischain.com](https://verdischain.com) |
| Status | **TESTNET** — Not mainnet. Not investor-ready. |

## Tokenomics

| Allocation | Amount | % |
|---|---|---|
| Ecosystem & Developer Grants | 25B | 25% |
| PoS Staking Rewards | 20B | 20% |
| Treasury | 20B | 20% |
| Development | 10B | 10% |
| Liquidity | 10B | 10% |
| Community | 5B | 5% |
| Seed / Strategic | 3B | 3% |
| Public Presale | 2B | 2% |
| Team & Advisors | 5B | 5% |
| **Total** | **100B** | **100%** |

Treasury is controlled by a **3-of-5 multisig** (cold storage, air-gapped key ceremony).

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

- **Binary**: `verdis-node` (Substrate-based)
- **Runtime**: Custom runtime with 16 pallets integrated via `construct_runtime!`
- **RPC**: HTTP (9933), WebSocket (9944), P2P (30333)
- **Chain Specs**: `chain-specs/dev`, `chain-specs/testnet`, `chain-specs/mainnet`

### Tests

- **489 test functions** across all pallets
- **2 dedicated test files** in `tests/`
- Tests cover: staking, delegation, slashing, DEX swap/liquidity, vesting, presale, eco credits, PoH, IBC, and more

## Web Components

### 31 Live Pages on [verdischain.com](https://verdischain.com)

All pages feature TESTNET banners, live RPC data, and the gradient-ui-ux template:

- **Homepage** — Overview, roadmap, token distribution
- **Explorer** — Live blocks, transactions, validators, DEX pools
- **Whitepaper** — Full technical specification
- **Tokenomics** — 9-category allocation, vesting schedule, staking APR
- **Sale** — 4-round fundraising (Seed, Community, Presale, TGE)
- **DEX** — AMM swap interface, liquidity pools
- **Validators** — DPoS validator registry, green scores
- **Eco** — Carbon credits, reforestation, green metrics
- **Wallet** — Non-custodial web wallet (@noble/secp256k1)
- **Governance** — Referendums, council, treasury proposals
- **Team** — Verified team members with public source links
- **Docs** — API reference, 15 RPC method categories
- Plus: Analytics, Monitoring, Faucet, Blog, Transactions, Lightpaper

### Services (17 running)

| Service | Port | Description |
|---|---|---|
| verdis-node | 9933/9944/30333 | Blockchain node (P2P + RPC) |
| verdis-node2 | 9934/30334 | Node 2 (Bob) |
| verdis-node3 | 9935/30335 | Node 3 (Charlie) |
| verdis-relay | 4400 | TX Relay v3 (Non-Custodial) |
| verdis-api | 3000 | REST API |
| verdis-faucet | 5000 | Testnet faucet |
| verdis-governance | 5020 | Governance API |
| verdis-price-collector | — | Price history collector |
| verdis-health-monitor | — | Health monitoring |
| verdis-finality-monitor | — | Finality monitoring |

### Android Wallet

- Non-custodial, BIP39 mnemonics, sr25519, SS58 909
- Built with Flutter, uses @noble/secp256k1
- Available at [verdischain.com/wallet/](https://verdischain.com/wallet/)

## Security

- **Security headers**: HSTS, CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy
- **Docker hardening**: Non-root user, read-only FS, cap_drop ALL, resource limits
- **No hardcoded keys** in source code
- **Air-gapped key ceremony** script for 21 validators + 5 multisig keys
- **3-of-5 Treasury multisig** specification

## CI/CD

GitHub Actions pipelines:
- **Format check** (cargo fmt --check)
- **Compile check** (cargo check --workspace)
- **Clippy** (strict, -D warnings)
- **Unit tests** (cargo test --workspace)
- **Release build** (cargo build --release)
- **WASM runtime build** (wasm32-unknown-unknown)
- **Dependency audit** (cargo audit)
- **Secret scanning** (gitleaks + hardcoded key detection)
- **RPC security scan**

## Documentation

Full documentation in `docs/`:
- [Architecture](docs/ARCHITECTURE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Validator Setup Guide](docs/VALIDATOR_SETUP_GUIDE.md)
- [RPC API Reference](docs/RPC_API_REFERENCE.md)
- [Security Audit Report](docs/security-audit.md)
- [GPT-4o Full Audit](docs/GPT4_FULL_AUDIT_MASTER.md)
- [Treasury Security Spec](docs/TREASURY_SECURITY_SPEC.md)
- [Mainnet Readiness Checklist](docs/MAINNET_READINESS_CHECKLIST.md)

## Roadmap

- [x] Core blockchain (16 pallets, DPoS, BABE/GRANDPA)
- [x] AMM DEX (6 liquidity pools)
- [x] Web wallet + Android APK
- [x] 31 web pages with live RPC data
- [x] CI/CD pipelines
- [x] Security hardening (headers, Docker, audits)
- [ ] 21 active validators (air-gapped key ceremony)
- [ ] Independent security audit
- [ ] Mainnet launch

## Contact

- **Website**: [verdischain.com](https://verdischain.com)
- **Contact**: [verdischain.com/contact/](https://verdischain.com/contact/)
- **Founder**: Rojs Gordons
- **CEO**: Dorian Jean

## License

Copyright (c) 2026 Verdis Chain / Protremix. All rights reserved.

Proprietary and confidential. See [LICENSE](LICENSE) for details.
