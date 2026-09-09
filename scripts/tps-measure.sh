#!/bin/bash
# TPS Measurement Script for Verdis Chain
# Measures transactions per second by sending N parallel transactions via RPC
# Usage: ./tps-measure.sh [num_transactions] [concurrency]

set -e

NUM_TX=${1:-100}
CONCURRENCY=${2:-10}
RPC_URL="http://localhost:9933"
WS_URL="ws://localhost:9944"

echo "=== Verdis Chain TPS Measurement ==="
echo "Transactions: $NUM_TX"
echo "Concurrency: $CONCURRENCY"
echo "RPC: $RPC_URL"
echo ""

# Check if node is running
if ! curl -s -X POST "$RPC_URL" -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"system_health","params":[],"id":1}' | grep -q "peers"; then
    echo "ERROR: Node is not running at $RPC_URL"
    exit 1
fi

# Get starting block number
START_BLOCK=$(curl -s -X POST "$RPC_URL" -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"chain_getHeader","params":[],"id":1}' \
    | python3 -c "import sys,json; print(json.load(sys.stdin)['result']['number'],end='')")

echo "Starting block: #$START_BLOCK"
echo "Sending $NUM_TX transactions..."

START_TIME=$(date +%s%N)

# Send transactions in parallel
seq 1 "$NUM_TX" | xargs -P "$CONCURRENCY" -I {} curl -s -X POST "$RPC_URL" \
    -H "Content-Type: application/json" \
    -d "{\"jsonrpc\":\"2.0\",\"method\":\"system_addLog\",\"params\":[\"TPS test tx {}\"],\"id\":{}}" \
    > /dev/null 2>&1 || true

# Also send signed transactions via tx-relay if available
for i in $(seq 1 "$NUM_TX"); do
    curl -s -X POST "http://localhost:4400/api/tx-relay/submit" \
        -H "Content-Type: application/json" \
        -d "{\"method\":\"system\",\"extrinsic\":\"remark\",\"args\":[\"tps-test-$i\"]}" \
        > /dev/null 2>&1 || true
done

# Wait for transactions to be included in blocks
echo "Waiting for block inclusion..."
sleep 10

# Get ending block number
END_BLOCK=$(curl -s -X POST "$RPC_URL" -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"chain_getHeader","params":[],"id":1}' \
    | python3 -c "import sys,json; print(json.load(sys.stdin)['result']['number'],end='')")

END_TIME=$(date +%s%N)

# Calculate TPS
ELAPSED_MS=$(( (END_TIME - START_TIME) / 1000000 ))
ELAPSED_S=$(echo "scale=2; $ELAPSED_MS / 1000" | bc)
BLOCKS_PRODUCED=$(( END_BLOCK - START_BLOCK ))

echo ""
echo "=== Results ==="
echo "Blocks produced: $BLOCKS_PRODUCED"
echo "Elapsed time: ${ELAPSED_S}s"
echo "Transactions sent: $NUM_TX"

if (( $(echo "$ELAPSED_S > 0" | bc -l) )); then
    TPS=$(echo "scale=2; $NUM_TX / $ELAPSED_S" | bc)
    echo "TPS: $TPS"
else
    echo "TPS: N/A (elapsed too short)"
fi

# Get additional chain stats
echo ""
echo "=== Chain Stats ==="
curl -s -X POST "$RPC_URL" -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"system_health","params":[],"id":1}' \
    | python3 -c "import sys,json; d=json.load(sys.stdin)['result']; print(f'Peers: {d.get(\"peers\",\"?\")}'); print(f'Syncing: {d.get(\"isSyncing\",\"?\")}')"

# Get current era/epoch info
curl -s -X POST "$RPC_URL" -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"babe_epochAuthorship","params":[],"id":1}' \
    | python3 -c "
import sys,json
try:
    d=json.load(sys.stdin)['result']
    print(f'Epoch validators: {len(d)}')
except:
    print('Epoch info: N/A')
" 2>/dev/null || echo "Epoch info: N/A"

echo ""
echo "=== Done ==="
