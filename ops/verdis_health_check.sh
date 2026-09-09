#!/usr/bin/env bash
# Verdis Chain health check — runs ON the main host (91.98.160.145).
# Emits a compact report to stdout. Exit 0 always; severity is in the text.
# Measures everything; never estimates. Missing reading => NOT_MEASURED.

RPC=http://localhost:9933
rpc() { curl -s -m 8 -H 'Content-Type: application/json' -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"$1\",\"params\":$2}" $RPC 2>/dev/null; }
hex2dec() { [ -n "$1" ] && printf '%d' "$1" 2>/dev/null || echo ""; }

# --- chain head / finality ---
BEST_HEX=$(rpc chain_getHeader '[]' | grep -oP '"number":"\K0x[0-9a-f]+')
FIN_HASH=$(rpc chain_getFinalizedHead '[]' | grep -oP '0x[0-9a-f]{64}')
FIN_HEX=""
[ -n "$FIN_HASH" ] && FIN_HEX=$(rpc chain_getHeader "[\"$FIN_HASH\"]" | grep -oP '"number":"\K0x[0-9a-f]+')
BEST=$(hex2dec "$BEST_HEX"); FIN=$(hex2dec "$FIN_HEX")

# --- finality rate over 60s ---
sleep 60
BEST2_HEX=$(rpc chain_getHeader '[]' | grep -oP '"number":"\K0x[0-9a-f]+')
FIN2_HASH=$(rpc chain_getFinalizedHead '[]' | grep -oP '0x[0-9a-f]{64}')
FIN2_HEX=""
[ -n "$FIN2_HASH" ] && FIN2_HEX=$(rpc chain_getHeader "[\"$FIN2_HASH\"]" | grep -oP '"number":"\K0x[0-9a-f]+')
BEST2=$(hex2dec "$BEST2_HEX"); FIN2=$(hex2dec "$FIN2_HEX")

LAG="NOT_MEASURED"; FRATE="NOT_MEASURED"; BRATE="NOT_MEASURED"; NET="NOT_MEASURED"
if [ -n "$BEST2" ] && [ -n "$FIN2" ]; then LAG=$(( BEST2 - FIN2 )); fi
if [ -n "$FIN" ] && [ -n "$FIN2" ]; then FRATE=$(( FIN2 - FIN )); fi
if [ -n "$BEST" ] && [ -n "$BEST2" ]; then BRATE=$(( BEST2 - BEST )); fi
if [ "$FRATE" != "NOT_MEASURED" ] && [ "$BRATE" != "NOT_MEASURED" ]; then NET=$(( FRATE - BRATE )); fi

