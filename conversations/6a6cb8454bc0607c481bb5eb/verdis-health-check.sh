#!/bin/bash
# Verdis blockchain health check - 10 node network
STATUS='OK'
WARNINGS=''

# 1. Node process running
NODE_COUNT=$(pgrep -c -f "verdis.*--chain" 2>/dev/null || echo 0)
if [ "$NODE_COUNT" -lt 8 ]; then
    STATUS='CRITICAL'
    WARNINGS="$WARNINGS Only $NODE_COUNT/10 nodes running."
fi

# 2. Block production
BLOCK_HEX=$(curl -s -X POST http://localhost:9933 -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","id":1,"method":"chain_getHeader","params":[]}' 2>/dev/null | python3 -c "import json,sys; h=json.load(sys.stdin)['result']; print(int(h['number'],16))" 2>/dev/null)

if [ -z "$BLOCK_HEX" ]; then
    STATUS='CRITICAL'
    WARNINGS="$WARNINGS Cannot reach RPC."
fi

# 3. Peer count
PEERS=$(curl -s -X POST http://localhost:9933 -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","id":1,"method":"system_peers","params":[]}' 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print(len(d.get('result',[])))" 2>/dev/null)
if [ "$PEERS" -lt 5 ]; then
    STATUS='WARNING'
    WARNINGS="$WARNINGS Low peer count: $PEERS"
fi

# 4. Disk space
DISK_PCT=$(df / | tail -1 | awk '{print $5}' | tr -d '%')
if [ "$DISK_PCT" -gt 80 ]; then
    STATUS='WARNING'
    WARNINGS="$WARNINGS Disk usage at ${DISK_PCT}%."
fi

# 5. Memory
MEM_PCT=$(free | awk '/Mem:/ {printf "%.0f", $3/$2*100}')
if [ "$MEM_PCT" -gt 85 ]; then
    STATUS='WARNING'
    WARNINGS="$WARNINGS Memory usage at ${MEM_PCT}%."
fi

# 6. SSL cert expiry
DAYS_LEFT=$(openssl s_client -connect verdischain.com:443 -servername verdischain.com </dev/null 2>/dev/null | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2 | xargs -I{} date -d "{}" +%s 2>/dev/null | xargs -I{} expr \( {} - $(date +%s) \) / 86400 2>/dev/null)
if [ -n "$DAYS_LEFT" ] && [ "$DAYS_LEFT" -lt 14 ]; then
    STATUS='WARNING'
    WARNINGS="$WARNINGS SSL cert expires in ${DAYS_LEFT} days."
fi

# 7. Check all node services
ALL_NODES_OK=true
for i in "" 2 3 4 5 6 7 8 9 10; do
    svc="verdis-node${i}"
    if ! systemctl is-active --quiet $svc 2>/dev/null; then
        ALL_NODES_OK=false
        WARNINGS="$WARNINGS $svc not active."
    fi
done
[ "$ALL_NODES_OK" = false ] && [ "$STATUS" = "OK" ] && STATUS='WARNING'

# Output
echo "[$(date)] Verdis Health: $STATUS"
echo "  Block: #$BLOCK_HEX"
echo "  Nodes: $NODE_COUNT/10"
echo "  Peers: $PEERS"
echo "  Disk: ${DISK_PCT}%"
echo "  Memory: ${MEM_PCT}%"
echo "  SSL: ${DAYS_LEFT:-unknown} days remaining"
if [ -n "$WARNINGS" ]; then
    echo "  Warnings: $WARNINGS"
fi
exit $([ "$STATUS" = "OK" ] && echo 0 || echo 1)
