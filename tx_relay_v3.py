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
NODE_URL = os.environ.get("VERDIS_NODE_URL", "http://127.0.0.1:9934")
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


# ===== Wallet Email Backup Storage =====
WALLET_BACKUPS_FILE = os.environ.get('WALLET_BACKUPS_FILE', '/opt/verdis-chain-rust/wallet_backups.json')
backup_lock = threading.Lock()

def load_backups():
    """Load email→encrypted-wallet mappings from file."""
    try:
        with open(WALLET_BACKUPS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_backup(email, encrypted_data):
    """Store encrypted wallet blob for an email."""
    with backup_lock:
        backups = load_backups()
        backups[email.lower()] = {
            'ciphertext': encrypted_data.get('ciphertext', ''),
            'salt': encrypted_data.get('salt', ''),
            'iv': encrypted_data.get('iv', ''),
            'address': encrypted_data.get('address', ''),
            'updated': time.time(),
        }
        with open(WALLET_BACKUPS_FILE, 'w') as f:
            json.dump(backups, f, indent=2)

def get_backup(email):
    """Retrieve encrypted wallet blob for an email."""
    backups = load_backups()
    return backups.get(email.lower())

# ===== PIN SECURITY (server-side PIN verification) =====
import hashlib
import hmac
import secrets as _secrets

PIN_STORE_FILE = os.environ.get('PIN_STORE_FILE', '/opt/verdis-chain-rust/wallet_pin_store.json')
pin_lock = threading.Lock()
MAX_PIN_ATTEMPTS = 5
LOCKOUT_DURATION = 900  # 15 minutes

def load_pin_store():
    try:
        with open(PIN_STORE_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_pin_store(store):
    with pin_lock:
        with open(PIN_STORE_FILE, 'w') as f:
            json.dump(store, f, indent=2)

def hash_pin(address, pin, salt=None):
    if salt is None:
        salt = _secrets.token_hex(16)
    combined = f"{address.lower()}:{pin}:{salt}"
    h = hashlib.sha256(combined.encode()).hexdigest()
    for _ in range(99999):
        h = hashlib.sha256(h.encode()).hexdigest()
    return h, salt

def register_pin(address, pin):
    store = load_pin_store()
    pin_hash, salt = hash_pin(address, pin)
    store[address.lower()] = {
        'pin_hash': pin_hash,
        'salt': salt,
        'failed_attempts': 0,
        'locked_until': 0,
        'created_at': time.time(),
        'updated_at': time.time(),
    }
    save_pin_store(store)
    return True

def verify_pin(address, pin):
    store = load_pin_store()
    addr_key = address.lower()
    if addr_key not in store:
        return True, "no_pin_registered", MAX_PIN_ATTEMPTS
    entry = store[addr_key]
    now = time.time()
    if entry.get('locked_until', 0) > now:
        remaining = int(entry['locked_until'] - now)
        return False, f"locked:{remaining}", 0
    pin_hash, _ = hash_pin(address, pin, entry['salt'])
    if hmac.compare_digest(pin_hash, entry['pin_hash']):
        entry['failed_attempts'] = 0
        entry['locked_until'] = 0
        entry['updated_at'] = now
        store[addr_key] = entry
        save_pin_store(store)
        return True, "verified", MAX_PIN_ATTEMPTS
    entry['failed_attempts'] = entry.get('failed_attempts', 0) + 1
    attempts_remaining = MAX_PIN_ATTEMPTS - entry['failed_attempts']
    if entry['failed_attempts'] >= MAX_PIN_ATTEMPTS:
        entry['locked_until'] = now + LOCKOUT_DURATION
        entry['failed_attempts'] = 0
        store[addr_key] = entry
        save_pin_store(store)
        return False, f"locked:{LOCKOUT_DURATION}", 0
    store[addr_key] = entry
    save_pin_store(store)
    return False, "wrong_pin", attempts_remaining

def get_pin_status(address):
    store = load_pin_store()
    addr_key = address.lower()
    if addr_key not in store:
        return {'has_pin': False, 'locked': False}
    entry = store[addr_key]
    now = time.time()
    locked = entry.get('locked_until', 0) > now
    return {
        'has_pin': True,
        'locked': locked,
        'locked_remaining': int(entry.get('locked_until', 0) - now) if locked else 0,
        'created_at': entry.get('created_at', 0),
    }



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
    """Get chain health and properties — formatted for wallet/clients."""
    health = substrate.rpc_request("system_health", [])
    chain = substrate.rpc_request("system_chain", [])
    props = substrate.rpc_request("system_properties", [])
    header = substrate.rpc_request("chain_getHeader", [])
    runtime = substrate.rpc_request("state_getRuntimeVersion", [])

    h = health.get("result", {})
    p = props.get("result", {})
    hdr = header.get("result", {})
    rt = runtime.get("result", {})

    block_num = int(hdr.get("number", "0x0"), 16) if hdr.get("number") else 0

    return {
        "chainName": chain.get("result", "Verdis"),
        "tokenSymbol": p.get("tokenSymbol", "VRDX"),
        "decimals": p.get("tokenDecimals", 9),
        "ss58Format": p.get("ss58Format", 909),
        "blockNumber": block_num,
        "blockHash": hdr.get("hash", ""),
        "peerCount": h.get("peers", 0),
        "isSyncing": h.get("isSyncing", False),
        "specName": rt.get("specName", "verdis-chain"),
        "specVersion": rt.get("specVersion", 0),
        "runtimeVersion": rt.get("transactionVersion", 0),
    }

def get_validators():
    """Get all validators with stakes, names, and green scores."""
    validators = substrate.rpc_request("dpos_allValidators", [])
    v_list = validators.get("result", [])
    active_vals = substrate.rpc_request("dpos_activeValidators", [])
    active_set = set(active_vals.get("result", []))
    result = []
    for v_addr in v_list:
        stake = substrate.rpc_request("dpos_validatorStake", [v_addr])
        name = substrate.rpc_request("dpos_validatorName", [v_addr])
        green = substrate.rpc_request("eco_getGreenScore", [v_addr])
        s = stake.get("result", 0)
        n = name.get("result", "")
        g = green.get("result", 0)
        if isinstance(s, dict):
            s = s.get("stake", 0) if "stake" in s else s.get("amount", 0)
        # Decode byte array names to string (RPC returns [86, 97, ...] not "Validator21")
        if isinstance(n, list):
            n = "".join(chr(b) for b in n if isinstance(b, int) and 32 <= b < 127)
        if not n:
            n = "Unknown"
        result.append({
            "address": v_addr,
            "stake": s,
            "name": n,
            "greenScore": g,
            "isActive": v_addr in active_set,
        })
    return result


def get_dex_pools():
    """Get all DEX pools — getAllPools returns full data, no need for getPool calls."""
    pools = substrate.rpc_request("amm_dex_getAllPools", [])
    pool_list = pools.get("result", [])
    # Convert byte arrays to readable token names
    for pool in pool_list:
        if isinstance(pool, dict):
            ta = pool.get("token_a", [])
            tb = pool.get("token_b", [])
            pool["tokenA"] = "".join(chr(b) for b in ta) if isinstance(ta, list) else str(ta)
            pool["tokenB"] = "".join(chr(b) for b in tb) if isinstance(tb, list) else str(tb)
            pool["reserveA"] = pool.get("reserve_a", 0)
            pool["reserveB"] = pool.get("reserve_b", 0)
            pool["totalLP"] = pool.get("total_lp", 0)
            pool["feeNumerator"] = pool.get("fee_numerator", 3)
            pool["feeDenominator"] = pool.get("fee_denominator", 1000)
    return pool_list

# ===== Extrinsic Validation =====
MAX_EXTRINSIC_SIZE = 256 * 1024  # 256KB max
submitted_tx_cache = set()
cache_lock = threading.Lock()

def validate_extrinsic(extrinsic_hex):
    """Validate a pre-signed extrinsic before submitting to node."""
    if not extrinsic_hex:
        raise ValueError("Missing extrinsic hex")
    if not extrinsic_hex.startswith("0x"):
        raise ValueError("Extrinsic must be hex-encoded (0x...)")

    # Size limit (DoS protection)
    raw_hex = extrinsic_hex[2:]
    if len(raw_hex) / 2 > MAX_EXTRINSIC_SIZE:
        raise ValueError(f"Extrinsic too large: {len(raw_hex) / 2} bytes (max {MAX_EXTRINSIC_SIZE})")

    # Replay protection — reject duplicate submissions
    ext_hash = hex(abs(hash(extrinsic_hex)))[2:]  # Quick hash for dedup
    with cache_lock:
        if ext_hash in submitted_tx_cache:
            raise ValueError("Duplicate extrinsic — already submitted")
        # Keep cache size bounded
        if len(submitted_tx_cache) > 10000:
            submitted_tx_cache.clear()
        submitted_tx_cache.add(ext_hash)

    # Basic format validation: minimum length for a signed extrinsic
    # (version byte + signature + signer + era + nonce + tip + call)
    min_len = (1 + 64 + 32 + 1 + 2 + 1 + 2) * 2  # ~103 hex chars
    if len(raw_hex) < min_len:
        raise ValueError(f"Extrinsic too short: {len(raw_hex)} hex chars (min {min_len})")

    # Verify it's a signed extrinsic (version byte 0x84 = signed, 0x80 = unsigned)
    try:
        version_byte = int(raw_hex[:2], 16)
        if not (version_byte & 0x80):
            raise ValueError("Extrinsic must be signed (bit 7 must be set)")
    except ValueError:
        raise ValueError("Invalid extrinsic version byte")

    return True


def submit_signed_extrinsic(extrinsic_hex):
    """Validate and submit a pre-signed extrinsic to the node. NO signing on server."""
    validate_extrinsic(extrinsic_hex)  # Throws on invalid

    result = substrate.rpc_request("author_submitExtrinsic", [extrinsic_hex])
    tx_hash = result.get("result", "")
    if not tx_hash:
        raise ValueError("Node rejected extrinsic: " + str(result.get("error", "unknown")))
    return tx_hash

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

        # ===== WALLET EMAIL BACKUP (encrypted client-side, server never sees plaintext) =====
        # SECURITY: backup is only accepted if the wallet already has a PIN registered
        # AND the caller proves knowledge of that exact PIN. This closes the bypass where
        # an email backup could exist for an address with no registered PIN, which would
        # let wallet-recover accept ANY pin (verify_pin returns True when unregistered).
        elif action == "wallet-backup":
            email = body.get("email", "").strip().lower()
            ciphertext = body.get("ciphertext", "")
            salt = body.get("salt", "")
            iv = body.get("iv", "")
            address = body.get("address", "").strip()
            pin = body.get("pin", "").strip()

            if not email or not ciphertext or not salt or not iv or not address:
                self._error("Missing email, ciphertext, salt, iv, or address")
                return
            if len(email) > 256 or len(ciphertext) > 4096:
                self._error("Payload too large")
                return
            if not pin or len(pin) < 4 or len(pin) > 6 or not pin.isdigit():
                self._error("A valid wallet PIN (4-6 digits) is required to create an email backup")
                return

            # Require a PIN to already be registered for this address, and require it to match.
            status = get_pin_status(address)
            if not status.get('has_pin'):
                self._error("This wallet has no PIN registered yet. Set your PIN first, then enable email recovery.", 403)
                return

            success, message, remaining = verify_pin(address, pin)
            if not success:
                if message.startswith("locked:"):
                    seconds = int(message.split(":")[1])
                    self._error(f"Too many attempts. Locked for {seconds}s.", 429)
                else:
                    self._error(f"Wrong PIN. {remaining} attempts remaining.", 403)
                return

            try:
                save_backup(email, {
                    'ciphertext': ciphertext,
                    'salt': salt,
                    'iv': iv,
                    'address': address,
                })
                self._success({'email': email, 'saved': True})
            except Exception as e:
                self._error(f"Backup failed: {str(e)}")

        elif action == "wallet-recover":
            email = body.get("email", "").strip().lower()
            pin = body.get("pin", "").strip()
            if not email:
                self._error("Missing email")
                return
            if not pin or len(pin) < 4 or not pin.isdigit():
                self._error("PIN is required for wallet recovery (4-6 digits)")
                return

            backup = get_backup(email)
            if not backup:
                self._error("No wallet backup found for this email", 404)
                return

            # Verify PIN before returning backup.
            # SECURITY: recovery is only possible if a PIN is registered for this address.
            # We never silently allow recovery for an address with no registered PIN —
            # that bypass previously let ANY pin succeed for such addresses.
            addr = backup.get("address", "")
            if not addr:
                self._error("Backup is missing wallet address — cannot verify PIN. Recovery denied.", 403)
                return

            status = get_pin_status(addr)
            if not status.get('has_pin'):
                self._error("No PIN is registered for this wallet. Recovery cannot proceed without your original PIN.", 403)
                return

            success, message, remaining = verify_pin(addr, pin)
            if not success:
                if message.startswith("locked:"):
                    seconds = int(message.split(":")[1])
                    self._error(f"Too many attempts. Locked for {seconds}s.", 429)
                else:
                    self._error(f"Wrong PIN. {remaining} attempts remaining.", 403)
                return

            self._success({'backup': backup})

        # ===== PIN SECURITY ENDPOINTS =====
        elif action == "pin-register":
            address = body.get("address", "").strip()
            pin = body.get("pin", "").strip()
            if not address or not pin:
                self._error("Missing address or PIN")
                return
            if len(pin) < 4 or len(pin) > 6 or not pin.isdigit():
                self._error("PIN must be 4-6 digits")
                return
            if len(address) > 64:
                self._error("Invalid address")
                return
            try:
                register_pin(address, pin)
                self._success({"registered": True, "address": address})
            except Exception as e:
                self._error(f"PIN registration failed: {str(e)}")

        elif action == "pin-verify":
            address = body.get("address", "").strip()
            pin = body.get("pin", "").strip()
            if not address or not pin:
                self._error("Missing address or PIN")
                return
            if len(pin) < 4 or len(pin) > 6 or not pin.isdigit():
                self._error("PIN must be 4-6 digits")
                return
            try:
                success, message, remaining = verify_pin(address, pin)
                if success:
                    self._success({"verified": True, "message": message, "attempts_remaining": remaining})
                else:
                    if message.startswith("locked:"):
                        seconds = int(message.split(":")[1])
                        self._error(f"Too many attempts. Locked for {seconds}s.", 429)
                    else:
                        self._error(f"Wrong PIN. {remaining} attempts remaining.", 403)
            except Exception as e:
                self._error(f"PIN verification failed: {str(e)}")

        elif action == "pin-status":
            address = body.get("address", "").strip()
            if not address:
                self._error("Missing address")
                return
            try:
                status = get_pin_status(address)
                self._success(status)
            except Exception as e:
                self._error(f"Status check failed: {str(e)}")

        else:
            self._error(f"Unknown action: {action}. Supported: balance, chain-info, validators, dex-pools, submit-extrinsic, estimate-fee, wallet-backup, wallet-recover, pin-register, pin-verify, pin-status")

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
