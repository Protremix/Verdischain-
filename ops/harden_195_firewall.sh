#!/usr/bin/env bash
# EMERGENCY: close unsafe RPC exposure on 195.154.80.40.
#
# Verified from the internet just now: ports 9933/9934/9935 answer
# system_nodeRoles -> ["Authority"] from outside. These are mainnet authorities
# holding live BABE/GRANDPA private keys, and all 4 units carry
# --unsafe-rpc-external --rpc-methods=unsafe. author_insertKey / author_rotateKeys
# are reachable by anyone on the internet.
#
# Firewall FIRST (instant, no downtime, no restart). Unit-flag cleanup comes
# afterwards in a separate step, one node at a time, so a mistake cannot take
# multiple authorities down at once (threshold is 15 of 21).

set -uo pipefail

echo "=== BEFORE: what listens ==="
ss -tlnp 2>/dev/null | grep -E ':99[0-9][0-9]' | awk '{print "  "$4}'

echo
echo "=== BEFORE: unsafe flags in units ==="
grep -l 'unsafe-rpc-external\|rpc-methods=unsafe' /etc/systemd/system/verdis*.service 2>/dev/null | sed 's/^/  /'

echo
echo "=== firewall backend ==="
if command -v ufw >/dev/null 2>&1; then echo "  ufw: $(ufw status | head -1)"; fi
echo "  iptables INPUT rules: $(iptables -S INPUT 2>/dev/null | wc -l)"

RPC_PORTS="9933 9934 9935 9936 9944 9945 9946"
KEEP="22 30333 30334 30335 30336"

echo
echo "=== applying: loopback ACCEPT, world DROP on RPC ports ==="
iptables -C INPUT -i lo -j ACCEPT 2>/dev/null || iptables -I INPUT 1 -i lo -j ACCEPT
for p in $RPC_PORTS; do
  iptables -C INPUT -p tcp --dport "$p" -s 127.0.0.1 -j ACCEPT 2>/dev/null \
    || iptables -A INPUT -p tcp --dport "$p" -s 127.0.0.1 -j ACCEPT
  iptables -C INPUT -p tcp --dport "$p" -j DROP 2>/dev/null \
    || iptables -A INPUT -p tcp --dport "$p" -j DROP
  echo "  $p: localhost ACCEPT / world DROP"
done

echo
echo "=== consensus + ssh ports must stay reachable ==="
for p in $KEEP; do
  if iptables -S INPUT | grep -qE -- "--dport $p .*DROP"; then
    echo "  !! WARNING $p is DROPped"
  else
    echo "  $p ok"
  fi
done

echo
echo "=== persist rules ==="
export DEBIAN_FRONTEND=noninteractive
if ! command -v netfilter-persistent >/dev/null 2>&1; then
  echo "iptables-persistent iptables-persistent/autosave_v4 boolean false" | debconf-set-selections
  echo "iptables-persistent iptables-persistent/autosave_v6 boolean false" | debconf-set-selections
  apt-get install -y -qq iptables-persistent >/dev/null 2>&1
fi
mkdir -p /etc/iptables
iptables-save > /etc/iptables/rules.v4
systemctl enable netfilter-persistent >/dev/null 2>&1
echo "  saved to /etc/iptables/rules.v4 ($(wc -l < /etc/iptables/rules.v4) lines)"
echo "  netfilter-persistent: $(systemctl is-enabled netfilter-persistent 2>&1)"
iptables-restore --test < /etc/iptables/rules.v4 && echo "  ruleset VALID"

echo
echo "=== AFTER: local RPC still works (must answer) ==="
for p in 9933 9934 9935; do
  printf "  localhost:%s -> " "$p"
  curl -s -m 6 -H 'Content-Type: application/json' \
    -d '{"jsonrpc":"2.0","id":1,"method":"system_chain","params":[]}' \
    "http://localhost:$p" 2>/dev/null | head -c 90
  echo
done

echo
echo "=== AFTER: all 4 validators still active ==="
for u in verdis-validator verdis-validator-v15 verdis-validator-v16 verdis-validator-v17; do
  printf "  %-24s %s\n" "$u" "$(systemctl is-active "$u")"
done

echo
echo "=== chain view from this host ==="
R() { curl -s -m 8 -H 'Content-Type: application/json' \
        -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"$1\",\"params\":$2}" http://localhost:9933; }
B=$(R chain_getHeader '[]' | grep -oP '"number":"\K0x[0-9a-f]+')
FH=$(R chain_getFinalizedHead '[]' | grep -oP '0x[0-9a-f]{64}')
F=$(R chain_getHeader "[\"$FH\"]" | grep -oP '"number":"\K0x[0-9a-f]+')
if [ -n "$B" ] && [ -n "$F" ]; then
  echo "  best=$((B)) finalized=$((F)) lag=$(( $((B)) - $((F)) ))"
fi
echo "  peers=$(R system_health '[]' | grep -oP '"peers":\K[0-9]+')"
