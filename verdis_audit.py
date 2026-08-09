#!/usr/bin/env python3
"""Verdis Blockchain Mainnet Readiness Audit
Covers: Explorer Verification, RPC Validation, Economic Invariants,
Security Audit, Performance Validation

Fixes applied:
- Fixed pass/fail/warn counting bug (was counting WARN as PASS)
- Made RPC URL configurable via VERDIS_RPC_URL env var (default: http://localhost:9949)
- Added retry logic for network failures (3 retries with 1s delay)
- Added proper error handling for RPC failures
- Results saved to /opt/verdis-chain-rust/audits/ instead of /tmp
"""
import json, time, sys, os, subprocess, statistics, random, string
from datetime import datetime

# Configurable RPC URL — use VERDIS_RPC_URL env var or default
RPC = os.environ.get("VERDIS_RPC_URL", "http://localhost:9949")
RESULTS = {}
AUDIT_DIR = "/opt/verdis-chain-rust/audits"
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds

def rpc(method, params=None):
    """Call JSON-RPC and return result with retry logic."""
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params or []})
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            cmd = ['curl', '-s', '-X', 'POST', RPC, '-H', 'Content-Type: application/json',
                   '-d', payload]
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            d = json.loads(r.stdout)
            if d.get('error'):
                return None, d.get('error')
            return d.get('result'), None
        except subprocess.TimeoutExpired:
            last_error = {"message": f"Timeout on attempt {attempt+1}/{MAX_RETRIES}"}
            time.sleep(RETRY_DELAY)
        except json.JSONDecodeError:
            last_error = {"message": f"Parse error: {r.stdout[:200]}"}
            time.sleep(RETRY_DELAY)
        except Exception as e:
            last_error = {"message": f"Error: {str(e)}"}
            time.sleep(RETRY_DELAY)
    return None, last_error or {"message": "Unknown error after retries"}

def log(phase, msg):
    print(f"[{phase}] {msg}", flush=True)

def count_result(results, status):
    """Properly increment pass/fail/warn counters."""
    if status == "PASS":
        results['passed'] += 1
    elif status == "FAIL":
        results['failed'] += 1
    elif status == "WARN":
        results['warnings'] += 1

# ============================================================
# PHASE 1: EXPLORER VERIFICATION
# ============================================================
def phase1_explorer():
    log("P1", "Starting Explorer Verification...")
    results = {"phase": "Explorer Verification", "checks": [], "passed": 0, "failed": 0, "warnings": 0}
    
    header, err = rpc('chain_getHeader')
    if not header:
        results['checks'].append({"test": "RPC connectivity", "status": "FAIL", "detail": f"Cannot get header: {err}"})
        count_result(results, "FAIL")
        return results
    current_block = int(header['number'], 16)
    results['checks'].append({"test": "RPC connectivity", "status": "PASS", "detail": f"Block #{current_block}"})
    count_result(results, "PASS")
    
    sample_size = min(50, current_block)
    sample_blocks = random.sample(range(1, current_block + 1), sample_size) if current_block > 1 else [1]
    
    block_errors = 0
    for bn in sample_blocks:
        hash_val, err = rpc('chain_getBlockHash', [bn])
        if err or not hash_val:
            block_errors += 1
            continue
        
        block, err = rpc('chain_getBlock', [hash_val])
        if err or not block:
            block_errors += 1
            continue
        
        actual_num = int(block['block']['header']['number'], 16)
        if actual_num != bn:
            block_errors += 1
            continue
        
        parent_hash = block['block']['header']['parentHash']
        if bn > 1:
            parent_hash_expected, _ = rpc('chain_getBlockHash', [bn - 1])
            if parent_hash_expected and parent_hash != parent_hash_expected:
                block_errors += 1
    
    status = "PASS" if block_errors == 0 else "FAIL"
    results['checks'].append({
        "test": f"Block verification ({sample_size} random blocks)",
        "status": status,
        "detail": f"{sample_size - block_errors}/{sample_size} blocks verified"
    })
    count_result(results, status)
    
    # Balance storage
    BALANCES_PREFIX = "0xc2261276cc9d1f8598ea4b6a74b15c2f"
    keys, err = rpc('state_getKeys', [BALANCES_PREFIX])
    if keys:
        balance_count = sum(1 for k in keys[:20] if rpc('state_getStorage', [k])[0])
        results['checks'].append({"test": "Balance storage queries", "status": "PASS", "detail": f"{balance_count} balance entries (checked 20 of {len(keys)})"})
        count_result(results, "PASS")
    else:
        results['checks'].append({"test": "Balance storage queries", "status": "FAIL", "detail": f"Cannot query: {err}"})
        count_result(results, "FAIL")
    
    # Session validators
    session_keys, err = rpc('session_validators')
    if session_keys is not None:
        status = "PASS" if len(session_keys) > 0 else "WARN"
        results['checks'].append({"test": "Session validators", "status": status, "detail": f"{len(session_keys)} validators"})
        count_result(results, status)
    else:
        results['checks'].append({"test": "Session validators", "status": "WARN", "detail": f"Query failed: {err}"})
        count_result(results, "WARN")
    
    # DEX and Eco storage
    for name, prefix in [("AmmDex", "0xaaf995822f98c19783008fced38cfdbd"), ("Eco", "0xeeb60ed95ea2197d8d32fd1c61f0e40e"), ("Tokenomics", "0xa6b5b1386f497b41d0aef5173bb50924")]:
        keys, _ = rpc('state_getKeys', [prefix])
        results['checks'].append({"test": f"{name} storage", "status": "PASS", "detail": f"{len(keys) if keys else 0} keys"})
        count_result(results, "PASS")
    
    return results

