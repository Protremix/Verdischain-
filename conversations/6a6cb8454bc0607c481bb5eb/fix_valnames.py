#!/usr/bin/env python3
"""Fix validator name byte array decoding in tx_relay_v3.py"""

FILE = '/opt/verdis-chain-rust/tx_relay_v3.py'

with open(FILE, 'r') as f:
    code = f.read()

# Fix: decode byte array names to strings
old = '        n = name.get("result", "")\n        g = green.get("result", 0)\n        if isinstance(s, dict):\n            s = s.get("stake", 0) if "stake" in s else s.get("amount", 0)\n        result.append({\n            "address": v_addr,\n            "stake": s,\n            "name": n if n else "Unknown",\n            "greenScore": g,\n            "isActive": v_addr in active_set,\n        })'

new = '        n = name.get("result", "")\n        g = green.get("result", 0)\n        if isinstance(s, dict):\n            s = s.get("stake", 0) if "stake" in s else s.get("amount", 0)\n        # Decode byte array names to string (RPC returns [86, 97, ...] not "Validator21")\n        if isinstance(n, list):\n            n = "".join(chr(b) for b in n if isinstance(b, int) and 32 <= b < 127)\n        if not n:\n            n = "Unknown"\n        result.append({\n            "address": v_addr,\n            "stake": s,\n            "name": n,\n            "greenScore": g,\n            "isActive": v_addr in active_set,\n        })'

if old in code:
    code = code.replace(old, new)
    print("OK: Fixed validator name decoding")
else:
    print("WARN: exact match not found, trying broader search...")
    # Try to find and replace just the name line
    old_line = '"name": n if n else "Unknown",'
    new_line = '"name": "".join(chr(b) for b in n if isinstance(b, int) and 32 <= b < 127) if isinstance(n, list) else (n if n else "Unknown"),'
    if old_line in code:
        code = code.replace(old_line, new_line)
        print("OK: Fixed validator name (line-level)")
    else:
        print("FAIL: Could not find name line")

with open(FILE, 'w') as f:
    f.write(code)
