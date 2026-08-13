# VERDIS CHAIN — MAINNET READINESS CHECKLIST

**Created:** 2026-08-14
**Status:** IN PROGRESS — Based on Kimi's 8-phase roadmap

---

## PHASE 0: TOKENOMICS & GOVERNANCE (2 weeks)

| # | Task | Status | Evidence |
|---|---|---|---|
| 0.1 | Tokenomics 9-category allocation (100B) | ✅ DONE | Code: chain_spec.rs |
| 0.2 | Treasury = 20B (code = source of truth) | ✅ DONE | Kimi confirmed |
| 0.3 | Economic invariants (8 tests) | ✅ DONE | pallets/tokenomics/src/economic_invariants.rs |
| 0.4 | Vesting schedules (seed, presale, team) | ✅ DONE | chain_spec.rs mainnet_genesis() |
| 0.5 | Governance: Council + Tech Committee + Democracy | ✅ DONE | runtime/src/lib.rs |
| 0.6 | Treasury spending via governance | ✅ DONE | runtime/src/lib.rs |
| 0.7 | Tokenomics documentation | ✅ DONE | docs/TOKENOMICS_FINAL.md |

## PHASE 1: VALIDATORS & GENESIS (3 weeks)

| # | Task | Status | Evidence |
|---|---|---|---|
| 1.1 | Separate dev/testnet/mainnet chain specs | ✅ DONE | chain_spec.rs |
| 1.2 | pallet_sudo removed from mainnet | ✅ DONE | mainnet_genesis() has no sudo |
| 1.3 | 21 validators in mainnet spec | ✅ DONE | mainnet_validator_uris() |
| 1.4 | Air-gapped key ceremony script | ✅ DONE | scripts/air-gapped-key-ceremony.sh |
| 1.5 | Key import script | ✅ DONE | scripts/import-mainnet-keys.py |
| 1.6 | Run actual air-gapped ceremony | ❌ PENDING | Requires physical air-gapped machine |
| 1.7 | Import real validator keys into chain spec | ❌ PENDING | Requires ceremony output |
| 1.8 | Replace PalletId team multisig with 3-of-5 cold storage | ❌ PENDING | PalletId(*b"verdistm") still in code |
| 1.9 | Verify genesis state root determinism | ❌ PENDING | Need to build and verify |
| 1.10 | Test session key rotation | ❌ PENDING | Needs real keys |

## PHASE 2: SECURITY HARDENING (4 weeks)

| # | Task | Status | Evidence |
|---|---|---|---|
| 2.1 | Internal security audit (72→100/100) | ✅ DONE | docs/AUDIT_STATUS.md |
| 2.2 | Bounded Vec<u8> on all extrinsics | ✅ DONE | Phase 150 |
| 2.3 | Safe integer casts (try_from) | ✅ DONE | Phase 150 |
| 2.4 | DEX overflow protection (checked_mul) | ✅ DONE | Phase 159 |
| 2.5 | Self-transfer guard | ✅ DONE | Phase 159 |
| 2.6 | LP overflow/underflow protection | ✅ DONE | Phase 146 |
| 2.7 | Eco pallet auth (root only) | ✅ DONE | Phase 149 |
| 2.8 | Independent third-party security audit | ❌ PENDING | Not engaged |
| 2.9 | Penetration testing | ❌ PENDING | Not performed |
| 2.10 | Formal verification of critical paths | ❌ PENDING | Not performed |

## PHASE 3: TESTING (4 weeks)

| # | Task | Status | Evidence |
|---|---|---|---|
| 3.1 | 491 unit tests across 16 pallets | ✅ DONE | See test count |
| 3.2 | 50 IBC tests | ✅ DONE | pallets/ibc/src/tests.rs |
| 3.3 | 85 presale tests | ✅ DONE | pallets/presale/src/tests.rs |
| 3.4 | 42 vesting tests | ✅ DONE | pallets/vesting/src/tests/ |
| 3.5 | 71 DPoS tests (incl slashing) | ✅ DONE | pallets/dpos/src/tests/ |
| 3.6 | 37 DEX tests | ✅ DONE | pallets/amm-dex/src/tests.rs |
| 3.7 | 70 tokenomics + economic invariant tests | ✅ DONE | pallets/tokenomics/ |
| 3.8 | Property-based tests | ✅ DONE | 8 property-based vesting tests |
| 3.9 | Integration tests (multi-pallet) | ❌ PENDING | Not created |
| 3.10 | Stress/load tests | ❌ PENDING | Not created |
| 3.11 | Chaos testing (node failure, partition) | ❌ PENDING | Not created |

## PHASE 4: BENCHMARKING (3 weeks)

| # | Task | Status | Evidence |
|---|---|---|---|
| 4.1 | Weight annotations on all dispatchables | ❌ PENDING | Not verified |
| 4.2 | Benchmarking framework setup | ❌ PENDING | Not started |
| 4.3 | TPS benchmarks | ❌ PENDING | Not measured |
| 4.4 | Block execution time benchmarks | ❌ PENDING | Not measured |
| 4.5 | Storage growth benchmarks | ❌ PENDING | Not measured |
| 4.6 | Network latency benchmarks | ❌ PENDING | Not measured |

## PHASE 5: DEVOPS & MONITORING (4 weeks)

