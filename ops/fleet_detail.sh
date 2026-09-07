#!/usr/bin/env bash
# Detail card for each host we can actually log into.
K=$HOME/.ssh/id_ed25519

probe() {
  local ip=$1 label=$2
  echo "[OK] $ip   $label"
  timeout 60 ssh -o BatchMode=yes -o StrictHostKeyChecking=no -i "$K" "root@$ip" 'bash -s' <<'REMOTE' 2>&1
echo "     host  : $(hostname) | $(grep -oP 'PRETTY_NAME="\K[^"]+' /etc/os-release)"
echo "     hw    : $(nproc) cores, $(free -g | awk 'NR==2{print $2}')G RAM (used $(free -g | awk 'NR==2{print $3}')G), disk free $(df -h / | tail -1 | awk '{print $4}')"
echo "     load  : $(cut -d' ' -f1-3 /proc/loadavg)   up since $(uptime -s)"
echo "     verdis: $(pgrep -cf verdis 2>/dev/null) processes, $(systemctl list-units 'verdis*' --state=active --no-legend --no-pager 2>/dev/null | wc -l) active units"
for p in 9933 9944 9945; do
  c=$(curl -s -m 5 -H 'Content-Type: application/json' \
        -d '{"jsonrpc":"2.0","id":1,"method":"system_chain","params":[]}' \
        "http://localhost:$p" 2>/dev/null | grep -oP 'result":"\K[^"]+')
  if [ -n "$c" ]; then
    B=$(curl -s -m 5 -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","id":1,"method":"chain_getHeader","params":[]}' "http://localhost:$p" | grep -oP '"number":"\K0x[0-9a-f]+')
    FH=$(curl -s -m 5 -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","id":1,"method":"chain_getFinalizedHead","params":[]}' "http://localhost:$p" | grep -oP '0x[0-9a-f]{64}')
    F=$(curl -s -m 5 -H 'Content-Type: application/json' -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"chain_getHeader\",\"params\":[\"$FH\"]}" "http://localhost:$p" | grep -oP '"number":"\K0x[0-9a-f]+')
    if [ -n "$B" ] && [ -n "$F" ]; then
      echo "     rpc:$p -> $c  best=$((B)) final=$((F)) lag=$(( $((B)) - $((F)) ))"
    else
      echo "     rpc:$p -> $c"
    fi
  fi
done
REMOTE
  echo
}

probe 185.84.224.91 "HostKey DE  (MAINNET)"
probe 5.223.77.19   "Hetzner SIN (testnet)"
probe 2.29.7.211    "GROVIM jump host"
