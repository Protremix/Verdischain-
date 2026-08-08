#!/usr/bin/env python3
"""Runtime upgrade via System::authorize_upgrade + apply_authorized_upgrade."""

import struct
import time
from substrateinterface import SubstrateInterface, Keypair

s = SubstrateInterface(url="http://127.0.0.1:9933", ss58_format=909, auto_discover=True)
sudo_kp = Keypair.create_from_uri("//Alice")

rt = s.rpc_request("state_getRuntimeVersion", []).get("result", {})
spec_version = int(rt.get("specVersion", 11))
tx_version = int(rt.get("transactionVersion", 3))
print(f"Current spec_version: {spec_version}")

def compact(n):
    if n < 64: return bytes([n << 2])
    elif n < 16384: return struct.pack("<H", (n << 2) | 0x01)
    elif n < 1073741824: return struct.pack("<I", (n << 2) | 0x02)
    else: return struct.pack("<Q", (n << 2) | 0x03)

genesis_hash = bytes.fromhex(s.get_block_hash(0)[2:])

def submit_call(call_data, kp):
    acct = s.query("System", "Account", [kp.ss58_address])
    nonce = acct.value.get("nonce", 0) if acct else 0
    era = bytes([0x00])
    payload = call_data + era + compact(nonce) + compact(0)
    payload += struct.pack("<I", spec_version)
    payload += struct.pack("<I", tx_version)
    payload += genesis_hash + genesis_hash
    signature = kp.sign(payload)
    body = bytes([0x84, 0x00]) + bytes(kp.public_key) + bytes([0x01]) + signature + era + compact(nonce) + compact(0) + call_data
    ext_hex = "0x" + (compact(len(body)) + body).hex()
    return s.rpc_request("author_submitExtrinsic", [ext_hex])

# Read the new WASM
wasm_path = "/opt/verdis-chain-rust/target/release/wbuild/verdis-runtime/verdis_runtime.compact.compressed.wasm"
with open(wasm_path, "rb") as f:
    wasm_bytes = f.read()
print(f"WASM size: {len(wasm_bytes)} bytes")

# Compute blake2b hash of the WASM
from hashlib import blake2b
code_hash = blake2b(wasm_bytes, digest_size=32).digest()
code_hash_hex = "0x" + code_hash.hex()
print(f"Code hash: {code_hash_hex}")

# Step 1: Authorize upgrade
# System(0)::authorize_upgrade(8) + hash(32 bytes)
authorize_call = bytes([0, 8]) + code_hash
print(f"\nStep 1: Authorize upgrade")
r1 = submit_call(authorize_call, sudo_kp)
print(f"  Result: {r1}")

if "result" not in r1:
    print("Authorization failed, aborting")
    exit(1)

print("Waiting 15s for block inclusion...")
time.sleep(15)

# Verify authorization
auth = s.query("System", "AuthorizedUpgrade", [])
print(f"  Authorized: {auth.value if auth else 'NONE'}")

# Step 2: Apply authorized upgrade
# System(0)::apply_authorized_upgrade(10) + wasm_bytes
print(f"\nStep 2: Apply authorized upgrade ({len(wasm_bytes)} bytes)")
apply_call = bytes([0, 10]) + compact(len(wasm_bytes)) + wasm_bytes
r2 = submit_call(apply_call, sudo_kp)
print(f"  Result: {r2}")

if "result" in r2:
    print("Waiting 30s for runtime upgrade to take effect...")
    time.sleep(30)
    
    # Check new version
    new_rt = s.rpc_request("state_getRuntimeVersion", []).get("result", {})
    new_spec = int(new_rt.get("specVersion", 0))
    print(f"New spec_version: {new_spec}")
    print(f"Upgrade {'SUCCESS' if new_spec != spec_version else 'MAY HAVE FAILED - same version'}")
    
    if new_spec == spec_version:
        # It might be the same version but with different code
        print("Note: Version may be the same but code changed. Testing Sudo access...")
else:
    print(f"Apply failed: {r2}")

# Test: try a Sudo call now
print(f"\nStep 3: Test Sudo access")
test_call = bytes([6, 0]) + bytes([0, 0]) + compact(4) + b"test"  # Sudo::sudo(System::remark('test'))
r3 = submit_call(test_call, sudo_kp)
print(f"  Result: {r3}")

if "result" in r3:
    print("Waiting 15s...")
    time.sleep(15)
    
    # Check events
    hdr = s.rpc_request("chain_getHeader", [])
    bn = int(hdr["result"]["number"], 16)
    for b in range(bn - 2, bn + 1):
        bh = s.rpc_request("chain_getBlockHash", [b]).get("result", "")
        if not bh: continue
        events = s.query("System", "Events", [], block_hash=bh)
        if events and events.value:
            for evt in events.value:
                m = evt.get("event", {}).get("module_id", "")
                e = evt.get("event", {}).get("event_id", "")
                if "Sudo" in m or "Failed" in e:
                    a = evt.get("event", {}).get("attributes", {})
                    print(f"  Block #{b}: {m}::{e} {str(a)[:200]}")
