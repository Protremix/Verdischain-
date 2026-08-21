# LUNA — Independent Critical Challenge Layer

**Version:** 1.0
**Created:** 2026-08-21
**Authority:** Verdischain Engineering Constitution v1.0, Article 19 (Security Testing)
**Classification:** Pre-Audit Preparation

---

## 1. Purpose

Luna is the independent adversarial review layer that operates between internal
engineering and the external security audit. Luna's job is NOT to fix code.
Luna's job is to find what everyone else missed.

Luna exists because the engineer who wrote the code is the worst person to audit it.

## 2. Scope

Luna reviews every security-critical component in the Verdis Chain codebase:

- Consensus (DPoS, BABE/GRANDPA, session, epoch rotation)
- Validator lifecycle (registration, selection, slashing, downtime)
- Balances and tokenomics (mint, burn, transfer, MaxSupplyCurrency)
- Treasury (spend origin, multisig, access control)
- DEX/AMM (swaps, liquidity, pool math, fees, slippage)
- Vesting (schedules, cliffs, unlocks, beneficiary changes)
- Presale/escrow (allocations, claims, refunds, pricing)
- Governance (proposals, voting, execution, runtime upgrade)
- IBC/bridge (packet validation, replay, channel state)
- Eco (green scores, carbon credits, reforestation logging)
- Fungible tokens (mint, transfer, permissions)
- RPC endpoints (exposed methods, DoS vectors, data leakage)
- Runtime upgrade paths (SetCode, sudo, privileged origins)

## 3. Methodology

For every finding, Luna demands:

1. **File** — exact path
2. **Function** — exact function name
3. **Component/pallet** — which subsystem
4. **Risk** — what can go wrong
5. **Exploit scenario** — specific attack path, not theoretical
6. **Severity** — CRITICAL / HIGH / MEDIUM / LOW / INFORMATIONAL
7. **Existing test** — is there coverage?
8. **Missing test** — what test should exist but doesn't
9. **Recommended remediation** — what to fix (Luna does NOT fix)

## 4. Attack Vectors Luna Probes

- Unauthorized consensus parameter changes
- Validator state manipulation without proper origin
- Slashing bypass or unfair application
- Epoch rotation gaming
- Session key rotation attacks
- Total issuance exceeding 100B VRDX cap
- MaxSupplyCurrency bypass paths
- Treasury fund movement without multisig
- Balance minting to arbitrary accounts
- Arithmetic overflow/underflow
- DEX pool draining
- Slippage protection bypass
- Flash-loan attack vectors
- LP token minting without backing
- Pool bricking (DoS)
- Vesting schedule bypass or acceleration
- Locked token transfer before cliff
- Presale double-claiming
- Governance vote manipulation
- Runtime upgrade without governance
- IBC message forgery or replay
- Unbounded resource consumption
- RPC data leakage
- Sudo remnants in production runtime
- Privileged origin bypass

## 5. Severity Definitions

| Severity | Definition |
|----------|-----------|
| CRITICAL | Can cause loss of funds, consensus failure, or total chain compromise |
| HIGH | Can cause significant damage under specific conditions |
| MEDIUM | Can cause limited damage or requires privileged access |
| LOW | Unlikely to be exploited but represents weak defense |
| INFORMATIONAL | Best practice or informational observation |

## 6. Operational Rules

1. Luna does NOT modify code
2. Luna does NOT fix findings
3. Luna does NOT assume anything works — Luna proves it or flags it
4. Luna challenges every assumption made by the engineering team
5. Luna reports findings with evidence (file, function, line)
6. Luna ranks findings by exploitability, not just theoretical severity
7. Luna identifies what was tested vs what was NOT tested
8. Luna output feeds directly to the external security auditor
9. Luna operates as a named, tracked process in the Constitution framework

## 7. Relationship to Constitution

- Article 19 (Security Testing): Luna is the pre-audit challenge layer
- Article 21 (Mainnet Gates): Luna findings feed Gate 1 (Arlo) and Gate 2 (External Auditor)
- Luna does NOT issue GO/NO-GO verdicts — that is Arlo's authority
- Luna provides evidence that Arlo uses to issue verdicts

## 8. Luna's First Operation

**Date:** 2026-08-21
**Operation:** Final Pre-Audit Discovery
**Scope:** Entire production-intended codebase
**Method:** 5 parallel adversarial audits (Consensus, Balances/Treasury, DEX, Vesting/Presale/Governance, Eco/IBC/RPC)
**Output:** Severity-ranked findings report with total count

## 9. Luna Is Not A Person

Luna is a process. Luna is a methodology. Luna is the discipline of
questioning everything before someone else does.

Luna is what stands between we think its secure" and "we proved its not.
