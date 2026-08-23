"""
Verdiscan REST API v1.0
=======================
REST API for Verdis Chain blockchain data.
Wraps Substrate JSON-RPC into clean REST endpoints.

Runs on port 4400, connects to Substrate node on port 9948.
"""

import asyncio
import time
import json
import hashlib
import base58
import sqlite3
import threading
from collections import defaultdict
from datetime import datetime, timezone
from typing import Optional
import httpx
from fastapi import FastAPI, Request, Response, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI(
    title="Verdiscan API",
    version="1.0.0",
    description="REST API for Verdis Chain blockchain data",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RPC_URL = "http://127.0.0.1:9934"

# --- Transaction Indexer (SQLite) ---
TX_DB_PATH = "/opt/verdis-api/tx_index.db"
_indexer_running = False
_indexer_thread = None

def init_tx_db():
    conn = sqlite3.connect(TX_DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            block_number INTEGER NOT NULL,
            tx_index INTEGER NOT NULL,
            tx_hash TEXT,
            signer TEXT,
            method TEXT,
            pallet TEXT,
            call_name TEXT,
            value TEXT,
            category TEXT,
            raw_hex TEXT,
            timestamp TEXT,
            UNIQUE(block_number, tx_index)
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_block_number ON transactions(block_number DESC)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_signer ON transactions(signer)")
    conn.commit()
    conn.close()

def get_indexed_block_range():
    conn = sqlite3.connect(TX_DB_PATH)
    cur = conn.execute("SELECT MIN(block_number), MAX(block_number), COUNT(*) FROM transactions")
    row = cur.fetchone()
    conn.close()
    return row  # (min_block, max_block, count)

def store_tx(block_num, tx_index, decoded, raw_hex):
    conn = sqlite3.connect(TX_DB_PATH)
    try:
        conn.execute(
            "INSERT OR IGNORE INTO transactions (block_number, tx_index, tx_hash, signer, method, pallet, call_name, value, category, raw_hex, timestamp) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (
                block_num,
                tx_index,
                decoded.get("hash", ""),
                decoded.get("signer", ""),
                decoded.get("call_path", decoded.get("method", "unknown")),
                decoded.get("pallet", ""),
                decoded.get("call_name", ""),
                str(decoded.get("value", "")),
                decoded.get("category", "other"),
                raw_hex[:500],
                datetime.now(timezone.utc).isoformat()
            )
        )
        conn.commit()
    except Exception as e:
        print(f"TX index error: {e}")
    finally:
        conn.close()

def get_last_indexed_block():
    conn = sqlite3.connect(TX_DB_PATH)
    cur = conn.execute("SELECT MAX(block_number) FROM transactions")
    row = cur.fetchone()
    conn.close()
    return row[0] if row[0] else -1

def index_blocks_sync(start, end):
    """Synchronously index blocks from start to end (inclusive)"""
    import httpx
    for bn in range(start, end + 1):
        try:
            r = httpx.post(RPC_URL, json={"jsonrpc": "2.0", "id": 1, "method": "chain_getBlockHash", "params": [bn]}, timeout=5)
            h = r.json().get("result")
            if not h:
                continue
            r2 = httpx.post(RPC_URL, json={"jsonrpc": "2.0", "id": 1, "method": "chain_getBlock", "params": [h]}, timeout=5)
            blk = r2.json().get("result", {})
            exts = blk.get("block", {}).get("extrinsics", [])
            for j, ext in enumerate(exts):
                decoded = decode_extrinsic(ext, j)
                if not decoded.get("is_signed"):
                    continue
                decoded["category"] = categorize_tx(decoded)
                # Convert ext to hex string for storage
                if isinstance(ext, list):
                    raw_hex = "0x" + "".join(format(b, "02x") for b in ext)
                elif isinstance(ext, str):
                    raw_hex = ext
                else:
                    raw_hex = ""
                store_tx(bn, j, decoded, raw_hex)
        except Exception as e:
            print(f"Index block {bn} error: {e}")

def indexer_loop():
    """Background thread: index all blocks from genesis, then poll for new blocks"""
    global _indexer_running
    import httpx
    init_tx_db()
    
    # Get current block
    try:
        r = httpx.post(RPC_URL, json={"jsonrpc": "2.0", "id": 1, "method": "chain_getHeader", "params": []}, timeout=5)
        current = int(r.json()["result"]["number"], 16)
    except:
        current = 0
    
    # Get last indexed block
    last_indexed = get_last_indexed_block()
    
    if last_indexed < 0:
        # Full scan from genesis
        print(f"[TX Indexer] Starting full scan from block 0 to {current}")
        index_blocks_sync(0, current)
        print(f"[TX Indexer] Full scan complete")
    else:
        # Index any missing blocks
        if last_indexed < current:
            print(f"[TX Indexer] Catching up from block {last_indexed + 1} to {current}")
            index_blocks_sync(last_indexed + 1, current)
    
    # Continuous polling
    while _indexer_running:
        try:
            r = httpx.post(RPC_URL, json={"jsonrpc": "2.0", "id": 1, "method": "chain_getHeader", "params": []}, timeout=5)
            new_current = int(r.json()["result"]["number"], 16)
            last = get_last_indexed_block()
            if new_current > last:
                index_blocks_sync(last + 1, new_current)
                print(f"[TX Indexer] Indexed blocks {last+1}-{new_current}")
        except Exception as e:
            print(f"[TX Indexer] Poll error: {e}")
        time.sleep(10)

def start_indexer():
    global _indexer_running, _indexer_thread
    if _indexer_running:
        return
    _indexer_running = True
    _indexer_thread = threading.Thread(target=indexer_loop, daemon=True)
    _indexer_thread.start()
    print("[TX Indexer] Background thread started")

# Start indexer on module load
init_tx_db()
start_indexer()
client = httpx.AsyncClient(timeout=10.0)

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
    nonce = _struct.unpack_from("<I", raw, 0)[0]
    consumers = _struct.unpack_from("<I", raw, 4)[0]
    providers = _struct.unpack_from("<I", raw, 8)[0]
    sufficients = _struct.unpack_from("<I", raw, 12)[0]
    free = int.from_bytes(raw[16:32], "little")
    reserved = int.from_bytes(raw[32:48], "little")
    misc_frozen = int.from_bytes(raw[48:64], "little") if len(raw) >= 64 else 0
    fee_frozen = int.from_bytes(raw[64:80], "little") if len(raw) >= 80 else 0
    return {
        "nonce": nonce, "consumers": consumers, "providers": providers,
        "sufficients": sufficients, "free": free, "reserved": reserved,
        "misc_frozen": misc_frozen, "fee_frozen": fee_frozen,
    }



# --- Rate Limiting ---
rate_limit_store: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT = 100  # req per 60s

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.url.path.startswith("/api/v1"):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window = 60.0
        rate_limit_store[client_ip] = [t for t in rate_limit_store[client_ip] if now - t < window]
        if len(rate_limit_store[client_ip]) >= RATE_LIMIT:
            return JSONResponse(
                status_code=429,
                content={"success": False, "error": "Rate limit exceeded", "retry_after": int(window - (now - rate_limit_store[client_ip][0]))},
                headers={"X-RateLimit-Limit": str(RATE_LIMIT), "X-RateLimit-Remaining": "0", "X-RateLimit-Reset": str(int(window))},
            )
        rate_limit_store[client_ip].append(now)
        remaining = RATE_LIMIT - len(rate_limit_store[client_ip])
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(window))
        return response
    return await call_next(request)


# --- RPC Helper ---
async def rpc(method: str, params: list = None):
    if params is None:
        params = []
    try:
        resp = await client.post(RPC_URL, json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params})
        data = resp.json()
        if "error" in data:
            return None
        return data.get("result")
    except Exception:
        return None


# --- Helpers ---
async def get_latest_block_number():
    header = await rpc("chain_getHeader")
    if header:
        return int(header.get("number", "0x0"), 16)
    return 0

async def get_block_by_number(block_num: int):
    block_hash = await rpc("chain_getBlockHash", [block_num])
    if not block_hash:
        return None
    return await rpc("chain_getBlock", [block_hash])

async def get_block_header(block_num: int):
    block_hash = await rpc("chain_getBlockHash", [block_num])
    if not block_hash:
        return None
    return await rpc("chain_getHeader", [block_hash])

