#!/usr/bin/env bash
# Inspect full INPUT chain structure + actual listen sockets before adding rules.
SSH="ssh -i $HOME/.ssh/id_ed25519 -o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=10"
for ip in 213.136.78.63 5.223.77.19; do
  echo "=== $ip ==="
  timeout 60 $SSH "root@$ip" 'echo "--policy--"; iptables -S INPUT | grep -E "^-P|^-A INPUT -j|ACCEPT$" | head -12
echo "--tail of INPUT--"; iptables -S INPUT | tail -4
echo "--listen sockets for authority rpc ports--"
ss -ltnp 2>/dev/null | grep -E "99(4[7-9]|5[0-9]|6[0-3])" || echo "none"
echo "--persistence--"; ls -1 /etc/iptables/ 2>/dev/null; dpkg -l iptables-persistent 2>/dev/null | tail -1' 2>&1 | head -40
done
exit 0
