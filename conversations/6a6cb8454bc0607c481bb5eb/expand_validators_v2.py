#!/usr/bin/env python3
"""Generate new validators with session keys to reach 15 active validators."""

import json
import time
import sys
from substrateinterface import SubstrateInterface, Keypair

substrate = SubstrateInterface(
    url="http://127.0.0.1:9933",
    ss58_format=909,
    auto_discover=True,
    type_registry_preset=None
)

DECIMALS = 9
FUND_AMOUNT = 20_000 * 10**DECIMALS  # 20k VRDX each
CHARLIE = Keypair.create_from_uri("//Charlie")

# Get current validators
current = substrate.query("Dpos", "ValidatorList", [])
print(f"Current total validators: {len(current.value) if current else 0}")

active = substrate.query("Dpos", "ActiveValidators", [])
print(f"Current active validators: {len(active.value) if active else 0}")

# We need 9 more validators with session keys (6 existing active + 9 new = 15)
NEW_COUNT = 9

print(f"\nGenerating {NEW_COUNT} new validators with session keys...\n")

new_validators = []
for i in range(NEW_COUNT):
    uri = f"//Validator{i+22}"  # Start from V22 to avoid conflicts
    kp = Keypair.create_from_uri(uri)
    # Also generate an ed25519 keypair for grandpa
    gp_uri = f"//Grandpa{i+22}"
    gp_kp = Keypair.create_from_uri(gp_uri, crypto_type=Keypair.ED25519)
    
    address = kp.ss58_address
    babe_key = "0x" + kp.public_key.hex()
    grandpa_key = "0x" + gp_kp.public_key.hex()
    
    print(f"  V{i+22}: {address}")
    print(f"    babe: {babe_key}")
    print(f"    grandpa: {grandpa_key}")
    
    new_validators.append({
        "uri": uri,
        "keypair": kp,
        "address": address,
        "babe_key_hex": babe_key,
        "grandpa_key_hex": grandpa_key,
        "gp_keypair": gp_kp
    })

# Step 1: Fund each new validator from Charlie
print("\n=== Step 1: Funding validators ===")
for i, v in enumerate(new_validators):
    try:
        acct = substrate.query("System", "Account", [v["address"]])
        free = int(acct.value.get("data", {}).get("free", 0)) if acct else 0
        if free > FUND_AMOUNT:
            print(f"  V{i+22}: Already funded ({free / 10**DECIMALS:.0f} VRDX)")
            continue
        
        call = substrate.compose_call(
            call_module="Balances",
            call_function="transfer_allow_death",
            call_params={
                "dest": {"AccountId32": v["address"]},
                "value": FUND_AMOUNT
            }
        )
        extrinsic = substrate.create_signed_extrinsic(call=call, keypair=CHARLIE)
        result = substrate.submit_extrinsic(extrinsic, wait_for_inclusion=True, wait_for_finalization=False)
        print(f"  V{i+22}: Funded {FUND_AMOUNT / 10**DECIMALS:.0f} VRDX")
    except Exception as e:
        print(f"  V{i+22}: Fund error - {e}")

print("\nWaiting 15s for transfers to settle...")
time.sleep(15)

# Step 2: Register each as validator
print("\n=== Step 2: Registering validators ===")
for i, v in enumerate(new_validators):
    try:
        is_val = substrate.query("Dpos", "Validators", [v["address"]])
        if is_val and is_val.value:
            print(f"  V{i+22}: Already registered")
            continue
        
        call = substrate.compose_call(
            call_module="Dpos",
            call_function="register_validator",
            call_params={
                "green_score": 3,
                "energy_source": b"solar"
            }
        )
        extrinsic = substrate.create_signed_extrinsic(call=call, keypair=v["keypair"])
        result = substrate.submit_extrinsic(extrinsic, wait_for_inclusion=True, wait_for_finalization=False)
        print(f"  V{i+22}: Registered")
    except Exception as e:
        print(f"  V{i+22}: Register error - {e}")

print("\nWaiting 15s for registrations to settle...")
time.sleep(15)

# Step 3: Set session keys for each new validator
print("\n=== Step 3: Setting session keys ===")
for i, v in enumerate(new_validators):
    try:
        # Session keys format: {babe: <sr25519 pub key bytes>, grandpa: <ed25519 pub key bytes>}
        babe_bytes = bytes.fromhex(v["babe_key_hex"][2:])
        grandpa_bytes = bytes.fromhex(v["grandpa_key_hex"][2:])
        
        call = substrate.compose_call(
            call_module="Session",
            call_function="set_keys",
            call_params={
                "keys": {
                    "babe": babe_bytes,
                    "grandpa": grandpa_bytes
                },
                "proof": b""
            }
        )
        extrinsic = substrate.create_signed_extrinsic(call=call, keypair=v["keypair"])
        result = substrate.submit_extrinsic(extrinsic, wait_for_inclusion=True, wait_for_finalization=False)
        print(f"  V{i+22}: Session keys set")
    except Exception as e:
        print(f"  V{i+22}: Set keys error - {e}")

print("\nWaiting 20s for session keys to propagate...")
time.sleep(20)

# Step 4: Verify
print("\n=== Step 4: Verification ===")
total = substrate.query("Dpos", "ValidatorList", [])
active = substrate.query("Dpos", "ActiveValidators", [])
print(f"Total validators: {len(total.value) if total else 0}")
print(f"Active validators: {len(active.value) if active else 0}")

for i, v in enumerate(new_validators):
    acct = substrate.query("System", "Account", [v["address"]])
    free = int(acct.value.get("data", {}).get("free", 0)) if acct else 0
    reserved = int(acct.value.get("data", {}).get("reserved", 0)) if acct else 0
    is_val = substrate.query("Dpos", "Validators", [v["address"]])
    registered = "REGISTERED" if is_val and is_val.value else "NOT REGISTERED"
    print(f"  V{i+22}: {free / 10**DECIMALS:.0f} free, {reserved / 10**DECIMALS:.0f} reserved [{registered}]")

print("\nDone! Session will rotate at next epoch boundary.")
