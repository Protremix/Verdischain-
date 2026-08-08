#!/usr/bin/env python3
"""Set session keys for validators using raw SCALE encoding."""

import hashlib
import struct
import requests
from substrateinterface import SubstrateInterface, Keypair

substrate = SubstrateInterface(url="http://127.0.0.1:9933", ss58_format=909, auto_discover=True)
DECIMALS = 9

# Get genesis hash and runtime version
genesis_hash = substrate.get_block_hash(0)
current_hash = substrate.get_chain_head()
rt_version = substrate.runtime_version
spec_version = rt_version.get("spec_version", 1)
tx_version = rt_version.get("transaction_version", 1)
print(f"Spec: {spec_version}, TX: {tx_version}")
print(f"Genesis: {genesis_hash}")

def compact_encode(n):
    """SCALE compact encode an integer."""
    if n < 64:
        return bytes([n << 2])
    elif n < 16384:
        return struct.pack("<H", (n << 2) | 0x01)
    elif n < 1073741824:
        return struct.pack("<I", (n << 2) | 0x02)
    else:
        return struct.pack("<Q", (n << 2) | 0x03)

def set_session_keys(n):
    """Set session keys for validator V{n}."""
    uri = f"//Validator{n}"
    kp = Keypair.create_from_uri(uri)
    addr = kp.ss58_address
    babe_pub = bytes(kp.public_key)
    seed = hashlib.sha256(f"//Grandpa{n}".encode()).digest()
    gp_kp = Keypair.create_from_seed(seed, crypto_type=0, ss58_format=909)
    grandpa_pub = bytes(gp_kp.public_key)
    
    # Get nonce
    acct = substrate.query("System", "Account", [addr])
    nonce = acct.value.get("nonce", 0) if acct else 0
    
    # Check if already set
    nk = substrate.query("Session", "NextKeys", [addr])
    if nk and nk.value:
        print(f"V{n}: Already has keys")
        return True
    
    # Build the call: Session(7).set_keys(0)
    # Keys: {babe: [32 bytes], grandpa: [32 bytes]}
    # Proof: Vec<u8> = 0x00 (empty)
    call_data = bytes([7, 0]) + babe_pub + grandpa_pub + bytes([0])
    
    # Build the signing payload:
    # call_data + era(0x00 immortal) + nonce(compact) + tip(compact 0) + spec_version(u32 LE) + tx_version(u32 LE) + genesis_hash(32) + block_hash(32)
    era = bytes([0x00])  # immortal era
    payload = call_data + era + compact_encode(nonce) + compact_encode(0)
    payload += struct.pack("<I", spec_version)
    payload += struct.pack("<I", tx_version)
    payload += bytes.fromhex(genesis_hash[2:])
    payload += bytes.fromhex(current_hash[2:])
    
    # Sign the payload (sr25519 signs the blake2b hash of the payload)
    signature = kp.sign(payload)
    
    # Build the signed extrinsic:
    # Format: 
    # - 4 bytes: "signed" indicator (0x80 0x00 0x00 0x00 for V4 unsigned? No...)
    # Actually, for Substrate extrinsic format v4:
    # - byte: 0x80 for signed, 0x00 for unsigned (bit 7 = signed)
    #   + bit 0-6: version (4)
    # So: 0x84 = signed + version 4
    # - Signer: MultiAddress::AccountId32 = 0x00 + 32 bytes
    # - Signature: MultiSignature::Sr25519 = 0x01 + 64 bytes
    # - Extra: era(1) + nonce(compact) + tip(compact)
    # - Call data
    
    signed_byte = bytes([0x84])  # signed + version 4
    signer = bytes([0x00]) + babe_pub  # MultiAddress::AccountId32
    sig = bytes([0x01]) + signature  # MultiSignature::Sr25519
    extra = era + compact_encode(nonce) + compact_encode(0)
    
    extrinsic_body = signed_byte + signer + sig + extra + call_data
    
    # Add length prefix (compact encoding)
    ext_length = len(extrinsic_body)
    length_prefix = compact_encode(ext_length)
    
    full_extrinsic = "0x" + (length_prefix + extrinsic_body).hex()
    
    print(f"V{n}: nonce={nonce}, ext_length={ext_length}")
    
    # Submit via RPC
    result = substrate.rpc_request("author_submitExtrinsic", [full_extrinsic])
    if "result" in result:
        print(f"V{n}: Submitted OK (hash: {result['result'][:20]}...)")
        return True
    elif "error" in result:
        print(f"V{n}: Error - {result['error']}")
        return False
    else:
        print(f"V{n}: Unknown result: {result}")
        return False

# Set keys for all 9 validators
success = 0
for n in range(22, 31):
    try:
        if set_session_keys(n):
            success += 1
    except Exception as e:
        print(f"V{n}: Exception - {e}")
        import traceback
        traceback.print_exc()

print(f"\n{success}/9 submitted")

# Wait and verify
import time
print("Waiting 30s..."); time.sleep(30)

total = substrate.query("Dpos", "ValidatorList", [])
keys_count = 0
for addr in total.value:
    nk = substrate.query("Session", "NextKeys", [addr])
    if nk and nk.value:
        keys_count += 1
print(f"Total validators: {len(total.value)}, with session keys: {keys_count}")

for n in range(22, 31):
    kp = Keypair.create_from_uri(f"//Validator{n}")
    addr = kp.ss58_address
    nk = substrate.query("Session", "NextKeys", [addr])
    has_keys = "YES" if nk and nk.value else "NO"
    print(f"  V{n}: keys={has_keys}")
