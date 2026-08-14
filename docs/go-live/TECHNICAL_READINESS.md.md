# VerdisChain Technical Readiness

## Purpose

This document defines the technical evidence required before VerdisChain mainnet launch.

It is a verification checklist, not a statement that any item has already been completed.

## 1. Build and Release

- [ ] Mainnet release commit/tag is explicitly identified.
- [ ] Release build is reproducible or the build process is documented and independently verified.
- [ ] Production binaries are built from the reviewed source revision.
- [ ] Dependency versions are pinned or otherwise controlled.
- [ ] Release artifacts are integrity-verified.
- [ ] No development-only configuration is enabled in the production release.

## 2. Genesis and Chain Identity

- [ ] Mainnet chain ID is finalized.
- [ ] Protocol ID is finalized.
- [ ] Genesis configuration is reviewed.
- [ ] Genesis hash is recorded.
- [ ] Runtime version is recorded.
- [ ] Genesis authorities are independently verified.
- [ ] Initial balances and allocations are independently verified.
- [ ] No placeholder production authorities remain in the final release.
- [ ] Chain-spec configuration matches the approved mainnet specification.

## 3. Validator Set

- [ ] Intended validator count is documented.
- [ ] Runtime validator-count configuration matches the approved design.
- [ ] Genesis validator configuration is verified.
- [ ] Validator public keys are independently checked.
- [ ] Validator identities are mapped to the approved operator register.
- [ ] Validator onboarding procedure is documented.
- [ ] Validator removal/replacement procedure is documented.
- [ ] Validator key recovery procedure is documented.
- [ ] No private validator keys are stored in source control.

## 4. Consensus and Staking

- [ ] Consensus configuration has been reviewed.
- [ ] Validator selection logic has been reviewed.
- [ ] Staking configuration has been reviewed.
- [ ] Reward calculation has been reviewed.
- [ ] Slashing conditions have been reviewed.
- [ ] Unbonding/withdrawal logic has been reviewed.
- [ ] Edge cases have automated tests.
- [ ] Failure scenarios have been tested.
- [ ] Consensus safety and liveness assumptions are documented.

## 5. Runtime and Governance

- [ ] Runtime version is recorded for the release candidate.
- [ ] Runtime upgrade mechanism is documented.
- [ ] Upgrade authority is explicitly identified.
- [ ] Privileged origins are inventoried.
- [ ] Emergency powers are inventoried.
- [ ] Governance permissions are documented.
- [ ] Unauthorized privileged operations have tests.
- [ ] Migration procedures are documented where applicable.

## 6. Custom Pallets

For every custom pallet:

- [ ] Access control reviewed.
- [ ] State transitions reviewed.
- [ ] Arithmetic reviewed.
- [ ] Overflow/underflow protections reviewed.
- [ ] Input validation reviewed.
- [ ] Events reviewed.
- [ ] Errors reviewed.
- [ ] Storage migrations reviewed.
- [ ] Property/invariant tests exist where appropriate.
- [ ] Security-sensitive functions have negative tests.

## 7. DEX and Economic Safety

- [ ] Swap mathematics reviewed.
- [ ] Liquidity accounting reviewed.
- [ ] Fee accounting reviewed.
- [ ] Slippage protections reviewed.
- [ ] Price manipulation scenarios tested.
- [ ] Integer precision/rounding reviewed.
- [ ] Minimum/maximum bounds reviewed.
- [ ] Unauthorized pool operations tested.
- [ ] Economic attack scenarios documented.
- [ ] Independent security review completed before production use.

## 8. Wallet and Transaction Security

- [ ] Transaction signing flow reviewed.
- [ ] Nonce handling reviewed.
- [ ] Replay protection reviewed.
- [ ] Signature validation reviewed.
- [ ] Transaction encoding/decoding reviewed.
- [ ] RPC transaction submission reviewed.
- [ ] Wallet error handling reviewed.
- [ ] Production credentials are outside source control.

## 9. Networking and RPC

- [ ] P2P configuration reviewed.
- [ ] Peer discovery configuration reviewed.
- [ ] RPC exposure reviewed.
- [ ] Public RPC methods inventoried.
- [ ] Administrative RPC methods protected.
- [ ] Rate limiting is documented where applicable.
- [ ] Network abuse scenarios tested.
- [ ] Production firewall/network policy documented.

## 10. Infrastructure and Secrets

- [ ] Production infrastructure is documented.
- [ ] Secrets are stored outside source control.
- [ ] CI/CD secrets are protected.
- [ ] Production credentials are separated from development credentials.
- [ ] Access control is documented.
- [ ] Logging does not expose secrets.
- [ ] Backup procedures are documented.
- [ ] Disaster recovery has been tested.
- [ ] Incident response has been tested.

## 11. Testing

- [ ] Unit tests pass.
- [ ] Integration tests pass.
- [ ] Runtime tests pass.
- [ ] Consensus tests pass.
- [ ] Staking tests pass.
- [ ] DEX tests pass.
- [ ] End-to-end tests pass.
- [ ] Multi-node tests pass.
- [ ] Failure/chaos scenarios are tested where appropriate.
- [ ] Fuzz/property testing is performed where appropriate.
- [ ] Test results are tied to the release candidate.

## 12. Security Audit

- [ ] Independent auditor selected.
- [ ] Scope approved.
- [ ] Auditor received the exact release candidate.
- [ ] Audit completed.
- [ ] Critical findings = 0.
- [ ] High findings are closed or formally accepted by the authorized security authority.
- [ ] Required remediation has been re-tested.
- [ ] Final audit report is archived.

## 13. Protremix Independence

- [ ] Critical dependencies on Protremix are inventoried.
- [ ] Administrative/control dependencies are documented.
- [ ] Code ownership is documented.
- [ ] Infrastructure ownership is documented.
- [ ] Key custody is independent of a single development organization.
- [ ] Operational procedures can continue if Protremix becomes unavailable.
- [ ] A controlled independence/failure test has been completed.
- [ ] Evidence of the test is archived.

## 14. Monitoring and Incident Response

- [ ] Node health monitoring is active.
- [ ] Validator monitoring is active.
- [ ] Consensus failure alerts are active.
- [ ] RPC/infrastructure alerts are active.
- [ ] Security incident escalation path is documented.
- [ ] Emergency contacts are documented.
- [ ] Incident response exercise completed.

## 15. Evidence Standard

Every completed item must reference verifiable evidence.

Acceptable evidence includes:

- source commit;
- release tag;
- automated test result;
- configuration;
- hash;
- signed audit report;
- incident-response exercise;
- recovery test;
- formal approval.

A checkbox must not be marked complete merely because a document claims that the requirement is satisfied.

## 16. Sensitive Material

Never commit:

- private keys;
- seed phrases;
- passwords;
- API tokens;
- production credentials;
- KYC/PII;
- multisig secrets;
- validator private keys.

Production key generation must occur through the approved air-gapped key ceremony.

## Final Rule

Technical readiness is not equivalent to legal, regulatory or security approval.

Mainnet launch remains blocked until all applicable P0 gates in `GO_LIVE_GATE.md` are closed.
