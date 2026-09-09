#!/usr/bin/env python
"""Phase 1 (READ-ONLY) with working sudo: inventory the real disk from rescue.

The rescue user needs a password for sudo, so feed it via stdin with `sudo -S`.
Nothing is modified in this script - it only identifies the real root filesystem
and reports what the host runs, so we can verify before writing the SSH key.
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
print("RESCUE LOGIN OK  (rescue RAM system, 62G RAM, Ubuntu 22.04.5)\n")


def sudo(cmd, quiet=False):
    """Run with sudo, supplying the password on stdin."""
    full = f"sudo -S -p '' {cmd}"
    stdin, o, e = cli.exec_command(full, timeout=180)
    stdin.write(PW + "\n")
    stdin.flush()
    out = o.read().decode(errors="replace").rstrip()
    err = e.read().decode(errors="replace").rstrip()
    if not quiet:
        if out:
            print(out)
        if err:
            print("  stderr:", err[:300])
    return out


print("=== block devices ===")
sudo("lsblk -o NAME,SIZE,FSTYPE,LABEL,MOUNTPOINT")

print("\n=== blkid (filesystems present on disk) ===")
sudo("blkid")

print("\n=== software RAID ===")
sudo("cat /proc/mdstat")

print("\n=== LVM ===")
sudo("bash -c 'pvs 2>/dev/null; vgs 2>/dev/null; lvs 2>/dev/null'")

print("\n=== currently mounted (rescue should have nothing from the real disk) ===")
sudo("bash -c \"mount | grep -E '^/dev' | head -10\"")
