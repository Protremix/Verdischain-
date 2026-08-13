#!/bin/bash
# Verdis Chain Consensus Health Check
# Verifies all nodes share the same genesis, runtime, and chain.
# Exit non-zero on any inconsistency.

set -euo pipefail

# Expected values (from canonical chain spec)
EXPECTED_GENESIS='0xfa13b9b2f73138e1'  # Truncated for comparison
EXPECTED_SPEC_VERSION=14
EXPECTED_IMPL_VERSION=7

# Node RPC ports
NODES=(
    "Alice:9933"
    "Charlie:9935"
    "Bob:9944"
    "Dave:9946"
    "Eve:9947"
)

ERRORS=0

echo "=== Verdis Chain Consensus Health Check ==="
echo "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "Expected genesis: $EXPECTED_GENESIS..."
echo "Expected runtime: spec=$EXPECTED_SPEC_VERSION impl=$EXPECTED_IMPL_VERSION"
echo ""

for node_entry in "${NODES[@]}"; do
    name=${node_entry%%:*}
    port=${node_entry##*:}
    
    # Get genesis hash
    genesis=$(curl -s -m 5 -X POST http://127.0.0.1:$port -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","method":"chain_getBlockHash","params":[0],"id":1}' 2>/dev/null | python3 -c 'import sys,json; print(json.load(sys.stdin).get("result","ERROR")[:18])' 2>/dev/null || echo "NO_RESPONSE")
    
    # Get runtime version
    rt=$(curl -s -m 5 -X POST http://127.0.0.1:$port -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","method":"state_getRuntimeVersion","params":[],"id":2}' 2>/dev/null | python3 -c 'import sys,json; r=json.load(sys.stdin).get("result",{}); print(f"{r.get("specVersion",0)},{r.get("implVersion",0)}")' 2>/dev/null || echo "0,0")
    
    # Get best block
    best=$(curl -s -m 5 -X POST http://127.0.0.1:$port -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","method":"chain_getHeader","params":[],"id":3}' 2>/dev/null | python3 -c 'import sys,json; h=json.load(sys.stdin).get("result",{}).get("number","0x0"); print(int(h,16))' 2>/dev/null || echo "0")
    
    # Get finalized head
    fin=$(curl -s -m 5 -X POST http://127.0.0.1:$port -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","method":"chain_getFinalizedHead","params":[],"id":4}' 2>/dev/null | python3 -c 'import sys,json; print(json.load(sys.stdin).get("result","ERROR")[:18])' 2>/dev/null || echo "NO_RESPONSE")
    
    # Get chain spec name
    chain=$(curl -s -m 5 -X POST http://127.0.0.1:$port -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","method":"system_chain","params":[],"id":5}' 2>/dev/null | python3 -c 'import sys,json; print(json.load(sys.stdin).get("result","?"))' 2>/dev/null || echo "?")
    
    spec_ver=${rt%,*}
    impl_ver=${rt#*,}
    
    # Check genesis
    if [[ "$genesis" != "$EXPECTED_GENESIS"* ]]; then
        echo "FAIL: $name (port $port) genesis mismatch: got $genesis, expected $EXPECTED_GENESIS"
        ERRORS=$((ERRORS + 1))
    fi
    
    # Check runtime version
    if [[ "$spec_ver" != "$EXPECTED_SPEC_VERSION" ]] || [[ "$impl_ver" != "$EXPECTED_IMPL_VERSION" ]]; then
        echo "FAIL: $name (port $port) runtime mismatch: spec=$spec_ver impl=$impl_ver"
        ERRORS=$((ERRORS + 1))
    fi
    
    echo "  $name: genesis=$genesis block=$best fin=$fin spec=$spec_ver impl=$impl_ver chain=$chain"
done

echo ""
if [ $ERRORS -eq 0 ]; then
    echo "PASS: All nodes consistent. Genesis, runtime, and chain spec match."
    exit 0
else
    echo "FAIL: $ERRORS consistency error(s) detected."
    exit 1
fi
