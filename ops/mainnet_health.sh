#!/usr/bin/env bash
# Verdis mainnet health check - the numbers that actually predict an outage.
#
# Hard-won context this encodes:
#   * Authority set is 21, finality threshold is 15, and we hold exactly 15 keys.
#     Headroom is ZERO: losing ONE validator stops finality. So the validator count
#     is the single most important number on this page.
#   * The 6 remaining authorities have no key on any server we control and there is
#     no Sudo pallet, so the set cannot be shrunk without governance.
#   * Testnet finality died on 2 Sep and nobody noticed for 5 days because the alert
#     only went to journald. Anything critical must reach Telegram.
#   * All three hosts had authority RPC exposed to the internet. Re-check that it
#     stays closed - a unit restart without the drop-in would re-open it.

KEY=$HOME/.ssh/id_ed25519
SSH="ssh -o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=12 -i $KEY"
HOSTS="185.84.224.91 195.154.80.40 213.136.78.63 5.223.77.19"
CRIT=0; WARN=0
say() { echo "$1"; }

say "VERDIS MAINNET  $(date -u '+%Y-%m-%d %H:%M') UTC"
say ""

# ---- chain state ----
read -r BEST FINAL PEERS AUTH <<<"$($SSH root@185.84.224.91 'R(){ curl -s -m 8 -H "Content-Type: application/json" -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"$1\",\"params\":$2}" http://localhost:9944; }
B=$(R chain_getHeader "[]"|grep -oP "\"number\":\"\K0x[0-9a-f]+")
FH=$(R chain_getFinalizedHead "[]"|grep -oP "0x[0-9a-f]{64}")
F=$(R chain_getHeader "[\"$FH\"]"|grep -oP "\"number\":\"\K0x[0-9a-f]+")
P=$(R system_health "[]"|grep -oP "\"peers\":\K[0-9]+")
A=$(R state_call "[\"GrandpaApi_grandpa_authorities\",\"0x\"]"|grep -oP "result\":\"0x\K[0-9a-f]+")
echo "$((B)) $((F)) ${P:-0} $(( ${#A} / 80 ))"' 2>/dev/null)"

if [ -z "$BEST" ] || [ "$BEST" = "0" ]; then
  say "CRIT  cannot read mainnet RPC"; CRIT=$((CRIT+1))
else
  LAG=$(( BEST - FINAL ))
  THRESH=$(( AUTH * 2 / 3 + 1 ))
  say "chain    best=$BEST finalized=$FINAL lag=$LAG peers=$PEERS"
  say "         authorities=$AUTH threshold=$THRESH"
  if [ "$LAG" -gt 50 ]; then say "CRIT  finality lag $LAG"; CRIT=$((CRIT+1))
  elif [ "$LAG" -gt 20 ]; then say "WARN  finality lag $LAG"; WARN=$((WARN+1)); fi
fi

# ---- validator count: two filters, --validator AND mainnet genesis ----
# History of this one number: counting by unit-name glob undercounted after renames
# (verdis-v13m was missed -> fake CRIT); counting by --validator alone OVERcounted 22
# of 21 because 5.223.77.19 also runs a testnet validator; and a unit without an
# explicit --rpc-port is invisible unless the default port is probed too.
# Ground truth = ExecStart has --validator AND chain_getBlockHash(0) is mainnet.
MAIN_GEN=0x2284393d11797c1a06e8def6a48a79f9d8d7539c5386d9973fce852852817c8e
count_on() {
  timeout 60 $SSH "root@$1" "MAIN_GEN=$MAIN_GEN bash -s" <<'RCOUNT' 2>/dev/null | tr -dc '0-9'
c=0
for u in $(systemctl list-units 'verdis*' --state=active --no-legend --no-pager 2>/dev/null | awk '{print $1}' | grep '\.service$'); do
  E=$(systemctl show -p ExecStart --value "$u" 2>/dev/null | grep -oP 'argv\[\]=\K[^;]+' | tail -1)
  case "$E" in *--validator*) ;; *) continue ;; esac
  rpc=$(echo "$E" | grep -oP '(?<=--rpc-port[= ])[0-9]+' | head -1)
  g=""
  for p in ${rpc:-} 9933 9944; do
    [ -z "$p" ] && continue
    g=$(curl -s -m 6 -H 'Content-Type: application/json' \
        -d '{"jsonrpc":"2.0","id":1,"method":"chain_getBlockHash","params":[0]}' \
        "http://localhost:$p" 2>/dev/null | grep -oP 'result":"\K[^"]+')
    [ -n "$g" ] && break
  done
  [ "$g" = "$MAIN_GEN" ] && c=$((c+1))
done
echo "$c"
RCOUNT
}

TOTALV=0
COUNTFAIL=0
declare -A PERHOST
for ip in $HOSTS; do
  n=""
  for attempt in 1 2 3; do
    n=$(count_on "$ip")
    [ -n "$n" ] && break
    sleep 3
  done
  if [ -z "$n" ]; then
    say "WARN  $ip validator count UNREADABLE (ssh timeout) - not counted as failure"
    WARN=$((WARN+1)); COUNTFAIL=1
    continue
  fi
  PERHOST[$ip]=$n
  TOTALV=$(( TOTALV + n ))
  say "$ip  validators=$n"
