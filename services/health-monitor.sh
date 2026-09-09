#!/bin/bash
# Verdis Chain Health Monitor v2.0
LOG="/var/log/verdis-health.log"
RPC1="http://localhost:9933"
RPC2="http://localhost:9934"
SERVICES="verdis-node verdis-node2 verdis-api verdis-faucet verdis-health-monitor verdis-rpc-filter verdis-tx-relay verdis-txbot nginx"

while true; do
    TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    BLOCK1=$(curl -sf -X POST "$RPC1" -H "Content-Type: application/json" -d "{\"jsonrpc\":\"2.0\",\"method\":\"chain_getHeader\",\"params\":[],\"id\":1}" 2>/dev/null | python3 -c "import sys,json; print(int(json.load(sys.stdin).get(\"result\",{}).get(\"number\",\"0x0\"),16))" 2>/dev/null)
    BLOCK2=$(curl -sf -X POST "$RPC2" -H "Content-Type: application/json" -d "{\"jsonrpc\":\"2.0\",\"method\":\"chain_getHeader\",\"params\":[],\"id\":2}" 2>/dev/null | python3 -c "import sys,json; print(int(json.load(sys.stdin).get(\"result\",{}).get(\"number\",\"0x0\"),16))" 2>/dev/null)
    PEERS=$(curl -sf -X POST "$RPC1" -H "Content-Type: application/json" -d "{\"jsonrpc\":\"2.0\",\"method\":\"system_peers\",\"params\":[],\"id\":3}" 2>/dev/null | python3 -c "import sys,json; print(len(json.load(sys.stdin).get(\"result\",[])))" 2>/dev/null)
    VALS=$(curl -sf -X POST "$RPC1" -H "Content-Type: application/json" -d "{\"jsonrpc\":\"2.0\",\"method\":\"dpos_allValidators\",\"params\":[],\"id\":4}" 2>/dev/null | python3 -c "import sys,json; print(len(json.load(sys.stdin).get(\"result\",[])))" 2>/dev/null)
    SVC_DOWN=""
    for svc in $SERVICES; do
        if ! systemctl is-active --quiet "$svc" 2>/dev/null; then SVC_DOWN="$SVC_DOWN $svc"; fi
    done
    DISK_PCT=$(df -h / | awk "END{print \$5}" | tr -d %)
    MEM_PCT=$(free | awk "NR==2{printf \"%.0f\", \$3/\$2*100}")
    WEB_STATUS=$(curl -sk -o /dev/null -w "%{http_code}" -m 5 https://verdischain.com/ 2>/dev/null)
    STATUS="OK"
    if [ -z "$BLOCK1" ] || [ "$BLOCK1" = "0" ]; then STATUS="CRITICAL:no_blocks"; fi
    if [ -n "$SVC_DOWN" ]; then STATUS="${STATUS}|WARN:svc_down:$SVC_DOWN"; fi
    if [ "$DISK_PCT" -gt 85 ] 2>/dev/null; then STATUS="${STATUS}|CRITICAL:disk_full"; fi
    if [ "$MEM_PCT" -gt 90 ] 2>/dev/null; then STATUS="${STATUS}|WARN:high_mem"; fi
    if [ "$WEB_STATUS" != "200" ]; then STATUS="${STATUS}|WARN:web:$WEB_STATUS"; fi
    if [ -n "$BLOCK2" ] && [ "$BLOCK2" != "0" ]; then
        DIFF=$((BLOCK1 - BLOCK2))
        if [ "$DIFF" -gt 10 ] || [ "$DIFF" -lt -10 ]; then STATUS="${STATUS}|WARN:node_lag:$DIFF"; fi
    fi
    echo "$TS block1=$BLOCK1 block2=$BLOCK2 peers=$PEERS vals=$VALS disk=${DISK_PCT}% mem=${MEM_PCT}% web=$WEB_STATUS status=$STATUS" >> "$LOG"
    if echo "$STATUS" | grep -q "CRITICAL"; then
        logger -t verdis-health "CRITICAL: $STATUS block=$BLOCK1 peers=$PEERS"
    fi
    sleep 60
done
