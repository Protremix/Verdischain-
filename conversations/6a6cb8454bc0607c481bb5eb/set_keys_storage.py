#!/usr/bin/env python3
"""Set session keys via Sudo + System::set_storage using raw SCALE encoding."""

import hashlib
import struct
import time
from substrateinterface import SubstrateInterface, Keypair

substrate = SubstrateInterface(url="http://127.0.0.1:9933", ss58_format=909, auto_discover=True)
sudo_kp = Keypair.create_from_uri("//Alice")

def compact_encode(n):
    if n < 64: return bytes([n << 2])
    elif n < 16384: return struct.pack("<H", (n << 2) | 0x01)
    elif n < 1073741824: return struct.pack("<I", (n << 2) | 0x02)
    else: return struct.pack("<Q", (n << 2) | 0x03)

def set_keys_storage(n):
    """Set NextKeys storage for validator V{n} via Sudo+set_storage."""
    kp = Keypair.create_from_uri(f"//Validator{n}")
    addr = kp.ss58_address
    babe_pub = bytes(kp.public_key)
    
    # Generate ed25519 grandpa key
    seed = hashlib.sha256(f"//Grandpa{n}".encode()).digest()
    gp_kp = Keypair.create_from_seed(seed, crypto_type=1, ss58_format=909)
    grandpa_pub = bytes(gp_kp.public_key)
    
    # Check if already set
    nk = substrate.query("Session", "NextKeys", [addr])
    if nk and nk.value:
        print(f"V{n}: Already has keys")
        return True
    
    # Build storage key for Session.NextKeys[addr]
    # Storage key = Twox64("Session") + Twox64("NextKeys") + hash(addr)
    # For StorageMap with Blake2_128Concat: hash = Blake2_128(addr) + addr
    from hashlib import blake2b
    module_prefix = blake2b(b"Session", digest_size=16).digest()  # Twox64
    storage_prefix = blake2b(b"NextKeys", digest_size=16).digest()  # Twox64
    # Actually Substrate uses xxHash for prefixes, not Blake2
    # Let me use the actual hash
    
    # For Substrate, the storage prefix uses Twox64 (xxHash64 with seed 0)
    # But hashlib doesn't have xxHash. Let me use the substrateinterface helper.
    
    # Actually, let me just query an existing key and replicate the format
    # Or use substrateinterface's generate_storage_call
    pass

# First, let's find the correct storage key format by checking Alice's existing key
alice = Keypair.create_from_uri("//Alice")
alice_addr = alice.ss58_address

# Get the raw storage key using substrateinterface
storage_key = substrate.generate_storage_call("Session", "NextKeys", [alice_addr])
print(f"Storage key for Alice NextKeys: {storage_key}")

# Also try using the scalecodec helper
from scalecodec import GenericStorageKey
try:
    # The storage key format in Substrate is:
    # Twox64(pallet) + Twox64(storage) + hash_fn(key)
    # For Blake2_128Concat: Blake2_128(key) + key
    import xxhash
    mod_hash = xxhash.xxh64("Session", seed=0).digest()
    stor_hash = xxhash.xxh64("NextKeys", seed=0).digest()
    alice_hash = blake2b(bytes(alice.public_key), digest_size=16).digest()
    key = mod_hash + stor_hash + alice_hash + bytes(alice.public_key)
    print(f"Manual key: 0x{key.hex()}")
    print(f"Match: {storage_key == '0x' + key.hex()}")
except ImportError:
    print("xxhash not available")

# Let me try a different approach - just use the storage key from substrateinterface
# and replicate the pattern for V22-V30
