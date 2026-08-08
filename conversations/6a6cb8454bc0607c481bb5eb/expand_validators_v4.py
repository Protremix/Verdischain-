#!/usr/bin/env python3
"""Generate new validators with session keys to reach 15 active validators."""

import time
import hashlib
from substrateinterface import SubstrateInterface, Keypair

# Use WebSocket for result handlers
substrate = SubstrateInterface(
    url="ws://127.0.0.1:9944",
    ss58_format=909,
    auto_discover=True,
    type_registry_preset=None
)

DECIMALS = 9
FUND_AMOUNT = 20_000 * 10**DECIMALS
CHARLIE = Keypair.create_from_uri("//Charlie")

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
    address = kp.ss58_address
    babe_key = bytes(kp.public_key)
    seed = hashlib.sha256(f"//Grandpa{n}".encode()).digest()
    gp_kp = Keypair.create_from_seed(seed, crypto_type=0, ss58_format=909)
    grandpa_key = bytes(gp_kp.public_key)
    print(f"  V{n}: {address}")
    new_validators.append({"n": n, "keypair": kp, "address": address, "babe_key": babe_key, "grandpa_key": grandpa_key})

# Step 1: Fund from Charlie
print("\n=== Step 1: Funding validators ===")
for v in new_validators:
    try:
        acct = substrate.query("System", "Account", [v["address"]])
        free = int(acct.value.get("data", {}).get("free", 0)) if acct else 0
        if free > FUND_AMOUNT:
            print(f"  V{v['n']}: Already funded ({free / 10**DECIMALS:.0f} VRDX)")
            continue
        call = substrate.compose_call("Balances", "transfer_allow_death", {
            "dest": v["address"],  # Use string address directly
            "value": FUND_AMOUNT
        })
        ext = substrate.create_signed_extrinsic(call=call, keypair=CHARLIE)
        substrate.submit_extrinsic(ext, wait_for_inclusion=True, wait_for_finalization=False)
        print(f"  V{v['n']}: Funded {FUND_AMOUNT / 10**DECIMALS:.0f} VRDX")
    except Exception as e:
        print(f"  V{v['n']}: Fund error - {e}")

print("\nWaiting 15s..."); time.sleep(15)

# Step 2: Register as validators
print("\n=== Step 2: Registering validators ===")
for v in new_validators:
    try:
        is_val = substrate.query("Dpos", "Validators", [v["address"]])
        if is_val and is_val.value:
            print(f"  V{v['n']}: Already registered")
            continue
        call = substrate.compose_call("Dpos", "register_validator", {
            "green_score": 3, "energy_source": b"solar"
        })
        ext = substrate.create_signed_extrinsic(call=call, keypair=v["keypair"])
        substrate.submit_extrinsic(ext, wait_for_inclusion=True, wait_for_finalization=False)
        print(f"  V{v['n']}: Registered")
    except Exception as e:
        print(f"  V{v['n']}: Register error - {e}")

print("\nWaiting 15s..."); time.sleep(15)

# Step 3: Set session keys
print("\n=== Step 3: Setting session keys ===")
for v in new_validators:
    try:
        call = substrate.compose_call("Session", "set_keys", {
            "keys": {"babe": v["babe_key"], "grandpa": v["grandpa_key"]},
            "proof": b""
        })
        ext = substrate.create_signed_extrinsic(call=call, keypair=v["keypair"])
        substrate.submit_extrinsic(ext, wait_for_inclusion=True, wait_for_finalization=False)
        print(f"  V{v['n']}: Session keys set")
    except Exception as e:
        print(f"  V{v['n']}: Set keys error - {e}")

print("\nWaiting 20s..."); time.sleep(20)

# Step 4: Verify
print("\n=== Verification ===")
total = substrate.query("Dpos", "ValidatorList", [])
active = substrate.query("Dpos", "ActiveValidators", [])
print(f"Total validators: {len(total.value) if total else 0}")
print(f"Active validators: {len(active.value) if active else 0}")
for v in new_validators:
    acct = substrate.query("System", "Account", [v["address"]])
    free = int(acct.value.get("data", {}).get("free", 0)) if acct else 0
    reserved = int(acct.value.get("data", {}).get("reserved", 0)) if acct else 0
    is_val = substrate.query("Dpos", "Validators", [v["address"]])
    status = "REGISTERED" if is_val and is_val.value else "NOT REGISTERED"
    nk = substrate.query("Session", "NextKeys", [v["address"]])
    has_keys = "KEYS SET" if nk and nk.value else "NO KEYS"
    print(f"  V{v['n']}: {free / 10**DECIMALS:.0f} free, {reserved / 10**DECIMALS:.0f} reserved [{status}] [{has_keys}]")
print("\nDone! Session rotates at next epoch boundary.")
