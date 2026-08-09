#!/usr/bin/env python3
"""Verdis Chain Transaction Relay - accepts remark messages from the web wallet and submits them as signed on-chain transactions."""

import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from substrateinterface import SubstrateInterface, Keypair

# Connect to local node
substrate = SubstrateInterface(
    url="http://127.0.0.1:9933",
    ss58_format=909,
    auto_discover=True,
    type_registry_preset=None
)

# Use Bob keypair for signing (pre-funded dev account)
keypair = Keypair.create_from_uri("//Bob")
ALICE_ADDRESS = keypair.ss58_address
print(f"TX Relay ready. Signing as: {ALICE_ADDRESS}")

class RelayHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok", "signer": ALICE_ADDRESS}).encode())

    def do_POST(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
            remark = body.get("remark", "").encode("utf-8")
            sender_label = body.get("sender", "Wallet User")

            if len(remark) > 256:
                self.wfile.write(json.dumps({"ok": False, "error": "Remark too long (max 256 bytes)"}).encode())
                return

            # Compose and sign the system.remark call
            call = substrate.compose_call("System", "remark", {"remark": remark})
            extrinsic = substrate.create_signed_extrinsic(call, keypair)
            result = substrate.submit_extrinsic(extrinsic, wait_for_inclusion=False)

            response = {
                "ok": True,
                "extrinsic_hash": result.extrinsic_hash,
                "block": None,
                "signer": ALICE_ADDRESS,
                "remark": remark.decode("utf-8"),
                "sender_label": sender_label
            }
            print(f"[RELAY] TX submitted: {result.extrinsic_hash} - {remark.decode()[:80]}")
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            print(f"[RELAY] Error: {str(e)}")
            self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode())

if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", 5001), RelayHandler)
    print("TX Relay listening on http://127.0.0.1:5001")
    server.serve_forever()
