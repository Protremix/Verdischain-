#!/usr/bin/env bash
# Fix and verify the mainnet public RPC node.
# Error was mine: `--rpc-external=false` is a flag, not a key=value option, so the
# node exited with status=2/INVALIDARGUMENT. Removing the line is correct because
# Substrate binds RPC to 127.0.0.1 by default - which is exactly what we want.

set -uo pipefail
KEY=$HOME/.ssh/id_ed25519
ssh -o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=15 -i "$KEY" \
    root@185.84.224.91 'bash -s' <<'REMOTE' 2>&1
set -uo pipefail
sed -i '/--rpc-external=false/d' /etc/systemd/system/verdis-public-rpc.service
systemctl daemon-reload
systemctl reset-failed verdis-public-rpc 2>/dev/null
systemctl restart verdis-public-rpc

for i in $(seq 1 30); do
  sleep 5
  st=$(systemctl is-active verdis-public-rpc)
  [ "$st" = "active" ] && break
  [ "$st" = "failed" ] && break
done
echo "  is-active: $(systemctl is-active verdis-public-rpc)"

if [ "$(systemctl is-active verdis-public-rpc)" != "active" ]; then
  journalctl -u verdis-public-rpc -n 8 --no-pager | tail -8 | cut -c1-170
  exit 1
fi

sleep 25
RPC=9955
q() { curl -s -m 8 -H 'Content-Type: application/json' \
      -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"$1\",\"params\":[]}" "http://localhost:$RPC"; }

echo "  --- verification ---"
echo "    chain:   $(q system_chain | grep -oP 'result":"\K[^"]+')"
echo "    genesis: $(curl -s -m 8 -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","id":1,"method":"chain_getBlockHash","params":[0]}' http://localhost:$RPC | grep -oP 'result":"\K[^"]+')"
echo "    roles:   $(q system_nodeRoles | grep -oP 'result":\K.*' | head -c 30)"
echo "    unsafe blocked? $(q author_rotateKeys | head -c 110)"
H=$(q system_health)
echo "    peers=$(echo "$H" | grep -oP '"peers":\K[0-9]+') syncing=$(echo "$H" | grep -oP '"isSyncing":\K(true|false)')"
B=$(curl -s -m 8 -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","id":1,"method":"chain_getHeader","params":[]}' http://localhost:$RPC | grep -oP '"number":"\K0x[0-9a-f]+')
[ -n "$B" ] && echo "    best=$((B))"
echo "    keystore files: $(find /data/mainnet-public-rpc -type f -path '*keystore*' 2>/dev/null | wc -l)  (must be 0)"
echo "    listens on: $(ss -tln | grep ':9955' | awk '{print $4}' | tr '\n' ' ')"

echo "  --- the 3 validators here must be untouched ---"
systemctl list-units 'verdis-validator*' --state=active --no-legend --no-pager | awk '{print "    "$1}'
REMOTE
