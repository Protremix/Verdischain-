import json, subprocess, time, requests
from substrateinterface import SubstrateInterface, Keypair

substrate = SubstrateInterface(url="http://127.0.0.1:9933", ss58_format=909, auto_discover=True, type_registry_preset=None)
RELAY_URL = "http://127.0.0.1:5001"

uris = ["//Validator15","//Validator16","//Validator17","//Validator18","//Validator19","//Validator20","//Validator21"]

# Phase 1: Fund all validators via tx-relay (Charlie has 250M VRDX)
print("=== Phase 1: Funding validators ===", flush=True)
for uri in uris:
    kp = Keypair.create_from_uri(uri, ss58_format=909)
    addr = kp.ss58_address
    try:
        r = requests.post(RELAY_URL + "/transfer", json={
            "action": "transfer",
            "dest": addr,
            "amount": 15_000_000_000_000
        }, timeout=15)
        result = r.json()
        if result.get("ok"):
            ext_hash = result.get("extrinsic_hash", "?")
            print("Funded {} ({}) -> {}".format(uri, addr[:20], ext_hash[:16]), flush=True)
        else:
            print("ERR {}: {}".format(uri, result), flush=True)
    except Exception as e:
        print("ERR {}: {}".format(uri, str(e)[:60]), flush=True)
    time.sleep(6)

# Wait for all funding to be included
print("Waiting 20s for all funding to be included...", flush=True)
time.sleep(20)

# Phase 2: Verify balances
print("=== Phase 2: Verify balances ===", flush=True)
for uri in uris:
    kp = Keypair.create_from_uri(uri, ss58_format=909)
    addr = kp.ss58_address
    acct = substrate.query("System", "Account", [addr])
    free = acct.value.get("data", {}).get("free", 0) if acct else 0
    print("  {}: free={} ({:.0f} VRDX)".format(uri, free, free/1_000_000_000), flush=True)

# Phase 3: Register validators
print("=== Phase 3: Register validators ===", flush=True)
for uri in uris:
    kp = Keypair.create_from_uri(uri, ss58_format=909)
    addr = kp.ss58_address
    v_nonce = substrate.get_account_nonce(addr)
    try:
        call = substrate.compose_call("Dpos", "register_validator", {"green_score": 3, "energy_source": "solar"})
        ext = substrate.create_signed_extrinsic(call, kp, nonce=v_nonce)
        substrate.submit_extrinsic(ext, wait_for_inclusion=False)
        time.sleep(6)
        print("Registered {} ({})".format(uri, addr[:20]), flush=True)
    except Exception as e:
        print("ERR {}: {}".format(uri, str(e)[:80]), flush=True)

time.sleep(15)

# Final count
r = subprocess.run(["curl", "-sf", "-X", "POST", "http://127.0.0.1:9933", "-H", "Content-Type: application/json",
    "-d", json.dumps({"jsonrpc": "2.0", "method": "dpos_allValidators", "params": [], "id": 1})],
    capture_output=True, text=True, timeout=10)
all_v = json.loads(r.stdout).get("result", [])
print("\nTotal validators: {}".format(len(all_v)), flush=True)

r = subprocess.run(["curl", "-sf", "-X", "POST", "http://127.0.0.1:9933", "-H", "Content-Type: application/json",
    "-d", json.dumps({"jsonrpc": "2.0", "method": "dpos_activeValidators", "params": [], "id": 1})],
    capture_output=True, text=True, timeout=10)
active = json.loads(r.stdout).get("result", [])
print("Active validators: {}".format(len(active)), flush=True)
