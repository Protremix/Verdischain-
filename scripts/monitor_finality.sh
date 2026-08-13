#!/bin/bash
# Verdis Chain Finality Monitor
# Checks finality lag, peer count, and epoch rotation events

RPC='http://localhost:9933'
LOG='/var/log/verdis-node.log'
ALERT_LAG=20  # Alert if finality lag exceeds 20 blocks

while true; do
  # Get best block
  BEST=$(curl -s -X POST -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","method":"chain_getHeader","params":[],"id":1}' $RPC | python3 -c 'import sys,json; print(int(json.loads(sys.stdin.read())["result"]["number"],16))' 2>/dev/null)
  
  # Get finalized block
  FIN_HASH=$(curl -s -X POST -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","method":"chain_getFinalizedHead","params":[],"id":1}' $RPC | python3 -c 'import sys,json; print(json.loads(sys.stdin.read())["result"])' 2>/dev/null)
  FIN=$(curl -s -X POST -H 'Content-Type: application/json' -d "{\"jsonrpc\":\"2.0\",\"method\":\"chain_getHeader\",\"params\":[\"$FIN_HASH\"],\"id\":1}" $RPC | python3 -c 'import sys,json; print(int(json.loads(sys.stdin.read())["result"]["number"],16))' 2>/dev/null)
  
  # Get peers
  PEERS=$(curl -s -X POST -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","method":"system_health","params":[],"id":1}' $RPC | python3 -c 'import sys,json; print(json.loads(sys.stdin.read())["result"]["peers"])' 2>/dev/null)
  
  # Calculate lag
  LAG=$((BEST - FIN))
  
  # Check for epoch changes
  EPOCH_COUNT=$(grep 'New epoch' $LOG | grep "$(date +%Y-%m-%d)" | wc -l)
  GRANDPA_CHANGES=$(grep 'Applying GRANDPA' $LOG | grep "$(date +%Y-%m-%d)" | wc -l)
  
  # Log status
  echo "$(date '+%H:%M:%S') | Best:#$BEST Fin:#$FIN Lag:$LAG Peers:$PEERS Epochs:$EPOCH_COUNT GRANDPA:$GRANDPA_CHANGES"
  
  # Alert on high lag
  if [ "$LAG" -gt "$ALERT_LAG" ]; then
    echo "⚠️  ALERT: Finality lag $LAG blocks exceeds threshold $ALERT_LAG"
  fi
  
  sleep 30
done
