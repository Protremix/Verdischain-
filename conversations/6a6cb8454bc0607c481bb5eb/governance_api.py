#!/usr/bin/env python3
"""Verdis Chain Governance API — queries democracy, council, and treasury pallets."""

import json
import sys
import traceback
from http.server import HTTPServer, BaseHTTPRequestHandler
from substrateinterface import SubstrateInterface

substrate = SubstrateInterface(
    url="http://127.0.0.1:9933",
    ss58_format=909,
    auto_discover=True,
    type_registry_preset=None
)

DECIMALS = 9

class GovernanceHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        try:
            data = {"referendums": [], "proposals": [], "council": [], "treasury_balance": 0, "treasury_proposals": []}

            # Democracy: public proposals
            try:
                prop_count = substrate.query("Democracy", "PublicPropCount", [])
                count = prop_count.value if prop_count else 0
                for i in range(min(count, 20)):
                    try:
                        prop = substrate.query("Democracy", "PublicProps", [i])
                        if prop and prop.value:
                            p = prop.value
                            # PublicProps is a tuple (prop_index, proposal, proposer)
                            proposer = str(p[2]) if len(p) > 2 else "unknown"
                            # Try to decode the proposal as a remark
                            title = "Proposal #" + str(i)
                            try:
                                if hasattr(p[1], 'value'):
                                    call_data = p[1].value
                                    if isinstance(call_data, dict) and 'remark' in str(call_data):
                                        remark = call_data.get('remark', b'')
                                        if isinstance(remark, (list, bytes)):
                                            title = bytes(remark).decode('utf-8', errors='ignore')[:100]
                            except:
                                pass
                            data["proposals"].append({
                                "index": i,
                                "title": title,
                                "description": "Public proposal via pallet-democracy",
                                "proposer": proposer,
                                "deposit": 1000 * 10**DECIMALS,
                                "seconds": 0
                            })
                    except Exception:
                        pass
            except Exception as e:
                print(f"[GOV] Democracy query error: {e}")

            # Democracy: active referendums
            try:
                ref_count = substrate.query("Democracy", "ReferendumCount", [])
                count = ref_count.value if ref_count else 0
                for i in range(min(count, 20)):
                    try:
                        ref = substrate.query("Democracy", "ReferendumInfoOf", [i])
                        if ref and ref.value:
                            info = ref.value
                            if isinstance(info, dict):
                                end_block = info.get("end", 0)
                                status = "active" if end_block > 0 else "finished"
                                data["referendums"].append({
                                    "index": i,
                                    "title": f"Referendum #{i}",
                                    "description": "On-chain referendum",
                                    "status": status,
                                    "end_block": end_block,
                                    "aye_votes": 0,
                                    "nay_votes": 0,
                                    "aye_percent": 50
                                })
                    except Exception:
                        pass
            except Exception as e:
                print(f"[GOV] Referendum query error: {e}")

            # Council members
            try:
                members = substrate.query("Council", "Members", [])
                if members and members.value:
                    data["council"] = [str(m) for m in members.value]
            except Exception as e:
                print(f"[GOV] Council query error: {e}")

            # Treasury balance
            try:
                treasury_pallet_id = "5FGSigC9HGRKVhB9FiEo4Y3koPsNmBmLJbpXg2mp1hXcS59Y"  # fallback
                # Try to query treasury account
                from substrateinterface.utils.ss58 import ss58_encode
                # Treasury pallet ID account
                try:
                    treasury_account = "5EYCAe5jYEcygU5QwrcnLh17Lq2dE2vqDYwF4wyqyYwd3LYm"  # Common treasury account
                    acct = substrate.query("System", "Account", [treasury_account])
                    if acct and acct.value:
                        data["treasury_balance"] = int(acct.value.get("data", {}).get("free", 0))
                except:
                    pass
            except Exception as e:
                print(f"[GOV] Treasury query error: {e}")

            # Treasury proposals
            try:
                prop_count = substrate.query("Treasury", "ProposalCount", [])
                count = prop_count.value if prop_count else 0
                for i in range(min(count, 20)):
                    try:
                        prop = substrate.query("Treasury", "Proposals", [i])
                        if prop and prop.value:
                            p = prop.value
                            data["treasury_proposals"].append({
                                "index": i,
                                "proposer": str(p.get("proposer", "unknown")),
                                "value": p.get("value", 0),
                                "beneficiary": str(p.get("beneficiary", "unknown")),
                                "bond": p.get("bond", 0)
                            })
                    except Exception:
                        pass
            except Exception as e:
                print(f"[GOV] Treasury proposals error: {e}")

            self.wfile.write(json.dumps(data).encode())

        except Exception as e:
            print(f"[GOV] Error: {traceback.format_exc()}")
            self.wfile.write(json.dumps({"error": str(e), "referendums": [], "proposals": [], "council": [], "treasury_balance": 0, "treasury_proposals": []}).encode())

if __name__ == "__main__":
    port = int(__import__('os').environ.get("GOVERNANCE_API_PORT", "5020"))
    server = HTTPServer(("127.0.0.1", port), GovernanceHandler)
    print(f"Governance API listening on http://127.0.0.1:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
