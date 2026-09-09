#!/usr/bin/env bash
# Collect raw evidence for the full mainnet audit. Read-only.
# Everything printed here must be a real reading - no estimates.

KEY=$HOME/.ssh/id_ed25519
SSH="ssh -o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=15 -i $KEY"
HOSTS="185.84.224.91 195.154.80.40 213.136.78.63"

echo "########## 1. CHAIN IDENTITY & RUNTIME ##########"
$SSH root@185.84.224.91 'R(){ curl -s -m 10 -H "Content-Type: application/json" -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"$1\",\"params\":$2}" http://localhost:9944; }
echo "chain:    $(R system_chain "[]" | grep -oP "result\":\"\K[^\"]+")"
echo "version:  $(R system_version "[]" | grep -oP "result\":\"\K[^\"]+")"
echo "name:     $(R system_name "[]" | grep -oP "result\":\"\K[^\"]+")"
echo "runtime:  $(R state_getRuntimeVersion "[]" | grep -oP "\"specName\":\"[^\"]+\"|\"specVersion\":[0-9]+|\"transactionVersion\":[0-9]+" | tr "\n" " ")"
echo "genesis:  $(R chain_getBlockHash "[0]" | grep -oP "result\":\"\K[^\"]+")"
echo "props:    $(R system_properties "[]" | head -c 200)"
echo "health:   $(R system_health "[]" | head -c 150)"'

echo
echo "########## 2. CONSENSUS & FINALITY ##########"
$SSH root@185.84.224.91 'R(){ curl -s -m 10 -H "Content-Type: application/json" -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"$1\",\"params\":$2}" http://localhost:9944; }
B=$(R chain_getHeader "[]"|grep -oP "\"number\":\"\K0x[0-9a-f]+")
FH=$(R chain_getFinalizedHead "[]"|grep -oP "0x[0-9a-f]{64}")
F=$(R chain_getHeader "[\"$FH\"]"|grep -oP "\"number\":\"\K0x[0-9a-f]+")
A=$(R state_call "[\"GrandpaApi_grandpa_authorities\",\"0x\"]"|grep -oP "result\":\"0x\K[0-9a-f]+")
N=$(( ${#A} / 80 ))
echo "best=$((B)) finalized=$((F)) lag=$(( $((B)) - $((F)) ))"
echo "grandpa_authorities=$N threshold=$(( N*2/3+1 ))"
echo "peers=$(R system_health "[]"|grep -oP "\"peers\":\K[0-9]+")"
echo "syncing=$(R system_health "[]"|grep -oP "\"isSyncing\":\K(true|false)")"
echo "should_have_peers=$(R system_health "[]"|grep -oP "\"shouldHavePeers\":\K(true|false)")"'

echo
echo "########## 3. FINALITY RATE (60s measured) ##########"
$SSH root@185.84.224.91 'R(){ curl -s -m 10 -H "Content-Type: application/json" -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"$1\",\"params\":$2}" http://localhost:9944; }
g(){ B=$(R chain_getHeader "[]"|grep -oP "\"number\":\"\K0x[0-9a-f]+"); FH=$(R chain_getFinalizedHead "[]"|grep -oP "0x[0-9a-f]{64}"); F=$(R chain_getHeader "[\"$FH\"]"|grep -oP "\"number\":\"\K0x[0-9a-f]+"); echo "$((B)) $((F))"; }
read B1 F1 <<<"$(g)"; sleep 60; read B2 F2 <<<"$(g)"
echo "blocks produced in 60s: $(( B2 - B1 ))"
echo "blocks finalized in 60s: $(( F2 - F1 ))"
echo "lag start=$(( B1 - F1 )) end=$(( B2 - F2 ))"'

echo
echo "########## 4. PALLETS IN RUNTIME ##########"
$SSH root@185.84.224.91 'M=$(curl -s -m 15 -H "Content-Type: application/json" -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"state_getMetadata\",\"params\":[]}" http://localhost:9944)
echo "metadata size: $(echo -n "$M" | wc -c) bytes"
for p in System Timestamp Babe Grandpa Balances TransactionPayment Sudo Session Staking Democracy Council TechnicalCommittee Treasury Vesting Utility Multisig Dpos Dex Identity Scheduler Preimage Offences ImOnline AuthorityDiscovery Historical ElectionsPhragmen Bounties Tips Assets Contracts Ethereum EVM; do
  H=$(printf "%s" "$p" | xxd -p | tr -d "\n")
  echo "$M" | grep -qi "$H" && echo "  present: $p"
done'

