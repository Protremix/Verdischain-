#!/usr/bin/env python3
"""Fix the Verdiscan API: block hash, DEX pools, eco metrics - all to live RPC"""
import sys

filepath = '/opt/verdis-api/verdiscan_api.py'
with open(filepath) as f:
    content = f.read()

fixes_applied = 0

# FIX 1: block_last - use chain_getBlockHash
old_block_last = '''    blocks = []
    for i in range(latest, max(latest - limit, -1), -1):
        header = await get_block_header(i)
        if header:
            blocks.append({
                "block": i,
                "hash": header.get("hash", ""),
                "parent_hash": header.get("parentHash", ""),
                "state_root": header.get("stateRoot", ""),
                "extrinsics_root": header.get("extrinsicsRoot", ""),
                "extrinsics_count": 0,
                "timestamp": None,
            })
    return {"success": True, "count": len(blocks), "data": blocks}'''

new_block_last = '''    blocks = []
    for i in range(latest, max(latest - limit, -1), -1):
        header = await get_block_header(i)
        if header:
            block_hash = await rpc("chain_getBlockHash", [i])
            block_data = await get_block_by_number(i)
            ext_count = 0
            if block_data and "block" in block_data:
                ext_count = len(block_data.get("block", {}).get("extrinsics", []))
            blocks.append({
                "block": i,
                "hash": block_hash or "",
                "parent_hash": header.get("parentHash", ""),
                "state_root": header.get("stateRoot", ""),
                "extrinsics_root": header.get("extrinsicsRoot", ""),
                "extrinsics_count": ext_count,
                "timestamp": None,
            })
    return {"success": True, "count": len(blocks), "data": blocks}'''

if old_block_last in content:
    content = content.replace(old_block_last, new_block_last, 1)
    fixes_applied += 1
    print("FIX 1: block_last hash - OK")
else:
    print("FIX 1: block_last hash - PATTERN NOT FOUND")

# FIX 2: block_detail - use chain_getBlockHash
old_detail = '"hash": block_data.get("blockHash", header.get("hash", "")),'
new_detail = '"hash": await rpc("chain_getBlockHash", [block_number]),'
if old_detail in content:
    content = content.replace(old_detail, new_detail, 1)
    fixes_applied += 1
    print("FIX 2: block_detail hash - OK")
else:
    print("FIX 2: block_detail hash - PATTERN NOT FOUND")

# FIX 3: Replace static DEX_POOLS with live RPC
old_dex = '''async def dex_pools():
    return {
        "success": True,
        "count": len(DEX_POOLS),
        "data": DEX_POOLS,
    }'''

new_dex = '''async def dex_pools():
    try:
        pools_data = await rpc("amm_dex_getAllPools", [])
        if isinstance(pools_data, list):
            live_pools = []
            for idx, p in enumerate(pools_data):
                if isinstance(p, dict):
                    pair = str(p.get("token_a", "A")) + "/" + str(p.get("token_b", "B"))
                    live_pools.append({
                        "id": idx,
                        "pair": pair,
                        "reserve_a": p.get("reserve_a", 0),
                        "reserve_b": p.get("reserve_b", 0),
                        "fee": "0.3%",
                        "tvl": (p.get("reserve_a", 0) + p.get("reserve_b", 0)),
                        "volume_24h": 0,
                    })
                else:
                    live_pools.append({"id": idx, "pair": str(p), "reserve_a": 0, "reserve_b": 0, "fee": "0.3%", "tvl": 0, "volume_24h": 0})
            return {"success": True, "count": len(live_pools), "data": live_pools}
    except Exception:
        pass
    return {
        "success": True,
        "count": len(DEX_POOLS),
        "data": DEX_POOLS,
    }'''

if old_dex in content:
    content = content.replace(old_dex, new_dex, 1)
    fixes_applied += 1
    print("FIX 3: DEX pools live RPC - OK")
else:
    print("FIX 3: DEX pools live RPC - PATTERN NOT FOUND")

# FIX 4: Eco metrics - use live RPC
old_eco = '''            "co2_offset_tons": 5260,
            "trees_planted": 526_000,
            "carbon_credits_minted": len(CARBON_CREDITS),
            "total_credit_tons": total_credits,
            "avg_green_score": round(sum(v["green_score"] for v in VALIDATORS) / len(VALIDATORS), 1) if VALIDATORS else 0,
            "reforestation_logs": 3,'''

new_eco = '''            "co2_offset_tons": (await rpc("eco_getTotalCO2Offset", []) or 0),
            "trees_planted": (await rpc("eco_getTotalTreesPlanted", []) or 0),
            "carbon_credits_minted": (await rpc("eco_getCarbonCreditCount", []) or 0),
            "total_credit_tons": total_credits,
            "avg_green_score": round(sum(v["green_score"] for v in VALIDATORS) / len(VALIDATORS), 1) if VALIDATORS else 0,
            "reforestation_logs": (await rpc("eco_getReforestProjectCount", []) or 0),'''

if old_eco in content:
    content = content.replace(old_eco, new_eco, 1)
    fixes_applied += 1
    print("FIX 4: Eco metrics live RPC - OK")
else:
    print("FIX 4: Eco metrics live RPC - PATTERN NOT FOUND")

with open(filepath, 'w') as f:
    f.write(content)
print(f"Saved {fixes_applied} fixes")
