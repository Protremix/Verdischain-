#!/usr/bin/env python3
"""Verdis Chain Transaction Relay v2.2 - Added governance actions (propose, vote, second, council)."""

import json
import os
import sys
import traceback
from http.server import HTTPServer, BaseHTTPRequestHandler
from substrateinterface import SubstrateInterface, Keypair

substrate = SubstrateInterface(
    url="http://127.0.0.1:9933",
    ss58_format=909,
    auto_discover=True,
    type_registry_preset=None
)

SIGNER = Keypair.create_from_uri("//Charlie")
SIGNER_ADDRESS = SIGNER.ss58_address
print(f"TX Relay v2.2 ready. Signing as: {SIGNER_ADDRESS}")

TOKEN_DECIMALS = 9

def get_signer_balance():
    try:
        result = substrate.query("System", "Account", [SIGNER_ADDRESS])
        if result:
            return int(result.value.get("data", {}).get("free", 0))
    except Exception:
        pass
    return 0

def submit_call(pallet, call_name, params):
    call = substrate.compose_call(pallet, call_name, params)
    extrinsic = substrate.create_signed_extrinsic(call, SIGNER)
    return substrate.submit_extrinsic(extrinsic, wait_for_inclusion=False)

class RelayHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        balance = get_signer_balance()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps({
            "status": "ok", "version": "2.2",
            "signer": SIGNER_ADDRESS,
            "signer_balance": balance,
            "signer_balance_formatted": f"{balance / 10**TOKEN_DECIMALS:,.4f} VRDX" if balance else "0",
            "supported_calls": [
                "system.remark","balances.transfer_allow_death",
                "amm_dex.create_pool","amm_dex.swap","amm_dex.add_liquidity","amm_dex.remove_liquidity",
                "dpos.vote","dpos.register_validator",
                "democracy.propose","democracy.vote","democracy.second",
                "council.propose","council.vote"
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
                if len(words) != 12: self._error("Mnemonic must be exactly 12 words"); return
                try:
                    kp = Keypair.create_from_mnemonic(mnemonic, ss58_format=909)
                    self._success(None, {"address": kp.ss58_address, "public_key": kp.public_key.hex(), "crypto_type": "sr25519", "ss58_prefix": 909})
                except Exception as e: self._error("Address derivation failed: " + str(e))
                return

            if action == "remark":
                remark = body.get("remark", "").encode("utf-8")
                if len(remark) > 256: self._error("Remark too long"); return
                result = submit_call("System", "remark", {"remark": remark})
                self._success(result, {"remark": remark.decode("utf-8")})

            elif action == "transfer":
                dest = body.get("dest", body.get("to", ""))
                amount = int(body.get("amount", body.get("value", 0)))
                if not dest: self._error("Missing destination"); return
                if amount <= 0: self._error("Invalid amount"); return
                if amount > get_signer_balance(): self._error("Insufficient signer balance"); return
                result = submit_call("Balances", "transfer_allow_death", {"dest": dest, "value": amount})
                self._success(result, {"type": "transfer", "dest": dest, "amount": amount})

            elif action == "create_pool":
                token_a = body.get("token_a", "")
                token_b = body.get("token_b", "")
                amount_a = int(body.get("amount_a", 0))
                amount_b = int(body.get("amount_b", 0))
                if not token_a or not token_b: self._error("Missing token_a or token_b"); return
                if amount_a <= 0 or amount_b <= 0: self._error("Invalid amounts"); return
                ta = token_a.encode("utf-8") if isinstance(token_a, str) else bytes(token_a)
                tb = token_b.encode("utf-8") if isinstance(token_b, str) else bytes(token_b)
                total = amount_a + amount_b
                if total > get_signer_balance(): self._error("Insufficient balance for pool"); return
                result = submit_call("AmmDex", "create_pool", {"token_a": ta, "token_b": tb, "amount_a": amount_a, "amount_b": amount_b})
                self._success(result, {"type": "create_pool", "token_a": token_a, "token_b": token_b, "amount_a": amount_a, "amount_b": amount_b})

            elif action == "swap":
                pool_id = int(body.get("pool_id", 0))
                token_in = body.get("token_in", "VRDX")
                amount_in = int(body.get("amount_in", 0))
                min_amount_out = int(body.get("min_amount_out", 0))
                if amount_in <= 0: self._error("Invalid amount_in"); return
                ti = token_in.encode("utf-8") if isinstance(token_in, str) else bytes(token_in)
                if amount_in > get_signer_balance(): self._error("Insufficient balance"); return
                result = submit_call("AmmDex", "swap", {"pool_id": pool_id, "token_in": ti, "amount_in": amount_in, "min_amount_out": min_amount_out})
                self._success(result, {"type": "swap", "pool_id": pool_id, "token_in": token_in, "amount_in": amount_in})

            elif action == "add_liquidity":
                pool_id = int(body.get("pool_id", 0))
                amount_a = int(body.get("amount_a", 0))
                amount_b = int(body.get("amount_b", 0))
                if amount_a <= 0 or amount_b <= 0: self._error("Invalid amounts"); return
                result = submit_call("AmmDex", "add_liquidity", {"pool_id": pool_id, "amount_a": amount_a, "amount_b": amount_b})
                self._success(result, {"type": "add_liquidity", "pool_id": pool_id, "amount_a": amount_a, "amount_b": amount_b})

            elif action == "remove_liquidity":
                pool_id = int(body.get("pool_id", 0))
                lp_amount = int(body.get("lp_amount", 0))
                if lp_amount <= 0: self._error("Invalid LP amount"); return
                result = submit_call("AmmDex", "remove_liquidity", {"pool_id": pool_id, "lp_amount": lp_amount})
                self._success(result, {"type": "remove_liquidity", "pool_id": pool_id, "lp_amount": lp_amount})

            elif action == "vote":
                validator = body.get("validator", "")
                amount = int(body.get("amount", 0))
                if not validator: self._error("Missing validator"); return
                if amount <= 0: self._error("Invalid amount"); return
                result = submit_call("Dpos", "vote", {"validator": validator, "amount": amount})
                self._success(result, {"type": "vote", "validator": validator, "amount": amount})

            elif action == "register_validator":
                green_score = int(body.get("green_score", 3))
                energy_source = body.get("energy_source", "solar")
                es = energy_source.encode("utf-8") if isinstance(energy_source, str) else bytes(energy_source)
                result = submit_call("Dpos", "register_validator", {"green_score": green_score, "energy_source": es})
                self._success(result, {"type": "register_validator", "green_score": green_score, "energy_source": energy_source})

            elif action == "propose":
                # Democracy propose: submit a proposal with a minimum deposit
                proposal_hex = body.get("proposal", "")
                deposit_amount = int(body.get("deposit", 1000 * 10**9))  # default 1000 VRDX
                if not proposal_hex: self._error("Missing proposal"); return
                if deposit_amount <= 0: self._error("Invalid deposit"); return
                # The proposal is a hex-encoded SCALE-encoded RuntimeCall
                # For simplicity, we support system.remark proposals
                if proposal_hex.startswith("0x"):
                    proposal_hex = proposal_hex[2:]
                # Create a remark proposal
                remark_bytes = bytes.fromhex(proposal_hex)
                call = substrate.compose_call("System", "remark", {"remark": remark_bytes})
                result = submit_call("Democracy", "propose", {
                    "proposal": call,
                    "value": deposit_amount
                })
                self._success(result, {"type": "propose", "deposit": deposit_amount})

            elif action == "democracy_vote":
                # Vote on a referendum: index, vote (Aye/Nay), conviction
                ref_index = int(body.get("referendum_index", 0))
                vote_choice = body.get("vote", "aye")  # "aye" or "nay"
                conviction = int(body.get("conviction", 1))  # 0-6 (Locked1x through Locked6x)
                if vote_choice not in ("aye", "nay"): self._error("Vote must be 'aye' or 'nay'"); return
                # Construct the vote
                from substrateinterface.utils.ss58 import ss58_decode
                vote = {"Standard": {"vote": {"aye": vote_choice == "aye", "conviction": conviction}, "balance": get_signer_balance() // 10}}
                result = submit_call("Democracy", "vote", {
                    "ref_index": ref_index,
                    "vote": vote
                })
                self._success(result, {"type": "democracy_vote", "referendum_index": ref_index, "vote": vote_choice, "conviction": conviction})

            elif action == "second":
                # Second a proposal in the public proposal queue
                prop_index = int(body.get("proposal_index", 0))
                seconds_upper = int(body.get("seconds", 1))
                result = submit_call("Democracy", "second", {
                    "proposal": prop_index,
                    "seconds_upper": seconds_upper
                })
                self._success(result, {"type": "second", "proposal_index": prop_index, "seconds_upper": seconds_upper})

            else:
                self._error(f"Unknown action: {action}")
        except Exception as e:
            print(f"[RELAY] Error: {traceback.format_exc()}")
            self._error(str(e))

    def _success(self, result, extra=None):
        response = {"ok": True, "extrinsic_hash": getattr(result, "extrinsic_hash", None), "block_hash": getattr(result, "block_hash", None), "signer": SIGNER_ADDRESS}
        if extra: response.update(extra)
        print(f"[RELAY] TX: {response.get('extrinsic_hash', '?')} - {response.get('type', 'remark')}")
        self.wfile.write(json.dumps(response).encode())

    def _error(self, msg):
        print(f"[RELAY] Error: {msg}")
        self.wfile.write(json.dumps({"ok": False, "error": msg}).encode())

if __name__ == "__main__":
    port = int(os.environ.get("TX_RELAY_PORT", 5001))
    server = HTTPServer(("127.0.0.1", port), RelayHandler)
    print(f"TX Relay v2.2 listening on http://127.0.0.1:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
