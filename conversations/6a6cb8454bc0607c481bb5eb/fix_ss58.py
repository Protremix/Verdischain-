import subprocess

# Read the current API file
result = subprocess.run(
    ["ssh", "-o", "ConnectTimeout=10", "root@91.98.160.145", "cat /opt/verdis-api/verdiscan_api.py"],
    capture_output=True, text=True
)
content = result.stdout

# Fix the SS58 encoding in token_holders: use prefix 42 instead of 909
old_ss58 = '''            # Convert to SS58
            try:
                import base58 as _b58
                ss58_bytes = bytes([909]) + bytes.fromhex(account_hex)
                checksum = _hashlib.blake2b(ss58_bytes, digest_size=64).digest()[:2]
                ss58 = _b58.b58encode(ss58_bytes + checksum).decode()
            except:
                ss58 = "0x" + account_hex[:16] + "...\"'''

new_ss58 = '''            # Convert to SS58 (using network prefix 42 = standard Substrate)
            try:
                account_bytes = bytes.fromhex(account_hex)
                # Check if it's a module account (starts with "modl")
                if account_hex.startswith("6d6f646c"):
                    # Module account - show readable name
                    try:
                        name = account_bytes.split(b'\\x00')[0].decode('ascii', errors='replace')
                        ss58 = f"Module: {name}"
                    except:
                        ss58 = "0x" + account_hex[:16] + "..."
                else:
                    import base58 as _b58
                    ss58_bytes = bytes([42]) + account_bytes
                    checksum = _hashlib.blake2b(ss58_bytes, digest_size=64).digest()[:2]
                    ss58 = _b58.b58encode(ss58_bytes + checksum).decode()
            except:
                ss58 = "0x" + account_hex[:16] + "...\"'''

if old_ss58 in content:
    content = content.replace(old_ss58, new_ss58)
    print("Fixed SS58 encoding in token_holders")
else:
    print("ERROR: old SS58 block not found")

# Also fix in the account_detail endpoint (the one we added earlier)
old_account_ss58 = '''        import base58
        ss58_bytes = base58.b58decode(address)
        # SS58 format: prefix(1 byte) + account(32 bytes) + checksum(2 bytes)
        account_hex = ss58_bytes[1:33].hex()'''

new_account_ss58 = '''        import base58
        ss58_bytes = base58.b58decode(address)
        # SS58 format: prefix(1 byte) + account(32 bytes) + checksum(2 bytes)
        # Works for prefix 42 (standard Substrate)
        account_hex = ss58_bytes[1:33].hex()'''

# This one is already correct (uses the address directly), no change needed

# Write back
proc = subprocess.run(
    ["ssh", "-o", "ConnectTimeout=10", "root@91.98.160.145", "cat > /opt/verdis-api/verdiscan_api.py"],
    input=content,
    capture_output=True,
    text=True
)
print(f"Written: exit {proc.returncode}")
