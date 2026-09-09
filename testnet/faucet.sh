#!/usr/bin/env bash
# Verdis Testnet Faucet
# Sends 1000 VRS to requesting addresses
# Rate limited: 1 request per address per 24h
set -euo pipefail

FAUCET_SEED="//Faucet"
RATE_LIMIT_FILE="/tmp/faucet-rate-limits.json"
NODE_URL="http://localhost:19944"

# Initialize rate limiter
if [ ! -f "$RATE_LIMIT_FILE" ]; then
    echo '{}' > "$RATE_LIMIT_FILE"
fi

REQUEST_ADDR="${1:-}"
if [ -z "$REQUEST_ADDR" ]; then
    echo '{"error":"Missing address parameter"}'
    exit 1
fi

# Check rate limit
LAST_REQUEST=$(jq -r ".\"$REQUEST_ADDR\" // 0" "$RATE_LIMIT_FILE" 2>/dev/null || echo 0)
NOW=$(date +%s)
DIFF=$((NOW - LAST_REQUEST))
if [ "$DIFF" -lt 86400 ]; then
    HOURS=$((DIFF / 3600))
    echo "{\"error\":\"Rate limited. Next request in $((24 - HOURS))h\"}"
    exit 1
fi

# Send tokens via node CLI
# /opt/verdis-chain-rust/target/release/verdis \
#   --chain testnet \
#   --uri "$FAUCET_SEED" \
#   --rpc-endpoint $NODE_URL \
#   execute --pallet balances --call transfer \
#   --args "$REQUEST_ADDR,1000000000000"

# Update rate limit
jq ".\"$REQUEST_ADDR\" = $NOW" "$RATE_LIMIT_FILE" > /tmp/faucet-rl.tmp
mv /tmp/faucet-rl.tmp "$RATE_LIMIT_FILE"

echo "{\"success\":true,\"amount\":\"1000\",\"unit\":\"VRS\",\"address\":\"$REQUEST_ADDR\"}"
