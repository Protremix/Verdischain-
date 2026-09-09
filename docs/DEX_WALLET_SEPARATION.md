# DEX & Wallet Separation (ARCH-034/036)

**Status:** Documentation — architectural principle for mainnet

---

## 1. DEX as Ecosystem Application (ARCH-034)

### 1.1 Principle

The Verdis Chain DEX (pallet-amm-dex) is an ecosystem application, NOT part of the protocol consensus layer. It must be treated as a separate product with its own regulatory exposure.

### 1.2 Current State

- DEX is a runtime pallet (on-chain, consensus-critical)
- DEX pools seeded at genesis
- DEX protocol fee (0.05%) collected to tokenomics treasury
- DEX is governed by the same governance as the protocol

### 1.3 Target State

| Aspect | Current | Target |
|--------|---------|--------|
| Code location | Runtime pallet | Runtime pallet (acceptable) |
| Governance | Protocol governance | Protocol governance (acceptable for core AMM) |
| Pool seeding | Genesis | Runtime governance (no genesis seeding on mainnet) |
| Frontend | verdischain.com/dex/ | Separate ecosystem frontend (independent operator) |
| Regulatory | Unaddressed | Legal review of DEX activities per jurisdiction |
| Fee collection | To tokenomics treasury | To tokenomics treasury (transparent) |

### 1.4 Separation Actions

1. Remove DEX pool seeding from mainnet genesis (pools created via governance post-launch)
2. Document DEX as ecosystem application, not protocol core
3. Consider separate legal entity for DEX operations
4. DEX frontend should be deployable by independent operators
5. Protocol fee collection must be transparent and auditable

---

## 2. Wallet as Ecosystem Product (ARCH-036)

### 2.1 Principle

The Verdis Chain wallet is an ecosystem product, NOT part of the protocol. Wallet compromise has high user impact but must not affect consensus.

### 2.2 Current State

- Web wallet: non-custodial, client-side key generation via @noble/secp256k1
- Android APK wallet: Flutter-based, same cryptographic primitives
- Both use TX Relay for submission (optional, can submit directly to RPC)
- Keys never leave the user's device

### 2.3 Security Requirements

1. **Key isolation**: Private keys generated and stored client-side only
2. **No server-side custody**: TX Relay never sees private keys
3. **Supply chain audit**: All NPM/Flutter dependencies must be audited
4. **CSP enforcement**: Content Security Policy prevents XSS key extraction
5. **Independent review**: Wallet must be audited by third-party (Mainnet Gate #6)

### 2.4 Hardware Wallet Roadmap (ARCH-038)

| Phase | Milestone | Target |
|-------|-----------|--------|
| Post-mainnet | Ledger integration | Support Ledger Nano S/X via Substrate app |
| 6 months | Polkadot.js extension | Support browser extension signing |
| 12 months | Trezor integration | Support Trezor hardware wallets |

### 2.5 Multiple Wallet Support

The protocol should support multiple independent wallets:
- Verdis Web Wallet (official, non-custodial)
- Verdis Android Wallet (official, non-custodial)
- Polkadot.js wallet (community, via SS58 compatibility)
- Any third-party wallet supporting Substrate SS58
