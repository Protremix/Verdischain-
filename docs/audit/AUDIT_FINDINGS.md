## Findings

| ID | Area | Severity | Finding | Status |
|---|---|---|---|---|
| AUDIT-001 | Consensus / Validators | CRITICAL | Runtime ActiveValidatorCount is 21, while mainnet SessionConfig provisions only the first 6 session keys. DPoS genesis and epoch rotation use the runtime active count. This creates a consensus-readiness mismatch that must be resolved and tested before mainnet. | OPEN — P0 |
| AUDIT-002 | Production Keys | CRITICAL | Mainnet validator identities currently use deterministic placeholder URIs `//MAINNET_VALIDATOR_1` through `//MAINNET_VALIDATOR_21`. These must be replaced by production keys generated through the approved air-gapped ceremony. | OPEN — P0 |
| AUDIT-003 | Tokenomics Genesis | HIGH | Mainnet genesis initializes the tokenomics pallet with `Default::default()` although the pallet has explicit genesis fields for supply, circulating supply, investor allocation, distribution and presale price. Generated mainnet state must be reconciled before any sale functionality is enabled. | OPEN — P0 |
| AUDIT-004 | Tokenomics Consistency | MEDIUM | Canonical facts state a 12B total investor allocation while runtime InvestorAllocationConst is 5B. The intended meaning and limits must be reconciled before any offering. | OPEN |
| AUDIT-005 | Mainnet Identity | MEDIUM | Mainnet chain ID is currently `verdis`; the existing audit report identifies `verdis-mainnet` as the intended final ID. The final chain identity must be frozen before genesis publication. | OPEN |
| AUDIT-006 | Independent Security | CRITICAL | No independent external security audit has been completed. Internal/AI-assisted review is not a substitute for the required independent audit. | OPEN — P0 |
