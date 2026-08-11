#!/usr/bin/env python3
"""P0-2 FIXED: Cross-check DPoS → Session → BABE → GRANDPA with proper SS58↔hex conversion"""
import json, subprocess, base58, hashlib

RPC = "http://localhost:9933"

def rpc(method, params=None):
    payload = {"jsonrpc": "2.0", "method": method, "params": params or [], "id": 1}
    r = subprocess.run(["curl", "-s", "-X", "POST", RPC, "-H", "Content-Type: application/json",
                       "-d", json.dumps(payload)], capture_output=True, text=True)
    return json.loads(r.stdout).get("result")

def ss58_to_hex(ss58_addr):
    """Convert SS58 address to 0x-prefixed AccountId32 hex"""
    decoded = base58.b58decode(ss58_addr)
    # SS58 format: prefix (1-2 bytes) + 32-byte AccountId + 2-byte checksum
    # Prefix 909 (Verdis) = 0x03 0x8d
    if len(decoded) >= 35:
        acct = decoded[2:34]  # skip 2-byte prefix, take 32 bytes
        return "0x" + acct.hex()
    elif len(decoded) >= 34:
        acct = decoded[1:33]  # skip 1-byte prefix
        return "0x" + acct.hex()
    return None

# Install base58 if needed
subprocess.run(["pip", "install", "base58", "-q"], capture_output=True)

# Known Alice-Ferdie AccountId32 values
known_accounts = {
    "0xd43593c715fdd31c61141abd04a99fd6822c8558854ccde39a5684e7a56da27d": "Alice",
    "0x8eaf04151687736326c9fea17e25fc5287613693c912909cb226aa4794f26a48": "Bob",
    "0x90b5ab205c6974c9ea841be688864633dc9ca8a357843eeacf2314649965fe22": "Charlie",
    "0x306721211d5404bd9da88e0204360a1a9ab8b87c66c1bc2fcdd37f3c2222cc20": "Dave",
    "0xe659a7a1628cdd93febc04a4e0646ea20e9f5f0ce097d9a05290d4a9e054df4e": "Eve",
    "0x1cbd2d43530a44705ad088af313e18f80b53ef16b36177cd4b77b846f2a5f07c": "Ferdie",
}

print("=" * 60)
print("P0-2: DPoS → Session → BABE → GRANDPA CROSS-CHECK (FIXED)")
print("=" * 60)

# 1. DPoS Active Validators (SS58)
active_ss58 = rpc("dpos_activeValidators")
active_hex = [ss58_to_hex(a) for a in active_ss58]
print(f"\nDPoS ActiveValidators: {len(active_hex)}")
for i, (ss58, h) in enumerate(zip(active_ss58, active_hex)):
    name = known_accounts.get(h, f"V{int(h[-2:], 16) if h else '?'}")
    print(f"  {i+1}. {name}: {h}")

# 2. Session::Validators (AccountId32 hex)
import xxhash
def twox128(name):
    h1 = xxhash.xxh64(name.encode(), seed=0).intdigest()
    h2 = xxhash.xxh64(name.encode(), seed=1).intdigest()
    return h1.to_bytes(8, "little").hex() + h2.to_bytes(8, "little").hex()

sv_key = "0x" + twox128("Session") + twox128("Validators")
sv_raw = rpc("state_getStorage", [sv_key])
sv_accounts = []
if sv_raw:
    raw = bytes.fromhex(sv_raw[2:])
    n = raw[0] >> 2
    offset = 1
    for i in range(n):
        acct = "0x" + raw[offset:offset+32].hex()
        sv_accounts.append(acct)
        offset += 32

print(f"\nSession::Validators: {len(sv_accounts)}")
for i, h in enumerate(sv_accounts):
    name = known_accounts.get(h, "Unknown")
    print(f"  {i+1}. {name}: {h}")

# 3. BABE::Authorities (BabeId = AccountId32 + u64 weight)
ba_key = "0x" + twox128("Babe") + twox128("Authorities")
ba_raw = rpc("state_getStorage", [ba_key])
ba_accounts = []
if ba_raw:
    raw = bytes.fromhex(ba_raw[2:])
    n = raw[0] >> 2
    offset = 1
    for i in range(n):
        acct = "0x" + raw[offset:offset+32].hex()
        weight = int.from_bytes(raw[offset+32:offset+40], "little")
        ba_accounts.append((acct, weight))
        offset += 40

print(f"\nBABE::Authorities: {len(ba_accounts)}")
for i, (h, w) in enumerate(ba_accounts):
    name = known_accounts.get(h, "Unknown")
    print(f"  {i+1}. {name}: {h} (weight={w})")

