#!/usr/bin/env python3
"""Register session keys for all validators using correct key mapping from keystore"""

import json
import sys
import traceback
import hashlib

from substrateinterface import SubstrateInterface, Keypair

# Connect
substrate = SubstrateInterface(
    url="http://127.0.0.1:9933",
    ss58_format=909,
    auto_discover=True,
    type_registry_preset=None
)

# Correct key mapping from keystore files
# babe keys = sr25519 public keys = same as account public keys
# grandpa keys = ed25519 public keys from keystore

validators = {
    "Alice": {
        "address": "5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY",
        "babe": "d43593c715fdd31c61141abd04a99fd6822c8558854ccde39a5684e7a56da27d",
        "grandpa": None,  # Need to find
    },
    "Bob": {
        "address": "5FHneW46xGXgs5mUiveU4sbTyGBzmstUspZC92UhjJM694ty",
        "babe": "8eaf04151687736326c9fea17e25fc5287613693c912909cb226aa4794f26a48",
        "grandpa": "d17c2d7823ebf260fd138f2d7e27d114c0145d968b5ff5006125f2414fadae69",
    },
    "Charlie": {
        "address": "5FLSigC9HGRKVhB9FiEo4Y3koPsNmBmLJbpXg2mp1hXcS59Y",
        "babe": "90b5ab205c6974c9ea841be688864633dc9ca8a357843eeacf2314649965fe22",
        "grandpa": "439660b36c6c03afafca027b910b4fecf99801834c62a5e6006f27d978de234f",
    },
    "Dave": {
        "address": "5DAAnrj7VHTznn2AWBemMuyBwZWs6FNFjdyVXUeYum3PTXFy",
        "babe": "306721211d5404bd9da88e0204360a1a9ab8b87c66c1bc2fcdd37f3c2222cc20",
        "grandpa": "5e639b43e0052c47447dac87d6fd2b6ec50bdd4d0f614e4299c665249bbd09d9",
    },
    "Eve": {
        "address": "5HGjWAeFDfFCWPsjFQdVV2Msvz2XtMktvgocEZcCj68kUMaw",
        "babe": "e659a7a1628cdd93febc04a4e0646ea20e9f5f0ce097d9a05290d4a9e054df4e",
        "grandpa": "1dfe3e22cc0d45c70779c1095f7489a8ef3cf52d62fbd8c2fa38c9f1723502b5",
    },
    "Ferdie": {
        "address": "5CiPPseXPECbkjWCa6MnjNokrgYjMqmKndv2rSnekmSK2DjL",
        "babe": "1cbd2d43530a44705ad088af313e18f80b53ef16b36177cd4b77b846f2a5f07c",
        "grandpa": "568cb4a574c6d178feb39c27dfc8b3f789e5f5423e19c71633c748b9acf086b5",
    },
}

# Try to find Alice's grandpa key using different derivation methods
print("=== Looking for Alice grandpa key ===")
alice_grandpa_candidates = []

# Method 1: blake2b-256
try:
    h = hashlib.blake2b(b"//Alice", digest_size=32).digest()
    alice_grandpa_candidates.append(("blake2b-256", h.hex()))
except Exception as e:
    print(f"blake2b-256 error: {e}")

# Method 2: blake2b-512 first 32 bytes
try:
    h = hashlib.blake2b(b"//Alice", digest_size=64).digest()
    alice_grandpa_candidates.append(("blake2b-512[:32]", h[:32].hex()))
except Exception as e:
    print(f"blake2b-512 error: {e}")

