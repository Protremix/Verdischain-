#!/usr/bin/env bash
# `location /rpc` in verdischain-com.conf hardcodes proxy_pass http://127.0.0.1:9950
# (the testnet node) instead of using the substrate_rpc upstream, so switching the
# upstream did not affect it. This is the endpoint the JS bundles call 386 times.
#
# Point it at the mainnet tunnel (127.0.0.1:9960). Backup + nginx -t + auto-restore.

set -uo pipefail
KEY=$HOME/.ssh/id_ed25519
MAIN_GEN=0x2284393d11797c1a06e8def6a48a79f9d8d7539c5386d9973fce852852817c8e
TEST_GEN=0xf72f1241cb7457a2af62498fc5cadbc79dc442cfc52a17aa7560ba8ec0ec8edb

ssh -o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=15 -i "$KEY" \
    root@91.98.160.145 'bash -s' <<'REMOTE' 2>&1
set -uo pipefail
F=/etc/nginx/sites-enabled/verdischain-com.conf
B="$F.bak-$(date -u +%Y%m%d-%H%M%S)"
cp -a "$F" "$B"
echo "  backup: $B"

echo "  --- all 9950 references ---"
grep -n '9950' "$F" | sed 's/^/    /'

# only inside the /rpc location, swap the port. Use python for precision.
python3 - "$F" <<'PY'
import sys, re
p = sys.argv[1]
lines = open(p).read().split('\n')
out, depth, inrpc, changed = [], 0, False, 0
for ln in lines:
    if re.match(r'\s*location\s+/rpc\s*\{', ln):
        inrpc, depth = True, 1
        out.append(ln); continue
    if inrpc:
        depth += ln.count('{') - ln.count('}')
        if 'proxy_pass' in ln and '9950' in ln:
            out.append(ln.replace('9950', '9960') + '  # MAINNET (was 9950 = testnet)')
            changed += 1
            if depth <= 0: inrpc = False
            continue
        if depth <= 0: inrpc = False
    out.append(ln)
open(p, 'w').write('\n'.join(out))
print(f"  proxy_pass lines changed inside /rpc: {changed}")
PY

grep -n '996[0-9]\|9950' "$F" | sed 's/^/    now: /'

if nginx -t 2>&1 | grep -q successful; then
  systemctl reload nginx
  echo "  nginx reloaded OK"
else
  cp -a "$B" "$F"; nginx -t 2>&1 | tail -3
  echo "  !! reverted"; exit 1
fi
REMOTE

echo
echo "=== public endpoints now ==="
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
  case "$g" in "$MAIN_GEN") t="MAINNET  OK" ;; "$TEST_GEN") t="still TESTNET" ;; *) t="? ${g:0:20}" ;; esac
  printf "  %-32s %-14s %-16s best=%s\n" "$u" "$t" "${c:-?}" "$( [ -n "$b" ] && printf %d "$b" )"
done

echo
echo "=== unsafe methods must be refused through the public endpoint ==="
timeout 12 curl -s -m 10 -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"author_rotateKeys","params":[]}' \
  https://rpc.verdischain.com | head -c 140
echo

echo
echo "=== site health ==="
for d in verdischain.com explorer.verdischain.com wallet.verdischain.com dex.verdischain.com \
         faucet.verdischain.com api.verdischain.com validators.verdischain.com blog.verdischain.com; do
  printf "  %-32s %s\n" "$d" "$(timeout 12 curl -s -o /dev/null -w '%{http_code}' "https://$d")"
done
