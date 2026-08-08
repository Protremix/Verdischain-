#!/usr/bin/env python3
"""Set session keys for V22-V30 validators."""

import time
import hashlib
from substrateinterface import SubstrateInterface, Keypair

substrate = SubstrateInterface(url="http://127.0.0.1:9933", ss58_format=909, auto_discover=True)

success = 0
for n in range(22, 31):
    uri = f"//Validator{n}"
    kp = Keypair.create_from_uri(uri)
    addr = kp.ss58_address
    babe_key = bytes(kp.public_key)
    seed = hashlib.sha256(f"//Grandpa{n}".encode()).digest()
    gp_kp = Keypair.create_from_seed(seed, crypto_type=0, ss58_format=909)
    grandpa_key = bytes(gp_kp.public_key)
    
    # Check if keys already set
    nk = substrate.query("Session", "NextKeys", [addr])
    if nk and nk.value:
        print(f"V{n}: Keys already set")
        success += 1
        continue
    
    try:
        call = substrate.compose_call("Session", "set_keys", {
            "keys": {"babe": babe_key, "grandpa": grandpa_key},
            "proof": b""
        })
        ext = substrate.create_signed_extrinsic(call=call, keypair=kp)
        substrate.submit_extrinsic(ext, wait_for_inclusion=False, wait_for_finalization=False)
        print(f"V{n}: Submitted set_keys")
        time.sleep(10)  # Wait for block
        # Verify
        nk = substrate.query("Session", "NextKeys", [addr])
        if nk and nk.value:
            print(f"V{n}: Keys confirmed SET")
            success += 1
        else:
            print(f"V{n}: Keys NOT confirmed yet")
    except Exception as e:
        print(f"V{n}: Error - {e}")
        time.sleep(5)

print(f"\n{success}/9 validators have session keys")
total = substrate.query("Dpos", "ValidatorList", [])
nk_count = 0
for addr in total.value:
    nk = substrate.query("Session", "NextKeys", [addr])
    if nk and nk.value:
        nk_count += 1
print(f"Total validators: {len(total.value)}, with keys: {nk_count}")
