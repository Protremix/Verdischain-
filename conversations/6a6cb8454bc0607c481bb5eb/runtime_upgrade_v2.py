#!/usr/bin/env python3
"""Full runtime upgrade: authorize + apply."""

import struct
import time
from substrateinterface import SubstrateInterface, Keypair
from hashlib import blake2b

s = SubstrateInterface(url="http://127.0.0.1:9933", ss58_format=909, auto_discover=True)
sudo_kp = Keypair.create_from_uri("//Alice")

# Read the new WASM
wasm_path = "/opt/verdis-chain-rust/target/release/wbuild/verdis-runtime/verdis_runtime.compact.compressed.wasm"
with open(wasm_path, "rb") as f:
    wasm_bytes = f.read()

code_hash = blake2b(wasm_bytes, digest_size=32).digest()
print(f"WASM: {len(wasm_bytes)} bytes, hash: 0x{code_hash.hex()}")

# Step 1: Authorize upgrade
print("\nStep 1: Authorize upgrade")
call = s.compose_call(
    call_module="System",
    call_function="authorize_upgrade",
    call_params={"code_hash": "0x" + code_hash.hex()}
)
ext = s.create_signed_extrinsic(call=call, keypair=sudo_kp)
ext_hex = ext.data.to_hex() if hasattr(ext.data, 'to_hex') else "0x" + ext.data.hex()
r1 = s.rpc_request("author_submitExtrinsic", [ext_hex])
print(f"  Result: {r1}")

if "result" not in r1:
    print("FAILED - aborting")
    exit(1)

print("Waiting 20s...")
time.sleep(20)

# Verify authorization
auth = s.query("System", "AuthorizedUpgrade", [])
print(f"  Authorized: {auth.value if auth and auth.value else 'NOT SET'}")

# Step 2: Apply authorized upgrade
print("\nStep 2: Apply authorized upgrade")
call = s.compose_call(
    call_module="System",
    call_function="apply_authorized_upgrade",
    call_params={"code": "0x" + wasm_bytes.hex()}
)
ext = s.create_signed_extrinsic(call=call, keypair=sudo_kp)
ext_hex = ext.data.to_hex() if hasattr(ext.data, 'to_hex') else "0x" + ext.data.hex()
r2 = s.rpc_request("author_submitExtrinsic", [ext_hex])
print(f"  Result: {r2}")

if "result" in r2:
    print("Waiting 30s for upgrade...")
    time.sleep(30)
    
    # Check new version
    new_rt = s.rpc_request("state_getRuntimeVersion", []).get("result", {})
    print(f"New spec_version: {new_rt.get('specVersion')}")
    
    # Check events
    hdr = s.rpc_request("chain_getHeader", [])
    bn = int(hdr["result"]["number"], 16)
    for b in range(bn - 5, bn + 1):
        bh = s.rpc_request("chain_getBlockHash", [b]).get("result", "")
        if not bh: continue
        events = s.query("System", "Events", [], block_hash=bh)
        if events and events.value:
            for evt in events.value:
                m = evt.get("event", {}).get("module_id", "")
                e = evt.get("event", {}).get("event_id", "")
                if "Code" in e or "Upgrade" in e or "Failed" in e:
                    a = evt.get("event", {}).get("attributes", {})
                    print(f"  Block #{b}: {m}::{e} {str(a)[:200]}")
else:
    print(f"  FAILED: {r2}")

# Step 3: Test Sudo
print("\nStep 3: Test Sudo::sudo(System::remark('upgrade-ok'))")
def compact(n):
    if n < 64: return bytes([n << 2])
    elif n < 16384: return struct.pack("<H", (n << 2) | 0x01)
    elif n < 1073741824: return struct.pack("<I", (n << 2) | 0x02)
    else: return struct.pack("<Q", (n << 2) | 0x03)

rt = s.rpc_request("state_getRuntimeVersion", []).get("result", {})
spec_version = int(rt.get("specVersion", 12))
tx_version = int(rt.get("transactionVersion", 3))
genesis_hash = bytes.fromhex(s.get_block_hash(0)[2:])

acct = s.query("System", "Account", [sudo_kp.ss58_address])
nonce = acct.value.get("nonce", 0) if acct else 0

# Sudo::sudo(System::remark('upgrade-ok'))
remark = bytes([0, 0]) + compact(10) + b"upgrade-ok"
sudo_call = bytes([6, 0]) + remark

era = bytes([0x00])
payload = sudo_call + era + compact(nonce) + compact(0)
payload += struct.pack("<I", spec_version)
payload += struct.pack("<I", tx_version)
payload += genesis_hash + genesis_hash
signature = sudo_kp.sign(payload)
body = bytes([0x84, 0x00]) + bytes(sudo_kp.public_key) + bytes([0x01]) + signature + era + compact(nonce) + compact(0) + sudo_call
ext_hex = "0x" + (compact(len(body)) + body).hex()
r3 = s.rpc_request("author_submitExtrinsic", [ext_hex])
print(f"  Result: {r3}")

if "result" in r3:
    print("Waiting 15s...")
    time.sleep(15)
    
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
    print("Sudo test complete!")
else:
    print("  Sudo test failed")
