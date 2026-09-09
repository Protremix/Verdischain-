# Verdis Chain — Production Infrastructure Checklist

## Status: PREPARATION — Not mainnet-ready

This checklist defines the infrastructure requirements for mainnet launch.

---

## 1. Validator Infrastructure (21 validators)

### Minimum Hardware (per validator)
- [ ] 4 CPU cores (dedicated, not shared)
- [ ] 16 GB RAM
- [ ] 500 GB NVMe SSD (grows over time)
- [ ] 1 Gbps network connection
- [ ] UPS battery backup (minimum 30 min runtime)
- [ ] Static public IP address

### Security
- [ ] HSM or YubiKey for key custody
- [ ] Dedicated machine (no other services)
- [ ] Firewall: only P2P (30333) and SSH (22, key-only) open
- [ ] SSH: key-only authentication, no root login
- [ ] Fail2ban or equivalent SSH protection
- [ ] Automated security updates (unattended-upgrades)
- [ ] No RPC exposed to public (or behind reverse proxy with rate limiting)

### Software
- [ ] Ubuntu 22.04 LTS or 24.04 LTS
- [ ] Verdis node binary (release build, deterministic)
- [ ] systemd service with auto-restart
- [ ] Log rotation configured
- [ ] Time sync (chrony/ntp)

### Monitoring
- [ ] Node exporter installed
- [ ] Prometheus scraping enabled
- [ ] Alert: node down > 5 min
- [ ] Alert: peer count < 3
- [ ] Alert: block production stalled
- [ ] Alert: disk usage > 80%
- [ ] Alert: CPU usage > 90% sustained

---

## 2. Bootnodes (minimum 2)

- [ ] 2 bootnodes on different cloud providers / regions
- [ ] Static, publicly known IP addresses
- [ ] DNS: `bootnode1.verdischain.com`, `bootnode2.verdischain.com`
- [ ] High availability (auto-restart, health checks)
- [ ] DDoS protection (Cloudflare or equivalent)
- [ ] NOT validators (relay only)

---

## 3. RPC Infrastructure

### Public RPC (rate-limited)
- [ ] Load balancer (HAProxy/nginx) in front of 2+ RPC nodes
- [ ] Rate limiting: 10 req/s per IP, 100 req/min
- [ ] CORS: only verdischain.com, evolvixos.com
- [ ] TLS (Let's Encrypt)
- [ ] RPC methods: Safe (no unsafe methods exposed)
- [ ] DDoS protection

### Archive Nodes
- [ ] 1 archive node for historical queries (full state)
- [ ] 1 backup archive node
- [ ] Backup schedule (daily snapshots)

---

## 4. Web Infrastructure

### Current (verdischain.com)
- [ ] nginx: keep security headers (CSP, HSTS, Permissions-Policy)
- [ ] nginx: keep rate limiting (faucet/sale/wallet 5r/s)
- [ ] nginx: keep HTTP method restrictions (no PUT/DELETE/TRACE)
- [ ] TLS: auto-renewal configured (Let's Encrypt)
- [ ] Backup: daily web file backup
- [ ] Monitoring: uptime check every 60s

### Current (evolvixos.com)
- [ ] Same security headers as verdischain.com
- [ ] TLS configured
- [ ] Monitoring enabled

---

## 5. Monitoring & Alerting

### Prometheus + Grafana
- [ ] Prometheus scraping all nodes (node_exporter)
- [ ] Prometheus scraping chain metrics (if exposed)
- [ ] Grafana dashboards:
  - [ ] Block height and production rate
  - [ ] Peer count per node
  - [ ] Validator participation
  - [ ] Transaction throughput (TPS)
  - [ ] Memory/CPU/Disk per node
  - [ ] Network latency
- [ ] Alerting rules configured (Slack/email/PagerDuty)

### Chain-specific Alerts
- [ ] Finality lag > 30 seconds
- [ ] Validator not producing blocks
- [ ] Validator equivocation detected
- [ ] Unusually high transaction volume
- [ ] DEX anomaly (large swaps, price manipulation)
- [ ] Governance proposal submitted
- [ ] Treasury spend proposed

---

## 6. TX Relay & API

- [ ] TX Relay v3 deployed behind nginx
- [ ] API key authentication for sensitive endpoints
- [ ] Rate limiting (per-key and per-IP)
- [ ] Health check endpoint
- [ ] Monitoring and alerting
- [ ] Backup TX relay instance

---

## 7. Backup & Recovery

### Chain Data
- [ ] Daily chain DB snapshot (at least 2 nodes)
- [ ] Off-site backup of chain spec
- [ ] Genesis file backed up in 3 locations

### Web Data
- [ ] Daily backup of all web files
- [ ] Database backup (if applicable)
- [ ] Configuration backup (nginx, systemd, etc.)

### Recovery Procedures
- [ ] Node recovery from snapshot documented
- [ ] Full chain recovery from genesis documented
- [ ] Web server recovery documented
- [ ] Disaster recovery runbook tested

---

## 8. DNS & Domains

- [ ] verdischain.com: DNS hosted on 2+ nameservers
- [ ] evolvixos.com: DNS hosted on 2+ nameservers
- [ ] DNSSEC enabled
- [ ] TTL: 300s for A records (fast failover)
- [ ] SPF, DKIM, DMARC for email (if used)

---

## 9. CI/CD Pipeline

- [ ] GitHub Actions: fmt, check, test, clippy (all passing)
- [ ] Release build pipeline (WASM, binary)
- [ ] Chain spec generation automated
- [ ] Deployment scripts tested
- [ ] Rollback procedure documented

---

## 10. Security Hardening (Pre-Mainnet)

- [ ] External security audit completed
- [ ] All P0/P1 issues resolved
- [ ] Penetration testing (web infrastructure)
- [ ] Bug bounty program published
- [ ] security.txt published (✅ done)
- [ ] Incident response plan documented
- [ ] Key custody policy documented

---

## 11. Legal & Compliance

- [ ] Token classification (utility vs security)
- [ ] KYC/AML requirements assessed
- [ ] Privacy policy and T&Cs published
- [ ] Jurisdiction analysis completed
- [ ] Terms of service for validators

---

## 12. Documentation

- [ ] Validator setup guide published
- [ ] Node operator runbook published
- [ ] API documentation published
- [ ] SDK documentation published
- [ ] Chain spec documentation
- [ ] Governance documentation
- [ ] Emergency procedures documented

---

## Launch Readiness Criteria

All of the following MUST be true before mainnet launch:

1. ✅ All code security fixes applied (446 tests pass)
2. ✅ Sudo removed from runtime
3. ✅ Governance configured for post-sudo operation
4. ✅ Mainnet genesis structure complete (tokenomics, vesting, council)
5. ✅ IBC tests passing (30 tests)
6. ✅ Website security headers configured
7. ✅ security.txt published
8. ✅ Rate limiting and HTTP method restrictions in place
9. ⬜ 21 real validator keys generated and custody-confirmed
10. ⬜ External security audit completed and passed
11. ⬜ Production infrastructure deployed and tested
12. ⬜ Monitoring and alerting operational
13. ⬜ Bug bounty program published
14. ⬜ Genesis hash signed and published
15. ⬜ Recovery procedures tested

**Current status: 8/15 items complete. 7 remaining — all operational, not code.**
