#!/usr/bin/env python3
"""Set session keys via Sudo+System::set_storage using raw SCALE encoding."""

import hashlib
import struct
import time
from substrateinterface import SubstrateInterface, Keypair

substrate = SubstrateInterface(url="http://127.0.0.1:9933", ss58_format=909, auto_discover=True)
sudo_kp = Keypair.create_from_uri("//Alice")

# Get runtime info
genesis_hash = substrate.get_block_hash(0)
rt_version = substrate.rpc_request("state_getRuntimeVersion", []).get("result", {})
spec_version = int(rt_version.get("specVersion", 11))
tx_version = int(rt_version.get("transactionVersion", 3))

def compact_encode(n):
    if n < 64: return bytes([n << 2])
    elif n < 16384: return struct.pack("<H", (n << 2) | 0x01)
    elif n < 1073741824: return struct.pack("<I", (n << 2) | 0x02)
    else: return struct.pack("<Q", (n << 2) | 0x03)

def twox64(data):
    """Compute xxHash64 with seed 0."""
    import xxhash
    return xxhash.xxh64(data, seed=0).digest()

def twox128(data):
    """Compute xxHash128 (two xxHash64 with different seeds)."""
    return twox64(data) + xxhash.xxh64(data, seed=1).digest()

def make_storage_key(pallet, storage, account_pubkey):
    """Build Substrate storage key for Session.NextKeys[account]."""
    prefix = twox128(pallet.encode()) + twox128(storage.encode())
    key_hash = twox64(account_pubkey) + account_pubkey
    return prefix + key_hash

def submit_raw_extrinsic(call_data, kp):
    """Submit a raw SCALE-encoded extrinsic signed by kp."""
    current_hash = substrate.get_chain_head()
    acct = substrate.query("System", "Account", [kp.ss58_address])
    nonce = acct.value.get("nonce", 0) if acct else 0
    
    # Build signing payload: call + era(0x00) + nonce(compact) + tip(0) + spec_version(u32) + tx_version(u32) + genesis + block_hash
    era = bytes([0x00])
    payload = call_data + era + compact_encode(nonce) + compact_encode(0)
    payload += struct.pack("<I", spec_version)
    payload += struct.pack("<I", tx_version)
    payload += bytes.fromhex(genesis_hash[2:])
    payload += bytes.fromhex(current_hash[2:])
    
    # Sign
    signature = kp.sign(payload)
    
    # Build extrinsic: 0x84 (signed v4) + 0x00 (AccountId32) + pubkey + 0x01 (Sr25519) + sig + era + nonce + tip + call
    babe_pub = bytes(kp.public_key)
    ext_body = bytes([0x84]) + bytes([0x00]) + babe_pub + bytes([0x01]) + signature + era + compact_encode(nonce) + compact_encode(0) + call_data
    ext_len = compact_encode(len(ext_body))
    full_hex = "0x" + (ext_len + ext_body).hex()
    
    result = substrate.rpc_request("author_submitExtrinsic", [full_hex])
    return result

success = 0
for n in range(22, 31):
    kp = Keypair.create_from_uri(f"//Validator{n}")
    addr = kp.ss58_address
    babe_pub = bytes(kp.public_key)
    
    # Generate ed25519 grandpa key
    seed = hashlib.sha256(f"//Grandpa{n}".encode()).digest()
    gp_kp = Keypair.create_from_seed(seed, crypto_type=1, ss58_format=909)
    grandpa_pub = bytes(gp_kp.public_key)
    
    # Check if already set
    nk = substrate.query("Session", "NextKeys", [addr])
    if nk and nk.value:
        print(f"V{n}: Already has keys")
        success += 1
        continue
    
    # Build storage key for Session.NextKeys[V{n}]
    storage_key = make_storage_key("Session", "NextKeys", babe_pub)
    
    # Build storage value: SessionKeys = babe(32) + grandpa(32)
    storage_value = babe_pub + grandpa_pub
    
    # Build inner call: System(0)::set_storage(4)
    # items: Vec<(Vec<u8>, Vec<u8>)> = compact(1) + (storage_key_len_prefix + storage_key, value_len_prefix + value)
    inner_call = bytes([0, 4])  # System::set_storage
    
    # Vec<(Vec<u8>, Vec<u8>)> with 1 item
    items = compact_encode(1)  # 1 item
    # First item: (storage_key, storage_value)
    items += compact_encode(len(storage_key)) + storage_key  # Vec<u8> key
    items += compact_encode(len(storage_value)) + storage_value  # Vec<u8> value
    
    inner_call += items
    
    # Build outer call: Sudo(6)::sudo(0) + inner_call
    outer_call = bytes([6, 0]) + inner_call
    
    print(f"V{n}: Submitting set_storage (key_len={len(storage_key)}, value_len={len(storage_value)})")
    
    result = submit_raw_extrinsic(outer_call, sudo_kp)
    
    if "result" in result:
        print(f"V{n}: OK (hash: {result['result'][:20]}...)")
        success += 1
    elif "error" in result:
        print(f"V{n}: Error - {result['error']}")
    else:
        print(f"V{n}: {result}")
    
    time.sleep(3)

print(f"\n{success}/9 submitted. Waiting 30s...")
time.sleep(30)

# Verify
total = substrate.query("Dpos", "ValidatorList", [])
keys_count = 0
for addr in total.value:
    nk = substrate.query("Session", "NextKeys", [addr])
    if nk and nk.value:
        keys_count += 1
print(f"Total validators: {len(total.value)}, with session keys: {keys_count}")

for n in range(22, 31):
    kp = Keypair.create_from_uri(f"//Validator{n}")
    nk = substrate.query("Session", "NextKeys", [kp.ss58_address])
    print(f"  V{n}: keys={'YES' if nk and nk.value else 'NO'}")
    if nk and nk.value:
        print(f"    babe: {str(nk.value.get('babe', ''))[:20]}...")
        print(f"    grandpa: {str(nk.value.get('grandpa', ''))[:20]}...")
