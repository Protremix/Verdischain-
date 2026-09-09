#!/usr/bin/env bash
# Close two audit findings that carry no risk to finality:
#   HIGH-1: SSH password auth enabled + fail2ban inactive on all three mainnet hosts.
#           Servers holding live validator private keys accept password logins with
#           no brute-force protection.
#   MEDIUM-2: verdis-validator.service on 185.84.224.91 is active but DISABLED, so
#           it would not come back after a reboot - and headroom is zero.
#
# Deliberately NOT touching: PasswordAuthentication is only disabled AFTER we prove
# key auth works from here, and sshd config is validated with `sshd -t` before reload.
# A broken sshd on a host we can only reach over SSH would be unrecoverable without
# rescue mode again.

set -uo pipefail
KEY=$HOME/.ssh/id_ed25519
SSH="ssh -o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=15 -i $KEY"

for ip in 185.84.224.91 195.154.80.40 213.136.78.63; do
  echo "===================================================================="
  echo "$ip"
  echo "===================================================================="
  $SSH "root@$ip" 'bash -s' <<'REMOTE' 2>&1
set -uo pipefail
export DEBIAN_FRONTEND=noninteractive

# ---- 1. prove key auth works before disabling passwords ----
nkeys=$(grep -c '^ssh-' /root/.ssh/authorized_keys 2>/dev/null || echo 0)
echo "  authorized_keys entries: $nkeys"
if [ "$nkeys" -lt 1 ]; then
  echo "  !! no keys in authorized_keys - refusing to disable password auth"
  exit 1
fi

# ---- 2. fail2ban ----
if ! command -v fail2ban-server >/dev/null 2>&1; then
  apt-get install -y -qq fail2ban >/dev/null 2>&1 && echo "  fail2ban installed" || echo "  fail2ban install FAILED"
fi
cat > /etc/fail2ban/jail.local <<'JAIL'
[DEFAULT]
bantime  = 3600
findtime = 600
maxretry = 5
backend  = systemd

[sshd]
enabled = true
port    = ssh
logpath = %(sshd_log)s
JAIL
systemctl enable fail2ban >/dev/null 2>&1
systemctl restart fail2ban >/dev/null 2>&1
sleep 3
echo "  fail2ban: $(systemctl is-active fail2ban) / enabled=$(systemctl is-enabled fail2ban 2>/dev/null)"
fail2ban-client status sshd 2>/dev/null | grep -E 'Currently banned|Total banned' | sed 's/^/    /'

# ---- 3. disable password auth, validated ----
cfg=/etc/ssh/sshd_config.d/99-verdis-hardening.conf
mkdir -p /etc/ssh/sshd_config.d
cat > "$cfg" <<'SSHCFG'
PasswordAuthentication no
PermitRootLogin prohibit-password
ChallengeResponseAuthentication no
KbdInteractiveAuthentication no
MaxAuthTries 4
SSHCFG

if sshd -t 2>/dev/null; then
  systemctl reload ssh 2>/dev/null || systemctl reload sshd 2>/dev/null
  sleep 2
  echo "  sshd reloaded"
  echo "    PasswordAuthentication: $(sshd -T 2>/dev/null | grep -i '^passwordauthentication' | awk '{print $2}')"
  echo "    PermitRootLogin:        $(sshd -T 2>/dev/null | grep -i '^permitrootlogin' | awk '{print $2}')"
else
  rm -f "$cfg"
  echo "  !! sshd config invalid - reverted, nothing changed"
fi

# ---- 4. enable validator units so they survive a reboot ----
echo "  --- autostart ---"
for u in $(systemctl list-units 'verdis*' --state=active --no-legend --no-pager 2>/dev/null | awk '{print $1}' | grep '\.service$'); do
  E=$(systemctl show -p ExecStart --value "$u" 2>/dev/null | grep -oP 'argv\[\]=\K[^;]+' | tail -1)
  echo "$E" | grep -q -- '--validator' || continue
  echo "$E" | grep -qP 'chain=?\S*mainnet' || continue
  en=$(systemctl is-enabled "$u" 2>/dev/null)
  if [ "$en" != "enabled" ]; then
    systemctl enable "$u" >/dev/null 2>&1
    printf "    %-28s %s -> %s\n" "$u" "$en" "$(systemctl is-enabled "$u" 2>/dev/null)"
  else
    printf "    %-28s already enabled\n" "$u"
  fi
done

# ---- 5. journal size cap so /var/log cannot fill the root fs again ----
mkdir -p /etc/systemd/journald.conf.d
cat > /etc/systemd/journald.conf.d/99-verdis-cap.conf <<'JC'
[Journal]
SystemMaxUse=500M
SystemKeepFree=2G
MaxRetentionSec=14day
JC
systemctl restart systemd-journald 2>/dev/null
echo "  journal capped at 500M (was unbounded)"
echo "  disk free now: $(df -h / | tail -1 | awk '{print $4}') ($(df -h / | tail -1 | awk '{print $5}') used)"

# ---- 6. still alive? ----
echo "  --- validators still running ---"
n=0
for u in $(systemctl list-units 'verdis*' --state=active --no-legend --no-pager 2>/dev/null | awk '{print $1}' | grep '\.service$'); do
  E=$(systemctl show -p ExecStart --value "$u" 2>/dev/null | grep -oP 'argv\[\]=\K[^;]+' | tail -1)
  echo "$E" | grep -q -- '--validator' && n=$((n+1))
done
echo "    active validators: $n"
REMOTE
  echo
done

echo "===================================================================="
echo "VERIFY: key auth still works on every host"
echo "===================================================================="
for ip in 185.84.224.91 195.154.80.40 213.136.78.63; do
  r=$($SSH "root@$ip" 'echo OK' 2>&1 | tail -1)
  printf "  %-16s %s\n" "$ip" "$r"
done
