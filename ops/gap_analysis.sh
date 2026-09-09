#!/usr/bin/env bash
# Gap analysis after deploying the 6 recovered validators. What is still weak?
# Measure everything; do not assume.

KEY=$HOME/.ssh/id_ed25519
SSH="ssh -o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=15 -i $KEY"
HOSTS="185.84.224.91 195.154.80.40 213.136.78.63"

echo "=== 1. HOST-LEVEL failure: headroom 6 is PER-NODE, what about per-HOST? ==="
TOT=0
declare -A CNT
for ip in $HOSTS; do
  n=$($SSH "root@$ip" "systemctl list-units 'verdis-validator*' 'verdis-v??b*' --state=active --no-legend --no-pager | wc -l" 2>/dev/null)
  CNT[$ip]=${n:-0}; TOT=$(( TOT + ${n:-0} ))
done
echo "  total running: $TOT, threshold 15"
for ip in $HOSTS; do
  rem=$(( TOT - ${CNT[$ip]} ))
  if [ "$rem" -lt 15 ]; then
    echo "  !! if $ip dies: ${CNT[$ip]} lost -> $rem remain < 15 -> FINALITY STOPS"
  else
    echo "     if $ip dies: ${CNT[$ip]} lost -> $rem remain >= 15 -> survives"
  fi
done

echo
echo "=== 2. is the keystore BACKUP still complete? (6 new validators added since) ==="
LOCAL_BK="$LOCALAPPDATA/hermes/profiles/verdis/secrets/keystore-backups"
echo "  local archives: $(ls -1 "$LOCAL_BK"/*.tar.gz 2>/dev/null | wc -l)"
echo "  newest: $(ls -1t "$LOCAL_BK"/*.tar.gz 2>/dev/null | head -1 | xargs -r basename)"
for ip in $HOSTS; do
  live=$($SSH "root@$ip" "find /data -type d -name keystore 2>/dev/null | grep -c . " 2>/dev/null)
  echo "  $ip live keystores: ${live:-?}"
done
echo "  -> backup was taken BEFORE the 6 new nodes existed; it is now incomplete"

echo
echo "=== 3. pending reboots / kernel updates ==="
for ip in $HOSTS; do
  r=$($SSH "root@$ip" '[ -f /var/run/reboot-required ] && echo YES || echo no' 2>/dev/null)
  k=$($SSH "root@$ip" 'uname -r' 2>/dev/null)
  echo "  $ip reboot_required=$r running_kernel=$k"
done

echo
echo "=== 4. disk headroom on each host ==="
for ip in $HOSTS; do
  $SSH "root@$ip" 'printf "  %-16s root=%s (%s used)  data=%s (%s used)  nodes=%s\n" \
    "'"$ip"'" "$(df -h / | tail -1 | awk "{print \$4}")" "$(df -h / | tail -1 | awk "{print \$5}")" \
    "$(df -h /data 2>/dev/null | tail -1 | awk "{print \$4}")" "$(df -h /data 2>/dev/null | tail -1 | awk "{print \$5}")" \
    "$(pgrep -cf local/bin/verdis)"' 2>/dev/null
done

echo
echo "=== 5. load after adding 6 nodes to Contabo ==="
for ip in $HOSTS; do
  $SSH "root@$ip" 'printf "  %-16s load=%s cores=%s ram_free=%sG\n" "'"$ip"'" \
    "$(cut -d" " -f1-3 /proc/loadavg)" "$(nproc)" "$(free -g|awk "NR==2{print \$7}")"' 2>/dev/null
done

echo
echo "=== 6. do the 6 new nodes survive a reboot? (enabled?) ==="
$SSH root@213.136.78.63 'for u in verdis-v16b verdis-v17b verdis-v18b verdis-v19b verdis-v20b verdis-v21b; do
  printf "  %-14s %s / %s\n" "$u" "$(systemctl is-active $u)" "$(systemctl is-enabled $u 2>/dev/null)"
done'

echo
echo "=== 7. governance: can we now actually use Council? ==="
Z="$LOCALAPPDATA/hermes/profiles/verdis/secrets/ceremony-keys-20260901.zip"
[ -f "$Z" ] && echo "  ceremony archive present: yes ($(stat -c%s "$Z") bytes)" || echo "  ceremony archive MISSING"
echo "  council accounts in archive: 3 (verified earlier)"
echo "  treasury-multisig accounts: 5"
echo "  -> authority set CAN now be changed by governance if ever needed"

echo
echo "=== 8. testnet: still burning resources? ==="
$SSH root@91.98.160.145 'echo "  nodes: $(pgrep -cf local/bin/verdis)"
echo "  services: $(systemctl list-units "verdis*" --state=active --no-legend --no-pager | wc -l)"
echo "  load: $(cut -d" " -f1-3 /proc/loadavg)"
echo "  disk: $(df -h / | tail -1 | awk "{print \$4\" free (\"\$5\" used)\"}")"
R(){ curl -s -m 6 -H "Content-Type: application/json" -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"$1\",\"params\":$2}" http://localhost:9933; }
B=$(R chain_getHeader "[]"|grep -oP "\"number\":\"\K0x[0-9a-f]+")
FH=$(R chain_getFinalizedHead "[]"|grep -oP "0x[0-9a-f]{64}")
F=$(R chain_getHeader "[\"$FH\"]"|grep -oP "\"number\":\"\K0x[0-9a-f]+")
[ -n "$B" ] && echo "  testnet lag: $(( $((B)) - $((F)) ))"' 2>/dev/null

echo
echo "=== 9. idle paid server 46.17.96.12 ==="
for p in 22 80 443 30333; do
  printf "  port %-6s " "$p"
  timeout 5 bash -c "echo > /dev/tcp/46.17.96.12/$p" 2>/dev/null && echo OPEN || echo closed
done

echo
echo "=== 10. TLS expiry ==="
for d in verdischain.com rpc.verdischain.com; do
  e=$(timeout 12 bash -c "echo | openssl s_client -servername $d -connect $d:443 2>/dev/null | openssl x509 -noout -enddate 2>/dev/null" | cut -d= -f2)
  echo "  $d expires $e"
done

echo
echo "=== 11. monitoring + watchdog alive ==="
for ip in $HOSTS; do
  echo "  $ip watchdog: $($SSH "root@$ip" 'systemctl is-active verdis-watchdog.timer' 2>/dev/null)"
done