done
say "         RUNNING VALIDATORS: $TOTALV  (need ${THRESH:-15})"
# Headroom is what actually matters. With 21 of 21 running against a threshold of 15
# we can lose 6 before finality stops. Warn only when that cushion is gone.
HEAD=$(( TOTALV - ${THRESH:-15} ))
say "         HEADROOM: $HEAD (can lose $HEAD validators before finality halts)"
if [ "$COUNTFAIL" = "0" ] && [ -n "${THRESH:-}" ] && [ "$TOTALV" -lt "$THRESH" ]; then
  if [ -n "${LAG:-}" ] && [ "$LAG" -lt 20 ]; then
    say "WARN  count says $TOTALV < $THRESH but finality is healthy (lag $LAG) - suspect a read error"
    WARN=$((WARN+1))
  else
    say "CRIT  $TOTALV < $THRESH and finality lag $LAG - FINALITY CANNOT PROCEED"; CRIT=$((CRIT+1))
  fi
elif [ "$HEAD" -eq 0 ]; then
  say "WARN  zero headroom: losing one validator halts finality"; WARN=$((WARN+1))
elif [ "$HEAD" -le 2 ]; then
  say "WARN  headroom down to $HEAD - investigate missing validators"; WARN=$((WARN+1))
fi

# ---- per-HOST survivability: the failure mode that actually bites ----
# Node-level headroom is not enough. If one HOST holds more than (total - threshold)
# validators, losing that machine halts finality even though headroom looks fine.
# Contabo once held 14 of 21 - a single reboot would have stopped the chain.
# Reuse the counts already measured above; do not re-query (that caused a false CRIT).
WORST_OK=1
for ip in $HOSTS; do
  n=${PERHOST[$ip]:-}
  [ -z "$n" ] && continue
  rem=$(( TOTALV - n ))
  if [ -n "${THRESH:-}" ] && [ "$rem" -lt "$THRESH" ]; then
    say "CRIT  if $ip is lost: $rem remain < $THRESH - single host can halt finality"
    CRIT=$((CRIT+1)); WORST_OK=0
  fi
done
[ "$WORST_OK" = "1" ] && say "         any single host can fail without halting finality  OK"

# ---- RPC must stay closed to the internet ----
EXPOSED=""
for ip in $HOSTS; do
  for p in 9933 9944 9945; do
    r=$(timeout 6 curl -s -m 5 -H 'Content-Type: application/json' \
        -d '{"jsonrpc":"2.0","id":1,"method":"system_nodeRoles","params":[]}' \
        "http://$ip:$p" 2>/dev/null)
    [ -n "$r" ] && EXPOSED="$EXPOSED $ip:$p"
  done
done
if [ -n "$EXPOSED" ]; then
  say "CRIT  authority RPC exposed:$EXPOSED"; CRIT=$((CRIT+1))
else
  say "rpc      all authority RPC closed to internet  OK"
fi

# ---- the public site must serve MAINNET, not testnet ----
MAIN_GEN=0x2284393d11797c1a06e8def6a48a79f9d8d7539c5386d9973fce852852817c8e
PUBOK=1
for u in https://rpc.verdischain.com https://verdischain.com/rpc; do
  g=$(timeout 12 curl -s -m 10 -H 'Content-Type: application/json' \
      -d '{"jsonrpc":"2.0","id":1,"method":"chain_getBlockHash","params":[0]}' "$u" 2>/dev/null \
      | grep -oP 'result":"\K[^"]+')
  if [ "$g" != "$MAIN_GEN" ]; then
    say "CRIT  $u serves the WRONG CHAIN (genesis ${g:0:18}…)"; CRIT=$((CRIT+1)); PUBOK=0
  fi
done
[ "$PUBOK" = "1" ] && say "public   rpc + /rpc serve mainnet  OK"

# the tunnel and public node that make that work
TUN=$($SSH root@91.98.160.145 'systemctl is-active verdis-mainnet-tunnel' 2>/dev/null)
PUB=$($SSH root@185.84.224.91 'systemctl is-active verdis-public-rpc' 2>/dev/null)
[ "$TUN" != "active" ] && { say "CRIT  mainnet tunnel on web host is $TUN"; CRIT=$((CRIT+1)); }
[ "$PUB" != "active" ] && { say "CRIT  public RPC node is $PUB"; CRIT=$((CRIT+1)); }
[ "$TUN" = "active" ] && [ "$PUB" = "active" ] && say "         tunnel + public node active  OK"

# ---- equivocation (cost me 738 events on testnet today) ----
EQ=0
for ip in $HOSTS; do
  e=$($SSH "root@$ip" "journalctl -u 'verdis*' --since '30 min ago' --no-pager 2>/dev/null | grep -ci equivocat" 2>/dev/null)
  EQ=$(( EQ + ${e:-0} ))
done
if [ "$EQ" -gt 0 ]; then say "CRIT  equivocation events (30min): $EQ"; CRIT=$((CRIT+1))
else say "keys     no equivocation in last 30 min  OK"; fi

# ---- disk ----
for ip in $HOSTS; do
  u=$($SSH "root@$ip" "df / | tail -1 | awk '{print \$5}' | tr -d '%'" 2>/dev/null)
  [ -n "$u" ] && [ "$u" -gt 85 ] && { say "WARN  $ip disk ${u}%"; WARN=$((WARN+1)); }
done

# ---- web ----
DOWN=""
for d in verdischain.com explorer.verdischain.com wallet.verdischain.com dex.verdischain.com; do
  c=$(timeout 12 curl -s -o /dev/null -w '%{http_code}' "https://$d" 2>/dev/null)
  [ "$c" != "200" ] && DOWN="$DOWN $d($c)"
done
[ -n "$DOWN" ] && { say "WARN  web:$DOWN"; WARN=$((WARN+1)); } || say "web      4/4 up  OK"

say ""
if [ "$CRIT" -gt 0 ]; then say "STATUS: CRIT ($CRIT critical, $WARN warnings)"; exit 2
elif [ "$WARN" -gt 0 ]; then say "STATUS: WARN ($WARN warnings)"; exit 1
else say "STATUS: OK"; exit 0; fi
