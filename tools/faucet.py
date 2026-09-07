#!/usr/bin/env python3
"""Verdis Testnet Faucet — distributes 1000 VRS per address per 24h"""
import json, os, time, threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from substrateinterface import SubstrateInterface, Keypair

RPC_URL = "ws://localhost:9948"
FAUCET_SEED = "//Alice"
AMOUNT = 1000000000000  # 1000 VRS (9 decimals)
RATE_LIMIT_FILE = "/tmp/faucet-rate-limits.json"

if not os.path.exists(RATE_LIMIT_FILE):
    with open(RATE_LIMIT_FILE, 'w') as f:
        json.dump({}, f)

rate_lock = threading.Lock()
substrate = SubstrateInterface(url=RPC_URL, type_registry_preset='substrate-node-template')
faucet_kp = Keypair.create_from_uri(FAUCET_SEED)

class FaucetHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<html><body><h1>Verdis Testnet Faucet</h1><p>1000 VRS per address per 24h</p><form method=POST><input name=address style=width:400px><button>Request</button></form></body></html>')
        elif self.path == '/health':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')

    def do_POST(self):
        body = self.rfile.read(int(self.headers['Content-Length'])).decode()
        address = body.split('address=')[1].replace('+',' ').strip() if 'address=' in body else ''
        if not address.startswith('5'):
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Invalid address'}).encode())
            return

        with rate_lock:
            with open(RATE_LIMIT_FILE, 'r') as f:
                limits = json.load(f)
            now = int(time.time())
            if now - limits.get(address, 0) < 86400:
                self.send_response(429)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': f'Rate limited. Try in {24 - (now - limits.get(address,0))//3600}h'}).encode())
                return

            try:
                nonce = substrate.get_account_nonce(faucet_kp.ss58_address)
                call = substrate.compose_call('Balances', 'transfer_allow_death', {'dest': address, 'value': AMOUNT})
                extrinsic = substrate.create_signed_extrinsic(call=call, keypair=faucet_kp, nonce=nonce)
                receipt = substrate.submit_extrinsic(extrinsic, wait_for_inclusion=False, wait_for_finalization=False)
                
                if receipt and receipt.extrinsic_hash:
                    limits[address] = now
                    with open(RATE_LIMIT_FILE, 'w') as f:
                        json.dump(limits, f)
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'success': True, 'amount': '1000', 'unit': 'VRS', 'tx_hash': receipt.extrinsic_hash}).encode())
                else:
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Transaction failed', 'tx_hash': receipt.extrinsic_hash}).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 8080), FaucetHandler)
    print('Faucet running on :8080')
    server.serve_forever()
