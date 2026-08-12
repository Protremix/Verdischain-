#!/usr/bin/env python3
"""Fix decode_extrinsic to handle SCALE length prefix + fix tx-relay validator names"""

# Fix the API decoder
api_path = '/opt/verdis-api/verdiscan_api.py'
with open(api_path) as f:
    content = f.read()

# Replace the signed detection logic in decode_extrinsic
# The current code checks first byte for 0x80 flag, but the extrinsic has a SCALE compact length prefix
old_decode = '''    # Remove 0x prefix
    hex_str = ext_bytes[2:] if ext_bytes.startswith("0x") else ext_bytes
    
    # First byte: version + signing flag
    if len(hex_str) < 2:
        return {"index": index, "raw": ext_bytes, "decoded": False}
    
    first_byte = int(hex_str[:2], 16)
    is_signed = (first_byte & 0x80) != 0
    version = first_byte & 0x7f'''

new_decode = '''    # Remove 0x prefix
    hex_str = ext_bytes[2:] if ext_bytes.startswith("0x") else ext_bytes
    
    if len(hex_str) < 4:
        return {"index": index, "raw": ext_bytes, "decoded": False}
    
    # The extrinsic starts with a SCALE compact length prefix
    # Skip it to find the actual version byte
    first_byte_raw = int(hex_str[:2], 16)
    offset = 0  # offset to version byte (after length prefix)
    
    # SCALE compact encoding: check top 2 bits
    if (first_byte_raw & 0xC0) == 0x00:
        # Single-byte mode: length = byte >> 2
        offset = 2  # 1 byte = 2 hex chars
    elif (first_byte_raw & 0xC0) == 0x40:
        # Two-byte mode
        offset = 4  # 2 bytes = 4 hex chars
    elif (first_byte_raw & 0xC0) == 0x80:
        # Four-byte mode
        offset = 8  # 4 bytes = 8 hex chars
    else:
        # Big-integer mode (uncommon)
        offset = 2  # fallback
    
    # Now read the version byte after the length prefix
    if len(hex_str) < offset + 2:
        return {"index": index, "raw": ext_bytes, "decoded": False}
    
    first_byte = int(hex_str[offset:offset+2], 16)
    is_signed = (first_byte & 0x80) != 0
    version = first_byte & 0x7f
    
    # Adjust hex_str to skip the length prefix for further parsing
    hex_str = hex_str[offset:]
    
    # Reset offset since we already stripped the length prefix
    offset = 2  # now points to after the version byte'''

if old_decode in content:
    content = content.replace(old_decode, new_decode, 1)
    print("FIX: decode_extrinsic SCALE length prefix - OK")
else:
    print("FIX: decode_extrinsic - PATTERN NOT FOUND")

# Also fix the "offset = 2" line that comes right after version byte parsing
# The existing code has: offset = 2  # version byte (for unsigned)
# But now we already stripped the length prefix, so offset should still be 2
# Actually the code uses `offset` variable later, let me check...

# The existing code after the signed check has:
# if is_signed:
#     offset = 2  # version byte
# This is fine because we reset offset = 2 above

with open(api_path, 'w') as f:
    f.write(content)

# Now fix the tx-relay validator names
relay_path = '/opt/verdis-chain-rust/tx_relay_v2.py'
with open(relay_path) as f:
    relay_content = f.read()

# Fix the name conversion in the validators handler
old_name = '''                        name_result = substrate.rpc_request("dpos_validatorName", [v_addr])
                        name = name_result.get("result", v_addr[:12] + "...")'''

new_name = '''                        name_result = substrate.rpc_request("dpos_validatorName", [v_addr])
                        name = name_result.get("result", v_addr[:12] + "...")
                        # Convert byte array to string if needed
                        if isinstance(name, list):
                            name = "".join(chr(b) for b in name if isinstance(b, int) and 0 <= b < 256)
                        elif isinstance(name, bytes):
                            name = name.decode("utf-8", errors="replace")'''

if old_name in relay_content:
    relay_content = relay_content.replace(old_name, new_name, 1)
    print("FIX: tx-relay validator names - OK")
else:
    print("FIX: tx-relay validator names - PATTERN NOT FOUND")

with open(relay_path, 'w') as f:
    f.write(relay_content)

print("All fixes saved")
