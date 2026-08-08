#!/usr/bin/env python3
"""Verdis Chain Governance API - provides on-chain governance data as JSON."""
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from substrateinterface import SubstrateInterface

substrate = SubstrateInterface(
    url="http://127.0.0.1:9933",
    ss58_format=909,
    auto_discover=True,
    type_registry_preset=None
)

class GovernanceHandler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self._cors()
        self.end_headers()

        result = {"governance": {}}

        try:
            # Council members
            council = substrate.query("Council", "Members")
            members = []
            if council and council.value:
                for m in council.value:
                    addr = str(m) if isinstance(m, str) else str(m)
                    members.append({"address": addr, "short": addr[:10] + "..." + addr[-6:]})
            result["governance"]["council"] = {"members": members, "count": len(members)}
        except Exception as e:
            result["governance"]["council"] = {"error": str(e), "members": [], "count": 0}

        try:
            # Democracy
            prop_count = substrate.query("Democracy", "PublicPropCount")
            ref_count = substrate.query("Democracy", "ReferendumCount")
            result["governance"]["democracy"] = {
                "publicPropCount": int(prop_count.value) if prop_count else 0,
                "referendumCount": int(ref_count.value) if ref_count else 0
            }
        except Exception as e:
            result["governance"]["democracy"] = {"error": str(e), "publicPropCount": 0, "referendumCount": 0}

        try:
            # Treasury
            prop_count = substrate.query("Treasury", "ProposalCount")
            result["governance"]["treasury"] = {
                "proposalCount": int(prop_count.value) if prop_count else 0
            }
        except Exception as e:
            result["governance"]["treasury"] = {"error": str(e), "proposalCount": 0}

        try:
            # Sudo
            sudo_key = substrate.query("Sudo", "Key")
            addr = str(sudo_key.value) if sudo_key and sudo_key.value else "None"
            result["governance"]["sudo"] = {
                "key": addr,
                "short": addr[:10] + "..." + addr[-6:] if len(addr) > 20 else addr
            }
        except Exception as e:
            result["governance"]["sudo"] = {"error": str(e)}

        try:
            # Session validators (active)
            sv = substrate.query("Session", "Validators")
            vals = []
            if sv and sv.value:
                for v in sv.value:
                    addr = str(v) if isinstance(v, str) else str(v)
                    vals.append(addr)
            result["governance"]["sessionValidators"] = vals
        except Exception as e:
            result["governance"]["sessionValidators"] = []

        try:
            # All DPOS validators
            all_vals = substrate.query("Dpos", "AllValidators")
            result["governance"]["totalValidators"] = len(all_vals.value) if all_vals else 0
        except Exception as e:
            result["governance"]["totalValidators"] = 0

        # Council proposals
        try:
            proposals = substrate.query("Council", "Proposals")
            prop_list = []
            if proposals and proposals.value:
                for p in proposals.value:
                    prop_list.append(str(p))
            result["governance"]["councilProposals"] = prop_list
        except Exception as e:
            result["governance"]["councilProposals"] = []

        # Active referenda details
        try:
            ref_count_val = int(substrate.query("Democracy", "ReferendumCount").value) if substrate.query("Democracy", "ReferendumCount") else 0
            referenda = []
            for i in range(ref_count_val):
                ref_info = substrate.query("Democracy", "ReferendumInfoOf", [i])
                if ref_info and ref_info.value:
                    referenda.append({"index": i, "info": str(ref_info.value)[:200]})
            result["governance"]["referenda"] = referenda
        except Exception as e:
            result["governance"]["referenda"] = []

        self.wfile.write(json.dumps(result).encode())

if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", 4401), GovernanceHandler)
    print("Governance API ready on port 4401")
    server.serve_forever()
