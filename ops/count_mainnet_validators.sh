#!/usr/bin/env bash
# Count MAINNET validators on a host. Two filters are required, not one.
#
# Filter 1: ExecStart contains --validator (excludes the public RPC full node).
# Filter 2: the node's own RPC reports the MAINNET genesis.
#
# Filter 2 is not optional: 5.223.77.19 also runs verdis-node, a TESTNET validator
# (Dave, genesis 0xf72f1241). Counting by --validator alone reported 22 of 21, and an
# inflated count is as dangerous as a deflated one - it would hide a real outage.
#
# Unit-name globs were tried and rejected: names drifted through
# verdis-validator.service, verdis-validator-v18, verdis-v16b, verdis-v13m, so any
# glob list silently undercounts after the next rename.
#
# Usage: count_mainnet_validators.sh <host>  -> single integer
set -uo pipefail
H="${1:?host required}"
KEY=$HOME/.ssh/id_ed25519
MAIN_GEN=0x2284393d11797c1a06e8def6a48a79f9d8d7539c5386d9973fce852852817c8e

ssh -o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=15 -i "$KEY" \
    "root@$H" "MAIN_GEN=$MAIN_GEN bash -s" <<'REMOTE' 2>/dev/null
c=0
for u in $(systemctl list-units 'verdis*' --state=active --no-legend --no-pager 2>/dev/null | awk '{print $1}' | grep '\.service$'); do
  E=$(systemctl show -p ExecStart --value "$u" 2>/dev/null | grep -oP 'argv\[\]=\K[^;]+' | tail -1)
  case "$E" in *--validator*) ;; *) continue ;; esac
  rpc=$(echo "$E" | grep -oP '(?<=--rpc-port[= ])[0-9]+' | head -1)
  # A unit may omit --rpc-port and use the default. Probe the default too, otherwise
  # that validator is invisible and the count comes out one short (20 of 21).
  cands="${rpc:-} 9933 9944"
  g=""
  for p in $cands; do
    [ -z "$p" ] && continue
    g=$(curl -s -m 6 -H 'Content-Type: application/json' \
        -d '{"jsonrpc":"2.0","id":1,"method":"chain_getBlockHash","params":[0]}' \
        "http://localhost:$p" 2>/dev/null | grep -oP 'result":"\K[^"]+')
    [ -n "$g" ] && break
  done
  [ "$g" = "$MAIN_GEN" ] && c=$((c+1))
done
echo "$c"
REMOTE
