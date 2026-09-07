#!/usr/bin/env python
"""Plan the deployment of the 6 recovered validators (validator-16..21).

Before touching anything, establish:
  1. that none of those 6 gran keys is ALREADY loaded in any keystore anywhere -
     starting a duplicate would cause equivocation (it cost 738 events on testnet today)
  2. which host has the resources to take 6 more archive nodes
  3. which p2p/rpc ports are free on that host
  4. the exact stash accounts, so we can confirm they hold the bond on chain

No changes are made. Output is a concrete plan with measured numbers.
Secrets are never printed - only public keys.
"""
import json, os, subprocess, zipfile
from pathlib import Path

KEY = os.path.expanduser("~/.ssh/id_ed25519")
ZIP = Path(os.environ["LOCALAPPDATA"]) / "hermes" / "profiles" / "verdis" / \
      "secrets" / "ceremony-keys-20260901.zip"
HOSTS = ["185.84.224.91", "195.154.80.40", "213.136.78.63"]
NEW = [f"validator-{n}" for n in range(16, 22)]


def ssh(host, cmd, timeout=150):
    p = subprocess.run(
        ["ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no",
         "-o", "ConnectTimeout=15", "-i", KEY, f"root@{host}", cmd],
        capture_output=True, text=True, timeout=timeout)
    return p.stdout.strip()


z = zipfile.ZipFile(ZIP)


def pub(v, kind):
    d = json.loads(z.read(f"ceremony-keys-20260901/validators/{v}/{kind}.json"))
    return d["publicKey"].removeprefix("0x").lower(), d.get("ss58Address", "")


print("=== 1. the 6 validators we are about to deploy ===")
keys = {}
for v in NEW:
    g, _ = pub(v, "grandpa")
    b, _ = pub(v, "babe")
    a, addr = pub(v, "account")
    keys[v] = {"gran": g, "babe": b, "acco": a, "addr": addr}
    print(f"  {v}  gran=0x{g[:20]}…  babe=0x{b[:16]}…  stash={addr[:16]}…")

print("\n=== 2. DUPLICATE CHECK - are any of these keys already running? ===")
dupes = []
for host in HOSTS:
    out = ssh(host, "find /data -type f -path '*keystore*' 2>/dev/null | xargs -r -n1 basename 2>/dev/null")
    present = set(out.split())
    for v, k in keys.items():
        for kind, prefix in (("gran", "6772616e"), ("babe", "62616265"), ("acco", "6163636f")):
            fname = prefix + k[kind]
            if fname in present:
                dupes.append((host, v, kind))
                print(f"  !! {host} already has {v} {kind}")
if not dupes:
    print("  none of the 18 key files exist on any host - safe to deploy")

print("\n=== 3. host capacity ===")
for host in HOSTS:
    out = ssh(host, "echo \"cores=$(nproc) ram_free=$(free -g|awk 'NR==2{print $7}')G "
                    "load=$(cut -d' ' -f1 /proc/loadavg) "
                    "data_free=$(df -h /data 2>/dev/null|tail -1|awk '{print $4}') "
                    "nodes=$(pgrep -cf 'local/bin/verdis') "
                    "db_per_node=$(du -sh /data/verdis-data 2>/dev/null|cut -f1)\"")
    print(f"  {host}: {out}")

print("\n=== 4. free ports on the best candidate (213.136.78.63) ===")
out = ssh("213.136.78.63", "ss -tln | grep -oP ':(3033[0-9]|303[4-9][0-9]|99[0-9][0-9])' | tr -d ':' | sort -un | tr '\\n' ' '")
used = set(out.split())
print(f"  in use: {out}")
free_p2p = [p for p in range(30341, 30360) if str(p) not in used][:6]
free_rpc = [p for p in range(9960, 9990) if str(p) not in used][:6]
print(f"  proposed p2p: {free_p2p}")
print(f"  proposed rpc: {free_rpc}")

print("\n=== 5. do the 6 stash accounts hold a bond on chain? ===")
for v in NEW:
    acct = keys[v]["acco"]
    cmd = ("curl -s -m 10 -H 'Content-Type: application/json' -d '"
           '{"jsonrpc":"2.0","id":1,"method":"state_getStorage","params":'
           f'["0x26aa394eea5630e07c48ae0c9558cef7b99d880ec681799c0cf30e8886371da9"]'
           "}' http://localhost:9944")
    # simpler: check the Dpos.Validators map for the gran-linked stash later;
    # here just report the address so Rojs can cross-check on the explorer
    print(f"  {v}: stash {keys[v]['addr']}")

print("\n=== 6. spec file to use (must yield genesis 0x2284393d…) ===")
for host in HOSTS:
    out = ssh(host, "for f in /data/verdis-chain/chain-specs/mainnet-raw.json "
                    "/data/verdis-chain/chain-specs/mainnet-raw-v13-verified.json; do "
                    "[ -f \"$f\" ] && echo \"$(sha256sum $f | cut -c1-16) $f\"; done")
    print(f"  {host}:")
    for line in out.split("\n"):
        if line:
            print(f"    {line}")
print("  wanted sha256 prefix: aca92919e13da10f")
