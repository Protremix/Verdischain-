import json, glob, os

base = "/app/conversations/6a6cb8454bc0607c481bb5eb/verdis-audit/"

pairs = [
    ("chain-specs/dev-plain.json", "chain-specs/dev-raw.json"),
    ("chain-specs/testnet-plain.json", "chain-specs/testnet-raw.json"),
    ("chain-specs/mainnet-plain.json", "chain-specs/mainnet-raw.json"),
    ("chain-specs/mainnet/verdis-mainnet-plain.json", "chain-specs/mainnet/verdis-mainnet-raw.json"),
    ("chain-specs/testnet/verdis-testnet-plain.json", "chain-specs/testnet/verdis-testnet-raw.json"),
    ("chain_spec_testnet.json", "chain_spec_testnet_raw.json"),
    ("multi-node/chain-spec.json", "multi-node/chain-spec-raw.json"),
]

for p_path, r_path in pairs:
    p_full = os.path.join(base, p_path)
    r_full = os.path.join(base, r_path)
    
    print(f"=== Comparing {p_path} vs {r_path} ===")
    if not os.path.exists(p_full) or not os.path.exists(r_full):
        print("  One or both files missing!")
        continue
        
    with open(p_full) as f:
        p_data = json.load(f)
    with open(r_full) as f:
        r_data = json.load(f)
        
    p_id = p_data.get("id")
    r_id = r_data.get("id")
    p_name = p_data.get("name")
    r_name = r_data.get("name")
    p_type = p_data.get("chainType")
    r_type = r_data.get("chainType")
    p_proto = p_data.get("protocolId")
    r_proto = r_data.get("protocolId")
    p_boot = p_data.get("bootNodes", [])
    r_boot = r_data.get("bootNodes", [])
    
    print(f"  Plain: name='{p_name}', id='{p_id}', type='{p_type}', proto='{p_proto}', bootNodes={len(p_boot)}")
    print(f"  Raw:   name='{r_name}', id='{r_id}', type='{r_type}', proto='{r_proto}', bootNodes={len(r_boot)}")
    
    mismatches = []
    if p_id != r_id: mismatches.append(f"id ({p_id} vs {r_id})")
    if p_name != r_name: mismatches.append(f"name ('{p_name}' vs '{r_name}')")
    if p_type != r_type: mismatches.append(f"chainType ({p_type} vs {r_type})")
    if p_proto != r_proto: mismatches.append(f"protocolId ({p_proto} vs {r_proto})")
    if p_boot != r_boot: mismatches.append(f"bootNodes ({p_boot} vs {r_boot})")
    
    if mismatches:
        print("  MISMATCHES DETECTED:", ", ".join(mismatches))
    else:
        print("  Metadata matches.")
    print()

