#!/usr/bin/env bash
SSH="ssh -o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=15 -i $HOME/.ssh/id_ed25519"

echo "=== base-path / validator flag for every ACTIVE verdis unit ==="
for ip in 185.84.224.91 195.154.80.40 213.136.78.63; do
  echo "--- $ip"
  $SSH "root@$ip" 'for u in $(systemctl list-units "verdis*" --state=active --no-legend --no-pager | awk "{print \$1}" | grep "\.service$"); do
      line=$(systemctl show -p ExecStart --value "$u" | tail -1)
      bp=$(echo "$line" | grep -oP "(?<=--base-path=)[^ ]+")
      val=$(echo "$line" | grep -c -- "--validator")
      printf "%-32s bp=%-28s validator=%s\n" "$u" "${bp:-none}" "$val"
    done'
done

echo
echo "=== crash-looping verdis-node.service on Contabo ==="
$SSH root@213.136.78.63 'systemctl show -p ExecStart --value verdis-node.service | tail -1 | sed "s/--bootnodes[^ ]*//g"'
echo "--- last log ---"
$SSH root@213.136.78.63 'journalctl -u verdis-node.service -n 12 --no-pager'
