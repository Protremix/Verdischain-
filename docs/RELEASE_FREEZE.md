# VERDIS CHAIN — RELEASE FREEZE DECLARATION

**Date:** 2026-08-23  
**Declared by:** Arlo (Chief Engineer & Technical Security Authority)  
**Git commit:** `ca3bacec` (HEAD of master)  
**Constitution Reference:** Article 21 (Mainnet GO/NO-GO gates)

---

## RELEASE FREEZE SCOPE

Effective immediately, the following codebase is FROZEN for the current audit cycle:

```
Repository:    https://github.com/Protremix/Verdischain-.git
Branch:        master
Commit:        ca3bacec
Frozen files:  ALL pallets, runtime, node, CI/CD workflows
```

**No code changes shall be made to the following pallets until the Halborn audit is complete:**
- `pallet-presale` (261 tests, 27 MASTER-9 evidence tests)
- `pallet-dpos` (93 tests)
- `pallet-amm-dex` (53 tests)
- `pallet-eco` (37 tests)
- `pallet-vesting` (35 tests)
- `pallet-tokenomics` (31 tests)
- `pallet-fungible-tokens` (17 tests)
- `pallet-governance` (59 tests)
- `pallet-contracts` (93 tests)
- `runtime/src/` (all configuration)
- `node/src/` (all chain spec and service code)
- `.github/workflows/` (all CI/CD pipelines)

**Exception:** Critical security fixes identified during the audit. Any such fix requires:
1. Arlo's written approval
2. Minimal diff (no refactoring)
3. New regression test covering the vulnerability
4. Re-run of full workspace test suite
5. Updated commit hash documented in this file

---

## FINAL REGRESSION RESULTS

```
Date:           2026-08-23 21:10 UTC+2
Commit:         ca3bacec
Total tests:    734
Passed:         734
Failed:         0
Ignored:        0

Clippy:         PASS (2 warnings in pallet-eco, no errors)
Formatting:     PASS (cargo fmt --all -- --check clean)
WASM build:     PASS (cargo build --release -p verdis-runtime)
Release build:  PASS (cargo build --release -p verdis-node)
```

### Per-pallet breakdown:

| Pallet | Tests | Status |
|---|---|---|
| pallet-balances (wrapper) | 6 | ✅ PASS |
| pallet-dpos | 93 | ✅ PASS |
| pallet-amm-dex | 53 | ✅ PASS |
| pallet-eco | 37 | ✅ PASS |
| pallet-tokenomics | 31 | ✅ PASS |
| pallet-vesting | 35 | ✅ PASS |
| pallet-fungible-tokens | 17 | ✅ PASS |
| pallet-presale | 261 | ✅ PASS (27 MASTER-9 evidence tests) |
| pallet-governance | 59 | ✅ PASS |
| pallet-contracts | 93 | ✅ PASS |
| Other pallets | 45 | ✅ PASS |
| Integration tests | 20 | ✅ PASS (incl presale→vesting flow) |
| Doc tests | 0 | ✅ PASS |

---

## PAYMENT ASSET DECISION (APPROVED)

```
TESTNET PAYMENT ASSET          = VRDX (native, MaxSupplyCurrency)
CURRENT AUDIT PAYMENT ASSET   = VRDX (native, MaxSupplyCurrency)
MAINNET PAYMENT ASSET         = VRDX, PENDING FINAL LEGAL/CEX/TOKENOMICS CONFIRMATION
```

**Approved by:** Rojs Gordons (project owner) — 2026-08-23  
**Decision:** Option A — VRDX-as-payment for testnet and audit release  
**Condition:** This decision is NOT irreversible for mainnet. Final mainnet payment asset subject to legal/CEX/tokenomics confirmation.  
**Code modification:** NONE. No changes to presale code. Current implementation preserved.

**Runtime configuration (unchanged):**
```rust
impl pallet_presale::Config for Runtime {
    type Currency = MaxSupplyCurrency;           // VRDX token distribution
    type PaymentCurrency = MaxSupplyCurrency;    // VRDX payment collection
    type AdminOrigin = Council 2/3;
    type Vesting = PresaleVestingHandler;
    type WeightInfo = pallet_presale::SubstrateWeight<Runtime>;
    type Treasury = TreasuryAccount;
    type EnforceUniqueVestingLabels = ConstBool<true>;
}
```

---

## HALBORN AUDIT PREPARATION

### Audit Scope

The Halborn audit shall cover the full Verdis Chain runtime:

