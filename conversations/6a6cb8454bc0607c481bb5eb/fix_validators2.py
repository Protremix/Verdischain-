#!/usr/bin/env python3
"""Submit session keys for Alice, Bob, Charlie validators + re-seed DEX pools."""
import sys
import json
from substrateinterface import SubstrateInterface, Keypair

substrate = SubstrateInterface(
    url="http://127.0.0.1:9933",
    ss58_format=909,
    auto_discover=True,
    type_registry_preset=None,
)

# Get session keys from each node
nodes = [
    ("Alice", 9933, "//Alice"),
    ("Bob", 9944, "//Bob"),
    ("Charlie", 9935, "//Charlie"),
]

for name, port, uri in nodes:
    print(f"\n=== {name} (port {port}) ===")
    try:
        node_sub = SubstrateInterface(
            url=f"http://127.0.0.1:{port}",
            ss58_format=909,
            auto_discover=True,
            type_registry_preset=None,
        )
        response = node_sub.rpc_request("author_rotateKeys", [])
        session_keys_hex = response.get("result", "")
        if not session_keys_hex:
            print(f"  ERROR: No session keys returned")
            continue
        print(f"  Session keys: {session_keys_hex[:40]}...")
    except Exception as e:
        print(f"  ERROR getting keys: {e}")
        continue
    
    keypair = Keypair.create_from_uri(uri)
    print(f"  Account: {keypair.ss58_address}")
    
    # Check balance
    try:
        account = substrate.query("System", "Account", [keypair.ss58_address])
        balance = account.value.get("data", {}).get("free", 0)
        print(f"  Balance: {balance / 10**9:,.4f} VRDX")
    except Exception as e:
        print(f"  Balance check error: {e}")
    
    # Submit session.setKeys
    try:
        # The keys from rotateKeys are a SCALE-encoded bytes object
        # session.set_keys(keys: Bytes, proof: Bytes)
        call = substrate.compose_call(
            call_module="Session",
            call_function="set_keys",
            call_params={
                "keys": session_keys_hex,
                "proof": "0x",
            }
        )
        extrinsic = substrate.create_signed_extrinsic(call=call, keypair=keypair)
        result = substrate.submit_extrinsic(extrinsic, wait_for_inclusion=True)
        if result.is_success:
            print(f"  ✅ Session keys set! Block: {result.block_hash}")
        else:
            print(f"  ❌ Failed: {result.error_message}")
    except Exception as e:
        print(f"  ERROR: {e}")

# Re-seed DEX pools
print("\n=== RE-SEEDING DEX POOLS ===")
alice_kp = Keypair.create_from_uri("//Alice")

pools = [
    (b"VRDX", b"ECO", 500_000_000_000_000, 500_000_000_000_000),
    (b"VRDX", b"CARBON", 300_000_000_000_000, 300_000_000_000_000),
    (b"VRDX", b"TREE", 200_000_000_000_000, 200_000_000_000_000),
    (b"VRDX", b"GREEN", 200_000_000_000_000, 200_000_000_000_000),
    (b"ECO", b"CARBON", 100_000_000_000_000, 100_000_000_000_000),
    (b"VRDX", b"REDD", 100_000_000_000_000, 100_000_000_000_000),
]

for token_a, token_b, amount_a, amount_b in pools:
    try:
        call = substrate.compose_call(
            call_module="AmmDex",
            call_function="create_pool",
            call_params={
                "token_a": token_a.decode(),
                "token_b": token_b.decode(),
                "amount_a": amount_a,
                "amount_b": amount_b,
            }
        )
        extrinsic = substrate.create_signed_extrinsic(call=call, keypair=alice_kp)
        result = substrate.submit_extrinsic(extrinsic, wait_for_inclusion=True)
        if result.is_success:
            print(f"  ✅ Pool {token_a.decode()}/{token_b.decode()} created")
        else:
            print(f"  ❌ Pool {token_a.decode()}/{token_b.decode()}: {result.error_message}")
    except Exception as e:
        print(f"  ❌ Pool {token_a.decode()}/{token_b.decode()}: {e}")

# Verify
print("\n=== VERIFICATION ===")
try:
    validators = substrate.query("Session", "Validators", [])
    print(f"Session validators: {len(validators.value)}")
except Exception as e:
    print(f"Session validators check error: {e}")

try:
    pools = substrate.query("AmmDex", "NextPoolId", [])
    print(f"DEX pools: {pools.value}")
except Exception as e:
    print(f"DEX pools check error: {e}")

print("\nDone!")