| # | Task | Status | Evidence |
|---|---|---|---|
| 5.1 | Docker multi-stage build | ✅ DONE | Dockerfile |
| 5.2 | Docker Compose for multi-node | ✅ DONE | docker-compose.yml |
| 5.3 | Nginx reverse proxy | ✅ DONE | nginx.conf |
| 5.4 | CI/CD pipeline (fmt/check/test/clippy) | ✅ DONE | .github/workflows/ci.yml |
| 5.5 | Security scan workflow | ✅ DONE | .github/workflows/security.yml |
| 5.6 | Secret scan workflow | ✅ DONE | .github/workflows/secret-scan.yml |
| 5.7 | Release workflow | ✅ DONE | .github/workflows/release.yml |
| 5.8 | Docker workflow | ✅ DONE | .github/workflows/docker.yml |
| 5.9 | Try-runtime workflow | ✅ DONE | .github/workflows/try-runtime.yml |
| 5.10 | Grafana monitoring | ✅ DONE | Server: Grafana on port 3000 |
| 5.11 | Prometheus metrics | ✅ DONE | Node exporter + Prometheus |
| 5.12 | Health monitor | ✅ DONE | verdis-health-monitor service |
| 5.13 | Log rotation | ✅ DONE | Docker log rotation |
| 5.14 | Backup script | ✅ DONE | scripts/backup.sh |
| 5.15 | Alerting (Slack/email/PagerDuty) | ❌ PENDING | Not configured |

## PHASE 6: DOCS & ECOSYSTEM (3 weeks)

| # | Task | Status | Evidence |
|---|---|---|---|
| 6.1 | JavaScript SDK (51 methods) | ✅ DONE | sdk/verdis-sdk.js |
| 6.2 | SDK documentation | ✅ DONE | README.md + VERDIS-SDK-GUIDE.md |
| 6.3 | Public source of truth | ✅ DONE | docs/PUBLIC_SOURCE_OF_TRUTH.md |
| 6.4 | Risk disclosure | ✅ DONE | docs/PUBLIC_RISK_DISCLOSURE.md |
| 6.5 | Legal regulatory matrix | ✅ DONE | docs/LEGAL_REGULATORY_MATRIX.md |
| 6.6 | Treasury policy | ✅ DONE | docs/TREASURY_POLICY.md |
| 6.7 | Developer documentation page | ✅ DONE | /docs/ on website |
| 6.8 | Whitepaper | ⚠️ PARTIAL | Live but needs MiCA format update |
| 6.9 | API documentation | ❌ PENDING | Not created (RPC methods) |
| 6.10 | Validator setup guide | ❌ PENDING | Not created |
| 6.11 | Node operator guide | ❌ PENDING | Not created |

## PHASE 7: TESTNET REHEARSAL & LAUNCH (4 weeks)

| # | Task | Status | Evidence |
|---|---|---|---|
| 7.1 | Testnet with 21 validators | ⚠️ PARTIAL | 6 dev validators, 21 in spec |
| 7.2 | Testnet with real keys (not Alice-Ferdie) | ❌ PENDING | Still using test keys |
| 7.3 | Full sync test (3+ nodes) | ❌ PENDING | 0 peers currently |
| 7.4 | Runtime upgrade rehearsal | ❌ PENDING | Not tested |
| 7.5 | Recovery procedure test | ❌ PENDING | Not tested |
| 7.6 | Genesis state verification | ❌ PENDING | Not verified |
| 7.7 | Final code freeze | ❌ PENDING | Not done |
| 7.8 | Mainnet launch | ❌ PENDING | Blocked by above |

---

## SUMMARY

| Phase | Total Tasks | Done | Pending | Partial | % Complete |
|---|---|---|---|---|---|
| 0: Tokenomics | 7 | 7 | 0 | 0 | 100% |
| 1: Validators | 10 | 5 | 5 | 0 | 50% |
| 2: Security | 10 | 7 | 3 | 0 | 70% |
| 3: Testing | 11 | 8 | 3 | 0 | 73% |
| 4: Benchmarking | 6 | 0 | 6 | 0 | 0% |
| 5: DevOps | 15 | 14 | 1 | 0 | 93% |
| 6: Docs | 11 | 7 | 3 | 1 | 64% |
| 7: Launch | 8 | 0 | 7 | 1 | 0% |
| **TOTAL** | **78** | **48** | **28** | **2** | **62%** |

---

## CRITICAL BLOCKERS (must resolve before mainnet)

1. **Air-gapped key ceremony** — Generate and import 21 real validator keys
2. **3-of-5 cold storage multisig** — Replace PalletId team account
3. **Independent security audit** — Engage third-party auditor
4. **Benchmarking** — Weight annotations and TPS measurement
5. **Integration/chaos testing** — Multi-pallet and failure scenarios
6. **Genesis determinism** — Verify state root is reproducible
7. **Legal entity** — Document and make public
8. **Validator setup guide** — Documentation for external operators

## RECOMMENDED ORDER

1. Phase 1: Run ceremony, import keys, replace multisig (CRITICAL)
2. Phase 2: Engage external auditor (CRITICAL)
3. Phase 3: Write integration tests (HIGH)
4. Phase 4: Add weight annotations + benchmark (HIGH)
5. Phase 7: Testnet rehearsal with real keys (HIGH)
6. Phase 6: Complete documentation (MEDIUM)
7. Phase 5: Configure alerting (MEDIUM)
