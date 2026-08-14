#!/usr/bin/env python3
"""ARCH-030: Genesis Consistency CI Check
Verifies chain_spec.rs allocations match canonical tokenomics.
"""
import re
import sys

def extract_allocations(path):
    with open(path, "r") as f:
        lines = f.readlines()
    
    # Find the mainnet_genesis function start
    start_line = None
    for i, line in enumerate(lines):
        if "fn mainnet_genesis" in line:
            start_line = i
            break
    
    if start_line is None:
        print("ERROR: mainnet_genesis not found")
        return {}
    
    # Find the end (next RuntimeGenesisConfig or end of file)
    end_line = len(lines)
    for i in range(start_line + 1, len(lines)):
        if "verdis_runtime::RuntimeGenesisConfig" in lines[i]:
            end_line = i
            break
    
    section = "".join(lines[start_line:end_line])
    
    var_map = {
        "eco_pool": "Ecosystem",
        "staking_pool": "Staking",
        "treasury_account": "Treasury",
        "dev_pool": "Development",
        "dex_pool": "Liquidity",
        "community_pool": "Community",
        "seed_pool": "Seed",
        "presale_pool": "Presale",
    }
    
    allocations = {}
    for var, name in var_map.items():
        # Match patterns like: (eco_pool, 25 * bn)
        pattern = r"\(" + re.escape(var) + r",\s*(\d+)\s*\*\s*bn\)"
        m = re.search(pattern, section)
        if m:
            allocations[name] = int(m.group(1))
    
    # Team is special: 5 * bn - ...
    team_match = re.search(r"team_multisig\.clone\(\),\s*\n\s*5\s*\*\s*bn", section)
    if team_match:
        allocations["Team"] = 5
    
    return allocations

def main():
    path = "node/src/chain_spec.rs"
    try:
        allocations = extract_allocations(path)
    except FileNotFoundError:
        print(f"ERROR: {path} not found")
        sys.exit(1)
    
    if not allocations:
        print("ERROR: Could not extract allocations")
        sys.exit(1)
    
    expected = {
        "Ecosystem": 25, "Staking": 20, "Treasury": 20,
        "Development": 10, "Liquidity": 10, "Community": 5,
        "Seed": 3, "Presale": 2, "Team": 5,
    }
    
    all_ok = True
    total = 0
    for name, exp_val in expected.items():
        actual = allocations.get(name)
        if actual is None:
            print(f"FAIL: {name} not found")
            all_ok = False
        elif actual != exp_val:
            print(f"FAIL: {name} expected {exp_val}B got {actual}B")
            all_ok = False
        else:
            print(f"OK: {name} = {actual}B")
            total += actual
    
    if total != 100:
        print(f"FAIL: Total {total}B expected 100B")
        all_ok = False
    else:
        print(f"OK: Total = 100B")
    
    if all_ok:
        print("ALL CONSISTENT")
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
