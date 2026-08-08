import xxhash
import struct
import urllib.request
import json
import hashlib

def twox_128(data):
    """Substrate twox_128: xxhash_64 with seed=0 and seed=1, in little-endian"""
    h0 = xxhash.xxh64(data, seed=0).intdigest()
    h1 = xxhash.xxh64(data, seed=1).intdigest()
    return struct.pack("<Q", h0) + struct.pack("<Q", h1)

def twox_64(data, seed=0):
    """Substrate twox_64 in little-endian"""
    h = xxhash.xxh64(data, seed=seed).intdigest()
    return struct.pack("<Q", h)

def rpc_call(method, params, port=9933):
    data = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(f"http://localhost:{port}", data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

# Test
sys_hash = twox_128(b"System")
print(f"System: {sys_hash.hex()}")
expected = "26aa394eea5630e07c48ae0c9558cef7"
if sys_hash.hex() == expected:
    print("System hash MATCHES!")
else:
    print(f"Expected: {expected}")
    # Try big-endian
    h0 = xxhash.xxh64(b"System", seed=0).intdigest()
    h1 = xxhash.xxh64(b"System", seed=1).intdigest()
    print(f"h0: {struct.pack('>Q', h0).hex()}")
    print(f"h1: {struct.pack('>Q', h1).hex()}")
    print(f"h0 LE: {struct.pack('<Q', h0).hex()}")
    print(f"h1 LE: {struct.pack('<Q', h1).hex()}")
    # Check if it matches in big-endian
    be = struct.pack(">Q", h0) + struct.pack(">Q", h1)
    print(f"BE combined: {be.hex()}")
