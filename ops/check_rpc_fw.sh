#!/usr/bin/env bash
# Show whether the out-of-range authority RPC ports have an explicit DROP rule.
# Ports 9947-9963 were deployed outside the firewalled 9933-9946 range.
SSH="ssh -i $HOME/.ssh/id_ed25519 -o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=10"
for ip in 185.84.224.91 195.154.80.40 213.136.78.63 5.223.77.19; do
  echo "=== $ip ==="
  timeout 60 $SSH "root@$ip" 'iptables -S INPUT 2>/dev/null | grep -E "99[0-9][0-9]" || echo "NO_RPC_RULES"' 2>&1 | head -30
done
exit 0
