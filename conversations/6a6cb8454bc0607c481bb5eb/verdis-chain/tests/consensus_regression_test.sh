#!/bin/bash
# Regression test: Genesis Consistency
# Ensures all nodes converge to the same genesis, runtime, and chain.
# This test prevents the Aug 13 genesis split (0x728d vs 0x9465) from recurring.

set -euo pipefail

NODES=(9933 9935 9944 9946 9947)
RESULTS_FILE=/tmp/consensus_test_results.txt
> $RESULTS_FILE

echo "=== Genesis Consistency Regression Test ==="

# Collect genesis hash from all nodes
for port in "${NODES[@]}"; do
    genesis=$(curl -s -m 5 -X POST http://127.0.0.1:$port -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","method":"chain_getBlockHash","params":[0],"id":1}' 2>/dev/null | python3 -c 'import sys,json; print(json.load(sys.stdin).get("result","ERROR"))' 2>/dev/null || echo "NO_RESPONSE")
    echo "$port:$genesis" >> $RESULTS_FILE
done

# Verify all genesis hashes are identical
UNIQUE_GENESIS=$(cut -d: -f2 $RESULTS_FILE | sort -u | wc -l)
if [ $UNIQUE_GENESIS -ne 1 ]; then
    echo "FAIL: Multiple genesis hashes detected ($UNIQUE_GENESIS unique values)"
    cat $RESULTS_FILE
    exit 1
fi

# Collect runtime version from all nodes
> $RESULTS_FILE
for port in "${NODES[@]}"; do
    rt=$(curl -s -m 5 -X POST http://127.0.0.1:$port -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","method":"state_getRuntimeVersion","params":[],"id":1}' 2>/dev/null | python3 -c 'import sys,json; r=json.load(sys.stdin).get("result",{}); print(f"{r.get("specVersion",0)}_{r.get("implVersion",0)}")' 2>/dev/null || echo "ERROR")
    echo "$port:$rt" >> $RESULTS_FILE
done

UNIQUE_RT=$(cut -d: -f2 $RESULTS_FILE | sort -u | wc -l)
if [ $UNIQUE_RT -ne 1 ]; then
    echo "FAIL: Multiple runtime versions detected"
    cat $RESULTS_FILE
    exit 1
fi

# Collect finalized head from all nodes
> $RESULTS_FILE
for port in "${NODES[@]}"; do
    fin=$(curl -s -m 5 -X POST http://127.0.0.1:$port -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","method":"chain_getFinalizedHead","params":[],"id":1}' 2>/dev/null | python3 -c 'import sys,json; print(json.load(sys.stdin).get("result","ERROR"))' 2>/dev/null || echo "NO_RESPONSE")
    echo "$port:$fin" >> $RESULTS_FILE
done

UNIQUE_FIN=$(cut -d: -f2 $RESULTS_FILE | sort -u | wc -l)
if [ $UNIQUE_FIN -ne 1 ]; then
    echo "WARN: Finalized heads differ (may converge shortly) - $UNIQUE_FIN unique values"
    cat $RESULTS_FILE
fi

echo "PASS: All nodes share identical genesis hash and runtime version."
exit 0
