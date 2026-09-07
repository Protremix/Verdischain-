#!/usr/bin/env bash
# Assess how much of Verdis MAINNET depends on 195.154.80.40 before touching it.
# 195.154.80.40 is the sole --bootnodes entry for all three validators on this
# host, so rebooting it into rescue mode has a real blast radius. Measure first.

R() { curl -s -m 8 -H 'Content-Type: application/json' \
        -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"$1\",\"params\":$2}" http://localhost:9944; }

echo "=== distinct remote hosts the mainnet nodes are connected to ==="
ss -tn state established 2>/dev/null | awk 'NR>1 {print $5}' \
  | cut -d: -f1 | grep -E '^[0-9]+\.' | grep -vE '^(127\.|172\.1[6-9]\.|172\.2[0-9]\.|172\.3[01]\.|10\.|192\.168\.)' \
  | sort | uniq -c | sort -rn

echo
echo "=== p2p sockets specifically (ports 3033x) ==="
ss -tn 2>/dev/null | grep -E ':3033[0-9]' | awk '{print $5}' | cut -d: -f1 | sort | uniq -c | sort -rn

echo
echo "=== is 195.154.80.40 currently connected? ==="
n=$(ss -tn 2>/dev/null | grep -c '195\.154\.80\.40')
echo "  sockets to 195.154.80.40: $n"

echo
echo "=== chain health ==="
B=$(R chain_getHeader '[]' | grep -oP '"number":"\K0x[0-9a-f]+')
FH=$(R chain_getFinalizedHead '[]' | grep -oP '0x[0-9a-f]{64}')
F=$(R chain_getHeader "[\"$FH\"]" | grep -oP '"number":"\K0x[0-9a-f]+')
echo "  best=$((B)) finalized=$((F)) lag=$(( $((B)) - $((F)) ))"
A=$(R state_call '["GrandpaApi_grandpa_authorities","0x"]' | grep -oP 'result":"0x\K[0-9a-f]+')
NA=$(( ${#A} / 80 ))
echo "  authorities=$NA threshold=$(( NA * 2 / 3 + 1 ))"
echo "  peers=$(R system_health '[]' | grep -oP '"peers":\K[0-9]+')"

echo
echo "=== how many authorities are actually AUTHORING? (last 200 blocks) ==="
journalctl -u verdis-validator-v18 -n 400 --no-pager 2>/dev/null \
  | grep -oP 'Prepared block for proposing|Pre-sealed' | wc -l | sed 's/^/  local proposals: /'

echo
echo "=== bootnode dependency ==="
grep -rhoP '(?<=--bootnodes=)\S+' /etc/systemd/system/verdis-validator*.service 2>/dev/null | sort -u | sed 's/^/  /'
echo "  -> if this host is the ONLY bootnode, losing it stops NEW peers from"
echo "     joining, but already-connected peers keep gossiping."

echo
echo "=== reserved/known peers configured? (would survive bootnode loss) ==="
grep -rhoP '(?<=--reserved-nodes=)\S+' /etc/systemd/system/verdis-validator*.service 2>/dev/null | sed 's/^/  /' \
  || echo "  none configured"
