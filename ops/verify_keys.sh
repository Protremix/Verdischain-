#!/usr/bin/env bash
SSH="ssh -o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=15 -i $HOME/.ssh/id_ed25519"

echo "=== do /data/validator-20 and -21 still exist on Contabo? ==="
$SSH root@213.136.78.63 'for d in /data/validator-16 /data/validator-17 /data/validator-20 /data/validator-21; do
  echo -n "$d: "
  if [ -d "$d" ]; then find "$d" -name "6772616e*" 2>/dev/null | head -3 | tr "\n" " "; echo; else echo GONE; fi
done'

echo
echo "=== keys held by the two migrated units on 195.154.80.40 ==="
$SSH root@195.154.80.40 'for d in /data/validator-16 /data/validator-17; do
  echo -n "$d: "; find "$d" -path "*/keystore/6772616e*" 2>/dev/null | while read f; do basename "$f" | cut -c9-24; done | tr "\n" " "; echo
done'

echo
echo "=== the two missing keys anywhere on any host? ==="
for ip in 185.84.224.91 195.154.80.40 213.136.78.63; do
  echo -n "$ip: "
  $SSH "root@$ip" 'find / -maxdepth 8 \( -name "6772616ec684b6445815fe73b22b70e6d192ecb72013e695b62d94b69885ecc80c699119" -o -name "6772616e1d1b56d9c8ffd65ac29154c9fdec596f81353617a7d8bd774d430aed3d23c48b" \) 2>/dev/null | tr "\n" " "; echo'
done

echo
echo "=== equivocation last 60 min (migration window) ==="
for ip in 185.84.224.91 195.154.80.40 213.136.78.63; do
  echo -n "$ip count="
  $SSH "root@$ip" 'journalctl -u "verdis*" --since "60 min ago" --no-pager 2>/dev/null | grep -ci equivocat'
done
