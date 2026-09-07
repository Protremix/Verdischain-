#!/usr/bin/env python3
"""Verdis Wallet Balance API — queries Substrate System::Account storage"""
import json, hashlib, struct
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

RPC_URL = "http://localhost:9944"
SYSTEM_PREFIX = "26aa394eea5630e07c48ae0c9558cef7"
ACCOUNT_HASH = "b99d880ec681799c0cf30e8886371da9"  # Twox64("Account")
DECIMALS = 9

def compute_storage_key(account_id_hex):
    """Compute System::Account storage key using Blake2_128"""
    if account_id_hex.startswith("0x"):
        account_id_hex = account_id_hex[2:]
    acct_bytes = bytes.fromhex(account_id_hex)
    # Blake2b with digest_size=16 (128 bits)
    blake_hash = hashlib.blake2b(acct_bytes, digest_size=16).hexdigest()
    return "0x" + SYSTEM_PREFIX + ACCOUNT_HASH + blake_hash + account_id_hex

def rpc_call(method, params):
    import urllib.request
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(RPC_URL, data=payload, headers={"Content-Type": "application/json"})
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read()).get("result")

def decode_u128_le(data, offset):
    """Decode a u128 value from little-endian bytes"""
    val = 0
    for i in range(16):
        val |= data[offset + i] << (i * 8)
    return val

def query_balance(account_id_hex):
    storage_key = compute_storage_key(account_id_hex)
    storage_hex = rpc_call("state_getStorage", [storage_key])
    if not storage_hex or storage_hex == "0x":
        return {"balance": 0, "free": 0, "reserved": 0, "frozen": 0, "nonce": 0, "exists": False}
    
    data = bytes.fromhex(storage_hex[2:])
    nonce = struct.unpack_from("<I", data, 0)[0]
    free = decode_u128_le(data, 16)
    reserved = decode_u128_le(data, 32)
    frozen = decode_u128_le(data, 48)
    
    divisor = 10 ** DECIMALS
    return {
        "exists": True,
        "nonce": nonce,
        "free": free,
        "reserved": reserved,
        "frozen": frozen,
        "freeVRS": free // divisor,
        "reservedVRS": reserved // divisor,
        "frozenVRS": frozen // divisor,
        "totalVRS": (free + reserved) // divisor
    }

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        
        if parsed.path == "/api/balance":
            account_id = params.get("accountId", [None])[0]
            if not account_id:
                self.send_json(400, {"error": "Missing accountId"})
                return
            try:
                result = query_balance(account_id)
                self.send_json(200, {"accountId": account_id, **result})
            except Exception as e:
                self.send_json(500, {"error": str(e)})
        elif parsed.path == "/api/health":
            self.send_json(200, {"status": "ok"})
        else:
            self.send_json(404, {"error": "Not found"})
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def send_json(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)
    
    def log_message(self, format, *args):
        pass  # Suppress logs

if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", 8889), Handler)
    print("Balance API running on port 8889")
    server.serve_forever()
