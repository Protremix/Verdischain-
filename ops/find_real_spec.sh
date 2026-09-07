#!/usr/bin/env bash
# The public node came up with genesis 0x60488cb4... but the live mainnet is
# 0x2284393d... So /data/verdis-chain/chain-specs/mainnet-raw.json on 185.84.224.91
# is NOT the spec the running validators use - it is a different (probably older or
# regenerated) mainnet spec. Find the file whose genesis actually matches.
#
# Method: read the exact --chain path from each running validator, hash-compare the
# candidate spec files, and ask each validator's own RPC for its genesis.

KEY=$HOME/.ssh/id_ed25519
SSH="ssh -o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=15 -i $KEY"
WANT=0x2284393d11797c1a06e8def6a48a79f9d8d7539c5386d9973fce852852817c8e

for ip in 185.84.224.91 195.154.80.40 213.136.78.63; do
  echo "===================================================================="
  echo "$ip"
  echo "===================================================================="
  $SSH "root@$ip" 'bash -s' <<'REMOTE' 2>&1
echo "  --- exact --chain path + genesis per validator ---"
for u in $(systemctl list-units 'verdis-validator*' --state=active --no-legend --no-pager 2>/dev/null | awk '{print $1}'); do
  E=$(systemctl show -p ExecStart --value "$u" 2>/dev/null | grep -oP 'argv\[\]=\K[^;]+' | tail -1)
  spec=$(echo "$E" | grep -oP '(?<=--chain=)[^ ]+')
  rpc=$(echo "$E" | grep -oP '(?<=--rpc-port=)[0-9]+')
  g=""
  [ -n "$rpc" ] && g=$(curl -s -m 6 -H 'Content-Type: application/json' \
      -d '{"jsonrpc":"2.0","id":1,"method":"chain_getBlockHash","params":[0]}' \
      "http://localhost:$rpc" 2>/dev/null | grep -oP 'result":"\K[^"]+')
  printf "    %-26s spec=%s\n" "$u" "${spec:-?}"
  printf "    %-26s genesis=%s\n" "" "${g:-unreadable}"
done

echo "  --- all mainnet spec files on this host, with sha256 ---"
find / -maxdepth 7 -name '*mainnet*.json' -not -path '/proc/*' 2>/dev/null | while read -r f; do
  printf "    %-58s %s  %s bytes\n" "$f" "$(sha256sum "$f" | cut -c1-16)" "$(stat -c%s "$f")"
done
REMOTE
  echo
done

echo "===================================================================="
echo "WANTED genesis: $WANT"
echo "===================================================================="
