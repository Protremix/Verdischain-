import socket
import ssl
import base64
import os

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

ws_endpoints = [
    "wss://verdischain.com/ws",
    "wss://verdischain.com/substrate-ws",
    "wss://verdischain.com/rpc",
    "wss://rpc.verdischain.com"
]

for ws_url in ws_endpoints:
    print(f"\n==========================================")
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
        resp = s.recv(4096).decode('utf-8', errors='ignore')
        s.close()
        print(resp[:500])
    except Exception as e:
        print(f"WS Error: {e}")
