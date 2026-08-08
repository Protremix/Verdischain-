with open('/opt/verdis-chain-rust/tx_relay_v2.py', 'r') as f:
    lines = f.readlines()

content = ''.join(lines)

# 1. Add derive-address to do_POST (after the action line)
old_action = '''            action = body.get("action", "remark")

            if action == "remark":'''

new_action = '''            action = body.get("action", "remark")

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
                return

            if action == "remark":'''

if old_action in content:
    content = content.replace(old_action, new_action)
    print("Added POST derive-address endpoint")
else:
    print("ERROR: Could not find action line in do_POST")

with open('/opt/verdis-chain-rust/tx_relay_v2.py', 'w') as f:
    f.write(content)

print("Done")
