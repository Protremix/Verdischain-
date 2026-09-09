# Halborn Security — Audit Scoping Email (DRAFT)

**Status:** DRAFT — NOT SENT
**Prepared by:** Arlo (Chief Engineer, Verdis Chain)
**Date:** August 21, 2026
**Classification:** Pre-Engagement Correspondence

---

**To:** partnerships@halborn.com, audits@halborn.com
**From:** info@verdischain.com
**Subject:** Security Audit Scoping Inquiry — Verdis Chain (Substrate-based Layer-1, 16 Custom Pallets)

---

Dear Halborn Team,

We are writing to request a scoping call for a comprehensive security audit of Verdis Chain — a Substrate-based Layer-1 blockchain with native DPoS consensus, an integrated AMM DEX, eco-tracking features, and a complete tokenomics/vesting/presale infrastructure.

## Project Overview

**Verdis Chain** is an enterprise-grade blockchain built on the Substrate framework (Rust) with the following architecture:

- **Consensus:** Delegated Proof-of-Stake (DPoS) with BABE block production and GRANDPA finality
- **Native Token:** VRDX — 100,000,000,000 fixed max supply, 9 decimals, hard-capped in genesis via MaxSupplyCurrency wrapper
- **Runtime:** 16 custom pallets (listed below)
- **Current State:** Public testnet operational — Block #35,800+, 21 validators, 5 peers
- **Test Coverage:** 621 integration tests passing, 0 failures
- **Internal Security Score:** 100/100 (infrastructure + runtime code audit)

## Pallet Inventory (16 Pallets)

| # | Pallet | Description |
|---|--------|-------------|
| 1 | `dpos` | Delegated Proof-of-Stake consensus — validator selection, delegation, slashing, epoch rotation, downtime penalties |
| 2 | `amm-dex` | Automated Market Maker DEX — liquidity pools, swaps, LP tokens, protocol fees, 6 active pools |
| 3 | `eco` | Eco-tracking — green validator scoring, carbon credits, reforestation logging, CO2 offset metrics |
| 4 | `fungible-tokens` | Custom fungible token issuance and management — mint, burn, transfer, metadata |
| 5 | `tokenomics` | Token economy management — supply enforcement, allocation tracking, reward distribution |
| 6 | `vesting` | Token vesting schedules — cliff, linear vesting, multi-beneficiary, timestamp-based release |
| 7 | `presale` | Token presale — contribution tracking, hard cap, whitelist, refund mechanism, claim distribution |
| 8 | `governance` | On-chain governance — referenda, council, treasury proposals, voting mechanisms |
| 9 | `ibc` | Inter-Blockchain Communication — packet send/receive, channel management, root-origin verification |
| 10 | `circuit-breaker` | Emergency pause mechanism — pallet-level freeze, global halt, admin-triggered and automatic triggers |
| 11 | `address-lookup-tables` | Address lookup table optimization for transaction size reduction |
| 12 | `gulf-stream` | Transaction mempool management and propagation |
| 13 | `poh` | Proof of History — transaction ordering and timestamp verification |
| 14 | `sealevel` | Parallel transaction execution runtime |
| 15 | `storage` | On-chain storage management and rent mechanism |
| 16 | `turbine` | Block propagation and network sharding |
| 17 | `zk-compression` | Zero-knowledge proof compression for state verification |

Note: Pallets 11-17 are infrastructure optimization pallets. The primary audit focus should be pallets 1-10 which handle consensus, value transfer, and economic logic.

## Internal Security Work Completed

Before engaging Halborn, we have completed a comprehensive internal security review:

### Luna Adversarial Audit (Internal)

- **33 findings** identified and remediated across DPoS, IBC, AMM, Vesting, Eco, and Circuit-Breaker pallets
- **Critical fixes applied:**
  - C1: Presale double-spend vulnerability — contribution could be counted twice on simultaneous calls. Fixed with atomic storage updates.
  - H1-H2: MaxSupplyCurrency bypass risks — AMM read-only routes could bypass supply cap. Fixed by routing all transfers through wrapper.
  - H3-H4: DPoS commission and slashing authorization — missing origin checks on commission updates and slash destination. Fixed with proper `ensure_signed` / `ensure_root` checks.
  - H5: Vesting cliff calculation — off-by-one error in timestamp comparison. Fixed.
  - IBC C1-C3: Packet authentication — missing root-origin verification on send/receive paths. Fixed with `ensure_root` origin checks.
- **60 adversarial tests added** specifically targeting the presale/vesting/escrow lifecycle
- **All 33 findings resolved** with regression tests

### MaxSupplyCurrency Wrapper

- All 17 runtime currency interfaces replaced with `MaxSupplyCurrency` wrapper
- Enforces 100B VRDX hard cap via atomic checked arithmetic
- Prevents inflationary minting through any pallet (DEX, tokenomics, staking rewards)
- Validated with 561 workspace tests (now expanded to 621)

### Infrastructure Hardening

- Security score: 100/100 (18 security checks pass)
- RPC interfaces restricted to localhost
- UFW firewall active (P2P 30333-30341, SSH 22 only)
- Validator key files restricted to 600 permissions
- All 6 security headers active on nginx (HSTS, CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy)

## Questions for Scoping

1. **Scope:** What is the recommended audit scope for a 16-pallet Substrate chain? Do you recommend auditing all pallets or focusing on consensus + value-transfer pallets first?

2. **Timeline:** What is your current lead time to start a new engagement? What is the typical duration for a Substrate chain of this size?

3. **Methodology:** Do you perform both automated (fuzzing, property-based testing) and manual review? What static analysis tools do you use for Rust/Substrate?

4. **Deliverables:** What does your final report include? Do you provide a public-facing summary suitable for investor due diligence?

5. **Remediation:** Do you offer a remediation review phase after we fix findings? Is this included in the base price or separate?

6. **Team:** Who on your team specializes in Substrate/Polkadot architecture? What is their experience level with DPoS consensus?

7. **Cost:** What is the estimated cost range for a project of this scope (16 pallets, ~620 tests, Substrate framework)?

8. **References:** Can you share references from previous Substrate-based chain audits?

## Technical Artifacts Available

- Complete source code (Rust, Substrate framework)
- Chain specification files (testnet + mainnet)
- Internal audit report (`AUDIT_REMEDIATION.md`, `FINAL_SECURITY_AUDIT.md`)
- External audit readiness package (`EXTERNAL-AUDIT-READINESS.md`)
- Architecture documentation (`ARCHITECTURE.md`, `ARCHITECTURAL_DECISIONS.md`)
- Threat model (`THREAT_MODEL.md`)
- Dependency inventory (`DEPENDENCY_INVENTORY.md`, `DEPENDENCY_SECURITY.md`)
- Key management documentation (`KEY_MANAGEMENT.md`)
- Treasury security specification (`TREASURY_SECURITY.md`)
- 10 mandatory engineering documents per our internal Constitution

## Target Commit

We will freeze a release candidate commit for the audit. Current HEAD: `da29b831`. We can provide a clean commit hash once the engagement is confirmed.

## Next Steps

We would like to schedule a scoping call within the next 1-2 weeks. Please let us know your availability and any additional information you need from us before the call.

Thank you for your time. We look forward to working with Halborn to achieve mainnet-ready security certification.

Best regards,

Verdis Chain Engineering Team
info@verdischain.com
https://verdischain.com

---

**END OF DRAFT — DO NOT SEND UNTIL ROJS APPROVES**
