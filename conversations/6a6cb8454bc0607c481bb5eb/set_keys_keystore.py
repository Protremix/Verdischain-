#!/usr/bin/env python3
"""Set session keys for V22-V30 using author_insertKey + Session::set_keys."""
import hashlib
import struct
import time
from substrateinterface import SubstrateInterface, Keypair

s = SubstrateInterface(url="http://127.0.0.1:9933", ss58_format=909, auto_discover=True)

rt = s.rpc_request("state_getRuntimeVersion", []).get("result", {})
spec_version = int(rt.get("specVersion", 11))
tx_version = int(rt.get("transactionVersion", 3))
genesis_hash = bytes.fromhex(s.get_block_hash(0)[2:])

def compact(n):
    if n < 64: return bytes([n << 2])
    elif n < 16384: return struct.pack("<H", (n << 2) | 0x01)
    elif n < 1073741824: return struct.pack("<I", (n << 2) | 0x02)
    else: return struct.pack("<Q", (n << 2) | 0x03)

def submit_signed(call_data, kp):
    acct = s.query("System", "Account", [kp.ss58_address])
    nonce = acct.value.get("nonce", 0) if acct else 0
    era = bytes([0x00])
    payload = call_data + era + compact(nonce) + compact(0)
    payload += struct.pack("<I", spec_version) + struct.pack("<I", tx_version)
    payload += genesis_hash + genesis_hash
    sig = kp.sign(payload)
    body = bytes([0x84, 0x00]) + bytes(kp.public_key) + bytes([0x01]) + sig
    body += era + compact(nonce) + compact(0) + call_data
    ext_hex = "0x" + (compact(len(body)) + body).hex()
    return s.rpc_request("author_submitExtrinsic", [ext_hex]), nonce

# Find Session pallet index and set_keys call index
metadata = s.metadata
session_pallet = None
for pallet in metadata.pallets:
    if pallet.name == "Session":
        session_pallet = pallet
        break

if session_pallet and session_pallet.calls:
    for call in session_pallet.calls:
        print(f"Session call: {call.name} index={call.index}")
        if call.name == "set_keys":
            session_index = session_pallet.index
            set_keys_index = call.index
            print(f"Session index: {session_index}, set_keys index: {set_keys_index}")
            # Check args
            for arg in call.args:
                print(f"  arg: {arg.name} type={arg.type_name}")

print("\n--- Setting keys for V22-V30 ---\n")

success = 0
for n in range(22, 31):
    kp = Keypair.create_from_uri(f"//Validator{n}")
    addr = kp.ss58_address
    babe_pub = bytes(kp.public_key)
    babe_pub_hex = "0x" + babe_pub.hex()
    
    # Generate grandpa key
    seed = hashlib.sha256(f"//Grandpa{n}".encode()).digest()
    gp_kp = Keypair.create_from_seed(seed, crypto_type=1, ss58_format=909)
    grandpa_pub = bytes(gp_kp.public_key)
    grandpa_pub_hex = "0x" + grandpa_pub.hex()
    
    # Check if already has keys
    nk = s.query("Session", "NextKeys", [addr])
    if nk and nk.value:
        print(f"V{n}: Already has keys")
        success += 1
        continue
    
    # Insert babe key into keystore
    try:
        r1 = s.rpc_request("author_insertKey", ["babe", f"//Validator{n}", babe_pub_hex])
        print(f"V{n}: Insert babe key: {r1.get('result', r1)}")
    except Exception as e:
        print(f"V{n}: Insert babe key error: {e}")
    
    # Insert grandpa key into keystore
    gp_seed_hex = "0x" + seed.hex()
    try:
        r2 = s.rpc_request("author_insertKey", ["gran", gp_seed_hex, grandpa_pub_hex])
        print(f"V{n}: Insert grandpa key: {r2.get('result', r2)}")
    except Exception as e:
        print(f"V{n}: Insert grandpa key error: {e}")
    
    # Now call Session::set_keys
    # SessionKeys = { babe: AccountId, grandpa: AccountId }
    # set_keys(keys: SessionKeys, proof: Vec<u8>)
    # SessionIndex::set_keys_index
    # Call: session_index (1 byte) + set_keys_index (1 byte) + keys + proof
    
    # Encode keys: babe (32 bytes) + grandpa (32 bytes)
    keys_encoded = babe_pub + grandpa_pub
    # Proof: empty
    proof_encoded = compact(0)  # empty Vec<u8>
    
    # Build call
    call_data = bytes([session_index, set_keys_index])
    call_data += compact(len(keys_encoded)) + keys_encoded  # Actually, SessionKeys is a tuple, not a Vec
    # Wait, the encoding depends on the type. Let me check.
    # If SessionKeys is a struct { babe: AccountId, grandpa: AccountId }, it's encoded as babe + grandpa (64 bytes)
    # If it's a Vec<u8>, it's encoded as compact(len) + bytes
    # Let me try struct encoding first (just the 64 bytes)
    call_data = bytes([session_index, set_keys_index]) + keys_encoded + proof_encoded
    
    try:
        result, nonce = submit_signed(call_data, kp)
        if "result" in result:
            print(f"V{n}: set_keys submitted (nonce={nonce})")
            success += 1
        else:
            print(f"V{n}: set_keys error: {result}")
    except Exception as e:
        print(f"V{n}: set_keys exception: {e}")
    
    time.sleep(6)

print(f"\n{success}/9 submitted. Waiting 30s...")
time.sleep(30)

# Verify
total = s.query("Dpos", "ValidatorList", [])
keys_count = 0
for addr in total.value:
    nk = s.query("Session", "NextKeys", [addr])
    if nk and nk.value:
        keys_count += 1
print(f"\nTotal validators: {len(total.value)}, with session keys: {keys_count}")

for n in range(22, 31):
    kp = Keypair.create_from_uri(f"//Validator{n}")
    nk = s.query("Session", "NextKeys", [kp.ss58_address])
    has = "YES" if nk and nk.value else "NO"
    print(f"  V{n}: keys={has}")
