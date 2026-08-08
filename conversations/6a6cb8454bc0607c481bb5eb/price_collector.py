#!/usr/bin/env python3
"""Price history collector for Verdis Chain DEX pools.
Samples pool prices every 30 seconds and saves to /var/www/verdiscan/price-history.json"""

import json
import time
import os
import subprocess
from datetime import datetime, timezone

RPC_URL = "http://localhost:9933"
HISTORY_FILE = "/var/www/verdiscan/price-history.json"
MAX_POINTS = 2880  # 24 hours at 30s intervals

def rpc_call(method, params=None):
    """Make a JSON-RPC call to the local node."""
    if params is None:
        params = []
    payload = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params
    })
    result = subprocess.run([
        "curl", "-s", "-X", "POST", RPC_URL,
        "-H", "Content-Type: application/json",
        "-d", payload
    ], capture_output=True, text=True)
    try:
        return json.loads(result.stdout)
    except:
        return None

def bytes_to_str(b):
    """Convert byte array to ASCII string."""
    if isinstance(b, str):
        return b
    if isinstance(b, list):
        return "".join(chr(int(x)) for x in b)
    return str(b)

def get_block_height():
    """Get current block height."""
    resp = rpc_call("chain_getBlock")
    if resp and "result" in resp:
        return int(resp["result"]["block"]["header"]["number"], 16)
    return 0

def get_all_pools():
    """Get all DEX pools with reserves."""
    resp = rpc_call("amm_dex_getAllPools")
    if resp and "result" in resp:
        return resp["result"]
    return []

def collect_price_point():
    """Collect a single price data point from all pools."""
    block = get_block_height()
    pools = get_all_pools()
    
    tokens = {}
    pool_data = []
    
    for pool in pools:
        token_a = bytes_to_str(pool.get("token_a"))
        token_b = bytes_to_str(pool.get("token_b"))
        reserve_a = int(pool.get("reserve_a", 0))
        reserve_b = int(pool.get("reserve_b", 0))
        
        # Price of token_b in terms of token_a
        price = reserve_b / reserve_a if reserve_a > 0 else 0
        
        # TVL in token_a terms
        tvl = reserve_a + reserve_b  # simplified
        
        pool_entry = {
            "pair": f"{token_a}/{token_b}",
            "token_a": token_a,
            "token_b": token_b,
            "reserve_a": reserve_a,
            "reserve_b": reserve_b,
            "price": price,
            "tvl": tvl
        }
        pool_data.append(pool_entry)
        
        # Track token prices relative to VRDX
        if token_a == "VRDX":
            tokens[token_b] = price  # 1 VRDX = price token_b
        elif token_b == "VRDX":
            tokens[token_a] = 1.0 / price if price > 0 else 0  # 1 VRDX = 1/price token_a
    
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "block": block,
        "tokens": tokens,
        "pools": pool_data
    }

def load_history():
    """Load existing price history."""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {"history": [], "started": datetime.now(timezone.utc).isoformat()}

def save_history(data):
    """Save price history to file."""
    tmp_file = HISTORY_FILE + ".tmp"
    with open(tmp_file, "w") as f:
        json.dump(data, f)
    os.rename(tmp_file, HISTORY_FILE)

def main():
    print(f"Price history collector started. Saving to {HISTORY_FILE}")
    print(f"Sampling every 30 seconds. Max {MAX_POINTS} points (24h).")
    
    data = load_history()
    
    while True:
        try:
            point = collect_price_point()
            data["history"].append(point)
            
            # Trim to max points
            if len(data["history"]) > MAX_POINTS:
                data["history"] = data["history"][-MAX_POINTS:]
            
            save_history(data)
            
            tokens_str = ", ".join(f"{k}: {v:.4f}" for k, v in point["tokens"].items())
            print(f"[{point['timestamp']}] Block #{point['block']} | {tokens_str} | {len(point['pools'])} pools")
            
        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(30)

if __name__ == "__main__":
    main()
