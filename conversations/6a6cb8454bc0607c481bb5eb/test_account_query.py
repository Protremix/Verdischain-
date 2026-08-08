import xxhash
import struct
import urllib.request
import json
import hashlib

def twox_128(data):
    h0 = xxhash.xxh64(data, seed=0).intdigest()
    h1 = xxhash.xxh64(data, seed=1).intdigest()
    return struct.pack("<Q", h0) + struct.pack("<Q", h1)

def twox_64(data, seed=0):
    h = xxhash.xxh64(data, seed=seed).intdigest()
    return struct.pack("<Q", h)

def rpc_call(method, params, port=9933):
    data = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(f"http://localhost:{port}", data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

# System::Account prefix
sys_hash = twox_128(b"System")
acc_hash = twox_128(b"Account")
prefix = sys_hash + acc_hash
prefix_hex = "0x" + prefix.hex()

print(f"System::Account prefix: {prefix_hex}")

# Alice's account
alice_hex = "d43593c715fdd31c61141abd04a99fd6822c8558854ccde39a5684e7a56da27d"
alice_bytes = bytes.fromhex(alice_hex)

# Try Twox64Concat: prefix ++ twox_64(account) ++ account
alice_key_twox = prefix + twox_64(alice_bytes) + alice_bytes
alice_key_hex = "0x" + alice_key_twox.hex()
print(f"\nAlice key (Twox64Concat): {alice_key_hex[:80]}... ({len(alice_key_twox)} bytes)")
val = rpc_call("state_getStorage", [alice_key_hex]).get("result", "")
if val and val != "null":
    val_bytes = bytes.fromhex(val[2:])
    print(f"  Value: {len(val_bytes)} bytes = {val[:80]}")
    if len(val_bytes) >= 48:
        nonce = struct.unpack_from("<I", val_bytes, 0)[0]
        consumers = struct.unpack_from("<I", val_bytes, 4)[0]
        providers = struct.unpack_from("<I", val_bytes, 8)[0]
        sufficients = struct.unpack_from("<I", val_bytes, 12)[0]
        free = int.from_bytes(val_bytes[16:32], "little")
        reserved = int.from_bytes(val_bytes[32:48], "little")
        print(f"  Alice: nonce={nonce} consumers={consumers} providers={providers} sufficients={sufficients}")
        print(f"  free={free/10**9:.4f} VRDX reserved={reserved/10**9:.4f} VRDX")
else:
    print("  Value: null")

# Try Blake2_256: prefix ++ blake2_256(account)
alice_key_blake = prefix + hashlib.blake2b(alice_bytes, digest_size=32).digest()
alice_key_blake_hex = "0x" + alice_key_blake.hex()
print(f"\nAlice key (Blake2_256): {alice_key_blake_hex[:80]}... ({len(alice_key_blake)} bytes)")
val = rpc_call("state_getStorage", [alice_key_blake_hex]).get("result", "")
if val and val != "null":
    val_bytes = bytes.fromhex(val[2:])
    print(f"  Value: {len(val_bytes)} bytes = {val[:80]}")
    if len(val_bytes) >= 48:
        nonce = struct.unpack_from("<I", val_bytes, 0)[0]
        free = int.from_bytes(val_bytes[16:32], "little")
        print(f"  Alice: nonce={nonce} free={free/10**9:.4f} VRDX")
else:
    print("  Value: null")

# Try Identity: prefix ++ account (raw)
alice_key_identity = prefix + alice_bytes
alice_key_identity_hex = "0x" + alice_key_identity.hex()
print(f"\nAlice key (Identity): {alice_key_identity_hex[:80]}... ({len(alice_key_identity)} bytes)")
val = rpc_call("state_getStorage", [alice_key_identity_hex]).get("result", "")
if val and val != "null":
    val_bytes = bytes.fromhex(val[2:])
    print(f"  Value: {len(val_bytes)} bytes = {val[:80]}")
    if len(val_bytes) >= 48:
        nonce = struct.unpack_from("<I", val_bytes, 0)[0]
        free = int.from_bytes(val_bytes[16:32], "little")
        print(f"  Alice: nonce={nonce} free={free/10**9:.4f} VRDX")
else:
    print("  Value: null")

# Also try Blake2_128Concat: prefix ++ blake2_128(account) ++ account
alice_key_b128 = prefix + hashlib.blake2b(alice_bytes, digest_size=16).digest() + alice_bytes
alice_key_b128_hex = "0x" + alice_key_b128.hex()
print(f"\nAlice key (Blake2_128Concat): {alice_key_b128_hex[:80]}... ({len(alice_key_b128)} bytes)")
val = rpc_call("state_getStorage", [alice_key_b128_hex]).get("result", "")
if val and val != "null":
    val_bytes = bytes.fromhex(val[2:])
    print(f"  Value: {len(val_bytes)} bytes = {val[:80]}")
    if len(val_bytes) >= 48:
        nonce = struct.unpack_from("<I", val_bytes, 0)[0]
        free = int.from_bytes(val_bytes[16:32], "little")
        print(f"  Alice: nonce={nonce} free={free/10**9:.4f} VRDX")
else:
    print("  Value: null")

# Check actual keys in storage to reverse-engineer the hasher
print(f"\n=== Checking actual keys in storage ===")
keys = rpc_call("state_getKeys", [prefix_hex]).get("result", [])
print(f"Total keys: {len(keys)}")
if keys:
    for k in keys[:3]:
        suffix = k[len(prefix_hex):]
        suffix_bytes = bytes.fromhex(suffix)
        print(f"  Suffix: {len(suffix_bytes)} bytes = {suffix[:40]}")
        val = rpc_call("state_getStorage", [k]).get("result", "")
        if val and val != "null":
            val_bytes = bytes.fromhex(val[2:])
            print(f"  Value: {len(val_bytes)} bytes")
            if len(val_bytes) >= 48:
                nonce = struct.unpack_from("<I", val_bytes, 0)[0]
                free = int.from_bytes(val_bytes[16:32], "little")
                print(f"  nonce={nonce} free={free/10**9:.4f} VRDX")
