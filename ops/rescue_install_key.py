#!/usr/bin/env python
"""Phase 4 (THE WRITE): install our SSH pubkey on the real root filesystem of
195.154.80.40, verified and reversible.

Findings from the read-only phases:
  * real root = /dev/md127p1 (RAID1), hostname sd-138654, Ubuntu 22.04.5
  * /data     = /dev/md125p1 (444G, RAID1) holds validator DBs + keystores
  * 4 validators here: verdis-validator (NL), -v15, -v16, -v17, all enabled at boot
  * every keystore holds a DISTINCT gran/babe/acco triple -> NO key duplication
    with the 3 nodes on 185.84.224.91, so no equivocation/slashing risk
  * all 4 units DO carry unsafe RPC flags (same hole we closed on the other host)
  * existing authorized_keys has 2 keys (kYON..., VWx5...) - we APPEND, never replace

This script:
  1. remounts root read-write (rescue mounts it ro)
  2. backs up authorized_keys with a timestamp
  3. appends our pubkey only if absent
  4. verifies with ssh-keygen -lf that all keys are intact
  5. leaves the unsafe-RPC fix for AFTER we have SSH, so a mistake cannot
     strand the host without access
"""
import os
import time
import paramiko

HOST = "195.154.80.40"
USER = "rojs"
PW = open(os.path.join(os.environ["LOCALAPPDATA"], "hermes", "profiles", "verdis",
                      "secrets", "online_rescue_pw.txt")).read().strip()
PUB = open(os.path.expanduser("~/.ssh/verdis_contabo.pub")).read().strip()
PUB_OLD = open(os.path.expanduser("~/.ssh/id_ed25519.pub")).read().strip()
ROOT = "/mnt/a"

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


print("=== 1. remount root read-write ===")
print(sudo(f"mount -o remount,rw {ROOT} 2>&1; echo rc=$?", quiet=True))
w = sudo(f"bash -c 'touch {ROOT}/root/.arlo_write_test && echo WRITABLE && rm -f {ROOT}/root/.arlo_write_test'", quiet=True)
print("  root writable:", "YES" if "WRITABLE" in w else "NO -> " + w[:120])
if "WRITABLE" not in w:
    print("!! cannot write; aborting, nothing changed")
    raise SystemExit(1)

print("\n=== 2. backup existing authorized_keys ===")
ts = time.strftime("%Y%m%d-%H%M%S")
sudo(f"cp -a {ROOT}/root/.ssh/authorized_keys {ROOT}/root/.ssh/authorized_keys.bak-{ts}")
print(f"  backup: authorized_keys.bak-{ts}")
print("  keys BEFORE:")
sudo(f"ssh-keygen -lf {ROOT}/root/.ssh/authorized_keys | sed 's/^/    /'")

print("\n=== 3. append our keys (both, so either works) ===")
for label, key in [("new verdis_contabo", PUB), ("old selene-supervisor", PUB_OLD)]:
    field = key.split()[1]
    present = sudo(f"bash -c 'grep -qF \"{field}\" {ROOT}/root/.ssh/authorized_keys && echo YES || echo no'", quiet=True)
    if present.strip().endswith("YES"):
        print(f"  {label}: already present")
    else:
        sudo(f"bash -c \"printf '%s\\n' '{key}' >> {ROOT}/root/.ssh/authorized_keys\"", quiet=True)
        print(f"  {label}: appended")

sudo(f"chmod 600 {ROOT}/root/.ssh/authorized_keys")
sudo(f"chown 0:0 {ROOT}/root/.ssh/authorized_keys")

print("\n=== 4. verify ALL keys intact ===")
sudo(f"ssh-keygen -lf {ROOT}/root/.ssh/authorized_keys | sed 's/^/    /'")
print("\n  expecting to see:")
print("    SHA256:yzXJjpBb9I0F85GB6D6535yp1I+4E/kfq3pyv1tLM9Y  (new)")
print("    SHA256:8J/ldsp9qa3uiZAaktRvQkZzUNAl/a/MVEG9Lck3CNc  (old)")
print("    SHA256:kYON312yGKkWJ4BRh+vHGaAT2kmHSvHhce+dsZ93/F4  (pre-existing)")
print("    SHA256:VWx57mL6AGTRQJjm0vvZjg/kNz2EGZRFzbSd+yU3fMI  (pre-existing)")

print("\n=== 5. sanity: sshd on the real system permits pubkey + root ===")
sudo(f"bash -c \"grep -hiE '^(PermitRootLogin|PubkeyAuthentication|PasswordAuthentication)' {ROOT}/etc/ssh/sshd_config {ROOT}/etc/ssh/sshd_config.d/*.conf 2>/dev/null | sed 's/^/    /'\"")

print("\n=== 6. sync and unmount cleanly ===")
sudo("sync")
sudo(f"umount /mnt/data 2>/dev/null; umount /mnt/b 2>/dev/null; umount /mnt/c 2>/dev/null; echo unmounted-extras", quiet=True)
print(sudo(f"bash -c 'mount | grep -E \"md12[567]\" | sed \"s/^/    /\"'", quiet=True) or "    (root still mounted, fine)")
print("\nDONE - key installed on disk. Next: return the server to normal boot.")
