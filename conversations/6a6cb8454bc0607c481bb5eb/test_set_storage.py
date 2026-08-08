#!/usr/bin/env python3
"""Submit a single sudo+set_storage and check events."""

import hashlib
import struct
import time
from substrateinterface import SubstrateInterface, Keypair

s = SubstrateInterface(url="http://127.0.0.1:9933", ss58_format=909, auto_discover=True)
sudo_kp = Keypair.create_from_uri("//Alice")

rt = s.rpc_request("state_getRuntimeVersion", []).get("result", {})
spec_version = int(rt.get("specVersion", 11))
tx_version = int(rt.get("transactionVersion", 3))

def compact(n):
    if n < 64:
        return bytes([n << 2])
    elif n < 16384:
        return struct.pack("<H", (n << 2) | 0x01)
    elif n < 1073741824:
        return struct.pack("<I", (n << 2) | 0x02)
    else:
        return struct.pack("<Q", (n << 2) | 0x03)

# Get V22 info
kp = Keypair.create_from_uri("//Validator22")
addr = kp.ss58_address
babe_pub = bytes(kp.public_key)

seed = hashlib.sha256(b"//Grandpa22").digest()
gp_kp = Keypair.create_from_seed(seed, crypto_type=1, ss58_format=909)
grandpa_pub = bytes(gp_kp.public_key)

sk = s.create_storage_key("Session", "NextKeys", [addr])
key_bytes = bytes.fromhex(sk.to_hex()[2:])
value_bytes = babe_pub + grandpa_pub

# Build call: Sudo(6)::sudo(0) + System(0)::set_storage(4) + items
inner = bytes([0, 4])  # System::set_storage
inner += compact(1)   # 1 item
inner += compact(len(key_bytes)) + key_bytes
inner += compact(len(value_bytes)) + value_bytes
call_data = bytes([6, 0]) + inner  # Sudo::sudo

# Get nonce
genesis_hash = bytes.fromhex(s.get_block_hash(0)[2:])
acct = s.query("System", "Account", [sudo_kp.ss58_address])
nonce = acct.value.get("nonce", 0) if acct else 0
print(f"Alice nonce: {nonce}")

# Build signing payload
era = bytes([0x00])
payload = call_data + era + compact(nonce) + compact(0)
payload += struct.pack("<I", spec_version)
payload += struct.pack("<I", tx_version)
payload += genesis_hash
payload += genesis_hash

signature = sudo_kp.sign(payload)

# Build extrinsic
body = bytes([0x84])
body += bytes([0x00])
body += bytes(sudo_kp.public_key)
body += bytes([0x01])
body += signature
body += era
body += compact(nonce)
body += compact(0)
body += call_data

ext_hex = "0x" + (compact(len(body)) + body).hex()
print(f"Extrinsic: {ext_hex[:80]}...")
print(f"Call data: 0x{call_data.hex()}")

result = s.rpc_request("author_submitExtrinsic", [ext_hex])
print(f"Submit result: {result}")

if "result" in result:
    print("Waiting 20s for block inclusion...")
    time.sleep(20)
    
    # Check events in last 5 blocks
    hdr = s.rpc_request("chain_getHeader", [])
    block_num = int(hdr["result"]["number"], 16)
    
    for bn in range(block_num - 3, block_num + 1):
        bh = s.rpc_request("chain_getBlockHash", [bn]).get("result", "")
        if not bh: continue
        
        events = s.query("System", "Events", [], block_hash=bh)
        if events and events.value:
            for evt in events.value:
                module = evt.get("event", {}).get("module_id", "")
                eid = evt.get("event", {}).get("event_id", "")
                print(f"  Block #{bn}: {module}::{eid}")
                if "Sudo" in module or "Failed" in eid or "set" in eid.lower():
                    attrs = evt.get("event", {}).get("attributes", {})
                    print(f"    Attrs: {str(attrs)[:300]}")
    
    # Check if V22 keys are set now
    nk = s.query("Session", "NextKeys", [addr])
    print(f"\nV22 keys: {nk.value if nk and nk.value else 'NONE'}")
else:
    print("Submission failed!")
