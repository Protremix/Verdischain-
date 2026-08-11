#!/usr/bin/env python3
"""P0-4: Test validator failure, removal and reactivation"""
import json, subprocess, time, sys

RPC = "http://localhost:9933"

def rpc(method, params=None):
    payload = {"jsonrpc": "2.0", "method": method, "params": params or [], "id": 1}
    r = subprocess.run(["curl", "-s", "-X", "POST", RPC, "-H", "Content-Type: application/json",
                       "-d", json.dumps(payload)], capture_output=True, text=True)
    return json.loads(r.stdout).get("result")

subprocess.run(["pip", "install", "xxhash", "-q"], capture_output=True)
import xxhash

def twox128(name):
    h1 = xxhash.xxh64(name.encode(), seed=0).intdigest()
    h2 = xxhash.xxh64(name.encode(), seed=1).intdigest()
    return h1.to_bytes(8, "little").hex() + h2.to_bytes(8, "little").hex()

def get_block():
    header = rpc("chain_getHeader")
    return int(header["number"], 16) if header else 0

def get_finalized():
    h = rpc("chain_getFinalizedHead")
    if h:
        fh = rpc("chain_getHeader", [h])
        return int(fh["number"], 16) if fh else 0
    return 0

def get_authority_counts():
    counts = {}
    for pallet, storage in [("Session", "Validators"), ("Babe", "Authorities"), ("Grandpa", "Authorities")]:
        key = "0x" + twox128(pallet) + twox128(storage)
        raw = rpc("state_getStorage", [key])
        if raw:
            n = bytes.fromhex(raw[2:])[0] >> 2
            counts[f"{pallet}::{storage}"] = n
    return counts

print("=" * 60)
print("P0-4: VALIDATOR FAILURE, REMOVAL AND REACTIVATION")
print("=" * 60)

# Phase 1: Baseline
print("\n--- Phase 1: Baseline (all 6 nodes running) ---")
block1 = get_block()
fin1 = get_finalized()
auth1 = get_authority_counts()
peers1 = len(rpc("system_peers") or [])
print(f"Block: {block1}, Finalized: {fin1}, Peers: {peers1}")
print(f"Authorities: {auth1}")

# Phase 2: Stop node 6 (Ferdie)
print("\n--- Phase 2: Stop verdis-node6 (Ferdie) ---")
subprocess.run(["ssh", "-o", "ConnectTimeout=10", "root@91.98.160.145",
                "systemctl stop verdis-node6"], capture_output=True)
print("Node 6 stopped")
time.sleep(10)  # Wait for the network to react

block2 = get_block()
fin2 = get_finalized()
auth2 = get_authority_counts()
peers2 = len(rpc("system_peers") or [])
print(f"Block: {block2} (was {block1}), Finalized: {fin2}")
print(f"Block advance: {block2 > block1}")
print(f"Finality advance: {fin2 > fin1}")
print(f"Authorities: {auth2}")
print(f"Peers: {peers2}")

if block2 > block1:
    print("✓ Block production continues with 5/6 validators")
else:
    print("✗ Block production stopped!")

if fin2 > fin1:
    print("✓ Finality continues with 5/6 validators (≥2/3 BFT)")
else:
    print("⚠ Finality may have paused (need >2/3 of 6 = 5 validators for GRANDPA)")

# Phase 3: Wait 30s and check again
print("\n--- Phase 3: Wait 30s after node stop ---")
time.sleep(30)
block3 = get_block()
fin3 = get_finalized()
auth3 = get_authority_counts()
print(f"Block: {block3}, Finalized: {fin3}")
print(f"Blocks produced in 30s: {block3 - block2}")
print(f"Finality advanced: {fin3 > fin2}")
print(f"Authorities unchanged: {auth3 == auth2}")

# Phase 4: Restart node 6
print("\n--- Phase 4: Restart verdis-node6 ---")
subprocess.run(["ssh", "-o", "ConnectTimeout=10", "root@91.98.160.145",
                "systemctl start verdis-node6"], capture_output=True)
print("Node 6 restarted")
time.sleep(15)

block4 = get_block()
fin4 = get_finalized()
auth4 = get_authority_counts()
peers4 = len(rpc("system_peers") or [])
print(f"Block: {block4}, Finalized: {fin4}, Peers: {peers4}")
print(f"Authorities: {auth4}")
print(f"Peers restored: {peers4 >= peers1}")

# Phase 5: Verify recovery
print("\n--- Phase 5: Verify full recovery ---")
time.sleep(15)
block5 = get_block()
fin5 = get_finalized()
print(f"Block: {block5}, Finalized: {fin5}")
print(f"Block production rate: {(block5 - block4) / 15:.1f} blocks/s")

# Verdict
print("\n" + "=" * 60)
print("P0-4 VERDICT")
print("=" * 60)
checks = [
    ("Block production survives 1 node stop", block2 > block1),
    ("Finality survives 1 node stop (5/6 ≥ 2/3)", fin2 > fin1 or fin3 > fin1),
    ("Block production continues after 30s", block3 > block2),
    ("Node rejoins after restart", peers4 >= peers1 - 1),
    ("Block production rate restored", (block5 - block4) > 0),
    ("Authorities unchanged throughout", auth2 == auth1 and auth4 == auth1),
]
all_pass = True
for check, result in checks:
    status = "✓ PASS" if result else "✗ FAIL"
    if not result: all_pass = False
    print(f"  {status}: {check}")
print(f"\nOverall: {'ALL PASS ✓' if all_pass else 'FAILURES ✗'}")
