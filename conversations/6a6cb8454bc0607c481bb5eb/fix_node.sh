#!/bin/bash
echo "=== Stopping all verdis services ==="
for svc in verdis-val-1 verdis-val-2 verdis-val-3 verdis-val-4 verdis-val-5 verdis-rpc-1 verdis-rpc-2 verdis-boot-1 verdis-boot-2 verdis-rpc-filter; do
    systemctl stop $svc 2>/dev/null
    echo "Stopped $svc"
done
sleep 2

echo ""
echo "=== Purging chain data for all nodes ==="
for dir in boot-1 boot-2 val-1 val-2 val-3 val-4 val-5 rpc-1 rpc-2; do
    DIR="/opt/verdis-data/$dir/chains"
    if [ -d "$DIR" ]; then
        rm -rf "$DIR"
        echo "Purged $dir"
    fi
done
sleep 1

echo ""
echo "=== Starting boot nodes first ==="
systemctl start verdis-boot-1
systemctl start verdis-boot-2
sleep 5
echo "Boot nodes started"
systemctl is-active verdis-boot-1
systemctl is-active verdis-boot-2

echo ""
echo "=== Starting validators ==="
for svc in verdis-val-1 verdis-val-2 verdis-val-3 verdis-val-4 verdis-val-5; do
    systemctl start $svc
    echo "Started $svc"
done
sleep 5

echo ""
echo "=== Starting RPC nodes ==="
systemctl start verdis-rpc-1
systemctl start verdis-rpc-2
systemctl start verdis-rpc-filter
sleep 3

echo ""
echo "=== Waiting for block production ==="
sleep 10

echo ""
echo "=== Health check ==="
curl -sk -X POST https://localhost/rpc -H "Host: verdischain.com" -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"system_health","params":[],"id":1}' 2>&1

echo ""
echo "=== Block height ==="
curl -sk -X POST https://localhost/rpc -H "Host: verdischain.com" -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"chain_getHeader","params":[],"id":1}' 2>&1 | python3 -c "import sys,json; d=json.load(sys.stdin); print('Block #'+str(int(d.get('result',{}).get('number','0x0'),16)))" 2>/dev/null

echo ""
echo "=== Wait 15s and check again ==="
sleep 15
curl -sk -X POST https://localhost/rpc -H "Host: verdischain.com" -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"chain_getHeader","params":[],"id":1}' 2>&1 | python3 -c "import sys,json; d=json.load(sys.stdin); print('Block #'+str(int(d.get('result',{}).get('number','0x0'),16)))" 2>/dev/null

echo ""
echo "=== Validator logs ==="
tail -10 /var/log/verdis-val-1.log 2>/dev/null
