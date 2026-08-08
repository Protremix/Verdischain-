#!/usr/bin/env python3
"""Register session keys for all validators"""

import json
import sys
import traceback
import hashlib

from substrateinterface import SubstrateInterface, Keypair

# Connect using WebSocket for wait_for_inclusion support
substrate = SubstrateInterface(
    url="ws://127.0.0.1:9944",
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

# Try to find Alice grandpa key using blake2b derivation
alice_grandpa = None
try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives import serialization
    
    seed = hashlib.blake2b(b"//Alice", digest_size=32).digest()
    sk = Ed25519PrivateKey.from_private_bytes(seed)
    pk = sk.public_key()
    raw = pk.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    alice_grandpa = "0x" + raw.hex()
    print(f"Alice grandpa key (blake2b): {alice_grandpa}")
except Exception as e:
    print(f"Could not derive Alice grandpa key: {e}")

if alice_grandpa:
    validators["Alice"] = {
        "babe": "0xd43593c715fdd31c61141abd04a99fd6822c8558854ccde39a5684e7a56da27d",
        "grandpa": alice_grandpa,
    }

# Submit session.set_keys() for each validator
print("\n=== Submitting session.set_keys() ===")
for name, info in validators.items():
    kp = Keypair.create_from_uri("//" + name)
    
    print(f"\n{name}:")
    print(f"  babe:    {info['babe']}")
    print(f"  grandpa: {info['grandpa']}")
    print(f"  signer:  {kp.ss58_address}")
    
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
        result = substrate.submit_extrinsic(extrinsic, wait_for_inclusion=True, wait_for_finalization=False)
        print(f"  SUCCESS: {result.extrinsic_hash}")
        print(f"  Block: {result.block_hash}")
    except Exception as e:
        print(f"  ERROR: {e}")
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

# Check each validator keys
for name in validators:
    kp = Keypair.create_from_uri("//" + name)
    addr = kp.ss58_address
    try:
        result = substrate.query("Session", "NextKeys", [addr])
        if result and result.value:
            print(f"{name}: keys registered")
        else:
            print(f"{name}: no keys registered")
    except Exception as e:
        print(f"{name}: error checking keys - {e}")
