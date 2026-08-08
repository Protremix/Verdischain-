#!/usr/bin/env python3
"""Verdis Chain Transaction Relay v2.0 - Supports balances.transfer, amm_dex.swap, amm_dex.add_liquidity, and system.remark."""

import json
import os
import sys
import traceback
from http.server import HTTPServer, BaseHTTPRequestHandler
from substrateinterface import SubstrateInterface, Keypair

# Connect to local node
substrate = SubstrateInterface(
    url="http://127.0.0.1:9933",
    ss58_format=909,
    auto_discover=True,
    type_registry_preset=None
)

# Use Alice keypair for signing (pre-funded dev account, has 13K+ VRDX)
SIGNER = Keypair.create_from_uri("//Charlie")
SIGNER_ADDRESS = SIGNER.ss58_address
print(f"TX Relay v2.0 ready. Signing as: {SIGNER_ADDRESS}")

TOKEN_DECIMALS = 9
VRDX_TOKEN = b"VRDX"

def decode_token_bytes(token_bytes):
    """Convert token byte array or hex to symbol string."""
    if isinstance(token_bytes, list):
        return bytes(token_bytes).decode('utf-8', errors='ignore')
    if isinstance(token_bytes, str):
        if token_bytes.startswith('0x'):
            return bytes.fromhex(token_bytes[2:]).decode('utf-8', errors='ignore')
        return token_bytes
    return str(token_bytes)

def get_signer_balance():
    """Get the signer's free balance."""
    try:
        result = substrate.query("System", "Account", [SIGNER_ADDRESS])
        if result:
            data = result.value
            free = data.get("data", {}).get("free", 0)
            return int(free)
    except Exception:
        pass
    return 0

def submit_call(pallet, call_name, params):
    """Compose, sign, and submit a call to the chain."""
    call = substrate.compose_call(pallet, call_name, params)
    extrinsic = substrate.create_signed_extrinsic(call, SIGNER)
    result = substrate.submit_extrinsic(extrinsic, wait_for_inclusion=False)
    return result

class RelayHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        """Health check and signer info."""
        balance = get_signer_balance()
        balance_fmt = f"{balance / 10**TOKEN_DECIMALS:,.4f}" if balance else "0"
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps({
            "status": "ok",
            "version": "2.0",
            "signer": SIGNER_ADDRESS,
            "signer_balance": balance,
            "signer_balance_formatted": f"{balance_fmt} VRDX",
            "supported_calls": [
                "system.remark",
                "balances.transfer_allow_death",
                "amm_dex.swap",
                "amm_dex.add_liquidity",
                "amm_dex.remove_liquidity",
                "dpos.vote",
                "dpos.register_validator"
            ]
        }).encode())

    def do_POST(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
            action = body.get("action", "remark")

            if action == "derive-address":
                mnemonic = body.get("mnemonic", "")
                words = mnemonic.strip().split()
                if len(words) != 12:
                    self._error("Mnemonic must be exactly 12 words")
                    return
                try:
                    kp = Keypair.create_from_mnemonic(mnemonic, ss58_format=909)
                    self._success(None, {"address": kp.ss58_address, "public_key": kp.public_key.hex(), "crypto_type": "sr25519", "ss58_prefix": 909})
                except Exception as e:
                    self._error("Address derivation failed: " + str(e))
                return

            if action == "remark":
                remark = body.get("remark", "").encode("utf-8")
                if len(remark) > 256:
                    self._error("Remark too long (max 256 bytes)")
                    return
                result = submit_call("System", "remark", {"remark": remark})
                self._success(result, {"remark": remark.decode("utf-8")})

            elif action == "transfer":
                dest = body.get("dest", body.get("to", ""))
                amount = body.get("amount", body.get("value", 0))
                if not dest:
                    self._error("Missing destination address")
                    return
                if not amount or int(amount) <= 0:
                    self._error("Invalid amount")
                    return
                amount_int = int(amount)
                signer_bal = get_signer_balance()
                if amount_int > signer_bal:
                    self._error(f"Insufficient signer balance: has {signer_bal/10**TOKEN_DECIMALS:.4f} VRDX, needs {amount_int/10**TOKEN_DECIMALS:.4f} VRDX")
                    return
                result = submit_call("Balances", "transfer_allow_death", {
                    "dest": dest,
                    "value": amount_int
                })
                self._success(result, {
                    "type": "transfer",
                    "dest": dest,
                    "amount": amount_int,
                    "amount_formatted": f"{amount_int/10**TOKEN_DECIMALS:.4f} VRDX"
                })

            elif action == "swap":
                pool_id = int(body.get("pool_id", 0))
                token_in = body.get("token_in", "VRDX")
                amount_in = int(body.get("amount_in", 0))
                min_amount_out = int(body.get("min_amount_out", 0))
                if amount_in <= 0:
                    self._error("Invalid amount_in")
                    return
                token_in_bytes = token_in.encode("utf-8") if isinstance(token_in, str) else bytes(token_in)
                signer_bal = get_signer_balance()
                if amount_in > signer_bal:
                    self._error(f"Insufficient signer balance for swap")
                    return
                result = submit_call("AmmDex", "swap", {
                    "pool_id": pool_id,
                    "token_in": token_in_bytes,
                    "amount_in": amount_in,
                    "min_amount_out": min_amount_out
                })
                self._success(result, {
                    "type": "swap",
                    "pool_id": pool_id,
                    "token_in": token_in,
                    "amount_in": amount_in,
                    "min_amount_out": min_amount_out
                })

            elif action == "add_liquidity":
                pool_id = int(body.get("pool_id", 0))
                amount_a = int(body.get("amount_a", 0))
                amount_b = int(body.get("amount_b", 0))
                if amount_a <= 0 or amount_b <= 0:
                    self._error("Invalid amounts")
                    return
                result = submit_call("AmmDex", "add_liquidity", {
                    "pool_id": pool_id,
                    "amount_a": amount_a,
                    "amount_b": amount_b
                })
                self._success(result, {
                    "type": "add_liquidity",
                    "pool_id": pool_id,
                    "amount_a": amount_a,
                    "amount_b": amount_b
                })

            elif action == "remove_liquidity":
                pool_id = int(body.get("pool_id", 0))
                lp_amount = int(body.get("lp_amount", 0))
                if lp_amount <= 0:
                    self._error("Invalid LP amount")
                    return
                result = submit_call("AmmDex", "remove_liquidity", {
                    "pool_id": pool_id,
                    "lp_amount": lp_amount
                })
                self._success(result, {
                    "type": "remove_liquidity",
                    "pool_id": pool_id,
                    "lp_amount": lp_amount
                })

            elif action == "vote":
                validator = body.get("validator", "")
                amount = int(body.get("amount", 0))
                if not validator:
                    self._error("Missing validator address")
                    return
                if amount <= 0:
                    self._error("Invalid amount")
                    return
                result = submit_call("Dpos", "vote", {
                    "validator": validator,
                    "amount": amount
                })
                self._success(result, {
                    "type": "vote",
                    "validator": validator,
                    "amount": amount
                })

            else:
                self._error(f"Unknown action: {action}")

        except Exception as e:
            print(f"[RELAY] Error: {traceback.format_exc()}")
            self._error(str(e))

    def _success(self, result, extra=None):
        response = {
            "ok": True,
            "extrinsic_hash": getattr(result, "extrinsic_hash", None),
            "block_hash": getattr(result, "block_hash", None),
            "signer": SIGNER_ADDRESS,
        }
        if extra:
            response.update(extra)
        print(f"[RELAY] TX submitted: {response.get('extrinsic_hash', '?')} - {response.get('type', 'remark')}")
        self.wfile.write(json.dumps(response).encode())

    def _error(self, msg):
        print(f"[RELAY] Error: {msg}")
        self.wfile.write(json.dumps({"ok": False, "error": msg}).encode())


if __name__ == "__main__":
    port = int(os.environ.get("TX_RELAY_PORT", 5001))
    server = HTTPServer(("127.0.0.1", port), RelayHandler)
    print(f"TX Relay v2.0 listening on http://127.0.0.1:{port}")
    server.serve_forever()
