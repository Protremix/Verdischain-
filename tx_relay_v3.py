#!/usr/bin/env python3
"""
Verdis Chain Transaction Relay v3.0 — Non-Custodial
====================================================
BREAKING CHANGES from v2:
- No signing keys stored on server
- No derive-address endpoint (mnemonics NEVER sent to server)
- Only accepts pre-signed extrinsics via author_submitExtrinsic
- CORS restricted to verdischain.com only
- Rate limiting on all endpoints
- No transaction signing — relay is a dumb pipe

The relay only:
1. Submits pre-signed extrinsics to the node
2. Provides read-only chain queries (balance, chain info, validators, DEX pools)
"""

import json
import os
import sys
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from collections import defaultdict, deque

try:
    from substrateinterface import SubstrateInterface
except ImportError:
    print("ERROR: substrate-interface not installed. Run: pip install substrate-interface")
    sys.exit(1)

# ===== Configuration =====
NODE_URL = os.environ.get("VERDIS_NODE_URL", "http://127.0.0.1:9950")
PORT = int(os.environ.get("VERDIS_RELAY_PORT", "5001"))
SS58_FORMAT = 909
TOKEN_DECIMALS = 9

# CORS: Only allow Verdis Chain domains
ALLOWED_ORIGINS = [
    "https://verdischain.com",
    "https://www.verdischain.com",
    "https://explorer.verdischain.com",
    "https://wallet.verdischain.com",
    "https://dex.verdischain.com",
]

# Rate limiting: 30 requests per minute per IP
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX = 30     # requests per window
ip_requests = defaultdict(deque)
rate_lock = threading.Lock()

def check_rate_limit(client_ip):
    """Returns True if request is allowed, False if rate limited."""
    with rate_lock:
        now = time.time()
        # Clean old entries
        while ip_requests[client_ip] and ip_requests[client_ip][0] < now - RATE_LIMIT_WINDOW:
            ip_requests[client_ip].popleft()
        if len(ip_requests[client_ip]) >= RATE_LIMIT_MAX:
            return False
        ip_requests[client_ip].append(now)
        return True

def get_cors_header(origin):
    """Return CORS header only for allowed origins."""
    if origin in ALLOWED_ORIGINS:
        return origin
    return ALLOWED_ORIGINS[0]  # Default to main domain

# ===== Substrate Connection =====
substrate = SubstrateInterface(
    url=NODE_URL,
    ss58_format=SS58_FORMAT,
    auto_discover=True,
    type_registry_preset=None
)

print(f"TX Relay v3.0 (Non-Custodial) ready. Node: {NODE_URL}")
print("NO signing keys on server. Only pre-signed extrinsics accepted.")

# ===== Helper Functions =====
def query_balance(address):
    """Query account balance from chain."""
    try:
        result = substrate.query("System", "Account", [address])
        if result:
            return int(result.value.get("data", {}).get("free", 0))
    except Exception:
        pass
    return 0

def get_chain_info():
    """Get chain health and properties."""
    health = substrate.rpc_request("system_health", [])
    chain = substrate.rpc_request("system_chain", [])
    props = substrate.rpc_request("system_properties", [])
    header = substrate.rpc_request("chain_getHeader", [])
    return {
        "health": health.get("result", {}),
        "chain": chain.get("result", ""),
        "properties": props.get("result", {}),
        "header": header.get("result", {}),
    }

def get_validators():
    """Get all validators with stakes and names."""
    validators = substrate.rpc_request("dpos_allValidators", [])
    v_list = validators.get("result", [])
    result = []
    for v_addr in v_list:
        stake = substrate.rpc_request("dpos_validatorStake", [v_addr])
        name = substrate.rpc_request("dpos_validatorName", [v_addr])
        green = substrate.rpc_request("eco_getGreenScore", [v_addr])
        result.append({
            "address": v_addr,
            "stake": int(stake.get("result", 0)),
            "name": name.get("result", ""),
            "green_score": int(green.get("result", 0)),
        })
    return result

def get_dex_pools():
    """Get all DEX pools."""
    pools = substrate.rpc_request("amm_dex_getAllPools", [])
    pool_list = []
    for pool_id in pools.get("result", []):
        detail = substrate.rpc_request("amm_dex_getPool", [pool_id])
        if detail and detail.get("result"):
            pool_list.append(detail["result"])
    return pool_list

def submit_signed_extrinsic(extrinsic_hex):
    """Submit a pre-signed extrinsic to the node. NO signing on server."""
    if not extrinsic_hex:
        raise ValueError("Missing extrinsic hex")
    if not extrinsic_hex.startswith("0x"):
        raise ValueError("Extrinsic must be hex-encoded (0x...)")
    # Just submit — we never sign anything
    result = substrate.rpc_request("author_submitExtrinsic", [extrinsic_hex])
    return result.get("result", "")

