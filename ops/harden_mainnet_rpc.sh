#!/usr/bin/env bash
# Harden the Verdis MAINNET validator host 185.84.224.91.
#
# FINDING: verdis-validator-v19 runs with --unsafe-rpc-external --rpc-methods=unsafe
# and RPC port 9945 is reachable from the public internet. system_nodeRoles returns
# ["Authority"], i.e. an outsider can reach unsafe RPC on a node holding live
# BABE/GRANDPA private keys. author_insertKey / author_rotateKeys / system_addReservedPeer
# are all in that surface.
#
# APPROACH: firewall first (instant, reversible, no chain downtime). Do NOT restart the
# validators here - a restart of an authority node risks missed slots, and node4-style
# stalls have already been seen on this project. Service-arg cleanup is proposed separately.
#
# Idempotent: safe to re-run.

set -uo pipefail

say() { echo "== $*"; }

say "BEFORE - listening sockets on RPC ports"
ss -tlnp 2>/dev/null | grep -E ':(994[0-9])' || echo "  none"

say "BEFORE - validator service args (proof of unsafe flags)"
for u in verdis-validator verdis-validator-v18 verdis-validator-v19; do
  printf '  %-28s ' "$u"
  systemctl show -p ExecStart --value "$u" 2>/dev/null \
    | grep -oE '\-\-(unsafe-rpc-external|rpc-external|rpc-methods=[a-z]+|rpc-port=[0-9]+|rpc-cors=[a-z]+)' \
    | tr '\n' ' '
  echo
done

say "firewall backend detection"
if command -v ufw >/dev/null 2>&1; then
  echo "  ufw present: $(ufw status 2>/dev/null | head -1)"
fi
echo "  iptables rules on INPUT: $(iptables -S INPUT 2>/dev/null | wc -l)"

# Ports that must NEVER be world-reachable on an authority node.
RPC_PORTS="9933 9934 9935 9944 9945 9946"
# Ports that MUST stay open for consensus/p2p and admin.
KEEP_OPEN="22 30333 30334 30335"

say "applying iptables rules: drop external RPC, keep loopback + p2p"
# Ensure loopback is always allowed (so local curl/monitoring keeps working).
iptables -C INPUT -i lo -j ACCEPT 2>/dev/null || iptables -I INPUT 1 -i lo -j ACCEPT

for p in $RPC_PORTS; do
  # allow from localhost explicitly (belt and braces), then drop the rest
  iptables -C INPUT -p tcp --dport "$p" -s 127.0.0.1 -j ACCEPT 2>/dev/null \
    || iptables -A INPUT -p tcp --dport "$p" -s 127.0.0.1 -j ACCEPT
  iptables -C INPUT -p tcp --dport "$p" -j DROP 2>/dev/null \
    || iptables -A INPUT -p tcp --dport "$p" -j DROP
  echo "  port $p: localhost ACCEPT, world DROP"
done

say "verifying consensus ports remain reachable in ruleset"
for p in $KEEP_OPEN; do
  if iptables -S INPUT 2>/dev/null | grep -qE -- "--dport $p .*DROP"; then
    echo "  !! WARNING: $p appears DROPped - consensus/admin port must stay open"
  else
    echo "  port $p: not blocked (good)"
  fi
done

say "persisting rules"
if command -v netfilter-persistent >/dev/null 2>&1; then
  netfilter-persistent save >/dev/null 2>&1 && echo "  saved via netfilter-persistent"
elif [ -d /etc/iptables ]; then
  iptables-save > /etc/iptables/rules.v4 && echo "  saved to /etc/iptables/rules.v4"
else
  mkdir -p /etc/iptables && iptables-save > /etc/iptables/rules.v4 \
    && echo "  saved to /etc/iptables/rules.v4 (dir created)"
  echo "  NOTE: install iptables-persistent so rules survive reboot"
fi

say "AFTER - INPUT rules touching RPC ports"
iptables -S INPUT | grep -E '994[0-9]|993[3-9]' || echo "  none"

say "AFTER - local RPC still works (must return Verdis Mainnet)"
for p in 9944 9945; do
  printf '  localhost:%s -> ' "$p"
  curl -s -m 8 -H 'Content-Type: application/json' \
    -d '{"jsonrpc":"2.0","id":1,"method":"system_chain","params":[]}' \
    "http://localhost:$p" 2>/dev/null | head -c 120
  echo
done

say "AFTER - chain still producing and finalizing"
R() { curl -s -m 8 -H 'Content-Type: application/json' \
        -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"$1\",\"params\":$2}" http://localhost:9944; }
B=$(R chain_getHeader '[]' | grep -oP '"number":"\K0x[0-9a-f]+')
FH=$(R chain_getFinalizedHead '[]' | grep -oP '0x[0-9a-f]{64}')
F=$(R chain_getHeader "[\"$FH\"]" | grep -oP '"number":"\K0x[0-9a-f]+')
if [ -n "$B" ] && [ -n "$F" ]; then
  echo "  best=$((B)) finalized=$((F)) lag=$(( $((B)) - $((F)) ))"
else
  echo "  NOT_MEASURED"
fi

say "AFTER - peers (p2p must be unaffected)"
curl -s -m 8 -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"system_health","params":[]}' http://localhost:9944

say "AFTER - services still running"
for u in verdis-validator verdis-validator-v18 verdis-validator-v19; do
  printf '  %-28s %s\n' "$u" "$(systemctl is-active "$u")"
done
