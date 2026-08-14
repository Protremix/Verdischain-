# Changelog

All notable changes to Verdis Chain are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

---

## [2.0.0] — 2026-08-13

### Added
- Comprehensive README.md with full architecture documentation
- LICENSE file (MIT)
- CONTRIBUTING.md with development guidelines
- Issue templates (bug report, feature request)
- Pull request template
- Social preview banner for GitHub
- `/token/` redirect page to `/tokenomics/`
- 16 pallets: dpos, amm-dex, eco, tokenomics, vesting, presale, fungible-tokens, poh, gulf-stream, turbine, zk-compression, ibc, address-lookup-tables, circuit-breaker, sealevel, storage
- 444 test functions across all pallets
- 28 web pages on verdischain.com
- JavaScript SDK (51 methods, native WebSocket, zero dependencies)
- Non-custodial web wallet (@noble/secp256k1 + @noble/hashes, SS58 909)
- Android wallet APK (Flutter, BIP39 mnemonics)
- Chain specs: dev, testnet, mainnet
- TX Relay v3 with AES-GCM encryption
- Governance API (port 5020)
- Monitoring stack: Prometheus, Grafana, AlertManager
- Docker multi-stage build with hardening (non-root, read-only FS, cap drop ALL)
- 20+ systemd services for full node operation
- Nginx reverse proxy with TLS, HSTS, CSP headers
- Carbon credit tracking, green validator scoring, reforestation logging
- Solscan-style transaction explorer with SCALE-aware extrinsic decoder
- Portfolio tracker in explorer
- Analytics and monitoring dashboards

### Security
- All extrinsic parameters bounded with length checks (32-128 bytes)
- Safe integer casts (12 unsafe `as` replaced with `try_from`)
- TX Relay v3: AES-GCM encryption, non-custodial
- SSH key-only authentication
- UFW firewall (SSH 22, HTTP 80/443, P2P 30333)
- Docker container hardening
- Nginx HSTS, CSP, X-XSS-Protection headers
- No hardcoded private keys, mnemonics, or backdoors
- PIN-bypass vulnerability in email recovery fixed
- Self-transfer guard in DEX
- DEX overflow protection with checked_mul
- Pool bricking fix
- Green score self-scoring prevention (requires root)
- Carbon credit minting requires root authorization
- Reforestation project creation requires admin

### Changed
- Fixed low-contrast `#caff33` → `#16a34a` across all 28 web pages
- Fixed `rgba(202,255,51)` → `rgba(22,163,74)` (RGB equivalent)
- Token symbol confirmed as VRDX (not VERDIS)
- Token decimals: 9
- SS58 prefix: 909
- Max supply: 100,000,000,000 VRDX (100B)
- Token allocations: Ecosystem 25B, Staking 20B, Treasury 15B, Development 10B, Liquidity 10B, Community 5B, Seed 3B, Presale 2B, Team 5B

### Removed
- 17 `.bak` / `.backup` files from repository
- 6 `__pycache__` / `.pyc` files from repository
- 1 `.tmp` file from repository
- 4 APK binary files from repository (~100MB — use GitHub Releases instead)
- Fake/hardcoded data from web pages (faucet count, DEX TVL, tree count, validator names)
- Old dark CSS variables (`--bg-1: #111111` → `#f8fafc`)

### Repository
- Added `.gitignore` entries for `.bak`, `.pyc`, `__pycache__`, `.tmp`, `.apk`, `dist/`, `*.log`
- GitHub repo description updated
- GitHub topics added: blockchain, substrate, dpos, eco-friendly, amm-dex, cryptocurrency, rust, polkadot, carbon-credits, web3
- GitHub homepage set to https://verdischain.com
- 645 tracked files (cleaned from 670)

---

## [1.0.0] — 2026-07-15

### Added
- Initial Substrate-based blockchain implementation
- DPoS consensus with BABE/GRANDPA
- Basic AMM DEX
- Block explorer (Verdiscan)
- Token faucet
- Initial web pages
- Node binary `verdis-node`
