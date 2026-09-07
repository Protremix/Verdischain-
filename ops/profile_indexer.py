#!/usr/bin/env python3
"""Find what makes the indexer slow before optimising blindly.

0.9 blocks/sec means ~15.5 hours for 50k blocks, which is unacceptable for a
re-indexable pipeline. Rather than guess, time each RPC call the indexer makes per block
and report the breakdown. The prime suspect is get_block_metadata(): fetching and parsing
231 KB of runtime metadata per block would dominate everything else, and metadata only
changes on a runtime upgrade - so it can be cached per spec_version.
"""
import json
import time
import urllib.request

from scalecodec.base import ScaleBytes
from substrateinterface import SubstrateInterface

URL = "http://127.0.0.1:9960"
s = SubstrateInterface(url=URL)


def raw(method, params):
    req = urllib.request.Request(
        URL, data=json.dumps({"jsonrpc": "2.0", "id": 1,
                              "method": method, "params": params}).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read()).get("result")


N = 12
start = 40000
timings = {k: 0.0 for k in
           ("get_block_hash", "chain_getBlock", "get_block_metadata",
            "decode_extrinsics", "get_events", "get_block_header_author")}

for i in range(N):
    bn = start + i
    t = time.time(); bh = s.get_block_hash(bn); timings["get_block_hash"] += time.time() - t
    t = time.time(); blk = raw("chain_getBlock", [bh]); timings["chain_getBlock"] += time.time() - t
    t = time.time(); md = s.get_block_metadata(block_hash=bh); timings["get_block_metadata"] += time.time() - t
    t = time.time()
    for rawex in blk["block"]["extrinsics"]:
        h = "0x" + bytes(rawex).hex() if isinstance(rawex, list) else rawex
        s.create_scale_object("Extrinsic", metadata=md).decode(ScaleBytes(h))
    timings["decode_extrinsics"] += time.time() - t
    t = time.time(); s.get_events(block_hash=bh); timings["get_events"] += time.time() - t
    t = time.time(); s.get_block_header(block_hash=bh, include_author=True); timings["get_block_header_author"] += time.time() - t

total = sum(timings.values())
print(f"=== per-block cost over {N} blocks ===")
for k, v in sorted(timings.items(), key=lambda kv: -kv[1]):
    print(f"  {k:<26} {v/N*1000:8.1f} ms/block   {v/total*100:5.1f}%")
print(f"  {'TOTAL':<26} {total/N*1000:8.1f} ms/block  -> {N/total:.2f} blk/s")

# Does metadata actually change across the chain? If spec_version is constant, one
# metadata fetch serves every block.
print("\n=== is per-block metadata necessary? ===")
specs = {}
for bn in (1, 10000, 25000, 40000, 50000):
    bh = s.get_block_hash(bn)
    rt = raw("state_getRuntimeVersion", [bh])
    specs[bn] = rt.get("specVersion") if rt else None
print(f"  specVersion by block: {specs}")
if len(set(specs.values())) == 1:
    print("  -> constant across the chain: metadata can be cached once per spec_version")

# How much does caching metadata save?
print("\n=== with metadata cached ===")
md_cached = s.get_block_metadata(block_hash=s.get_block_hash(start))
t0 = time.time()
for i in range(N):
    bn = start + 100 + i
    bh = s.get_block_hash(bn)
    blk = raw("chain_getBlock", [bh])
    for rawex in blk["block"]["extrinsics"]:
        h = "0x" + bytes(rawex).hex() if isinstance(rawex, list) else rawex
        s.create_scale_object("Extrinsic", metadata=md_cached).decode(ScaleBytes(h))
    s.get_events(block_hash=bh)
    s.get_block_header(block_hash=bh, include_author=True)
el = time.time() - t0
print(f"  {el/N*1000:.1f} ms/block -> {N/el:.2f} blk/s")
print(f"  50k blocks would take {50000/(N/el)/60:.0f} min")
