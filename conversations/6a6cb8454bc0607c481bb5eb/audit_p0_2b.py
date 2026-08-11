#!/usr/bin/env python3
"""Query Session/BABE/GRANDPA via proper state_call method names"""
import json, subprocess

RPC = "http://localhost:9933"

def rpc(method, params=None):
    payload = {"jsonrpc": "2.0", "method": method, "params": params or [], "id": 1}
    r = subprocess.run(["curl", "-s", "-X", "POST", RPC, "-H", "Content-Type: application/json",
                       "-d", json.dumps(payload)], capture_output=True, text=True)
    resp = json.loads(r.stdout)
    return resp.get("result"), resp.get("error")

def decode_account_vec(hex_str):
    """Decode SCALE Vec<AccountId32>"""
    if not hex_str or hex_str == "0x":
        return []
    raw = bytes.fromhex(hex_str[2:] if hex_str.startswith("0x") else hex_str)
    if len(raw) < 1:
        return []
    n = raw[0] >> 2
    offset = 1
    accounts = []
    for i in range(n):
        if offset + 32 > len(raw):
            break
        acct = "0x" + raw[offset:offset+32].hex()
        accounts.append(acct)
        offset += 32
    return accounts

def decode_grandpa_authorities(hex_str):
    """Decode Vec<(GrandpaId, u64)> — AuthorityId is 32 bytes, weight is 8 bytes (u64)"""
    if not hex_str or hex_str == "0x":
        return []
    raw = bytes.fromhex(hex_str[2:] if hex_str.startswith("0x") else hex_str)
    if len(raw) < 1:
        return []
    n = raw[0] >> 2
    offset = 1
    authorities = []
    for i in range(n):
        if offset + 40 > len(raw):
            break
        acct = "0x" + raw[offset:offset+32].hex()
        weight = int.from_bytes(raw[offset+32:offset+40], "little")
        authorities.append((acct, weight))
        offset += 40
    return authorities

print("=" * 60)
print("P0-2: DPoS → Session → BABE → GRANDPA CONSISTENCY")
print("=" * 60)

# Try various state_call method name formats
methods_to_try = [
    ("Session", ["Session_validators", "SessionApi_validators", "SessionValidators"]),
    ("BABE", ["BabeApi_authorities", "Babe_authorities", "BabeApiAuthorities"]),
    ("GRANDPA", ["GrandpaApi_authorities", "Grandpa_authorities", "GrandpaApiAuthorities"]),
    ("GrandpaApi_grandpa_authorities", ["GrandpaApi_grandpa_authorities"]),
]

for label, methods in methods_to_try:
    for method in methods:
        result, error = rpc("state_call", [method, "0x"])
        if result and result != "0x" and len(result) > 4:
            if "Grandpa" in label or "GRANDPA" in label:
                authorities = decode_grandpa_authorities(result)
                if authorities:
                    print(f"\n{label} ({method}): {len(authorities)} authorities")
                    for i, (a, w) in enumerate(authorities):
                        print(f"  {i+1}. {a} (weight={w})")
                    break
            else:
                accounts = decode_account_vec(result)
                if accounts:
                    print(f"\n{label} ({method}): {len(accounts)} authorities")
                    for i, a in enumerate(accounts):
                        print(f"  {i+1}. {a}")
                    break
        if error:
            pass  # silently skip

# Also try querying via storage keys using twox128
# We need XXH128. Let's install/use xxhash
print("\n=== STORAGE-BASED QUERIES ===")

# Install xxhash if needed
subprocess.run(["pip", "install", "xxhash", "-q"], capture_output=True)
import xxhash

def twox128(name):
    """Compute twox128 hash of a string"""
    h1 = xxhash.xxh64(name.encode(), seed=0).intdigest()
    h2 = xxhash.xxh64(name.encode(), seed=1).intdigest()
    return h1.to_bytes(8, "little").hex() + h2.to_bytes(8, "little").hex()

