# Dependency Inventory (ARCH-073)

**Status:** Initial inventory — must be completed before mainnet

---

## 1. Critical Dependencies

These dependencies are in the consensus path or handle user funds. A vulnerability in any of these could compromise the network.

### Substrate / Polkadot SDK

| Dependency | Version | Risk | Notes |
|-----------|---------|------|-------|
| frame-support | v48 | HIGH | Core runtime primitives |
| frame-system | v48 | HIGH | System pallet |
| sp-runtime | v48 | HIGH | Runtime traits |
| sp-consensus-babe | v48 | CRITICAL | Block production |
| sp-consensus-grandpa | v48 | CRITICAL | Finality |
| sp-core | v48 | HIGH | Core types (crypto) |
| sp-std | v48 | MEDIUM | Standard library |
| sp-io | v48 | HIGH | I/O operations |
| pallet-balances | v48 | CRITICAL | Token transfers |
| pallet-transaction-payment | v48 | HIGH | Fee handling |

### Cryptographic Libraries

| Dependency | Version | Risk | Notes |
|-----------|---------|------|-------|
| sp-core (sr25519) | v48 | CRITICAL | Validator key signing |
| sp-core (ed25519) | v48 | HIGH | GRANDPA finality |
| @noble/secp256k1 | 2.0.0 | HIGH | Web wallet signing |
| @noble/hashes | latest | HIGH | Web wallet hashing |

### Infrastructure

| Dependency | Version | Risk | Notes |
|-----------|---------|------|-------|
| nginx | system | MEDIUM | Web serving, TLS |
| Docker | system | MEDIUM | Container runtime |

## 2. Custom Pallets (First-Party Code)

| Pallet | Location | Risk | Test Count |
|-------|----------|------|------------|
| pallet-dpos | pallets/dpos/ | CRITICAL | 76 |
| pallet-amm-dex | pallets/amm-dex/ | HIGH | TBD |
| pallet-eco | pallets/eco/ | MEDIUM | TBD |
| pallet-tokenomics | pallets/tokenomics/ | HIGH | 8 |
| pallet-vesting | pallets/vesting/ | HIGH | TBD |
| pallet-presale | pallets/presale/ | HIGH | TBD |
| pallet-treasury | pallets/treasury/ | MEDIUM | TBD |
| pallet-fungible-tokens | pallets/fungible-tokens/ | MEDIUM | TBD |

## 3. Supply Chain Risks

1. **Substrate version**: Pinned to v48 — must track upstream security advisories
2. **NPM packages**: Web wallet dependencies must be audited (npm audit)
3. **Docker base images**: Must be pinned to specific digests, not tags
4. **Rust crates**: cargo-audit must be run in CI (already done)

## 4. CI Integration

- `cargo audit` runs in CI (already configured)
- `npm audit` should be added for web wallet
- Dependency versions should be pinned in Cargo.lock
- Dependabot/Renovate should be enabled for automated PRs
