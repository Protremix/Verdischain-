#!/usr/bin/env python
"""Phase 2 (READ-ONLY): mount each RAID array read-only, find the real root
filesystem, and inventory the mainnet validators on it.

Layout found on 195.154.80.40:
  md127p1  20G   ext4   <- likely /  (root)
  md126p1  523M  ext4   <- likely /boot
  md125p1  444G  ext4   <- likely /data or /home
All arrays are auto-read-only, so mounting with -o ro is non-destructive.

Open questions this answers:
  * how many validator nodes does this host run (authority count vs threshold 15)
  * are any session keys duplicated with other hosts (equivocation / slashing risk)
  * is unsafe RPC exposed here like it was on 185.84.224.91
"""
import os
import paramiko

HOST = "195.154.80.40"
USER = "rojs"
PW = open(os.path.join(os.environ["LOCALAPPDATA"], "hermes", "profiles", "verdis",
                      "secrets", "online_rescue_pw.txt")).read().strip()

cli = paramiko.SSHClient()
cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
cli.connect(HOST, username=USER, password=PW, timeout=40,
            allow_agent=False, look_for_keys=False)


def sudo(cmd, quiet=False, timeout=180):
    stdin, o, e = cli.exec_command(f"sudo -S -p '' {cmd}", timeout=timeout)
    stdin.write(PW + "\n")
    stdin.flush()
    out = o.read().decode(errors="replace").rstrip()
    err = e.read().decode(errors="replace").rstrip()
    if not quiet:
        if out:
            print(out)
        if err:
            print("  stderr:", err[:200])
    return out


print("=== mounting each array READ-ONLY to identify root ===")
sudo("mkdir -p /mnt/a /mnt/b /mnt/c")
for dev, mp in [("/dev/md127p1", "/mnt/a"), ("/dev/md126p1", "/mnt/b"), ("/dev/md125p1", "/mnt/c")]:
    r = sudo(f"mount -o ro {dev} {mp} 2>&1 && echo MOUNTED", quiet=True)
    marker = sudo(f"bash -c 'ls {mp} | head -14 | tr \"\\n\" \" \"'", quiet=True)
    print(f"  {dev:16} -> {mp}  {'ok' if 'MOUNTED' in r else r[:60]}")
    print(f"      contents: {marker}")

print("\n=== which mount is the real ROOT? (has /etc/fstab + /root) ===")
root_mp = None
for mp in ["/mnt/a", "/mnt/b", "/mnt/c"]:
    has = sudo(f"bash -c '[ -f {mp}/etc/fstab ] && [ -d {mp}/root ] && echo YES || echo no'", quiet=True)
    print(f"  {mp}: {has}")
    if has.strip().endswith("YES") and root_mp is None:
        root_mp = mp
print(f"  -> ROOT = {root_mp}")

if not root_mp:
    print("!! could not identify root; aborting before any write")
    raise SystemExit(1)

print(f"\n=== fstab on {root_mp} ===")
sudo(f"cat {root_mp}/etc/fstab")

print(f"\n=== hostname / os of the real system ===")
sudo(f"bash -c 'cat {root_mp}/etc/hostname; grep PRETTY {root_mp}/etc/os-release'")

print("\n=== VALIDATOR UNITS on the real disk ===")
sudo(f"bash -c 'ls {root_mp}/etc/systemd/system/ | grep -i verdis'")

print("\n=== full ExecStart of each verdis unit (KEY DUPLICATION CHECK) ===")
sudo(f"bash -c 'grep -H \"ExecStart\\|--validator\\|--name\" {root_mp}/etc/systemd/system/verdis*.service 2>/dev/null | head -40'")

print("\n=== keystores present (how many authorities live here) ===")
sudo(f"bash -c 'find {root_mp}/opt {root_mp}/data {root_mp}/var/lib -maxdepth 6 -type d -name keystore 2>/dev/null | head -20'")

print("\n=== existing authorized_keys (BEFORE we touch it) ===")
sudo(f"bash -c 'ls -la {root_mp}/root/.ssh/ 2>/dev/null; echo ---; ssh-keygen -lf {root_mp}/root/.ssh/authorized_keys 2>/dev/null'")
