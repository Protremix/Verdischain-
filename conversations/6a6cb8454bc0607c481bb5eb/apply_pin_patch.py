#!/usr/bin/env python3
"""
Apply PIN security patch to tx_relay_v3.py:
1. Add PIN store imports and functions at top
2. Replace wallet-recover handler to require PIN
3. Add pin-register, pin-verify, pin-status handlers
"""

import re

TX_RELAY_PATH = '/opt/verdis-chain-rust/tx_relay_v3.py'

with open(TX_RELAY_PATH, 'r') as f:
    content = f.read()

# 1. Add PIN security imports after the WALLET_BACKUPS_FILE line
pin_imports = '''
# ===== PIN SECURITY (server-side PIN verification) =====
import hashlib
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
    if pin_hash == entry['pin_hash']:
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

'''

# Insert after the get_backup function (which ends before the RelayHandler class)
# Find "def get_backup" and its end
backup_end_marker = "    backups = load_backups()\n    return backups.get(email.lower())"
if backup_end_marker in content:
    content = content.replace(backup_end_marker, backup_end_marker + "\n" + pin_imports)
    print("[OK] PIN security functions added after get_backup()")
else:
    # Try alternative: insert before class RelayHandler
    class_marker = "class RelayHandler"
    if class_marker in content:
        content = content.replace(class_marker, pin_imports + "\n" + class_marker)
        print("[OK] PIN security functions added before RelayHandler class")
    else:
        print("[ERROR] Could not find insertion point")
        exit(1)

# 2. Replace the wallet-recover handler to require PIN
old_recover = '''        elif action == "wallet-recover":
            email = body.get("email", "").strip().lower()
            if not email:
                self._error("Missing email")
                return

            backup = get_backup(email)
            if not backup:
                self._error("No wallet backup found for this email", 404)
                return
            self._success({'backup': backup})'''

new_recover = '''        elif action == "wallet-recover":
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

            # Verify PIN before returning backup
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
                self._error(f"Status check failed: {str(e)}")'''

if old_recover in content:
    content = content.replace(old_recover, new_recover)
    print("[OK] wallet-recover handler updated to require PIN")
else:
    print("[WARN] Could not find exact wallet-recover handler, trying regex")
    # Try to find and replace using regex
    pattern = r'elif action == "wallet-recover":.*?self\._success\(\{\'backup\': backup\}\)'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        content = content[:match.start()] + new_recover + content[match.end():]
        print("[OK] wallet-recover handler updated via regex")
    else:
        print("[ERROR] Could not find wallet-recover handler")
        exit(1)

# 3. Update the supported actions message
old_actions = "Supported: balance, chain-info, validators, dex-pools, submit-extrinsic, estimate-fee, wallet-backup, wallet-recover"
new_actions = "Supported: balance, chain-info, validators, dex-pools, submit-extrinsic, estimate-fee, wallet-backup, wallet-recover, pin-register, pin-verify, pin-status"
content = content.replace(old_actions, new_actions)
print("[OK] Updated supported actions list")

# Write the patched file
with open(TX_RELAY_PATH, 'w') as f:
    f.write(content)
print("\n[DONE] tx_relay_v3.py patched successfully")