# 4. GRANDPA::Authorities (GrandpaId = 32 bytes + u64 weight)
ga_key = "0x" + twox128("Grandpa") + twox128("Authorities")
ga_raw = rpc("state_getStorage", [ga_key])
ga_accounts = []
if ga_raw:
    raw = bytes.fromhex(ga_raw[2:])
    n = raw[0] >> 2
    offset = 1
    for i in range(n):
        acct = "0x" + raw[offset:offset+32].hex()
        weight = int.from_bytes(raw[offset+32:offset+40], "little")
        ga_accounts.append((acct, weight))
        offset += 40

print(f"\nGRANDPA::Authorities: {len(ga_accounts)}")
for i, (h, w) in enumerate(ga_accounts):
    # GRANDPA keys are NOT AccountIds — they're separate key types
    print(f"  {i+1}. {h} (weight={w})")

# 5. Cross-check: DPoS Active == Session
print("\n=== CROSS-CHECK RESULTS ===")
dpos_set = set(active_hex)
session_set = set(sv_accounts)
babe_set = set(h for h, w in ba_accounts)

print(f"DPoS Active == Session: {dpos_set == session_set}")
print(f"DPoS Active == BABE: {dpos_set == babe_set}")
print(f"Session == BABE: {session_set == babe_set}")

# GRANDPA uses different key types (not AccountIds), so we verify count + no duplicates
print(f"GRANDPA count == 6: {len(ga_accounts) == 6}")
print(f"GRANDPA no duplicates: {len(set(h for h, w in ga_accounts)) == len(ga_accounts)}")
print(f"GRANDPA all weights == 1: {all(w == 1 for h, w in ga_accounts)}")

# 6. Verify NO inactive validator in consensus
all_validators_ss58 = rpc("dpos_allValidators")
all_validators_hex = [ss58_to_hex(v) for v in all_validators_ss58]
inactive_hex = [h for h in all_validators_hex if h not in dpos_set]

print(f"\nInactive validators: {len(inactive_hex)}")
inactive_in_session = [h for h in inactive_hex if h in session_set]
inactive_in_babe = [h for h in inactive_hex if h in babe_set]
print(f"Inactive in Session: {len(inactive_in_session)}")
print(f"Inactive in BABE: {len(inactive_in_babe)}")

if not inactive_in_session and not inactive_in_babe:
    print("✓ PASS: No inactive validator participates in consensus")
else:
    print("✗ FAIL: Inactive validator found in consensus authorities!")

# 7. Finality
finalized = rpc("chain_getFinalizedHead")
header = rpc("chain_getHeader")
block_num = int(header["number"], 16) if header else 0
if finalized:
    fin_header = rpc("chain_getHeader", [finalized])
    fin_num = int(fin_header["number"], 16) if fin_header else 0
    print(f"\nBlock: {block_num}, Finalized: {fin_num}, Lag: {block_num - fin_num}")

# 8. Token supply
ti_key = "0x" + twox128("Balances") + twox128("TotalIssuance")
ti_raw = rpc("state_getStorage", [ti_key])
if ti_raw:
    ti = int.from_bytes(bytes.fromhex(ti_raw[2:])[:16], "little")
    target = 100_000_000_000 * 10**9
    print(f"\nTotalIssuance: {ti} ({ti/1e9:.0f} VRDX)")
    print(f"Target: {target} ({target/1e9:.0f} VRDX)")
    print(f"Match: {ti == target}")

# 9. Summary
print("\n" + "=" * 60)
print("P0-2 VERDICT:")
print("=" * 60)
checks = [
    ("DPoS ActiveValidators == 6", len(active_hex) == 6),
    ("Session::Validators == 6", len(sv_accounts) == 6),
    ("BABE::Authorities == 6", len(ba_accounts) == 6),
    ("GRANDPA::Authorities == 6", len(ga_accounts) == 6),
    ("DPoS == Session (same set)", dpos_set == session_set),
    ("DPoS == BABE (same set)", dpos_set == babe_set),
    ("No inactive validator in consensus", not inactive_in_session and not inactive_in_babe),
    ("No duplicate authorities", 
     len(dpos_set) == len(active_hex) and 
     len(session_set) == len(sv_accounts) and 
     len(babe_set) == len(ba_accounts)),
    ("GRANDPA all weight=1", all(w == 1 for h, w in ga_accounts)),
    ("Finality working", finalized is not None),
    ("TotalIssuance == 100B VRDX", ti == target if ti_raw else False),
]
all_pass = True
for check, result in checks:
    status = "✓ PASS" if result else "✗ FAIL"
    if not result:
        all_pass = False
    print(f"  {status}: {check}")

print(f"\nOverall: {'ALL PASS' if all_pass else 'FAILURES DETECTED'}")