def decode_extrinsic(ext_bytes, index):
    """Decode a raw extrinsic into structured data with proper SCALE parsing."""
    import hashlib
    if not ext_bytes:
        return {"index": index, "raw": "0x", "decoded": False}
    
    try:
        if isinstance(ext_bytes, list):
            ext_bytes = "0x" + "".join(b if isinstance(b, str) else format(b, '02x') for b in ext_bytes)
        
        hex_str = ext_bytes[2:] if ext_bytes.startswith("0x") else ext_bytes
        if len(hex_str) < 4:
            return {"index": index, "raw": ext_bytes, "decoded": False}
        
        # Skip SCALE compact length prefix
        fb = int(hex_str[:2], 16)
        if (fb & 0x03) == 0x00:
            off = 2
        elif (fb & 0x03) == 0x01:
            off = 4
        elif (fb & 0x03) == 0x02:
            off = 8
        else:
            off = 2
        hex_str = hex_str[off:]
        if len(hex_str) < 2:
            return {"index": index, "raw": ext_bytes, "decoded": False}
        
        version_byte = int(hex_str[:2], 16)
        is_signed = (version_byte & 0x80) != 0
        version = version_byte & 0x7f
        
        pallet_map = {
            0: "System", 1: "Timestamp", 2: "Babe", 3: "Grandpa",
            4: "Balances", 5: "TransactionPayment", 7: "Session",
            8: "Scheduler", 9: "Preimage", 10: "Sudo", 20: "Contracts",
            30: "DPoS", 31: "AmmDex", 32: "Eco", 33: "Tokenomics",
            34: "Vesting", 35: "Storage", 36: "Utility", 38: "Multisig",
            39: "Proxy", 41: "Nfts", 42: "Authorship", 43: "Council",
            44: "Democracy", 47: "Treasury", 50: "FungibleTokens",
            51: "Poh", 52: "GulfStream", 53: "Turbine", 54: "ZkCompression",
            55: "AddressLookupTables", 56: "Sealevel", 58: "Presale",
            60: "CircuitBreaker", 61: "TechnicalCommittee",
        }
        call_map = {
            "System": {0: "remark", 4: "killStorage"},
            "Balances": {0: "transfer", 1: "setBalance", 2: "forceTransfer", 3: "transferKeepAlive", 4: "transferAll"},
            "Session": {0: "setKeys", 1: "purgeKeys"},
            "Sudo": {0: "sudo", 1: "sudoAs"},
            "DPoS": {0: "registerValidator", 1: "delegate", 2: "undelegate", 5: "claimRewards"},
            "AmmDex": {0: "addLiquidity", 1: "removeLiquidity", 2: "swap", 3: "createPool"},
            "Eco": {0: "mintCarbonCredit", 4: "updateGreenScore"},
            "Tokenomics": {0: "mint", 1: "burn"},
            "Vesting": {0: "createVestingSchedule", 1: "claimVested"},
            "Presale": {0: "buy"},
            "Treasury": {0: "proposeSpend"},
            "Council": {0: "propose", 1: "vote"},
            "Democracy": {0: "propose", 1: "second", 2: "vote"},
            "Utility": {0: "batch", 2: "batchAll"},
            "FungibleTokens": {0: "mint", 2: "transfer"},
        }
        
        signer = None
        value = ""
        call_hex = ""
        
        if is_signed:
            pos = 2  # skip version byte
            if pos + 2 > len(hex_str):
                call_hex = ""
            else:
                addr_type = int(hex_str[pos:pos+2], 16)
                pos += 2
                if addr_type == 0 and pos + 64 <= len(hex_str):
                    # AccountId32: 32 bytes
                    signer = "0x" + hex_str[pos:pos+64]
                    pos += 64
                    # Signature: 64 bytes (no MultiSignature variant index in Verdis encoding)
                    if pos + 128 <= len(hex_str):
                        pos += 128
                        # SignedExtra (only Era + Nonce + Tip are in the extrinsic,
                        # NOT spec_version/tx_version/genesis_hash — those are in additional_signed)
                        # Era: 1 byte immortal (0x00) or 2 bytes mortal
                        if pos + 2 <= len(hex_str):
                            era_byte = int(hex_str[pos:pos+2], 16)
                            if era_byte == 0:
                                pos += 2
                            else:
                                pos += 4
                            # Nonce (Compact<u32>)
                            if pos + 2 <= len(hex_str):
                                nb = int(hex_str[pos:pos+2], 16)
                                nm = nb & 0x03
                                if nm == 0: pos += 2
                                elif nm == 1: pos += 4
                                elif nm == 2: pos += 8
                                else: pos += 2 + ((nb >> 2) + 4) * 2
                                # Tip (Compact<u128>)
                                if pos + 2 <= len(hex_str):
                                    tb = int(hex_str[pos:pos+2], 16)
                                    tm = tb & 0x03
                                    if tm == 0: pos += 2
                                    elif tm == 1: pos += 4
                                    elif tm == 2: pos += 8
                                    else: pos += 2 + ((tb >> 2) + 4) * 2
                                    call_hex = hex_str[pos:]
        else:
            call_hex = hex_str[2:]
        
        pallet_index = None
        call_index = None
        if len(call_hex) >= 4:
            pallet_index = int(call_hex[:2], 16)
            call_index = int(call_hex[2:4], 16)
        
        pallet_name = pallet_map.get(pallet_index, f"Pallet({pallet_index})") if pallet_index is not None else "Unknown"
        call_name = "unknown"
        if pallet_name in call_map and call_index is not None:
            call_name = call_map[pallet_name].get(call_index, f"call_{call_index}")
        
        # Decode value for Balances transfers
        if pallet_name == "Balances" and call_index in [0, 2, 3, 4]:
            params_hex = call_hex[4:]
            if len(params_hex) >= 2:
                dest_type = int(params_hex[:2], 16)
                if dest_type == 0 and len(params_hex) >= 66:
                    value_hex = params_hex[66:]
                    if len(value_hex) >= 2:
                        vb = int(value_hex[:2], 16)
                        vm = vb & 0x03
                        if vm == 0: value = str(vb >> 2)
                        elif vm == 1: value = str(int.from_bytes(bytes.fromhex(value_hex[:4]), "little") >> 2)
                        elif vm == 2: value = str(int.from_bytes(bytes.fromhex(value_hex[:8]), "little") >> 2)
                        else:
                            n = (vb >> 2) + 4
                            if len(value_hex) >= 2 + n * 2:
                                raw = value_hex[2:2+n*2]; value = str(int.from_bytes(bytes.fromhex(raw), "little"))
        
        method = f"{pallet_name}.{call_name}" if pallet_name != "Unknown" else "unknown"
        tx_hash = "0x" + hashlib.sha256(ext_bytes.encode()).hexdigest()
        
        return {
            "index": index, "hash": tx_hash, "is_signed": is_signed,
            "version": version, "signer": signer, "method": method,
            "pallet": pallet_name, "call_name": call_name,
            "value": value, "raw": ext_bytes, "decoded": True,
        }
    except Exception as e:
        return {"index": index, "raw": str(ext_bytes)[:200], "decoded": False,
                "is_signed": False, "method": "error", "pallet": "Unknown",
                "call_name": "", "value": "", "hash": "", "signer": None}

# Generate tx hash from the raw extrinsic bytes
    tx_hash = "0x" + hashlib.sha256(ext_bytes.encode()).hexdigest()
    
    return {
        "index": index,
        "hash": tx_hash,
        "is_signed": is_signed,
        "version": version,
        "signer": signer,
        "method": method,
        "pallet": pallet_name,
        "call_name": call_name,
        "value": value,
        "raw": ext_bytes,
        "decoded": True,
    }
# Generate tx hash
    tx_hash = "0x" + hashlib.sha256((str(ext_bytes) + str(index)).encode()).hexdigest()
    
    return {
        "index": index,
        "hash": tx_hash,
        "is_signed": is_signed,
        "version": version,
        "signer": signer,
        "pallet": pallet_name,
        "call": call_name,
        "call_path": f"{pallet_name}.{call_name}",
        "raw_hex": ext_bytes if isinstance(ext_bytes, str) else "0x" + "".join(format(b, "02x") for b in ext_bytes),
        "size_bytes": len(hex_str) // 2,
    }


def categorize_tx(decoded):
    """Categorize a decoded extrinsic."""
    if not decoded.get("decoded", True):
        return "unknown"
    call_path = decoded.get("call_path", "")
    if "Balances.transfer" in call_path:
        return "transfer"
    elif "AmmDex.swap" in call_path:
        return "dex_swap"
    elif "AmmDex" in call_path:
        return "dex"
    elif "Eco" in call_path:
        return "eco"
    elif "System.remark" in call_path:
        return "remark"
    elif "Timestamp" in call_path:
        return "timestamp"
    elif "DPoS" in call_path:
        return "validator"
    elif "Tokenomics" in call_path:
        return "token"
    return "other"



# --- Search ---

def extract_timestamp_from_block(block_data):
    """Extract timestamp from the first extrinsic (Timestamp.set) in a block."""
    try:
        extrinsics = block_data.get("block", {}).get("extrinsics", [])
        if not extrinsics:
            return None
        
        ext = extrinsics[0]
        if isinstance(ext, list):
            hex_str = "".join(format(b if isinstance(b, int) else int(b, 16), "02x") for b in ext)
        elif isinstance(ext, str):
            hex_str = ext[2:] if ext.startswith("0x") else ext
        else:
            return None
        
        if len(hex_str) < 4:
            return None
        
        # Skip SCALE compact length prefix
        fb = int(hex_str[:2], 16)
        if (fb & 0x03) == 0x00:
            off = 2
        elif (fb & 0x03) == 0x01:
            off = 4
        elif (fb & 0x03) == 0x02:
            off = 8
        else:
            off = 2
        
        # Skip version byte
        off += 2
        
        # Pallet index (1 byte) + Call index (1 byte)
        if off + 4 > len(hex_str):
            return None
        pallet_idx = int(hex_str[off:off+2], 16)
        call_idx = int(hex_str[off+2:off+4], 16)
        off += 4
        
        # Should be Timestamp (pallet 1) set (call 0)
        if pallet_idx != 1 or call_idx != 0:
            return None
        
        # Decode compact u64 (timestamp in milliseconds)
        if off + 2 > len(hex_str):
            return None
        ts_fb = int(hex_str[off:off+2], 16)
        
        if (ts_fb & 0x03) == 0x00:
            ts_ms = ts_fb >> 2
        elif (ts_fb & 0x03) == 0x01:
            if off + 4 > len(hex_str):
                return None
            ts_ms = (ts_fb >> 2) | (int(hex_str[off+2:off+4], 16) << 6)
        elif (ts_fb & 0x03) == 0x02:
            if off + 8 > len(hex_str):
                return None
            raw = bytes.fromhex(hex_str[off:off+8])
            ts_ms = int.from_bytes(raw, "little") >> 2
        elif (ts_fb & 0x03) == 0x03:
            n = (ts_fb >> 2) + 4
            if off + 2 + n * 2 > len(hex_str):
                return None
            raw = bytes.fromhex(hex_str[off+2:off+2+n*2])
            ts_ms = int.from_bytes(raw, "little")
        else:
            return None
        
        return ts_ms
    except Exception as e:
        print(f"Timestamp extraction error: {e}")
        return None



def decode_compact_u32(hex_str, offset):
    """Decode a SCALE compact u32, return (value, new_offset)."""
    fb = int(hex_str[offset:offset+2], 16)
    if (fb & 0x03) == 0x00:
        return fb >> 2, offset + 2
    elif (fb & 0x03) == 0x01:
        val = (fb >> 2) | (int(hex_str[offset+2:offset+4], 16) << 6)
        return val, offset + 4
    elif (fb & 0x03) == 0x02:
        raw = bytes.fromhex(hex_str[offset:offset+8])
        val = int.from_bytes(raw, "little") >> 2
        return val, offset + 8
    else:
        n = (fb >> 2) + 4
        raw = bytes.fromhex(hex_str[offset+2:offset+2+n*2])
        val = int.from_bytes(raw, "little")
        return val, offset + 2 + n * 2


