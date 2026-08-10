import json, glob, os

base = "/app/conversations/6a6cb8454bc0607c481bb5eb/verdis-audit/"
all_json = sorted(glob.glob(os.path.join(base, "**/*.json"), recursive=True))

specs = []
for path in all_json:
    rel = os.path.relpath(path, base)
    if any(x in rel for x in ["node_modules", "package", "audit", "grafana", "version-manifest", "keys/"]):
        continue
    try:
        with open(path) as f:
            data = json.load(f)
            if isinstance(data, dict) and ("id" in data or "genesis" in data or "name" in data):
                specs.append((rel, data))
    except Exception as e:
        print(f"Error loading {rel}: {e}")

print(f"Loaded {len(specs)} JSON specs\n")

for rel, data in specs:
    name = data.get("name", "N/A")
    cid = data.get("id", "N/A")
    ctype = data.get("chainType", "N/A")
    proto = data.get("protocolId", "N/A")
    boot_nodes = data.get("bootNodes", [])
    
    genesis = data.get("genesis", {})
    is_raw = "raw" in genesis
    
    print(f"=== {rel} ===")
    print(f"Name: {name} | ID: {cid} | Type: {ctype} | Proto: {proto} | Is Raw: {is_raw} | BootNodes: {len(boot_nodes)}")
    
    if not is_raw and "runtime" in genesis:
        rt = genesis["runtime"]
        print("Pallets in genesis.runtime:", list(rt.keys()))
        
        # Check sudo
        sudo = rt.get("sudo", {})
        print(" Sudo:", sudo)
        
        # Check session
        session = rt.get("session", {})
        keys = session.get("keys", [])
        print(f" Session keys count: {len(keys)}")
        if keys:
            print("  Sample key:", keys[0])
            
        # Check dpos
        dpos = rt.get("dpos", {})
        vals = dpos.get("validators", [])
        vc = dpos.get("validator_count")
        print(f" DPoS validators count: {len(vals)}, validator_count cfg: {vc}")
        
        # Check babe
        babe = rt.get("babe", {})
        babe_auths = babe.get("authorities", [])
        print(f" BABE authorities count: {len(babe_auths)}")
        
        # Check grandpa
        grandpa = rt.get("grandpa", {})
        grandpa_auths = grandpa.get("authorities", [])
        print(f" GRANDPA authorities count: {len(grandpa_auths)}")
        
        # Check balances
        balances_cfg = rt.get("balances", {})
        b_list = balances_cfg.get("balances", [])
        tot = 0
        for item in b_list:
            if isinstance(item, list) and len(item) == 2:
                v = item[1]
                if isinstance(v, str):
                    if v.startswith("0x"):
                        v = int(v, 16)
                    else:
                        v = int(v)
                tot += v
        print(f" Balances count: {len(b_list)}, Total balance: {tot} (in units: {tot/1e9:,.0f} VRDX)")
    elif is_raw:
        raw_top = genesis.get("raw", {}).get("top", {})
        print(f" Raw top keys count: {len(raw_top)}")
    print()

