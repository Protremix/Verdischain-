#!/usr/bin/env python3
"""Set session keys for V22-V30 via Sudo+System::set_storage."""
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

def submit_sudo_set_storage(key_bytes, value_bytes):
    # System(0)::set_storage(4) + 1 item
    inner = bytes([0, 4]) + compact(1)
    inner += compact(len(key_bytes)) + key_bytes
    inner += compact(len(value_bytes)) + value_bytes
    # Sudo(6)::sudo(0)
    call_data = bytes([6, 0]) + inner
    
    acct = s.query("System", "Account", [sudo_kp.ss58_address])
    nonce = acct.value.get("nonce", 0) if acct else 0
    
    era = bytes([0x00])
    payload = call_data + era + compact(nonce) + compact(0)
    payload += struct.pack("<I", spec_version) + struct.pack("<I", tx_version)
    payload += genesis_hash + genesis_hash
    sig = sudo_kp.sign(payload)
    body = bytes([0x84, 0x00]) + bytes(sudo_kp.public_key) + bytes([0x01]) + sig
    body += era + compact(nonce) + compact(0) + call_data
    ext_hex = "0x" + (compact(len(body)) + body).hex()
    
    return s.rpc_request("author_submitExtrinsic", [ext_hex]), nonce

success = 0
for n in range(22, 31):
    kp = Keypair.create_from_uri(f"//Validator{n}")
    addr = kp.ss58_address
    babe_pub = bytes(kp.public_key)
    
    # Check if already has keys
    nk = s.query("Session", "NextKeys", [addr])
    if nk and nk.value:
        print(f"V{n}: Already has keys")
        success += 1
        continue
    
    # Generate grandpa key
    seed = hashlib.sha256(f"//Grandpa{n}".encode()).digest()
    gp_kp = Keypair.create_from_seed(seed, crypto_type=1, ss58_format=909)
    grandpa_pub = bytes(gp_kp.public_key)
    
    # Build storage key: Session::NextKeys(addr)
    sk = s.create_storage_key("Session", "NextKeys", [addr])
    key_bytes = bytes.fromhex(sk.to_hex()[2:])
    value_bytes = babe_pub + grandpa_pub
    
    try:
        result, nonce = submit_sudo_set_storage(key_bytes, value_bytes)
        if "result" in result:
            print(f"V{n}: Submitted (nonce={nonce})")
            success += 1
        else:
            print(f"V{n}: Error - {result}")
    except Exception as e:
        print(f"V{n}: Exception - {e}")
    
    time.sleep(8)

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
