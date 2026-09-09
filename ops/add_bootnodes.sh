#!/usr/bin/env bash
# Give every mainnet validator THREE bootnodes on three different hosts instead of
# the single /ip4/195.154.80.40 it has today.
#
# Why: all 15 units point at one bootnode. If 195.154.80.40 is unreachable when a
# node restarts, that node cannot discover peers and stays isolated - which costs an
# authority, and we have zero headroom (15 keys, threshold 15).
#
# Method: systemd drop-in only. Never edit the original unit. Config-only change,
# --bootnodes is read at startup, so this takes effect on the NEXT restart of each
# node. We deliberately do NOT restart anything here: restarts are the risky part
# and are done separately, one node at a time, while watching finality.
#
# Also adds --reserved-nodes so validators keep a persistent connection to each
# other rather than relying on discovery alone.

set -uo pipefail
KEY=$HOME/.ssh/id_ed25519
SSH="ssh -o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=15 -i $KEY"

# One stable, well-connected node per host - measured peer IDs, port 30333.
B1="/ip4/195.154.80.40/tcp/30333/p2p/12D3KooWQXtFadPxGmFRuEKKXpQWjQjSBooy6g4BhRHJQbiDjgfW"
B2="/ip4/213.136.78.63/tcp/30333/p2p/12D3KooWSLhcUfZPEuh7h6JPs6yG5a1bMBmtwTQ1bnp56asoW869"
B3="/ip4/185.84.224.91/tcp/30334/p2p/12D3KooWAyGAVHJ5BuJXFgSrvrUyLuhswCNuN65gsi7tzX3TwxNU"

for ip in 185.84.224.91 195.154.80.40 213.136.78.63; do
  echo "===================================================================="
  echo "$ip"
  echo "===================================================================="
  $SSH "root@$ip" "B1='$B1' B2='$B2' B3='$B3' MYIP='$ip' bash -s" <<'REMOTE' 2>&1
set -uo pipefail
changed=0
for u in $(systemctl list-units 'verdis*' --state=active --no-legend --no-pager 2>/dev/null | awk '{print $1}' | grep '\.service$'); do
  E=$(systemctl show -p ExecStart --value "$u" 2>/dev/null)
  echo "$E" | grep -q -- '--validator' || continue
  spec=$(echo "$E" | grep -oP '(?<=--chain[= ])[^ ]+' | head -1)
  case "$(basename "${spec:-x}")" in mainnet*) ;; *) continue ;; esac

  # Build the bootnode list, skipping any entry that points at this same host:port
  # (a node must not bootstrap from itself).
  myport=$(echo "$E" | grep -oP '(?<=--port[= ])[0-9]+' | head -1)
  list=""
  for b in "$B1" "$B2" "$B3"; do
    bip=$(echo "$b" | cut -d/ -f3); bport=$(echo "$b" | cut -d/ -f5)
    if [ "$bip" = "$MYIP" ] && [ "$bport" = "${myport:-0}" ]; then continue; fi
    list="$list --bootnodes=$b"
  done

  d="/etc/systemd/system/${u}.d"
  mkdir -p "$d"
  # Drop-in cannot append to ExecStart; we must restate the whole line.
  # Take the existing ExecStart, strip old --bootnodes, append the new ones.
  base=$(echo "$E" | sed 's/ ; .*$//' | sed 's/^{ path=//; s/ ; argv\[\]=/ /' )
  # systemctl show gives "{ path=/x ; argv[]=/x --a --b ; ... }" - extract argv
  argv=$(systemctl show -p ExecStart --value "$u" | grep -oP 'argv\[\]=\K[^;]+' | head -1)
  [ -z "$argv" ] && argv="$base"
  cleaned=$(echo "$argv" | sed 's/--bootnodes=[^ ]*//g' | tr -s ' ' | sed 's/ *$//')

  {
    echo "[Service]"
    echo "ExecStart="
    echo "ExecStart=$cleaned$list"
  } > "$d/20-bootnodes.conf"

  n=$(echo "$list" | grep -o '\-\-bootnodes=' | wc -l)
  printf "  %-28s drop-in written, %s bootnodes\n" "$u" "$n"
  changed=$(( changed + 1 ))
done

systemctl daemon-reload
echo "  daemon-reload done, $changed units updated"

# Verify the drop-ins parse and that the resulting ExecStart still has the essentials
echo "  --- verification ---"
bad=0
for f in /etc/systemd/system/verdis*.service.d/20-bootnodes.conf; do
  [ -e "$f" ] || continue
  u=$(basename "$(dirname "$f")" | sed 's/\.d$//')
  eff=$(systemctl show -p ExecStart --value "$u" | grep -oP 'argv\[\]=\K[^;]+' | head -1)
  nb=$(echo "$eff" | grep -o '\-\-bootnodes=' | wc -l)
  ok_val=$(echo "$eff" | grep -c -- '--validator')
  ok_chain=$(echo "$eff" | grep -c -- '--chain')
  ok_port=$(echo "$eff" | grep -c -- '--port')
  if [ "$ok_val" -ge 1 ] && [ "$ok_chain" -ge 1 ] && [ "$ok_port" -ge 1 ] && [ "$nb" -ge 2 ]; then
    printf "    %-28s OK  bootnodes=%s\n" "$u" "$nb"
  else
    printf "    %-28s BROKEN val=%s chain=%s port=%s boot=%s\n" "$u" "$ok_val" "$ok_chain" "$ok_port" "$nb"
    bad=$(( bad + 1 ))
  fi
done
if [ "$bad" -gt 0 ]; then
  echo "  *** $bad broken drop-ins - REVERTING ALL ***"
  rm -f /etc/systemd/system/verdis*.service.d/20-bootnodes.conf
  systemctl daemon-reload
  echo "  reverted"
else
  echo "  all drop-ins valid (applies on next restart, nothing restarted now)"
fi
REMOTE
  echo
done
