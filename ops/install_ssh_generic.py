#!/usr/bin/env python
"""Install our SSH pubkey on a freshly created host, verify key-only login,
then rotate the root password that was exposed in chat.

Usage: python install_ssh_generic.py <host> <initial_pw_file> <label>
"""
import os
import sys
import secrets
import string
import paramiko

if len(sys.argv) < 4:
    print("usage: install_ssh_generic.py <host> <initial_pw_file> <label>")
    raise SystemExit(2)

HOST, PW_IN, LABEL = sys.argv[1], sys.argv[2], sys.argv[3]
USER = "root"
SECRETS_DIR = os.path.join(os.environ["LOCALAPPDATA"], "hermes", "profiles", "verdis", "secrets")
PW_OUT = os.path.join(SECRETS_DIR, f"{LABEL}_root.txt")
PUB = os.path.expanduser("~/.ssh/id_ed25519.pub")
PRIV = os.path.expanduser("~/.ssh/id_ed25519")

pubkey = open(PUB).read().strip()
initial_pw = open(PW_IN).read().strip()
print(f"target {USER}@{HOST}  ({LABEL})")

cli = paramiko.SSHClient()
cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
cli.connect(HOST, username=USER, password=initial_pw, timeout=40,
            allow_agent=False, look_for_keys=False)
print("PASSWORD LOGIN: OK")


def run(cmd, quiet=False):
    _i, o, e = cli.exec_command(cmd, timeout=120)
    out = o.read().decode(errors="replace").strip()
    err = e.read().decode(errors="replace").strip()
    rc = o.channel.recv_exit_status()
    if not quiet:
        if out:
            print(out)
        if err:
            print("stderr:", err)
    return rc, out, err


print("\n=== host identity ===")
for c in ["hostname", "grep PRETTY /etc/os-release", "uptime -s",
          "ip -4 addr show scope global | grep inet", "nproc",
          "free -g | sed -n 2p", "df -h / | tail -1"]:
    run(c)

print("\n=== pre-existing chain software? ===")
run("ls /opt 2>/dev/null | head -20 || true")
run("systemctl list-units 'verdis*' --all --no-legend --no-pager 2>/dev/null | head || echo 'no verdis units'")
run("pgrep -af 'verdis|substrate|polkadot' || echo 'no chain process'")
run("ss -tlnp 2>/dev/null | grep -E ':(3033[0-9]|99[34][0-9])' || echo 'no chain ports listening'")

print("\n=== installing pubkey ===")
run("mkdir -p /root/.ssh && chmod 700 /root/.ssh")
field = pubkey.split()[1]
rc, _, _ = run(f"grep -qF '{field}' /root/.ssh/authorized_keys 2>/dev/null", quiet=True)
if rc == 0:
    print("key already present")
else:
    sftp = cli.open_sftp()
    try:
        try:
            existing = sftp.open("/root/.ssh/authorized_keys").read().decode()
        except IOError:
            existing = ""
        merged = (existing.rstrip("\n") + "\n" + pubkey + "\n").lstrip("\n")
        fh = sftp.open("/root/.ssh/authorized_keys", "w")
        fh.write(merged)
        fh.close()
        sftp.chmod("/root/.ssh/authorized_keys", 0o600)
    finally:
        sftp.close()
    print("key appended")

run("chmod 600 /root/.ssh/authorized_keys; ssh-keygen -lf /root/.ssh/authorized_keys | tail -3")
run("sshd -t && echo 'sshd config OK'")

# rotate exposed password
alphabet = string.ascii_letters + string.digits + "!@%^_-+="
newpw = "".join(secrets.choice(alphabet) for _ in range(28))
rc, _, _ = run(f"printf '%s\\n%s\\n' '{newpw}' '{newpw}' | passwd root >/dev/null 2>&1 && echo ROTATED", quiet=True)
cli.close()

if rc == 0:
    os.makedirs(SECRETS_DIR, exist_ok=True)
    with open(PW_OUT, "w") as fh:
        fh.write(newpw + "\n")
    try:
        os.chmod(PW_OUT, 0o600)
    except Exception:
        pass
    print(f"\nROOT PASSWORD ROTATED -> {PW_OUT}")
else:
    print("\nWARNING: rotation unconfirmed - exposed password may still work")

print("\n=== verify KEY-ONLY login ===")
v = paramiko.SSHClient()
v.set_missing_host_key_policy(paramiko.AutoAddPolicy())
v.connect(HOST, username=USER, key_filename=PRIV, timeout=40,
          allow_agent=False, look_for_keys=False)
_i, o, _e = v.exec_command("hostname; id -un; echo KEYAUTH_CONFIRMED", timeout=30)
print(o.read().decode().strip())
v.close()
