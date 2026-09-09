#!/usr/bin/env bash
# Fix bootnodes on 185.84.224.91 only.
#
# Why the generic script failed here: v18 and v19 already carry a 10-hardening.conf
# drop-in (from removing --unsafe-rpc-external earlier today). systemctl show then
# reports SEVERAL ExecStart entries - the reset (empty) plus the drop-in's. Taking
# `head -1` grabbed the wrong argv, so the generated line lost its bootnodes and the
# script correctly self-reverted.
#
# Correct approach: take the LAST argv[] reported, which is the effective one, and
# write the new drop-in with a higher prefix (20-) so it wins over 10-hardening.

set -uo pipefail
KEY=$HOME/.ssh/id_ed25519
B1="/ip4/195.154.80.40/tcp/30333/p2p/12D3KooWQXtFadPxGmFRuEKKXpQWjQjSBooy6g4BhRHJQbiDjgfW"
B2="/ip4/213.136.78.63/tcp/30333/p2p/12D3KooWSLhcUfZPEuh7h6JPs6yG5a1bMBmtwTQ1bnp56asoW869"
B3="/ip4/185.84.224.91/tcp/30334/p2p/12D3KooWAyGAVHJ5BuJXFgSrvrUyLuhswCNuN65gsi7tzX3TwxNU"

ssh -o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=15 -i "$KEY" \
    root@185.84.224.91 "B1='$B1' B2='$B2' B3='$B3' bash -s" <<'REMOTE' 2>&1
set -uo pipefail
MYIP=185.84.224.91

echo "=== existing drop-ins ==="
ls -1 /etc/systemd/system/verdis*.service.d/*.conf 2>/dev/null | sed 's/^/  /' || echo "  none"

for u in verdis-validator-v18.service verdis-validator-v19.service verdis-validator.service; do
  systemctl list-units "$u" --all --no-legend --no-pager >/dev/null 2>&1 || continue

  # LAST argv[] is the effective ExecStart after all drop-ins
  argv=$(systemctl show -p ExecStart --value "$u" | grep -oP 'argv\[\]=\K[^;]+' | tail -1 | sed 's/ *$//')
  if [ -z "$argv" ]; then printf "  %-28s NO ExecStart, skip\n" "$u"; continue; fi

  myport=$(echo "$argv" | grep -oP '(?<=--port[= ])[0-9]+' | head -1)
  list=""
  for b in "$B1" "$B2" "$B3"; do
    bip=$(echo "$b" | cut -d/ -f3); bport=$(echo "$b" | cut -d/ -f5)
    [ "$bip" = "$MYIP" ] && [ "$bport" = "${myport:-0}" ] && continue
    list="$list --bootnodes=$b"
  done

  cleaned=$(echo "$argv" | sed 's/--bootnodes=[^ ]*//g' | tr -s ' ' | sed 's/ *$//')
  d="/etc/systemd/system/${u}.d"; mkdir -p "$d"
  { echo "[Service]"; echo "ExecStart="; echo "ExecStart=$cleaned$list"; } > "$d/20-bootnodes.conf"
  printf "  %-28s written (port=%s)\n" "$u" "${myport:-?}"
done

systemctl daemon-reload
echo
echo "=== verification (effective ExecStart) ==="
bad=0
for u in verdis-validator-v18.service verdis-validator-v19.service verdis-validator.service; do
  eff=$(systemctl show -p ExecStart --value "$u" | grep -oP 'argv\[\]=\K[^;]+' | tail -1)
  nb=$(echo "$eff" | grep -o '\-\-bootnodes=' | wc -l)
  v=$(echo "$eff" | grep -c -- '--validator'); c=$(echo "$eff" | grep -c -- '--chain')
  p=$(echo "$eff" | grep -c -- '--port')
  unsafe=$(echo "$eff" | grep -c -- '--unsafe-rpc-external\|--rpc-methods=unsafe')
  if [ "$v" -ge 1 ] && [ "$c" -ge 1 ] && [ "$p" -ge 1 ] && [ "$nb" -ge 2 ] && [ "$unsafe" -eq 0 ]; then
    printf "  %-28s OK   bootnodes=%s unsafe=%s\n" "$u" "$nb" "$unsafe"
  else
    printf "  %-28s BAD  val=%s chain=%s port=%s boot=%s unsafe=%s\n" "$u" "$v" "$c" "$p" "$nb" "$unsafe"
    bad=$(( bad + 1 ))
  fi
done

if [ "$bad" -gt 0 ]; then
  echo "  *** reverting 20-bootnodes.conf on this host ***"
  rm -f /etc/systemd/system/verdis*.service.d/20-bootnodes.conf
  systemctl daemon-reload
  echo "  reverted - hardening drop-ins left intact"
else
  echo "  all 3 valid; applies on next restart (nothing restarted)"
fi

echo
echo "=== nodes still running ==="
for u in verdis-validator verdis-validator-v18 verdis-validator-v19; do
  printf "  %-24s %s\n" "$u" "$(systemctl is-active $u)"
done
REMOTE
