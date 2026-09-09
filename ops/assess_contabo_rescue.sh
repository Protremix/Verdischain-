#!/usr/bin/env bash
# Decide whether rebooting 213.136.78.63 into rescue is survivable for mainnet.
#
# Known: 21 GRANDPA authorities, threshold 15 (2/3+1). We now have SSH on two of
# the three hosts, so we can count real nodes instead of guessing:
#   185.84.224.91 = 3 nodes  (verdis-validator, v18, v19)
#   195.154.80.40 = 4 nodes  (verdis-validator NL, v15, v16, v17)
#   213.136.78.63 = ?        (no SSH yet - estimate from socket ratio)
#
# If Contabo carries more than 6 authorities, taking it down drops us below 15
# and finality STOPS until it returns. Measure before acting.

R() { curl -s -m 8 -H 'Content-Type: application/json' \
        -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"$1\",\"params\":$2}" http://localhost:9933; }

echo "=== authority set ==="
A=$(R state_call '["GrandpaApi_grandpa_authorities","0x"]' | grep -oP 'result":"0x\K[0-9a-f]+')
N=$(( ${#A} / 80 ))
TH=$(( N * 2 / 3 + 1 ))
echo "  authorities=$N  threshold=$TH  max_losable=$(( N - TH ))"

echo
echo "=== nodes on THIS host (195.154.80.40) ==="
LOCAL=$(pgrep -cf 'local/bin/verdis')
echo "  running verdis processes: $LOCAL"
echo "  p2p listeners: $(ss -tln 2>/dev/null | grep -cE ':3033[0-9] ')"

echo
echo "=== established p2p sockets per remote host ==="
ss -tn state established 2>/dev/null | awk '{print $5}' | grep -E ':3033' \
  | cut -d: -f1 | sort | uniq -c | sort -rn | sed 's/^/  /'

echo
echo "=== how many DISTINCT peers does the network report ==="
echo "  system_health peers: $(R system_health '[]' | grep -oP '"peers":\K[0-9]+')"

echo
echo "=== ESTIMATE for 213.136.78.63 ==="
S185=$(ss -tn state established 2>/dev/null | grep -c '185\.84\.224\.91')
S213=$(ss -tn state established 2>/dev/null | grep -c '213\.136\.78\.63')
echo "  sockets to 185.84.224.91 (known 3 nodes): $S185"
echo "  sockets to 213.136.78.63 (unknown)      : $S213"
if [ "$S185" -gt 0 ]; then
  PERNODE=$(( S185 / 3 ))
  [ "$PERNODE" -lt 1 ] && PERNODE=1
  EST=$(( S213 / PERNODE ))
  echo "  sockets per node ~= $PERNODE  ->  estimated nodes on Contabo ~= $EST"
  echo
  TOTAL=$(( 3 + LOCAL + EST ))
  echo "  total known nodes = 3 (HostKey) + $LOCAL (here) + $EST (Contabo) = $TOTAL"
  REMAIN=$(( 3 + LOCAL ))
  echo "  if Contabo goes down, authorities left = $REMAIN"
  if [ "$REMAIN" -lt "$TH" ]; then
    echo "  *** VERDICT: $REMAIN < $TH  -> FINALITY WOULD HALT. DO NOT RESCUE CONTABO. ***"
  else
    echo "  VERDICT: $REMAIN >= $TH -> finality would survive"
  fi
fi

echo
echo "=== current finality (baseline) ==="
B=$(R chain_getHeader '[]' | grep -oP '"number":"\K0x[0-9a-f]+')
FH=$(R chain_getFinalizedHead '[]' | grep -oP '0x[0-9a-f]{64}')
F=$(R chain_getHeader "[\"$FH\"]" | grep -oP '"number":"\K0x[0-9a-f]+')
[ -n "$B" ] && echo "  best=$((B)) finalized=$((F)) lag=$(( $((B)) - $((F)) ))"
