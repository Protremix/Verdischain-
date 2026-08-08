#!/usr/bin/env python3
"""Set session keys for V22-V30 with proper ownership proof."""

import hashlib
import time
from substrateinterface import SubstrateInterface, Keypair
from scalecodec.base import ScaleBytes

substrate = SubstrateInterface(url="http://127.0.0.1:9933", ss58_format=909, auto_discover=True)

def set_keys_with_proof(n):
    """Set session keys for validator V{n} with a valid ownership proof."""
    # Validator's main keypair (sr25519) - this is the "owner"
    kp = Keypair.create_from_uri(f"//Validator{n}")
    addr = kp.ss58_address
    owner_bytes = bytes(kp.public_key)  # 32-byte AccountId
    
    # Babe key (sr25519) - same as the validator keypair
    babe_pub = bytes(kp.public_key)
    
    # Grandpa key (ed25519) - derived from //Grandpa{n}
    seed = hashlib.sha256(f"//Grandpa{n}".encode()).digest()
    gp_kp = Keypair.create_from_seed(seed, crypto_type=0, ss58_format=909)  # ed25519
    grandpa_pub = bytes(gp_kp.public_key)
    
    # Check if already set
    nk = substrate.query("Session", "NextKeys", [addr])
    if nk and nk.value:
        print(f"V{n}: Already has keys")
        return True
    
    # Create ownership proof:
    # The proof is a SCALE-encoded tuple of (babe_signature, grandpa_signature)
    # Each signature is a signature of the owner_bytes (32-byte account ID)
    
    # Sign owner_bytes with babe key (sr25519)
    babe_sig = kp.sign(owner_bytes)
    
    # Sign owner_bytes with grandpa key (ed25519)
    grandpa_sig = gp_kp.sign(owner_bytes)
    
    # SCALE encode the proof as a tuple: (babe_sig, grandpa_sig)
    # For fixed-size byte arrays, SCALE encoding is just concatenation
    proof = babe_sig + grandpa_sig  # 64 + 64 = 128 bytes
    
    print(f"V{n}: owner={owner_bytes.hex()[:16]}... babe_sig={babe_sig.hex()[:16]}... proof_len={len(proof)}")
    
    try:
        call = substrate.compose_call("Session", "set_keys", {
            "keys": {"babe": babe_pub, "grandpa": grandpa_pub},
            "proof": proof
        })
        ext = substrate.create_signed_extrinsic(call=call, keypair=kp)
        ext_hex = "0x" + ext.data.hex() if hasattr(ext.data, "hex") else str(ext.data)
        result = substrate.rpc_request("author_submitExtrinsic", [ext_hex])
        
        if "result" in result:
            print(f"V{n}: Submitted OK (hash: {result['result'][:20]}...)")
            return True
        elif "error" in result:
            print(f"V{n}: Error - {result['error']}")
            return False
    except Exception as e:
        print(f"V{n}: Exception - {e}")
        return False

# Set keys for all 9 validators
success = 0
for n in range(22, 31):
    if set_keys_with_proof(n):
        success += 1
    time.sleep(3)

print(f"\n{success}/9 submitted. Waiting 30s for blocks...")
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
