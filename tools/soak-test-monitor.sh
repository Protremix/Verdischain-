#!/bin/bash
# Verdis Chain 14-Day Soak Test Monitor
# Start: Aug 14 2026 23:07 Madrid (21:07 UTC)
# End:   Aug 28 2026 23:07 Madrid (21:07 UTC)
# Duration: 14 days (336 hourly checks via cron)

LOG_FILE="/opt/verdis-repo/soak-test-log.csv"
ALERT_LOG="/opt/verdis-repo/soak-test-alerts.log"
START_EPOCH=$(date -u -d "2026-08-14 19:09:36 UTC" +%s)
END_EPOCH=$(date -u -d "2026-08-28 19:09:36 UTC" +%s)
NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)
NOW_EPOCH=$(date -u +%s)

# Check if soak test period is over
if [ "$NOW_EPOCH" -gt "$END_EPOCH" ]; then
    echo "$NOW,SOAK_TEST_COMPLETE" >> "$LOG_FILE"
    exit 0
fi

# Initialize log file with headers if it does not exist
if [ ! -f "$LOG_FILE" ]; then
    echo "timestamp,block_height,peers,is_syncing,all_validators,active_validators,green_validators,dex_pools,services_active,services_failed,disk_pct,ram_pct,cpu_load,uptime_hours,hour_num" > "$LOG_FILE"
fi

# Calculate hour number (0-335)
HOUR_NUM=$(( (NOW_EPOCH - START_EPOCH) / 3600 ))

# Fetch chain metrics via RPC
BLOCK_HEIGHT=$(curl -s http://localhost:9933 -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"chain_getHeader","params":[]}' 2>/dev/null \
  | python3 -c 'import json,sys; print(int(json.load(sys.stdin)["result"]["number"],16))' 2>/dev/null || echo "FAIL")

HEALTH=$(curl -s http://localhost:9933 -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"system_health","params":[]}' 2>/dev/null)
PEERS=$(echo "$HEALTH" | python3 -c 'import json,sys; print(json.load(sys.stdin)["result"]["peers"])' 2>/dev/null || echo "FAIL")
IS_SYNCING=$(echo "$HEALTH" | python3 -c 'import json,sys; print(json.load(sys.stdin)["result"]["isSyncing"])' 2>/dev/null || echo "FAIL")

ALL_VALS=$(curl -s http://localhost:9933 -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"dpos_allValidators","params":[]}' 2>/dev/null \
  | python3 -c 'import json,sys; print(len(json.load(sys.stdin)["result"]))' 2>/dev/null || echo "FAIL")

ACTIVE_VALS=$(curl -s http://localhost:9933 -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"dpos_activeValidators","params":[]}' 2>/dev/null \
  | python3 -c 'import json,sys; print(len(json.load(sys.stdin)["result"]))' 2>/dev/null || echo "FAIL")

GREEN_VALS=$(curl -s https://verdischain.com/api/v1/validators 2>/dev/null \
  | python3 -c 'import json,sys; d=json.load(sys.stdin); print(sum(1 for v in d.get("data",[]) if v.get("green_score",0)>0))' 2>/dev/null || echo "FAIL")

DEX_POOLS=$(curl -s https://verdischain.com/api/v1/dex/pools 2>/dev/null \
  | python3 -c 'import json,sys; d=json.load(sys.stdin); print(len(d.get("data",[])))' 2>/dev/null || echo "FAIL")

# Services
SERVICES_ACTIVE=$(systemctl list-units "verdis*" --no-pager --state=active 2>/dev/null | grep -c "verdis" || echo "0")
SERVICES_FAILED=$(systemctl list-units "verdis*" --no-pager --state=failed 2>/dev/null | grep -c "verdis" || echo "0")

# Disk usage
DISK_PCT=$(df -h / | awk 'NR==2{gsub(/%/,""); print $5}')

# RAM
RAM_PCT=$(free | awk 'NR==2{printf "%.0f", $3/$2*100}')

# CPU load (1-minute average)
CPU_LOAD=$(awk '{print $1}' /proc/loadavg)

# Uptime
UPTIME_HOURS=$(awk '{printf "%.1f", $1/3600}' /proc/uptime)

# Log the entry
echo "$NOW,$BLOCK_HEIGHT,$PEERS,$IS_SYNCING,$ALL_VALS,$ACTIVE_VALS,$GREEN_VALS,$DEX_POOLS,$SERVICES_ACTIVE,$SERVICES_FAILED,$DISK_PCT,$RAM_PCT,$CPU_LOAD,$UPTIME_HOURS,$HOUR_NUM" >> "$LOG_FILE"

# Check for alerts
ALERTS=""
[ "$BLOCK_HEIGHT" = "FAIL" ] && ALERTS="$ALERTS BLOCK_HEIGHT_FAIL"
[ "$PEERS" = "0" ] && ALERTS="$ALERTS NO_PEERS"
[ "$IS_SYNCING" = "True" ] && ALERTS="$ALERTS SYNCING"
[ "$SERVICES_FAILED" -gt 0 ] 2>/dev/null && ALERTS="$ALERTS SERVICES_FAILED($SERVICES_FAILED)"
[ "$DISK_PCT" -gt 90 ] 2>/dev/null && ALERTS="$ALERTS DISK_CRITICAL"

if [ -n "$ALERTS" ]; then
    echo "$NOW ALERT:$ALERTS" >> "$ALERT_LOG"
fi

echo "Soak test hour $HOUR_NUM/336: Block #$BLOCK_HEIGHT | $PEERS peers | $ACTIVE_VALS active vals | $GREEN_VALS green | $DEX_POOLS pools | $SERVICES_FAILED failed | ${DISK_PCT}% disk | ${RAM_PCT}% RAM"