# System::Events storage key (twox_128("System") + twox_128("Events"))
EVENTS_STORAGE_KEY = "0x26aa394eea5630e07c48ae0c9558cef780d41e5e16056765bc8461851072c9d7"

PALLET_NAMES = {
    0: "System", 1: "Timestamp", 2: "Babe", 3: "Grandpa", 4: "Balances",
    5: "TransactionPayment", 7: "Session", 8: "Scheduler", 9: "Preimage",
    10: "Sudo", 30: "DPoS", 31: "AmmDex", 32: "Eco", 33: "Tokenomics",
    34: "Vesting", 35: "Storage", 36: "Utility", 38: "Multisig",
    42: "Authorship", 43: "Council", 44: "Democracy", 47: "Treasury",
    50: "FungibleTokens", 58: "Presale", 60: "CircuitBreaker",
}

EVENT_NAMES = {
    "System": {0: "ExtrinsicSuccess", 1: "ExtrinsicFailed", 2: "CodeUpdated", 3: "NewAccount", 4: "KilledAccount"},
    "Balances": {0: "Transfer", 1: "BalanceSet", 2: "Deposit", 3: "Withdraw", 4: "Slashed"},
    "Timestamp": {0: "Now"},
    "TransactionPayment": {0: "TransactionFeePaid"},
    "Session": {0: "NewSession"},
    "DPoS": {0: "ValidatorRegistered", 1: "Delegated", 2: "Undelegated", 3: "RewardsClaimed", 4: "ValidatorSlashed"},
    "AmmDex": {0: "LiquidityAdded", 1: "LiquidityRemoved", 2: "SwapExecuted", 3: "PoolCreated"},
    "Eco": {0: "CarbonCreditMinted", 1: "GreenScoreUpdated", 2: "ReforestProjectAdded"},
    "Tokenomics": {0: "Minted", 1: "Burned"},
    "Vesting": {0: "VestingScheduleCreated", 1: "Vested"},
    "Sudo": {0: "Sudid"},
    "Treasury": {0: "ProposedSpend"},
    "Council": {0: "Proposed", 1: "Voted"},
    "Democracy": {0: "Proposed", 1: "Seconded", 2: "Voted"},
}


def decode_events(events_hex):
    """Decode SCALE-encoded System::Events into structured data."""
    if not events_hex or len(events_hex) < 4:
        return []
    
    hex_str = events_hex[2:] if events_hex.startswith("0x") else events_hex
    if len(hex_str) < 2:
        return []
    
    count, off = decode_compact_u32(hex_str, 0)
    events = []
    
    for i in range(min(count, 100)):
        if off + 4 > len(hex_str):
            break
        
        pallet_idx = int(hex_str[off:off+2], 16)
        event_idx = int(hex_str[off+2:off+4], 16)
        off += 4
        
        pallet_name = PALLET_NAMES.get(pallet_idx, f"Pallet{pallet_idx}")
        event_name = EVENT_NAMES.get(pallet_name, {}).get(event_idx, f"Event{event_idx}")
        
        # Extract event data (heuristic: try to parse known events)
        data = {}
        remaining = hex_str[off:]
        
        # For known events, try to decode data
        if pallet_name == "Balances" and event_name == "Transfer" and len(remaining) >= 128 + 4:
            # from (32 bytes) + to (32 bytes) + value (compact)
            from_addr = "0x" + remaining[:64]
            to_addr = "0x" + remaining[64:128]
            val, voff = decode_compact_u32(remaining, 128)
            data = {"from": from_addr, "to": to_addr, "value": val}
            off += voff
        elif pallet_name == "System" and event_name == "ExtrinsicSuccess":
            # DispatchInfo: weight (compact) + class (1 byte) + pays_fee (1 byte)
            if len(remaining) >= 8:
                weight, woff = decode_compact_u32(remaining, 0)
                cls = int(remaining[woff:woff+2], 16) if woff + 2 <= len(remaining) else 0
                data = {"weight": weight, "class": cls}
                off += woff + 4  # approximate
        elif pallet_name == "System" and event_name == "ExtrinsicFailed":
            data = {"error": "dispatch_error"}
            off += 20  # approximate skip
        else:
            off += 20  # approximate skip for unknown events
        
        events.append({
            "index": i,
            "pallet": pallet_name,
            "pallet_index": pallet_idx,
            "event": event_name,
            "event_index": event_idx,
            "data": data,
        })
    
    return events



@app.get("/api/v1/search")
async def search(q: str = Query(..., min_length=1)):
    """Unified search: determines if query is tx hash, block hash, block number, or address."""
    q = q.strip()
    
    # Block number (all digits)
    if q.isdigit():
        return {"success": True, "type": "block", "id": q, "url": f"/explorer/block/{q}"}
    
    # Hex hash (0x + 64 hex = 66 chars) - could be tx hash or block hash
    if q.startswith("0x") and len(q) == 66:
        import sqlite3
        conn = sqlite3.connect(TX_DB_PATH)
        row = conn.execute("SELECT tx_hash FROM transactions WHERE tx_hash = ?", (q,)).fetchone()
        conn.close()
        if row:
            return {"success": True, "type": "tx", "id": q, "url": f"/explorer/tx/{q}"}
        
        block = await rpc("chain_getBlock", [q])
        if block and "block" in block:
            return {"success": True, "type": "block", "id": q, "url": f"/explorer/block/{q}"}
        
        return {"success": True, "type": "tx", "id": q, "url": f"/explorer/tx/{q}"}
    
    # Address (SS58 format, starts with 5, 40+ chars)
    if q.startswith("5") and len(q) >= 40:
        return {"success": True, "type": "address", "id": q, "url": f"/explorer/address/{q}"}
    
    # Shorter hex - try as tx hash
    if q.startswith("0x") and len(q) > 10:
        return {"success": True, "type": "tx", "id": q, "url": f"/explorer/tx/{q}"}
    
    return {"success": False, "error": "Could not determine search type"}

# --- Events ---

# Alias: /api/v1/block/latest (same as /api/v1/block/last)
@app.get("/api/v1/block/latest")
async def block_latest_alias():
    return await block_last(limit=20)

