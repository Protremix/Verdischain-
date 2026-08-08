import subprocess

# Read the current API file
result = subprocess.run(
    ["ssh", "-o", "ConnectTimeout=10", "root@91.98.160.145", "cat /opt/verdis-api/verdiscan_api.py"],
    capture_output=True, text=True
)
content = result.stdout

old_holders = '''@app.get("/api/v1/token/holders")
async def token_holders():
    holders = sorted(VALIDATORS, key=lambda v: v["stake"], reverse=True)
    return {
        "success": True,
        "count": len(holders),
        "data": [{"address": v["address"], "name": v["name"], "balance": v["stake"]} for v in holders],
    }'''

new_holders = '''@app.get("/api/v1/token/holders")
async def token_holders():
    """Query all token holders from System::Account storage via state_getKeysPaged"""
    DEC = 9
    prefix = _twox_128(b"System") + _twox_128(b"Account")
    prefix_hex = "0x" + prefix.hex()

    all_holders = []
    start_key = prefix_hex
    page_size = 1000

    while True:
        keys_result = await rpc("state_getKeysPaged", [prefix_hex, page_size, start_key])
        if not keys_result:
            break
        for k in keys_result:
            val = await rpc("state_getStorage", [k])
            if not val or val == "null":
                continue
            raw = bytes.fromhex(val[2:] if val.startswith("0x") else val)
            if len(raw) < 48:
                continue
            free = int.from_bytes(raw[16:32], "little")
            reserved = int.from_bytes(raw[32:48], "little")
            total = free + reserved
            if total == 0:
                continue
            # Extract account from key (Blake2_128Concat: prefix + blake2_128(16) + account(32))
            account_hex = k[-64:]
            # Convert to SS58
            try:
                import base58 as _b58
                ss58_bytes = bytes([909]) + bytes.fromhex(account_hex)
                checksum = _hashlib.blake2b(ss58_bytes, digest_size=64).digest()[:2]
                ss58 = _b58.b58encode(ss58_bytes + checksum).decode()
            except:
                ss58 = "0x" + account_hex[:16] + "..."

            # Check if validator
            vname = None
            try:
                vals = await rpc("dpos_allValidators", [])
                if ss58 in (vals or []):
                    name_res = await rpc("dpos_validatorName", [ss58])
                    if name_res and isinstance(name_res, list):
                        vname = "".join(chr(b) for b in name_res).strip()
                    elif name_res and isinstance(name_res, str):
                        vname = name_res.strip()
            except:
                pass

            all_holders.append({
                "address": ss58,
                "balance": total,
                "balance_formatted": f"{total / 10**DEC:,.4f} VRDX",
                "free": free,
                "free_formatted": f"{free / 10**DEC:,.4f} VRDX",
                "reserved": reserved,
                "reserved_formatted": f"{reserved / 10**DEC:,.4f} VRDX",
                "is_validator": vname is not None,
                "name": vname,
            })
        start_key = keys_result[-1]
        if len(keys_result) < page_size:
            break

    all_holders.sort(key=lambda x: x["balance"], reverse=True)
    return {"success": True, "count": len(all_holders), "data": all_holders}'''

if old_holders in content:
    content = content.replace(old_holders, new_holders)
    print("Replaced token holders endpoint")
else:
    print("ERROR: old endpoint not found")

# Write back
proc = subprocess.run(
    ["ssh", "-o", "ConnectTimeout=10", "root@91.98.160.145", "cat > /opt/verdis-api/verdiscan_api.py"],
    input=content,
    capture_output=True,
    text=True
)
print(f"Written: exit {proc.returncode}")
if proc.stderr:
    print(f"Stderr: {proc.stderr[:200]}")
