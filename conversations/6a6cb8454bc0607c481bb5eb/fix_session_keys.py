#!/usr/bin/env python3
"""Fix session keys for all validators by calling session.set_keys()"""

import json
import os
import sys
import traceback

from substrateinterface import SubstrateInterface, Keypair

# Connect
substrate = SubstrateInterface(
    url="http://127.0.0.1:9933",
    ss58_format=909,
    auto_discover=True,
    type_registry_preset=None
)

# Well-known dev accounts
accounts = ["Alice", "Bob", "Charlie", "Dave", "Eve", "Ferdie"]
account_keys = {}
for name in accounts:
    kp = Keypair.create_from_uri("//" + name)
    account_keys[name] = {
        "address": kp.ss58_address,
        "pubkey_hex": kp.public_key.hex(),
        "keypair": kp,
    }
    print(f"{name}: {kp.ss58_address} ({kp.public_key.hex()})")

# Read keystore
keystore_path = "/opt/verdis-node1-data-v5/chains/verdis/keystore"
babe_keys = []
grandpa_keys = []
for f in os.listdir(keystore_path):
    if f.startswith("62616265"):  # babe key type
        pubkey = f[8:]
        babe_keys.append(pubkey)
    elif f.startswith("6772616e"):  # grandpa key type
        pubkey = f[8:]
        grandpa_keys.append(pubkey)

print(f"\nBabe keys in keystore: {len(babe_keys)}")
for k in sorted(babe_keys):
    matched = False
    for name, info in account_keys.items():
        if k == info["pubkey_hex"]:
            print(f"  {k} -> {name}")
            matched = True
            break
    if not matched:
        print(f"  {k} -> unknown")

print(f"\nGrandpa keys in keystore: {len(grandpa_keys)}")
for k in sorted(grandpa_keys):
    print(f"  {k}")

# Try to generate ed25519 keys
ed25519_keys = {}
try:
    import hashlib
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives import serialization

    for name in accounts:
        seed = hashlib.sha256(("//" + name).encode()).digest()
        private_key = Ed25519PrivateKey.from_private_bytes(seed)
        public_key = private_key.public_key()
        raw_bytes = public_key.public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw
        )
        ed25519_keys[name] = raw_bytes.hex()
        in_keystore = raw_bytes.hex() in grandpa_keys
        print(f"\n{name} ed25519 grandpa key: {raw_bytes.hex()} (in keystore: {in_keystore})")
except ImportError:
    print("\ncryptography library not available, trying PyNaCl...")
    try:
        import nacl.signing
        import nacl.encoding
        import hashlib
        for name in accounts:
            seed = hashlib.sha256(("//" + name).encode()).digest()
            signing_key = nacl.signing.SigningKey(seed)
            verify_key = signing_key.verify_key
            raw_bytes = verify_key.encode(encoder=nacl.encoding.RawEncoder)
            ed25519_keys[name] = raw_bytes.hex()
            in_keystore = raw_bytes.hex() in grandpa_keys
            print(f"{name} ed25519 grandpa key: {raw_bytes.hex()} (in keystore: {in_keystore})")
    except ImportError:
        print("Neither cryptography nor PyNaCl available!")

# Build session key mapping
print("\n=== SESSION KEY MAPPING ===")
validator_session_keys = {}
for name in accounts:
    babe_pubkey = account_keys[name]["pubkey_hex"]
    # Check if babe key is in keystore
    babe_in_keystore = babe_pubkey in babe_keys

    # Find grandpa key
    grandpa_pubkey = None
    if name in ed25519_keys:
        ed_key = ed25519_keys[name]
        if ed_key in grandpa_keys:
            grandpa_pubkey = ed_key
            print(f"{name}: babe={babe_pubkey[:16]}... grandpa={grandpa_pubkey[:16]}... (both found)")

    if grandpa_pubkey is None:
        print(f"{name}: babe={babe_pubkey[:16]}... grandpa=NOT FOUND")

    validator_session_keys[name] = {
        "babe": babe_pubkey,
        "grandpa": grandpa_pubkey,
    }

# Try to compose and submit session.set_keys() for each validator
print("\n=== SUBMITTING SESSION.SET_KEYS ===")
for name in accounts:
    info = validator_session_keys[name]
    if info["grandpa"] is None:
        print(f"Skipping {name} - no grandpa key found")
        continue

    kp = account_keys[name]["keypair"]
    babe_hex = "0x" + info["babe"]
    grandpa_hex = "0x" + info["grandpa"]

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
        print(f"{name}: set_keys submitted - {result.extrinsic_hash}")
    except Exception as e:
        print(f"{name}: ERROR - {e}")
        traceback.print_exc()

# Verify
print("\n=== VERIFICATION ===")
try:
    result = substrate.query("Session", "Validators")
    validators = result.value
    print(f"Session validators: {len(validators)}")
    for v in validators:
        print(f"  {v}")
except Exception as e:
    print(f"Error querying validators: {e}")

try:
    result = substrate.query("Session", "NextKeys")
    print(f"Next keys: {result}")
except Exception as e:
    print(f"Error querying next keys: {e}")