**Pallets (16):**
1. pallet-dpos — DPoS consensus, validator selection, slashing, epoch rotation
2. pallet-amm-dex — AMM DEX, 6 liquidity pools, swap/add/remove liquidity
3. pallet-presale — multi-round presale, escrow, refund, vesting, collection
4. pallet-vesting — scheduled vesting, MaxSchedulesPerAccount, release
5. pallet-eco — green validator scoring, carbon credits, reforestation
6. pallet-tokenomics — 100B supply cap, 9-category allocation, mint/burn
7. pallet-fungible-tokens — custom token creation, mint/burn/transfer
8. pallet-governance — democracy, council, treasury spend
9. pallet-contracts — smart contract execution
10. pallet-multisig — multisig operations
11. pallet-proxy — proxy accounts
12. pallet-scheduler — scheduled dispatches
13. pallet-preimage — preimage management
14. pallet-sudo — emergency superuser (testnet only)
15. pallet-session — session key management
16. pallet-timestamp — block timestamp

**Runtime:**
- construct_runtime! composition
- MaxSupplyCurrency wrapper (100B cap enforcement)
- Chain spec (genesis configuration)
- RPC extensions (157 methods)
- Weight calculations

**Node:**
- Service composition
- CLI commands
- Network protocol (BABE/GRANDPA)

### Pre-Audit Checklist

- [x] All 734 tests passing, 0 failures
- [x] CI/CD pipeline green (fmt, clippy, test, WASM, release)
- [x] Code formatting clean (cargo fmt --all -- --check)
- [x] Clippy clean (no errors, 2 non-critical warnings)
- [x] Release build successful
- [x] WASM build successful
- [x] Presale payment asset decision documented and approved
- [x] All P0/P1/P2/P3 audit findings from previous internal audit resolved
- [x] MASTER-1 through MASTER-9 evidence test suites complete
- [x] Luna adversarial test suite complete (8 attacks, all BLOCKED)
- [x] Integration tests complete (20 tests, incl presale→vesting)
- [ ] Halborn audit engagement letter signed
- [ ] Halborn audit scope confirmed
- [ ] Halborn audit timeline agreed
- [ ] Code repository access granted to Halborn team
- [ ] Documentation package delivered to Halborn

### Documentation Package for Halborn

The following documents are available in `/docs/`:

1. `MAINNET_PRESALE_PAYMENT_ASSET_DECISION.md` — Payment asset analysis and decision
2. `MAINNET_READINESS_CHECKLIST.md` — 78-task mainnet checklist
3. `SECURITY_LOG.md` — Security findings and remediations log
4. `SECURITY_INCIDENT_RESPONSE.md` — Incident response procedures
5. `MAINNET_READINESS.md` — Mainnet readiness assessment
6. `ARCHITECTURE.md` — System architecture documentation
7. `THREAT_MODEL.md` — Threat model and attack surfaces
8. `KEY_MANAGEMENT.md` — Key management procedures
9. `TREASURY_SECURITY.md` — Treasury security specification
10. `DEPENDENCY_SECURITY.md` — Dependency security analysis
11. `AUDIT_REMEDIATION.md` — Previous audit findings and remediations
12. `RPC_API_REFERENCE.md` — Full RPC API documentation
13. `VALIDATOR_SETUP_GUIDE.md` — Validator setup procedures

### Halborn Audit Targets

Based on the internal security audit (100/100 score, all P0/P1 fixed), the following areas should receive special attention:

1. **Presale escrow isolation** — Per-round escrow accounts, fund isolation, refund atomicity
2. **DPoS slashing** — Validator downtime detection, slashing logic, reactivation cooldown
3. **AMM DEX** — Liquidity pool accounting, overflow protection, reentrancy
4. **Vesting schedule** — MaxSchedulesPerAccount enforcement, release calculation
5. **Tokenomics supply cap** — MaxSupplyCurrency enforcement, mint path audit
6. **Governance multisig** — Council 2/3 origin, treasury spend authorization
7. **Weight calculations** — Weight sufficiency for all dispatchables

---

## RELEASE FREEZE LOG

| Date | Action | Commit | Author |
|---|---|---|---|
| 2026-08-23 | Release freeze declared | ca3bacec | Arlo |
| 2026-08-23 | Payment asset decision approved (Option A) | ca3bacec | Rojs |
| 2026-08-23 | Final regression: 734 tests, 0 failures | ca3bacec | Arlo |
| 2026-08-23 | FMT/Clippy/WASM/Release all PASS | ca3bacec | Arlo |

---

## NEXT ACTIONS

1. **Halborn engagement** — Sign audit engagement letter, confirm scope and timeline
2. **Grant repository access** — Provide Halborn team with read access to GitHub repo
3. **Deliver documentation package** — Share all 13 docs in `/docs/` with Halborn
4. **14-day soak test** — Continue monitoring (Day 6/14, 8 days remaining)
5. **Physical servers** — Order 3 validator servers (Hostkey NL, Hostkey USA, Hetzner FI)
6. **Key ceremony** — Schedule air-gapped key ceremony (21 validator keys + 5 multisig keys)
7. **Legal entity** — Initiate UAE/VARA legal entity formation

**No code changes until audit completion unless critical security fix identified by Halborn.**
