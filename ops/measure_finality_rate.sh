#!/usr/bin/env bash
# Measure finality catch-up rate over a 4-minute window with all 6 nodes at head.
# Also scan every node for BABE equivocation reports.

RPC=http://localhost:9933
R() { curl -s -m 8 -H 'Content-Type: application/json' \
        -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"$1\",\"params\":$2}" "$RPC"; }
best() { R chain_getHeader '[]' | grep -oP '"number":"\K0x[0-9a-f]+'; }
fin() {
  local fh
  fh=$(R chain_getFinalizedHead '[]' | grep -oP '0x[0-9a-f]{64}')
  [ -n "$fh" ] && R chain_getHeader "[\"$fh\"]" | grep -oP '"number":"\K0x[0-9a-f]+'
}
d() { printf '%d' "$1" 2>/dev/null || echo 0; }

F0=$(d "$(fin)"); B0=$(d "$(best)"); T0=$(date +%s)
echo "T0 $(date -u +%H:%M:%S)  finalized=$F0 best=$B0 lag=$((B0 - F0))"

for i in 1 2 3 4; do
  sleep 60
  Fn=$(d "$(fin)"); Bn=$(d "$(best)"); EL=$(( $(date +%s) - T0 ))
  echo "[+${EL}s] finalized=$Fn (+$((Fn - F0)))  best=$Bn (+$((Bn - B0)))  lag=$((Bn - Fn))"
done

Fn=$(d "$(fin)"); Bn=$(d "$(best)"); EL=$(( $(date +%s) - T0 ))
GF=$((Fn - F0)); GB=$((Bn - B0)); NET=$((GF - GB)); LAG=$((Bn - Fn))

echo
echo "=== ${EL}s window, all 6 nodes at head ==="
echo "finality   +${GF}  ($((GF * 60 / EL))/min)"
echo "production +${GB}  ($((GB * 60 / EL))/min)"
echo "net        $((NET * 60 / EL))/min"
if [ "$NET" -gt 0 ]; then
  echo "CATCHING UP -> ETA $(( LAG * EL / NET / 3600 ))h to zero lag (current lag $LAG)"
else
  echo "NOT catching up (net <= 0), lag $LAG"
fi

echo
echo "=== equivocation scan, last 15 min ==="
for u in verdis-node verdis-node2 verdis-node3 verdis-node4 verdis-node5 verdis-node6; do
  n=$(journalctl -u "$u" --since '15 min ago' --no-pager 2>/dev/null | grep -ci equivocat)
  echo "  $u: $n lines"
done
echo "--- samples ---"
journalctl -u verdis-node4 --since '15 min ago' --no-pager 2>/dev/null | grep -i equivocat | tail -3
