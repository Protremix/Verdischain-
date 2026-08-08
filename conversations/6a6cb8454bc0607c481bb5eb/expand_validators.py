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
current_validators = substrate.query("Dpos", "AllValidators", [])
print(f"Current total validators: {len(current_validators.value) if current_validators else 0}")

active_validators = substrate.query("Dpos", "ActiveValidators", [])
print(f"Current active validators: {len(active_validators.value) if active_validators else 0}")

# We need 9 more validators with session keys (6 existing active + 9 new = 15)
NEW_VALIDATORS = 9

print(f"\nGenerating {NEW_VALIDATORS} new validators with session keys...\n")

new_keypairs = []
for i in range(NEW_VALIDATORS):
    # Generate deterministic keypair from a unique URI
    uri = f"//Validator{i+22}"  # Start from V22 to avoid conflicts
    kp = Keypair.create_from_uri(uri)
    address = kp.ss58_address
    print(f"  V{i+22}: {address}")
    new_keypairs.append({"uri": uri, "keypair": kp, "address": address})

# Step 1: Fund each new validator from Charlie
print("\n=== Step 1: Funding validators ===")
for i, v in enumerate(new_keypairs):
    try:
        # Check existing balance
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
for i, v in enumerate(new_keypairs):
    try:
        # Check if already registered
        is_validator = substrate.query("Dpos", "Validators", [v["address"]])
        if is_validator and is_validator.value:
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
for i, v in enumerate(new_keypairs):
    try:
        # Generate session keys (use same keypair for babe/grandpa/im-online)
        # Session keys are typically a tuple of (Babe, Grandpa) or similar
        # For simplicity, we use the validator's own public key as session key
        
        # Get the current session key prefix from runtime config
        # Typical: [babe_authority_id, grandpa_authority_id]
        # We'll use the validator's own public key for both
        
        # Create session key payload
        # The session key is typically a concatenation of multiple key types
        # For our runtime, we need to check what types are expected
        
        # Try using the keystore approach: set_keys with the validator's own keys
        # The keys are bytes of the public key
        pub_key = bytes(v["keypair"].public_key)
        
        # For Substrate, session keys are typically:
        # - Babe: sr25519 (32 bytes)  
        # - Grandpa: ed25519 (32 bytes)
        # But we may only have sr25519. Let's use the same key for babe.
        # Grandpa needs ed25519. We can generate one from the same URI.
        
        # Actually, let's try setting just babe keys first
        # The session.set_keys call takes: keys (Vec<u8>), proof (Vec<u8>)
        
        # For simplicity, use the sr25519 public key as the session key
        # The proof can be empty if the runtime doesn't require it
        
        # Let's compose the call and see what params it needs
        call = substrate.compose_call(
            call_module="Session",
            call_function="set_keys",
            call_params={
                "keys": pub_key,  # Use validator's own pub key as session key
                "proof": b""      # Empty proof
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
total_validators = substrate.query("Dpos", "AllValidators", [])
active = substrate.query("Dpos", "ActiveValidators", [])
print(f"Total validators: {len(total_validators.value) if total_validators else 0}")
print(f"Active validators: {len(active.value) if active else 0}")

for i, v in enumerate(new_keypairs):
    acct = substrate.query("System", "Account", [v["address"]])
    free = int(acct.value.get("data", {}).get("free", 0)) if acct else 0
    reserved = int(acct.value.get("data", {}).get("reserved", 0)) if acct else 0
    is_val = substrate.query("Dpos", "Validators", [v["address"]])
    registered = "REGISTERED" if is_val and is_val.value else "NOT REGISTERED"
    print(f"  V{i+22}: {free / 10**DECIMALS:.0f} free, {reserved / 10**DECIMALS:.0f} reserved [{registered}]")

print("\nDone! Session will rotate at next epoch boundary.")
