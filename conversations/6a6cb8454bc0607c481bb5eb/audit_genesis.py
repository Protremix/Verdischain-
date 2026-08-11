import json, os, xxhash

def twox128(data):
    h1 = xxhash.xxh64(data.encode(), seed=0).intdigest()
    h2 = xxhash.xxh64(data.encode(), seed=1).intdigest()
    return h1.to_bytes(8, "little").hex() + h2.to_bytes(8, "little").hex()

# Find mainnet spec
mainnet_file = None
for f in ["chain-spec-mainnet-raw.json", "chain_spec_mainnet_raw.json"]:
    path = os.path.join("/opt/verdis-chain-rust", f)
    if os.path.exists(path):
        mainnet_file = path
        break

if not mainnet_file and os.path.isdir("/opt/verdis-chain-rust/chain-specs"):
    for f in os.listdir("/opt/verdis-chain-rust/chain-specs"):
        if "mainnet" in f.lower() and f.endswith(".json"):
            mainnet_file = os.path.join("/opt/verdis-chain-rust/chain-specs", f)
            break

if not mainnet_file:
    path = "/opt/verdis-chain-rust/chain-spec.json"
    if os.path.exists(path):
        mainnet_file = path

if mainnet_file:
    print(f"Spec: {mainnet_file}")
    with open(mainnet_file) as f:
        spec = json.load(f)
    sname = spec.get("name", "?")
    sid = spec.get("id", "?")
    stype = spec.get("chainType", "?")
    print(f"  name: {sname}")
    print(f"  id: {sid}")
    print(f"  chainType: {stype}")
    
    raw = spec.get("genesis", {}).get("raw", {}).get("top", {})
    
    sudo_prefix = "0x" + twox128("Sudo")
    has_sudo = any(k.startswith(sudo_prefix) for k in raw)
    print(f"  has_sudo: {has_sudo}")
    
    alice_key = "d43593c715fdd31c61141abd04a99fd6822c8558854ccde39a5684e7a56da27d"
    has_alice = any(alice_key in v for v in raw.values())
    print(f"  has_dev_identity_alice: {has_alice}")
    
    sv_key = "0x" + twox128("Session") + twox128("Validators")
    for k, v in raw.items():
        if k.lower().startswith(sv_key.lower()):
            n = bytes.fromhex(v[2:])[0] >> 2
            print(f"  session_validators: {n}")
            break
    
    babe_key = "0x" + twox128("Babe") + twox128("Authorities")
    for k, v in raw.items():
        if k.lower().startswith(babe_key.lower()):
            n = bytes.fromhex(v[2:])[0] >> 2
            print(f"  babe_authorities: {n}")
            break
    
    gpa_key = "0x" + twox128("Grandpa") + twox128("Authorities")
    for k, v in raw.items():
        if k.lower().startswith(gpa_key.lower()):
            n = bytes.fromhex(v[2:])[0] >> 2
            print(f"  grandpa_authorities: {n}")
            break
    
    # Sum all balance entries
    bal_prefix = "0x" + twox128("Balances")
    bal_total = 0
    bal_count = 0
    for k, v in raw.items():
        if k.startswith(bal_prefix):
            bal_count += 1
            raw_v = bytes.fromhex(v[2:])
            # AccountData: free(u128) + reserved(u128) + flags(u8)
            if len(raw_v) >= 32:
                free = int.from_bytes(raw_v[0:16], "little")
                reserved = int.from_bytes(raw_v[16:32], "little")
                bal_total += free + reserved
    
    print(f"  balance_entries: {bal_count}")
    print(f"  total_balances: {bal_total / 10**9:.0f} VRDX")
    
    # Check DPOS
    dpos_vl_key = "0x" + twox128("Dpos") + twox128("ValidatorList")
    for k, v in raw.items():
        if k.lower().startswith(dpos_vl_key.lower()):
            n = bytes.fromhex(v[2:])[0] >> 2
            print(f"  dpos_validator_list: {n}")
            break
    
    # Sum DPOS validator stakes
    dpos_val_prefix = "0x" + twox128("Dpos") + twox128("Validators")
    dpos_stake_total = 0
    for k, v in raw.items():
        if k.startswith(dpos_val_prefix) and len(v) > 100:
            raw_b = bytes.fromhex(v[2:])
            if len(raw_b) >= 48:
                stake = int.from_bytes(raw_b[32:48], "little")
                dpos_stake_total += stake
    print(f"  dpos_total_stake: {dpos_stake_total / 10**9:.0f} VRDX")
    
    target = 100_000_000_000 * 10**9
    print(f"  target_supply: {target / 10**9:.0f} VRDX")
    print(f"  actual_supply: {bal_total / 10**9:.0f} VRDX")
    diff = bal_total - target
    print(f"  difference: {diff / 10**9:.0f} VRDX")
    print(f"  match: {bal_total == target}")
    
    # Also check testnet spec
    print("\n--- Testnet Spec ---")
    testnet_file = "/opt/verdis-chain-rust/verdis-dev-raw-6val.json"
    if os.path.exists(testnet_file):
        with open(testnet_file) as f:
            ts = json.load(f)
        traw = ts.get("genesis", {}).get("raw", {}).get("top", {})
        tbal_total = 0
        for k, v in traw.items():
            if k.startswith(bal_prefix):
                raw_v = bytes.fromhex(v[2:])
                if len(raw_v) >= 32:
                    free = int.from_bytes(raw_v[0:16], "little")
                    reserved = int.from_bytes(raw_v[16:32], "little")
                    tbal_total += free + reserved
        print(f"  testnet_total_balances: {tbal_total / 10**9:.0f} VRDX")
        print(f"  testnet_match: {tbal_total == target}")
else:
    print("No spec found")
