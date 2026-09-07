#!/usr/bin/env python
"""Phase 1 (READ-ONLY): log into the Online.net rescue system on 195.154.80.40,
identify the real root filesystem, and inventory it WITHOUT modifying anything.

Rescue boots Ubuntu in RAM; the real disks are present but unmounted. Before
touching authorized_keys we must be certain which partition is the real root,
and we want to see what validators this host actually runs (authority count and
key duplication risk are the open questions on mainnet).
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
print("RESCUE LOGIN OK\n")


def run(cmd, sudo=True, quiet=False):
    full = f"sudo -n {cmd}" if sudo else cmd
    _i, o, e = cli.exec_command(full, timeout=120)
    out = o.read().decode(errors="replace").rstrip()
    err = e.read().decode(errors="replace").rstrip()
    if not quiet:
        if out:
            print(out)
        if err and "sudo" not in err.lower():
            print("stderr:", err)
    return out


print("=== rescue environment (this is the RAM system, not the disk) ===")
run("hostname", sudo=False)
run("grep PRETTY /etc/os-release", sudo=False)
run("uptime -s", sudo=False)
run("nproc && free -g | sed -n 2p", sudo=False)

print("\n=== block devices ===")
run("lsblk -o NAME,SIZE,FSTYPE,LABEL,MOUNTPOINT")

print("\n=== partitions with filesystems ===")
run("blkid")

print("\n=== software RAID? (dedibox often uses md) ===")
run("cat /proc/mdstat")

print("\n=== LVM? ===")
run("pvs 2>/dev/null; vgs 2>/dev/null; lvs 2>/dev/null")
