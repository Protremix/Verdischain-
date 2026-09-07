#!/usr/bin/env bash
# Final end-to-end verification after switching the public site from testnet to
# mainnet. Everything here must be read live - no assumptions.

MAIN=0x2284393d11797c1a06e8def6a48a79f9d8d7539c5386d9973fce852852817c8e
TEST=0xf72f1241cb7457a2af62498fc5cadbc79dc442cfc52a17aa7560ba8ec0ec8edb
KEY=$HOME/.ssh/id_ed25519
SSH="ssh -o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=12 -i $KEY"

echo "=== 1. PUBLIC ENDPOINTS: which chain? ==="
for u in https://rpc.verdischain.com https://verdischain.com/rpc; do
  g=$(timeout 15 curl -s -m 12 -H 'Content-Type: application/json' \
      -d '{"jsonrpc":"2.0","id":1,"method":"chain_getBlockHash","params":[0]}' "$u" 2>/dev/null | grep -oP 'result":"\K[^"]+')
  b=$(timeout 15 curl -s -m 12 -H 'Content-Type: application/json' \
      -d '{"jsonrpc":"2.0","id":1,"method":"chain_getHeader","params":[]}' "$u" 2>/dev/null | grep -oP '"number":"\K0x[0-9a-f]+')
  case "$g" in "$MAIN") t="MAINNET  OK" ;; "$TEST") t="TESTNET  BAD" ;; *) t="? ${g:0:16}" ;; esac
  printf "  %-32s %-13s best=%s\n" "$u" "$t" "$( [ -n "$b" ] && printf %d "$b" )"
done

echo
echo "=== 2. unsafe RPC must be refused publicly ==="
for m in author_rotateKeys author_insertKey system_addReservedPeer; do
  r=$(timeout 12 curl -s -m 10 -H 'Content-Type: application/json' \
      -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"$m\",\"params\":[]}" https://rpc.verdischain.com 2>/dev/null)
  echo "$r" | grep -q 'unsafe\|not found\|-32601' && printf "  %-26s refused OK\n" "$m" \
    || printf "  %-26s !! ALLOWED: %s\n" "$m" "$(echo "$r" | head -c 80)"
done

echo
echo "=== 3. mainnet consensus untouched by today's work ==="
$SSH root@185.84.224.91 'R(){ curl -s -m 8 -H "Content-Type: application/json" -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"$1\",\"params\":$2}" http://localhost:9944; }
B=$(R chain_getHeader "[]"|grep -oP "\"number\":\"\K0x[0-9a-f]+")
FH=$(R chain_getFinalizedHead "[]"|grep -oP "0x[0-9a-f]{64}")
F=$(R chain_getHeader "[\"$FH\"]"|grep -oP "\"number\":\"\K0x[0-9a-f]+")
A=$(R state_call "[\"GrandpaApi_grandpa_authorities\",\"0x\"]"|grep -oP "result\":\"0x\K[0-9a-f]+")
echo "  best=$((B)) finalized=$((F)) lag=$(( $((B)) - $((F)) )) authorities=$(( ${#A} / 80 )) peers=$(R system_health "[]"|grep -oP "\"peers\":\K[0-9]+")"'

echo
echo "=== 4. all 15 validators + the new public node ==="
T=0
for ip in 185.84.224.91 195.154.80.40 213.136.78.63; do
  n=$($SSH "root@$ip" "systemctl list-units 'verdis-validator*' --state=active --no-legend --no-pager 2>/dev/null | wc -l")
  T=$(( T + ${n:-0} ))
  printf "  %-16s validators=%s\n" "$ip" "${n:-?}"
done
echo "  TOTAL validators: $T (threshold 15)"
$SSH root@185.84.224.91 'echo "  public RPC node: $(systemctl is-active verdis-public-rpc), roles=$(curl -s -m 6 -H "Content-Type: application/json" -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"system_nodeRoles\",\"params\":[]}" http://localhost:9955 | grep -oP "result\":\K.*" | head -c 12), keys=$(find /data/mainnet-public-rpc -type f -path "*keystore*" 2>/dev/null | wc -l)"'
$SSH root@91.98.160.145 'echo "  tunnel: $(systemctl is-active verdis-mainnet-tunnel)  ws-filter: $(systemctl is-active verdis-ws-filter)"'

echo
echo "=== 5. authority RPC still closed to the internet ==="
X=""
for ip in 185.84.224.91 195.154.80.40 213.136.78.63; do
  for p in 9933 9944 9945 9955; do
    r=$(timeout 6 curl -s -m 5 -H 'Content-Type: application/json' \
        -d '{"jsonrpc":"2.0","id":1,"method":"system_nodeRoles","params":[]}' "http://$ip:$p" 2>/dev/null)
    [ -n "$r" ] && X="$X $ip:$p"
  done
done
[ -n "$X" ] && echo "  !! EXPOSED:$X" || echo "  all closed OK (incl. the new 9955)"

echo
echo "=== 6. website ==="
for d in verdischain.com explorer.verdischain.com wallet.verdischain.com dex.verdischain.com \
         faucet.verdischain.com docs.verdischain.com api.verdischain.com rpc.verdischain.com \
         validators.verdischain.com developers.verdischain.com ws.verdischain.com blog.verdischain.com; do
  printf "  %-34s %s\n" "$d" "$(timeout 12 curl -s -o /dev/null -w '%{http_code}' "https://$d")"
done

echo
echo "=== 7. equivocation in the last 15 min (the new node must not cause any) ==="
E=0
for ip in 185.84.224.91 195.154.80.40 213.136.78.63; do
  e=$($SSH "root@$ip" "journalctl -u 'verdis*' --since '15 min ago' --no-pager 2>/dev/null | grep -ci equivocat")
  E=$(( E + ${e:-0} ))
done
echo "  total: $E"
