# Verdis Chain Release Candidate v1.0.0-rc1

**Date:** 2026-08-17
**Git Commit:** 3e924160
**Status:** Release Candidate — Mainnet Ready (pending key ceremony)

## Test Results

| Phase | Description | Result |
|-------|-------------|--------|
| 1 | BUILD (release binary) | ✅ PASS |
| 2 | Regression tests (all pallets) | ✅ 540 tests, 0 failures |
| 3 | Test matrix (IBC/DEX/ZK/Gulf Stream) | ✅ PASS |
| 4 | Mainnet chain spec generation | ✅ Deterministic, verified |
| 5 | Server security (non-root, UFW, RPC) | ✅ Verified |
| 6 | IBC regression (35 tests) | ✅ PASS |
| 7 | DEX security regression (18 tests) | ✅ PASS |
| 8 | ZK compression (12 tests) | ✅ PASS |
| 9 | Gulf Stream (18 tests) | ✅ PASS |
| 10 | Full workspace (540 tests) | ✅ PASS |
| 11 | Release candidate commit | ✅ This commit |

## Security Audit Status

- 11-area comprehensive audit completed
- 8 CRITICAL findings remediated
- 16 HIGH findings remediated
- 30+ MEDIUM findings addressed
- Audit score: 100/100 (all checks pass)

## Mainnet Chain Spec Verification

- Total supply: 100,000,000,000 VRDX (100B) ✅
- 9-category tokenomics allocation ✅
- 21 DPoS validators (6 active, 15 standby) ✅
- No Sudo pallet ✅
- No test DEX pools or eco data ✅
- Deterministic (verified via dual generation) ✅
- Vesting schedules: seed (730d/365 cliff), presale (365d/180 cliff), team (1095d/365 cliff) ✅

## Remaining Mainnet Blockers (External Only)

1. **Key Ceremony:** 21 validator keypairs must be generated on air-gapped machine
2. **3-of-5 Multisig:** Replace PalletId placeholder with real cold-storage multisig address
3. **Independent Security Audit:** Third-party audit required before TGE
4. **Genesis Distribution:** Replace placeholder validator URIs with real keys

## What Changed Since Last Release

- Fixed 5 DPoS test failures (green_score bounds exceeded MaxGreenScore=5)
- Fixed 2 vesting test failures (wrong error variants for InvalidVestingDays)
- Fixed 2 ZK proof test failures (pre-existing: missing tree creation setup)
- Regenerated mainnet chain spec from corrected code
- All 540 workspace tests pass with 0 failures

## Disclaimer

This release candidate is mainnet-ready at the code level. Production deployment
requires the external items listed above (key ceremony, multisig, independent audit).
Do NOT deploy to mainnet without completing these steps.
