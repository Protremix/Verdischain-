# Mainnet Launch Gate (ARCH-075)

**Status:** Formal launch gate — no mainnet without all gates closed

---

## 1. Hard Blockers (ALL must be resolved)

| # | Blocker | Current Status | Required Evidence |
|---|---------|---------------|-------------------|
| 1 | Dubai/UAE legal and VARA path unresolved | OPEN | Signed UAE/VARA legal memo |
| 2 | VRDX EU/MiCA classification unresolved | OPEN | Signed VRDX classification opinion |
| 3 | Global jurisdiction policy unresolved | OPEN | Versioned allow/restrict/block policy |
| 4 | Independent security audit not completed | OPEN | Third-party audit report, 0 critical findings |
| 5 | Critical security findings open | OPEN | 0 critical, 0 high findings |
| 6 | Genesis/runtime/consensus inconsistencies | PARTIALLY RESOLVED | CI checks pass, genesis determinism verified |
| 7 | Tokenomics inconsistent across code/docs | RESOLVED | CI consistency check passes (scripts/check_genesis_consistency.py) |
| 8 | Company-controlled stake concentration exceeds policy | OPEN | On-chain evidence: Protremix + Foundation <= 33% |
| 9 | Disaster recovery not exercised | OPEN | DR test report |
| 10 | Public status/evidence documentation inaccurate | RESOLVED | Status page live, claims register verified |
| 11 | Executive/legal/security/technical sign-off missing | OPEN | 4-way sign-off below |

---

## 2. Evidence Checklist

### Legal & Regulatory
- [ ] UAE/VARA legal memo signed by counsel
- [ ] EU/MiCA VRDX classification opinion signed by counsel
- [ ] Global jurisdiction policy versioned and approved
- [ ] Offering entity legally established
- [ ] KYC/AML provider contracted
- [ ] Sale compliance architecture tested
- [ ] Whitepaper legally reviewed

### Security
- [ ] Independent security audit completed
- [ ] 0 critical findings
- [ ] 0 high findings
- [ ] Penetration test completed
- [ ] Wallet security review completed
- [ ] All P0 remediation tasks closed

### Technical
- [ ] 21+ independent validators operational
- [ ] Genesis determinism verified (same hash across all nodes)
- [ ] Air-gapped key ceremony completed
- [ ] 3-of-5 treasury multisig keys generated and imported
- [ ] pallet_sudo removed (DONE)
- [ ] CI/CD release gates passing (7 gates)
- [ ] Tokenomics consistency CI passing (DONE)
- [ ] Supply invariant tests passing (38 tests — DONE)
- [ ] Vesting edge case tests passing (59 tests — DONE)
- [ ] DEX security regression tests passing (PENDING)
- [ ] DPoS consensus tests passing (76 tests — DONE)
- [ ] Runtime upgrade tested with try-runtime
- [ ] Slashing and recovery tested
- [ ] Validator onboarding/offboarding tested
- [ ] Chain spec frozen and signed

### Decentralization
- [ ] Protremix + Foundation combined stake <= 33%
- [ ] Nakamoto coefficient >= 7
- [ ] Geographic diversity (3+ countries, 3+ ASNs)
- [ ] No single operator > 33% of validators
- [ ] Top-10 stake concentration < 50%
- [ ] Protremix Independence Test passed

### Operations
- [ ] Incident response plan tested (tabletop exercise)
- [ ] Disaster recovery tested (node failure, data corruption, server failure)
- [ ] Monitoring dashboard public
- [ ] Backup strategy tested
- [ ] Recovery time objectives met

### Transparency
- [ ] Status page live (DONE: verdischain.com/status/)
- [ ] Claims register published (DONE: docs/CLAIMS_REGISTER.md)
- [ ] Tokenomics consistency CI passing (DONE)
- [ ] Validator roadmap published (DONE: docs/VALIDATOR_ROADMAP.md)
- [ ] Bug bounty program published (DONE: docs/BUG_BOUNTY_PROGRAM.md)
- [ ] Threat model published (DONE: docs/TX_RELAY_THREAT_MODEL.md)
- [ ] Incident response plan published (DONE: docs/INCIDENT_RESPONSE_PLAN.md)

---

## 3. Sign-Off Matrix

| Gate | Signatory | Requirement | Status |
|------|----------|-------------|--------|
| Legal | Rojs Gordons + External Counsel | All legal/regulatory gates closed | PENDING |
| Security | Independent Audit Firm | Audit report with 0 critical/high findings | PENDING |
| Technical | Architecture Lead | All technical gates closed, tests passing | PARTIAL (tests in progress) |
| Executive | Rojs Gordons | Final launch authorization | PENDING |

**NO MAINNET LAUNCH WITHOUT ALL FOUR SIGN-OFFS**

---

## 4. Launch Procedure

### Phase 1: Final Preparation (after all gates closed)
1. Freeze genesis spec (git tag mainnet-genesis)
2. Run air-gapped key ceremony (21 validators + 5 multisig)
3. Import keys to chain spec
4. Verify genesis determinism (same hash on 3+ independent machines)
5. Deploy to 21 independent validator nodes
6. Verify block production and consensus

### Phase 2: Launch Day
1. All 21 validators start simultaneously
2. Verify first 100 blocks produced
3. Verify finality (GRANDPA)
4. Verify all pallets functional (DEX, staking, vesting, governance)
5. Update status page to "MAINNET LIVE"
6. Publish genesis hash and block 0 hash

### Phase 3: Post-Launch (first 24 hours)
1. Monitor block production continuously
2. Monitor peer connections
3. Monitor validator participation
4. No runtime changes for first 7 days
5. Daily status reports for first 7 days
6. Weekly status reports for first 30 days

---

## 5. Abort Conditions

If ANY of the following occur during launch, ABORT and revert to testnet:

- Any validator produces invalid blocks
- Consensus fails to finalize within 10 minutes
- Any pallet produces unexpected errors
- Genesis hash differs across nodes
- Treasury or tokenomics invariants violated
- Any critical security vulnerability discovered

---

## 6. Decision Record

| Decision | By | Date | Notes |
|----------|-----|------|-------|
| Approve launch gate framework | Rojs | 2026-08-14 | APPROVED |
| Approve entity separation (ARCH-001) | Rojs | 2026-08-14 | APPROVED |
| Authorize UAE/VARA legal (ARCH-002) | Rojs | 2026-08-14 | APPROVED |
| Authorize EU/MiCA classification (ARCH-003) | Rojs | 2026-08-14 | APPROVED |
| Approve global jurisdiction policy (ARCH-004) | Rojs | 2026-08-14 | APPROVED |
| Approve Protremix Independence Test (ARCH-005) | Rojs | 2026-08-14 | APPROVED |
| Approve token offering compliance (ARCH-007) | Rojs | 2026-08-14 | APPROVED |
| Approve independent security audit (ARCH-008) | Rojs | 2026-08-14 | APPROVED - budget + firm TBD |
| Approve mainnet launch gate (ARCH-075) | Rojs | 2026-08-14 | APPROVED |
| Sale disabled until legal approval | Rojs | 2026-08-14 | bash raised confirmed |
| Treasury 3-of-5 multisig | Rojs | 2026-08-14 | 5 air-gapped keys |
| Token symbol VRDX (not VERDIS) | Rojs | 2026-08-08 | Override of hardening task |
