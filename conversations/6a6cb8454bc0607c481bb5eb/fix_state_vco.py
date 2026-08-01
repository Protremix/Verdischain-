import json

path = "/opt/verdis/blobs/verdis-state.json"
with open(path) as f:
    state = json.load(f)

changes = 0

# Fix pools
if "pools" in state:
    for pool in state["pools"]:
        if pool.get("tokenA") == "VCO":
            pool["tokenA"] = "VRS"
            changes += 1
        if pool.get("tokenB") == "VCO":
            pool["tokenB"] = "VRS"
            changes += 1
        if "VCO" in pool.get("id", ""):
            pool["id"] = pool["id"].replace("VCO", "VRS")
            changes += 1

# Fix any VCO in mempool transactions
if "mempool" in state and isinstance(state["mempool"], list):
    for tx in state["mempool"]:
        if isinstance(tx, dict):
            if tx.get("tokenIn") == "VCO":
                tx["tokenIn"] = "VRS"
                changes += 1
            if tx.get("tokenOut") == "VCO":
                tx["tokenOut"] = "VRS"
                changes += 1
            if tx.get("token") == "VCO":
                tx["token"] = "VRS"
                changes += 1

# Do a blanket string replace on the raw JSON for any remaining VCO
raw = json.dumps(state)
raw_vco = raw.count("VCO")
raw = raw.replace('"VCO"', '"VRS"')
raw = raw.replace("_VCO_", "_VRS_")
raw = raw.replace("_VCO\"", "_VRS\"")
raw = raw.replace("VCO/", "VRS/")
raw = raw.replace("/VCO", "/VRS")

state = json.loads(raw)

with open(path, "w") as f:
    json.dump(state, f, indent=2)

# Verify
with open(path) as f:
    verify = f.read()
print(f"Pool token changes: {changes}")
print(f"Raw VCO remaining: {verify.count('VCO')}")
print(f"VRS occurrences: {verify.count('VRS')}")

# Show updated pools
if "pools" in state:
    for p in state["pools"][:5]:
        print(f"  Pool: {p.get('tokenA','')}/{p.get('tokenB','')} (id: {p.get('id','')})")
