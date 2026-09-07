#!/usr/bin/env bash
# Count mainnet validators on a host by INSPECTING ExecStart, not by unit-name globs.
#
# Why: unit names drifted as work progressed - verdis-validator.service,
# verdis-validator-v18, verdis-v16b, verdis-v13m. Any glob list is one rename away
# from undercounting, and an undercount fakes a CRIT ("single host can halt finality")
# while the chain is perfectly healthy. A false alarm trains you to ignore alerts.
#
# Ground truth: a unit is a mainnet validator iff its effective ExecStart contains
# --validator. The public RPC node has no such flag, so it is correctly excluded.
#
# Usage: count_validators_on.sh <host>   -> prints a single integer
set -uo pipefail
H="${1:?host required}"
KEY=$HOME/.ssh/id_ed25519

ssh -o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=15 -i "$KEY" \
    "root@$H" 'bash -s' <<'REMOTE' 2>/dev/null
c=0
for u in $(systemctl list-units 'verdis*' --state=active --no-legend --no-pager 2>/dev/null | awk '{print $1}' | grep '\.service$'); do
  E=$(systemctl show -p ExecStart --value "$u" 2>/dev/null | grep -oP 'argv\[\]=\K[^;]+' | tail -1)
  case "$E" in *--validator*) c=$((c+1)) ;; esac
done
echo "$c"
REMOTE
