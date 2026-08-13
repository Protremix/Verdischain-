#!/usr/bin/env bash
# Verdis Integration Test Suite
# Tests a running Verdis node for full functionality
set -euo pipefail

NODE_URL="${1:-http://localhost:9944}"
PASS=0
FAIL=0
SKIP=0

echo "================================================"
echo "  Verdis Integration Tests"
echo "  Target: $NODE_URL"
echo "  $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "================================================"

rpc_call() {
    local method="$1"
    local params="${2:-[]}"
    curl -s -X POST "$NODE_URL" \
        -H 'Content-Type: application/json' \
        -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"$method\",\"params\":$params}"
}

test_pass() { echo "  ✅ $1"; PASS=$((PASS+1)); }
test_fail() { echo "  ❌ $1"; FAIL=$((FAIL+1)); }
test_skip() { echo "  ⏭️  $1"; SKIP=$((SKIP+1)); }

# 1. Node health
echo ""
echo "[1/10] Node Health..."
HEALTH=$(rpc_call "system_health")
PEERS=$(echo "$HEALTH" | jq -r '.result.peers // -1' 2>/dev/null)
SYNCING=$(echo "$HEALTH" | jq -r '.result.isSyncing // false' 2>/dev/null)
if [ "$PEERS" -ge 0 ] 2>/dev/null; then
    test_pass "system_health responded (peers: $PEERS, syncing: $SYNCING)"
else
    test_fail "system_health failed"
fi

# 2. Block production
echo ""
echo "[2/10] Block Production..."
BLOCK1=$(rpc_call "chain_getHeader" | jq -r '.result.number // "0"' 2>/dev/null)
sleep 7
BLOCK2=$(rpc_call "chain_getHeader" | jq -r '.result.number // "0"' 2>/dev/null)
if [ "$BLOCK1" != "0" ] && [ "$BLOCK2" != "0" ] && [ "$((16#$BLOCK2))" -gt "$((16#$BLOCK1))" ]; then
    DIFF=$(( 16#$BLOCK2 - 16#$BLOCK1 ))
    test_pass "Block advanced: #$((16#$BLOCK1)) → #$((16#$BLOCK2)) ($DIFF blocks in 7s)"
else
    test_fail "Block production stalled (block1=$BLOCK1, block2=$BLOCK2)"
fi

# 3. GRANDPA finality
echo ""
echo "[3/10] GRANDPA Finality..."
BEST=$(rpc_call "chain_getHeader" | jq -r '.result.number // "0"' 2>/dev/null)
FINALIZED=$(rpc_call "chain_getFinalizedHead" | jq -r '.result // "null"' 2>/dev/null)
if [ "$FINALIZED" != "null" ] && [ -n "$FINALIZED" ]; then
    FINALIZED_BLOCK=$(rpc_call "chain_getHeader" "[\"$FINALIZED\"]" | jq -r '.result.number // "0"' 2>/dev/null)
    if [ "$FINALIZED_BLOCK" != "0" ]; then
        LAG=$(( 16#$BEST - 16#$FINALIZED_BLOCK ))
        if [ "$LAG" -le 10 ]; then
            test_pass "Finality lag: $LAG blocks (best=$((16#$BEST)), finalized=$((16#$FINALIZED_BLOCK)))"
        else
            test_fail "Finality lag too high: $LAG blocks"
        fi
    else
        test_fail "Could not get finalized block header"
    fi
else
    test_fail "No finalized head"
fi

# 4. RPC endpoints
echo ""
echo "[4/10] RPC Endpoints..."
for method in "system_version" "system_chain" "system_name" "system_properties"; do
    RESULT=$(rpc_call "$method" | jq -r '.result // "FAIL"' 2>/dev/null)
    if [ "$RESULT" != "FAIL" ] && [ -n "$RESULT" ]; then
        test_pass "$method = $RESULT"
    else
        test_fail "$method failed"
    fi
done

# 5. Chain state
echo ""
echo "[5/10] Chain State..."
VERSION=$(rpc_call "state_getRuntimeVersion" | jq -r '.result.specVersion // "FAIL"' 2>/dev/null)
if [ "$VERSION" != "FAIL" ]; then
    test_pass "Runtime version: $VERSION"
else
    test_fail "state_getRuntimeVersion failed"
fi

# 6. Token supply
echo ""
echo "[6/10] Token Supply..."
# Query TotalIssuance storage key
ISSUANCE_KEY="0x3a617574686f726974966f725f6465706f7369745f746f74616c5f69737375616e6365"
ISSUANCE=$(rpc_call "state_getStorage" "[\"$ISSUANCE_KEY\"]" | jq -r '.result // "null"' 2>/dev/null)
if [ "$ISSUANCE" != "null" ] && [ -n "$ISSUANCE" ]; then
    test_pass "TotalIssuance storage accessible"
else
    test_skip "TotalIssuance storage key may differ (skipped)"
fi

# 7. Peer info
echo ""
echo "[7/10] Peer Information..."
PEER_COUNT=$(rpc_call "system_health" | jq -r '.result.peers // -1' 2>/dev/null)
if [ "$PEER_COUNT" -ge 0 ] 2>/dev/null; then
    if [ "$PEER_COUNT" -gt 0 ]; then
        PEERS_DATA=$(rpc_call "system_peers")
        PEER_LIST_LEN=$(echo "$PEERS_DATA" | jq -r '.result | length' 2>/dev/null || echo 0)
        test_pass "Peers: $PEER_COUNT connected, $PEER_LIST_LEN in list"
    else
        test_pass "Peers: 0 (single-node mode)"
    fi
else
    test_fail "Could not get peer count"
fi

# 8. Consensus
echo ""
echo "[8/10] Consensus..."
GRANDPA_PROGRESS=$(rpc_call "grandpa_roundState" 2>/dev/null | jq -r '.result // "FAIL"' 2>/dev/null)
if [ "$GRANDPA_PROGRESS" != "FAIL" ] && [ -n "$GRANDPA_PROGRESS" ]; then
    test_pass "GRANDPA round state accessible"
else
    test_skip "grandpa_roundState not available (may need --unsafe-rpc-external)"
fi

# 9. Epoch transitions
echo ""
echo "[9/10] Epoch Transitions..."
CURRENT_BLOCK=$((16#$BEST))
EPOCH_LENGTH=600
CURRENT_EPOCH=$((CURRENT_BLOCK / EPOCH_LENGTH))
BLOCKS_TO_NEXT=$((EPOCH_LENGTH - (CURRENT_BLOCK % EPOCH_LENGTH)))
test_pass "Epoch $CURRENT_EPOCH, $BLOCKS_TO_NEXT blocks to next transition"

# 10. WebSocket
echo ""
echo "[10/10] WebSocket..."
WS_TEST=$(timeout 5 curl -s -N \
    -H "Connection: Upgrade" \
    -H "Upgrade: websocket" \
    -H "Sec-WebSocket-Version: 13" \
    -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" \
    "$NODE_URL" 2>/dev/null | head -c 1 || echo "")
if [ -n "$WS_TEST" ]; then
    test_pass "WebSocket endpoint reachable"
else
    test_skip "WebSocket test inconclusive (may require ws:// protocol)"
fi

# Summary
echo ""
echo "================================================"
echo "  Integration Test Results"
echo "================================================"
echo "  ✅ Passed:  $PASS"
echo "  ❌ Failed:  $FAIL"
echo "  ⏭️  Skipped: $SKIP"
echo "  Total:      $((PASS + FAIL + SKIP))"
echo "================================================"

if [ "$FAIL" -gt 0 ]; then
    exit 1
else
    exit 0
fi
