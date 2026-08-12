import re

with open('/opt/verdis-chain-rust/tx_relay_v3.py', 'r') as f:
    content = f.read()

old_backup = '''        # ===== WALLET EMAIL BACKUP (encrypted client-side, server never sees plaintext) =====
        elif action == "wallet-backup":
            email = body.get("email", "").strip().lower()
            ciphertext = body.get("ciphertext", "")
            salt = body.get("salt", "")
            iv = body.get("iv", "")
            address = body.get("address", "")

            if not email or not ciphertext or not salt or not iv:
                self._error("Missing email, ciphertext, salt, or iv")
                return
            if len(email) > 256 or len(ciphertext) > 4096:
                self._error("Payload too large")
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

            self._success({'backup': backup})'''

new_backup = '''        # ===== WALLET EMAIL BACKUP (encrypted client-side, server never sees plaintext) =====
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

            self._success({'backup': backup})'''

if old_backup not in content:
    print("ERROR: old_backup block not found exactly, aborting")
else:
    content = content.replace(old_backup, new_backup)
    with open('/opt/verdis-chain-rust/tx_relay_v3.py', 'w') as f:
        f.write(content)
    print("Patch applied successfully")