echo
echo "########## 5. VALIDATOR INVENTORY ##########"
for ip in $HOSTS; do
  echo "--- $ip ---"
  $SSH "root@$ip" 'for u in $(systemctl list-units "verdis*" --all --no-legend --no-pager 2>/dev/null | awk "{print \$1}" | grep "\.service$"); do
    E=$(systemctl show -p ExecStart --value $u 2>/dev/null | grep -oP "argv\[\]=\K[^;]+" | tail -1)
    echo "$E" | grep -q -- "--validator" || continue
    st=$(systemctl is-active $u); en=$(systemctl is-enabled $u 2>/dev/null)
    ch=$(echo "$E" | grep -oP "(?<=--chain=)[^ ]+" | xargs -r basename)
    un=$(echo "$E" | grep -c -- "unsafe\|cors=all")
    nb=$(echo "$E" | grep -o "\-\-bootnodes=" | wc -l)
    pr=$(echo "$E" | grep -oP "(?<=--state-pruning=)[^ ]+")
    printf "  %-28s %-9s %-9s %-20s unsafe=%s boot=%s pruning=%s\n" "$u" "$st" "$en" "$ch" "$un" "$nb" "${pr:-default}"
  done'
done

echo
echo "########## 6. SECURITY POSTURE ##########"
for ip in $HOSTS; do
  echo "--- $ip ---"
  $SSH "root@$ip" 'echo "  os: $(grep -oP "PRETTY_NAME=\"\K[^\"]+" /etc/os-release)"
  echo "  kernel: $(uname -r)"
  echo "  ufw: $(ufw status 2>/dev/null | head -1)"
  echo "  fail2ban: $(systemctl is-active fail2ban 2>/dev/null)"
  echo "  iptables_rules: $(iptables -S INPUT 2>/dev/null | wc -l)"
  echo "  persistent: $(systemctl is-enabled netfilter-persistent 2>/dev/null)"
  echo "  ssh_root_login: $(sshd -T 2>/dev/null | grep -i permitrootlogin | head -1)"
  echo "  ssh_password_auth: $(sshd -T 2>/dev/null | grep -i "^passwordauthentication" | head -1)"
  echo "  authorized_keys: $(wc -l < /root/.ssh/authorized_keys 2>/dev/null) keys"
  echo "  unattended_upgrades: $(systemctl is-active unattended-upgrades 2>/dev/null)"
  echo "  reboot_required: $([ -f /var/run/reboot-required ] && echo YES || echo no)"'
done

echo
echo "########## 7. EXTERNAL PORT SCAN ##########"
for ip in $HOSTS; do
  printf "%-16s" "$ip"
  for p in 22 80 443 9933 9934 9944 9945 9946 30333 30334; do
    timeout 5 bash -c "echo > /dev/tcp/$ip/$p" 2>/dev/null && printf " %s:OPEN" "$p" || printf " %s:-" "$p"
  done
  echo
done

echo
echo "########## 8. RESOURCES ##########"
for ip in $HOSTS; do
  $SSH "root@$ip" 'printf "%-18s cores=%-3s ram=%-4s used=%-4s disk_free=%-6s disk_use=%-5s load=%s\n" \
    "$(hostname | cut -c1-16)" "$(nproc)" "$(free -g|awk "NR==2{print \$2}")G" "$(free -g|awk "NR==2{print \$3}")G" \
    "$(df -h /|tail -1|awk "{print \$4}")" "$(df -h /|tail -1|awk "{print \$5}")" "$(cut -d" " -f1 /proc/loadavg)"'
done

echo
echo "########## 9. ERRORS IN LOGS (60 min) ##########"
for ip in $HOSTS; do
  echo "--- $ip ---"
  $SSH "root@$ip" 'L=$(journalctl -u "verdis*" --since "60 min ago" --no-pager 2>/dev/null)
  echo "  lines: $(echo "$L" | wc -l)"
  echo "  equivocation: $(echo "$L" | grep -ci equivocat)"
  echo "  errors: $(echo "$L" | grep -ci "error")"
  echo "  panics: $(echo "$L" | grep -ci "panic")"
  echo "  stalled: $(echo "$L" | grep -ci "stall")"
  echo "  disconnect: $(echo "$L" | grep -ci "disconnect")"
  echo "  essential_failed: $(echo "$L" | grep -ci "Essential task")"
  echo "  slot_skipped: $(echo "$L" | grep -ci "Skipping proposal slot")'
done

echo
echo "########## 10. WEB / TLS ##########"
for d in verdischain.com explorer.verdischain.com wallet.verdischain.com dex.verdischain.com \
         faucet.verdischain.com docs.verdischain.com api.verdischain.com rpc.verdischain.com \
         validators.verdischain.com developers.verdischain.com ws.verdischain.com blog.verdischain.com; do
  c=$(timeout 12 curl -s -o /dev/null -w '%{http_code}' "https://$d" 2>/dev/null)
  e=$(timeout 12 bash -c "echo | openssl s_client -servername $d -connect $d:443 2>/dev/null | openssl x509 -noout -enddate 2>/dev/null" | cut -d= -f2)
  printf "  %-34s %s  expires=%s\n" "$d" "$c" "${e:-unknown}"
done

echo
echo "########## 11. BACKUPS ##########"
ls -l "$LOCALAPPDATA/hermes/profiles/verdis/secrets/keystore-backups" 2>/dev/null | tail -5 | sed 's/^/  /'
for ip in $HOSTS; do
  $SSH "root@$ip" 'echo "  '"$ip"': $(ls -1 /root/keystore-backup-*.tar.gz 2>/dev/null | wc -l) archive(s) on server"'
done
