#!/usr/bin/env python3
"""Verdis Chain Audit - P0: Verify validator architecture"""
import json, subprocess, sys

RPC = "http://localhost:9933"

def rpc(method, params=None):
    payload = {"jsonrpc": "2.0", "method": method, "params": params or [], "id": 1}
    r = subprocess.run(["curl", "-s", "-X", "POST", RPC, "-H", "Content-Type: application/json",
                       "-d", json.dumps(payload)], capture_output=True, text=True)
    return json.loads(r.stdout).get("result")

def rpc_storage(pallet, key):
    """Query storage via state_getStorage"""
    import hashlib
    # Twox64
    import struct
    def twox64(data, seed):
        import ctypes
        # Simple XXH64 implementation would be complex; use the RPC instead
        pass
    # Use state_getStorageHash to find keys
    return None

print("=" * 60)
print("P0-1: VERIFY VALIDATOR ARCHITECTURE")
print("=" * 60)

# 1. Chain info
header = rpc("chain_getHeader")
block_num = int(header["number"], 16) if header else 0
print(f"\nBlock height: {block_num}")

# 2. DPoS validators
all_validators = rpc("dpos_allValidators")
print(f"\nDPoS registered validators: {len(all_validators)}")
for i, v in enumerate(all_validators):
    print(f"  {i+1}. {v}")

# 3. DPoS active validators
active = rpc("dpos_activeValidators")
print(f"\nDPoS active validators: {len(active)}")
for i, v in enumerate(active):
    print(f"  {i+1}. {v}")

# 4. Session validators (via state_getStorage)
# Query session.validators
def twox128(name):
    import hashlib
    # XXH128 with seed=0 — need proper implementation
    # Use the runtime API instead
    pass

# Use state_call for Session::validators
try:
    session_vals = rpc("state_call", ["SessionValidators", "0x"])
    if session_vals:
        # Decode SCALE compact vec of AccountId32
        raw = bytes.fromhex(session_vals[2:])
        n = raw[0] >> 2
        offset = 1
        accounts = []
        for i in range(n):
            acct = raw[offset:offset+32]
            accounts.append("0x" + acct.hex())
            offset += 32
        print(f"\nSession::Validators: {len(accounts)}")
        for i, a in enumerate(accounts):
            print(f"  {i+1}. {a}")
    else:
        print("\nSession::Validators: Unable to query")
except Exception as e:
    print(f"\nSession::Validators: Error - {e}")

# 5. BABE authorities via state_call
try:
    babe_vals = rpc("state_call", ["BabeApiAuthorities", "0x"])
    if babe_vals:
        raw = bytes.fromhex(babe_vals[2:])
        n = raw[0] >> 2
        offset = 1
        accounts = []
        for i in range(n):
            acct = raw[offset:offset+32]
            accounts.append("0x" + acct.hex())
            offset += 32
        print(f"\nBABE::Authorities: {len(accounts)}")
        for i, a in enumerate(accounts):
            print(f"  {i+1}. {a}")
    else:
        print("\nBABE::Authorities: Unable to query")
except Exception as e:
    print(f"\nBABE::Authorities: Error - {e}")

# 6. GRANDPA authorities via state_call
try:
    grandpa_vals = rpc("state_call", ["GrandpaApiAuthorities", "0x"])
    if grandpa_vals:
        raw = bytes.fromhex(grandpa_vals[2:])
        # GRANDPA authorities are (AuthorityId, AuthorityWeight) pairs
        n = raw[0] >> 2
        offset = 1
        accounts = []
        for i in range(n):
            acct = raw[offset:offset+32]
            weight = int.from_bytes(raw[offset+32:offset+36], "little") if len(raw) > offset+36 else 0
            accounts.append(f"0x{acct.hex()} (weight={weight})")
            offset += 36  # 32 bytes ID + 4 bytes weight
        print(f"\nGRANDPA::Authorities: {len(accounts)}")
        for i, a in enumerate(accounts):
            print(f"  {i+1}. {a}")
    else:
        print("\nGRANDPA::Authorities: Unable to query")
except Exception as e:
    print(f"\nGRANDPA::Authorities: Error - {e}")

# 7. Peer count
peers = rpc("system_peers")
print(f"\nConnected peers: {len(peers) if peers else 0}")

# 8. Node count (system_networkState)
network = rpc("system_networkState")
if network:
    print(f"Node peerId: {network.get('peerId', '?')[:20]}...")

# 9. Active validator count config
try:
    avc = rpc("dpos_activeValidatorCount")
    print(f"\nActiveValidatorCount: {avc}")
except:
    print("\nActiveValidatorCount: Unable to query")

# 10. Check that active validators are a subset of registered
if all_validators and active:
    active_in_registered = all(a in all_validators for a in active)
    print(f"\nAll active validators in registered set: {active_in_registered}")
    inactive = [v for v in all_validators if v not in active]
    print(f"Registered but inactive: {len(inactive)}")
    for i, v in enumerate(inactive):
        print(f"  {i+1}. {v}")

# 11. Verify stake amounts
print("\n=== STAKE VERIFICATION ===")
for v in all_validators:
    stake = rpc("dpos_validatorStake", [v])
    is_active = v in active
    print(f"  {v[:20]}... stake={stake} active={is_active}")

# 12. Finality
finalized = rpc("chain_getFinalizedHead")
print(f"\nFinalized head: {finalized[:20] if finalized else 'None'}..." if finalized else "\nFinalized head: None")

# 13. Token supply
issuance = rpc("balances_totalIssuance")
if issuance:
    # Convert from U128 hex to int
    val = int(issuance, 16) if isinstance(issuance, str) else issuance
    print(f"\nTotalIssuance: {val} ({val / 1e9:.0f} VRDX)")
    target = 100_000_000_000 * 10**9
    print(f"Target: {target} ({target / 1e9:.0f} VRDX)")
    print(f"Match: {val == target}")
else:
    print("\nTotalIssuance: Unable to query")

print("\n" + "=" * 60)
print("P0-1 COMPLETE")
print("=" * 60)