# --- nodes: which are at the head, which are stuck ---
NODES_OK=0; NODES_STUCK=0; NODE_DETAIL=""
for p in 9933 9934 9935 9936 9937 9938; do
  CB=$(curl -s -m 6 -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","id":1,"method":"system_syncState","params":[]}' http://localhost:$p 2>/dev/null | grep -oP '"currentBlock":\K[0-9]+')
  if [ -z "$CB" ]; then NODE_DETAIL="$NODE_DETAIL\n  rpc:$p DOWN"; NODES_STUCK=$((NODES_STUCK+1)); continue; fi
  if [ -n "$BEST2" ] && [ $(( BEST2 - CB )) -lt 100 ]; then
    NODES_OK=$((NODES_OK+1))
  else
    NODES_STUCK=$((NODES_STUCK+1)); NODE_DETAIL="$NODE_DETAIL\n  rpc:$p STUCK at #$CB"
  fi
done

# --- grandpa authority count + threshold ---
AUTH_HEX=$(rpc state_call '["GrandpaApi_grandpa_authorities","0x"]' | grep -oP '"result":"0x\K[0-9a-f]+')
AUTH_N="NOT_MEASURED"; THRESH="NOT_MEASURED"
if [ -n "$AUTH_HEX" ]; then
  AUTH_N=$(( (${#AUTH_HEX} - 2) / 80 ))
  THRESH=$(( AUTH_N * 2 / 3 + 1 ))
fi

# --- peers / services / disk ---
PEERS=$(rpc system_health '[]' | grep -oP '"peers":\K[0-9]+'); [ -z "$PEERS" ] && PEERS=NOT_MEASURED
SVC_ACTIVE=$(systemctl list-units 'verdis*' --state=active --no-legend --no-pager 2>/dev/null | wc -l)
SVC_FAILED=$(systemctl list-units 'verdis*' --state=failed --no-legend --no-pager 2>/dev/null | wc -l)
DISK_PCT=$(df / | tail -1 | awk '{print $5}' | tr -d '%')
DISK_FREE=$(df -h / | tail -1 | awk '{print $4}')
LOAD=$(cut -d' ' -f1-3 /proc/loadavg)
CORES=$(nproc)

# --- web endpoints ---
WEB_OK=0; WEB_BAD=""
for d in verdischain.com explorer.verdischain.com wallet.verdischain.com faucet.verdischain.com \
         dex.verdischain.com docs.verdischain.com api.verdischain.com rpc.verdischain.com \
         validators.verdischain.com developers.verdischain.com ws.verdischain.com; do
  C=$(curl -s -o /dev/null -w '%{http_code}' -m 10 https://$d 2>/dev/null)
  case "$C" in
    200|301|302|401) WEB_OK=$((WEB_OK+1)) ;;
    *) WEB_BAD="$WEB_BAD $d($C)" ;;
  esac
done

# --- severity ---
SEV="OK"; ALERTS=""
if [ "$LAG" != "NOT_MEASURED" ] && [ "$LAG" -gt 100 ]; then
  SEV="CRIT"; ALERTS="$ALERTS\nFinality lag $LAG blocks (threshold 100)"
fi
if [ "$NET" != "NOT_MEASURED" ] && [ "$NET" -lt 0 ] && [ "$LAG" != "NOT_MEASURED" ] && [ "$LAG" -gt 100 ]; then
  ALERTS="$ALERTS\nLag GROWING at ${NET#-} blocks/min - finality slower than production"
fi
if [ "$NODES_STUCK" -gt 0 ]; then
  [ "$SEV" = "OK" ] && SEV="WARN"; ALERTS="$ALERTS\n$NODES_STUCK node(s) not at head:$NODE_DETAIL"
fi
if [ "$AUTH_N" != "NOT_MEASURED" ] && [ "$NODES_OK" -lt "$THRESH" ]; then
  SEV="CRIT"; ALERTS="$ALERTS\nVoting nodes $NODES_OK < GRANDPA threshold $THRESH - finality CANNOT progress"
fi
if [ "$DISK_PCT" -ge 85 ]; then
  SEV="CRIT"; ALERTS="$ALERTS\nDisk ${DISK_PCT}% full ($DISK_FREE free) - ENOSPC killed nodes on Aug 31"
elif [ "$DISK_PCT" -ge 75 ]; then
  [ "$SEV" = "OK" ] && SEV="WARN"; ALERTS="$ALERTS\nDisk ${DISK_PCT}% full ($DISK_FREE free)"
fi
if [ "$SVC_FAILED" -gt 0 ]; then
  [ "$SEV" = "OK" ] && SEV="WARN"; ALERTS="$ALERTS\n$SVC_FAILED verdis service(s) FAILED"
fi
if [ -n "$WEB_BAD" ]; then
  [ "$SEV" = "OK" ] && SEV="WARN"; ALERTS="$ALERTS\nWeb endpoints down:$WEB_BAD"
fi

echo "SEVERITY=$SEV"
echo "best=$BEST2 finalized=$FIN2 lag=$LAG"
echo "finality_rate=${FRATE}/min production_rate=${BRATE}/min net=${NET}/min"
echo "grandpa_authorities=$AUTH_N threshold=$THRESH nodes_at_head=$NODES_OK nodes_stuck=$NODES_STUCK"
echo "peers=$PEERS services_active=$SVC_ACTIVE services_failed=$SVC_FAILED"
echo "disk=${DISK_PCT}% free=$DISK_FREE load=$LOAD cores=$CORES"
echo "web_ok=$WEB_OK/11"
[ -n "$ALERTS" ] && printf "ALERTS:%b\n" "$ALERTS"
exit 0
