#!/usr/bin/env python3
"""
Verdis Chain Faucet (Python) — v2.0
Replaces broken Node.js faucet that had signing issues.
Uses substrate-interface library (same as tx_relay_v3).
Sends 100 VRDX per address per 24h from Alice's account.
"""
import json
import os
import sys
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
from collections import defaultdict, deque

try:
    from substrateinterface import SubstrateInterface, Keypair
except ImportError:
    print("ERROR: substrate-interface not installed. Run: pip install substrate-interface")
    sys.exit(1)

# ===== Config =====
NODE_URL = 'ws://127.0.0.1:9933'
SS58_FORMAT = 909
FAUCET_SEED = '//Alice'
AMOUNT_VRDX = 100  # 100 VRDX per drip (Alice has ~350 VRDX free)
AMOUNT_PLANCK = AMOUNT_VRDX * 10**9  # 100 VRDX in smallest unit
RATE_FILE = '/tmp/faucet-rate-limits.json'
STATS_FILE = '/tmp/faucet-stats.json'
PORT = 8080
DECIMALS = 9

# ===== State =====
substrate = None
faucet_kp = None
lock = threading.Lock()

def init():
    global substrate, faucet_kp
    for attempt in range(10):
        try:
            substrate = SubstrateInterface(
                url=NODE_URL,
                ss58_format=SS58_FORMAT,
                auto_discover=True,
                type_registry_preset=None
            )
            faucet_kp = Keypair.create_from_uri(FAUCET_SEED, ss58_format=SS58_FORMAT)
            print(f"Faucet ready. Alice: {faucet_kp.ss58_address}")
            return True
        except Exception as e:
            print(f"Init attempt {attempt+1} failed: {e}")
            time.sleep(5)
    return False

def load_rate_limits():
    if os.path.exists(RATE_FILE):
        with open(RATE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_rate_limits(limits):
    with open(RATE_FILE, 'w') as f:
        json.dump(limits, f)

def load_stats():
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, 'r') as f:
            return json.load(f)
    return {"totalDispensed": 0, "uniqueRecipients": 0, "totalRequests": 0, "dailyRequests": {}, "distributions": []}

def save_stats(stats):
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=2)
    # Also write to nginx-servable path
    try:
        os.makedirs('/var/www/verdiscan/faucet', exist_ok=True)
        with open('/var/www/verdiscan/faucet/stats.json', 'w') as f:
            json.dump({
                "totalDispensed": stats["totalDispensed"],
                "uniqueRecipients": stats["uniqueRecipients"],
                "todayRequests": stats["dailyRequests"].get(time.strftime("%Y-%m-%d"), 0),
                "totalRequests": stats["totalRequests"],
                "distributions": stats["distributions"][:20]
            }, f, indent=2)
    except Exception:
        pass

def send_drip(dest_address):
    """Send AMOUNT_VRDX to dest_address from Alice's account."""
    with lock:  # Prevent concurrent sends (nonce safety)
        try:
            call = substrate.compose_call(
                call_module='Balances',
                call_function='transfer_allow_death',
                call_params={
                    'dest': dest_address,
                    'value': AMOUNT_PLANCK
                }
            )
            extrinsic = substrate.create_signed_extrinsic(call=call, keypair=faucet_kp)
            # Submit without waiting for inclusion (faster, avoids decode bugs)
            tx_hash = substrate.submit_extrinsic(extrinsic, wait_for_inclusion=False)
            return True, str(tx_hash)
        except Exception as e:
            return False, str(e)

class FaucetHandler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def _json(self, code, data):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self._cors()
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _html(self, html, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'text/html')
        self._cors()
        self.end_headers()
        self.wfile.write(html.encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_GET(self):
        if self.path == '/health':
            self._json(200, {"status": "ok", "amount": f"{AMOUNT_VRDX} VRDX"})
            return

        if self.path == '/stats':
            stats = load_stats()
            limits = load_rate_limits()
            self._json(200, {
                "totalDispensed": stats["totalDispensed"],
                "uniqueRecipients": len(limits),
                "todayRequests": stats["dailyRequests"].get(time.strftime("%Y-%m-%d"), 0),
                "totalRequests": stats["totalRequests"],
                "distributions": stats["distributions"][:20]
            })
            return

        if self.path == '/':
            self._html(f'<html><body style="font-family:monospace;padding:40px;background:#040806;color:#00ff88">'
                       f'<h1>Verdis Testnet Faucet</h1>'
                       f'<p>{AMOUNT_VRDX} VRDX per address per 24h</p>'
                       f'<p>POST to / with address=YOUR_ADDRESS</p>'
                       f'<p>Status: <a href="/health">health</a> | <a href="/stats">stats</a></p>'
                       f'</body></html>')
            return

        self._json(404, {"error": "Not found"})

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode()

        # Parse address
        if 'address=' in body:
            params = parse_qs(body)
            address = params.get('address', [''])[0].strip()
        else:
            # JSON body
            try:
                data = json.loads(body)
                address = data.get('address', '').strip()
            except Exception:
                address = body.strip()

        if not address or (not address.startswith('5') and not address.startswith('k')):
            self._json(400, {"error": "Invalid address format"})
            return

        # Rate limit check
        limits = load_rate_limits()
        now = int(time.time())
        if address in limits and now - limits[address] < 86400:
            hours_left = 24 - (now - limits[address]) // 3600
            self._json(429, {"error": f"Rate limited. Try again in {hours_left}h"})
            return

        # Send drip
        success, tx_hash = send_drip(address)

        if success:
            # Record rate limit
            limits[address] = now
            save_rate_limits(limits)

            # Record stats
            stats = load_stats()
            stats["totalDispensed"] += AMOUNT_VRDX
            stats["uniqueRecipients"] = len(limits)
            stats["totalRequests"] += 1
            today = time.strftime("%Y-%m-%d")
            stats["dailyRequests"][today] = stats["dailyRequests"].get(today, 0) + 1
            stats["distributions"].insert(0, {
                "address": address[:8] + '...' + address[-4:],
                "amount": AMOUNT_VRDX,
                "txHash": tx_hash[:10] + '...',
                "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            })
            stats["distributions"] = stats["distributions"][:50]
            save_stats(stats)

            self._json(200, {
                "success": True,
                "amount": str(AMOUNT_VRDX),
                "unit": "VRDX",
                "tx_hash": tx_hash
            })
        else:
            self._json(500, {"error": tx_hash})

    def log_message(self, format, *args):
        print(f"[{time.strftime('%H:%M:%S')}] {args[0]}")

def main():
    if not init():
        print("FATAL: Could not connect to node after 10 attempts")
        sys.exit(1)

    # Write stats on startup and every 30s
    stats = load_stats()
    limits = load_rate_limits()
    stats["uniqueRecipients"] = len(limits)
    save_stats(stats)
    
    def stats_loop():
        while True:
            time.sleep(30)
            stats = load_stats()
            limits = load_rate_limits()
            stats["uniqueRecipients"] = len(limits)
            save_stats(stats)

    threading.Thread(target=stats_loop, daemon=True).start()

    server = HTTPServer(('0.0.0.0', PORT), FaucetHandler)
    print(f"Faucet listening on :{PORT}")
    server.serve_forever()

if __name__ == '__main__':
    main()
