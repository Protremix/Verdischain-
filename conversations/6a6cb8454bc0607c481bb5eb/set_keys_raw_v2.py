#!/usr/bin/env python3
"""Set session keys using raw SCALE encoding + Alice's sudo key (fixed signing)."""

import hashlib
import struct
import time
from substrateinterface import SubstrateInterface, Keypair

s = SubstrateInterface(url="http://127.0.0.1:9933", ss58_format=909, auto_discover=True)
sudo_kp = Keypair.create_from_uri("//Alice")

# Get runtime version info
rt = s.rpc_request("state_getRuntimeVersion", []).get("result", {})
spec_version = int(rt.get("specVersion", 11))
tx_version = int(rt.get("transactionVersion", 3))

def compact(n):
    if n < 64:
        return bytes([n << 2])
    elif n < 16384:
        return struct.pack("<H", (n << 2) | 0x01)
    elif n < 1073741824:
        return struct.pack("<I", (n << 2) | 0x02)
    else:
        return struct.pack("<Q", (n << 2) | 0x03)

def build_set_keys_call(storage_key_bytes, storage_value_bytes):
    """Build SCALE-encoded Sudo::sudo(System::set_storage([(key, value)])) call."""
    # System(0)::set_storage(4)
    inner = bytes([0, 4])  # System::set_storage
    inner += compact(1)   # 1 item
    inner += compact(len(storage_key_bytes)) + storage_key_bytes
    inner += compact(len(storage_value_bytes)) + storage_value_bytes
    # Sudo(6)::sudo(0)
    outer = bytes([6, 0]) + inner
    return outer

def build_and_submit_extrinsic(call_data, kp):
    """Build a signed extrinsic and submit it."""
    genesis_hash = bytes.fromhex(s.get_block_hash(0)[2:])
    
    acct = s.query("System", "Account", [kp.ss58_address])
    nonce = acct.value.get("nonce", 0) if acct else 0
    
    # Signing payload for immortal era:
    # call || era(0x00) || nonce(compact) || tip(compact 0) || spec_version(u32 LE) || tx_version(u32 LE) || genesis_hash || genesis_hash
    era = bytes([0x00])
    payload = call_data + era + compact(nonce) + compact(0)
    payload += struct.pack("<I", spec_version)
    payload += struct.pack("<I", tx_version)
    payload += genesis_hash
    payload += genesis_hash  # For immortal, block_hash = genesis_hash
    
    # Sign payload
    signature = kp.sign(payload)
    
    # Build extrinsic body
    body = bytes([0x84])           # signed v4
    body += bytes([0x00])          # AccountId32
    body += bytes(kp.public_key)   # 32-byte pubkey
    body += bytes([0x01])          # sr25519
    body += signature              # 64-byte signature
    body += era                    # 0x00 Immortal
    body += compact(nonce)         # nonce
    body += compact(0)             # tip
    body += call_data              # the actual call
    
    ext_hex = "0x" + (compact(len(body)) + body).hex()
    
    return s.rpc_request("author_submitExtrinsic", [ext_hex])

success = 0
for n in range(22, 31):
    kp = Keypair.create_from_uri(f"//Validator{n}")
    addr = kp.ss58_address
    babe_pub = bytes(kp.public_key)
    
    nk = s.query("Session", "NextKeys", [addr])
    if nk and nk.value:
        print(f"V{n}: Already has keys")
        success += 1
        continue
    
    seed = hashlib.sha256(f"//Grandpa{n}".encode()).digest()
    gp_kp = Keypair.create_from_seed(seed, crypto_type=1, ss58_format=909)
    grandpa_pub = bytes(gp_kp.public_key)
    
    sk = s.create_storage_key("Session", "NextKeys", [addr])
    key_bytes = bytes.fromhex(sk.to_hex()[2:])
    value_bytes = babe_pub + grandpa_pub
    
    call_data = build_set_keys_call(key_bytes, value_bytes)
    print(f"V{n}: call={len(call_data)}B key={len(key_bytes)}B val={len(value_bytes)}B")
    
    try:
        result = build_and_submit_extrinsic(call_data, sudo_kp)
        if "result" in result:
            print(f"V{n}: OK (hash: {result['result'][:20]}...)")
            success += 1
        elif "error" in result:
            print(f"V{n}: RPC Error - {result['error']}")
        else:
            print(f"V{n}: {result}")
    except Exception as e:
        print(f"V{n}: Exception - {e}")
    time.sleep(5)

print(f"\n{success}/9 submitted. Waiting 30s...")
time.sleep(30)

# Verify
total = s.query("Dpos", "ValidatorList", [])
keys_count = 0
for addr in total.value:
    nk = s.query("Session", "NextKeys", [addr])
    if nk and nk.value:
        keys_count += 1
print(f"Total validators: {len(total.value)}, with session keys: {keys_count}")

for n in range(22, 31):
    kp = Keypair.create_from_uri(f"//Validator{n}")
    nk = s.query("Session", "NextKeys", [kp.ss58_address])
    has = "YES" if nk and nk.value else "NO"
    print(f"  V{n}: keys={has}")
    if nk and nk.value:
        print(f"    babe: {str(nk.value.get('babe',''))[:30]}")
        print(f"    grandpa: {str(nk.value.get('grandpa',''))[:30]}")
