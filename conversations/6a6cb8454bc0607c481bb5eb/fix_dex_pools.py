#!/usr/bin/env python3
"""Fix DEX pool seeding using WebSocket + verify session validators."""
from substrateinterface import SubstrateInterface, Keypair

# Use WebSocket for submit_extrinsic with wait_for_inclusion
substrate = SubstrateInterface(
    url="ws://127.0.0.1:9944",
    ss58_format=909,
    auto_discover=True,
    type_registry_preset=None,
)

print("=== SESSION VALIDATORS CHECK ===")
try:
    validators = substrate.query("Session", "Validators", [])
    print(f"Session validators: {len(validators.value)}")
    for v in validators.value:
        print(f"  {v}")
except Exception as e:
    print(f"Error: {e}")

print("\n=== DPOS ACTIVE VALIDATORS ===")
try:
    response = substrate.rpc_request("dpos_activeValidators", [])
    vals = response.get("result", [])
    print(f"DPoS active validators: {len(vals)}")
    for v in vals:
        print(f"  {v}")
except Exception as e:
    print(f"Error: {e}")

print("\n=== RE-SEEDING DEX POOLS ===")
alice_kp = Keypair.create_from_uri("//Alice")

# Check Alice balance
try:
    account = substrate.query("System", "Account", [alice_kp.ss58_address])
    balance = account.value.get("data", {}).get("free", 0)
    print(f"Alice balance: {balance / 10**9:,.4f} VRDX")
except Exception as e:
    print(f"Balance error: {e}")

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

print("\n=== FINAL VERIFICATION ===")
try:
    response = substrate.rpc_request("amm_getAllPools", [])
    pools = response.get("result", [])
    print(f"DEX pools: {len(pools)}")
except Exception as e:
    print(f"DEX pools error: {e}")

try:
    response = substrate.rpc_request("session_validators", [])
    vals = response.get("result", [])
    print(f"Session validators: {len(vals)}")
except Exception as e:
    print(f"Session validators error: {e}")

try:
    response = substrate.rpc_request("dpos_activeValidators", [])
    vals = response.get("result", [])
    print(f"DPoS active validators: {len(vals)}")
except Exception as e:
    print(f"DPoS active validators error: {e}")

# Block height
try:
    response = substrate.rpc_request("chain_getHeader", [])
    block = int(response.get("result", {}).get("number", "0x0"), 16)
    print(f"Block: #{block}")
except:
    pass

print("\nDone!")
