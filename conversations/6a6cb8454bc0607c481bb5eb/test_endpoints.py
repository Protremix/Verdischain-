import urllib.request
import urllib.error
import ssl
import json
import socket

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

endpoints_to_test = [
    # RPC endpoints
    ("POST", "https://rpc.verdischain.com", {"jsonrpc": "2.0", "method": "system_health", "params": [], "id": 1}),
    ("POST", "https://rpc.verdischain.com", {"jsonrpc": "2.0", "method": "chain_getHeader", "params": [], "id": 1}),
    ("POST", "https://verdischain.com/rpc", {"jsonrpc": "2.0", "method": "system_health", "params": [], "id": 1}),
    ("POST", "https://verdischain.com/rpc/", {"jsonrpc": "2.0", "method": "system_health", "params": [], "id": 1}),
    ("GET", "https://verdischain.com/rpc", None),
    
    # API endpoints
    ("GET", "https://verdischain.com/api/", None),
    ("GET", "https://verdischain.com/api/v1", None),
    ("GET", "https://verdischain.com/api/v1/token/holders", None),
    ("GET", "https://verdischain.com/api/v1/account/vrd1sample", None),
    ("POST", "https://verdischain.com/api/tx-relay", {"tx": "0x1234"}),
    ("GET", "https://verdischain.com/faucet/stats.json", None),
    ("GET", "https://verdischain.com/faucet/api/stats", None),
    ("POST", "https://verdischain.com/faucet/api", {"address": "vrd1test"}),
    ("GET", "https://verdischain.com/price-history.json", None),
    ("GET", "https://verdischain.com/api/docs/", None),
]

ws_endpoints = [
    "wss://verdischain.com/ws",
    "wss://verdischain.com/substrate-ws",
]

print("=== TESTING HTTP / JSON-RPC ENDPOINTS ===")
results = {}

for method, url, payload in endpoints_to_test:
    key = f"{method} {url}"
    print(f"Testing {key}...")
    try:
        data_bytes = json.dumps(payload).encode('utf-8') if payload else None
        req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)
        if payload:
            req.add_header('Content-Type', 'application/json')
            
        with urllib.request.urlopen(req, context=ctx, timeout=5) as resp:
            body = resp.read().decode('utf-8', errors='ignore')
            results[key] = {
                'status': resp.status,
                'body_snippet': body[:200]
            }
            print(f"  -> SUCCESS ({resp.status}): {body[:100]}")
    except urllib.error.HTTPError as e:
        results[key] = {'status': e.code, 'error': str(e)}
        print(f"  -> HTTP ERROR {e.code}")
    except Exception as e:
        results[key] = {'status': 'Error', 'error': str(e)}
        print(f"  -> ERROR: {e}")

print("\n=== TESTING WEBSOCKET ENDPOINTS ===")
# Simple WS test using python websocket or raw ssl socket handshakes
import base64
for ws_url in ws_endpoints:
    print(f"Testing WS {ws_url}...")
    host = ws_url.replace("wss://", "").replace("ws://", "").split("/")[0]
    path = "/" + "/".join(ws_url.replace("wss://", "").replace("ws://", "").split("/")[1:])
    try:
        s = socket.create_connection((host, 443), timeout=5)
        s = ctx.wrap_socket(s, server_hostname=host)
        key = base64.b64encode(os.urandom(16)).decode('ascii')
        headers = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host}\r\n"
            f"Upgrade: websocket\r\n"
            f"Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            f"Sec-WebSocket-Version: 13\r\n\r\n"
        )
        s.sendall(headers.encode('utf-8'))
        resp = s.recv(1024).decode('utf-8', errors='ignore')
        s.close()
        print(f"  -> WS Response: {resp.splitlines()[0] if resp else 'No response'}")
    except Exception as e:
        print(f"  -> WS Error: {e}")

