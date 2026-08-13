#!/bin/bash
# Verdis Chain Testnet Health Monitor
# Runs every 5 minutes via cron, logs to /var/log/verdis-health.log

LOG="/var/log/verdis-health.log"
RPC="http://localhost:9933"
ALERT_EMAIL=""

# Get block height
BLOCK=$(curl -s -m10 -X POST "$RPC" -H "Content-Type: application/json" -d "{\"jsonrpc\":\"2.0\",\"method\":\"chain_getHeader\",\"params\":[],\"id\":1}" | python3 -c "import sys,json; d=json.load(sys.stdin); print(int(d.get(\"result\",{}).get(\"number\",\"0x0\"),16))" 2>/dev/null)

# Get peers
PEERS=$(curl -s -m10 -X POST "$RPC" -H "Content-Type: application/json" -d "{\"jsonrpc\":\"2.0\",\"method\":\"system_peers\",\"params\":[],\"id\":1}" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get(\"result\",[])))" 2>/dev/null)

# Get DEX pools
POOLS=$(curl -s -m10 -X POST "$RPC" -H "Content-Type: application/json" -d "{\"jsonrpc\":\"2.0\",\"method\":\"amm_dex_getAllPools\",\"params\":[],\"id\":1}" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get(\"result\",[])))" 2>/dev/null)

# Get DPoS validators
VALIDATORS=$(curl -s -m10 -X POST "$RPC" -H "Content-Type: application/json" -d "{\"jsonrpc\":\"2.0\",\"method\":\"dpos_activeValidators\",\"params\":[],\"id\":1}" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get(\"result\",[])))" 2>/dev/null)

# Check node services
NODES_UP=0
for i in 1 2 3 4 5 6; do
  status=$(systemctl is-active verdis-node$i 2>/dev/null)
  if [ "$status" = "active" ]; then
    NODES_UP=$((NODES_UP+1))
  fi
done

TIMESTAMP=$(date -u "+%Y-%m-%d %H:%M:%S UTC")

# Log health
echo "[$TIMESTAMP] Block=$BLOCK Peers=$PEERS Pools=$POOLS Validators=$VALIDATORS Nodes=$NODES_UP/6" >> "$LOG"

# Alert conditions
ALERT=""
if [ "$BLOCK" = "0" ] || [ -z "$BLOCK" ]; then
  ALERT="CRITICAL: Chain not producing blocks"
elif [ "$PEERS" = "0" ] || [ -z "$PEERS" ]; then
  ALERT="WARNING: No peers connected"
elif [ "$NODES_UP" -lt 4 ]; then
  ALERT="WARNING: Only $NODES_UP/6 nodes running"
elif [ "$VALIDATORS" = "0" ] || [ -z "$VALIDATORS" ]; then
  ALERT="WARNING: No active validators"
elif [ "$POOLS" = "0" ] || [ -z "$POOLS" ]; then
  ALERT="INFO: No DEX pools"
fi

if [ -n "$ALERT" ]; then
  echo "[$TIMESTAMP] ALERT: $ALERT" >> "$LOG"
fi
