# VerdisChain Go-Live Gate

## Purpose

This document defines the mandatory evidence gates for VerdisChain mainnet launch.

A gate is considered closed only when the required evidence exists and has been reviewed by the responsible owner.

## P0 — Legal and Regulatory

- [ ] UAE / VARA legal review completed.
- [ ] VRDX issuance classification completed by qualified counsel.
- [ ] EU / MiCA analysis completed by qualified counsel.
- [ ] Global jurisdiction policy approved.
- [ ] Offering entity legally formed.
- [ ] Entity separation and control structure documented.
- [ ] Token offering is disabled until legal approval is obtained.

## P0 — Independent Security

- [ ] Independent security auditor selected.
- [ ] Audit scope approved.
- [ ] Security audit completed against the exact release candidate.
- [ ] All Critical findings closed.
- [ ] All High findings closed or formally accepted by the security authority.
- [ ] Required remediation has been re-tested.
- [ ] Final audit report archived.

## P0 — Production Keys

- [ ] Key ceremony specification approved.
- [ ] 21 validator custodians appointed.
- [ ] 5 multisig custodians appointed.
- [ ] Production keys generated only in the approved air-gapped environment.
- [ ] Public-key/address mapping independently verified.
- [ ] Recovery procedure tested.
- [ ] Ceremony evidence signed and archived.

## P0 — Genesis and Protocol

- [ ] Mainnet chain identity is finalized.
- [ ] Genesis configuration is independently reviewed.
- [ ] Validator configuration is verified.
- [ ] Runtime configuration matches the intended mainnet configuration.
- [ ] Token allocation and supply are verified.
- [ ] Consensus configuration is verified.
- [ ] Runtime upgrade authority is documented.
- [ ] Governance permissions are documented.
- [ ] No placeholder production credentials remain.

## P0 — Tokenomics

- [ ] Canonical token supply is defined.
- [ ] Genesis allocation matches canonical tokenomics.
- [ ] Runtime balances match canonical tokenomics.
- [ ] Documentation matches canonical tokenomics.
- [ ] Website/public materials match canonical tokenomics.
- [ ] Any discrepancy blocks launch until resolved.

## P0 — Infrastructure

- [ ] Production node configuration reviewed.
- [ ] RPC exposure reviewed.
- [ ] P2P configuration reviewed.
- [ ] Secrets are outside source control.
- [ ] CI/CD release process reviewed.
- [ ] Backup and disaster-recovery procedure tested.
- [ ] Monitoring and alerting tested.
- [ ] Incident-response procedure tested.

## P1 — Compliance

- [ ] KYC/KYB provider selected where legally required.
- [ ] Sanctions/PEP screening implemented where required.
- [ ] Jurisdiction restrictions implemented.
- [ ] Compliance ownership appointed.
- [ ] Required records and audit evidence are retained.

## P1 — Marketing

- [ ] Public claims have supporting evidence.
- [ ] Regulatory claims have legal approval.
- [ ] No unsupported statement describes the network as licensed, approved, audited or compliant.
- [ ] Token-sale materials are consistent with the approved legal structure.

## Final Authorization

The following sign-offs are required before production launch:

- [ ] Technical lead
- [ ] Security lead
- [ ] Legal counsel
- [ ] Compliance owner
- [ ] Executive / Rojs

## Hard Stop Rule

If any unresolved P0 gate remains open, mainnet launch must not be authorized.

If legal classification, regulatory authorization, or required external review is incomplete, the relevant activity must remain disabled.

## Evidence

Each closed gate must reference verifiable evidence.

Examples:

- commit/tag;
- test result;
- configuration hash;
- signed legal opinion;
- audit report;
- executed agreement;
- ceremony report;
- provider contract;
- formal approval.

## Sensitive Material

Never commit the following to this repository:

- private keys;
- seed phrases;
- passwords;
- API tokens;
- production credentials;
- KYC/PII;
- multisig secrets.

This document contains process requirements only and does not constitute legal, regulatory or security certification.
