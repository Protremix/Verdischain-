#!/usr/bin/env python
"""Switch the LIVE Verdiscan API (verdis-api.service) from testnet to mainnet.

Correction to an earlier assumption: discan_api.py was NOT the explorer backend. The
real one is /opt/verdis-api/verdiscan_api.py - 2226 lines, 38 endpoints, running under
verdis-api.service on 127.0.0.1:4400 for 10 hours. It was already answering, but from
RPC_URL = http://127.0.0.1:9934, which is the TESTNET (genesis 0xf72f1241, block
185608, finalized 112557 - a 73k finality gap). Mainnet is 127.0.0.1:9960
(genesis 0x2284393d).

So the explorer's API was live but serving the wrong chain, and the frontend received
HTML because nginx never routed /api/v1 to it.

This script only changes the chain the API reads. Verify by GENESIS HASH, never by
chain name - a spec file can carry the right name and the wrong genesis, which is how
the v13m/v14m nodes ended up on a private fork.

Rollback: the file is backed up first; on any failed check the backup is restored and
the service restarted, so the API cannot be left pointing nowhere.
"""
import os
import subprocess
import sys
import time

HOST = "91.98.160.145"
KEY = os.path.expanduser("~/.ssh/id_ed25519")
APP = "/opt/verdis-api/verdiscan_api.py"
UNIT = "verdis-api"
OLD_RPC = "http://127.0.0.1:9934"
NEW_RPC = "http://127.0.0.1:9960"
MAINNET_GENESIS = "0x2284393d11797c1a06e8def6a48a79f9d8d7539c5386d9973fce852852817c8e"
TS = time.strftime("%Y%m%d-%H%M%S")


def ssh(cmd, timeout=280):
    p = subprocess.run(
        ["ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no",
         "-o", "ConnectTimeout=15", "-i", KEY, f"root@{HOST}", cmd],
        capture_output=True, text=True, timeout=timeout)
    return p.stdout.strip()


def api(path):
    return ssh(f"curl -s -m 15 http://127.0.0.1:4400{path} 2>/dev/null | head -c 220")


print("=" * 70)
print("BEFORE")
print("=" * 70)
print(f"  RPC_URL in code : {ssh(f'grep -m1 ^RPC_URL {APP}')}")
print(f"  service         : {ssh(f'systemctl is-active {UNIT}')}")
print(f"  /network/stats  : {api('/api/v1/network/stats')[:150]}")

# confirm which chain each port really is, by genesis
for port in (9934, 9960):
    g = ssh(f"""curl -s -m 10 -H 'Content-Type: application/json' """
            f"""-d '{{"jsonrpc":"2.0","id":1,"method":"chain_getBlockHash","params":[0]}}' """
            f"""http://127.0.0.1:{port} | grep -oP 'result":"\\K[^"]+'""")
    label = "MAINNET" if g == MAINNET_GENESIS else "not mainnet"
    print(f"  :{port} genesis {g[:20]}… {label}")

print("\n" + "=" * 70)
print("APPLY")
print("=" * 70)
ssh(f"cp {APP} {APP}.bak-{TS}")
print(f"  backup: {APP}.bak-{TS}")

n = ssh(f"grep -c '{OLD_RPC}' {APP}")
print(f"  occurrences of the testnet URL: {n}")
ssh(f"sed -i 's|{OLD_RPC}|{NEW_RPC}|g' {APP}")
# some code paths hardcode a testnet label in responses
ssh(f"""sed -i 's|"network": *"testnet"|"network": "mainnet"|g; """
    f"""s|"chain": *"Verdis Testnet"|"chain": "Verdis Mainnet"|g' {APP}""")
print(f"  RPC_URL now: {ssh(f'grep -m1 ^RPC_URL {APP}')}")
left = ssh(f"grep -c '9934' {APP}")
print(f"  any 9934 left: {left}")

ssh(f"systemctl restart {UNIT}")
time.sleep(9)
state = ssh(f"systemctl is-active {UNIT}")
print(f"  service: {state}")

print("\n" + "=" * 70)
print("VERIFY")
print("=" * 70)
ok = True
if state != "active":
    print("  service is not active - rolling back")
    ok = False
else:
    stats = api("/api/v1/network/stats")
    print(f"  /api/v1/network/stats -> {stats[:200]}")
    # the mainnet is around block 50k with a finality lag of a few blocks;
    # the testnet was at 185k with a 73k gap. Use that to tell them apart.
    import re
    m = re.search(r'"block_height":(\d+).*?"finalized_block":(\d+)', stats)
    if not m:
        print("  could not parse block height - rolling back")
        ok = False
    else:
        best, fin = int(m.group(1)), int(m.group(2))
        gap = best - fin
        print(f"  best={best} finalized={fin} gap={gap}")
        if best > 120000 or gap > 500:
            print("  STILL TESTNET (height/gap too large) - rolling back")
            ok = False
        else:
            print("  looks like mainnet: plausible height and small finality gap")

if not ok:
    ssh(f"cp {APP}.bak-{TS} {APP} && systemctl restart {UNIT}")
    time.sleep(6)
    print(f"  rolled back; service: {ssh(f'systemctl is-active {UNIT}')}")
    sys.exit(1)

print("\n  --- sample endpoints ---")
for p in ("/api/v1/block/last", "/api/v1/validators", "/api/v1/token/info",
          "/api/v1/tx/last?limit=3"):
    print(f"    {p}")
    print(f"      {api(p)[:170]}")
print("\nDONE - live API now reads mainnet")
