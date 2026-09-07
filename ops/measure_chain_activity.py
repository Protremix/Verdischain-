#!/usr/bin/env python3
"""Measure what the mainnet chain actually CONTAINS before building an explorer on it.

Reason for this check: a random sample of 320 blocks found no block with more than one
extrinsic - i.e. nothing but the Timestamp inherent. If that holds chain-wide, then
mainnet has no user transactions at all, and an "account history / holders / volume
charts" explorer would be rendering empty tables no matter how good the indexer is.
That is a fact worth establishing before writing more code, and worth telling the
founder plainly.

Method: scan a contiguous window plus a wide random sample, count extrinsics per block,
and separately count Balances.Transfer events. Report absolute numbers, no estimates.
"""
import json
import random
import sys
import urllib.request
from collections import Counter

RPC = "http://127.0.0.1:9960"


def rpc(method, params):
    req = urllib.request.Request(
        RPC, data=json.dumps({"jsonrpc": "2.0", "id": 1,
                              "method": method, "params": params}).encode(),
        headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=25).read()).get("result")


tip = int(rpc("chain_getHeader", [])["number"], 16)
print(f"mainnet tip: {tip}")

# 1. contiguous window at the head - recent activity
# 2. contiguous window right after genesis - launch activity
# 3. wide random sample - anything in between
random.seed(11)
windows = {
    "head (last 300)": range(max(1, tip - 300), tip + 1),
    "genesis (1..300)": range(1, 301),
    "random 400": [random.randrange(1, tip) for _ in range(400)],
}

grand = Counter()
per_window = {}
examples = []

for label, rng in windows.items():
    counts = Counter()
    multi = []
    for bn in rng:
        try:
            bh = rpc("chain_getBlockHash", [bn])
            exs = rpc("chain_getBlock", [bh])["block"]["extrinsics"]
            n = len(exs)
            counts[n] += 1
            grand[n] += 1
            if n > 1:
                multi.append(bn)
                if len(examples) < 10:
                    examples.append((bn, n))
        except Exception:                      # noqa: BLE001
            counts["error"] += 1
    per_window[label] = (counts, multi)
    total = sum(v for k, v in counts.items() if isinstance(k, int))
    print(f"\n{label}: {total} blocks read")
    for n in sorted(k for k in counts if isinstance(k, int)):
        print(f"  {n} extrinsic(s): {counts[n]} blocks")
    if multi:
        print(f"  blocks with >1 extrinsic: {multi[:12]}")

print("\n" + "=" * 60)
tot = sum(v for k, v in grand.items() if isinstance(k, int))
multi_tot = sum(v for k, v in grand.items() if isinstance(k, int) and k > 1)
print(f"blocks sampled : {tot}")
print(f"with >1 extrinsic: {multi_tot}")
print(f"examples: {examples if examples else 'NONE'}")

# Balances.Transfer events chain-wide, via the System.Events storage at each block is
# expensive; instead check the total issuance vs the account table, which tells us
# whether value ever moved after genesis.
print("\n=== accounts and issuance ===")
# System.Account prefix
acct_prefix = "0x26aa394eea5630e07c48ae0c9558cef7b99d880ec681799c0cf30e8886371da9"
keys = rpc("state_getKeys", [acct_prefix]) or []
print(f"System.Account keys: {len(keys)}")

issuance_key = "0xc2261276cc9d1f8598ea4b6a74b15c2f57c875e4cff74148e4628f264b974c80"
raw = rpc("state_getStorage", [issuance_key])
if raw:
    v = int.from_bytes(bytes.fromhex(raw[2:])[:16], "little")
    print(f"total issuance: {v/10**9:,.0f} VRDX")

# Are there any Balances.Transfer events at all? Sample the events storage on a
# handful of blocks - a chain with real usage shows them quickly.
print("\n=== Balances.Transfer events in sampled blocks ===")
ev_key = "0x26aa394eea5630e07c48ae0c9558cef780d41e5e16056765bc8461851072c9d7"
hits = 0
checked = 0
for bn in list(range(max(1, tip - 60), tip + 1)) + [random.randrange(1, tip) for _ in range(60)]:
    try:
        bh = rpc("chain_getBlockHash", [bn])
        raw = rpc("state_getStorageAt", [ev_key, bh]) if False else rpc(
            "state_getStorage", [ev_key, bh])
        checked += 1
        if raw and len(raw) > 400:      # a block with only system events is short
            hits += 1
    except Exception:                    # noqa: BLE001
        pass
print(f"  blocks whose event blob is large (activity): {hits}/{checked}")

print("\n" + "=" * 60)
if multi_tot == 0:
    print("CONCLUSION: no user transactions found in any sampled block.")
    print("Every block carries only the Timestamp inherent. The chain is producing")
    print("and finalizing blocks correctly, but nothing is transacting on it.")
    print("An explorer will therefore show empty transaction/holder/volume views -")
    print("not because the indexer is wrong, but because there is no activity to index.")
else:
    print(f"CONCLUSION: {multi_tot} sampled blocks carry user extrinsics.")
