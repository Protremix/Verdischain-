#!/usr/bin/env python3
"""Set session keys for V22 via Sudo+set_storage."""
import hashlib
import struct
import time
from substrateinterface import SubstrateInterface, Keypair

s = SubstrateInterface(url="http://127.0.0.1:9933", ss58_format=909, auto_discover=True)
sudo_kp = Keypair.create_from_uri("//Alice")

rt = s.rpc_request("state_getRuntimeVersion", []).get("result", {})
spec_version = int(rt.get("specVersion", 11))
tx_version = int(rt.get("transactionVersion", 3))
genesis_hash = bytes.fromhex(s.get_block_hash(0)[2:])

def compact(n):
    if n < 64: return bytes([n << 2])
    elif n < 16384: return struct.pack("<H", (n << 2) | 0x01)
    elif n < 1073741824: return struct.pack("<I", (n << 2) | 0x02)
    else: return struct.pack("<Q", (n << 2) | 0x03)

# V22 keypair
kp22 = Keypair.create_from_uri("//Validator22")
seed = hashlib.sha256(b"//Grandpa22").digest()
gp_kp = Keypair.create_from_seed(seed, crypto_type=1, ss58_format=909)

sk = s.create_storage_key("Session", "NextKeys", [kp22.ss58_address])
key_bytes = bytes.fromhex(sk.to_hex()[2:])
value_bytes = bytes(kp22.public_key) + bytes(gp_kp.public_key)

# System(0)::set_storage(4) + 1 item
inner = bytes([0, 4]) + compact(1)
inner += compact(len(key_bytes)) + key_bytes
inner += compact(len(value_bytes)) + value_bytes
# Sudo(6)::sudo(0)
call_data = bytes([6, 0]) + inner

acct = s.query("System", "Account", [sudo_kp.ss58_address])
nonce = acct.value.get("nonce", 0) if acct else 0
print(f"Nonce: {nonce}, key_len={len(key_bytes)}, val_len={len(value_bytes)}")

era = bytes([0x00])
payload = call_data + era + compact(nonce) + compact(0)
payload += struct.pack("<I", spec_version) + struct.pack("<I", tx_version)
payload += genesis_hash + genesis_hash
sig = sudo_kp.sign(payload)
body = bytes([0x84, 0x00]) + bytes(sudo_kp.public_key) + bytes([0x01]) + sig
body += era + compact(nonce) + compact(0) + call_data
ext_hex = "0x" + (compact(len(body)) + body).hex()

r = s.rpc_request("author_submitExtrinsic", [ext_hex])
print(f"Submit: {r}")
time.sleep(20)

# Check events
hdr = s.rpc_request("chain_getHeader", [])
bn = int(hdr["result"]["number"], 16)
for b in range(bn - 4, bn + 1):
    bh = s.rpc_request("chain_getBlockHash", [b]).get("result", "")
    if not bh: continue
    events = s.query("System", "Events", [], block_hash=bh)
    if events and events.value:
        for evt in events.value:
            m = evt.get("event", {}).get("module_id", "")
            e = evt.get("event", {}).get("event_id", "")
            if "Sudo" in m or "Failed" in e:
                a = evt.get("event", {}).get("attributes", {})
                print(f"Block #{b}: {m}::{e} {str(a)[:200]}")

# Check if key was set
nk = s.query("Session", "NextKeys", [kp22.ss58_address])
print(f"V22 keys: {nk.value if nk and nk.value else 'NOT SET'}")
