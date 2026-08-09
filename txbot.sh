#!/bin/bash
# Verdis Chain Transaction Bot
# Sends system.remark extrinsics every 10-25 seconds to generate chain activity

RPC_URL="http://127.0.0.1:9933"
SEED="//Alice"
REMARKS=(
  "Verdis Chain: Building a greener blockchain"
  "VRDX: 100B total supply, 12B investor allocation"
  "Carbon credits tracked on-chain"
  "DPoS consensus with 14 validators"
  "Eco-friendly blockchain with green validator scoring"
  "AMM DEX with 6 liquidity pools live"
  "526,000 trees planted and counting"
  "Verdiscan: Real-time blockchain explorer"
  "EvolvixOS: AI Engineering Platform"
  "Testnet live and producing blocks"
)

while true; do
  # Pick a random remark
  REMARK="${REMARKS[$((RANDOM % ${#REMARKS[@]}))]}"
  
  # Send the extrinsic
  RESULT=$(/usr/local/bin/verdis submit-extrinsic --rpc-url "$RPC_URL" --sr25519-key "$SEED" "system.remark($REMARK)" 2>&1)
  
  if [ $? -eq 0 ]; then
    echo "[$(date)] TX sent: $REMARK -> $RESULT"
  else
    # Try alternative command format
    RESULT=$(/usr/local/bin/verdis --dev --rpc-port 9933 --rpc-cors all --unsafe-rpc-external --rpc-methods unsafe send-remark "$REMARK" --sr25519-key "$SEED" 2>&1)
    if [ $? -eq 0 ]; then
      echo "[$(date)] TX sent (alt): $REMARK -> $RESULT"
    else
      echo "[$(date)] TX failed: $RESULT"
    fi
  fi
  
  # Wait 10-25 seconds
  SLEEP_TIME=$((RANDOM % 16 + 10))
  sleep $SLEEP_TIME
done
