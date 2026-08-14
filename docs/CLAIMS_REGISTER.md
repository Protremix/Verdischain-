# Verdis Chain Claims Register (ARCH-046)

**Purpose:** Every public claim about Verdis Chain must have evidence. No claim may be published without a source in this register.
**Owner:** Product + Legal
**Last Updated:** 2026-08-14

---

## Technical Claims

| Claim | Evidence | Source | Status | Last Verified |
|-------|----------|--------|--------|---------------|
| Layer-1 blockchain in Rust + Substrate | Source code | node/src/, runtime/src/, pallets/ | VERIFIED | 2026-08-14 |
| Native DPoS consensus | Source code | pallets/dpos/src/lib.rs | VERIFIED | 2026-08-14 |
| BABE block production | Runtime config | runtime/src/lib.rs | VERIFIED | 2026-08-14 |
| GRANDPA finality | Runtime config | runtime/src/lib.rs | VERIFIED | 2026-08-14 |
| AMM-based DEX | Source code | pallets/amm-dex/src/lib.rs | VERIFIED | 2026-08-14 |
| Carbon credit tracking | Source code | pallets/eco/src/lib.rs | VERIFIED | 2026-08-14 |
| Green validator scoring | Source code | pallets/dpos/src/lib.rs | VERIFIED | 2026-08-14 |
| 16 pallets | Source code | runtime/src/lib.rs | VERIFIED | 2026-08-14 |
| 76 DPoS tests pass | Test run | cargo test -p pallet-dpos | VERIFIED | 2026-08-14 |
| @noble/secp256k1 for crypto | Source code | web/wallet/package.json | VERIFIED | 2026-08-14 |
| SS58 prefix 909 | Chain spec | node/src/chain_spec.rs | VERIFIED | 2026-08-14 |
| pallet_sudo removed from mainnet | Source code | runtime/src/lib.rs | VERIFIED | 2026-08-14 |

## Tokenomics Claims

| Claim | Evidence | Source | Status | Last Verified |
|-------|----------|--------|--------|---------------|
| 100B total supply | Genesis code | scripts/check_genesis_consistency.py | VERIFIED (CI) | 2026-08-14 |
| 9 decimals | Chain spec | node/src/chain_spec.rs | VERIFIED | 2026-08-14 |
| Token symbol VRDX | Chain spec | node/src/chain_spec.rs | VERIFIED | 2026-08-14 |
| Treasury 20B | Genesis code | scripts/check_genesis_consistency.py | VERIFIED (CI) | 2026-08-14 |
| 9 allocations | Genesis code | node/src/chain_spec.rs | VERIFIED | 2026-08-14 |
| Seed vesting 12mo cliff | Chain spec | node/src/chain_spec.rs (730 blocks) | VERIFIED | 2026-08-14 |
| Presale vesting 6mo cliff | Chain spec | node/src/chain_spec.rs (365 blocks) | VERIFIED | 2026-08-14 |
| Team vesting 18mo cliff | Chain spec | node/src/chain_spec.rs (1095 blocks) | VERIFIED | 2026-08-14 |

## Security Claims

| Claim | Evidence | Source | Status | Last Verified |
|-------|----------|--------|--------|---------------|
| Internal security review completed | Audit report | docs/security-audit.md | VERIFIED | 2026-08-14 |
| Independent third-party audit | NOT COMPLETED | N/A | NOT VERIFIED | N/A |
| 3-of-5 treasury multisig | Spec doc | docs/TREASURY_SECURITY_SPEC.md | SPEC ONLY | 2026-08-14 |
| AES-GCM encryption (TX Relay) | Source code | tx-relay v3 | VERIFIED | 2026-08-14 |
| Non-custodial wallet | Source code | web/wallet/ | VERIFIED | 2026-08-14 |
| Security headers (HSTS, CSP) | Nginx config | /etc/nginx/ | VERIFIED | 2026-08-14 |

## Infrastructure Claims

| Claim | Evidence | Source | Status | Last Verified |
|-------|----------|--------|--------|---------------|
| Testnet live | Node running | systemctl status | VERIFIED | 2026-08-14 |
| 6 active validators | On-chain | RPC dpos_allValidators | VERIFIED | 2026-08-14 |
| Docker hardened config | Source code | Dockerfile | VERIFIED | 2026-08-14 |
| GitHub CI/CD | Workflows | .github/workflows/ | VERIFIED | 2026-08-14 |

## Team Claims

| Claim | Evidence | Source | Status | Last Verified |
|-------|----------|--------|--------|---------------|
| Rojs Gordons (Founder) | Public records | web/team/ page | VERIFIED | 2026-08-14 |
| Dorian Jean (CEO) | Public records | web/team/ page | VERIFIED | 2026-08-14 |
| Mark Roetzer P.E. (CTO) | Public records | web/team/ page | VERIFIED | 2026-08-14 |
| Maria Dolores Marquez de Prado | Public records | web/team/ page | VERIFIED | 2026-08-14 |
| Ignacio Martinez-Arrieta | Public records | web/team/ page | VERIFIED | 2026-08-14 |
| Elizabeth Jefferson | Public records | web/team/ page | VERIFIED | 2026-08-14 |

## Claims NOT Allowed (Removed)

| Former Claim | Why Removed | Date Fixed |
|-------------|------------|------------|
| "$18M Total Raised" | False - $0 received | 2026-08-14 |
| "Carbon Negative" | Not verified | 2026-08-14 |
| "World's First Green Blockchain" | Not verified | 2026-08-14 |
| "Comprehensive security audit" | Only internal review | 2026-08-14 |
| "Verra/WWF/UN partnerships" | Not verified | 2026-08-14 |
| "30+ pallets" | Only 16 pallets | 2026-08-14 |
| "MIT License" | Changed to Proprietary | 2026-08-14 |
| "Referral program" | Removed (no legal review) | 2026-08-14 |
| "100% auditable" | Changed to "designed for transparency" | 2026-08-14 |
| "Officially launched" | Changed to "launched testnet" | 2026-08-14 |
