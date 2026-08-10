#!/usr/bin/env python3
"""Register 15 additional validators using Alice as funder."""
import time
from substrateinterface import SubstrateInterface, Keypair

sub = SubstrateInterface(
    url="http://127.0.0.1:9933",
    ss58_format=909,
    auto_discover=True,
    type_registry_preset=None
)

ALICE = Keypair.create_from_uri("//Alice")
FUND_AMOUNT = 101_000_000 * 1_000_000_000  # 101M VRDX (stake + fees)

alice_balance = sub.query("System", "Account", [ALICE.ss58_address])
print(f"Alice balance: {alice_balance.value['data']['free'] / 1e9:,.0f} VRDX")

# Check existing validators
existing = sub.query_map("Dpos", "Validators")
existing_addrs = set()
for addr, _ in existing:
    existing_addrs.add(str(addr.value))
print(f"Existing validators: {len(existing_addrs)}")

# Helper: submit and wait for inclusion by polling nonce
def submit_and_wait(call, signer, label=""):
    try:
        ext = sub.create_signed_extrinsic(call, signer)
        result = sub.submit_extrinsic(ext, wait_for_inclusion=False)
        print(f"    {label} submitted: {str(result)[:60]}")
        time.sleep(6)  # Wait for block inclusion
        return True
    except Exception as e:
        print(f"    {label} FAILED: {e}")
        return False

# Register 15 new validators
registered = 0
for i in range(1, 16):
    uri = f"//Val{i}"
    kp = Keypair.create_from_uri(uri)
    addr = kp.ss58_address

    if addr in existing_addrs:
        print(f"  {uri} ({addr}) already registered, skipping")
        continue

    # Step 1: Fund the validator from Alice
    print(f"  Funding {uri} ({addr}) with 101M VRDX...")
    call = sub.compose_call("Balances", "transfer_allow_death", {
        "dest": addr,
        "value": FUND_AMOUNT
    })
    if not submit_and_wait(call, ALICE, "Fund"):
        continue
    time.sleep(3)

    # Step 2: Register as validator
    print(f"  Registering {uri} as validator...")
    call2 = sub.compose_call("Dpos", "register_validator", {
        "green_score": 3,
        "energy_source": b"solar"
    })
    if submit_and_wait(call2, kp, "Register"):
        registered += 1
    time.sleep(3)

print(f"\nDone! Registered {registered} new validators.")

# Verify total
time.sleep(6)
existing2 = sub.query_map("Dpos", "Validators")
count = 0
for _ in existing2:
    count += 1
print(f"Total validators now: {count}")
