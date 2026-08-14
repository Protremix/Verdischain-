<p align="center">
  <img src="web/assets/verdis-logo-full.png" alt="Verdis Chain" width="200">
</p>

<h1 align="center">Verdis Chain</h1>

<p align="center">
  <strong>The energy-efficient DPoS blockchain powering the Evolvix ecosystem.</strong>
</p>

<p align="center">
  <a href="https://verdischain.com">Website</a> &middot;
  <a href="https://verdischain.com/explorer/">Explorer</a> &middot;
  <a href="https://verdischain.com/dex/">DEX</a> &middot;
  <a href="https://verdischain.com/wallet/">Wallet</a> &middot;
  <a href="https://verdischain.com/docs/">Docs</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/node-2.0.0-16a34a" alt="Node Version">
  <img src="https://img.shields.io/badge/token-VRDX-16a34a" alt="Token">
  <img src="https://img.shields.io/badge/consensus-DPoS%20%2B%20BABE%2FGRANDPA-16a34a" alt="Consensus">
  <img src="https://img.shields.io/badge/SS58-909-16a34a" alt="SS58">
  <img src="https://img.shields.io/badge/tests-534%20functions-22c55e" alt="Tests">
  <img src="https://img.shields.io/badge/pallets-16-16a34a" alt="Pallets">
  <img src="https://img.shields.io/badge/pages-31%20live-22c55e" alt="Pages">
  <img src="https://img.shields.io/badge/status-TESTNET-f59e0b" alt="Status">
  <img src="https://img.shields.io/badge/license-MIT-blue" alt="License">
</p>

---

Verdis Chain is a Substrate-based blockchain implementing Delegated Proof of Stake (DPoS) consensus with BABE/GRANDPA finality, a native AMM decentralized exchange (DEX), energy-efficient carbon credit tracking, and AI-native tooling.

## Current State

