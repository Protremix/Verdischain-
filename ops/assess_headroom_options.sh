#!/usr/bin/env bash
# Can we gain finality headroom WITHOUT governance and WITHOUT the 6 lost keys?
#
# Facts established:
#   * authority set 21, threshold 15, we hold exactly 15 keys -> zero headroom
#   * no Sudo pallet
#   * we do NOT hold any of the 3 Council member private keys, so we cannot even
#     propose shrinking the set. Governance is closed to us.
#
# Remaining idea: the threshold is a property of the AUTHORITY SET, not of how many
# machines run. We cannot change the set. BUT the real risk is not "a validator
# process dies" - it is "a HOST dies and takes 3-8 authorities with it".
#
# So the achievable win is REDUNDANCY OF HOSTING, not more authorities:
#   - 46.17.96.12 sits idle and paid for. If a keystore is replicated there, a dead
#     host can be replaced in minutes instead of never.
#   - CRITICAL: the replica must NEVER run at the same time as the original, or we
#     get equivocation (which already cost 738 events on testnet today).
#
# This script only MEASURES what a warm-spare setup would require. No changes.

KEY=$HOME/.ssh/id_ed25519
SSH="ssh -o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=12 -i $KEY"

echo "=== 1. is 46.17.96.12 reachable at all? ==="
for p in 22 80 443 30333; do
  printf "  port %-6s " "$p"
  timeout 6 bash -c "echo > /dev/tcp/46.17.96.12/$p" 2>/dev/null && echo OPEN || echo closed
done

echo
echo "=== 2. per-host authority exposure (what one host failure costs) ==="
for ip in 185.84.224.91 195.154.80.40 213.136.78.63; do
  n=$($SSH "root@$ip" "systemctl list-units 'verdis*' --state=active --no-legend --no-pager 2>/dev/null | awk '{print \$1}' | grep '\.service\$' | while read u; do systemctl show -p ExecStart --value \$u 2>/dev/null | grep -oP 'argv\\[\\]=\\K[^;]+' | tail -1; done | grep -c -- '--validator'" 2>/dev/null)
  echo "  $ip loses $n of 21 -> ${n:-?} down leaves $(( 15 - (15 - ${n:-0}) )) ... remaining=$(( 15 - ${n:-0} )) vs threshold 15"
done

echo
echo "=== 3. how fast does a node reach 'active' from cold start? ==="
echo "  (measured earlier: archive node took ~90s+; systemd default TimeoutStartSec applies)"
$SSH root@213.136.78.63 'systemctl show -p TimeoutStartUSec --value verdis-validator-v9 2>/dev/null | sed "s/^/  TimeoutStartSec: /"'

echo
echo "=== 4. keystore size per validator (how much to replicate) ==="
$SSH root@213.136.78.63 'for ks in $(find /data -maxdepth 6 -type d -name keystore -path "*verdis-mainnet*" 2>/dev/null | head -3); do
  echo "  $ks: $(du -sh "$ks" 2>/dev/null | cut -f1) ($(find "$ks" -type f | wc -l) files)"
done'

echo
echo "=== 5. chain db size (a warm spare needs synced state) ==="
for ip in 185.84.224.91 213.136.78.63; do
  $SSH "root@$ip" 'echo "  '"$ip"': $(du -sh /data/verdis-data 2>/dev/null | cut -f1) per node, $(df -h /data | tail -1 | awk "{print \$4}") free on /data"'
done

echo
echo "=== 6. VERDICT INPUTS ==="
echo "  Council private keys held: NO (checked all 3 members on all 3 hosts)"
echo "  Sudo pallet: absent"
echo "  => authority set cannot be changed by us"
echo "  => only achievable mitigation is host-level redundancy (cold/warm spare)"
