#!/usr/bin/env python3
"""Fix tx-relay v3: DEX pools, chain-info, and validators endpoints."""

import re

FILE = '/opt/verdis-chain-rust/tx_relay_v3.py'

with open(FILE, 'r') as f:
    code = f.read()

# 1. Fix get_dex_pools() — getAllPools already returns full pool data, no need for getPool calls
old_dex = '''def get_dex_pools():
    """Get all DEX pools."""
    pools = substrate.rpc_request("amm_dex_getAllPools", [])
    pool_list = []
    for pool_id in pools.get("result", []):
        detail = substrate.rpc_request("amm_dex_getPool", [pool_id])
        if detail and detail.get("result"):
            pool_list.append(detail["result"])
    return pool_list'''

new_dex = '''def get_dex_pools():
    """Get all DEX pools — getAllPools returns full data, no need for getPool calls."""
    pools = substrate.rpc_request("amm_dex_getAllPools", [])
    pool_list = pools.get("result", [])
    # Convert byte arrays to readable token names
    for pool in pool_list:
        if isinstance(pool, dict):
            ta = pool.get("token_a", [])
            tb = pool.get("token_b", [])
            pool["tokenA"] = "".join(chr(b) for b in ta) if isinstance(ta, list) else str(ta)
            pool["tokenB"] = "".join(chr(b) for b in tb) if isinstance(tb, list) else str(tb)
            pool["reserveA"] = pool.get("reserve_a", 0)
            pool["reserveB"] = pool.get("reserve_b", 0)
            pool["totalLP"] = pool.get("total_lp", 0)
            pool["feeNumerator"] = pool.get("fee_numerator", 3)
            pool["feeDenominator"] = pool.get("fee_denominator", 1000)
    return pool_list'''

if old_dex in code:
    code = code.replace(old_dex, new_dex)
    print("[OK] Fixed get_dex_pools() — use getAllPools data directly, add token name decoding")
else:
    print("[WARN] get_dex_pools not found exactly")

# 2. Fix get_chain_info() — format response with readable field names
old_chain = '''def get_chain_info():
    """Get chain health and properties."""
    health = substrate.rpc_request("system_health", [])
    chain = substrate.rpc_request("system_chain", [])
    props = substrate.rpc_request("system_properties", [])
    header = substrate.rpc_request("chain_getHeader", [])
    return {
        "health": health.get("result", {}),
        "chain": chain.get("result", ""),
        "properties": props.get("result", {}),
        "header": header.get("result", {}),
    }'''

new_chain = '''def get_chain_info():
    """Get chain health and properties — formatted for wallet/clients."""
    health = substrate.rpc_request("system_health", [])
    chain = substrate.rpc_request("system_chain", [])
    props = substrate.rpc_request("system_properties", [])
    header = substrate.rpc_request("chain_getHeader", [])
    runtime = substrate.rpc_request("state_getRuntimeVersion", [])

    h = health.get("result", {})
    p = props.get("result", {})
    hdr = header.get("result", {})
    rt = runtime.get("result", {})

    block_num = int(hdr.get("number", "0x0"), 16) if hdr.get("number") else 0

    return {
        "chainName": chain.get("result", "Verdis"),
        "tokenSymbol": p.get("tokenSymbol", "VRDX"),
        "decimals": p.get("tokenDecimals", 9),
        "ss58Format": p.get("ss58Format", 909),
        "blockNumber": block_num,
        "blockHash": hdr.get("hash", ""),
        "peerCount": h.get("peers", 0),
        "isSyncing": h.get("isSyncing", False),
        "specName": rt.get("specName", "verdis-chain"),
        "specVersion": rt.get("specVersion", 0),
        "runtimeVersion": rt.get("transactionVersion", 0),
    }'''

if old_chain in code:
    code = code.replace(old_chain, new_chain)
    print("[OK] Fixed get_chain_info() — formatted response with readable field names")
else:
    print("[WARN] get_chain_info not found exactly")

# 3. Fix get_validators() — ensure it returns a proper list with all validator data
old_val = '''def get_validators():
    """Get all validators with stakes and names."""
    validators = substrate.rpc_request("dpos_allValidators", [])
    v_list = validators.get("result", [])
    result = []
    for v_addr in v_list:
        stake = substrate.rpc_request("dpos_validatorStake", [v_addr])
        name = substrate.rpc_request("dpos_validatorName", [v_addr])'''

# Find the full function and replace it
# Let's find the function boundary by looking at the next def or handler
val_match = re.search(r'def get_validators\(\):.*?(?=\ndef |\n    def |\nclass )', code, re.DOTALL)
if val_match:
    old_val_full = val_match.group(0)
    new_val_full = '''def get_validators():
    """Get all validators with stakes, names, and green scores."""
    validators = substrate.rpc_request("dpos_allValidators", [])
    v_list = validators.get("result", [])
    active_vals = substrate.rpc_request("dpos_activeValidators", [])
    active_set = set(active_vals.get("result", []))
    result = []
    for v_addr in v_list:
        stake = substrate.rpc_request("dpos_validatorStake", [v_addr])
        name = substrate.rpc_request("dpos_validatorName", [v_addr])
        green = substrate.rpc_request("eco_getGreenScore", [v_addr])
        s = stake.get("result", 0)
        n = name.get("result", "")
        g = green.get("result", 0)
        if isinstance(s, dict):
            s = s.get("stake", 0) if "stake" in s else s.get("amount", 0)
        result.append({
            "address": v_addr,
            "stake": s,
            "name": n if n else "Unknown",
            "greenScore": g,
            "isActive": v_addr in active_set,
        })
    return result

'''
    code = code.replace(old_val_full, new_val_full)
    print("[OK] Fixed get_validators() — returns list with address, stake, name, greenScore, isActive")
else:
    print("[WARN] get_validators function not found")

with open(FILE, 'w') as f:
    f.write(code)

print("\n=== TX RELAY FIXES APPLIED ===")
