#!/usr/bin/env python3
"""Register session keys using HTTP (no wait_for_inclusion)"""

import json
import sys
import traceback
import hashlib
import time

from substrateinterface import SubstrateInterface, Keypair

# Connect using HTTP
substrate = SubstrateInterface(
    url="http://127.0.0.1:9933",
    ss58_format=909,
    auto_discover=True,
    type_registry_preset=None
)

# Key mapping from keystore
validators = {
    "Bob": {
        "babe": "0x8eaf04151687736326c9fea17e25fc5287613693c912909cb226aa4794f26a48",
        "grandpa": "0xd17c2d7823ebf260fd138f2d7e27d114c0145d968b5ff5006125f2414fadae69",
    },
    "Charlie": {
        "babe": "0x90b5ab205c6974c9ea841be688864633dc9ca8a357843eeacf2314649965fe22",
        "grandpa": "0x439660b36c6c03afafca027b910b4fecf99801834c62a5e6006f27d978de234f",
    },
    "Dave": {
        "babe": "0x306721211d5404bd9da88e0204360a1a9ab8b87c66c1bc2fcdd37f3c2222cc20",
        "grandpa": "0x5e639b43e0052c47447dac87d6fd2b6ec50bdd4d0f614e4299c665249bbd09d9",
    },
    "Eve": {
        "babe": "0xe659a7a1628cdd93febc04a4e0646ea20e9f5f0ce097d9a05290d4a9e054df4e",
        "grandpa": "0x1dfe3e22cc0d45c70779c1095f7489a8ef3cf52d62fbd8c2fa38c9f1723502b5",
    },
    "Ferdie": {
        "babe": "0x1cbd2d43530a44705ad088af313e18f80b53ef16b36177cd4b77b846f2a5f07c",
        "grandpa": "0x568cb4a574c6d178feb39c27dfc8b3f789e5f5423e19c71633c748b9acf086b5",
    },
}

# For Alice, try blake2b derivation
try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives import serialization
    seed = hashlib.blake2b(b"//Alice", digest_size=32).digest()
    sk = Ed25519PrivateKey.from_private_bytes(seed)
    pk = sk.public_key()
    raw = pk.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    validators["Alice"] = {
        "babe": "0xd43593c715fdd31c61141abd04a99fd6822c8558854ccde39a5684e7a56da27d",
        "grandpa": "0x" + raw.hex(),
    }
    print(f"Alice grandpa (blake2b): {validators['Alice']['grandpa']}")
except Exception as e:
    print(f"Could not derive Alice key: {e}")

# Submit using author_submitExtrinsic (no watch)
print("\n=== Submitting session.set_keys() (HTTP, no wait) ===")
for name, info in validators.items():
    kp = Keypair.create_from_uri("//" + name)
    
    print(f"\n{name}: signer={kp.ss58_address}")
    
    try:
        call = substrate.compose_call(
            "Session",
            "set_keys",
            {
                "keys": {
                    "babe": info["babe"],
                    "grandpa": info["grandpa"],
                },
                "proof": "0x",
            }
        )
        extrinsic = substrate.create_signed_extrinsic(call, kp)
        # Use author_submitExtrinsic (no wait)
        result = substrate.submit_extrinsic(extrinsic, wait_for_inclusion=False, wait_for_finalization=False)
        print(f"  Submitted: {result.extrinsic_hash}")
        time.sleep(3)  # Wait for inclusion
    except Exception as e:
        print(f"  ERROR: {e}")

# Wait a bit for block inclusion
print("\nWaiting 6s for block inclusion...")
time.sleep(6)

# Verify
print("\n=== Verification ===")
try:
    result = substrate.query("Session", "Validators")
    vals = result.value
    print(f"Session validators: {len(vals)}")
    for v in vals:
        print(f"  {v}")
except Exception as e:
    print(f"Error: {e}")

# Check next keys
for name in validators:
    kp = Keypair.create_from_uri("//" + name)
    try:
        result = substrate.query("Session", "NextKeys", [kp.ss58_address])
        if result and result.value:
            val = result.value
            babe_val = val.get("babe", "?") if isinstance(val, dict) else str(val)[:40]
            print(f"{name}: keys OK (babe={str(babe_val)[:20]}...)")
        else:
            print(f"{name}: no keys")
    except Exception as e:
        print(f"{name}: error - {e}")
