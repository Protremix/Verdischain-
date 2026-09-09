# Verdis Chain Incident Response Plan (ARCH-053)

**Status:** Draft — must be tested via tabletop exercise before mainnet

---

## 1. Scope

This plan covers security incidents, consensus failures, infrastructure outages, and key compromise scenarios for the Verdis Chain network.

## 2. Incident Severity Levels

| Level | Description | Response Time | Examples |
|-------|------------|---------------|----------|
| SEV-0 | Critical — funds at risk or consensus halted | Immediate (< 15 min) | Validator key compromise, consensus halt, DEX exploit |
| SEV-1 | High — service degradation or security breach | < 1 hour | Node outage, RPC DDoS, partial key compromise |
| SEV-2 | Medium — limited impact, workaround exists | < 4 hours | Single validator offline, monitoring failure |
| SEV-3 | Low — cosmetic or non-urgent | < 24 hours | Display bug, stale documentation |

## 3. Response Team

| Role | Responsibility | Current Owner |
|------|---------------|---------------|
| Incident Commander | Coordinate response, make go/no-go decisions | Rojs Gordons |
| Protocol Lead | Technical assessment, runtime fixes | Architecture lead |
| Infrastructure Lead | Server/network operations | DevOps |
| Communications | Public statements, community updates | TBD |
| Legal | Regulatory notification, compliance | TBD (needs counsel) |

## 4. Response Procedures

### 4.1 Validator Key Compromise (SEV-0)
1. Immediately slash the compromised validator via governance motion
2. Remove validator from active set via session key rotation
3. Investigate scope: check all transactions signed by compromised key
4. If multisig key compromised: require emergency 3-of-5 vote to rotate
5. Post-mortem: document timeline, root cause, prevention measures

### 4.2 Consensus Halt (SEV-0)
1. Verify halt: check all nodes stopped producing blocks
2. Identify cause: runtime panic, insufficient validators, network partition
3. If runtime panic: prepare emergency runtime upgrade with fix
4. If insufficient validators: activate standby validators
5. Communicate to community: status page, Discord/Telegram
6. Resume: coordinated restart with all validators

### 4.3 DEX Exploit (SEV-0)
1. Immediately pause DEX via governance (if pause mechanism exists) or emergency runtime upgrade
2. Identify exploited vulnerability: flash loan, overflow, price manipulation
3. Assess fund impact: check all affected pools
4. If funds stolen: track destination addresses, attempt recovery via governance
5. Patch: fix vulnerability in pallet-amm-dex
6. Post-mortem: document exploit, fix, prevention measures

### 4.4 Infrastructure Outage (SEV-1)
1. Check server status: CPU, memory, disk, network
2. Identify failed service: node, RPC, nginx, tx-relay
3. Restart failed service: systemctl restart
4. If hardware failure: failover to backup server
5. Verify recovery: check block production, RPC responses, web pages

### 4.5 Website Defacement (SEV-2)
1. Take affected page offline immediately
2. Restore from known-good backup (git HEAD)
3. Check for unauthorized access: SSH logs, nginx logs
4. Rotate any compromised credentials
5. Verify all other pages are intact

## 5. Communication Plan

| Audience | Channel | SEV-0 | SEV-1 | SEV-2 |
|----------|---------|-------|-------|-------|
| Internal team | Direct message | Immediate | < 1h | < 4h |
| Validators | Private channel | < 30 min | < 2h | N/A |
| Community | Status page + social | < 1h | < 4h | < 24h |
| Public/Legal | Official statement | < 24h | < 48h | N/A |

## 6. Post-Incident Requirements

1. Post-mortem document within 72 hours
2. Root cause analysis with timeline
3. Prevention measures implemented
4. Test plan for prevention measures
5. Update this document with lessons learned

## 7. Pre-Mainnet Testing

- [ ] Tabletop exercise: validator key compromise scenario
- [ ] Tabletop exercise: consensus halt scenario
- [ ] Technical exercise: server failover (restore from backup)
- [ ] Technical exercise: emergency runtime upgrade deployment
- [ ] Communication test: status page update within 30 minutes
