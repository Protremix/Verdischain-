#!/usr/bin/env python3
"""
Verdis Chain Validator Monitor v1.0
Tracks per-validator block production, uptime, and performance metrics.
Outputs to /var/log/validator-monitor.json for web dashboard consumption.
"""
import json, time, os, subprocess, sys
from datetime import datetime

RPC = "http://127.0.0.1:9933"
LOG_FILE = "/var/log/validator-monitor.json"
HISTORY_FILE = "/var/log/validator-blocks.history"
RPC_TIMEOUT = 5

def rpc(method, params=None):
    """Make a JSON-RPC call to the node."""
    payload = json.dumps({
        "jsonrpc": "2.0",
        "method": method,
        "params": params or [],
        "id": 1
    })
    try:
        result = subprocess.run(
            ["curl", "-sf", "-X", "POST", RPC, "-H", "Content-Type: application/json",
             "-d", payload, "--connect-timeout", str(RPC_TIMEOUT)],
            capture_output=True, text=True, timeout=RPC_TIMEOUT + 5
        )
        if result.returncode == 0 and result.stdout:
            return json.loads(result.stdout).get("result")
    except:
        pass
    return None

def get_validators():
    """Get all registered validators with their stakes and green scores."""
    validators = rpc("dpos_allValidators", []) or []
    green_scores = {}
    
    # Try to get green scores
    for i in range(len(validators)):
        addr = validators[i] if isinstance(validators[i], str) else validators[i]
        score = rpc("eco_getGreenScore", [addr])
        if score is not None:
            green_scores[addr] = score
    
    # Get stakes
    result = []
    for addr in validators:
        addr_str = addr if isinstance(addr, str) else str(addr)
        stake = rpc("dpos_validatorStake", [addr_str]) or 0
        name = rpc("dpos_validatorName", [addr_str]) or ""
        result.append({
            "address": addr_str,
            "stake": stake,
            "green_score": green_scores.get(addr_str, 0),
            "name": name if isinstance(name, str) else "",
        })
    return result

def get_block_author(block_hash):
    """Get the author of a specific block."""
    header = rpc("chain_getHeader", [block_hash])
    if not header:
        return None
    # The author is encoded in the block logs (BABE pre-digest)
    logs = header.get("digest", {}).get("logs", [])
    for log in logs:
        if isinstance(log, str) and len(log) > 6:
            # Try to extract author from BABE pre-digest
            # The author public key is embedded in the seal
            pass
    return None

def get_session_validators():
    """Get the current session validators (active block producers)."""
    return rpc("session_validators", []) or []

def main():
    print("Starting Verdis Validator Monitor v1.0", flush=True)
    
    # Load existing history
    block_history = {}
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE) as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        block_history[entry["address"]] = block_history.get(entry["address"], 0) + 1
                    except:
                        pass
        except:
            pass
    
    last_block = 0
    uptime_start = time.time()
    
    while True:
        try:
            ts = datetime.utcnow().isoformat() + "Z"
            
            # Get current block
            header = rpc("chain_getHeader", [])
            if not header:
                time.sleep(15)
                continue
            
            block_num = int(header.get("number", "0x0"), 16)
            block_hash = header.get("parentHash", "")
            
            # Get all validators
            all_validators = get_validators()
            session_validators = get_session_validators()
            session_set = set(v if isinstance(v, str) else str(v) for v in session_validators)
            
            # Get node health
            health = rpc("system_health", [])
            peers = health.get("peers", 0) if health else 0
            
            # Get DEX stats
            pool_count = rpc("amm_dex_getPoolCount", []) or 0
            
            # Build monitoring data
            monitor_data = {
                "timestamp": ts,
                "block_height": block_num,
                "peers": peers,
                "total_validators": len(all_validators),
                "active_validators": len(session_validators),
                "pools": pool_count,
                "uptime_seconds": int(time.time() - uptime_start),
                "validators": []
            }
            
            for v in all_validators:
                addr = v["address"]
                is_active = addr in session_set
                monitor_data["validators"].append({
                    "address": addr,
                    "name": v["name"],
                    "stake": v["stake"],
                    "green_score": v["green_score"],
                    "is_active": is_active,
                    "blocks_produced": block_history.get(addr, 0),
                })
            
            # Write to JSON file (for web dashboard)
            with open(LOG_FILE, "w") as f:
                json.dump(monitor_data, f, indent=2)
            
            # Log block progression
            if block_num > last_block:
                print(f"[{ts}] Block #{block_num} | {len(all_validators)} validators | {len(session_validators)} active | {peers} peers | {pool_count} pools", flush=True)
                last_block = block_num
        
        except Exception as e:
            print(f"Error: {e}", flush=True)
        
        time.sleep(15)

if __name__ == "__main__":
    main()
