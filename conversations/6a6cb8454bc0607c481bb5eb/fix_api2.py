#!/usr/bin/env python3
"""Fix DEX pool token names (byte arrays to strings) and eco metrics"""

filepath = '/opt/verdis-api/verdiscan_api.py'
with open(filepath) as f:
    content = f.read()

fixes = 0

# FIX: DEX pool token names - convert byte arrays to strings
# The RPC returns token_a/token_b as arrays of bytes like [86, 82, 68, 88] for "VRDX"
# Find the line that creates the pair string
old_pair = 'pair = str(p.get("token_a", "A")) + "/" + str(p.get("token_b", "B"))'
new_pair = '''def bytes_to_str(v):
                        if isinstance(v, list):
                            return "".join(chr(b) for b in v if isinstance(b, int) and 0 <= b < 256)
                        return str(v)
                    pair = bytes_to_str(p.get("token_a", "A")) + "/" + bytes_to_str(p.get("token_b", "B"))'''

if old_pair in content:
    content = content.replace(old_pair, new_pair, 1)
    fixes += 1
    print("FIX: DEX pool token names - OK")
else:
    print("FIX: DEX pool token names - PATTERN NOT FOUND")

# FIX: Eco metrics - try alternative patterns
import re

# Find the eco_metrics function and fix the static values
old_eco_patterns = [
    '"co2_offset_tons": 5260,',
    '"co2_offset_tons": (await rpc("eco_getTotalCO2Offset", []) or 0),',  # already fixed?
]

for old in old_eco_patterns:
    if old in content:
        new = '"co2_offset_tons": (await rpc("eco_getTotalCO2Offset", []) or 0),'
        content = content.replace(old, new, 1)
        fixes += 1
        print(f"FIX: eco co2_offset_tons - replaced '{old[:40]}...'")
        break

# Fix trees
old_trees = '"trees_planted": 526_000,'
new_trees = '"trees_planted": (await rpc("eco_getTotalTreesPlanted", []) or 0),'
if old_trees in content:
    content = content.replace(old_trees, new_trees, 1)
    fixes += 1
    print("FIX: eco trees_planted - OK")

# Fix carbon credits
old_credits = '"carbon_credits_minted": len(CARBON_CREDITS),'
new_credits = '"carbon_credits_minted": (await rpc("eco_getCarbonCreditCount", []) or 0),'
if old_credits in content:
    content = content.replace(old_credits, new_credits, 1)
    fixes += 1
    print("FIX: eco carbon_credits_minted - OK")

# Fix reforestation
old_reforest = '"reforestation_logs": 3,'
new_reforest = '"reforestation_logs": (await rpc("eco_getReforestProjectCount", []) or 0),'
if old_reforest in content:
    content = content.replace(old_reforest, new_reforest, 1)
    fixes += 1
    print("FIX: eco reforestation_logs - OK")

# FIX: Validator data - replace static VALIDATORS with live RPC
# Find the validators endpoint
old_validators_endpoint = '''async def validators_list():
    return {
        "success": True,
        "count": len(VALIDATORS),
        "data": VALIDATORS,
    }'''

# Check if it exists
if old_validators_endpoint in content:
    new_validators_endpoint = '''async def validators_list():
    try:
        val_data = await rpc("dpos_allValidators", [])
        active = await rpc("dpos_activeValidators", [])
        if isinstance(val_data, list):
            live_vals = []
            for idx, addr in enumerate(val_data):
                stake = await rpc("dpos_validatorStake", [addr])
                name = await rpc("dpos_validatorName", [addr])
                green = await rpc("eco_getGreenScore", [addr])
                # Convert name from byte array if needed
                if isinstance(name, list):
                    name = "".join(chr(b) for b in name if isinstance(b, int) and 0 <= b < 256)
                is_active = addr in active if isinstance(active, list) else False
                live_vals.append({
                    "address": addr,
                    "name": name or "Validator-" + str(idx),
                    "stake": stake or 0,
                    "green_score": green or 0,
                    "status": "active" if is_active else "inactive",
                })
            return {"success": True, "count": len(live_vals), "data": live_vals}
    except Exception as e:
        pass
    return {
        "success": True,
        "count": len(VALIDATORS),
        "data": VALIDATORS,
    }'''
    content = content.replace(old_validators_endpoint, new_validators_endpoint, 1)
    fixes += 1
    print("FIX: validators live RPC - OK")
else:
    print("FIX: validators - PATTERN NOT FOUND, searching...")
    # Search for the validators endpoint
    import re
    match = re.search(r'async def validators.*?return.*?VALIDATORS.*?\}', content, re.DOTALL)
    if match:
        print("  Found at:", match.group()[:100])

with open(filepath, 'w') as f:
    f.write(content)
print(f"Saved {fixes} fixes")
