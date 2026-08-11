import json

with open("/tmp/dev-spec.json") as f:
    spec = json.load(f)

print("Chain name: " + spec.get("name", "unknown"))
print("ID: " + spec.get("id", "unknown"))
genesis = spec.get("genesis", {})
runtime = genesis.get("runtime", {})
print("Runtime pallets: " + str(list(runtime.keys())))
session = runtime.get("session", {})
if session:
    keys = session.get("keys", [])
    print("Session keys: " + str(len(keys)))
staking = runtime.get("staking", {})
if staking:
    stakers = staking.get("stakers", [])
    print("Stakers: " + str(len(stakers)))
dpos = runtime.get("dpos", {})
if dpos:
    print("DPoS keys: " + str(list(dpos.keys())))
balances = runtime.get("balances", {})
if balances:
    bal_list = balances.get("balances", [])
    print("Balances: " + str(len(bal_list)) + " entries")
