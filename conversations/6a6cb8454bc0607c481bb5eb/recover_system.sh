#!/usr/bin/env bash
# Comprehensive Verdis Chain system health check and fix script
# Run this immediately after server comes back online

echo "=== VERDIS CHAIN SYSTEM RECOVERY ==="
echo "Time: $(date)"

# 1. Check system resources
echo ""
echo "=== SYSTEM RESOURCES ==="
free -h
df -h /
echo "Load: $(cat /proc/loadavg)"

# 2. Clear logs if disk is full
USED=$(df / | tail -1 | awk '{print $5}' | tr -d '%')
if [ "$USED" -gt 90 ]; then
    echo "DISK ALMOST FULL ($USED%) — cleaning logs..."
    journalctl --vacuum-size=200M
    find /var/log -name "*.gz" -mtime +7 -delete
    find /opt/verdis-chain-rust -name "*.log" -size +100M -truncate -s 0
fi

# 3. Restart all services in order
echo ""
echo "=== RESTARTING SERVICES ==="
systemctl restart verdis-node
sleep 5
systemctl restart verdis-val-2 verdis-val-3 verdis-val-4 verdis-val-5 verdis-node3
sleep 3
systemctl restart verdis-tx-relay
sleep 2
systemctl restart verdis-api verdis-faucet verdis-governance
sleep 2
systemctl restart verdis-health-monitor verdis-rpc-filter verdis-validator-monitor verdis-finality-monitor
sleep 2
systemctl restart verdis-txbot verdis-price-collector verdis-soak-test

echo ""
echo "=== SERVICE STATUS ==="
for svc in verdis-node verdis-node3 verdis-val-2 verdis-val-3 verdis-val-4 verdis-val-5 verdis-tx-relay verdis-api verdis-faucet verdis-governance verdis-health-monitor verdis-rpc-filter verdis-txbot; do
    status=$(systemctl is-active $svc 2>/dev/null)
    echo "  $svc: $status"
done

# 4. Wait for node to sync
echo ""
echo "=== WAITING FOR NODE SYNC ==="
for i in $(seq 1 30); do
    HEALTH=$(curl -s -X POST http://127.0.0.1:9933 -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","method":"system_health","params":[],"id":1}' 2>/dev/null)
    if [ -n "$HEALTH" ]; then
        PEERS=$(echo $HEALTH | python3 -c 'import sys,json;print(json.load(sys.stdin)["result"]["peers"])' 2>/dev/null)
        SYNCING=$(echo $HEALTH | python3 -c 'import sys,json;print(json.load(sys.stdin)["result"]["isSyncing"])' 2>/dev/null)
        echo "  Peers: $PEERS, Syncing: $SYNCING"
        if [ "$SYNCING" = "False" ] && [ "$PEERS" -gt 0 ]; then
            echo "  Node is ready!"
            break
        fi
    else
        echo "  Waiting for node... ($i/30)"
    fi
    sleep 2
done

# 5. Verify chain state
echo ""
echo "=== CHAIN STATE ==="
curl -s -X POST http://127.0.0.1:9933 -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","method":"chain_getHeader","params":[],"id":1}' | python3 -c '
import sys,json
d=json.load(sys.stdin)
h=d["result"]
print(f"Block: #{h[\"number\"]}")
print(f"Hash: {h[\"hash\"][:20]}...")
' 2>/dev/null

# 6. Check TX Relay
echo ""
echo "=== TX RELAY ==="
curl -s http://127.0.0.1:5001/health | python3 -c 'import sys,json;d=json.load(sys.stdin);print(f"Status: {d[\"data\"][\"status\"]}, v{d[\"data\"][\"version\"]}")' 2>/dev/null

# 7. Test balance query
echo ""
echo "=== BALANCE TEST ==="
curl -s -X POST http://127.0.0.1:5001/ -H 'Content-Type: application/json' -d '{"action":"balance","address":"5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY"}' | python3 -c 'import sys,json;d=json.load(sys.stdin);print(f"Alice balance: {d[\"data\"][\"balance\"]/1e9:.4f} VRDX")' 2>/dev/null

# 8. Check validators
echo ""
echo "=== VALIDATORS ==="
curl -s -X POST http://127.0.0.1:9933 -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","method":"dpos_activeValidators","params":[],"id":1}' | python3 -c 'import sys,json;d=json.load(sys.stdin);print(f"Active validators: {len(d[\"result\"])}")' 2>/dev/null

# 9. Check DEX pools
echo ""
echo "=== DEX POOLS ==="
curl -s -X POST http://127.0.0.1:9933 -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","method":"amm_dex_getPoolCount","params":[],"id":1}' | python3 -c 'import sys,json;d=json.load(sys.stdin);print(f"DEX pools: {d[\"result\"]}")' 2>/dev/null

# 10. Check web pages
echo ""
echo "=== WEB PAGES ==="
ok=0; fail=0
for page in / /explorer/ /dex/ /whitepaper/ /wallet/ /sale/ /tokenomics/ /faucet/ /validators/ /eco/ /docs/ /transactions/ /governance/ /status/; do
    code=$(curl -s -o /dev/null -w '%{http_code}' https://verdischain.com$page 2>/dev/null)
    if [ "$code" = "200" ]; then ok=$((ok+1)); else fail=$((fail+1)); echo "  FAIL: $page -> $code"; fi
done
echo "Pages: $ok OK, $fail FAIL"

echo ""
echo "=== RECOVERY COMPLETE ==="
