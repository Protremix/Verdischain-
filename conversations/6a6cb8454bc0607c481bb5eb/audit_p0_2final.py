#!/usr/bin/env python3
"""P0-2 FINAL: Cross-check using storage AccountId32 values, not SS58"""
import json, subprocess

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

def get_storage_accounts(pallet, storage):
    key = "0x" + twox128(pallet) + twox128(storage)
    raw = rpc("state_getStorage", [key])
    if not raw or raw == "0x":
        return []
    data = bytes.fromhex(raw[2:])
    n = data[0] >> 2
    offset = 1
    accounts = []
    for i in range(n):
        accounts.append("0x" + data[offset:offset+32].hex())
        offset += 32
    return accounts

def get_storage_authorities_with_weight(pallet, storage):
    key = "0x" + twox128(pallet) + twox128(storage)
    raw = rpc("state_getStorage", [key])
    if not raw or raw == "0x":
        return []
    data = bytes.fromhex(raw[2:])
    n = data[0] >> 2
    offset = 1
    authorities = []
    for i in range(n):
        acct = "0x" + data[offset:offset+32].hex()
        weight = int.from_bytes(data[offset+32:offset+40], "little")
        authorities.append((acct, weight))
        offset += 40
    return authorities

known = {
    "0xd43593c715fdd31c61141abd04a99fd6822c8558854ccde39a5684e7a56da27d": "Alice",
    "0x8eaf04151687736326c9fea17e25fc5287613693c912909cb226aa4794f26a48": "Bob",
    "0x90b5ab205c6974c9ea841be688864633dc9ca8a357843eeacf2314649965fe22": "Charlie",
    "0x306721211d5404bd9da88e0204360a1a9ab8b87c66c1bc2fcdd37f3c2222cc20": "Dave",
    "0xe659a7a1628cdd93febc04a4e0646ea20e9f5f0ce097d9a05290d4a9e054df4e": "Eve",
    "0x1cbd2d43530a44705ad088af313e18f80b53ef16b36177cd4b77b846f2a5f07c": "Ferdie",
}

print("=" * 60)
print("P0-2 FINAL: DPoS → Session → BABE → GRANDPA CONSISTENCY")
print("=" * 60)

# Query all 4 authority sets via storage (AccountId32 hex)
dpos_active = get_storage_accounts("Dpos", "ActiveValidators")
dpos_all = get_storage_accounts("Dpos", "ValidatorList")
session = get_storage_accounts("Session", "Validators")
babe = get_storage_authorities_with_weight("Babe", "Authorities")
grandpa = get_storage_authorities_with_weight("Grandpa", "Authorities")

babe_accts = [a for a, w in babe]
grandpa_accts = [a for a, w in grandpa]

def name_of(h):
    return known.get(h, h[:12] + "...")

print(f"\nDPoS ActiveValidators: {len(dpos_active)}")
for i, h in enumerate(dpos_active):
    print(f"  {i+1}. {name_of(h)}")

print(f"\nDPoS RegisteredValidators: {len(dpos_all)}")
for i, h in enumerate(dpos_all):
    print(f"  {i+1}. {name_of(h)}")

print(f"\nSession::Validators: {len(session)}")
for i, h in enumerate(session):
    print(f"  {i+1}. {name_of(h)}")

print(f"\nBABE::Authorities: {len(babe)}")
for i, (h, w) in enumerate(babe):
    print(f"  {i+1}. {name_of(h)} (weight={w})")

print(f"\nGRANDPA::Authorities: {len(grandpa)}")
for i, (h, w) in enumerate(grandpa):
    print(f"  {i+1}. {h[:12]}... (weight={w})")

# Cross-checks
print("\n=== CROSS-CHECK ===")
dpos_set = set(dpos_active)
session_set = set(session)
babe_set = set(babe_accts)

print(f"DPoS Active == Session: {dpos_set == session_set}")
print(f"DPoS Active == BABE: {dpos_set == babe_set}")
print(f"Session == BABE: {session_set == babe_set}")
print(f"GRANDPA count == 6: {len(grandpa) == 6}")
print(f"GRANDPA weights all == 1: {all(w == 1 for h, w in grandpa)}")
print(f"GRANDPA no duplicates: {len(set(grandpa_accts)) == len(grandpa_accts)}")

# Inactive validators not in consensus
inactive = [h for h in dpos_all if h not in dpos_set]
inactive_in_session = [h for h in inactive if h in session_set]
inactive_in_babe = [h for h in inactive if h in babe_set]
print(f"\nInactive validators: {len(inactive)}")
print(f"Inactive in Session: {len(inactive_in_session)}")
print(f"Inactive in BABE: {len(inactive_in_babe)}")
print(f"No inactive in consensus: {not inactive_in_session and not inactive_in_babe}")

# Duplicates
print(f"\nDuplicate DPoS active: {len(dpos_active) != len(dpos_set)}")
print(f"Duplicate Session: {len(session) != len(session_set)}")
print(f"Duplicate BABE: {len(babe_accts) != len(babe_set)}")

# Token supply
ti_key = "0x" + twox128("Balances") + twox128("TotalIssuance")
ti_raw = rpc("state_getStorage", [ti_key])
ti = int.from_bytes(bytes.fromhex(ti_raw[2:])[:16], "little") if ti_raw else 0
target = 100_000_000_000 * 10**9
print(f"\nTotalIssuance: {ti/1e9:.0f} VRDX (target: {target/1e9:.0f} VRDX)")
print(f"Match: {ti == target}")

# Finality
finalized = rpc("chain_getFinalizedHead")
header = rpc("chain_getHeader")
block_num = int(header["number"], 16) if header else 0
if finalized:
    fin_header = rpc("chain_getHeader", [finalized])
    fin_num = int(fin_header["number"], 16) if fin_header else 0
    print(f"\nBlock: {block_num}, Finalized: {fin_num}, Lag: {block_num - fin_num}")

# Verdict
print("\n" + "=" * 60)
print("P0-2 VERDICT")
print("=" * 60)
checks = [
    ("DPoS ActiveValidators == 6", len(dpos_active) == 6),
    ("DPoS RegisteredValidators == 21", len(dpos_all) == 21),
    ("Session::Validators == 6", len(session) == 6),
    ("BABE::Authorities == 6", len(babe) == 6),
    ("GRANDPA::Authorities == 6", len(grandpa) == 6),
    ("DPoS Active set == Session set", dpos_set == session_set),
    ("DPoS Active set == BABE set", dpos_set == babe_set),
    ("Session set == BABE set", session_set == babe_set),
    ("No inactive validator in consensus", not inactive_in_session and not inactive_in_babe),
    ("No duplicate authorities", len(dpos_active) == len(dpos_set) and len(session) == len(session_set) and len(babe_accts) == len(babe_set)),
    ("GRANDPA all weights == 1", all(w == 1 for h, w in grandpa)),
    ("Finality working", finalized is not None),
    ("TotalIssuance == 100B VRDX", ti == target),
]
all_pass = True
for check, result in checks:
    status = "✓ PASS" if result else "✗ FAIL"
    if not result: all_pass = False
    print(f"  {status}: {check}")
print(f"\nOverall: {'ALL PASS ✓' if all_pass else 'FAILURES ✗'}")
