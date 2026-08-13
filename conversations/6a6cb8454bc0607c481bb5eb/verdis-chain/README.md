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
  <img src="https://img.shields.io/badge/status-TESTNET%2FDEVNET-f59e0b" alt="Status">
  <img src="https://img.shields.io/badge/token-VRDX-16a34a" alt="Token">
  <img src="https://img.shields.io/badge/consensus-DPoS%20%2B%20BABE%2FGRANDPA-16a34a" alt="Consensus">
  <img src="https://img.shields.io/badge/SS58-909-16a34a" alt="SS58">
  <img src="https://img.shields.io/badge/tests-491%20functions-22c55e" alt="Tests">
  <img src="https://img.shields.io/badge/pallets-16%20custom-16a34a" alt="Pallets">
  <img src="https://img.shields.io/badge/license-Proprietary-red" alt="License">
</p>

---

> **NETWORK STATUS: TESTNET / DEVELOPMENT CHAIN**
>
> VRDX testnet tokens have **no monetary value**. Mainnet is **planned but not live**.
> No independent security audit has been performed. No funds have been raised ($0 verified).
> See docs/PUBLIC_RISK_DISCLOSURE.md for full risk disclosure.

---

Verdis Chain is a Substrate-based blockchain implementing Delegated Proof of Stake (DPoS) consensus with BABE/GRANDPA finality, a native AMM decentralized exchange (DEX), carbon credit tracking infrastructure, and AI-native tooling.

## Key Facts

| Property | Value | Status |
|---|---|---|
| Token Symbol | VRDX | LIVE |
| Token Decimals | 9 | LIVE |
| Max Supply | 100,000,000,000 VRDX (100B) | IMPLEMENTED |
| SS58 Prefix | 909 | LIVE |
| Consensus | DPoS + BABE / GRANDPA | IMPLEMENTED |
| Active Validators | 6 (devnet) / 21 (mainnet spec) | TESTNET |
| Chain Specs | dev, testnet, mainnet | IMPLEMENTED |
| Domain | verdischain.com | LIVE |
| Network Type | Development Chain | NOT MAINNET |
| Independent Audit | None | NOT PERFORMED |
| Verified Raised | $0 | NO FUNDS RAISED |

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

## Architecture

### Pallets (16 custom, 491 tests)

| Pallet | Tests | Description |
|---|---|---|
| dpos | 71 | DPoS — validator registration, staking, delegation, slashing |
| amm-dex | 37 | AMM DEX — swap, liquidity, pool management |
| eco | 26 | Carbon credits, green validator scoring, reforestation |
| tokenomics | 70 | Token allocation, supply management, economic invariants |
| vesting | 42 | Vesting schedules with cliffs and linear release |
| presale | 85 | Presale rounds, whitelisting, contributions |
| fungible-tokens | 27 | Custom token creation and management |
| ibc | 50 | Inter-Blockchain Communication |
| poh | 10 | Proof of History |
| gulf-stream | 16 | Mempool-less transaction forwarding |
| turbine | 9 | Block propagation optimization |
| zk-compression | 10 | Zero-knowledge state compression |
| circuit-breaker | 15 | Automated pausing on anomalies |
| sealevel | 9 | Parallel smart contract execution |
| storage | 9 | On-chain data storage |
| address-lookup-tables | 4 | Compact account references |

### Web (15 pages on verdischain.com)

Landing, Explorer, Transactions, DEX, Wallet, Validators, Governance, Eco, Whitepaper, Tokenomics, Sale, Faucet, Docs, Analytics, Monitoring

### SDK

JavaScript SDK with 51 methods, native WebSocket, zero dependencies (sdk/verdis-sdk.js)

## Mainnet Readiness

See docs/MAINNET_READINESS_CHECKLIST.md — 62% complete (48/78 tasks)

Critical blockers: air-gapped validator keys, 3-of-5 cold storage multisig, independent audit, benchmarking, integration tests, genesis determinism, legal entity.

## CI/CD

GitHub Actions: fmt, check, clippy, test, security audit, secret scan, release, Docker, try-runtime

## Quick Start

```bash
cargo build --release
./target/release/verdis --dev
cargo test --workspace
```

## Documentation

Key docs in docs/:
- PUBLIC_SOURCE_OF_TRUTH.md — Central verified facts
- MAINNET_READINESS_CHECKLIST.md — 78-task mainnet checklist
- PUBLIC_RISK_DISCLOSURE.md — Risk disclosure
- TOKENOMICS_FINAL.md — Tokenomics specification
- AUDIT_STATUS.md — Audit disclosure (internal only)
- INVESTOR_DATA_ROOM.md — Investor evidence index

## Ecosystem

Verdis Chain is the blockchain layer of the Evolvix ecosystem:
- EvolvixOS — AI Engineering OS at evolvixos.com
- AI Platform — AI models, agents, services
- Smart Contract Platform — ink! contracts
- Developer Ecosystem — SDKs, APIs, tools

## License

Proprietary.

---

> Disclaimer: Development chain / testnet. All claims about carbon credits, environmental impact, and performance are design objectives, not verified facts. No independent audit performed. Mainnet has no confirmed date.
