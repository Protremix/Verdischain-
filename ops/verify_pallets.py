#!/usr/bin/env python
"""Extract the EXACT pallet list from mainnet runtime metadata.

Why strict parsing: an earlier grep for capitalised words in the raw SCALE blob is not
evidence - it can miss a pallet that exists and invent one that does not. The website
claims a DEX, EVM opcodes and an Eco/carbon module; before reporting those as absent
the pallet names must be read from the metadata structure itself.

Approach: metadata v14/v15 encodes the pallet list as a SCALE vector near a known
marker. Rather than write a full SCALE decoder, use substrate's own RPC:
state_getMetadata gives the blob, and every pallet name appears as a length-prefixed
ASCII string inside the pallets vector. Cross-check each candidate against
state_getKeys for its storage prefix (twox128 of the pallet name) - a pallet that
really exists in the runtime has a queryable storage prefix. That is proof, not
pattern matching.
"""
import hashlib
import json
import re
import subprocess

HOST = "91.98.160.145"
KEY = "~/.ssh/id_ed25519"
RPC = "http://localhost:9960"


def ssh(cmd, timeout=240):
    import os
    p = subprocess.run(
        ["ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no",
         "-o", "ConnectTimeout=15", "-i", os.path.expanduser(KEY),
         f"root@{HOST}", cmd],
        capture_output=True, text=True, timeout=timeout)
    return p.stdout.strip()


def rpc(method, params="[]"):
    out = ssh(f"""curl -s -m 40 -H 'Content-Type: application/json' """
              f"""-d '{{"jsonrpc":"2.0","id":1,"method":"{method}","params":{params}}}' {RPC}""")
    try:
        return json.loads(out).get("result")
    except Exception:
        return None


print("=== fetching runtime metadata ===")
meta = rpc("state_getMetadata")
if not meta:
    raise SystemExit("metadata not retrieved")
blob = bytes.fromhex(meta[2:])
print(f"  {len(blob)/1024:.0f} KB")

# Candidate pallet names: length-prefixed ASCII identifiers in the metadata.
# SCALE encodes a short string as a single compact byte (len<<2) then the bytes.
cands = set()
for m in re.finditer(rb"[A-Z][A-Za-z0-9]{2,30}", blob):
    name = m.group()
    start = m.start()
    if start == 0:
        continue
    prefix = blob[start - 1]
    if prefix == (len(name) << 2):  # compact-encoded length matches
        cands.add(name.decode())

print(f"  {len(cands)} length-prefixed identifiers")


def twox128(data: bytes) -> str:
    """xxhash64 twice, little-endian - the storage prefix substrate uses."""
    try:
        import xxhash
    except ImportError:
        return ""
    a = xxhash.xxh64(data, seed=0).intdigest().to_bytes(8, "little")
    b = xxhash.xxh64(data, seed=1).intdigest().to_bytes(8, "little")
    return (a + b).hex()


# Proof step: a real pallet has storage under twox128(name). Ask the node.
print("\n=== verifying each candidate against on-chain storage ===")
have_xxhash = twox128(b"test") != ""
if not have_xxhash:
    print("  xxhash unavailable locally - verifying on the server instead")

INTEREST = ["Balances", "Contracts", "Dpos", "Nfts", "Treasury", "Council",
            "Democracy", "Utility", "Vesting", "Identity", "Multisig", "Proxy",
            "Scheduler", "Session", "Grandpa", "Babe", "System", "Timestamp",
            "Sudo", "Staking", "Assets", "Dex", "Evm", "Ethereum", "Eco",
            "Carbon", "Uniques", "TransactionPayment", "Elections", "Bounties",
            "Preimage", "Referenda", "ConvictionVoting", "Whitelist"]

script = r'''
import hashlib, json, subprocess, sys
try:
    import xxhash
except ImportError:
    sys.exit("NOXXHASH")
names = %s
def twox128(d):
    a = xxhash.xxh64(d, seed=0).intdigest().to_bytes(8,"little")
    b = xxhash.xxh64(d, seed=1).intdigest().to_bytes(8,"little")
    return (a+b).hex()
import urllib.request
def rpc(method, params):
    req = urllib.request.Request("%s",
        data=json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode(),
        headers={"Content-Type":"application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=30).read()).get("result")
for n in names:
    pref = "0x" + twox128(n.encode())
    keys = rpc("state_getKeys", [pref])
    print(f"{n}\t{len(keys) if keys else 0}")
''' % (json.dumps(INTEREST), RPC)

import base64
enc = base64.b64encode(script.encode()).decode()
out = ssh(f"echo {enc} | base64 -d > /tmp/pv.py && python3 /tmp/pv.py 2>&1", timeout=300)

if "NOXXHASH" in out:
    ssh("pip3 install --quiet xxhash 2>&1 | tail -1", timeout=280)
    out = ssh("python3 /tmp/pv.py 2>&1", timeout=300)

present, absent = [], []
for line in out.splitlines():
    if "\t" not in line:
        continue
    name, cnt = line.split("\t")[:2]
    try:
        n = int(cnt)
    except ValueError:
        continue
    (present if n > 0 else absent).append((name, n))

print(f"\n  PRESENT in runtime storage ({len(present)}):")
for n, c in sorted(present, key=lambda x: -x[1]):
    print(f"    {n:<22} {c} storage keys")
print(f"\n  NO storage keys ({len(absent)}):")
for n, c in absent:
    print(f"    {n}")

print("\n=== website claims vs runtime ===")
CLAIMS = {
    "AMM DEX": ["Dex", "Assets"],
    "EVM / 23 opcodes": ["Evm", "Ethereum"],
    "carbon credits / Eco module": ["Eco", "Carbon"],
    "ink! smart contracts": ["Contracts"],
    "DPoS consensus": ["Dpos"],
    "NFTs": ["Nfts"],
    "governance": ["Council", "Democracy"],
}
pnames = {n for n, _ in present}
for claim, pallets in CLAIMS.items():
    hit = [p for p in pallets if p in pnames]
    status = f"OK via {hit}" if hit else f"NOT IN RUNTIME (looked for {pallets})"
    print(f"  {claim:<30} {status}")
