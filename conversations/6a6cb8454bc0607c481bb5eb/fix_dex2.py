#!/usr/bin/env python3
"""Fix DEX pool seeding — use correct Vec<u8> format."""
from substrateinterface import SubstrateInterface, Keypair

substrate = SubstrateInterface(
    url="ws://127.0.0.1:9944",
    ss58_format=909,
    auto_discover=True,
    type_registry_preset=None,
)

alice_kp = Keypair.create_from_uri("//Alice")

# Check Alice balance
try:
    account = substrate.query("System", "Account", [alice_kp.ss58_address])
    balance = account.value.get("data", {}).get("free", 0)
    print(f"Alice balance: {balance / 10**9:,.4f} VRDX")
except Exception as e:
    print(f"Balance error: {e}")

# Get metadata to check AmmDex create_pool params
print("\n=== AmmDex create_pool params ===")
try:
    metadata = substrate.metadata
    # Find AmmDex pallet
    for pallet in metadata.get("metadata", {}).get("pallets", []):
        if pallet.get("name") == "AmmDex":
            for call in pallet.get("calls", []):
                if call.get("name") == "create_pool":
                    print(f"create_pool args: {call.get('args')}")
                    break
            break
except Exception as e:
    # Try with decoded metadata
    print(f"Metadata decode error: {e}")
    # Just try different formats
    pass

# Try with hex-encoded tokens
pools = [
    ("VRDX", "ECO", 500_000_000_000_000, 500_000_000_000_000),
    ("VRDX", "CARBON", 300_000_000_000_000, 300_000_000_000_000),
    ("VRDX", "TREE", 200_000_000_000_000, 200_000_000_000_000),
    ("VRDX", "GREEN", 200_000_000_000_000, 200_000_000_000_000),
    ("ECO", "CARBON", 100_000_000_000_000, 100_000_000_000_000),
    ("VRDX", "REDD", 100_000_000_000_000, 100_000_000_000_000),
]

for token_a, token_b, amount_a, amount_b in pools:
    try:
        # Try with hex-encoded bytes
        token_a_hex = "0x" + token_a.encode().hex()
        token_b_hex = "0x" + token_b.encode().hex()
        
        call = substrate.compose_call(
            call_module="AmmDex",
            call_function="create_pool",
            call_params={
                "token_a": token_a_hex,
                "token_b": token_b_hex,
                "amount_a": amount_a,
                "amount_b": amount_b,
            }
        )
        extrinsic = substrate.create_signed_extrinsic(call=call, keypair=alice_kp)
        result = substrate.submit_extrinsic(extrinsic, wait_for_inclusion=True)
        if result.is_success:
            print(f"  ✅ Pool {token_a}/{token_b} created")
        else:
            print(f"  ❌ Pool {token_a}/{token_b}: {result.error_message}")
    except Exception as e:
        print(f"  ❌ Pool {token_a}/{token_b}: {e}")

# Verify pools
print("\n=== VERIFY ===")
try:
    # Try different RPC methods
    for method in ["amm_getAllPools", "amm_getPoolCount", "amm_allPools"]:
        try:
            response = substrate.rpc_request(method, [])
            r = response.get("result")
            if r is not None:
                if isinstance(r, list):
                    print(f"{method}: {len(r)} pools")
                else:
                    print(f"{method}: {r}")
                break
        except:
            continue
except:
    pass

# Check NextPoolId storage
try:
    for storage in ["NextPoolId", "PoolCount", "Pools"]:
        try:
            result = substrate.query("AmmDex", storage, [])
            print(f"AmmDex.{storage}: {result.value}")
            break
        except:
            continue
except:
    pass

print("\nDone!")
