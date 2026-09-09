#!/usr/bin/env python
"""REVERT the testnet-banner edits. They were wrong.

The user's correction: the site says TESTNET deliberately, because Verdis has NOT
publicly launched mainnet and has not passed the external (Halborn) audit yet. The
banner "Not mainnet. Not investor-ready." is an intentional legal and positioning
disclaimer, not a stale label. Changing it to "MAINNET LIVE" made the site claim
something the project has not earned yet - the most damaging kind of wrong text for an
L1, in the opposite direction from what I assumed.

Restore every HTML file from the backup this session created, then verify the original
wording is back in place, byte-for-byte where possible.

Kept (these were genuine defects, unrelated to positioning):
  * the /api/v1 and /rpc nginx routes - the frontend was receiving HTML instead of JSON
  * the API reading a real chain instead of a dead testnet port
Those are questions of "does the page work at all", not of what the project claims.
Whether the explorer should display mainnet or testnet data is a decision for the user,
asked separately - not something to change unilaterally.
"""
import os
import subprocess
import time

HOST = "91.98.160.145"
KEY = os.path.expanduser("~/.ssh/id_ed25519")
ROOT = "/var/www/verdiscan"


def ssh(cmd, timeout=280):
    p = subprocess.run(
        ["ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no",
         "-o", "ConnectTimeout=15", "-i", KEY, f"root@{HOST}", cmd],
        capture_output=True, text=True, timeout=timeout)
    return p.stdout.strip()


print("=" * 70)
print("RESTORING HTML FROM THIS SESSION'S BACKUPS")
print("=" * 70)

# Backups made minutes ago by fix_explorer_content.py: *.bak-20260907-2100xx
baks = ssh(f"find {ROOT} -name '*.bak-20260907-21*' -o -name '*.bak-loading-20260907-21*' "
           f"2>/dev/null | sort")
files = [b for b in baks.splitlines() if b.strip()]
print(f"  backups found: {len(files)}")

restored = 0
for bak in files:
    # strip the .bak-... suffix to get the original path
    orig = bak.rsplit(".bak-", 1)[0]
    if not ssh(f"test -f '{bak}' && echo y"):
        continue
    ssh(f"cp '{bak}' '{orig}'")
    restored += 1
print(f"  restored: {restored} file(s)")

print("\n=== confirming the original wording is back ===")
for pat, label in (("currently in testnet phase", "testnet banner"),
                   ("Not investor-ready", "'Not investor-ready'"),
                   ("Testnet Live", "'Testnet Live' pill")):
    n = ssh(f"grep -rl '{pat}' {ROOT} --include='*.html' 2>/dev/null "
            f"| grep -v _backup | grep -v -- '-bak' | wc -l")
    print(f"  {label:<26} present in {n} file(s)")

for pat in ("MAINNET LIVE", "mainnet is live", "Mainnet Live"):
    n = ssh(f"grep -rl '{pat}' {ROOT} --include='*.html' 2>/dev/null "
            f"| grep -v _backup | grep -v -- '-bak' | wc -l")
    print(f"  my wording '{pat}': {n} file(s) (should be 0)")

print("\n=== live pages ===")
for url in ("https://verdischain.com", "https://explorer.verdischain.com"):
    out = subprocess.run(
        ["curl", "-s", "-m", "20", url], capture_output=True, text=True, timeout=60).stdout
    code = subprocess.run(
        ["curl", "-s", "-o", os.devnull, "-w", "%{http_code}", "-m", "20", url],
        capture_output=True, text=True, timeout=60).stdout
    banner = "TESTNET banner present" if "currently in testnet phase" in out else "banner MISSING"
    mine = "MY WORDING STILL THERE" if "mainnet is live" in out else "my wording gone"
    print(f"  {url:<38} {code}  {banner}  {mine}")

# clean up the backups I created, now that they are restored
print("\n=== cleaning up my backup files ===")
n = ssh(f"find {ROOT} -name '*.bak-20260907-21*' -delete -print 2>/dev/null | wc -l")
print(f"  removed {n} backup file(s)")
