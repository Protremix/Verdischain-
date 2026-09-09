#!/usr/bin/env python
"""Move 4 of the 6 newly-deployed validators from Contabo to 195.154.80.40, so that
losing any single HOST no longer stops finality.

The real risk measured after deployment:
    185.84.224.91   3 validators   -> if it dies, 18 remain, survives
    195.154.80.40   4 validators   -> if it dies, 17 remain, survives
    213.136.78.63  14 validators   -> if it dies,  7 remain, FINALITY STOPS

Threshold is 15 of 21, so no host may hold more than 6. Target layout:
    185.84.224.91   3  (+0)
    195.154.80.40   8  (+4)   <- takes v18b, v19b, v20b, v21b
    213.136.78.63  10  (-4)
Then the worst single-host loss leaves 11... still below 15.

Correct target: no host above 6. With only 3 usable hosts and 21 validators that is
impossible (3*6=18 < 21). So the honest goal here is to make the LARGEST host
survivable, which needs a 4th host. 5.223.77.19 (Hetzner Singapore, glibc 2.43, same
as Contabo, verdis binary already present) is the candidate.

This script ONLY measures and prints the plan plus the binary/spec compatibility for
the 4th host. Moving a validator means: stop it on A, copy keystore to B, start on B,
verify no equivocation - and it must be done one at a time with the key existing in
exactly one place at any moment. That is done by move_one_validator.py after review.
"""
import os, subprocess

KEY = os.path.expanduser("~/.ssh/id_ed25519")
HOSTS = {"185.84.224.91": "HostKey DE", "195.154.80.40": "Online.net",
         "213.136.78.63": "Contabo", "5.223.77.19": "Hetzner SIN"}


def sh(host, cmd, timeout=150):
    p = subprocess.run(
        ["ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no",
         "-o", "ConnectTimeout=15", "-i", KEY, f"root@{host}", cmd],
        capture_output=True, text=True, timeout=timeout)
    return p.stdout.strip()


print("=== current distribution ===")
counts = {}
for ip in ("185.84.224.91", "195.154.80.40", "213.136.78.63"):
    n = sh(ip, "systemctl list-units 'verdis-validator*' 'verdis-v??b*' "
               "--state=active --no-legend --no-pager | wc -l")
    counts[ip] = int(n or 0)
total = sum(counts.values())
TH = 15
print(f"  total={total} threshold={TH}")
for ip, n in counts.items():
    rem = total - n
    verdict = "survives" if rem >= TH else "FINALITY STOPS"
    print(f"  {ip:<16} {HOSTS[ip]:<12} {n:>2}  -> lose it: {rem} remain, {verdict}")

max_per_host = total - TH
print(f"\n  no host may hold more than {max_per_host} validators")
print(f"  hosts needed at {max_per_host} each: {-(-total // max_per_host)}")

print("\n=== 4th host viability: 5.223.77.19 (Hetzner Singapore) ===")
out = sh("5.223.77.19", "echo \"os=$(grep -oP 'PRETTY_NAME=\\\"\\K[^\\\"]+' /etc/os-release)\"; "
                        "echo \"glibc=$(ldd --version|head -1|grep -oP '[0-9]+\\.[0-9]+$')\"; "
                        "echo \"cores=$(nproc) ram_free=$(free -g|awk 'NR==2{print $7}')G "
                        "load=$(cut -d' ' -f1 /proc/loadavg)\"; "
                        "echo \"disk=$(df -h /|tail -1|awk '{print $4}')\"; "
                        "echo \"binary=$(stat -c%s /usr/local/bin/verdis 2>/dev/null||echo MISSING)\"; "
                        "echo \"binary_needs=$(objdump -T /usr/local/bin/verdis 2>/dev/null|grep -oP 'GLIBC_[0-9.]+'|sort -V|tail -1)\"; "
                        "echo \"running=$(pgrep -cf local/bin/verdis)\"; "
                        "echo \"chain_of_running=$(curl -s -m 5 -H 'Content-Type: application/json' "
                        "-d '{\\\"jsonrpc\\\":\\\"2.0\\\",\\\"id\\\":1,\\\"method\\\":\\\"system_chain\\\",\\\"params\\\":[]}' "
                        "http://localhost:9933 2>/dev/null | grep -oP 'result\\\":\\\"\\K[^\\\"]+')\"; "
                        "echo \"spec_present=$(ls /data/verdis-chain/chain-specs/mainnet-raw.json 2>/dev/null||echo NO)\"")
for line in out.split("\n"):
    print(f"  {line}")

print("\n=== does the mainnet spec exist there, and is it the right one? ===")
print(" ", sh("5.223.77.19", "find / -maxdepth 5 -name 'mainnet-raw*.json' 2>/dev/null | "
                             "while read f; do echo \"$(sha256sum $f|cut -c1-16) $f\"; done | head -5"))
print("  wanted: aca92919e13da10f")

print("\n=== PLAN ===")
print(f"""
  Problem: Contabo holds {counts['213.136.78.63']} of {total}. Losing it leaves
  {total - counts['213.136.78.63']} < {TH} and finality stops. No single host may exceed {max_per_host}.

  Step 1: bring 5.223.77.19 into the mainnet as a 4th validator host
          (copy the verified spec, it already has the binary and matching glibc)
  Step 2: move validators one at a time until every host is at or below {max_per_host}:
            185.84.224.91  3 -> 5
            195.154.80.40  4 -> 6
            213.136.78.63 14 -> 6
            5.223.77.19    0 -> 4
          worst single-host loss then leaves {total - max_per_host} >= {TH}: finality survives
  Step 3: re-run the keystore backup and the gap analysis

  Each move: stop on source, copy keystore, start on target, confirm the key exists in
  exactly ONE place, watch equivocation and finality. One at a time, never two.
""")
