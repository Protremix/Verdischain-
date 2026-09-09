#!/usr/bin/env bash
# Reconcile the on-chain GRANDPA authority set against the keys actually present
# in node keystores on all three mainnet hosts.
#
# Two questions answered in one pass:
#   Q1 (todo 2): which of the 21 authorities have NO running node / NO key on disk?
#                Those are the 6 idle slots. If a key file exists we can start a
#                node for it and gain finality headroom.
#   Q2 (todo 6): is any single key present in TWO keystores? That is equivocation
#                and on a slashing chain it costs stake.
#
# Substrate keystore filenames are hex(key_type) + hex(pubkey):
#   gran = 6772616e   babe = 62616265   acco = 61636f6e/6163636f
# We only need gran, since GRANDPA authority set membership is what gates finality.

KEY=$HOME/.ssh/id_ed25519
SSH="ssh -o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=12 -i $KEY"
OUT=$(mktemp -d)

echo "=== STEP 1: on-chain GRANDPA authority set ==="
$SSH root@185.84.224.91 'curl -s -m 10 -H "Content-Type: application/json" \
  -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"state_call\",\"params\":[\"GrandpaApi_grandpa_authorities\",\"0x\"]}" \
  http://localhost:9944' > "$OUT/raw.json" 2>/dev/null

HEX=$(grep -oP 'result":"0x\K[0-9a-f]+' "$OUT/raw.json")
if [ -z "$HEX" ]; then echo "  FAILED to read authority set"; exit 1; fi

# SCALE: compact length prefix, then N * (32-byte pubkey + 8-byte weight).
# Strip the leading compact prefix by aligning to a multiple of 80 from the end.
LEN=${#HEX}
BODY_LEN=$(( (LEN / 80) * 80 ))
OFF=$(( LEN - BODY_LEN ))
BODY=${HEX:$OFF}
N=$(( BODY_LEN / 80 ))
echo "  authorities=$N  threshold=$(( N * 2 / 3 + 1 ))  (prefix stripped: $OFF hex chars)"

: > "$OUT/onchain.txt"
for i in $(seq 0 $(( N - 1 ))); do
  echo "${BODY:$(( i * 80 )):64}" >> "$OUT/onchain.txt"
done
echo "  extracted $(wc -l < "$OUT/onchain.txt") pubkeys"

echo
echo "=== STEP 2: gran keys present on disk, per host ==="
: > "$OUT/ondisk.txt"
for ip in 185.84.224.91 195.154.80.40 213.136.78.63; do
  echo "  --- $ip ---"
  $SSH "root@$ip" 'bash -s' <<'REMOTE' > "$OUT/host.txt" 2>/dev/null
# find every keystore dir, list gran key files (6772616e prefix)
for ks in $(find / -maxdepth 7 -type d -name keystore 2>/dev/null | grep -v snapshot); do
  for f in "$ks"/6772616e*; do
    [ -e "$f" ] || continue
    echo "$(basename "$f" | sed 's/^6772616e//') $ks"
  done
done
REMOTE
  cnt=$(wc -l < "$OUT/host.txt")
  echo "      gran keys found: $cnt"
  sed "s|^|$ip |" "$OUT/host.txt" >> "$OUT/ondisk.txt"
  # show which keystore paths, condensed
  awk '{print $2}' "$OUT/host.txt" | sed 's|/keystore$||' | sort | sed 's|^|      |'
done

echo
echo "=== STEP 3: DUPLICATE KEY CHECK (slashing risk) ==="
awk '{print $2}' "$OUT/ondisk.txt" | sort | uniq -d > "$OUT/dupes.txt"
if [ -s "$OUT/dupes.txt" ]; then
  echo "  *** DUPLICATES FOUND ***"
  while read -r k; do
    echo "  key ${k:0:16}... appears in:"
    grep " $k " "$OUT/ondisk.txt" | awk '{print "      "$1"  "$3}'
  done < "$OUT/dupes.txt"
else
  echo "  no duplicates - every gran key exists in exactly one keystore  OK"
fi

echo
echo "=== STEP 4: reconcile - which authorities have no key on disk? ==="
MATCHED=0
: > "$OUT/missing.txt"
while read -r auth; do
  if grep -qi " $auth " "$OUT/ondisk.txt"; then
    MATCHED=$(( MATCHED + 1 ))
  else
    echo "$auth" >> "$OUT/missing.txt"
  fi
done < "$OUT/onchain.txt"
echo "  authorities WITH a key on our servers : $MATCHED / $N"
echo "  authorities with NO key anywhere      : $(wc -l < "$OUT/missing.txt")"
if [ -s "$OUT/missing.txt" ]; then
  echo "  missing (these are the idle slots, keys not on any server we control):"
  while read -r m; do echo "      0x${m:0:24}..."; done < "$OUT/missing.txt"
fi

echo
echo "=== STEP 5: keys on disk that are NOT in the authority set ==="
EXTRA=0
while read -r line; do
  k=$(echo "$line" | awk '{print $2}')
  grep -qi "^$k$" "$OUT/onchain.txt" || { echo "      $(echo "$line" | awk '{print $1}')  0x${k:0:24}...  $(echo "$line" | awk '{print $3}')"; EXTRA=$(( EXTRA + 1 )); }
done < "$OUT/ondisk.txt"
[ "$EXTRA" -eq 0 ] && echo "      none - every key on disk is a real authority"

echo
echo "=== SUMMARY ==="
echo "  authority set size      : $N"
echo "  finality threshold      : $(( N * 2 / 3 + 1 ))"
echo "  keys we hold            : $MATCHED"
echo "  headroom if all started : $(( MATCHED - (N * 2 / 3 + 1) ))"
rm -rf "$OUT"
