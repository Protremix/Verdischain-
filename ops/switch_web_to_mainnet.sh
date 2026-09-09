#!/usr/bin/env bash
# Switch nginx upstream substrate_rpc from the testnet node (127.0.0.1:9950) to the
# mainnet tunnel (127.0.0.1:9960), verified reversible.
#
# The tunnel already answers "Verdis Mainnet" / genesis 0x2284393d on the web host.
# Frontend URLs do not change, so no rebuild is needed.
#
# substrate_ws is left alone for now: it points at :9944 which is silent on the web
# host, and the WS path goes through verdis-ws-filter. Changing RPC first keeps the
# blast radius to one line, and we verify the site before touching WS.

set -uo pipefail
KEY=$HOME/.ssh/id_ed25519
SSH="ssh -o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=15 -i $KEY"
WEB=91.98.160.145
MAIN_GEN=0x2284393d11797c1a06e8def6a48a79f9d8d7539c5386d9973fce852852817c8e
TEST_GEN=0xf72f1241cb7457a2af62498fc5cadbc79dc442cfc52a17aa7560ba8ec0ec8edb

echo "=== BEFORE ==="
for u in https://rpc.verdischain.com https://verdischain.com/rpc; do
  g=$(timeout 12 curl -s -m 10 -H 'Content-Type: application/json' \
      -d '{"jsonrpc":"2.0","id":1,"method":"chain_getBlockHash","params":[0]}' "$u" 2>/dev/null \
      | grep -oP 'result":"\K[^"]+')
  case "$g" in "$MAIN_GEN") t=MAINNET ;; "$TEST_GEN") t=TESTNET ;; *) t="?" ;; esac
  printf "  %-32s %s\n" "$u" "$t"
done

echo
echo "=== switching upstream ==="
$SSH "root@$WEB" 'bash -s' <<'REMOTE' 2>&1
set -uo pipefail
F=/etc/nginx/conf.d/upstreams.conf
cp -a "$F" "$F.bak-$(date -u +%Y%m%d-%H%M%S)"
echo "  backup: $(ls -1t $F.bak-* | head -1)"

grep -n 'substrate_rpc' "$F" | sed 's/^/  before: /'

# comment the old line, add the new one right after it
python3 - "$F" <<'PY'
import re, sys
p = sys.argv[1]
s = open(p).read()
old = re.search(r'^upstream substrate_rpc.*$', s, re.M)
if not old:
    print("  ERROR: substrate_rpc upstream not found"); sys.exit(1)
line = old.group(0)
if '9960' in line:
    print("  already pointing at 9960"); sys.exit(0)
new = ("# TESTNET (was): " + line + "\n"
       "upstream substrate_rpc     { server 127.0.0.1:9960; keepalive 32; }"
       "  # MAINNET via tunnel to 185.84.224.91:9955\n")
s = s.replace(line + "\n", new)
open(p, 'w').write(s)
print("  rewritten")
PY

grep -n 'substrate_rpc' "$F" | sed 's/^/  after: /'

if nginx -t 2>&1 | grep -q 'successful'; then
  systemctl reload nginx
  echo "  nginx reloaded OK"
else
  echo "  !! nginx -t FAILED - restoring"
  cp -a "$(ls -1t $F.bak-* | head -1)" "$F"
  nginx -t 2>&1 | tail -2
  exit 1
fi
REMOTE

echo
echo "=== AFTER (public endpoints) ==="
sleep 5
for u in https://rpc.verdischain.com https://verdischain.com/rpc; do
  g=$(timeout 15 curl -s -m 12 -H 'Content-Type: application/json' \
      -d '{"jsonrpc":"2.0","id":1,"method":"chain_getBlockHash","params":[0]}' "$u" 2>/dev/null \
      | grep -oP 'result":"\K[^"]+')
  c=$(timeout 15 curl -s -m 12 -H 'Content-Type: application/json' \
      -d '{"jsonrpc":"2.0","id":1,"method":"system_chain","params":[]}' "$u" 2>/dev/null \
      | grep -oP 'result":"\K[^"]+')
  b=$(timeout 15 curl -s -m 12 -H 'Content-Type: application/json' \
      -d '{"jsonrpc":"2.0","id":1,"method":"chain_getHeader","params":[]}' "$u" 2>/dev/null \
      | grep -oP '"number":"\K0x[0-9a-f]+')
  case "$g" in "$MAIN_GEN") t="MAINNET  OK" ;; "$TEST_GEN") t="still TESTNET" ;; *) t="? $g" ;; esac
  printf "  %-32s %-14s chain=%-16s best=%s\n" "$u" "$t" "${c:-?}" "$( [ -n "$b" ] && printf %d "$b" )"
done

echo
echo "=== site still serves 200? ==="
for d in verdischain.com explorer.verdischain.com wallet.verdischain.com dex.verdischain.com faucet.verdischain.com; do
  printf "  %-32s %s\n" "$d" "$(timeout 12 curl -s -o /dev/null -w '%{http_code}' "https://$d")"
done
