#!/usr/bin/env python3
"""
PIN Security Patch for TX Relay v3
Adds server-side PIN registration, verification, and rate limiting.
The server NEVER stores the actual PIN — only a salted hash.
"""

import json
import time
import hashlib
import secrets
import threading
import os

# ===== PIN Security Storage =====
PIN_STORE_FILE = os.environ.get('PIN_STORE_FILE', '/opt/verdis-chain-rust/wallet_pin_store.json')
pin_lock = threading.Lock()

# Rate limiting
MAX_PIN_ATTEMPTS = 5
LOCKOUT_DURATION = 900  # 15 minutes

def load_pin_store():
    """Load address → pin_hash mappings."""
    try:
        with open(PIN_STORE_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_pin_store(store):
    """Save pin store to file."""
    with pin_lock:
        with open(PIN_STORE_FILE, 'w') as f:
            json.dump(store, f, indent=2)

def hash_pin(address, pin, salt=None):
    """Create a salted hash of address+pin. Returns (hash_hex, salt_hex)."""
    if salt is None:
        salt = secrets.token_hex(16)
    # PBKDF2-like: 100k iterations of SHA256
    combined = f"{address.lower()}:{pin}:{salt}"
    h = hashlib.sha256(combined.encode()).hexdigest()
    for _ in range(99999):
        h = hashlib.sha256(h.encode()).hexdigest()
    return h, salt

def register_pin(address, pin):
    """Register a PIN for a wallet address. Overwrites if exists (re-PIN)."""
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
    """
    Verify a PIN against stored hash.
    Returns (success: bool, message: str, attempts_remaining: int)
    """
    store = load_pin_store()
    addr_key = address.lower()

    # Check if address has a registered PIN
    if addr_key not in store:
        # No PIN registered — this is a new wallet, allow import
        return True, "no_pin_registered", MAX_PIN_ATTEMPTS

    entry = store[addr_key]

    # Check lockout
    now = time.time()
    if entry.get('locked_until', 0) > now:
        remaining = int(entry['locked_until'] - now)
        return False, f"locked:{remaining}", 0

    # Verify PIN
    pin_hash, _ = hash_pin(address, pin, entry['salt'])
    if pin_hash == entry['pin_hash']:
        # Reset failed attempts on success
        entry['failed_attempts'] = 0
        entry['locked_until'] = 0
        entry['updated_at'] = now
        store[addr_key] = entry
        save_pin_store(store)
        return True, "verified", MAX_PIN_ATTEMPTS

    # Failed attempt
    entry['failed_attempts'] = entry.get('failed_attempts', 0) + 1
    attempts_remaining = MAX_PIN_ATTEMPTS - entry['failed_attempts']

    if entry['failed_attempts'] >= MAX_PIN_ATTEMPTS:
        entry['locked_until'] = now + LOCKOUT_DURATION
        entry['failed_attempts'] = 0  # Reset after lockout
        store[addr_key] = entry
        save_pin_store(store)
        return False, f"locked:{LOCKOUT_DURATION}", 0

    store[addr_key] = entry
    save_pin_store(store)
    return False, "wrong_pin", attempts_remaining

def get_pin_status(address):
    """Check if a PIN is registered for an address."""
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


# ===== Patch instructions for tx_relay_v3.py =====
# Add these actions to the handle_post method:

PIN_ACTIONS_CODE = '''
        # ===== PIN SECURITY (server-side PIN verification) =====
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
                    status_code = 403
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

        elif action == "wallet-recover":
            email = body.get("email", "").strip().lower()
            pin = body.get("pin", "").strip()  # NEW: PIN required for recovery
            if not email:
                self._error("Missing email")
                return
            # NEW: Require PIN for recovery
            if not pin or len(pin) < 4 or not pin.isdigit():
                self._error("PIN is required for wallet recovery (4-6 digits)")
                return

            backup = get_backup(email)
            if not backup:
                self._error("No wallet backup found for this email", 404)
                return

            # NEW: Verify PIN before returning backup
            addr = backup.get("address", "")
            if addr:
                success, message, remaining = verify_pin(addr, pin)
                if not success:
                    if message.startswith("locked:"):
                        seconds = int(message.split(":")[1])
                        self._error(f"Too many attempts. Locked for {seconds}s.", 429)
                    else:
                        self._error(f"Wrong PIN. {remaining} attempts remaining.", 403)
                    return

            self._success({'backup': backup})
'''

if __name__ == "__main__":
    print("PIN Security Patch - ready to apply to tx_relay_v3.py")
    print(PIN_ACTIONS_CODE)