def estimate_fee(call_data_hex):
    """Estimate transaction fee from a pre-signed or unsigned extrinsic."""
    try:
        result = substrate.rpc_request("payment_queryInfo", [call_data_hex])
        return result.get("result", {})
    except Exception:
        return {}

# ===== HTTP Handler =====
class RelayHandler(BaseHTTPRequestHandler):
    def _cors_headers(self):
        origin = self.headers.get("Origin", "")
        allowed = get_cors_header(origin)
        self.send_header("Access-Control-Allow-Origin", allowed)
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Vary", "Origin")

    def _send_json(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self._cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _success(self, data=None, extra=None):
        payload = {"ok": True}
        if data is not None:
            payload["data"] = data
        if extra:
            payload.update(extra)
        self._send_json(200, payload)

    def _error(self, msg, code=400):
        self._send_json(code, {"ok": False, "error": msg})

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors_headers()
        self.end_headers()

    def do_GET(self):
        client_ip = self.client_address[0]
        if not check_rate_limit(client_ip):
            self._error("Rate limit exceeded. Max 30 requests/minute.", 429)
            return

        path = self.path.rstrip("/") or "/"
        
        if path == "/health":
            self._success({"status": "ok", "version": "3.0", "custodial": False})
        elif path == "/chain-info":
            try:
                info = get_chain_info()
                self._success(info)
            except Exception as e:
                self._error(f"Chain query failed: {str(e)}")
        elif path == "/validators":
            try:
                vals = get_validators()
                self._success({"validators": vals, "count": len(vals)})
            except Exception as e:
                self._error(f"Validator query failed: {str(e)}")
        elif path == "/dex-pools":
            try:
                pools = get_dex_pools()
                self._success({"pools": pools, "count": len(pools)})
            except Exception as e:
                self._error(f"DEX query failed: {str(e)}")
        else:
            self._error("Unknown endpoint", 404)

    def do_POST(self):
        client_ip = self.client_address[0]
        if not check_rate_limit(client_ip):
            self._error("Rate limit exceeded. Max 30 requests/minute.", 429)
            return

        # Verify CORS origin
        origin = self.headers.get("Origin", "")
        if origin and origin not in ALLOWED_ORIGINS:
            self._error("Origin not allowed", 403)
            return

        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body_raw = self.rfile.read(content_length)
            body = json.loads(body_raw) if body_raw else {}
        except Exception:
            self._error("Invalid JSON body")
            return

        action = body.get("action", "")

        # ===== READ-ONLY ACTIONS =====
        if action == "balance":
            address = body.get("address", "")
            if not address:
                self._error("Missing address")
                return
            balance = query_balance(address)
            self._success({"address": address, "balance": balance})

        elif action == "chain-info":
            try:
                info = get_chain_info()
                self._success(info)
            except Exception as e:
                self._error(f"Chain query failed: {str(e)}")

        elif action == "validators":
            try:
                vals = get_validators()
                self._success({"validators": vals, "count": len(vals)})
            except Exception as e:
                self._error(f"Validator query failed: {str(e)}")

        elif action == "dex-pools":
            try:
                pools = get_dex_pools()
                self._success({"pools": pools, "count": len(pools)})
            except Exception as e:
                self._error(f"DEX query failed: {str(e)}")

        # ===== SIGNED EXTRINSIC SUBMISSION (non-custodial) =====
        elif action == "submit-extrinsic":
            extrinsic = body.get("extrinsic", "")
            if not extrinsic:
                self._error("Missing 'extrinsic' field (pre-signed hex)")
                return
            try:
                tx_hash = submit_signed_extrinsic(extrinsic)
                self._success({"tx_hash": tx_hash})
            except Exception as e:
                self._error(f"Extrinsic submission failed: {str(e)}")

        # ===== FEE ESTIMATION =====
        elif action == "estimate-fee":
            call_data = body.get("call_data", "")
            if not call_data:
                self._error("Missing 'call_data' field")
                return
            try:
                fee_info = estimate_fee(call_data)
                self._success({"fee_info": fee_info})
            except Exception as e:
                self._error(f"Fee estimation failed: {str(e)}")

        else:
            self._error(f"Unknown action: {action}. Supported: balance, chain-info, validators, dex-pools, submit-extrinsic, estimate-fee")

    def log_message(self, format, *args):
        # Minimal logging — no sensitive data
        print(f"[{self.client_address[0]}] {args[0] if args else ''}")


def main():
    server = HTTPServer(("127.0.0.1", PORT), RelayHandler)
    print(f"TX Relay v3.0 listening on http://127.0.0.1:{PORT}")
    print(f"Allowed origins: {', '.join(ALLOWED_ORIGINS)}")
    print(f"Rate limit: {RATE_LIMIT_MAX} req/{RATE_LIMIT_WINDOW}s per IP")
    server.serve_forever()

if __name__ == "__main__":
    main()
