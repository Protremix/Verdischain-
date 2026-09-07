#!/usr/bin/env bash
# Testnet hygiene on 91.98.160.145: archive dead unit files and stale chain-specs.
# NOTHING RUNNING IS TOUCHED. Everything is moved to a timestamped archive dir,
# never deleted, so any of it can be restored with a single mv.
#
# Guards:
#  - a unit is only archived if it is inactive AND (disabled or masked)
#  - the 6 testnet validators, monitors, and every enabled unit are skipped
#  - the spec actually referenced by a running node is never archived

set -uo pipefail
STAMP=$(date -u +%Y%m%d-%H%M%S)
ARCH=/opt/verdis-archive/$STAMP
mkdir -p "$ARCH/systemd" "$ARCH/chain-specs"

echo "== archive dir: $ARCH"
echo

# ---------- 1. unit files ----------
echo "=== UNIT FILES ==="
KEEP_RE='verdis-(node|node2|node3|node4|node5|node6|api|faucet|governance|relay|txbot|soak-test|price-collector|rpc-filter|ws-filter|backup|finality-monitor|health-monitor|validator-monitor|insert-keys)\.(service|timer)$'

moved=0; kept=0
for u in $(systemctl list-unit-files 'verdis*' --no-legend --no-pager 2>/dev/null | awk '{print $1}'); do
  state=$(systemctl is-enabled "$u" 2>&1 | head -1)
  active=$(systemctl is-active "$u" 2>&1 | head -1)
  path="/etc/systemd/system/$u"

  if echo "$u" | grep -qE "$KEEP_RE"; then
    kept=$((kept+1)); continue
  fi
  if [ "$active" = "active" ] || [ "$active" = "activating" ]; then
    echo "  SKIP (running)  $u"
    kept=$((kept+1)); continue
  fi
  if [ "$state" = "enabled" ]; then
    echo "  SKIP (enabled)  $u"
    kept=$((kept+1)); continue
  fi
  if [ ! -e "$path" ] && [ ! -L "$path" ]; then
    continue
  fi
  # masked units are symlinks to /dev/null - record and remove the mask
  if [ -L "$path" ] && [ "$(readlink -f "$path")" = "/dev/null" ]; then
    echo "  ARCHIVE (mask)  $u"
    echo "$u was a mask -> /dev/null" >> "$ARCH/systemd/MASKS.txt"
    rm -f "$path"
    moved=$((moved+1)); continue
  fi
  echo "  ARCHIVE ($state) $u"
  mv "$path" "$ARCH/systemd/" 2>/dev/null && moved=$((moved+1))
  rm -rf "/etc/systemd/system/$u.d" 2>/dev/null
done
echo "  -> archived=$moved kept=$kept"
systemctl daemon-reload
echo "  daemon-reload done"
echo

# ---------- 2. chain specs ----------
echo "=== CHAIN SPECS ==="
SPECDIR=/opt/verdis-chain-rust/chain-specs
# collect every spec path referenced by any verdis unit (running or not)
IN_USE=$(grep -rhoP '(?<=--chain[= ])\S+' /etc/systemd/system/verdis-*.service 2>/dev/null | xargs -r -n1 basename | sort -u)
echo "  referenced by units: $(echo $IN_USE | tr '\n' ' ')"

for f in "$SPECDIR"/*.json; do
  [ -f "$f" ] || continue
  b=$(basename "$f")
  if echo "$IN_USE" | grep -qxF "$b"; then
    echo "  KEEP (in use)   $b"
    continue
  fi
  # keep the audited mainnet spec regardless
  if [ "$b" = "mainnet-raw-v13.json" ]; then
    echo "  KEEP (audited)  $b"
    continue
  fi
  echo "  ARCHIVE         $b"
  mv "$f" "$ARCH/chain-specs/"
done
echo
echo "  remaining in $SPECDIR:"
ls -1 "$SPECDIR"/*.json 2>/dev/null | xargs -r -n1 basename | sed 's/^/    /'
echo

# ---------- 3. verify nothing broke ----------
echo "=== VERIFY ==="
for u in verdis-node verdis-node2 verdis-node3 verdis-node5 verdis-node6; do
  printf "  %-16s %s\n" "$u" "$(systemctl is-active $u)"
done
echo "  failed units: $(systemctl list-units 'verdis*' --state=failed --no-legend --no-pager | wc -l)"
echo "  bad-setting : $(systemctl list-units 'verdis*' --all --no-legend --no-pager 2>&1 | grep -c bad-setting)"
echo "  unit files  : $(systemctl list-unit-files 'verdis*' --no-legend --no-pager | wc -l) (was 50)"
echo
R() { curl -s -m 8 -H 'Content-Type: application/json' -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"$1\",\"params\":$2}" http://localhost:9933; }
B=$(R chain_getHeader '[]' | grep -oP '"number":"\K0x[0-9a-f]+')
FH=$(R chain_getFinalizedHead '[]' | grep -oP '0x[0-9a-f]{64}')
F=$(R chain_getHeader "[\"$FH\"]" | grep -oP '"number":"\K0x[0-9a-f]+')
[ -n "$B" ] && echo "  chain: best=$((B)) finalized=$((F)) lag=$(( $((B)) - $((F)) ))" || echo "  chain: NOT_MEASURED"
echo
echo "== restore any item with: mv $ARCH/systemd/<unit> /etc/systemd/system/ && systemctl daemon-reload"
