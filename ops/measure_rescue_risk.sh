#!/usr/bin/env bash
# Measure the blast radius of rebooting 195.154.80.40 (rescue mode).
#
# rescue does NOT wipe the disk - it netboots a RAM image, data stays intact.
# The real risk is the REBOOT: validators on that host stop while it is in rescue.
# Mainnet has 21 GRANDPA authorities, threshold 15. If that host carries more than
# 6 authorities, stopping it drops us below threshold and FINALITY HALTS.
#
# So: count how many DISTINCT authorities are actively authoring blocks, and how
# many block-author slots we would lose.

R() { curl -s -m 8 -H 'Content-Type: application/json' \
        -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"$1\",\"params\":$2}" http://localhost:9944; }

echo "=== authority set size and threshold ==="
A=$(R state_call '["GrandpaApi_grandpa_authorities","0x"]' | grep -oP 'result":"0x\K[0-9a-f]+')
N=$(( ${#A} / 80 ))
echo "  authorities = $N"
echo "  GRANDPA threshold = $(( N * 2 / 3 + 1 )) votes needed"
echo "  max we can lose  = $(( N - (N * 2 / 3 + 1) )) authorities"

echo
echo "=== how many DISTINCT block authors in the last 120 blocks? ==="
BEST=$(R chain_getHeader '[]' | grep -oP '"number":"\K0x[0-9a-f]+')
BESTD=$((BEST))
START=$(( BESTD - 120 ))
echo "  scanning blocks $START..$BESTD"

TMP=$(mktemp)
for n in $(seq $START 4 $BESTD); do
  HX=$(printf '0x%x' "$n")
  BH=$(R chain_getBlockHash "[$n]" | grep -oP '0x[0-9a-f]{64}')
  [ -z "$BH" ] && continue
  # BABE pre-runtime digest carries the authority index; extract the 0x0642414245 log
  R chain_getHeader "[\"$BH\"]" \
    | grep -oP '0x0642414245[0-9a-f]{20}' | head -1 >> "$TMP"
done
TOTAL=$(wc -l < "$TMP")
DISTINCT=$(sort -u "$TMP" | wc -l)
echo "  sampled $TOTAL blocks, $DISTINCT distinct author digests"
rm -f "$TMP"

echo
echo "=== who do we actually talk to (p2p sockets by host) ==="
ss -tn 2>/dev/null | grep -E ':3033' | awk '{print $5}' | cut -d: -f1 \
  | sort | uniq -c | sort -rn | sed 's/^/  /'

echo
echo "=== our OWN nodes on this host ==="
for u in verdis-validator verdis-validator-v18 verdis-validator-v19; do
  printf "  %-24s %s\n" "$u" "$(systemctl is-active $u)"
done
echo "  -> this host runs 3 nodes out of $N authorities"

echo
echo "=== is 195.154.80.40 the only bootnode? ==="
grep -rhoP '(?<=--bootnodes=)\S+' /etc/systemd/system/verdis-validator*.service 2>/dev/null | sort -u | sed 's/^/  /'
echo "  reserved-nodes configured:"
grep -rhoP '(?<=--reserved-nodes=)\S+' /etc/systemd/system/verdis-validator*.service 2>/dev/null | sed 's/^/  /' || echo "    NONE"

echo
echo "=== current finality (baseline before any change) ==="
B=$(R chain_getHeader '[]' | grep -oP '"number":"\K0x[0-9a-f]+')
FH=$(R chain_getFinalizedHead '[]' | grep -oP '0x[0-9a-f]{64}')
F=$(R chain_getHeader "[\"$FH\"]" | grep -oP '"number":"\K0x[0-9a-f]+')
echo "  best=$((B)) finalized=$((F)) lag=$(( $((B)) - $((F)) ))"
echo "  peers=$(R system_health '[]' | grep -oP '"peers":\K[0-9]+')"
