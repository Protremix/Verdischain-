# Key Emergency Procedure — Verdis Chain

**Document ID:** KEY-EMERGENCY
**Date:** 2026-08-14
**Status:** Specification (not yet executed)
**Approval Required:** Rojs Gordons + Council

---

## 1. Emergency Scenarios

| Scenario | Severity | Impact | Response Time |
|----------|----------|--------|---------------|
| Validator key compromise | SEV-0 | Block production risk | < 1 hour |
| Multisig key compromise (3+) | SEV-0 | Treasury at risk | < 1 hour |
| Theft of key storage site | SEV-1 | All keys at site compromised | < 4 hours |
| Custodian disappearance | SEV-2 | Key unavailable | < 24 hours |
| Catastrophic loss (fire/flood) | SEV-1 | Keys + backups destroyed | < 4 hours |
| Air-gapped machine seized | SEV-1 | Ceremony environment compromised | < 4 hours |
| Insider threat | SEV-0 | Malicious actor with key access | < 1 hour |

## 2. Immediate Actions (0-1 Hour)

### 2.1 Validator Key Compromise

1. **Isolate:** Remove compromised validator from active set
   - Council emergency session: `Dpos::deactivate_validator(compromised_address)`
   - If council unavailable: technical team pauses the validator node directly

2. **Verify Chain Health:**
   - Check block production continues with remaining validators
   - Verify finality (GRANDPA) is not stalled
   - Monitor for 6 blocks to confirm stability
   - If chain stalls: activate emergency consensus mode (reduce active validator count)

3. **Notify:**
   - Rojs Gordons (Founder) — phone + encrypted message
   - All council members — emergency channel
   - Key custodians — verify their keys are safe
   - Security auditor (if engaged) — for incident documentation

4. **Secure:**
   - Freeze all non-essential chain operations
   - Enable enhanced monitoring on all validator nodes
   - Begin logging all transactions from compromised address

### 2.2 Multisig Key Compromise

1. **Freeze Treasury:**
   - Council emergency resolution: pause all treasury spend authority
   - If runtime supports: emergency `PauseTreasury` extrinsic
   - If not: council votes to reject all treasury proposals until keys are replaced

2. **Verify:**
   - Check recent treasury transactions for unauthorized transfers
   - Audit all multisig proposals in the last 24 hours
   - Verify remaining multisig keys are intact

3. **Notify:**
   - Rojs Gordons — immediate
   - All multisig key custodians — verify key safety
   - Council — emergency session

## 3. Short-Term Actions (1-24 Hours)

### 3.1 Key Rotation

1. Convene emergency key ceremony (minimum: Rojs + 2 witnesses + key operator)
2. Air-gapped machine prepared in secure location
3. Generate replacement key(s)
4. Insert new session keys into validator node
5. Re-register validator with new public key
6. Verify chain is producing blocks with new key
7. Zeroize compromised key (if recovered)

### 3.2 Chain Stabilization

1. Verify all 21 validators are active and producing blocks
2. Check peer connectivity (minimum 15 peers)
3. Verify finality is working (GRANDPA)
4. Run health checks on all services
5. Monitor for 100 blocks to confirm stability
6. Publish incident report to community (if public chain)

### 3.3 Security Audit

1. Review all blocks produced by compromised validator
2. Check for: double-signing, invalid transactions, unauthorized transfers
3. If malicious activity found: slash compromised validator
4. Document all findings in incident report
5. Engage security auditor for independent review

## 4. Medium-Term Actions (1-7 Days)

### 4.1 Full Key Audit

1. Verify all 21 validator keys are intact and held by authorized custodians
2. Verify all 5 multisig keys are intact
3. Check all physical storage sites for tamper evidence
4. Review access logs for all storage locations
5. Interview all key custodians

### 4.2 Process Review

1. How was the compromise detected?
2. What was the root cause?
3. Were existing security procedures followed?
4. What procedures need to be updated?
5. Is additional training needed for custodians?
6. Should the key ceremony process be revised?

### 4.3 Remediation

1. Replace any compromised keys (validator + multisig)
2. Update key inventory with new hashes
3. Re-verify all key pairs (sign + verify test)
4. Update physical security at storage sites
5. Implement additional safeguards identified in review
6. Council approves updated key inventory

## 5. Communication Protocol

| Audience | When | Method | Content |
|----------|------|--------|---------|
| Rojs Gordons | Immediately | Phone + Signal | Full incident details |
| Council members | < 1 hour | Emergency channel | Incident summary + actions |
| Key custodians | < 1 hour | Phone | Verify key safety |
| Validator operators | < 2 hours | Encrypted channel | Instructions |
| Community (if public) | < 24 hours | Official announcement | Approved summary |
| Security auditor | < 24 hours | Email + report | Full incident report |
| Law enforcement | If criminal | Per legal counsel | Per counsel guidance |

## 6. Recovery to Operational State

An incident is considered resolved when:

- [ ] All compromised keys have been replaced
- [ ] All 21 validators are active and producing blocks
- [ ] All 5 multisig keys are verified
- [ ] Treasury is operational (if was frozen)
- [ ] Chain has been stable for 100+ blocks
- [ ] No unauthorized transactions remain unexplained
- [ ] Key inventory is updated and signed off
- [ ] Incident report is completed
- [ ] Post-mortem review is conducted
- [ ] Council formally resolves the incident
- [ ] Rojs signs off on recovery

## 7. Emergency Contacts

| Role | Name | Contact | Backup |
|------|------|---------|--------|
| Founder | Rojs Gordons | <TBD> | <TBD> |
| Security Lead | <TBD> | <TBD> | <TBD> |
| Council Chair | <TBD> | <TBD> | <TBD> |
| Key Custodian 1 | <TBD> | <TBD> | <TBD> |
| Key Custodian 2 | <TBD> | <TBD> | <TBD> |
| Legal Counsel | <TBD> | <TBD> | <TBD> |
| Security Auditor | <TBD> | <TBD> | <TBD> |

## 8. Post-Incident Review

Within 7 days of incident resolution:

1. Full timeline reconstruction
2. Root cause analysis
3. Detection time assessment (how quickly was it detected?)
4. Response time assessment (how quickly was it contained?)
5. Effectiveness of existing procedures
6. Recommended changes to procedures
7. Council review and approval of changes
8. Implementation of changes
9. Follow-up test of new procedures
10. Final report published (internal)
