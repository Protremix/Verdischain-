#!/usr/bin/env bash
# Prove the watchdog actually recovers a dead validator.
#
# A watchdog that has never been tested is not a safety net. Test it for real: stop
# ONE validator on the host that carries the FEWEST authorities (185.84.224.91, 3 of
# 21), then watch the timer bring it back without human action.
#
# Risk accepted: while that node is down we have 14 of 15, so finality pauses for up
# to ~2 minutes (timer interval) plus node start time. Blocks keep being produced and
# finality resumes on recovery - exactly the scenario the watchdog exists for, so it
# is better to see it now, deliberately, than at 3am by surprise.
#
# Chosen victim: verdis-validator-v18 on 185.84.224.91.

set -uo pipefail
KEY=$HOME/.ssh/id_ed25519
SSH="ssh -o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=15 -i $KEY"
H=185.84.224.91
U=verdis-validator-v18

fin() {
  $SSH root@$H 'R(){ curl -s -m 8 -H "Content-Type: application/json" -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"$1\",\"params\":$2}" http://localhost:9944; };
  B=$(R chain_getHeader "[]"|grep -oP "\"number\":\"\K0x[0-9a-f]+")
  FH=$(R chain_getFinalizedHead "[]"|grep -oP "0x[0-9a-f]{64}")
  F=$(R chain_getHeader "[\"$FH\"]"|grep -oP "\"number\":\"\K0x[0-9a-f]+")
  echo "$((B)) $((F))"' 2>/dev/null
}

read -r B0 F0 <<<"$(fin)"
echo "=== baseline: best=$B0 finalized=$F0 lag=$(( B0 - F0 )) ==="

echo
echo "=== stopping $U deliberately (simulating a crash) ==="
$SSH root@$H "systemctl stop $U; echo '  is-active: '\$(systemctl is-active $U)"

echo
echo "=== watching for the watchdog to notice and recover (timer runs every 2 min) ==="
recovered=no
for i in $(seq 1 20); do
  sleep 20
  st=$($SSH root@$H "systemctl is-active $U" 2>/dev/null)
  read -r B F <<<"$(fin)"
  printf "  [%s] %s=%-11s best=%s finalized=%s lag=%s\n" \
    "$(date -u +%H:%M:%S)" "$U" "$st" "$B" "$F" "$(( B - F ))"
  if [ "$st" = "active" ]; then recovered=yes; break; fi
done

echo
if [ "$recovered" = yes ]; then
  echo "=== WATCHDOG WORKS - node was restarted without human action ==="
else
  echo "=== WATCHDOG DID NOT RECOVER IT - starting manually ==="
  $SSH root@$H "systemctl reset-failed $U; systemctl start $U"
  sleep 30
  echo "  manual restart -> $($SSH root@$H "systemctl is-active $U")"
fi

echo
echo "=== watchdog log ==="
$SSH root@$H 'cat /var/log/verdis-watchdog.log 2>/dev/null | tail -8 | sed "s/^/  /"'

echo
echo "=== final state ==="
read -r B1 F1 <<<"$(fin)"
echo "  best=$B1 finalized=$F1 lag=$(( B1 - F1 ))"
echo "  finality advanced: $F0 -> $F1 ($(( F1 - F0 )) blocks)"
T=0
for ip in 185.84.224.91 195.154.80.40 213.136.78.63; do
  n=$($SSH "root@$ip" "systemctl list-units 'verdis-validator*' --state=active --no-legend --no-pager | wc -l")
  T=$(( T + ${n:-0} ))
done
echo "  validators active: $T / 15"
