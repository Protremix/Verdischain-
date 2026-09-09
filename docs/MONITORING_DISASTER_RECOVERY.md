# Independent Monitoring and Disaster Recovery (ARCH-055/056)

Status: Draft - must be tested before mainnet

## 1. Independent Monitoring Stack (ARCH-055)

Principle: Protocol availability must not depend on a single operator dashboard.

Current State:
- Prometheus + Grafana on server (localhost-only)
- Node metrics via substrate Prometheus endpoint
- No public monitoring dashboard

Target Architecture:
- Multiple independent Prometheus instances
- Public status page (verdischain.com/status/) - DONE
- Alertmanager to Telegram/email
- External uptime checker (UptimeRobot or similar)

Minimum Monitoring Metrics:
1. Block height and production rate
2. Peer count
3. Active validator count
4. Transaction throughput (TPS)
5. DEX pool reserves
6. Treasury balance
7. Node CPU / memory / disk
8. RPC response time

## 2. Disaster Recovery Testing (ARCH-056)

Test Scenarios:
1. Single node failure - Kill one node, verify chain continues
2. All nodes failure - Kill all nodes, restart, verify chain resumes
3. Database corruption - Corrupt chain DB, restore from backup
4. Server failure - Power off, boot from backup
5. Network partition - Firewall between nodes, verify partition heals
6. Validator key loss - Rotate via governance
7. Runtime upgrade failure - Emergency rollback to previous WASM

Backup Strategy:
- Chain database: rsync to backup server, daily, 7 day retention
- Web files: Git (GitHub), continuous, permanent
- Validator keys: Air-gapped backup, at ceremony, permanent
- Nginx config: Git + server backup, on change, permanent

Recovery Time Objectives:
- Chain (single node): RTO 5 min, RPO 0 blocks
- Chain (all nodes): RTO 30 min, RPO 0 blocks
- Website: RTO 5 min, RPO 0 (git HEAD)
- TX Relay: RTO 5 min, RPO 0 (stateless)
- API: RTO 5 min, RPO 0 (stateless)

Pre-Mainnet Testing Plan:
1. Kill node1, verify chain continues, restart, verify sync
2. Kill all nodes, restart, verify chain resumes
3. Restore web files from git, verify all pages 200
4. Simulate runtime upgrade failure, verify rollback
5. Document all test results in disaster recovery report
