# Verdis Chain Testnet Test Results

**Last Updated:** 2026-08-14 15:07 UTC  
**Commit SHA:** `2261c82b`

## Compilation Tests

| Test | Command | Result |
|---|---|---|
| cargo build --release | `cargo build --release` | PASS (1m 31s) |
| cargo fmt --check | `cargo fmt --check` | PASS |
| cargo check --workspace | `cargo check --workspace` | PASS |
| cargo test --workspace | `cargo test --workspace` | PASS (0 failures) |
| cargo clippy | `cargo clippy --workspace` | PASS (0 errors) |
| cargo audit | `cargo audit` | 8 vulnerabilities (dep updates needed) |
| WASM build | `cargo build --release` | PASS (included in release build) |

## Pallet Test Counts

| Pallet | Test Functions | Test Files |
|---|---|---|
| DPoS | 115 | integration_tests.rs, slashing_tests.rs |
| Tokenomics | 40 | property_tests.rs |
| Vesting | 84 | vesting_tests.rs, edge_case_tests.rs |
| DEX (AMM) | 51 | mod.rs, security_regression_tests.rs |
| Sealevel | 9 | — |
| **Total** | **299** | — |

## On-Chain Verification

| Check | Method | Result |
|---|---|---|
| Block production | RPC chain_getHeader | PASS |
| Finality | journalctl grep finalized | PASS |
| Peer connectivity | RPC system_health | PASS (2 peers) |
| Validator registration | RPC dpos_allValidators | PASS (6 registered) |
| Active validators | RPC dpos_activeValidators | PASS (3 active) |
| DEX pools | RPC amm_dex_getAllPools | PASS (6 pools) |
| Token symbol | Chain spec properties | PASS (VRDX) |
| Decimals | Chain spec properties | PASS (9) |
| Total supply | Genesis balances | PASS (100B VRDX) |
| Sudo removed | Chain spec + runtime | PASS |
| Session keys | Journalctl | PASS (0 errors for active validators) |

## Consensus Recovery Tests

| Test | Result | Notes |
|---|---|---|
| Node shutdown | PASS | Chain continued #64->#69, finality maintained |
| Node restart | PASS | Node3 resynced to #72, peers restored to 2 |
| Peer connection loss | PASS | Peers dropped 2->1, chain continued |
| Multiple validators offline | PASS | 2/3 nodes stopped, BABE continued |
| Node resynchronization | PASS | Both nodes resynced after restart |

## Smart Contract (Sealevel) E2E Verification

| Check | Method | Result |
|---|---|---|
| Pallet in runtime | state_getMetadata | PASS (pallet index 56) |
| create_batch extrinsic | Metadata | PASS |
| report_execution extrinsic | Metadata | PASS |
| report_conflict extrinsic | Metadata | PASS |
| create_batch_parallel_works | Unit test | PASS |
| create_batch_sequential_works | Unit test | PASS |
| report_execution_works | Unit test | PASS |
| report_conflict_works | Unit test | PASS |
| Unsigned rejection | Unit test | PASS |
| Max size exceeded | Unit test | PASS |
| Compute budget exceeded | Unit test | PASS |
| Total tests | 11/11 | ALL PASS |

## Treasury Multisig

| Check | Method | Result |
|---|---|---|
| 3-of-5 multisig origin | Code review | PASS (EnsureMultisigOrCouncilSpend) |
| Pre-ceremony fallback | Code review | PASS (Council 2/3) |
| Post-ceremony multisig | Code review | PASS (pallet_multisig integration) |
| Compilation | cargo build | PASS |
| Tests | cargo test | PASS (no regressions) |

## Soak Test

| Metric | Value |
|---|---|
| Start date | 2026-08-14 13:05 UTC |
| Duration | 0 days (just started) |
| Required duration | 14 days |
| Status | IN PROGRESS |

## Security Audits

| Audit | Date | Result |
|---|---|---|
| Internal (Claude) | 2026-08-14 | 30 findings (5 Critical, 7 High, 8 Medium, 5 Low, 5 Info) |
| Internal (GPT-4o) | 2026-08-14 | See docs/security-audit.md |
| Independent third-party | NOT STARTED | Required before mainnet |
