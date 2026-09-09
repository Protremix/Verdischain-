#!/usr/bin/env bash
# Verdis TESTNET architecture audit collector — runs on 91.98.160.145.
# Read-only. Emits SECTION:: markers so the report generator can parse it.
# Every number is measured here; nothing is inferred.

RPC=http://localhost:9933
R() { curl -s -m 8 -H 'Content-Type: application/json' \
        -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"$1\",\"params\":$2}" "$RPC" 2>/dev/null; }
hx() { [ -n "$1" ] && printf '%d' "$1" 2>/dev/null || echo ""; }

echo "SECTION::META"
echo "audit_host=$(hostname)"
echo "audit_time_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "kernel=$(uname -r)"
echo "distro=$(grep -oP 'PRETTY_NAME="\K[^"]+' /etc/os-release)"
echo "uptime_since=$(uptime -s)"

echo "SECTION::CHAIN"
echo "chain=$(R system_chain '[]' | grep -oP 'result":"\K[^"]+')"
echo "version=$(R system_version '[]' | grep -oP 'result":"\K[^"]+')"
echo "genesis=$(R chain_getBlockHash '[0]' | grep -oP '0x[0-9a-f]{64}')"
echo "spec_version=$(R state_getRuntimeVersion '[]' | grep -oP '"specVersion":\K[0-9]+')"
echo "node_roles=$(R system_nodeRoles '[]' | grep -oP 'result":\K.*' | tr -d '}')"
B1=$(hx "$(R chain_getHeader '[]' | grep -oP '"number":"\K0x[0-9a-f]+')")
FH=$(R chain_getFinalizedHead '[]' | grep -oP '0x[0-9a-f]{64}')
F1=$(hx "$(R chain_getHeader "[\"$FH\"]" | grep -oP '"number":"\K0x[0-9a-f]+')")
echo "best_t0=$B1"
echo "finalized_t0=$F1"
[ -n "$B1" ] && [ -n "$F1" ] && echo "lag_t0=$((B1 - F1))" || echo "lag_t0=NOT_MEASURED"
AUTH=$(R state_call '["GrandpaApi_grandpa_authorities","0x"]' | grep -oP 'result":"0x\K[0-9a-f]+')
if [ -n "$AUTH" ]; then
  echo "grandpa_authorities=$(( ${#AUTH} / 80 ))"
  echo "grandpa_threshold=$(( (${#AUTH} / 80) * 2 / 3 + 1 ))"
else
  echo "grandpa_authorities=NOT_MEASURED"
fi
echo "peers=$(R system_health '[]' | grep -oP '"peers":\K[0-9]+')"
echo "is_syncing=$(R system_health '[]' | grep -oP '"isSyncing":\K(true|false)')"

echo "SECTION::RATE"
sleep 120
B2=$(hx "$(R chain_getHeader '[]' | grep -oP '"number":"\K0x[0-9a-f]+')")
FH2=$(R chain_getFinalizedHead '[]' | grep -oP '0x[0-9a-f]{64}')
F2=$(hx "$(R chain_getHeader "[\"$FH2\"]" | grep -oP '"number":"\K0x[0-9a-f]+')")
echo "best_t1=$B2"
echo "finalized_t1=$F2"
if [ -n "$B1" ] && [ -n "$B2" ] && [ -n "$F1" ] && [ -n "$F2" ]; then
  echo "window_s=120"
  echo "production_per_min=$(( (B2 - B1) / 2 ))"
  echo "finality_per_min=$(( (F2 - F1) / 2 ))"
  echo "net_per_min=$(( ((F2 - F1) - (B2 - B1)) / 2 ))"
  echo "lag_t1=$((B2 - F2))"
fi

echo "SECTION::NODES"
for p in 9933 9934 9935 9936 9937 9938; do
  CB=$(curl -s -m 6 -H 'Content-Type: application/json' \
        -d '{"jsonrpc":"2.0","id":1,"method":"system_syncState","params":[]}' \
        "http://localhost:$p" 2>/dev/null | grep -oP '"currentBlock":\K[0-9]+')
  echo "rpc_${p}_currentBlock=${CB:-DOWN}"
done

echo "SECTION::SERVICES"
systemctl list-units 'verdis*' --all --no-legend --no-pager 2>/dev/null \
  | awk '{print $1"|"$2"|"$3"|"$4}'
echo "failed_count=$(systemctl list-units 'verdis*' --state=failed --no-legend --no-pager 2>/dev/null | wc -l)"
echo "active_count=$(systemctl list-units 'verdis*' --state=active --no-legend --no-pager 2>/dev/null | wc -l)"

echo "SECTION::UNIT_HYGIENE"
for u in $(systemctl list-unit-files 'verdis*' --no-legend --no-pager 2>/dev/null | awk '{print $1}'); do
  st=$(systemctl is-enabled "$u" 2>&1 | head -1)
  echo "$u|$st"
done

echo "SECTION::VALIDATOR_FLAGS"
for u in verdis-node verdis-node2 verdis-node3 verdis-node4 verdis-node5 verdis-node6; do
  E=$(systemctl show -p ExecStart --value "$u" 2>/dev/null)
  DEV=$(echo "$E" | grep -oE '\-\-(alice|bob|charlie|dave|eve|ferdie)' | tr '\n' ',')
  UNSAFE=$(echo "$E" | grep -oE '\-\-(unsafe-rpc-external|rpc-external|rpc-methods=unsafe|rpc-cors=all)' | tr '\n' ',')
  SPEC=$(echo "$E" | grep -oP '(?<=--chain[= ])[^ ]+')
  echo "$u|dev_keys=${DEV:-none}|unsafe=${UNSAFE:-none}|spec=$(basename ${SPEC:-none})"
done

echo "SECTION::SECURITY_PORTS"
ss -tlnp 2>/dev/null | awk 'NR>1 {print $4"|"$6}' | grep -vE '^\[?::1\]?:|^127\.0\.0\.1:' | sort -u | head -40

echo "SECTION::FIREWALL"
echo "ufw=$(command -v ufw >/dev/null 2>&1 && ufw status 2>/dev/null | head -1 || echo 'not installed')"
echo "iptables_input_rules=$(iptables -S INPUT 2>/dev/null | wc -l)"
echo "iptables_rpc_rules=$(iptables -S INPUT 2>/dev/null | grep -cE '99[0-9][0-9]')"
echo "fail2ban=$(systemctl is-active fail2ban 2>/dev/null)"
echo "netfilter_persistent=$(systemctl is-enabled netfilter-persistent 2>/dev/null)"

echo "SECTION::SSH_CONFIG"
sshd -T 2>/dev/null | grep -iE '^(permitrootlogin|passwordauthentication|pubkeyauthentication|port|permitemptypasswords)' | sort

echo "SECTION::RESOURCES"
echo "cores=$(nproc)"
echo "load=$(cut -d' ' -f1-3 /proc/loadavg)"
echo "mem_total_gb=$(free -g | awk 'NR==2{print $2}')"
echo "mem_used_gb=$(free -g | awk 'NR==2{print $3}')"
echo "mem_avail_gb=$(free -g | awk 'NR==2{print $7}')"
echo "disk_pct=$(df / | tail -1 | awk '{print $5}' | tr -d '%')"
echo "disk_free=$(df -h / | tail -1 | awk '{print $4}')"
echo "disk_total=$(df -h / | tail -1 | awk '{print $2}')"
echo "swap_total_gb=$(free -g | awk 'NR==3{print $2}')"

echo "SECTION::DISK_HOGS"
du -sh /opt/* 2>/dev/null | sort -rh | head -10

echo "SECTION::CHAINSPEC"
ls -la /opt/verdis-chain-rust/chain-specs/*.json 2>/dev/null | awk '{print $5"|"$9}'
echo "quarantine=$(ls /opt/verdis-chain-rust/chain-specs/QUARANTINE 2>/dev/null | wc -l) files"

echo "SECTION::BACKUP"
echo "backup_timer=$(systemctl is-active verdis-backup.timer 2>/dev/null)"
echo "backup_service=$(systemctl is-active verdis-backup.service 2>/dev/null)"
echo "backup_last=$(systemctl show -p ExecMainExitTimestamp --value verdis-backup.service 2>/dev/null)"
ls -la /opt/verdis-backups/ 2>/dev/null | tail -5 || echo "no /opt/verdis-backups dir"

echo "SECTION::MONITORING"
for u in verdis-finality-monitor verdis-health-monitor verdis-validator-monitor; do
  echo "$u=$(systemctl is-active $u 2>/dev/null)"
done
echo "alert_destination_check:"
grep -rlisE 'telegram|slack|webhook|smtp|sendmail' /opt/verdis-chain-rust/*monitor* /opt/verdis-chain-rust/monitor* 2>/dev/null | head -5 || echo "  no external alert sink found in monitor scripts"

echo "SECTION::ERRORS_24H"
for u in verdis-node verdis-node2 verdis-node3 verdis-node4 verdis-node5 verdis-node6; do
  n=$(journalctl -u "$u" --since '24 hours ago' --no-pager 2>/dev/null | grep -ciE 'error|panic|essential task|no space' )
  eq=$(journalctl -u "$u" --since '24 hours ago' --no-pager 2>/dev/null | grep -ci 'equivocat')
  echo "$u|errors=$n|equivocations=$eq"
done

echo "SECTION::WEB"
for d in verdischain.com explorer.verdischain.com wallet.verdischain.com faucet.verdischain.com \
         dex.verdischain.com docs.verdischain.com api.verdischain.com rpc.verdischain.com \
         validators.verdischain.com developers.verdischain.com ws.verdischain.com \
         blog.verdischain.com status.verdischain.com monitoring.verdischain.com; do
  echo "$d=$(curl -s -o /dev/null -w '%{http_code}' -m 10 https://$d 2>/dev/null)"
done

echo "SECTION::TLS"
for d in verdischain.com explorer.verdischain.com wallet.verdischain.com; do
  exp=$(echo | timeout 10 openssl s_client -servername "$d" -connect "$d:443" 2>/dev/null \
        | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)
  echo "$d|expires=${exp:-NOT_MEASURED}"
done

echo "SECTION::END"
