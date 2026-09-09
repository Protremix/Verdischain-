# Verdis Chain 14-Day Soak Test

## Overview
- Start: Aug 14 2026 19:09 UTC (21:09 Madrid)
- End: Aug 28 2026 19:09 UTC (21:09 Madrid)
- Duration: 14 days (336 hourly checks)
- Status: IN PROGRESS

## Monitoring
- Script: /opt/verdis-repo/soak-test-monitor.sh
- Log: /opt/verdis-repo/soak-test-log.csv (CSV, hourly entries)
- Alerts: /opt/verdis-repo/soak-test-alerts.log
- Cron: Hourly at 0 * * * *

## Metrics Tracked (Hourly)
1. block_height - Current chain height
2. peers - Connected peers
3. is_syncing - Chain sync status
4. all_validators - Total registered validators
5. active_validators - Active validator set
6. green_validators - Validators with green_score > 0
7. dex_pools - Active DEX pools
8. services_active - Running verdis-* services
9. services_failed - Failed services
10. disk_pct - Root filesystem usage
11. ram_pct - RAM utilization
12. cpu_load - 1-minute load average
13. uptime_hours - Server uptime

## Alert Thresholds
- BLOCK_HEIGHT_FAIL: RPC call failed
- NO_PEERS: Peer count is 0
- SYNCING: Chain in sync mode
- SERVICES_FAILED: Services failed
- DISK_CRITICAL: Disk above 90%

## Pass Criteria
1. Block production continuous for 14 days
2. GRANDPA finality must not stall
3. At least 1 peer connected at all times
4. All 15 services remain active
5. No node crashes or consensus stalls
6. Data consistency maintained

## Initial State (Hour 0)
- Block: #3639
- Peers: 2
- Active Validators: 21
- Green Validators: 21
- DEX Pools: 6
- Services: 15 active, 0 failed
- Disk: 63%, RAM: 17%

## Daily Check
tail -24 /opt/verdis-repo/soak-test-log.csv
cat /opt/verdis-repo/soak-test-alerts.log

## Completion
Verify: 336 entries, no alerts, steady block growth, all services active.
