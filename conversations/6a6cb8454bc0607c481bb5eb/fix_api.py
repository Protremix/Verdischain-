import xxhash
import struct
import hashlib

# Read the existing API file
import subprocess
result = subprocess.run(
    ["ssh", "-o", "ConnectTimeout=10", "root@91.98.160.145", "cat /opt/verdis-api/verdiscan_api.py"],
    capture_output=True, text=True
)
content = result.stdout

# 1. Fix RPC port from 9948 to 9933
content = content.replace("RPC_URL = \"http://127.0.0.1:9948\"", "RPC_URL = \"http://127.0.0.1:9933\"")

# 2. Add twox_128 and blake2_128 helper functions after the imports
helper_code = '''
# --- Storage Key Helpers ---
import xxhash as _xxhash
import struct as _struct
import hashlib as _hashlib

def _twox_128(data: bytes) -> bytes:
    """Substrate twox_128 hash"""
    h0 = _xxhash.xxh64(data, seed=0).intdigest()
    h1 = _xxhash.xxh64(data, seed=1).intdigest()
    return _struct.pack("<Q", h0) + _struct.pack("<Q", h1)

def _account_storage_key(address_hex: str) -> str:
    """Compute System::Account storage key using Blake2_128Concat"""
    # Remove 0x prefix if present
    if address_hex.startswith("0x"):
        address_hex = address_hex[2:]
    account_bytes = bytes.fromhex(address_hex)
    prefix = _twox_128(b"System") + _twox_128(b"Account")
    # Blake2_128Concat: blake2_128(account) ++ account
    blake = _hashlib.blake2b(account_bytes, digest_size=16).digest()
    return "0x" + (prefix + blake + account_bytes).hex()

def _decode_account_info(hex_value: str) -> dict:
    """Decode SCALE-encoded AccountInfo from storage value"""
    if not hex_value or hex_value == "null":
        return None
    raw = bytes.fromhex(hex_value[2:] if hex_value.startswith("0x") else hex_value)
    if len(raw) < 48:
        return None
    nonce = struct.unpack_from("<I", raw, 0)[0]
    consumers = struct.unpack_from("<I", raw, 4)[0]
    providers = struct.unpack_from("<I", raw, 8)[0]
    sufficients = struct.unpack_from("<I", raw, 12)[0]
    free = int.from_bytes(raw[16:32], "little")
    reserved = int.from_bytes(raw[32:48], "little")
    misc_frozen = int.from_bytes(raw[48:64], "little") if len(raw) >= 64 else 0
    fee_frozen = int.from_bytes(raw[64:80], "little") if len(raw) >= 80 else 0
    return {
        "nonce": nonce, "consumers": consumers, "providers": providers,
        "sufficients": sufficients, "free": free, "reserved": reserved,
        "misc_frozen": misc_frozen, "fee_frozen": fee_frozen,
    }

'''

# Insert helper code after the CORS middleware setup
insert_after = "client = httpx.AsyncClient(timeout=10.0)"
content = content.replace(insert_after, insert_after + "\n" + helper_code)

# 3. Replace the fallback account endpoint with real balance query
old_account_endpoint = '''@app.get("/api/v1/account/{address}")
async def account_detail(address: str):
    # Try to query system account
    # For now, return fallback data
    balance = 10000
    for v in VALIDATORS:
        if v["address"][:10] in address or address[:10] in v["address"]:
            balance = v["stake"]
            break
    
    return {
        "success": True,
        "data": {
            "address": address,
            "balance": balance,
            "balance_formatted": f"{balance:,.0f} VRDX",
            "nonce": 0,
            "identity": None,
            "is_validator": any(v["address"][:10] in address for v in VALIDATORS),
            "source": "fallback",
        }
    }'''

new_account_endpoint = '''@app.get("/api/v1/account/{address}")
async def account_detail(address: str):
    """Query real account data from System::Account storage via state_getStorage"""
    DEC = 9  # VRDX decimals

    # Get nonce via system_accountNextIndex (always available)
    nonce_val = await rpc("system_accountNextIndex", [address])

    # Query balance via state_getStorage with computed Blake2_128Concat key
    # First convert SS58 address to hex - we need the raw account bytes
    # For known test accounts, we can hardcode the hex. For others, try state_call.
    # Use the address directly as the storage key parameter
    balance = None
    try:
        # Try to decode SS58 to hex
        import base58
        ss58_bytes = base58.b58decode(address)
        # SS58 format: prefix(1 byte) + account(32 bytes) + checksum(2 bytes)
        account_hex = ss58_bytes[1:33].hex()

        storage_key = _account_storage_key(account_hex)
        result = await rpc("state_getStorage", [storage_key])

        if result:
            decoded = _decode_account_info(result)
            if decoded:
                free = decoded["free"]
                reserved = decoded["reserved"]
                total = free + reserved
                balance = {
                    "free": free,
                    "reserved": reserved,
                    "total": total,
                    "misc_frozen": decoded["misc_frozen"],
                    "fee_frozen": decoded["fee_frozen"],
                    "free_formatted": f"{free / 10**DEC:,.4f} VRDX",
                    "reserved_formatted": f"{reserved / 10**DEC:,.4f} VRDX",
                    "total_formatted": f"{total / 10**DEC:,.4f} VRDX",
                }
    except Exception as e:
        pass

    # Check if validator
    is_validator = False
    validator_name = None
    try:
        vals = await rpc("dpos_allValidators", [])
        if vals and address in vals:
            is_validator = True
            try:
                name_result = await rpc("dpos_validatorName", [address])
                if name_result and isinstance(name_result, list):
                    validator_name = "".join(chr(b) for b in name_result).strip()
                elif name_result and isinstance(name_result, str):
                    validator_name = name_result.strip()
            except:
                pass
    except:
        pass

    # Check green score
    green_score = 0
    if is_validator:
        try:
            gs = await rpc("eco_getGreenScore", [address])
            green_score = gs or 0
        except:
            pass

    return {
        "success": True,
        "data": {
            "address": address,
            "nonce": nonce_val or 0,
            "balance": balance.get("total", 0) if balance else 0,
            "balance_formatted": balance.get("total_formatted", "0 VRDX") if balance else "N/A",
            "free_balance": balance.get("free", 0) if balance else 0,
            "free_balance_formatted": balance.get("free_formatted", "N/A") if balance else "N/A",
            "reserved_balance": balance.get("reserved", 0) if balance else 0,
            "reserved_formatted": balance.get("reserved_formatted", "N/A") if balance else "N/A",
            "misc_frozen": balance.get("misc_frozen", 0) if balance else 0,
            "fee_frozen": balance.get("fee_frozen", 0) if balance else 0,
            "is_validator": is_validator,
            "validator_name": validator_name,
            "green_score": green_score,
            "identity": validator_name,
            "source": "rpc" if balance else "partial",
        }
    }'''

if old_account_endpoint in content:
    content = content.replace(old_account_endpoint, new_account_endpoint)
    print("Replaced account endpoint with real balance query")
else:
    print("WARNING: old account endpoint not found")

# 4. Add base58 import at the top
content = content.replace(
    "import hashlib\nfrom collections import defaultdict",
    "import hashlib\nimport base58\nfrom collections import defaultdict"
)

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
