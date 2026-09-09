#!/usr/bin/env bash
# Remove --unsafe-rpc-external / --rpc-methods=unsafe / --rpc-cors=all from ONE
# mainnet validator, restart it, and verify the chain never lost finality.
#
# Usage: harden_one_validator.sh <unit> <rpc_port>
#
# Why one at a time: these are live authorities on Verdis Mainnet (21 authorities,
# GRANDPA threshold 15). Restarting one is safe; restarting several at once is not.
# Firewall already blocks these ports externally - this closes the hole at the
# process level too, so a firewall flush or host migration cannot re-expose it.
#
# Rollback: rm the drop-in and `systemctl restart <unit>`.

set -uo pipefail
UNIT="${1:?unit name required}"
PORT="${2:?rpc port required}"
DROPIN="/etc/systemd/system/${UNIT}.service.d/90-safe-rpc.conf"

R() { curl -s -m 8 -H 'Content-Type: application/json' \
        -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"$1\",\"params\":$2}" http://localhost:9944; }
fin() {
  local fh
  fh=$(R chain_getFinalizedHead '[]' | grep -oP '0x[0-9a-f]{64}')
  [ -n "$fh" ] && R chain_getHeader "[\"$fh\"]" | grep -oP '"number":"\K0x[0-9a-f]+'
}
best() { R chain_getHeader '[]' | grep -oP '"number":"\K0x[0-9a-f]+'; }
dec() { [ -n "${1:-}" ] && printf '%d' "$1" 2>/dev/null || echo ""; }

echo "== target: $UNIT (rpc $PORT)"

OLD=$(systemctl show -p ExecStart --value "$UNIT")
BIN=$(echo "$OLD" | grep -oP '(?<=argv\[\]=)[^ ]+' | head -1)
[ -z "$BIN" ] && BIN=$(echo "$OLD" | grep -oP '(?<=path=)[^ ]+' | head -1)
ARGS=$(echo "$OLD" | sed 's/.*argv\[\]=//' | sed 's/ ; ignore_errors.*//')
# strip the binary itself off the front of argv
ARGS=$(echo "$ARGS" | sed "s|^${BIN}||")

echo "== binary: $BIN"
echo "== old args contained:"
echo "$ARGS" | tr ' ' '\n' | grep -E 'unsafe|rpc-cors|rpc-methods|rpc-external' | sed 's/^/     /' || echo "     (none)"

# Remove the unsafe trio. Keep --rpc-port so local tooling keeps working;
# without --rpc-external the server binds loopback only, and default
# --rpc-methods is "auto" (safe for non-local callers, full for localhost).
NEW=$(echo "$ARGS" \
  | sed -E 's/--unsafe-rpc-external[[:space:]]*//g' \
  | sed -E 's/--rpc-external[[:space:]]*//g' \
  | sed -E 's/--rpc-methods=unsafe[[:space:]]*//g' \
  | sed -E 's/--rpc-cors=all[[:space:]]*//g' \
  | tr -s ' ')

echo "== new args:"
echo "     $NEW"
if echo "$NEW" | grep -qE 'unsafe|rpc-cors=all'; then
  echo "!! unsafe flags survived the rewrite - aborting"
  exit 1
fi

B0=$(dec "$(best)"); F0=$(dec "$(fin)")
echo "== chain before: best=$B0 finalized=$F0 lag=$(( ${B0:-0} - ${F0:-0} ))"
echo "== peers before: $(R system_health '[]')"

mkdir -p "$(dirname "$DROPIN")"
{
  echo "# Written by Arlo $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "# Removes unsafe RPC exposure from a live mainnet authority."
  echo "# Rollback: rm this file && systemctl daemon-reload && systemctl restart $UNIT"
  echo "[Service]"
  echo "ExecStart="
  echo "ExecStart=${BIN}${NEW}"
} > "$DROPIN"

systemctl daemon-reload
echo "== drop-in written, restarting"
systemctl restart "$UNIT"

# Substrate nodes sit in "activating" while they open the DB; give it real time.
# Judge health by "did the process stay up AND does its RPC answer", not by a
# single early is-active poll.
ok=0
for i in $(seq 1 20); do
  sleep 6
  st=$(systemctl is-active "$UNIT")
  if [ "$st" = "failed" ]; then
    echo "== poll $i: state=failed (hard fail)"
    break
  fi
  ans=$(curl -s -m 5 -H 'Content-Type: application/json' \
        -d '{"jsonrpc":"2.0","id":1,"method":"system_chain","params":[]}' \
        "http://localhost:$PORT" 2>/dev/null)
  if echo "$ans" | grep -q 'Verdis'; then
    echo "== poll $i: state=$st, RPC answers -> healthy"
    ok=1
    break
  fi
  echo "== poll $i: state=$st, RPC not answering yet"
done

if [ "$ok" -ne 1 ]; then
  echo "!! did not become healthy in ~120s - rolling back"
  echo "-- last 15 log lines:"
  journalctl -u "$UNIT" -n 15 --no-pager | tail -15 | sed 's/^/     /'
  rm -f "$DROPIN"; systemctl daemon-reload; systemctl restart "$UNIT"
  sleep 20
  echo "   after rollback: $(systemctl is-active "$UNIT")"
  exit 1
fi

echo "== effective args now:"
systemctl show -p ExecStart --value "$UNIT" | tr ' ' '\n' | grep -E 'unsafe|rpc-' | sed 's/^/     /'

echo "== waiting 60s for the node to rejoin"
sleep 60
B1=$(dec "$(best)"); F1=$(dec "$(fin)")
echo "== chain after: best=$B1 finalized=$F1 lag=$(( ${B1:-0} - ${F1:-0} ))"
echo "== peers after: $(R system_health '[]')"
if [ -n "$F0" ] && [ -n "$F1" ]; then
  if [ "$F1" -gt "$F0" ]; then
    echo "== FINALITY ADVANCED $F0 -> $F1  (+$(( F1 - F0 ))) OK"
  else
    echo "!! finality did not advance ($F0 -> $F1) - investigate"
  fi
fi

echo "== local RPC on $PORT still answers:"
curl -s -m 8 -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"system_chain","params":[]}' \
  "http://localhost:$PORT" || echo "   no answer"
echo
echo "== listener binding for $PORT (must be 127.0.0.1 / ::1 only):"
ss -tlnp 2>/dev/null | grep ":$PORT" || echo "   not listening"
