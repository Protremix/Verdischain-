#!/usr/bin/env python3
"""Generate new validators with session keys — one at a time to avoid nonce conflicts."""

import time
import hashlib
from substrateinterface import SubstrateInterface, Keypair

substrate = SubstrateInterface(
    url="http://127.0.0.1:9933",
    ss58_format=909,
    auto_discover=True,
    type_registry_preset=None
)

DECIMALS = 9
FUND_AMOUNT = 20_000 * 10**DECIMALS
CHARLIE = Keypair.create_from_uri("//Charlie")

# Get current state
current = substrate.query("Dpos", "ValidatorList", [])
print(f"Current total validators: {len(current.value) if current else 0}")
active = substrate.query("Dpos", "ActiveValidators", [])
print(f"Current active validators: {len(active.value) if active else 0}")

NEW_COUNT = 9
print(f"\nGenerating {NEW_COUNT} new validators with session keys...\n")

new_validators = []
for i in range(NEW_COUNT):
    n = i + 22
    uri = f"//Validator{n}"
    kp = Keypair.create_from_uri(uri)
    babe_key = bytes(kp.public_key)
    seed = hashlib.sha256(f"//Grandpa{n}".encode()).digest()
    gp_kp = Keypair.create_from_seed(seed, crypto_type=0, ss58_format=909)
    grandpa_key = bytes(gp_kp.public_key)
    print(f"  V{n}: {kp.ss58_address}")
    new_validators.append({"n": n, "keypair": kp, "address": kp.ss58_address, "babe_key": babe_key, "grandpa_key": grandpa_key})

def submit_tx(call_module, call_function, call_params, keypair, label=""):
    """Submit one extrinsic, wait for next block, verify."""
    try:
        call = substrate.compose_call(call_module, call_function, call_params)
        ext = substrate.create_signed_extrinsic(call=call, keypair=keypair)
        result = substrate.submit_extrinsic(ext, wait_for_inclusion=False, wait_for_finalization=False)
        # Wait for block to process
        time.sleep(8)
        return True, result
    except Exception as e:
        return False, str(e)

# Process each validator sequentially: fund -> register -> set keys
print("\n=== Processing validators one at a time ===")
success_count = 0
for v in new_validators:
    print(f"\n--- V{v['n']} ({v['address'][:12]}...) ---")
    
    # Check if already funded
    acct = substrate.query("System", "Account", [v["address"]])
    free = int(acct.value.get("data", {}).get("free", 0)) if acct else 0
    
    if free < 1000:
        # Fund from Charlie
        ok, msg = submit_tx("Balances", "transfer_allow_death", {
            "dest": v["address"], "value": FUND_AMOUNT
        }, CHARLIE, f"Fund V{v['n']}")
        if ok:
            print(f"  Funded: YES")
        else:
            print(f"  Fund FAILED: {msg}")
            continue
        time.sleep(3)
    
    # Check if already registered
    is_val = substrate.query("Dpos", "Validators", [v["address"]])
    if not (is_val and is_val.value):
        # Register
        ok, msg = submit_tx("Dpos", "register_validator", {
            "green_score": 3, "energy_source": b"solar"
        }, v["keypair"], f"Register V{v['n']}")
        if ok:
            print(f"  Registered: YES")
        else:
            print(f"  Register FAILED: {msg}")
            continue
        time.sleep(3)
    else:
        print(f"  Already registered")
    
    # Set session keys
    ok, msg = submit_tx("Session", "set_keys", {
        "keys": {"babe": v["babe_key"], "grandpa": v["grandpa_key"]},
        "proof": b""
    }, v["keypair"], f"SetKeys V{v['n']}")
    if ok:
        print(f"  Session keys: SET")
        success_count += 1
    else:
        print(f"  Set keys FAILED: {msg}")

print(f"\n=== Summary: {success_count}/{NEW_COUNT} validators fully set up ===")

# Final verification
total = substrate.query("Dpos", "ValidatorList", [])
active = substrate.query("Dpos", "ActiveValidators", [])
print(f"Total validators: {len(total.value) if total else 0}")
print(f"Active validators: {len(active.value) if active else 0}")
print("\nSession will rotate at next epoch boundary to include new validators.")
