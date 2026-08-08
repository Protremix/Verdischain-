with open('/opt/verdis-chain-rust/tx_relay_v2.py', 'r') as f:
    content = f.read()

# Fix the derive-address _success call to use None as result and dict as extra
old = 'self._success({"address": kp.ss58_address, "public_key": kp.public_key.hex(), "crypto_type": "sr25519", "ss58_prefix": 909})'
new = 'self._success(None, {"address": kp.ss58_address, "public_key": kp.public_key.hex(), "crypto_type": "sr25519", "ss58_prefix": 909})'

if old in content:
    content = content.replace(old, new)
    print("Fixed _success call")
else:
    print("Pattern not found")

with open('/opt/verdis-chain-rust/tx_relay_v2.py', 'w') as f:
    f.write(content)
