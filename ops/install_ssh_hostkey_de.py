#!/usr/bin/env python
"""Install our SSH pubkey on HostKey DE 185.84.224.91 (freshly reinstalled),
then verify key-only login works. Password is read from a file, never hardcoded.
Also rotates the root password to a freshly generated one and stores it locally 0600.
"""
import os
import sys
import secrets
import string
import paramiko

HOST = "185.84.224.91"
USER = "root"
SECRETS_DIR = os.path.join(os.environ["LOCALAPPDATA"], "hermes", "profiles", "verdis", "secrets")
PW_IN = os.path.join(SECRETS_DIR, "hostkey_de_root_initial.txt")
PW_OUT = os.path.join(SECRETS_DIR, "hostkey_de_185.84.224.91_root.txt")
PUBKEY_PATH = os.path.expanduser("~/.ssh/id_ed25519.pub")

pubkey = open(PUBKEY_PATH).read().strip()
initial_pw = open(PW_IN).read().strip()

print(f"target {USER}@{HOST}")
print(f"pubkey {pubkey.split()[-1]} ({pubkey.split()[0]})")

cli = paramiko.SSHClient()
cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
cli.connect(HOST, username=USER, password=initial_pw, timeout=30,
            allow_agent=False, look_for_keys=False)
print("PASSWORD LOGIN: OK")


def run(cmd, quiet=False):
    _in, out, err = cli.exec_command(cmd, timeout=90)
    o = out.read().decode(errors="replace").strip()
    e = err.read().decode(errors="replace").strip()
    rc = out.channel.recv_exit_status()
    if not quiet:
        if o:
            print(o)
        if e:
            print("stderr:", e)
    return rc, o, e


print("\n=== identity / state before touching anything ===")
for c in ["hostname", "cat /etc/os-release | head -2", "uptime",
          "ip -4 addr show scope global | grep inet",
          "df -h / | tail -1", "nproc; free -g | head -2"]:
    run(c)

print("\n=== is there any verdis/substrate remnant after reinstall? ===")
run("ls -la /opt 2>/dev/null | head -20")
run("systemctl list-units 'verdis*' --all --no-legend --no-pager 2>/dev/null | head || echo 'no verdis units'")
run("ss -tlnp 2>/dev/null | grep -E ':(3033[0-9]|993[0-9])' || echo 'nothing listening on substrate ports'")
run("pgrep -af 'verdis|substrate|polkadot' || echo 'no chain process'")

print("\n=== installing pubkey ===")
run("mkdir -p /root/.ssh && chmod 700 /root/.ssh")
# append only if absent
key_field = pubkey.split()[1]
rc, _, _ = run(f"grep -qF '{key_field}' /root/.ssh/authorized_keys 2>/dev/null", quiet=True)
if rc == 0:
    print("key already present")
else:
    sftp = cli.open_sftp()
    try:
        try:
            existing = sftp.open("/root/.ssh/authorized_keys").read().decode()
        except IOError:
            existing = ""
        new = (existing.rstrip("\n") + "\n" + pubkey + "\n").lstrip("\n")
        f = sftp.open("/root/.ssh/authorized_keys", "w")
        f.write(new)
        f.close()
        sftp.chmod("/root/.ssh/authorized_keys", 0o600)
    finally:
        sftp.close()
    print("key appended")

run("chmod 600 /root/.ssh/authorized_keys; wc -l < /root/.ssh/authorized_keys")
run("sshd -t && echo 'sshd config OK'")
run("grep -E '^(PubkeyAuthentication|PasswordAuthentication|PermitRootLogin)' /etc/ssh/sshd_config /etc/ssh/sshd_config.d/*.conf 2>/dev/null || echo 'defaults in use'")

# rotate the password that was exposed in chat
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
    print(f"\nROOT PASSWORD ROTATED -> stored at {PW_OUT}")
else:
    print("\nWARNING: password rotation did not confirm; exposed password may still be active")

print("\n=== verify KEY-ONLY login (no password) ===")
v = paramiko.SSHClient()
v.set_missing_host_key_policy(paramiko.AutoAddPolicy())
v.connect(HOST, username=USER, key_filename=os.path.expanduser("~/.ssh/id_ed25519"),
          timeout=30, allow_agent=False, look_for_keys=False)
_i, o, _e = v.exec_command("hostname; id -un; echo KEYAUTH_CONFIRMED", timeout=30)
print(o.read().decode().strip())
v.close()
