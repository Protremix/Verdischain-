#!/usr/bin/env python3
"""Query Session/BABE/GRANDPA authorities via runtime APIs and storage"""
import json, subprocess

RPC = "http://localhost:9933"

def rpc(method, params=None):
    payload = {"jsonrpc": "2.0", "method": method, "params": params or [], "id": 1}
    r = subprocess.run(["curl", "-s", "-X", "POST", RPC, "-H", "Content-Type: application/json",
                       "-d", json.dumps(payload)], capture_output=True, text=True)
    return json.loads(r.stdout).get("result")

def rpc_storage(pallet, storage_key):
    """Query storage via state_getStorage with twox128 keys"""
    # We need to compute twox128 manually
    # Use Python's xxhash or compute via the node
    pass

# Try runtime API methods
print("=== RUNTIME API QUERIES ===")

# Method 1: Try Core_version
try:
    version = rpc("state_call", ["Core_version", "0x"])
    print(f"Core_version: {version}")
except Exception as e:
    print(f"Core_version error: {e}")

# Method 2: Try state_getStorage for Session::Validators
# Session storage prefix = twox128("Session") + twox128("Validators")
# We need XXH128. Let's try querying known storage keys.

# Actually, let's use the node's RPC to query storage keys
# First, let's try to get the storage key for Session::Validators
# by using state_getStorageHash

# Alternative: use state_getKeys with prefix
# Session prefix = twox128("Session")
import struct

def xxh64(data, seed=0):
    """XXH64 implementation"""
    # Use a simple approach - the server has python3 with hashlib
    # Actually, XXH64 is not in hashlib. Let's try a different approach.
    # We can use the substrate API to query storage.
    pass

# Let's try the substrate-style state_call with proper API names
# Session API: "SessionApiValidators" or "SessionValidators"
# BABE API: "BabeApiAuthorities" or "BabeAuthorities"  
# GRANDPA API: "GrandpaApiAuthorities" or "GrandpaAuthorities"

# Try different API name patterns
api_names = {
    "Session": ["SessionValidators", "SessionApiValidators", "Session_authorities"],
    "BABE": ["BabeApiAuthorities", "BabeAuthorities", "Babe_authorities"],
    "GRANDPA": ["GrandpaApiAuthorities", "GrandpaAuthorities", "Grandpa_authorities", "GrandpaApiCurrentSetId"],
}

for pallet, names in api_names.items():
    for name in names:
        try:
            result = rpc("state_call", [name, "0x"])
            if result and result != "0x" and len(result) > 4:
                raw = bytes.fromhex(result[2:])
                n = raw[0] >> 2
                offset = 1
                accounts = []
                for i in range(n):
                    acct = raw[offset:offset+32]
                    accounts.append("0x" + acct.hex())
                    offset += 32
                print(f"\n{name}: {len(accounts)} authorities")
                for i, a in enumerate(accounts):
                    print(f"  {i+1}. {a}")
                break
            elif result:
                print(f"{name}: {result[:40]}... (non-empty, trying to decode)")
        except Exception as e:
            pass

# Try state_getKeys to find session/babe/grandpa storage
print("\n=== STORAGE KEY SCAN ===")
for pallet in ["Session", "Babe", "Grandpa", "Dpos"]:
    # Get all keys with this pallet prefix
    # We'll try prefix queries
    try:
        # state_getKeys requires a hex-encoded prefix
        # We can try with empty prefix to get all keys
        keys = rpc("state_getKeys", ["0x"])
        if keys:
            pallet_keys = [k for k in keys if pallet.lower() in k.lower()]
            if pallet_keys:
                print(f"\n{pallet} storage keys found: {len(pallet_keys)}")
                for k in pallet_keys[:5]:
                    val = rpc("state_getStorage", [k])
                    print(f"  {k[:40]}... = {val[:60] if val else 'None'}...")
    except Exception as e:
        print(f"{pallet} keys: {e}")

# Try alternative: use system_properties and chain metadata
print("\n=== CHAIN METADATA ===")
try:
    meta = rpc("state_getMetadata")
    if meta:
        print(f"Metadata length: {len(meta)} chars")
    else:
        print("Metadata: None")
except Exception as e:
    print(f"Metadata error: {e}")

# Get runtime version
print("\n=== RUNTIME VERSION ===")
try:
    version = rpc("state_getRuntimeVersion")
    if version:
        print(f"SpecName: {version.get('specName')}")
        print(f"SpecVersion: {version.get('specVersion')}")
        print(f"TransactionVersion: {version.get('transactionVersion')}")
        apis = version.get('apis', [])
        print(f"APIs ({len(apis)}):")
        for api_id, api_ver in apis:
            print(f"  {api_id}: {api_ver}")
except Exception as e:
    print(f"Runtime version error: {e}")

# Query TotalIssuance via different methods
print("\n=== TOTAL ISSUANCE ===")
try:
    # Method 1: balances_totalIssuance (custom RPC)
    ti = rpc("balances_totalIssuance")
    if ti:
        val = int(ti, 16) if isinstance(ti, str) else int(ti)
        print(f"balances_totalIssuance: {val} ({val/1e9:.0f} VRDX)")
except:
    pass

# Try state_call for Balances::TotalIssuance
try:
    ti = rpc("state_call", ["BalancesTotalIssuance", "0x"])
    if ti:
        val = int.from_bytes(bytes.fromhex(ti[2:])[:16], "little")
        print(f"BalancesTotalIssuance: {val} ({val/1e9:.0f} VRDX)")
except Exception as e:
    print(f"BalancesTotalIssuance: {e}")

# Query via substrate API
try:
    # AccountBalanceApi
    alice = "0xd43593c715fdd31c61141abd04a99fd6822c8558854ccde39a5684e7a56da27d"
    bal = rpc("state_call", ["AccountBalanceApiBalance", "0x" + alice])
    if bal:
        val = int.from_bytes(bytes.fromhex(bal[2:])[:16], "little")
        print(f"Alice balance: {val} ({val/1e9:.0f} VRDX)")
except Exception as e:
    print(f"AccountBalanceApi: {e}")

# Check finalized blocks
print("\n=== FINALITY ===")
finalized = rpc("chain_getFinalizedHead")
print(f"Finalized head: {finalized}")

# Check block production
header = rpc("chain_getHeader")
print(f"Current block: {int(header['number'], 16)}")
