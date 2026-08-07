#!/usr/bin/env python3
"""Verdis RPC Filter Proxy — blocks unsafe RPC methods before forwarding to Substrate node.

Sits between nginx and the Substrate RPC node (on port 9950), filtering out
requests that contain unsafe methods like author_insertKey, author_rotateKeys,
system_addReservedPeer, system_removeReservedPeer.

Listens on 127.0.0.1:9950, forwards safe requests to 127.0.0.1:9949.
"""
import json
import sys
import http.server
import urllib.request
import urllib.error
import threading
import time
import os

LISTEN_PORT = 9950
BACKEND_PORT = 9949
BACKEND_URL = f"http://127.0.0.1:{BACKEND_PORT}"

# Methods that must never be exposed externally
BLOCKED_METHODS = {
    "author_insertKey",
    "author_removeKey",
    "author_rotateKeys",
    "author_rotateKeysWithOwner",
    "author_submitExtrinsic",  # block unsigned/raw extrinsic submission
    "author_pendingExtrinsics",
    "system_addReservedPeer",
    "system_removeReservedPeer",
    "system_setHeapPages",
    "system_setStorage",
    "system_addLog",
    "system_addWellKnownLog",
    "state_call",
}

# Allow author_submitExtrinsic for signed transactions (dapps need it)
# We'll check if the method is in the blocked set and reject
# Actually, author_submitExtrinsic IS needed for dapps to submit signed transactions
# Remove it from blocked
BLOCKED_METHODS.discard("author_submitExtrinsic")

LOG_FILE = "/var/log/verdis-rpc-filter.log"
START_TIME = time.time()
request_count = 0
blocked_count = 0

def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{ts}] {msg}\n")

def check_methods(body_str):
    """Check if the request body contains any blocked RPC methods."""
    try:
        data = json.loads(body_str)
    except json.JSONDecodeError:
        return None  # Let the backend handle invalid JSON

    # Single request
    if isinstance(data, dict) and "method" in data:
        method = data.get("method", "")
        if method in BLOCKED_METHODS:
            return [method]
        return None

    # Batch request (array of requests)
    if isinstance(data, list):
        blocked = []
        for item in data:
            if isinstance(item, dict) and "method" in item:
                method = item.get("method", "")
                if method in BLOCKED_METHODS:
                    blocked.append(method)
        return blocked if blocked else None

    return None

def make_error_response(method, id_val, code=-32600, message="Method blocked by RPC filter"):
    return json.dumps({
        "jsonrpc": "2.0",
        "error": {
            "code": code,
            "message": f"Method '{method}' is blocked by the RPC security filter"
        },
        "id": id_val if id_val is not None else None
    }).encode()

class FilterHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        global request_count, blocked_count
        request_count += 1

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        body_str = body.decode("utf-8", errors="replace")

        # Check for blocked methods
        blocked = check_methods(body_str)
        if blocked:
            blocked_count += 1
            for m in blocked:
                log(f"BLOCKED method={m} from={self.client_address[0]} path={self.path}")

            # Return error response for each blocked method
            try:
                data = json.loads(body_str)
                if isinstance(data, list):
                    # Batch — return errors for blocked, forward the rest
                    responses = []
                    for item in data:
                        if isinstance(item, dict) and item.get("method") in BLOCKED_METHODS:
                            responses.append(json.loads(make_error_response(
                                item.get("method", ""), item.get("id"))))
                        else:
                            # Forward this one
                            single_body = json.dumps(item).encode()
                            resp = self._forward(single_body)
                            responses.append(json.loads(resp))
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(responses).encode())
                    return
                else:
                    # Single blocked request
                    id_val = data.get("id") if isinstance(data, dict) else None
                    resp = make_error_response(blocked[0], id_val)
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(resp)
                    return
            except Exception as e:
                log(f"ERROR processing blocked request: {e}")

        # Forward to backend
        resp = self._forward(body)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(resp)

    def do_GET(self):
        # Forward GET requests (health checks, etc.)
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b""
        resp = self._forward(body, method="GET")
        if resp:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(resp)
        else:
            self.send_response(502)
            self.end_headers()

    def do_OPTIONS(self):
        # CORS preflight
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _forward(self, body, method="POST"):
        """Forward request to the Substrate backend."""
        try:
            req = urllib.request.Request(
                BACKEND_URL,
                data=body,
                headers={"Content-Type": "application/json"},
                method=method
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            return json.dumps({
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": f"Backend error: {e.code}"},
                "id": None
            }).encode()
        except Exception as e:
            log(f"FORWARD ERROR: {e}")
            return json.dumps({
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": f"Proxy error: {str(e)}"},
                "id": None
            }).encode()

    def log_message(self, format, *args):
        pass  # Suppress default logging

class ThreadedHTTPServer(http.server.ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

def health_check():
    """Log stats every 5 minutes."""
    while True:
        time.sleep(300)
        uptime = int(time.time() - START_TIME)
        log(f"STATS uptime={uptime}s requests={request_count} blocked={blocked_count}")

if __name__ == "__main__":
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    log(f"RPC Filter Proxy starting on port {LISTEN_PORT} -> {BACKEND_PORT}")
    log(f"Blocked methods: {', '.join(sorted(BLOCKED_METHODS))}")

    # Start health check thread
    t = threading.Thread(target=health_check, daemon=True)
    t.start()

    server = ThreadedHTTPServer(("127.0.0.1", LISTEN_PORT), FilterHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log("Shutting down...")
        server.shutdown()