# Method 3: Try using cryptography library with different seed derivations
try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives import serialization
    
    # Method 3a: blake2b-256 seed
    seed = hashlib.blake2b(b"//Alice", digest_size=32).digest()
    sk = Ed25519PrivateKey.from_private_bytes(seed)
    pk = sk.public_key()
    raw = pk.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    alice_grandpa_candidates.append(("ed25519-blake2b", raw.hex()))
    
    # Method 3b: blake2b-512 first 32 bytes
    seed2 = hashlib.blake2b(b"//Alice", digest_size=64).digest()[:32]
    sk2 = Ed25519PrivateKey.from_private_bytes(seed2)
    pk2 = sk2.public_key()
    raw2 = pk2.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    alice_grandpa_candidates.append(("ed25519-blake2b512", raw2.hex()))
    
except ImportError:
    print("cryptography not available for ed25519 derivation")

# Method 4: Try using PyNaCl
try:
    import nacl.signing
    import nacl.encoding
    
    seed = hashlib.blake2b(b"//Alice", digest_size=32).digest()
    sk = nacl.signing.SigningKey(seed)
    pk = sk.verify_key.encode(encoder=nacl.encoding.RawEncoder)
    alice_grandpa_candidates.append(("nacl-blake2b", pk.hex()))
except ImportError:
    pass

# Check if any candidate matches the known pattern
# Alice grandpa key is NOT in keystore, but we can try to insert it
for name, key in alice_grandpa_candidates:
    print(f"  {name}: {key}")
    validators["Alice"]["grandpa"] = key

# Now submit session.set_keys() for each validator
print("\n=== Submitting session.set_keys() ===")
for name, info in validators.items():
    if info["grandpa"] is None:
        print(f"Skipping {name} - no grandpa key")
        continue
    
    kp = Keypair.create_from_uri("//" + name)
    babe_hex = "0x" + info["babe"]
    grandpa_hex = "0x" + info["grandpa"]
    
    print(f"\n{name}:")
    print(f"  babe:    {babe_hex}")
    print(f"  grandpa: {grandpa_hex}")
    print(f"  signer:  {kp.ss58_address}")
    
    try:
        call = substrate.compose_call(
            "Session",
            "set_keys",
            {
                "keys": {
                    "babe": babe_hex,
                    "grandpa": grandpa_hex,
                },
                "proof": "0x",
            }
        )
        extrinsic = substrate.create_signed_extrinsic(call, kp)
        result = substrate.submit_extrinsic(extrinsic, wait_for_inclusion=True, wait_for_finalization=False)
        print(f"  Result: {result.extrinsic_hash}")
    except Exception as e:
        print(f"  ERROR: {e}")
        # Try with different key format
        try:
            # Maybe keys need to be raw bytes
            call = substrate.compose_call(
                "Session",
                "set_keys",
                {
                    "keys": bytes.fromhex(info["babe"]) + bytes.fromhex(info["grandpa"]),
                    "proof": b"",
                }
            )
            extrinsic = substrate.create_signed_extrinsic(call, kp)
            result = substrate.submit_extrinsic(extrinsic, wait_for_inclusion=True, wait_for_finalization=False)
            print(f"  Result (raw): {result.extrinsic_hash}")
        except Exception as e2:
            print(f"  ERROR (raw): {e2}")
            traceback.print_exc()

# Verify
print("\n=== Verification ===")
try:
    result = substrate.query("Session", "Validators")
    validators_list = result.value
    print(f"Session validators: {len(validators_list)}")
    for v in validators_list:
        print(f"  {v}")
except Exception as e:
    print(f"Error: {e}")

# Check session keys
try:
    for name, info in validators.items():
        kp = Keypair.create_from_uri("//" + name)
        addr = kp.ss58_address
        result = substrate.query("Session", "NextKeys", [addr])
        print(f"{name} next keys: {result}")
except Exception as e:
    print(f"Error querying next keys: {e}")

# Try querying KeyOwner
try:
    for name, info in validators.items():
        kp = Keypair.create_from_uri("//" + name)
        addr = kp.ss58_address
        result = substrate.query("Session", "KeyOwner", [info["grandpa"]])
        print(f"{name} key owner: {result}")
except Exception as e:
    print(f"Error querying key owner: {e}")
