#!/usr/bin/env bash
# Which chain does the PUBLIC website actually talk to?
#
# Just discovered: https://rpc.verdischain.com returns genesis 0xf72f1241... which is
# the TESTNET, not the mainnet (0x2284393d...). If explorer/wallet/dex all read that
# endpoint, then everything a visitor sees - balances, blocks, transactions - comes
# from a chain that is 72 000 blocks behind on finality and secured by public dev keys
# (Alice..Ferdie). That is a far bigger finding than anything in the audit so far:
# users could be sending real value against a test chain.
#
# Establish the facts before proposing any change. Read-only.

MAIN=0x2284393d11797c1a06e8def6a48a79f9d8d7539c5386d9973fce852852817c8e
TEST=0xf72f1241cb7457a2af62498fc5cadbc79dc442cfc52a17aa7560ba8ec0ec8edb

echo "=== public RPC/WS endpoints ==="
for url in https://rpc.verdischain.com https://api.verdischain.com https://ws.verdischain.com; do
  g=$(timeout 12 curl -s -m 10 -H 'Content-Type: application/json' \
      -d '{"jsonrpc":"2.0","id":1,"method":"chain_getBlockHash","params":[0]}' "$url" 2>/dev/null \
      | grep -oP 'result":"\K[^"]+')
  c=$(timeout 12 curl -s -m 10 -H 'Content-Type: application/json' \
      -d '{"jsonrpc":"2.0","id":1,"method":"system_chain","params":[]}' "$url" 2>/dev/null \
      | grep -oP 'result":"\K[^"]+')
  b=$(timeout 12 curl -s -m 10 -H 'Content-Type: application/json' \
      -d '{"jsonrpc":"2.0","id":1,"method":"chain_getHeader","params":[]}' "$url" 2>/dev/null \
      | grep -oP '"number":"\K0x[0-9a-f]+')
  case "$g" in
    "$MAIN") tag="MAINNET" ;;
    "$TEST") tag="*** TESTNET ***" ;;
    "")      tag="no answer" ;;
    *)       tag="unknown $g" ;;
  esac
  printf "  %-32s %-16s chain=%-16s best=%s\n" "$url" "$tag" "${c:-?}" "$( [ -n "$b" ] && printf %d "$b" )"
done

echo
echo "=== which RPC URL is baked into the web bundles? ==="
KEY=$HOME/.ssh/id_ed25519
ssh -o BatchMode=yes -o StrictHostKeyChecking=no -i "$KEY" root@91.98.160.145 'bash -s' <<'REMOTE'
for d in /opt/verdis-repo/dist /opt/verdis-repo /var/www; do
  [ -d "$d" ] || continue
  echo "  --- $d ---"
  grep -rhoP '(wss?|https?)://[a-z0-9.-]*verdischain\.com[a-z0-9/._-]*' "$d" 2>/dev/null \
    | sort | uniq -c | sort -rn | head -8 | sed 's/^/    /'
done
echo "  --- nginx upstreams ---"
grep -h 'upstream' /etc/nginx/conf.d/upstreams.conf 2>/dev/null | sed 's/^/    /'
echo "  --- what listens on those ports ---"
for p in 9933 9944 9949 9950; do
  c=$(curl -s -m 5 -H 'Content-Type: application/json' \
      -d '{"jsonrpc":"2.0","id":1,"method":"system_chain","params":[]}' \
      "http://localhost:$p" 2>/dev/null | grep -oP 'result":"\K[^"]+')
  g=$(curl -s -m 5 -H 'Content-Type: application/json' \
      -d '{"jsonrpc":"2.0","id":1,"method":"chain_getBlockHash","params":[0]}' \
      "http://localhost:$p" 2>/dev/null | grep -oP 'result":"\K[^"]{20}')
  printf "    :%-6s %-18s %s\n" "$p" "${c:-silent}" "${g:-}"
done
REMOTE

echo
echo "=== is the mainnet reachable from the web host at all? ==="
for ip in 185.84.224.91 195.154.80.40 213.136.78.63; do
  printf "  %-16s p2p 30333: " "$ip"
  timeout 6 bash -c "echo > /dev/tcp/$ip/30333" 2>/dev/null && echo reachable || echo unreachable
done
