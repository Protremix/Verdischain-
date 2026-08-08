import xxhash
import struct
import urllib.request
import json

def twox_128(data):
    """Substrate twox_128: concatenation of xxhash_64 with seed=0 and seed=1"""
    h0 = xxhash.xxh64(data, seed=0)
    h1 = xxhash.xxh64(data, seed=1)
    return h0.digest() + h1.digest()

def twox_64(data, seed=0):
    """Substrate twox_64"""
    h = xxhash.xxh64(data, seed=seed)
    return h.digest()

def rpc_call(method, params, port=9933):
    data = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(f"http://localhost:{port}", data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

# Test: twox_128("System") should be 26aa394eea5630e07c48ae0c9558cef7
sys_hash = twox_128(b"System")
print(f"System: {sys_hash.hex()}")
assert sys_hash.hex() == "26aa394eea5630e07c48ae0c9558cef7", "System hash mismatch!"
print("System hash verified!")

# twox_128("Account")
acc_hash = twox_128(b"Account")
print(f"Account: {acc_hash.hex()}")

# Full prefix for System::Account
prefix = sys_hash + acc_hash
prefix_hex = "0x" + prefix.hex()
print(f"System::Account prefix: {prefix_hex}")

# Check what storage items exist under the System pallet
for item_name in ["Account", "Events", "BlockHash", "Number", "Digest", "ParentHash", "AllExtrinsicsLen", "BlockWeight", "EventCount", "Account"]:
    item_hash = twox_128(item_name.encode())
    full_prefix = "0x" + (sys_hash + item_hash).hex()
    count = len(rpc_call("state_getKeys", [full_prefix]).get("result", []))
    print(f"  System::{item_name}: {count} keys (prefix: {full_prefix[:40]}...)")

# Now check Account storage specifically
keys = rpc_call("state_getKeys", [prefix_hex]).get("result", [])
print(f"\nSystem::Account keys: {len(keys)}")

# Check key suffix lengths
if keys:
    for k in keys[:3]:
        suffix = k[len(prefix_hex):]
        suffix_bytes = bytes.fromhex(suffix)
        print(f"  Suffix: {suffix} ({len(suffix_bytes)} bytes)")
    
    # The suffix is 12 bytes. Let me check if it is twox_64Concat(account_id)
    # twox_64Concat = twox_64(key, seed=0) ++ key
    # For 32-byte account: 8 + 32 = 40 bytes. But suffix is 12 bytes.
    # For 4-byte account: 8 + 4 = 12 bytes! That matches!
    
    # Maybe the account IDs are only 4 bytes? No, sr25519 accounts are 32 bytes.
    # Let me try: maybe these are NOT account storage but something else.
    
    # Check value of first key
    val = rpc_call("state_getStorage", [keys[0]]).get("result", "")
    if val:
        val_bytes = bytes.fromhex(val[2:])
        print(f"\n  First key value: {len(val_bytes)} bytes = {val[:60]}")
        
    # Let me try computing a key for Alice using Twox64Concat
    alice_hex = "d43593c715fdd31c61141abd04a99fd6822c8558854ccde39a5684e7a56da27d"
    alice_bytes = bytes.fromhex(alice_hex)
    
    # Twox64Concat
    alice_key_twox = prefix + twox_64(alice_bytes) + alice_bytes
    alice_key_hex = "0x" + alice_key_twox.hex()
    print(f"\n  Alice key (Twox64Concat): {alice_key_hex[:80]}... ({len(alice_key_twox)} bytes)")
    val = rpc_call("state_getStorage", [alice_key_hex]).get("result", "")
    if val:
        val_bytes = bytes.fromhex(val[2:])
        print(f"  Value: {len(val_bytes)} bytes = {val[:80]}")
        if len(val_bytes) >= 48:
            nonce = struct.unpack_from("<I", val_bytes, 0)[0]
            free = int.from_bytes(val_bytes[16:32], "little")
            print(f"  Alice: nonce={nonce} free={free/10**9:.2f} VRDX")
    else:
        print("  Value: null")
    
    # Try Blake2_256
    import hashlib
    alice_key_blake = prefix + hashlib.blake2b(alice_bytes, digest_size=32).digest()
    alice_key_blake_hex = "0x" + alice_key_blake.hex()
    print(f"\n  Alice key (Blake2_256): {alice_key_blake_hex[:80]}... ({len(alice_key_blake)} bytes)")
    val = rpc_call("state_getStorage", [alice_key_blake_hex]).get("result", "")
    if val:
        val_bytes = bytes.fromhex(val[2:])
        print(f"  Value: {len(val_bytes)} bytes = {val[:80]}")
        if len(val_bytes) >= 48:
            nonce = struct.unpack_from("<I", val_bytes, 0)[0]
            free = int.from_bytes(val_bytes[16:32], "little")
            print(f"  Alice: nonce={nonce} free={free/10**9:.2f} VRDX")
    else:
        print("  Value: null")
    
    # Try Identity (just the raw key)
    alice_key_identity = prefix + alice_bytes
    alice_key_identity_hex = "0x" + alice_key_identity.hex()
    print(f"\n  Alice key (Identity): {alice_key_identity_hex[:80]}... ({len(alice_key_identity)} bytes)")
    val = rpc_call("state_getStorage", [alice_key_identity_hex]).get("result", "")
    if val:
        val_bytes = bytes.fromhex(val[2:])
        print(f"  Value: {len(val_bytes)} bytes = {val[:80]}")
        if len(val_bytes) >= 48:
            nonce = struct.unpack_from("<I", val_bytes, 0)[0]
            free = int.from_bytes(val_bytes[16:32], "little")
            print(f"  Alice: nonce={nonce} free={free/10**9:.2f} VRDX")
    else:
        print("  Value: null")