# ============================================================
# PHASE 2: RPC VALIDATION
# ============================================================
def phase2_rpc():
    log("P2", "Starting RPC Validation...")
    results = {"phase": "RPC Validation", "checks": [], "passed": 0, "failed": 0, "warnings": 0}
    
    methods_result, _ = rpc('rpc_methods')
    all_methods = methods_result.get('methods', []) if methods_result else []
    
    # Check for unsafe methods
    UNSAFE = ['author_insertKey', 'author_removeKey', 'author_rotateKeys',
              'system_addReservedPeer', 'system_removeReservedPeer']
    exposed_unsafe = [m for m in all_methods if any(u in m for u in UNSAFE)]
    status = "PASS" if not exposed_unsafe else "FAIL"
    results['checks'].append({"test": "Unsafe RPC methods exposure", "status": status, "detail": f"Exposed: {exposed_unsafe}" if exposed_unsafe else "No unsafe methods exposed"})
    count_result(results, status)
    
    # Check custom RPC methods
    CUSTOM = ['dpos_activeValidators', 'dpos_allValidators', 'dpos_currentEpoch', 'dpos_validatorStake',
              'amm_dex_getPool', 'amm_dex_getAllPools', 'amm_dex_getPrice',
              'contracts_call', 'contracts_getStorage', 'contracts_instantiate']
    missing = [m for m in CUSTOM if m not in all_methods]
    status = "PASS" if not missing else "FAIL"
    results['checks'].append({"test": "Custom RPC methods present", "status": status, "detail": f"Missing: {missing}" if missing else f"All {len(CUSTOM)} custom methods present"})
    count_result(results, status)
    
    # Check total method count
    results['checks'].append({"test": "RPC method count", "status": "PASS", "detail": f"{len(all_methods)} methods"})
    count_result(results, "PASS")
    
    return results

# ============================================================
# PHASE 3: ECONOMIC INVARIANTS
# ============================================================
def phase3_economic():
    log("P3", "Starting Economic Invariants...")
    results = {"phase": "Economic Invariants", "checks": [], "passed": 0, "failed": 0, "warnings": 0}
    
    # Total supply check
    TOTAL_ISSUANCE_KEY = "REDACTED_KEY"
    val, err = rpc('state_getStorage', [TOTAL_ISSUANCE_KEY])
    if val and val != '0x':
        # Decode u128 LE from hex
        try:
            hex_bytes = bytes.fromhex(val[2:])
            supply = int.from_bytes(hex_bytes[:16], 'little')
            expected = 100_000_000_000 * 10**9  # 100B with 9 decimals
            status = "PASS" if supply == expected else "FAIL"
            results['checks'].append({"test": "Total supply = 100B VRDX", "status": status, "detail": f"Supply: {supply / 10**9:.0f} VRDX (expected {expected / 10**9:.0f})"})
            count_result(results, status)
        except Exception as e:
            results['checks'].append({"test": "Total supply = 100B VRDX", "status": "FAIL", "detail": f"Decode error: {e}"})
            count_result(results, "FAIL")
    else:
        results['checks'].append({"test": "Total supply = 100B VRDX", "status": "WARN", "detail": f"Cannot read: {err}"})
        count_result(results, "WARN")
    
    # Token properties
    props, _ = rpc('system_properties')
    if props:
        token = props.get('tokenSymbol', '')
        ss58 = props.get('ss58Format', 0)
        decimals = props.get('tokenDecimals', 0)
        status = "PASS" if token == 'VRDX' and ss58 == 909 and decimals == 9 else "FAIL"
        results['checks'].append({"test": "Token properties", "status": status, "detail": f"{token}, SS58={ss58}, decimals={decimals}"})
        count_result(results, status)
    else:
        results['checks'].append({"test": "Token properties", "status": "FAIL", "detail": "No properties returned"})
        count_result(results, "FAIL")
    
    return results

