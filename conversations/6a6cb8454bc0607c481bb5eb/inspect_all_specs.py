import json, glob, os

base = "/app/conversations/6a6cb8454bc0607c481bb5eb/verdis-audit/"

all_json = sorted(glob.glob(os.path.join(base, "**/*.json"), recursive=True))

specs_summary = []
for path in all_json:
    rel = os.path.relpath(path, base)
    if any(x in rel for x in ["node_modules", "package", "audit", "grafana", "version-manifest", "keys/"]):
        continue
    size = os.path.getsize(path)
    if size == 0:
        specs_summary.append({
            "path": rel, "status": "EMPTY FILE", "size": 0
        })
        continue
    try:
        with open(path) as f:
            data = json.load(f)
            if isinstance(data, dict) and ("id" in data or "genesis" in data or "name" in data):
                name = data.get("name", "N/A")
                cid = data.get("id", "N/A")
                ctype = data.get("chainType", "N/A")
                proto = data.get("protocolId", "N/A")
                boot = data.get("bootNodes", [])
                genesis = data.get("genesis", {})
                is_raw = "raw" in genesis
                specs_summary.append({
                    "path": rel,
                    "status": "VALID",
                    "size": size,
                    "name": name,
                    "id": cid,
                    "type": ctype,
                    "proto": proto,
                    "is_raw": is_raw,
                    "boot_nodes": boot
                })
    except Exception as e:
        specs_summary.append({
            "path": rel, "status": f"INVALID JSON: {e}", "size": size
        })

print(f"{'Path':<45} | {'Type':<12} | {'Name':<18} | {'ID':<15} | {'IsRaw':<5} | {'Boot'}")
print("-" * 110)
for s in specs_summary:
    if s["status"] == "VALID":
        print(f"{s['path']:<45} | {s['type']:<12} | {s['name']:<18} | {s['id']:<15} | {str(s['is_raw']):<5} | {len(s['boot_nodes'])}")
    else:
        print(f"{s['path']:<45} | {s['status']}")

