#!/bin/bash
# Verdis Chain Health Monitor
# Checks all services, RPC, and blockchain state every 60s
# Logs to /var/log/verdis-health.log

LOG="/var/log/verdis-health.log"
RPC="http://localhost:9948"

while true; do
    TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    # Check block height
    BLOCK=$(curl -sf -X POST "$RPC" -H "Content-Type: application/json" \
        -d '{"jsonrpc":"2.0","method":"chain_getHeader","params":[],"id":1}' 2>/dev/null \
        | python3 -c "import sys,json; print(int(json.load(sys.stdin).get('result',{}).get('number','0x0'),16))" 2>/dev/null)
    
    # Check peers
    PEERS=$(curl -sf -X POST "$RPC" -H "Content-Type: application/json" \
        -d '{"jsonrpc":"2.0","method":"system_health","params":[],"id":2}' 2>/dev/null \
        | python3 -c "import sys,json; print(json.load(sys.stdin).get('result',{}).get('peers',0))" 2>/dev/null)
    
    # Check services
    SVC_DOWN=""
    for svc in verdis-rpc-1 verdis-val-1 verdis-val-2 verdis-val-3 verdis-val-4 verdis-val-5 nginx; do
        if ! systemctl is-active --quiet "$svc" 2>/dev/null; then
            SVC_DOWN="$SVC_DOWN $svc"
        fi
    done
    
    # Check disk
    DISK_PCT=$(df / | awk 'NR==2{gsub(/%/,""); print $5}')
    
    # Check memory
    MEM_PCT=$(free | awk 'NR==2{printf "%.0f", $3/$2*100}')
    
    # Log status
    STATUS="OK"
    if [ -z "$BLOCK" ] || [ "$BLOCK" = "0" ]; then STATUS="CRITICAL:no_blocks"; fi
    if [ -n "$SVC_DOWN" ]; then STATUS="WARNING:services_down$SVC_DOWN"; fi
    if [ "$DISK_PCT" -gt 85 ]; then STATUS="CRITICAL:disk_full"; fi
    if [ "$MEM_PCT" -gt 90 ]; then STATUS="WARNING:high_memory"; fi
    
    echo "$TS block=$BLOCK peers=$PEERS disk=${DISK_PCT}% mem=${MEM_PPT}% status=$STATUS" >> "$LOG"
    
    # Alert on critical
    if [[ "$STATUS" == CRITICAL* ]]; then
        logger -t verdis-health "CRITICAL: $STATUS block=$BLOCK peers=$PEERS"
    fi
    
    sleep 60
done
