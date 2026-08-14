# VerdisChain Audit Findings

## Purpose

This document records findings produced during the VerdisChain technical audit.

Only findings supported by repository evidence should be recorded as confirmed findings.

## Severity Definitions

- **Critical** — a confirmed issue that can cause catastrophic loss of funds, compromise of critical control, or prevent safe operation.
- **High** — a confirmed issue with significant security, integrity, availability, or economic impact.
- **Medium** — a confirmed issue with material but more limited impact.
- **Low** — a confirmed issue with limited impact or hardening value.
- **Informational** — an observation or improvement that is not a security vulnerability.

Severity must be assigned only after reviewing the actual evidence and impact.

## Findings

| ID | Area | Severity | Finding | Evidence | Status |
|---|---|---|---|---|---|
| AUDIT-001 | Genesis | TBD | Genesis configuration requires verification against the approved mainnet specification. | To be established from repository evidence. | Open |
| AUDIT-002 | Tokenomics | TBD | Token supply and allocation require verification against the canonical tokenomics specification. | To be established from repository evidence. | Open |
| AUDIT-003 | Validators | TBD | Validator configuration requires verification against the approved validator set and runtime configuration. | To be established from repository evidence. | Open |
| AUDIT-004 | Runtime | TBD | Privileged origins and administrative control paths require review. | To be established from repository evidence. | Open |

## Evidence Rules

Every confirmed finding must include:

1. Exact repository path.
2. Relevant line number or code section where practical.
3. Commit or branch containing the evidence.
4. Description of the observed behavior.
5. Security or operational impact.
6. Reproduction or verification procedure where applicable.
7. Recommended remediation.
8. Validation status after remediation.

## Status Definitions

- **Open** — evidence supports the finding and remediation is outstanding.
- **In Progress** — remediation has started.
- **Resolved** — remediation has been implemented and verified.
- **Accepted Risk** — an authorized decision-maker has formally accepted the residual risk.
- **False Positive** — subsequent evidence disproved the finding.

## Audit Discipline

Do not classify a condition as a vulnerability merely because it is undocumented.

Do not claim that a component is secure merely because no