| Property | Value |
|---|---|
| Status | **TESTNET** — Not mainnet. Not investor-ready. |
| Latest Block | #8,689 |
| Node Version | verdis-node 2.0.0 (100 MB binary) |
| Runtime | Custom Substrate runtime, 16 pallets |
| Token Symbol | VRDX |
| Token Decimals | 9 |
| Max Supply | 100,000,000,000 VRDX (100B) |
| SS58 Prefix | 909 |
| Consensus | DPoS + BABE / GRANDPA |
| Block Time | 6 seconds |
| DEX Fee | 0.3% (3/1000) |
| Validators | 6 registered (target: 21 -> 200+) |
| Chain Specs | dev, testnet, mainnet (6 files) |
| Test Functions | 534 across 16 pallets |
| CI/CD Workflows | 11 GitHub Actions pipelines |
| Web Pages | 31 live on verdischain.com |
| Services | 17 systemd services |
| Docs | 55 files in docs/ |
| Git Commits | 913+ |
| License | MIT |
| Domain | [verdischain.com](https://verdischain.com) |

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

| Pallet | Tests | Description |
|---|---|---|
| dpos | 115 | Delegated Proof of Stake — validator registration, staking, delegation, slashing |
| presale | 85 | Token presale rounds, whitelisting, contribution tracking |
| vesting | 84 | Token vesting schedules with cliffs and linear release |
| amm-dex | 51 | Native AMM decentralized exchange — swap, add/remove liquidity, pool management |
| tokenomics | 40 | Token allocation, distribution schedule, supply management |
| eco | 29 | Carbon credit tracking, green validator scoring, reforestation logging |
| ibc | 28 | Inter-Blockchain Communication protocol |
| fungible-tokens | 27 | Custom token creation and management |
| storage | 23 | On-chain data storage primitives |
| gulf-stream | 16 | Mempool-less transaction forwarding (Solana-inspired) |
| circuit-breaker | 15 | Automated pausing on anomalous conditions |
| poh | 10 | Proof of History — verifiable delay function for sequencing |
| zk-compression | 10 | Zero-knowledge compression for state |
| turbine | 9 | Block propagation optimization (Solana-inspired) |
| sealevel | 9 | Parallel smart contract execution model |
| address-lookup-tables | 4 | ALT for compact account references |
| **Total** | **534** | |

### Chain Specs (6 files)

| File | Type |
|---|---|
| chain-specs/dev-plain.json | Development |
| chain-specs/dev-raw.json | Development (SCALE-encoded) |
| chain-specs/testnet-plain.json | Testnet |
| chain-specs/testnet-canonical-raw.json | Testnet (SCALE-encoded) |
| chain-specs/mainnet-plain.json | Mainnet |
| chain-specs/mainnet-raw.json | Mainnet (SCALE-encoded) |

### RPC Methods

**DPoS:** dpos_allValidators, dpos_activeValidators, dpos_currentEpoch, dpos_validatorName, dpos_validatorStake

**DEX:** amm_dex_getAllPools, amm_dex_getAllTokenPools, amm_dex_getPool, amm_dex_getPoolCount, amm_dex_getPrice, amm_dex_getLiquidity, amm_dex_getTokenPool, amm_dex_getTokenPoolCount, amm_dex_getTokenLiquidity

**Eco:** eco_getAllGreenValidators, eco_getGreenScore, eco_getGreenValidatorCount, eco_getCarbonCreditCount, eco_getReforestProjectCount, eco_getTotalCO2Offset, eco_getTotalTreesPlanted, eco_getTotalCreditsRetired

### Node

- **Binary:** verdis-node (100 MB, Substrate-based)
- **Runtime:** Custom runtime with 16 pallets via construct_runtime!
- **Ports:** RPC HTTP (9933), WebSocket (9944), P2P (30333)
- **Nodes:** 3 (verdis-node, verdis-node2, verdis-node3)

### Services (17 running)

| Service | Port | Description |
|---|---|---|
| verdis-node | 9933/9944/30333 | Blockchain node (P2P + RPC) |
| verdis-node2 | 9934/30334 | Node 2 |
| verdis-node3 | 9935/30335 | Node 3 |
| verdis-relay | 4400 | TX Relay v3 (Non-Custodial, AES-GCM) |
| verdis-api | 3000 | REST API |
| verdis-faucet | 5000 | Testnet faucet |
| verdis-governance | 5020 | Governance API |
| verdis-price-collector | - | Price history collector |
| verdis-health-monitor | - | Health monitoring |
| verdis-finality-monitor | - | Finality monitoring |
| verdis-validator-monitor | - | Validator monitoring |
| verdis-rpc-filter | - | RPC security filter |
| verdis-soak-test | - | Soak testing |
| verdis-txbot | - | Transaction bot |
| verdis-val-2/4/5 | - | Additional validator nodes |

## Web Components

### 31 Live Pages on verdischain.com

All pages feature TESTNET banners, live RPC data, and the gradient-ui-ux template:

| Page | Description |
|---|---|
| [Homepage](https://verdischain.com/) | Overview, roadmap, token distribution |
| [Explorer](https://verdischain.com/explorer/) | Live blocks, transactions, validators, DEX pools |
| [Whitepaper](https://verdischain.com/whitepaper/) | Full technical specification |
| [Tokenomics](https://verdischain.com/tokenomics/) | 9-category allocation, vesting schedule, staking APR |
| [Sale](https://verdischain.com/sale/) | 4-round fundraising (Seed, Community, Presale, TGE) |
| [DEX](https://verdischain.com/dex/) | AMM swap interface, liquidity pools |
| [Validators](https://verdischain.com/validators/) | DPoS validator registry, green scores |
| [Eco](https://verdischain.com/eco/) | Carbon credits, reforestation, green metrics |
| [Wallet](https://verdischain.com/wallet/) | Non-custodial web wallet (@noble/secp256k1) |
| [Governance](https://verdischain.com/governance/) | Referendums, council, treasury proposals |
| [Team](https://verdischain.com/team/) | Verified team members with public source links |
| [Docs](https://verdischain.com/docs/) | API reference, RPC methods |
| [Transactions](https://verdischain.com/transactions/) | Solscan-style transaction explorer |
| [Analytics](https://verdischain.com/analytics/) | Network analytics dashboard |
| [Monitoring](https://verdischain.com/monitoring/) | Real-time network monitoring |
| [Lightpaper](https://verdischain.com/lightpaper/) | Summary whitepaper |
| Plus: Faucet, Blog, Security, Status, Contact, Developers, Download, Disclaimer, Privacy, Terms, Cookies, Incentives |

### Android Wallet

- Non-custodial, BIP39 mnemonics, sr25519, SS58 909
- Built with Flutter, uses @noble/secp256k1
- APK: 37.8 MB
- Available at [verdischain.com/wallet/](https://verdischain.com/wallet/)

## Security

- **Security headers:** HSTS, CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy (6 active)
- **Docker hardening:** Non-root user, read-only FS, cap_drop ALL, resource limits
- **No hardcoded keys** in source code
- **Air-gapped key ceremony** script for 21 validators + 5 multisig keys
- **3-of-5 Treasury multisig** specification
- **TX Relay v3:** Non-custodial, AES-GCM encryption, CSP headers

## CI/CD (11 GitHub Actions workflows)

| Workflow | Description |
|---|---|
| ci.yml | Format check, compile, clippy, unit tests, release build, WASM, audit |
| deploy.yml | Automated deployment to verdischain.com |
| docker.yml | Docker image build and push |
| release.yml | Release binary build |
| benchmark-check.yml | Performance benchmarking |
| genesis-consistency.yml | Genesis determinism verification |
| release-gates.yml | Mainnet release gate checks |
| try-runtime.yml | Runtime migration testing |
| security.yml | Security scanning |
| secret-scan.yml | Secret/credential detection |
| repo-hygiene.yml | Repository hygiene checks |

## Documentation (55 files in docs/)

Key documents:
- [Architecture](docs/ARCHITECTURE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Validator Setup Guide](docs/VALIDATOR_SETUP_GUIDE.md)
- [RPC API Reference](docs/RPC_API_REFERENCE.md)
- [Security Audit Report](docs/security-audit.md)
- [Treasury Security Spec](docs/TREASURY_SECURITY_SPEC.md)
- [Mainnet Readiness Checklist](docs/MAINNET_READINESS_CHECKLIST.md)
- [Genesis Ceremony Plan](docs/GENESIS_CEREMONY_PLAN.md)
- [Canonical Facts](docs/CANONICAL_FACTS.md)
- [Claims Register](docs/CLAIMS_REGISTER.md)

## Roadmap

- [x] Core blockchain (16 pallets, DPoS, BABE/GRANDPA)
- [x] AMM DEX (6 liquidity pools)
- [x] Web wallet + Android APK (37.8 MB)
- [x] 31 web pages with live RPC data
- [x] 11 CI/CD pipelines
- [x] Security hardening (6 headers, Docker, audits)
- [x] 534 test functions across 16 pallets
- [x] 6 chain specs (dev, testnet, mainnet)
- [x] MIT License
- [ ] 21 active validators (air-gapped key ceremony)
- [ ] Independent security audit
- [ ] Mainnet launch

## Contact

- **Website:** [verdischain.com](https://verdischain.com)
- **Contact:** [verdischain.com/contact/](https://verdischain.com/contact/)
- **Founder:** Rojs Gordons
- **CEO:** Dorian Jean

## License

Copyright (c) 2026 Verdis Chain / Protremix. Licensed under the MIT License.

See [LICENSE](LICENSE) for details.
