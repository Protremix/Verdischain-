#!/usr/bin/env bash
# Point the public RPC node at the spec that actually produces genesis 0x2284393d...
#
# Root cause of the wrong genesis: /data/verdis-chain/chain-specs/mainnet-raw.json is
# NOT the same file on every host.
#   213.136.78.63 : sha256 aca92919e13da10f, 2565313 bytes  <- the REAL mainnet spec
#                   (identical to /tmp/mainnet-raw-v13.json, matching the v13 name we
#                    knew from earlier notes)
#   185.84.224.91 : a different file under the same name -> genesis 0x60488cb4...
#
# The validators on HostKey nonetheless run the real chain because they were started
# with a DB already synced to it; the spec mismatch only bites a node syncing from
# scratch, which is exactly what the public node does.
#
# Fix: copy the verified spec from Contabo, hash-check it, wipe the public node's
# 0-block DB and restart. Validators are not touched.

set -uo pipefail
KEY=$HOME/.ssh/id_ed25519
SSH="ssh -o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=15 -i $KEY"
WANT_SHA=aca92919e13da10f
WANT_GEN=0x2284393d11797c1a06e8def6a48a79f9d8d7539c5386d9973fce852852817c8e
TMP="$LOCALAPPDATA/Temp/verdis-mainnet-spec.json"

echo "=== fetch the verified spec from Contabo ==="
scp -q -o BatchMode=yes -o StrictHostKeyChecking=no -i "$KEY" \
    root@213.136.78.63:/data/verdis-chain/chain-specs/mainnet-raw.json "$TMP"
got=$(sha256sum "$TMP" | tr -d '\\' | cut -c1-16)
echo "  local copy: $(stat -c%s "$TMP") bytes, sha256 $got"
if [ "$got" != "$WANT_SHA" ]; then echo "  HASH MISMATCH (want $WANT_SHA) - abort"; exit 1; fi
echo "  hash OK"

echo
echo "=== install as mainnet-raw-v13-verified.json on 185.84.224.91 ==="
scp -q -o BatchMode=yes -o StrictHostKeyChecking=no -i "$KEY" \
    "$TMP" root@185.84.224.91:/data/verdis-chain/chain-specs/mainnet-raw-v13-verified.json
$SSH root@185.84.224.91 'sha256sum /data/verdis-chain/chain-specs/mainnet-raw-v13-verified.json | cut -c1-16 | sed "s/^/  remote sha256: /"'

echo
echo "=== repoint the public node and resync from block 0 ==="
$SSH root@185.84.224.91 'bash -s' <<'REMOTE' 2>&1
set -uo pipefail
systemctl stop verdis-public-rpc
sed -i 's|--chain=/data/verdis-chain/chain-specs/mainnet-raw.json|--chain=/data/verdis-chain/chain-specs/mainnet-raw-v13-verified.json|' \
    /etc/systemd/system/verdis-public-rpc.service
grep -c 'mainnet-raw-v13-verified.json' /etc/systemd/system/verdis-public-rpc.service | sed 's/^/  spec lines updated: /'
# the DB holds the wrong genesis - it must go, but only this node's DB
rm -rf /data/mainnet-public-rpc/chains
systemctl daemon-reload
systemctl reset-failed verdis-public-rpc 2>/dev/null
systemctl start verdis-public-rpc

for i in $(seq 1 30); do
  sleep 5
  st=$(systemctl is-active verdis-public-rpc)
  [ "$st" = "active" ] && break
  [ "$st" = "failed" ] && break
done
echo "  is-active: $(systemctl is-active verdis-public-rpc)"
[ "$(systemctl is-active verdis-public-rpc)" != "active" ] && {
  journalctl -u verdis-public-rpc -n 8 --no-pager | tail -8 | cut -c1-170; exit 1; }

sleep 30
RPC=9955
G=$(curl -s -m 8 -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","id":1,"method":"chain_getBlockHash","params":[0]}' http://localhost:$RPC | grep -oP 'result":"\K[^"]+')
H=$(curl -s -m 8 -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","id":1,"method":"system_health","params":[]}' http://localhost:$RPC)
B=$(curl -s -m 8 -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","id":1,"method":"chain_getHeader","params":[]}' http://localhost:$RPC | grep -oP '"number":"\K0x[0-9a-f]+')
echo "  genesis: $G"
echo "  peers=$(echo "$H" | grep -oP '"peers":\K[0-9]+') syncing=$(echo "$H" | grep -oP '"isSyncing":\K(true|false)')"
[ -n "$B" ] && echo "  best=$((B))"
echo "  roles: $(curl -s -m 8 -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","id":1,"method":"system_nodeRoles","params":[]}' http://localhost:$RPC | grep -oP 'result":\K.*' | head -c 20)"
echo "  validators here: $(systemctl list-units 'verdis-validator*' --state=active --no-legend --no-pager | wc -l)"
REMOTE

echo
echo "=== expected genesis: $WANT_GEN ==="
rm -f "$TMP"
