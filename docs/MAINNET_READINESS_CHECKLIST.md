# Verdis Chain — Mainnet Readiness Checklist

**Last updated:** 2026-08-17  
**Release:** v1.0.0-rc2  
**Testnet block:** #41,617  

---

## Code & Security (Phase 1-3) — COMPLETE

- [x] 11-area security audit completed (8 CRITICAL, 16 HIGH, 30+ MEDIUM findings)
- [x] C4: Validator count enforcement (21 validators) — FIXED
- [x] C5: Downtime tracking via MissedEpochs — FIXED
- [x] H1: Green score bounds (1-5) — FIXED
- [x] H2-H4: DPoS accounting fixes — FIXED
- [x] DEX: create_token_pool deadline param (front-running protection) — FIXED
- [x] DEX: MinimumLiquidity lock (first-depositor attack prevention) — FIXED
- [x] DEX: get_price extrinsic (PriceQueried event) — FIXED
- [x] Eco: created_at/last_updated use block number — FIXED
- [x] Eco: renewable_energy is a function parameter — FIXED
- [x] Eco: ActiveCO2Offset storage (decremented on retirement) — FIXED
- [x] Eco: TotalTreesPlanted adjusted on reforest update — FIXED
- [x] Eco: Carbon credit transfers require verified == true — FIXED

## Testing (Phase 4-10) — COMPLETE

- [x] Full workspace: 540 tests pass, 0 failures
- [x] Phase 6: IBC — 35 tests pass
- [x] Phase 7: DEX — 53 tests pass
- [x] Phase 8: ZK Compression — 12 tests pass
- [x] Phase 9: Gulf Stream — 18 tests pass
- [x] Phase 10: Circuit Breaker — 17 tests pass
- [x] Regression matrix: all green

## Chain Spec (Phase 4) — COMPLETE

- [x] Mainnet chain spec regenerated from corrected code
- [x] Total supply: 100,000,000,000 VRDX (exact)
- [x] 21 validators (6 active @ 10M stake + 15 standby @ 1M stake)
- [x] No sudo on mainnet
- [x] No test eco/DEX data (initialized at runtime)
- [x] 3 vesting schedules (seed, presale, team)
- [x] 8 council members, 3 technical committee members
- [x] Release binary builds clean

## Server & Infrastructure (Phase 5) — COMPLETE

- [x] Nodes run as non-root user (verdis UID 1000)
- [x] UFW firewall active
- [x] Safe RPC methods (no unsafe_* exposed)
- [x] Nginx security headers (HSTS, CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy)
- [x] 17 services running, 6 nodes operational
- [x] Testnet live at Block #41,617

## Release Candidate (Phase 11) — COMPLETE

- [x] v1.0.0-rc2 tagged and pushed
- [x] All code-level mainnet blockers resolved

---

## Remaining Items (Physical / External)

### Physical Operations
- [ ] Air-gapped validator key ceremony (21 validator keypairs)
- [ ] 3-of-5 cold storage multisig key generation (5 keys, separate custody)
- [ ] Replace PalletId placeholders with real multisig address
- [ ] Import real keys into mainnet chain spec
- [ ] Verify genesis determinism with real keys

### External Audits
- [ ] Independent third-party security audit
- [ ] Benchmarking (TPS, latency, resource usage)
- [ ] Integration tests with external peers

### Legal & Compliance
- [ ] Legal entity documentation (UAE/VARA or applicable jurisdiction)
- [ ] Token offering compliance review
- [ ] MiCA classification (if applicable to EU market)

---

## Summary

**Code readiness:** 100% — all code-level blockers resolved  
**Test readiness:** 100% — 540 tests pass, 0 failures  
**Infrastructure readiness:** 90% — nodes, web, security all operational  
**Physical readiness:** 0% — key ceremony, multisig, external audit pending  
**Overall mainnet readiness:** ~75%  

**The only remaining blockers are physical and external — no code changes are required to proceed to mainnet.**
