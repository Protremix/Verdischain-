#!/usr/bin/env bash
# Install a per-host watchdog that restarts a dead mainnet validator automatically.
#
# Why this is the single most valuable thing left: the authority set is 21, threshold
# 15, we hold exactly 15 keys, and NO new validator can be added (all balances sit on
# keyless PalletId accounts, no Sudo, no Council keys). So one dead node = finality
# stops. It is fully recoverable by restarting the node - the risk is not noticing.
#
# The watchdog only ever RESTARTS a unit that systemd already considers failed or
# inactive. It never touches a healthy node, never changes flags, and never starts
# anything that was deliberately disabled.

set -uo pipefail
KEY=$HOME/.ssh/id_ed25519
SSH="ssh -o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=15 -i $KEY"

for ip in 185.84.224.91 195.154.80.40 213.136.78.63; do
  echo "===================================================================="
  echo "$ip"
  echo "===================================================================="
  $SSH "root@$ip" 'bash -s' <<'REMOTE' 2>&1
set -uo pipefail

cat > /usr/local/bin/verdis-watchdog.sh <<'WD'
#!/usr/bin/env bash
# Restart any mainnet validator unit that is enabled but not running.
# Finality threshold is 15 of 21 with exactly 15 keys held, so a single dead
# validator halts finality. Recovery is a restart; do it without waiting for a human.
LOG=/var/log/verdis-watchdog.log
ts() { date -u '+%Y-%m-%d %H:%M:%S'; }

for u in $(systemctl list-units 'verdis-validator*' --all --no-legend --no-pager 2>/dev/null | awk '{print $1}' | grep '\.service$'); do
  # only units meant to be running
  [ "$(systemctl is-enabled "$u" 2>/dev/null)" = "enabled" ] || continue
  st=$(systemctl is-active "$u" 2>/dev/null)
  [ "$st" = "active" ] && continue
  [ "$st" = "activating" ] && continue   # give slow archive starts a chance

  echo "$(ts) $u is $st - restarting" >> "$LOG"
  systemctl reset-failed "$u" 2>/dev/null
  systemctl restart "$u" 2>/dev/null

  ok=no
  for i in $(seq 1 24); do
    sleep 5
    [ "$(systemctl is-active "$u")" = "active" ] && { ok=yes; break; }
  done
  if [ "$ok" = yes ]; then
    echo "$(ts) $u recovered" >> "$LOG"
  else
    echo "$(ts) $u FAILED TO RECOVER - needs a human" >> "$LOG"
    journalctl -u "$u" -n 5 --no-pager 2>/dev/null | tail -5 >> "$LOG"
  fi
done

# keep the log small
[ -f "$LOG" ] && tail -500 "$LOG" > "$LOG.tmp" 2>/dev/null && mv "$LOG.tmp" "$LOG"
WD
chmod +x /usr/local/bin/verdis-watchdog.sh

cat > /etc/systemd/system/verdis-watchdog.service <<'UNIT'
[Unit]
Description=Restart dead Verdis mainnet validators (finality has zero headroom)

[Service]
Type=oneshot
ExecStart=/usr/local/bin/verdis-watchdog.sh
UNIT

cat > /etc/systemd/system/verdis-watchdog.timer <<'TIMER'
[Unit]
Description=Run the Verdis validator watchdog every 2 minutes

[Timer]
OnBootSec=3min
OnUnitActiveSec=2min
AccuracySec=15s

[Install]
WantedBy=timers.target
TIMER

systemctl daemon-reload
systemctl enable --now verdis-watchdog.timer >/dev/null 2>&1
echo "  timer: $(systemctl is-active verdis-watchdog.timer) / enabled=$(systemctl is-enabled verdis-watchdog.timer 2>/dev/null)"

# prove it does nothing when everything is healthy
/usr/local/bin/verdis-watchdog.sh
echo "  dry run on a healthy host wrote: $(wc -l < /var/log/verdis-watchdog.log 2>/dev/null || echo 0) log lines (0 = nothing touched)"
echo "  validators still active: $(systemctl list-units 'verdis-validator*' --state=active --no-legend --no-pager | wc -l)"
echo "  next run: $(systemctl list-timers verdis-watchdog.timer --no-pager 2>/dev/null | sed -n 2p | awk '{print $1, $2, $3}')"
REMOTE
  echo
done
