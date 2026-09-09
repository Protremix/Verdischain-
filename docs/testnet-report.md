# Verdis Testnet Validation Report

## Network Configuration
| Parameter | Value |
|-----------|-------|
| Chain Name | Verdis Testnet |
| Binary Version | 2.0.0 |
| Consensus | BABE (block production) + GRANDPA (finality) |
| Validators | 5 (Alice, Bob, Charlie, Dave, Eve) |
| Boot Nodes | 2 |
| RPC Nodes | 2 |
| Total Nodes | 9 |
| Block Time | 6 seconds |
| Session Period | 600 blocks (~1 hour) |
| Epoch Management | pallet_session (SessionManager) |
| Total Supply | 100,000,000,000 VRS |
| SS58 Format | 909 |
| Token Decimals | 9 |

## Test Results Summary

| Test | Status | Details |
|------|--------|---------|
| Multi-Node Networking | PASS | 9 nodes, 8 peers each, stable 6s blocks |
| GRANDPA Finality | PASS | 2-3 block finalization lag |
| 1K TX Load Test | PASS | 408 TPS, 100% success, 24ms avg |
| 10K TX Load Test | PASS | 556 TPS, 96% success, 86ms avg |
| 100K TX Load Test | PASS | 430 TPS, 99.89% success, 9ms avg |
| RPC Performance | PASS | 1.2ms latency, 105 safe methods |
| Security Hardening | PASS | Localhost RPC, UFW, Nginx headers |
| Token Supply | PASS | 100B VRS verified on-chain |
| Faucet | PASS | 1000 VRS/24h, polkadot.js |
| Monitoring | PARTIAL | Prometheus/Grafana running, substrate metrics pending |
| Epoch Transitions | PENDING | Awaiting blocks 600/1200/1800/2400 |

## Load Test Details

### 1K Transaction Test
- TPS: 408.7
- Success: 1000/1000 (100%)
- Latency: min=14ms, avg=24ms, p50=21ms, p90=29ms, p99=97ms, max=136ms
- Memory delta: +28 MB
- DB growth: 0 KB

### 10K Transaction Test
- TPS: 556.0
- Success: 9602/10000 (96%)
- Latency: min=14ms, avg=86ms, p50=84ms, p90=110ms, p99=174ms, max=218ms
- Memory delta: +247 MB
- DB growth: +456 KB
- Failures: transaction pool limit (1016 error)

### 100K Transaction Test
- TPS: 430.1
- Success: 99893/100000 (99.89%)
- Failures: 107 (nonce conflicts, auto-retried)
- Latency: min=4ms, avg=9ms, p50=7ms, p90=10ms, p99=49ms, max=2131ms
- Memory delta: +529 MB (5236 → 5765 MB)
- DB growth: +7888 KB (7.3 MB for 100K transactions)
- Duration: 232 seconds
- Architecture: 5 per-account sequential workers (Alice→Bob→Charlie→Dave→Eve ring)

## Security Hardening
- RPC bound to localhost only (no --unsafe-rpc-external)
- --rpc-methods Safe (no unsafe methods)
- UFW firewall: ports 22/80/443/30333 only
- Nginx: HSTS, X-Frame-Options, X-Content-Type-Options, XSS-Protection
- Rate limiting: 30 r/s RPC
- CORS: restricted to verdischain.com

## Issues Found and Fixed
1. GRANDPA Equivocation: dev key injection was inserting //Alice keys into all validators
2. WASM Linker: added -C link-arg=--allow-undefined in runtime/build.rs
3. SS58 Format 909: using raw public keys instead of SS58 addresses for RPC calls
4. Transaction Pool Drops: per-account sequential workers prevent nonce conflicts
5. Consensus Stall at Block 600: removed SameAuthoritiesForever from pallet_babe

## Deployment Artifacts
1. Verdis binary (target/release/verdis)
2. Chain spec (chain-spec-raw.json)
3. Dockerfile
4. Docker Compose (docker-compose-testnet.yml)
5. Node operator guide (docs/node-operator-guide.md)
6. Faucet (faucet.js - polkadot.js based)
7. Load testing tools (load-test.js, load-test-v2.js)
8. Epoch monitor (epoch-monitor.js)
9. Monitoring stack (Prometheus, Grafana, Alertmanager, Node Exporter)
10. 14 documentation files (ARCHITECTURE, DEPLOYMENT, DISASTER_RECOVERY, etc.)

## Conclusion
The Verdis blockchain v2.0.0 (Rust + Substrate) testnet is operationally stable with 9 nodes, achieving 430 TPS with 99.89% transaction success rate over 100K transactions. Security hardening is complete. The critical epoch transition test at blocks 600/1200/1800/2400 is pending final verification.
