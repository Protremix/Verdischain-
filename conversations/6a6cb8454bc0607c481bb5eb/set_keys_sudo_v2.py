#!/usr/bin/env python3
"""Set session keys via Sudo + System::set_storage using substrateinterface."""

import hashlib
import time
from substrateinterface import SubstrateInterface, Keypair

s = SubstrateInterface(url="http://127.0.0.1:9933", ss58_format=909, auto_discover=True)
sudo_kp = Keypair.create_from_uri("//Alice")

success = 0
for n in range(22, 31):
    kp = Keypair.create_from_uri(f"//Validator{n}")
    addr = kp.ss58_address
    babe_pub = bytes(kp.public_key)
    
    nk = s.query("Session", "NextKeys", [addr])
    if nk and nk.value:
        print(f"V{n}: Already has keys")
        success += 1
        continue
    
    seed = hashlib.sha256(f"//Grandpa{n}".encode()).digest()
    gp_kp = Keypair.create_from_seed(seed, crypto_type=1, ss58_format=909)
    grandpa_pub = bytes(gp_kp.public_key)
    
    storage_key = s.create_storage_key("Session", "NextKeys", [addr])
    key_hex = storage_key.to_hex()
    value_hex = "0x" + (babe_pub + grandpa_pub).hex()
    
    try:
        call = s.compose_call(
            call_module="Sudo",
            call_function="sudo",
            call_params={
                "call": {
                    "call_module": "System",
                    "call_function": "set_storage",
                    "call_params": {
                        "items": [[key_hex, value_hex]]
                    }
                }
            }
        )
        
        ext = s.create_signed_extrinsic(call=call, keypair=sudo_kp)
        ext_hex = ext.data.to_hex() if hasattr(ext.data, 'to_hex') else "0x" + ext.data.hex()
        
        result = s.rpc_request("author_submitExtrinsic", [ext_hex])
        
        if "result" in result:
            print(f"V{n}: OK (hash: {result['result'][:20]}...)")
            success += 1
        elif "error" in result:
            print(f"V{n}: RPC Error - {result['error']}")
        else:
            print(f"V{n}: {result}")
    except Exception as e:
        print(f"V{n}: Exception - {e}")
    
    time.sleep(5)

print(f"\n{success}/9 submitted. Waiting 30s...")
time.sleep(30)

# Verify
total = s.query("Dpos", "ValidatorList", [])
keys_count = 0
for addr in total.value:
    nk = s.query("Session", "NextKeys", [addr])
    if nk and nk.value:
        keys_count += 1
print(f"Total validators: {len(total.value)}, with session keys: {keys_count}")

for n in range(22, 31):
    kp = Keypair.create_from_uri(f"//Validator{n}")
    nk = s.query("Session", "NextKeys", [kp.ss58_address])
    has = "YES" if nk and nk.value else "NO"
    print(f"  V{n}: keys={has}")
