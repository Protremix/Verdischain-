#!/usr/bin/env python
"""Phase 3 (READ-ONLY): inspect the 4 validators on 195.154.80.40 for the two
risks that matter, then report. Still no writes.

Confirmed layout:
  /mnt/a = real root (md127p1), hostname sd-138654
  /data  lives on md125p1 (444G) - validator databases and keystores are there
Validators: verdis-validator (NL), -v15, -v16, -v17  => 4 authorities on this host

Checks:
  1. session keys per node -> compare against the 3 nodes on 185.84.224.91
     (a key present on two hosts = equivocation = slashing)
  2. unsafe RPC flags -> same hole we closed on the other host
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
    if not quiet and out:
        print(out)
    if not quiet and err:
        print("  stderr:", err[:200])
    return out


# /data is a separate array; mount it so we can see keystores
print("=== mounting /data array read-only ===")
sudo("mkdir -p /mnt/data")
r = sudo("mount -o ro /dev/md125p1 /mnt/data 2>&1; echo rc=$?", quiet=True)
print("  md125p1 ->", "mounted" if "rc=0" in r else r[:80])
print(sudo("bash -c 'ls /mnt/data | head -10'", quiet=True))

print("\n=== FULL unit definitions (flags + chain spec + ports) ===")
for u in ["verdis-validator", "verdis-validator-v15", "verdis-validator-v16", "verdis-validator-v17"]:
    print(f"\n--- {u}")
    sudo(f"bash -c \"grep -vE '^\\s*#|^$' /mnt/a/etc/systemd/system/{u}.service | tr -s ' '\"")

print("\n=== UNSAFE RPC EXPOSURE on this host? ===")
sudo("bash -c \"grep -l 'unsafe-rpc-external\\|rpc-methods=unsafe\\|rpc-external' /mnt/a/etc/systemd/system/verdis*.service 2>/dev/null || echo '  none - clean'\"")

print("\n=== keystores on /data (session keys per node) ===")
ks = sudo("bash -c 'find /mnt/data /mnt/a/opt -maxdepth 7 -type d -name keystore 2>/dev/null'", quiet=True)
print(ks or "  none found")
for d in [x for x in ks.splitlines() if x.strip()]:
    n = sudo(f"bash -c 'ls -1 {d} 2>/dev/null | wc -l'", quiet=True)
    print(f"\n  {d}  ({n.strip()} key files)")
    # print key TYPE prefixes + pubkey tails so we can compare across hosts
    sudo(f"bash -c 'ls -1 {d} 2>/dev/null | head -8 | sed \"s/^/      /\"'")

print("\n=== which chain spec + genesis do these use ===")
sudo("bash -c \"grep -ho '\\-\\-chain[= ][^ ]*' /mnt/a/etc/systemd/system/verdis*.service | sort -u\"")

print("\n=== enabled at boot? (will they auto-start when we return to normal) ===")
sudo("bash -c 'ls -la /mnt/a/etc/systemd/system/multi-user.target.wants/ | grep -i verdis'")
