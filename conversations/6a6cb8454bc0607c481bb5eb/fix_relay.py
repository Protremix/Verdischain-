import sys

with open('/opt/verdis-chain-rust/tx_relay_v2.py', 'r') as f:
    lines = f.readlines()

content = ''.join(lines)

# Find do_GET and add derive-address endpoint
old_get = '''    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        if self.path == "/health":
            self._success({"status": "ok", "signer": SIGNER_ADDRESS})'''

new_get = '''    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        if self.path == "/health":
            self._success({"status": "ok", "signer": SIGNER_ADDRESS})
        elif self.path.startswith("/derive-address"):
            from urllib.parse import urlparse, parse_qs
            params = parse_qs(urlparse(self.path).query)
            mnemonic = params.get("mnemonic", [""])[0]
            if not mnemonic or len(mnemonic.split()) != 12:
                self._error("Valid 12-word mnemonic required")
                return
            try:
                kp = Keypair.create_from_mnemonic(mnemonic, ss58_format=909)
                self._success({"address": kp.ss58_address, "public_key": kp.public_key.hex(), "crypto_type": "sr25519", "ss58_prefix": 909})
            except Exception as e:
                self._error("Address derivation failed: " + str(e))'''

if old_get in content:
    content = content.replace(old_get, new_get)
    print("Added GET /derive-address endpoint")
else:
    print("WARNING: Could not find do_GET to patch")

# Add POST derive-address
old_post = '''    def do_POST(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        try:
            body = json.loads(self.rfi.read(int(self.headers.get("Content-Length", 0))))
            action = body.get("action", "remark")'''

new_post = '''    def do_POST(self):
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
                    self._success({"address": kp.ss58_address, "public_key": kp.public_key.hex(), "crypto_type": "sr25519", "ss58_prefix": 909})
                except Exception as e:
                    self._error("Address derivation failed: " + str(e))
                return'''

if old_post in content:
    content = content.replace(old_post, new_post)
    print("Added POST /derive-address endpoint")
else:
    print("WARNING: Could not find do_POST to patch")

with open('/opt/verdis-chain-rust/tx_relay_v2.py', 'w') as f:
    f.write(content)

print("TX Relay updated successfully")