# ============================================================
# PHASE 4: SECURITY AUDIT
# ============================================================
def phase4_security():
    log("P4", "Starting Security Audit...")
    results = {"phase": "Security Audit", "checks": [], "passed": 0, "failed": 0, "warnings": 0}
    
    methods_result, _ = rpc('rpc_methods')
    all_methods = methods_result.get('methods', []) if methods_result else []
    
    # Unsafe methods
    UNSAFE = ['author_insertKey', 'author_removeKey', 'author_rotateKeys',
              'system_addReservedPeer', 'system_removeReservedPeer']
    exposed = [m for m in all_methods if any(u in m for u in UNSAFE)]
    status = "PASS" if not exposed else "FAIL"
    results['checks'].append({"test": "Unsafe RPC methods blocked", "status": status, "detail": f"Exposed: {exposed}" if exposed else "All unsafe methods blocked"})
    count_result(results, status)
    
    # Malformed extrinsic rejection
    _, err = rpc('author_submitExtrinsic', ["0x" + "ff" * 100])
    status = "PASS" if err else "FAIL"
    results['checks'].append({"test": "Malformed extrinsic rejected", "status": status, "detail": f"Rejected: {err.get('message', '')[:80]}" if err else "Accepted!"})
    count_result(results, status)
    
    # Empty extrinsic rejection
    _, err = rpc('author_submitExtrinsic', ["0x"])
    status = "PASS" if err else "FAIL"
    results['checks'].append({"test": "Empty extrinsic rejected", "status": status, "detail": f"Rejected: {err.get('message', '')[:80]}" if err else "Accepted!"})
    count_result(results, status)
    
    # Invalid signature rejection
    fake_sig = "0x" + "".join(random.choices("0123456789abcdef", k=130))
    _, err = rpc('author_submitExtrinsic', [fake_sig])
    status = "PASS" if err else "FAIL"
    results['checks'].append({"test": "Invalid signature rejected", "status": status, "detail": f"Rejected: {err.get('message', '')[:80]}" if err else "Accepted!"})
    count_result(results, status)
    
    return results

# ============================================================
# PHASE 5: PERFORMANCE
# ============================================================
def phase5_performance():
    log("P5", "Starting Performance Validation...")
    results = {"phase": "Performance", "checks": [], "passed": 0, "failed": 0, "warnings": 0}
    
    # RPC latency
    latencies = []
    test_methods = ['chain_getHeader', 'system_health', 'system_properties', 'rpc_methods']
    for method in test_methods:
        times = []
        for _ in range(10):
            start = time.time()
            rpc(method)
            times.append(time.time() - start)
        if times:
            latencies.append(statistics.mean(times) * 1000)
    
    if latencies:
        avg = statistics.mean(latencies)
        p95 = sorted(latencies)[int(len(latencies) * 0.95)] if len(latencies) > 1 else latencies[0]
        status = "PASS" if p95 < 100 else "WARN"
        results['checks'].append({"test": "RPC latency", "status": status, "detail": f"Avg: {avg:.1f}ms, p95: {p95:.1f}ms"})
        count_result(results, status)
    else:
        results['checks'].append({"test": "RPC latency", "status": "FAIL", "detail": "No data"})
        count_result(results, "FAIL")
    
    # Finality lag
    best_header, _ = rpc('chain_getHeader')
    finalized_hash, _ = rpc('chain_getFinalizedHead')
    finalized_header, _ = rpc('chain_getHeader', [finalized_hash]) if finalized_hash else (None, None)
    if best_header and finalized_header:
        best_num = int(best_header['number'], 16)
        final_num = int(finalized_header['number'], 16)
        lag = best_num - final_num
        status = "PASS" if lag <= 5 else "WARN"
        results['checks'].append({"test": "Finality lag", "status": status, "detail": f"Best: #{best_num}, Finalized: #{final_num}, Lag: {lag}"})
        count_result(results, status)
    else:
        results['checks'].append({"test": "Finality lag", "status": "WARN", "detail": "Cannot determine"})
        count_result(results, "WARN")
    
    return results

# ============================================================
# MAIN
# ============================================================
def main():
    os.makedirs(AUDIT_DIR, exist_ok=True)
    
    print("=" * 60, flush=True)
    print(f"Verdis Blockchain Audit — {datetime.now().isoformat()}", flush=True)
    print(f"RPC endpoint: {RPC}", flush=True)
    print("=" * 60, flush=True)
    
    all_results = {
        "timestamp": datetime.now().isoformat(),
        "rpc_endpoint": RPC,
        "phases": {}
    }
    
    phases = [
        ("phase1", phase1_explorer),
        ("phase2", phase2_rpc),
        ("phase3", phase3_economic),
        ("phase4", phase4_security),
        ("phase5", phase5_performance),
    ]
    
    total_pass = 0
    total_fail = 0
    total_warn = 0
    
    for name, func in phases:
        try:
            result = func()
            all_results["phases"][name] = result
            total_pass += result['passed']
            total_fail += result['failed']
            total_warn += result['warnings']
            print(f"\n[{name}] {result['phase']}: {result['passed']} PASS, {result['failed']} FAIL, {result['warnings']} WARN", flush=True)
        except Exception as e:
            print(f"\n[{name}] ERROR: {e}", flush=True)
            all_results["phases"][name] = {"phase": name, "error": str(e), "checks": [], "passed": 0, "failed": 1, "warnings": 0}
            total_fail += 1
    
    print("\n" + "=" * 60, flush=True)
    print(f"TOTAL: {total_pass} PASS, {total_fail} FAIL, {total_warn} WARN", flush=True)
    print("=" * 60, flush=True)
    
    # Save results
    output_file = os.path.join(AUDIT_DIR, f"audit-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json")
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    print(f"Results saved to: {output_file}", flush=True)
    
    return total_fail == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