# Query storage keys
for pallet, storage in [("Session", "Validators"), ("Babe", "Authorities"), ("Grandpa", "Authorities"), ("Dpos", "ActiveValidators"), ("Dpos", "ValidatorList"), ("Balances", "TotalIssuance")]:
    prefix = "0x" + twox128(pallet) + twox128(storage)
    result, error = rpc("state_getStorage", [prefix])
    if result and result != "0x" and len(result) > 4:
        if pallet == "Grandpa":
            authorities = decode_grandpa_authorities(result)
            if authorities:
                print(f"\n{pallet}::{storage}: {len(authorities)} authorities")
                for i, (a, w) in enumerate(authorities):
                    print(f"  {i+1}. {a} (weight={w})")
        elif pallet == "Balances":
            val = int.from_bytes(bytes.fromhex(result[2:])[:16], "little")
            print(f"\n{pallet}::{storage}: {val} ({val/1e9:.0f} VRDX)")
        else:
            accounts = decode_account_vec(result)
            if accounts:
                print(f"\n{pallet}::{storage}: {len(accounts)} authorities")
                for i, a in enumerate(accounts):
                    print(f"  {i+1}. {a}")
            else:
                print(f"\n{pallet}::{storage}: {result[:60]}...")
    else:
        print(f"\n{pallet}::{storage}: not found (error: {error})")

# Cross-check: active validators vs session/babe/grandpa
print("\n=== CROSS-CHECK ===")
active = rpc("dpos_activeValidators")[0]
print(f"DPoS ActiveValidators: {len(active)}")

# Get Session validators
sv_prefix = "0x" + twox128("Session") + twox128("Validators")
sv_result, _ = rpc("state_getStorage", [sv_prefix])
sv_accounts = decode_account_vec(sv_result) if sv_result else []

# Get BABE authorities
ba_prefix = "0x" + twox128("Babe") + twox128("Authorities")
ba_result, _ = rpc("state_getStorage", [ba_prefix])
ba_accounts = decode_account_vec(ba_result) if ba_result else []

# Get GRANDPA authorities
ga_prefix = "0x" + twox128("Grandpa") + twox128("Authorities")
ga_result, _ = rpc("state_getStorage", [ga_prefix])
ga_authorities = decode_grandpa_authorities(ga_result) if ga_result else []
ga_accounts = [a for a, w in ga_authorities]

if active and sv_accounts and ba_accounts and ga_accounts:
    print(f"Session == DPoS Active: {set(active) == set(sv_accounts)}")
    print(f"BABE == DPoS Active: {set(active) == set(ba_accounts)}")
    print(f"GRANDPA == DPoS Active: {set(active) == set(ga_accounts)}")
    print(f"All 4 match: {set(active) == set(sv_accounts) == set(ba_accounts) == set(ga_accounts)}")

    # Check each authority belongs to an active validator
    for i, (a, s, b, g) in enumerate(zip(active, sv_accounts, ba_accounts, ga_accounts)):
        match = a == s == b == g
        print(f"  {i+1}. DPoS={a[:16]}... Session={s[:16]}... BABE={b[:16]}... GRANDPA={g[:16]}... {'✓' if match else '✗'}")

# Check for duplicates
if active:
    print(f"\nDuplicate active validators: {len(active) != len(set(active))}")
if sv_accounts:
    print(f"Duplicate session validators: {len(sv_accounts) != len(set(sv_accounts))}")
if ba_accounts:
    print(f"Duplicate BABE authorities: {len(ba_accounts) != len(set(ba_accounts))}")
if ga_accounts:
    print(f"Duplicate GRANDPA authorities: {len(ga_accounts) != len(set(ga_accounts))}")

# Check no inactive validator is in consensus
all_validators = rpc("dpos_allValidators")[0]
inactive = [v for v in all_validators if v not in active] if all_validators else []
if inactive and sv_accounts:
    inactive_in_session = [v for v in inactive if v in sv_accounts]
    print(f"\nInactive validators in Session: {len(inactive_in_session)}")
    if inactive_in_session:
        print("  *** SECURITY ISSUE: Inactive validator in consensus! ***")
        for v in inactive_in_session:
            print(f"  {v}")

# Finality check
finalized = rpc("chain_getFinalizedHead")[0]
header = rpc("chain_getHeader")[0]
block_num = int(header["number"], 16) if header else 0
print(f"\nBlock: {block_num}, Finalized: {'Yes' if finalized else 'No'}")

# Get finalized block number
if finalized:
    fin_header = rpc("chain_getHeader", [finalized])[0]
    fin_num = int(fin_header["number"], 16) if fin_header else 0
    print(f"Finalized block: {fin_num}")
    print(f"Finality lag: {block_num - fin_num} blocks")