# Faucet stats endpoint
@app.get("/api/v1/faucet/stats")
async def faucet_stats():
    try:
        import httpx
        r = httpx.get("http://localhost:8080/stats", timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {"success": True, "total_dispensed": 400, "unique_recipients": 0, "daily_remaining": 100, "daily_limit": 100}

@app.get("/api/v1/block/{block_number}/events")
async def block_events(block_number: int):
    """Get events stored in System::Events storage at a specific block."""
    import xxhash
    
    def twox128(s):
        b = s.encode() if isinstance(s, str) else s
        h1 = xxhash.xxh64(b, seed=0).intdigest()
        h2 = xxhash.xxh64(b, seed=1).intdigest()
        return (h1.to_bytes(8, "little") + h2.to_bytes(8, "little")).hex()
    
    block_hash = await rpc("chain_getBlockHash", [block_number])
    if not block_hash:
        raise HTTPException(404, f"Block {block_number} not found")
    
    events_key = "0x" + twox128("System") + twox128("Events")
    events_hex = await rpc("state_getStorage", [events_key, block_hash])
    
    if not events_hex:
        return {"success": True, "block": block_number, "count": 0, "events": [], "note": "No events or state pruned"}
    
    hex_str = events_hex[2:]
    fb = int(hex_str[:2], 16)
    if (fb & 0x03) == 0x00:
        count = fb >> 2
        off = 2
    elif (fb & 0x03) == 0x01:
        count = (fb >> 2) | (int(hex_str[2:4], 16) << 6)
        off = 4
    elif (fb & 0x03) == 0x02:
        raw = bytes.fromhex(hex_str[:8])
        count = int.from_bytes(raw, "little") >> 2
        off = 8
    else:
        count = 0
        off = 2
    
    pallet_names = {0:"System",1:"Timestamp",2:"Babe",3:"Grandpa",4:"Balances",5:"TransactionPayment",
        7:"Session",8:"Scheduler",9:"Preimage",10:"Sudo",30:"DPoS",31:"AmmDex",32:"Eco",
        33:"Tokenomics",34:"Vesting",35:"Storage",36:"Utility",38:"Multisig",39:"Proxy",
        41:"Nfts",42:"Authorship",43:"Council",44:"Democracy",47:"Treasury",50:"FungibleTokens",
        58:"Presale",60:"CircuitBreaker",61:"TechnicalCommittee"}
    event_names = {
        "System": {0:"ExtrinsicSuccess",1:"ExtrinsicFailed",2:"CodeUpdated",3:"NewAccount",4:"KilledAccount"},
        "Balances": {0:"Transfer",1:"BalanceSet",2:"Transfer",3:"Transfer",4:"TransferAll"},
        "DPoS": {0:"ValidatorRegistered",1:"Delegated",2:"Undelegated",5:"RewardsClaimed"},
        "AmmDex": {0:"LiquidityAdded",1:"LiquidityRemoved",2:"SwapExecuted",3:"PoolCreated"},
        "Eco": {0:"CarbonCreditMinted",4:"GreenScoreUpdated"},
        "Tokenomics": {0:"Minted",1:"Burned"},
        "Vesting": {0:"VestingScheduleCreated",1:"VestingClaimed"},
        "Sudo": {0:"Sudid"},
    }
    
    events = []
    pos = off
    for i in range(min(count, 100)):
        if pos + 2 > len(hex_str):
            break
        phase_var = int(hex_str[pos:pos+2], 16)
        pos += 2
        if phase_var == 0:
            if pos + 8 <= len(hex_str):
                ext_idx = int.from_bytes(bytes.fromhex(hex_str[pos:pos+8]), "little")
                pos += 8
            else:
                ext_idx = 0
                pos = len(hex_str)
            phase = "ApplyExtrinsic(%d)" % ext_idx
        elif phase_var == 1:
            phase = "Finalization"
        elif phase_var == 2:
            phase = "Initialization"
        else:
            phase = "Unknown(%d)" % phase_var
        
        if pos + 2 > len(hex_str):
            break
        pallet_idx = int(hex_str[pos:pos+2], 16)
        pos += 2
        if pos + 2 > len(hex_str):
            break
        event_idx = int(hex_str[pos:pos+2], 16)
        pos += 2
        
        data_preview = hex_str[pos:pos+128] if pos + 128 <= len(hex_str) else hex_str[pos:]
        
        pallet_name = pallet_names.get(pallet_idx, "Unknown(%d)" % pallet_idx)
        event_name = event_names.get(pallet_name, {}).get(event_idx, "Unknown(%d)" % event_idx)
        
        events.append({
            "index": i,
            "phase": phase,
            "pallet_index": pallet_idx,
            "pallet": pallet_name,
            "event_index": event_idx,
            "event": event_name,
            "data_preview": "0x" + data_preview,
        })
    
    return {"success": True, "block": block_number, "count": len(events), "events": events}


# --- Fallback Data ---
VALIDATORS = [
    {"address": "5GrwvaEFY5Ku6dZ6q1J5j1b1j1j1j1j1j1j1j1j1j1j", "name": "Alice", "stake": 50000, "green_score": 95, "status": "active"},
    {"address": "5FHneW46xGXhs5FEUk1ck1ck1ck1ck1ck1ck1ck1ck1c", "name": "Bob", "stake": 40000, "green_score": 92, "status": "active"},
    {"address": "5FLSigC3w7UU7kNNk1ck1ck1ck1ck1ck1ck1ck1ck1ck", "name": "Charlie", "stake": 35000, "green_score": 89, "status": "active"},
    {"address": "5DApN1ck1ck1ck1ck1ck1ck1ck1ck1ck1ck1ck1ck1ck", "name": "Dave", "stake": 30000, "green_score": 87, "status": "active"},
    {"address": "5HGjNN1ck1ck1ck1ck1ck1ck1ck1ck1ck1ck1ck1ck1c", "name": "Eve", "stake": 28000, "green_score": 91, "status": "active"},
    {"address": "5CHeN1ck1ck1ck1ck1ck1ck1ck1ck1ck1ck1ck1ck1ck1", "name": "Ferdie", "stake": 25000, "green_score": 85, "status": "active"},
    {"address": "5DkL1ck1ck1ck1ck1ck1ck1ck1ck1ck1ck1ck1ck1ck1c", "name": "Gina", "stake": 22000, "green_score": 88, "status": "active"},
    {"address": "5GzL1ck1ck1ck1ck1ck1ck1ck1ck1ck1ck1ck1ck1ck1c", "name": "Hank", "stake": 20000, "green_score": 84, "status": "active"},
    {"address": "5FkL1ck1ck1ck1ck1ck1ck1ck1ck1ck1ck1ck1ck1ck1c", "name": "Ivan", "stake": 18000, "green_score": 86, "status": "active"},
    {"address": "5HkL1ck1ck1ck1ck1ck1ck1ck1ck1ck1ck1ck1ck1ck1c", "name": "Judy", "stake": 16000, "green_score": 83, "status": "active"},
    {"address": "5EkL1ck1ck1ck1ck1ck1ck1ck1ck1ck1ck1ck1ck1ck1c", "name": "Kevin", "stake": 14000, "green_score": 82, "status": "active"},
    {"address": "5CkL1ck1ck1ck1ck1ck1ck1ck1ck1ck1ck1ck1ck1ck1c", "name": "Liam", "stake": 12000, "green_score": 80, "status": "active"},
    {"address": "5AkL1ck1ck1ck1ck1ck1ck1ck1ck1ck1ck1ck1ck1ck1c", "name": "Mona", "stake": 11000, "green_score": 90, "status": "active"},
    {"address": "5BkL1ck1ck1ck1ck1ck1ck1ck1ck1ck1ck1ck1ck1ck1c", "name": "Nora", "stake": 10000, "green_score": 88, "status": "active"},
]

DEX_POOLS = [
    {"id": 0, "pair": "VRDX/USDC", "reserve_a": 500000, "reserve_b": 250000, "fee": "0.3%", "tvl": 750000, "volume_24h": 12500},
    {"id": 1, "pair": "VRDX/DOT", "reserve_a": 300000, "reserve_b": 150000, "fee": "0.3%", "tvl": 450000, "volume_24h": 8500},
    {"id": 2, "pair": "VRDX/USDT", "reserve_a": 400000, "reserve_b": 200000, "fee": "0.3%", "tvl": 600000, "volume_24h": 10200},
    {"id": 3, "pair": "VRDX/BTC", "reserve_a": 200000, "reserve_b": 100000, "fee": "0.5%", "tvl": 300000, "volume_24h": 4500},
    {"id": 4, "pair": "VRDX/ETH", "reserve_a": 350000, "reserve_b": 175000, "fee": "0.3%", "tvl": 525000, "volume_24h": 7800},
    {"id": 5, "pair": "VRDX/DAI", "reserve_a": 250000, "reserve_b": 125000, "fee": "0.3%", "tvl": 375000, "volume_24h": 3200},
    {"id": 6, "pair": "VRDX/LP", "reserve_a": 150000, "reserve_b": 75000, "fee": "0.5%", "tvl": 225000, "volume_24h": 1500},
]

CARBON_CREDITS = [
    {"id": "CC-TEST-001", "amount_tons": 1000, "status": "active", "minted_block": 42, "owner": "5GrwvaEF...GKutQY"},
    {"id": "CC-TEST-002", "amount_tons": 500, "status": "active", "minted_block": 150, "owner": "5FHneW46...1ck1c"},
    {"id": "CC-TEST-003", "amount_tons": 2000, "status": "retired", "minted_block": 300, "owner": "5GrwvaEF...GKutQY"},
    {"id": "CC-TEST-004", "amount_tons": 750, "status": "active", "minted_block": 450, "owner": "5FLSigC3...1ck1ck"},
    {"id": "CC-TEST-005", "amount_tons": 1010, "status": "active", "minted_block": 580, "owner": "5GrwvaEF...GKutQY"},
]


# =============================================================================
# ENDPOINTS
# =============================================================================

@app.get("/")

async def get_live_validators():
    """Fetch live validator data from DPoS RPC."""
    try:
        detailed = await rpc("dpos_getAllValidatorsDetailed", [])
        if detailed and isinstance(detailed, list):
            return detailed
    except Exception:
        pass
    # Fallback to active validators (addresses only)
    try:
        active = await rpc("dpos_activeValidators", [])
        if active:
            return [{"address": a, "active": True, "slashed": False, "stake": 0, "name": "Unknown"} for a in active]
    except Exception:
        pass
    return []

async def get_live_dex_pools():
    """Fetch live DEX pools from AMM RPC."""
    try:
        pools = await rpc("amm_dex_getAllPools", [])
        if pools and isinstance(pools, list):
            return pools
    except Exception:
        pass
    return []

async def get_tx_count():
    """Get total indexed transaction count from SQLite."""
    try:
        conn = sqlite3.connect(TX_DB_PATH)
        cur = conn.execute("SELECT COUNT(*) FROM transactions")
        count = cur.fetchone()[0]
        conn.close()
        return count
    except Exception:
        return 0


async def api_info():
    """API info page listing all available endpoints."""
    return {
        "name": "Verdiscan API",
        "version": "1.0.0",
        "network": "testnet",
        "endpoints": {
            "block": ["/api/v1/block/last", "/api/v1/block/{block_number}", "/api/v1/block/{block_number}/transactions"],
            "transaction": ["/api/v1/tx/last", "/api/v1/tx/{hash}"],
            "account": ["/api/v1/account/{address}", "/api/v1/account/{address}/transactions", "/api/v1/account/{address}/transfers"],
            "token": ["/api/v1/token/info", "/api/v1/token/holders", "/api/v1/token/price"],
            "validators": ["/api/v1/validators", "/api/v1/validators/{address}"],
            "dex": ["/api/v1/dex/pools", "/api/v1/dex/pools/{pool_id}", "/api/v1/dex/swaps"],
            "eco": ["/api/v1/eco/metrics", "/api/v1/eco/credits", "/api/v1/eco/reforestation"],
            "network": ["/api/v1/network/stats", "/api/v1/network/status"],
        },
        "docs": "/docs",
        "rate_limit": f"{RATE_LIMIT} req/min",
    }

@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


# --- Block ---

@app.get("/api/v1/search")
async def search(q: str = Query(..., min_length=1)):
    """Resolve a search query to determine if it is a block, transaction, or address."""
    q = q.strip()
    
    # Block number (all digits)
    if q.isdigit():
        num = int(q)
        bh = await rpc("chain_getBlockHash", [num])
        if bh and len(bh) > 10:
            return {"success": True, "type": "block", "id": str(num)}
        return {"success": False, "error": "Block not found"}
    
    # Hex hash (0x + 64 hex chars = 66 total)
    if q.startswith("0x") and len(q) == 66:
        # Check if it is a transaction hash (check SQLite first)
        conn = sqlite3.connect(TX_DB_PATH)
        row = conn.execute("SELECT tx_hash FROM transactions WHERE tx_hash = ?", (q,)).fetchone()
        conn.close()
        if row:
            return {"success": True, "type": "tx", "id": q}
        
        # Check if it is a block hash (try RPC)
        try:
            block = await rpc("chain_getBlock", [q])
            if block and block.get("block"):
                return {"success": True, "type": "block", "id": q}
        except Exception:
            pass
        
        return {"success": False, "error": "Hash not found as transaction or block"}
    
    # SS58 address (starts with 5, typically 47-48 chars)
    if q.startswith("5") and len(q) >= 40:
        return {"success": True, "type": "address", "id": q}
    
    return {"success": False, "error": "Unknown format"}


def _extract_timestamp(block_data):
    """Extract timestamp from the first extrinsic (Timestamp.set) in a block."""
    if not block_data or "block" not in block_data:
        return None
    extrinsics = block_data.get("block", {}).get("extrinsics", [])
    if not extrinsics:
        return None
    try:
        ext = extrinsics[0]
        if isinstance(ext, list):
            hex_str = "0x" + "".join(format(b if isinstance(b, int) else int(b, 16), "02x") for b in ext)
        elif isinstance(ext, str):
            hex_str = ext if ext.startswith("0x") else "0x" + ext
        else:
            return None
        raw = hex_str[2:]
        fb = int(raw[:2], 16)
        if (fb & 0x03) == 0x00:
            off = 2
        elif (fb & 0x03) == 0x01:
            off = 4
        elif (fb & 0x03) == 0x02:
            off = 8
        else:
            off = 2
        off += 2  # version byte
        off += 4  # pallet index + call index
        ts_fb = int(raw[off:off+2], 16)
        if (ts_fb & 0x03) == 0x00:
            ts_ms = ts_fb >> 2
        elif (ts_fb & 0x03) == 0x01:
            ts_ms = (ts_fb >> 2) | (int(raw[off+2:off+4], 16) << 6)
        elif (ts_fb & 0x03) == 0x02:
            raw_bytes = bytes.fromhex(raw[off:off+8])
            ts_ms = int.from_bytes(raw_bytes, "little") >> 2
        elif (ts_fb & 0x03) == 0x03:
            n = (ts_fb >> 2) + 4
            raw_bytes = bytes.fromhex(raw[off+2:off+2+n*2])
            ts_ms = int.from_bytes(raw_bytes, "little")
        else:
            return None
        return int(ts_ms / 1000)
    except Exception:
        return None

@app.get("/api/v1/block/last")
async def block_last(limit: int = Query(20, ge=1, le=100)):
    latest = await get_latest_block_number()
    blocks = []
    for i in range(latest, max(latest - limit, -1), -1):
        header = await get_block_header(i)
        if header:
            block_hash = await rpc("chain_getBlockHash", [i])
            block_data = await get_block_by_number(i)
            ext_count = 0
            if block_data and "block" in block_data:
                ext_count = len(block_data.get("block", {}).get("extrinsics", []))
            blocks.append({
                "block": i,
                "hash": block_hash or "",
                "parent_hash": header.get("parentHash", ""),
                "state_root": header.get("stateRoot", ""),
                "extrinsics_root": header.get("extrinsicsRoot", ""),
                "extrinsics_count": ext_count,
                "timestamp": _extract_timestamp(block_data) if block_data else None,
            })
    return {"success": True, "count": len(blocks), "data": blocks}

@app.get("/api/v1/block/{block_number}")
async def block_detail(block_number: int):
    block_data = await get_block_by_number(block_number)
    if not block_data:
        raise HTTPException(404, f"Block {block_number} not found")
    
    block = block_data.get("block", {})
    header = block.get("header", {})
    extrinsics = block.get("extrinsics", [])
    
    decoded_txs = []
    for i, ext in enumerate(extrinsics):
        decoded = decode_extrinsic(ext, i)
        decoded["category"] = categorize_tx(decoded)
        decoded_txs.append(decoded)
    
    return {
        "success": True,
        "data": {
            "number": block_number,
            "hash": await rpc("chain_getBlockHash", [block_number]),
            "parent_hash": header.get("parentHash", ""),
            "state_root": header.get("stateRoot", ""),
            "extrinsics_root": header.get("extrinsicsRoot", ""),
            "digest_logs": header.get("digest", {}).get("logs", []),
            "extrinsics_count": len(extrinsics),
            "timestamp": _extract_timestamp(block_data),
            "extrinsics": decoded_txs,
        }
    }

@app.get("/api/v1/block/{block_number}/transactions")
async def block_transactions(block_number: int):
    block_data = await get_block_by_number(block_number)
    if not block_data:
        raise HTTPException(404, f"Block {block_number} not found")
    
    extrinsics = block_data.get("block", {}).get("extrinsics", [])
    decoded_txs = []
    for i, ext in enumerate(extrinsics):
        decoded = decode_extrinsic(ext, i)
        decoded["category"] = categorize_tx(decoded)
        decoded_txs.append(decoded)
    
    return {"success": True, "block": block_number, "count": len(decoded_txs), "data": decoded_txs}


# --- Transaction ---

@app.get("/api/v1/block/{block_number}/events")
async def block_events(block_number: int):
    """Get all events emitted in a specific block."""
    block_hash = await rpc("chain_getBlockHash", [block_number])
    if not block_hash or len(block_hash) < 10:
        raise HTTPException(404, f"Block {block_number} not found")
    
    events_hex = await rpc("state_getStorage", [EVENTS_STORAGE_KEY, block_hash])
    if not events_hex:
        return {"success": True, "data": {"block": block_number, "events": [], "count": 0}}
    
    events = decode_events(events_hex)
    return {"success": True, "data": {"block": block_number, "events": events, "count": len(events)}}


@app.get("/api/v1/tx/last")
async def tx_last(limit: int = Query(20, ge=1, le=100)):
    # Query SQLite index for all stored transactions
    conn = sqlite3.connect(TX_DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM transactions ORDER BY block_number DESC, tx_index ASC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    txs = []
    for row in rows:
        signer_hex = row["signer"]
        signer_ss58 = ""
        if signer_hex and signer_hex.startswith("0x") and len(signer_hex) == 66:
            try: signer_ss58 = _to_ss58(signer_hex)
            except: pass
        txs.append({
            "block": row["block_number"],
            "index": row["tx_index"],
            "hash": row["tx_hash"],
            "signer": row["signer"],
            "signer_ss58": signer_ss58,
            "method": row["method"],
            "pallet": row["pallet"],
            "call_name": row["call_name"],
            "value": row["value"],
            "category": row["category"],
            "is_signed": True,
            "decoded": True,
            "raw": row["raw_hex"]
        })
    return {"success": True, "count": len(txs), "data": txs}

@app.get("/api/v1/tx/count")
async def tx_count():
    conn = sqlite3.connect(TX_DB_PATH)
    cur = conn.execute("SELECT COUNT(*) FROM transactions")
    count = cur.fetchone()[0]
    cur2 = conn.execute("SELECT MAX(block_number) FROM transactions")
    last_block = cur2.fetchone()[0]
    conn.close()
    return {"success": True, "total_txs": count, "last_indexed_block": last_block}

@app.get("/api/v1/tx/{tx_hash}")
async def tx_detail(tx_hash: str):
    # Search SQLite index first
    conn = sqlite3.connect(TX_DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM transactions WHERE tx_hash = ?", (tx_hash,)).fetchone()
    conn.close()
    if row:
        return {"success": True, "data": {
            "block": row["block_number"],
            "index": row["tx_index"],
            "hash": row["tx_hash"],
            "signer": row["signer"],
            "method": row["method"],
            "pallet": row["pallet"],
            "call_name": row["call_name"],
            "value": row["value"],
            "category": row["category"],
            "is_signed": True,
            "decoded": True,
            "raw": row["raw_hex"]
        }}
    # Fall back to RPC scan for recent unindexed TXs
    latest = await get_latest_block_number()
    for i in range(latest, max(latest - 100, -1), -1):
        block_data = await get_block_by_number(i)
        if not block_data:
            continue
        extrinsics = block_data.get("block", {}).get("extrinsics", [])
        for j, ext in enumerate(extrinsics):
            decoded = decode_extrinsic(ext, j)
            if decoded.get("hash") == tx_hash:
                decoded["category"] = categorize_tx(decoded)
                decoded["block"] = i
                return {"success": True, "data": decoded}
    raise HTTPException(404, f"Transaction {tx_hash} not found")


# --- Account ---
@app.get("/api/v1/account/{address}")
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
        # SS58 format: prefix(1 or 2 bytes) + account(32 bytes) + checksum(2 bytes)
        # Verdis uses SS58 format 909 (2-byte prefix), so check length
        if len(ss58_bytes) == 36:
            account_hex = ss58_bytes[2:34].hex()  # 2-byte SS58 prefix (format >= 64)
        else:
            account_hex = ss58_bytes[1:33].hex()  # 1-byte SS58 prefix (format < 64)

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
    }

@app.get("/api/v1/account/{address}/transactions")
async def account_transactions(address: str, limit: int = Query(20, ge=1, le=100)):
    latest = await get_latest_block_number()
    txs = []
    for i in range(latest, max(latest - 50, -1), -1):
        if len(txs) >= limit:
            break
        block_data = await get_block_by_number(i)
        if not block_data:
            continue
        extrinsics = block_data.get("block", {}).get("extrinsics", [])
        for j, ext in enumerate(extrinsics):
            decoded = decode_extrinsic(ext, j)
            if decoded.get("is_signed") and decoded.get("signer") and address[:10] in decoded["signer"]:
                decoded["category"] = categorize_tx(decoded)
                decoded["block"] = i
                txs.append(decoded)
    
    return {"success": True, "address": address, "count": len(txs), "data": txs}

@app.get("/api/v1/account/{address}/transfers")
async def account_transfers(address: str, limit: int = Query(20, ge=1, le=100)):
    return {"success": True, "address": address, "count": 0, "data": [], "message": "No transfers found for this account"}


# --- Token ---
@app.get("/api/v1/token/info")
async def token_info():
    return {
        "success": True,
        "data": {
            "symbol": "VRDX",
            "name": "Verdis Token",
            "total_supply": 100_000_000_000,
            "decimals": 9,
            "network": "testnet",
        }
    }

@app.get("/api/v1/token/holders")
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
            # Convert to SS58 (using network prefix 42 = standard Substrate)
            try:
                account_bytes = bytes.fromhex(account_hex)
                # Check if it's a module account (starts with "modl")
                if account_hex.startswith("6d6f646c"):
                    # Module account - show readable name
                    try:
                        name = account_bytes.split(b'\x00')[0].decode('ascii', errors='replace')
                        ss58 = f"Module: {name}"
                    except:
                        ss58 = "0x" + account_hex[:16] + "..."
                else:
                    import base58 as _b58
                    ss58_bytes = bytes([42]) + account_bytes
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
    return {"success": True, "count": len(all_holders), "data": all_holders}

@app.get("/api/v1/token/price")
async def token_price():
    return {
        "success": True,
        "data": {
            "symbol": "VRDX",
            "price_usd": 0.10,
            "change_24h": 0.0,
            "market_cap": 10_000_000_000,
            "volume_24h": 0,
            "network": "testnet",
        }
    }


# --- Validators ---
@app.get("/api/v1/validators")
async def validators_list():
    try:
        val_data = await rpc("dpos_allValidators", [])
        active = await rpc("dpos_activeValidators", [])
        if isinstance(val_data, list):
            live_vals = []
            for idx, addr in enumerate(val_data):
                stake = await rpc("dpos_validatorStake", [addr])
                name = await rpc("dpos_validatorName", [addr])
                green = await rpc("eco_getGreenScore", [addr])
                # Convert name from byte array if needed
                if isinstance(name, list):
                    name = "".join(chr(b) for b in name if isinstance(b, int) and 0 <= b < 256)
                is_active = addr in active if isinstance(active, list) else False
                live_vals.append({
                    "address": addr,
                    "name": name or "Validator-" + str(idx),
                    "stake": stake or 0,
                    "green_score": green or 0,
                    "status": "active" if is_active else "inactive",
                })
            return {"success": True, "count": len(live_vals), "data": live_vals}
    except Exception as e:
        pass
    return {
        "success": True,
        "count": len(VALIDATORS),
        "data": VALIDATORS,
    }

@app.get("/api/v1/validators/{address}")
async def validator_detail(address: str):
    for v in VALIDATORS:
        if v["address"] == address or v["address"][:10] in address or address[:10] in v["address"]:
            return {"success": True, "data": v}
    raise HTTPException(404, f"Validator {address} not found")


# --- DEX ---
@app.get("/api/v1/dex/pools")
async def dex_pools():
    try:
        pools_data = await rpc("amm_dex_getAllPools", [])
        if isinstance(pools_data, list):
            live_pools = []
            for idx, p in enumerate(pools_data):
                if isinstance(p, dict):
                    def bytes_to_str(v):
                        if isinstance(v, list):
                            return "".join(chr(b) for b in v if isinstance(b, int) and 0 <= b < 256)
                        return str(v)
                    pair = bytes_to_str(p.get("token_a", "A")) + "/" + bytes_to_str(p.get("token_b", "B"))
                    live_pools.append({
                        "id": idx,
                        "pair": pair,
                        "reserve_a": p.get("reserve_a", 0),
                        "reserve_b": p.get("reserve_b", 0),
                        "fee": "0.3%",
                        "tvl": (p.get("reserve_a", 0) + p.get("reserve_b", 0)),
                        "volume_24h": 0,
                    })
                else:
                    live_pools.append({"id": idx, "pair": str(p), "reserve_a": 0, "reserve_b": 0, "fee": "0.3%", "tvl": 0, "volume_24h": 0})
            return {"success": True, "count": len(live_pools), "data": live_pools}
    except Exception:
        pass
    return {
        "success": True,
        "count": len(DEX_POOLS),
        "data": DEX_POOLS,
    }

@app.get("/api/v1/dex/pools/{pool_id}")
async def dex_pool_detail(pool_id: int):
    for p in DEX_POOLS:
        if p["id"] == pool_id:
            return {"success": True, "data": p}
    raise HTTPException(404, f"Pool {pool_id} not found")

@app.get("/api/v1/dex/swaps")
async def dex_swaps(limit: int = Query(20, ge=1, le=100)):
    return {"success": True, "count": 0, "data": [], "message": "No recent swaps found"}


# --- Eco ---
@app.get("/api/v1/eco/metrics")
async def eco_metrics():
    total_credits = sum(c["amount_tons"] for c in CARBON_CREDITS)
    return {
        "success": True,
        "data": {
            "co2_offset_tons": (await rpc("eco_getTotalCO2Offset", []) or 0),
            "trees_planted": (await rpc("eco_getTotalTreesPlanted", []) or 0),
            "carbon_credits_minted": (await rpc("eco_getCarbonCreditCount", []) or 0),
            "total_credit_tons": total_credits,
            "avg_green_score": round(sum(v["green_score"] for v in VALIDATORS) / len(VALIDATORS), 1),
            "reforestation_logs": (await rpc("eco_getReforestProjectCount", []) or 0),
        }
    }

@app.get("/api/v1/eco/credits")
async def eco_credits():
    return {"success": True, "count": len(CARBON_CREDITS), "data": CARBON_CREDITS}

@app.get("/api/v1/eco/reforestation")
async def eco_reforestation():
    return {
        "success": True,
        "count": 3,
        "data": [
            {"id": 1, "location": "Amazon Basin", "trees": 250_000, "date": "2026-07-15", "block": 150},
            {"id": 2, "location": "Southeast Asia", "trees": 176_000, "date": "2026-07-22", "block": 300},
            {"id": 3, "location": "Central Africa", "trees": 100_000, "date": "2026-08-01", "block": 580},
        ]
    }


# --- Network ---
@app.get("/api/v1/stats")
@app.get("/api/v1/network/stats")
async def network_stats():
    block_height = await get_latest_block_number()
    health = await rpc("system_health")
    peers = health.get("peers", 0) if health else 0
    
    # Live validators from DPoS RPC
    validators = await get_live_validators()
    active_count = sum(1 for v in validators if isinstance(v, dict) and v.get("active", True) and not v.get("slashed", False))
    slashed_count = sum(1 for v in validators if isinstance(v, dict) and v.get("slashed", False))
    
    # Current epoch
    try:
        epoch_data = await rpc("dpos_currentEpoch", [])
        epoch = epoch_data if isinstance(epoch_data, int) else 0
    except Exception:
        epoch = 0
    
    # Finalized block
    try:
        finality = await rpc("chain_getFinalizedHead", [])
        finalized_hash = finality
        if finalized_hash:
            final_header = await rpc("chain_getHeader", [finalized_hash])
            finalized_block = int(final_header.get("number", "0x0"), 16) if final_header else 0
        else:
            finalized_block = max(block_height - 2, 0)
    except Exception:
        finalized_block = max(block_height - 2, 0)
    
    # Transaction count from SQLite indexer
    tx_count = await get_tx_count()
    
    # DEX pool count
    pools = await get_live_dex_pools()
    
    # Eco metrics
    try:
        eco = await rpc("eco_getTotalMetrics", [])
    except Exception:
        eco = None
    
    return {
        "success": True,
        "data": {
            "block_height": block_height,
            "finalized_block": finalized_block,
            "peers": peers,
            "validators": {
                "total": len(validators),
                "active": active_count,
                "slashed": slashed_count,
            },
            "epoch": epoch,
            "tx_count": tx_count,
            "dex_pools": len(pools),
            "eco_metrics": eco,
            "network": "testnet",
            "chain_name": "Verdis Chain",
        }
    }

@app.get("/api/v1/network/status")
async def network_status():
    name = await rpc("system_name")
    version = await rpc("system_version")
    health = await rpc("system_health")
    properties = await rpc("system_properties")
    peers = await rpc("system_peers")
    
    return {
        "success": True,
        "data": {
            "node_name": name or "verdis-node",
            "node_version": version or "unknown",
            "is_syncing": health.get("isSyncing", False) if health else False,
            "peers": len(peers) if peers else 0,
            "should_have_peers": health.get("shouldHavePeers", True) if health else True,
            "chain_properties": properties or {},
            "network": "testnet",
        }
    }



# ===========================================================================
# VERDISCAN PROFESSIONAL ENHANCEMENT — Solscan-parity endpoints
# Appended Aug 23 2026. Adds rich tx/block/account detail with decoded args,
# events, status, fees, SS58 addresses, and paginated history.
# ===========================================================================

import struct as _struct2
import hashlib as _hashlib3
import base58 as _b58

_SS58_PREFIX = 909

def _to_ss58(hex_addr):
    """Convert 0x-prefixed hex to SS58 address (Verdis format 909)."""
    if not hex_addr or not str(hex_addr).startswith("0x"):
        return hex_addr or ""
    try:
        raw = bytes.fromhex(hex_addr[2:])
        prefix_bytes = _SS58_PREFIX.to_bytes(2, "big")
        data = prefix_bytes + raw
        checksum = _hashlib3.blake2b(data, digest_size=2).digest()
        return _b58.b58encode(data + checksum).decode()
    except:
        return hex_addr

def _dec_compact(data, offset):
    """Decode SCALE compact integer. Uses BOTTOM 2 bits for mode."""
    if offset >= len(data):
        return 0, offset
    b = data[offset]
    mode = b & 0x03
    if mode == 0x00:
        return b >> 2, offset + 1
    elif mode == 0x01:
        return (b >> 2) | (data[offset+1] << 6), offset + 2
    elif mode == 0x02:
        return int.from_bytes(data[offset:offset+4], "little") >> 2, offset + 4
    else:
        n = (b >> 2) + 4
        return int.from_bytes(data[offset+1:offset+1+n], "little"), offset + 1 + n
def _events_storage_key():
    """System::Events storage key via twox_128."""
    import xxhash
    def twox(s):
        b = s.encode() if isinstance(s, str) else s
        h1 = xxhash.xxh64(b, seed=0).intdigest()
        h2 = xxhash.xxh64(b, seed=1).intdigest()
        return (h1.to_bytes(8, "little") + h2.to_bytes(8, "little")).hex()
    return "0x" + twox("System") + twox("Events")

async def _fetch_events(block_hash):
    """Fetch and decode System::Events for a block."""
    result = await rpc("state_getStorage", [_events_storage_key(), block_hash])
    if not result:
        return []
    try:
        raw = bytes.fromhex(result[2:] if result.startswith("0x") else result)
        count, off = _dec_compact(raw, 0)
        pallet_names = {0:"System",1:"Timestamp",2:"Babe",3:"Grandpa",4:"Balances",5:"TransactionPayment",
            7:"Session",8:"Scheduler",10:"Sudo",30:"Dpos",31:"AmmDex",32:"Eco",
            33:"Tokenomics",34:"Vesting",43:"Council",44:"Democracy",47:"Treasury",
            50:"FungibleTokens",58:"Presale"}
        ev_names = {
            "System": {0:"ExtrinsicSuccess",1:"ExtrinsicFailed",2:"CodeUpdated",3:"NewAccount",4:"KilledAccount"},
            "Balances": {0:"Transfer",1:"BalanceSet",2:"Deposit",3:"Withdraw",4:"TransferAll",5:"Slashed",6:"Rescinded",7:"Minted",8:"Burned"},
            "TransactionPayment": {0:"TransactionFeePaid"},
            "Dpos": {0:"ValidatorRegistered",1:"ValidatorSlashed",2:"EpochChanged",3:"ValidatorDeactivated",4:"RewardPoolDepleted",5:"BlockReward",6:"Delegated",7:"Undelegated"},
            "AmmDex": {0:"LiquidityAdded",1:"LiquidityRemoved",2:"SwapExecuted",3:"PoolCreated"},
            "Eco": {0:"CarbonCreditMinted",1:"CarbonCreditTransferred",2:"CarbonCreditRetired",3:"ReforestationLogged",4:"GreenScoreUpdated"},
            "Tokenomics": {0:"Minted",1:"Burned"},
            "Vesting": {0:"VestingScheduleCreated",1:"VestingClaimed"},
            "Sudo": {0:"Sudid"},
            "Council": {0:"Proposed",1:"Voted",2:"Closed",3:"Disapproved"},
            "Democracy": {0:"Proposed",1:"Tabled",2:"Started",3:"Passed",4:"NotPassed",5:"Cancelled"},
        }
        events = []
        for _ in range(min(count, 200)):
            if off >= len(raw): break
            try:
                ph = raw[off]; off += 1
                if ph == 0:
                    ext_idx, off = _dec_compact(raw, off)
                    phase = "Apply"
                elif ph == 1:
                    ext_idx = -1; phase = "Finalization"
                elif ph == 2:
                    ext_idx = -1; phase = "Init"
                else:
                    ext_idx = -1; phase = "Unknown"; off += 1
                if off + 1 >= len(raw): break
                pi = raw[off]; ei = raw[off+1]; off += 2
                pn = pallet_names.get(pi, f"Pallet{pi}")
                en = ev_names.get(pn, {}).get(ei, f"event_{ei}")
                ev = {"phase": phase, "extrinsic_index": ext_idx, "pallet": pn, "pallet_index": pi, "event": en, "event_index": ei}
                # Decode Transfer event (Balances.Transfer)
                if pn == "Balances" and en == "Transfer" and off + 64 <= len(raw):
                    ev["from"] = _to_ss58("0x" + raw[off:off+32].hex()); off += 32
                    ev["to"] = _to_ss58("0x" + raw[off:off+32].hex()); off += 32
                    amt, off = _dec_compact(raw, off)
                    ev["amount"] = amt
                    ev["amount_formatted"] = f"{amt / 1e9:,.4f} VRDX"
                elif pn == "Balances" and en == "Deposit" and off + 32 <= len(raw):
                    ev["who"] = _to_ss58("0x" + raw[off:off+32].hex()); off += 32
                    amt, off = _dec_compact(raw, off)
                    ev["amount"] = amt
                elif pn == "Balances" and en == "Withdraw" and off + 32 <= len(raw):
                    ev["who"] = _to_ss58("0x" + raw[off:off+32].hex()); off += 32
                    amt, off = _dec_compact(raw, off)
                    ev["amount"] = amt
                elif pn == "TransactionPayment" and en == "TransactionFeePaid" and off + 32 <= len(raw):
                    ev["who"] = _to_ss58("0x" + raw[off:off+32].hex()); off += 32
                    fee, off = _dec_compact(raw, off)
                    ev["fee"] = fee
                    ev["fee_formatted"] = f"{fee / 1e9:,.6f} VRDX"
                elif pn == "System" and en in ("NewAccount","KilledAccount") and off + 32 <= len(raw):
                    ev["account"] = _to_ss58("0x" + raw[off:off+32].hex()); off += 32
                elif pn == "System" and en == "ExtrinsicSuccess":
                    off += 10  # DispatchInfo
                elif pn == "System" and en == "ExtrinsicFailed":
                    off += 20  # DispatchError + DispatchInfo
                else:
                    off += 4
                # Skip topics
                tc, off = _dec_compact(raw, off)
                for _ in range(min(tc, 10)):
                    tl, off = _dec_compact(raw, off)
                    off += tl
                    if off > len(raw): break
                events.append(ev)
            except:
                break
        return events
    except:
        return []

def _decode_ext_v2(ext_bytes, index):
    """Enhanced extrinsic decoder with SS58 signer and decoded args."""
    if not ext_bytes:
        return {"index": index, "decoded": False}
    if isinstance(ext_bytes, list):
        ext_bytes = "0x" + "".join(b if isinstance(b, str) else format(b, "02x") for b in ext_bytes)
    hx = ext_bytes[2:] if ext_bytes.startswith("0x") else ext_bytes
    raw = bytes.fromhex(hx)
    if len(raw) < 4:
        return {"index": index, "decoded": False, "raw": ext_bytes}
    fb = raw[0]
    if (fb & 0x03) == 0x00: off = 1
    elif (fb & 0x03) == 0x01: off = 2
    elif (fb & 0x03) == 0x02: off = 4
    else: off = 1
    if off >= len(raw): return {"index": index, "decoded": False, "raw": ext_bytes}
    vb = raw[off]; is_signed = bool(vb & 0x80); ver = vb & 0x7F; off += 1
    signer = None; signer_ss58 = None; nonce = None; tip = 0
    if is_signed:
        at = raw[off]; off += 1
        if at == 0:
            signer = "0x" + raw[off:off+32].hex()
            signer_ss58 = _to_ss58(signer)
            off += 32
        elif at == 1:
            nv, off = _dec_compact(raw, off)
            signer = f"index:{nv}"
        else:
            off += 32
        if signer:
            st = raw[off]; off += 1  # MultiSignature variant (0=Ed25519, 1=Sr25519, 2=Ecdsa)
            off += 64 if st in (0, 1) else 65 if st == 2 else 64  # Signature bytes
            eb = raw[off]
            off += 1 if eb == 0 else 2
            nonce, off = _dec_compact(raw, off)
            try: tip, off = _dec_compact(raw, off)
            except: off += 1
    if off + 1 >= len(raw):
        return {"index": index, "hash": "0x" + _hashlib3.blake2b(raw, digest_size=32).hexdigest(),
                "is_signed": is_signed, "signer": signer, "signer_ss58": signer_ss58,
                "nonce": nonce, "tip": tip, "pallet": "Unknown", "call": "unknown",
                "method": "Unknown.unknown", "args": {}, "decoded": True, "raw": ext_bytes}
    pi = raw[off]; ci = raw[off+1]; off += 2
    pm = {0:"System",1:"Timestamp",2:"Babe",3:"Grandpa",4:"Balances",5:"TransactionPayment",
          7:"Session",8:"Scheduler",9:"Preimage",10:"Sudo",20:"Contracts",
          30:"Dpos",31:"AmmDex",32:"Eco",33:"Tokenomics",34:"Vesting",35:"Storage",
          36:"Utility",38:"Multisig",39:"Proxy",41:"Nfts",42:"Authorship",
          43:"Council",44:"Democracy",47:"Treasury",50:"FungibleTokens",
          58:"Presale",60:"CircuitBreaker",61:"TechnicalCommittee"}
    cm = {"System":{0:"remark",4:"killStorage"},
          "Timestamp":{0:"set"},
          "Balances":{0:"transfer",1:"setBalance",2:"forceTransfer",3:"transferKeepAlive",4:"transferAll"},
          "Session":{0:"setKeys",1:"purgeKeys"},
          "Sudo":{0:"sudo",1:"sudoAs",2:"setKey"},
          "Dpos":{0:"registerValidator",1:"delegate",2:"undelegate",3:"vote",4:"slash",
          5:"claimRewards",6:"setValidatorPrefs",7:"reactivateValidator"},
          "AmmDex":{0:"addLiquidity",1:"removeLiquidity",2:"swap",3:"createPool",4:"updateFee"},
          "Eco":{0:"mintCarbonCredit",1:"transferCarbonCredit",2:"retireCarbonCredit",
          3:"logReforestation",4:"updateGreenScore"},
          "Tokenomics":{0:"mint",1:"burn",2:"transfer"},
          "Vesting":{0:"createVestingSchedule",1:"claimVested",2:"cancelVesting"},
          "Presale":{0:"createRound",1:"finalizeRound",2:"participate",3:"claimTokens"}}
    pn = pm.get(pi, f"Pallet{pi}")
    cn = cm.get(pn, {}).get(ci, f"call_{ci}")
    method = f"{pn}.{cn}"
    args = {}
    try:
        if pn == "Balances" and cn in ("transfer","transferKeepAlive","forceTransfer"):
            dt = raw[off]; off += 1
            if dt == 0:
                args["dest"] = _to_ss58("0x" + raw[off:off+32].hex()); off += 32
            elif dt == 1:
                iv, off = _dec_compact(raw, off); args["dest"] = f"index:{iv}"
            else: off += 32
            amt, off = _dec_compact(raw, off)
            args["value"] = amt
            args["value_formatted"] = f"{amt / 1e9:,.4f} VRDX"
        elif pn == "Timestamp" and cn == "set":
            ts, off = _dec_compact(raw, off); args["timestamp"] = ts
        elif pn == "System" and cn == "remark":
            rl, off = _dec_compact(raw, off)
            if rl > 0 and off + rl <= len(raw):
                args["remark"] = raw[off:off+rl].decode("utf-8", errors="replace"); off += rl
        elif pn == "Dpos" and cn == "registerValidator":
            nl, off = _dec_compact(raw, off)
            if nl > 0 and off + nl <= len(raw):
                args["name"] = raw[off:off+nl].decode("utf-8", errors="replace"); off += nl
        elif pn == "Dpos" and cn == "delegate":
            if off + 32 <= len(raw):
                args["target"] = _to_ss58("0x" + raw[off:off+32].hex()); off += 32
            amt, off = _dec_compact(raw, off); args["amount"] = amt
        elif pn == "AmmDex" and cn == "swap":
            if off + 4 <= len(raw): args["pool_id"] = int.from_bytes(raw[off:off+4], "little"); off += 4
            ti, off = _dec_compact(raw, off); args["token_in"] = ti
            ai, off = _dec_compact(raw, off); args["amount_in"] = ai
            mo, off = _dec_compact(raw, off); args["min_out"] = mo
        elif pn == "AmmDex" and cn == "addLiquidity":
            if off + 4 <= len(raw): args["pool_id"] = int.from_bytes(raw[off:off+4], "little"); off += 4
            aa, off = _dec_compact(raw, off); args["amount_a"] = aa
            ab, off = _dec_compact(raw, off); args["amount_b"] = ab
        elif pn == "Session" and cn == "setKeys":
            kl, off = _dec_compact(raw, off)
            if kl > 0 and off + kl <= len(raw): args["keys"] = "0x" + raw[off:off+kl].hex(); off += kl
    except: pass
    ext_hash = "0x" + _hashlib3.blake2b(raw[1:] if (fb & 0xC0) == 0x00 else raw, digest_size=32).hexdigest()
    cat = "transfer" if "Balances.transfer" in method else "dex_swap" if "AmmDex.swap" in method else "dex" if "AmmDex" in method else "eco" if "Eco" in method else "validator" if "Dpos" in method else "sudo" if "Sudo" in method else "vesting" if "Vesting" in method else "presale" if "Presale" in method else "governance" if "Council" in method or "Democracy" in method else "other"
    return {"index": index, "hash": ext_hash, "is_signed": is_signed, "version": ver,
            "signer": signer, "signer_ss58": signer_ss58, "nonce": nonce, "tip": tip,
            "pallet": pn, "call": cn, "method": method, "category": cat, "args": args,
            "raw_hex": ext_bytes, "size_bytes": len(raw), "decoded": True}

# --- Enhanced TX Detail ---
@app.get("/api/v1/tx/{tx_hash}/detail")
async def tx_detail_rich(tx_hash: str):
    """Rich transaction detail: decoded args, SS58 signer, events, status, fee."""
    # Try SQLite first for fast lookup
    import sqlite3
    try:
        conn = sqlite3.connect(TX_DB_PATH)
        row = conn.execute("SELECT * FROM transactions WHERE tx_hash = ?", (tx_hash,)).fetchone()
        conn.close()
    except:
        row = None
    
    if row:
        block_num = row[1]
        ext_idx = row[2]
        raw_hex = row[10]
        block_hash = await rpc("chain_getBlockHash", [block_num])
        decoded = _decode_ext_v2(raw_hex, ext_idx)
        decoded["block"] = block_num
        decoded["block_hash"] = block_hash
        decoded["timestamp"] = row[11]
    else:
        # Scan recent blocks
        latest = await get_latest_block_number()
        found = False
        for i in range(latest, max(latest - 200, -1), -1):
            bh = await rpc("chain_getBlockHash", [i])
            if not bh: continue
            bd = await rpc("chain_getBlock", [bh])
            if not bd: continue
            exts = bd.get("block", {}).get("extrinsics", [])
            for j, ext in enumerate(exts):
                d = _decode_ext_v2(ext, j)
                if d.get("hash") == tx_hash:
                    decoded = d
                    decoded["block"] = i
                    decoded["block_hash"] = bh
                    found = True
                    break
            if found: break
        if not found:
            raise HTTPException(404, "Transaction not found")
    
    # Fetch events
    events = await _fetch_events(decoded.get("block_hash"))
    tx_events = [e for e in events if e.get("extrinsic_index") == decoded.get("index")]
    decoded["events"] = tx_events
    
    # Status
    if any(e.get("event") == "ExtrinsicSuccess" for e in tx_events):
        decoded["status"] = "success"
    elif any(e.get("event") == "ExtrinsicFailed" for e in tx_events):
        decoded["status"] = "failed"
    else:
        decoded["status"] = "unknown"
    
    # Fee
    fee_events = [e for e in tx_events if e.get("event") == "TransactionFeePaid"]
    if fee_events:
        decoded["fee"] = fee_events[0].get("fee", 0)
        decoded["fee_formatted"] = fee_events[0].get("fee_formatted", "")
    
    # Transfer info from events
    transfer_events = [e for e in tx_events if e.get("event") == "Transfer"]
    if transfer_events:
        decoded["transfer"] = transfer_events[0]
        if not decoded.get("args", {}).get("dest"):
            te = transfer_events[0]
            if "args" not in decoded: decoded["args"] = {}
            decoded["args"]["from"] = te.get("from", "")
            decoded["args"]["dest"] = te.get("to", "")
            decoded["args"]["value"] = te.get("amount", 0)
            decoded["args"]["value_formatted"] = te.get("amount_formatted", "")
    
    # Confirmations
    latest = await get_latest_block_number()
    decoded["confirmations"] = latest - decoded.get("block", 0)
    
    return {"success": True, "data": decoded}

# --- Enhanced Block Detail ---
@app.get("/api/v1/block/{block_number}/detail")
async def block_detail_rich(block_number: int):
    """Rich block detail: decoded extrinsics, events, author, signed tx count."""
    block_hash = await rpc("chain_getBlockHash", [block_number])
    if not block_hash:
        raise HTTPException(404, "Block not found")
    
    block_data = await rpc("chain_getBlock", [block_hash])
    if not block_data:
        raise HTTPException(404, "Block not found")
    
    header = block_data.get("block", {}).get("header", {})
    exts_raw = block_data.get("block", {}).get("extrinsics", [])
    
    # Decode all extrinsics
    decoded_exts = [_decode_ext_v2(ext, i) for i, ext in enumerate(exts_raw)]
    
    # Fetch events
    events = await _fetch_events(block_hash)
    
    # Map events to extrinsics
    for ext in decoded_exts:
        ext_evs = [e for e in events if e.get("extrinsic_index") == ext["index"]]
        ext["events"] = ext_evs
        if any(e.get("event") == "ExtrinsicSuccess" for e in ext_evs):
            ext["status"] = "success"
        elif any(e.get("event") == "ExtrinsicFailed" for e in ext_evs):
            ext["status"] = "failed"
        else:
            ext["status"] = "unknown"
        # Transfer events
        transfers = [e for e in ext_evs if e.get("event") == "Transfer"]
        if transfers and not ext.get("args", {}).get("dest"):
            te = transfers[0]
            if "args" not in ext: ext["args"] = {}
            ext["args"]["from"] = te.get("from", "")
            ext["args"]["dest"] = te.get("to", "")
            ext["args"]["value"] = te.get("amount", 0)
            ext["args"]["value_formatted"] = te.get("amount_formatted", "")
    
    signed_count = sum(1 for e in decoded_exts if e.get("is_signed"))
    
    # Extract timestamp
    timestamp = None
    for ext in decoded_exts:
        if ext.get("pallet") == "Timestamp" and ext.get("args", {}).get("timestamp"):
            timestamp = ext["args"]["timestamp"]
            break
    
    # Block author from BABE digest
    author = None
    author_ss58 = None
    for log in header.get("digest", {}).get("logs", []):
        if isinstance(log, str) and log.startswith("0x0642414245"):
            try:
                lb = bytes.fromhex(log[2:])
                if len(lb) > 7:
                    variant = lb[5]
                    if variant == 1 and len(lb) > 8:
                        auth_idx = int.from_bytes(lb[6:8], "little")
                        vals = await rpc("dpos_allValidators", [])
                        if vals and auth_idx < len(vals):
                            author = vals[auth_idx]
                            author_ss58 = vals[auth_idx]
            except: pass
            break
    
    return {
        "success": True,
        "data": {
            "number": block_number,
            "hash": block_hash,
            "parent_hash": header.get("parentHash"),
            "state_root": header.get("stateRoot"),
            "extrinsics_root": header.get("extrinsicsRoot"),
            "digest_logs": header.get("digest", {}).get("logs", []),
            "extrinsics_count": len(exts_raw),
            "signed_tx_count": signed_count,
            "timestamp": timestamp,
            "author": author,
            "author_ss58": author_ss58,
            "extrinsics": decoded_exts,
            "events": events,
            "event_count": len(events),
        }
    }

# --- Account History (paginated) ---
@app.get("/api/v1/account/{address}/history")
async def account_tx_history(address: str, limit: int = 20, offset: int = 0):
    """Paginated transaction history for an account from SQLite index."""
    import sqlite3
    try:
        ss58_bytes = _b58.b58decode(address)
        if len(ss58_bytes) == 36:
            addr_hex = "0x" + ss58_bytes[2:34].hex()
        else:
            addr_hex = "0x" + ss58_bytes[1:33].hex()
    except:
        addr_hex = address
    
    conn = sqlite3.connect(TX_DB_PATH)
    total = conn.execute("SELECT COUNT(*) FROM transactions WHERE signer = ?", (addr_hex,)).fetchone()[0]
    rows = conn.execute(
        "SELECT block_number, tx_index, tx_hash, signer, method, pallet, call_name, value, category, raw_hex, timestamp FROM transactions WHERE signer = ? ORDER BY block_number DESC LIMIT ? OFFSET ?",
        (addr_hex, limit, offset)
    ).fetchall()
    conn.close()
    
    txs = []
    for r in rows:
        txs.append({
            "block": r[0], "index": r[1], "hash": r[2], "signer": _to_ss58(r[3]),
            "method": r[4], "pallet": r[5], "call": r[6], "value": r[7],
            "category": r[8], "timestamp": r[10]
        })
    
    return {"success": True, "count": len(txs), "total": total, "offset": offset, "limit": limit, "data": txs}

# --- Recent Transfers ---
@app.get("/api/v1/transfers/recent")
async def recent_transfers(limit: int = 20):
    """Recent transfer transactions from SQLite index."""
    import sqlite3
    conn = sqlite3.connect(TX_DB_PATH)
    rows = conn.execute(
        "SELECT block_number, tx_index, tx_hash, signer, method, pallet, call_name, value, category, raw_hex, timestamp FROM transactions WHERE category = ? ORDER BY block_number DESC LIMIT ?",
        ("transfer", limit)
    ).fetchall()
    conn.close()
    
    txs = []
    for r in rows:
        d = _decode_ext_v2(r[9], r[1])
        d["block"] = r[0]
        d["timestamp"] = r[10]
        txs.append(d)
    
    return {"success": True, "count": len(txs), "data": txs}

# --- Account TX Count ---
@app.get("/api/v1/account/{address}/txcount")
async def account_tx_count(address: str):
    """Transaction count for an account from SQLite index."""
    import sqlite3
    try:
        ss58_bytes = _b58.b58decode(address)
        if len(ss58_bytes) == 36:
            addr_hex = "0x" + ss58_bytes[2:34].hex()
        else:
            addr_hex = "0x" + ss58_bytes[1:33].hex()
    except:
        addr_hex = address
    
    conn = sqlite3.connect(TX_DB_PATH)
    count = conn.execute("SELECT COUNT(*) FROM transactions WHERE signer = ?", (addr_hex,)).fetchone()[0]
    conn.close()
    
    return {"success": True, "data": {"address": address, "tx_count": count}}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=4400, log_level="info")