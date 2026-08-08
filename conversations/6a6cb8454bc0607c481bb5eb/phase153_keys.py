import json, subprocess, time, requests
from substrateinterface import SubstrateInterface, Keypair

substrate = SubstrateInterface(url="http://127.0.0.1:9933", ss58_format=909, auto_discover=True, type_registry_preset=None)
RELAY_URL = "http://127.0.0.1:5001"

# Standard keyring validators that need session keys
KEYRING_VALIDATORS = ["//Bob", "//Charlie", "//Dave", "//Eve", "//Ferdie"]

# New validators to register
NEW_VALIDATORS = ["//Validator15","//Validator16","//Validator17","//Validator18","//Validator19","//Validator20","//Validator21"]

def rpc_call(method, params):
    """Call an RPC method on the node"""
    r = subprocess.run(["curl", "-sf", "-X", "POST", "http://127.0.0.1:9933", 
        "-H", "Content-Type: application/json",
        "-d", json.dumps({"jsonrpc":"2.0","method":method,"params":params,"id":1})],
        capture_output=True, text=True, timeout=15)
    return json.loads(r.stdout) if r.stdout else {}

def insert_key(key_type, suri, public_key_hex):
    """Insert a key into the node's keystore"""
    result = rpc_call("author_insertKey", [key_type, suri, "0x" + public_key_hex])
    return result.get("result", False)

# Step 1: Fund new validators via tx-relay (Charlie has 250M VRDX)
print("=== Step 1: Fund new validators ===", flush=True)
for uri in NEW_VALIDATORS:
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
            print("  Funded {} ({})".format(uri, addr[:20]), flush=True)
        else:
            print("  ERR {}: {}".format(uri, result.get("error","?")), flush=True)
    except Exception as e:
        print("  ERR {}: {}".format(uri, str(e)[:60]), flush=True)
    time.sleep(6)

print("Waiting 15s for funding inclusion...", flush=True)
time.sleep(15)

# Step 2: Register new validators
print("=== Step 2: Register new validators ===", flush=True)
for uri in NEW_VALIDATORS:
    kp = Keypair.create_from_uri(uri, ss58_format=909)
    addr = kp.ss58_address
    v_nonce = substrate.get_account_nonce(addr)
    try:
        call = substrate.compose_call("Dpos", "register_validator", {"green_score": 3, "energy_source": "solar"})
        ext = substrate.create_signed_extrinsic(call, kp, nonce=v_nonce)
        substrate.submit_extrinsic(ext, wait_for_inclusion=False)
        time.sleep(6)
        print("  Registered {} ({})".format(uri, addr[:20]), flush=True)
    except Exception as e:
        print("  ERR {}: {}".format(uri, str(e)[:60]), flush=True)

print("Waiting 15s for registration inclusion...", flush=True)
time.sleep(15)

# Step 3: Insert session keys into keystore AND set on-chain
print("=== Step 3: Set session keys ===", flush=True)

# First, insert keys for keyring validators (Bob-Ferdie)
for uri in KEYRING_VALIDATORS:
    name = uri.replace("//", "")
    # Babe key (sr25519)
    babe_kp = Keypair.create_from_uri(uri, ss58_format=909, crypto_type=1)
    babe_pub = babe_kp.public_key.hex()
    # Grandpa key (ed25519)
    grandpa_kp = Keypair.create_from_uri(uri, ss58_format=909, crypto_type=0)
    grandpa_pub = grandpa_kp.public_key.hex()
    
    # Insert into keystore
    r1 = insert_key("babe", uri, babe_pub)
    r2 = insert_key("gran", uri, grandpa_pub)
    print("  Keystore {}: babe={}, gran={}".format(name, r1, r2), flush=True)
    
    # Set on-chain via session.set_keys
    try:
        v_nonce = substrate.get_account_nonce(babe_kp.ss58_address)
        # SessionKeys struct: { babe: AccountId, grandpa: AccountId }
        keys = {
            "babe": babe_pub,
            "grandpa": grandpa_pub
        }
        call = substrate.compose_call("Session", "set_keys", {"keys": keys, "proof": b""})
        ext = substrate.create_signed_extrinsic(call, babe_kp, nonce=v_nonce)
        substrate.submit_extrinsic(ext, wait_for_inclusion=False)
        time.sleep(6)
        print("  On-chain {}: set_keys submitted".format(name), flush=True)
    except Exception as e:
        print("  ERR {}: {}".format(name, str(e)[:60]), flush=True)

# Then for new validators (V15-V21)
for uri in NEW_VALIDATORS:
    name = uri.replace("//", "")
    babe_kp = Keypair.create_from_uri(uri, ss58_format=909, crypto_type=1)
    babe_pub = babe_kp.public_key.hex()
    grandpa_kp = Keypair.create_from_uri(uri, ss58_format=909, crypto_type=0)
    grandpa_pub = grandpa_kp.public_key.hex()
    
    # Insert into keystore
    r1 = insert_key("babe", uri, babe_pub)
    r2 = insert_key("gran", uri, grandpa_pub)
    print("  Keystore {}: babe={}, gran={}".format(name, r1, r2), flush=True)
    
    # Set on-chain
    try:
        v_nonce = substrate.get_account_nonce(babe_kp.ss58_address)
        keys = {"babe": babe_pub, "grandpa": grandpa_pub}
        call = substrate.compose_call("Session", "set_keys", {"keys": keys, "proof": b""})
        ext = substrate.create_signed_extrinsic(call, babe_kp, nonce=v_nonce)
        substrate.submit_extrinsic(ext, wait_for_inclusion=False)
        time.sleep(6)
        print("  On-chain {}: set_keys submitted".format(name), flush=True)
    except Exception as e:
        print("  ERR {}: {}".format(name, str(e)[:60]), flush=True)

# Step 4: Check status
print("\n=== Step 4: Status ===", flush=True)
r = rpc_call("dpos_allValidators", [])
all_v = r.get("result", [])
print("Total validators: {}".format(len(all_v)), flush=True)

r = rpc_call("dpos_activeValidators", [])
active = r.get("result", [])
print("Active validators: {}".format(len(active)), flush=True)

r = rpc_call("chain_getHeader", [])
block = int(r.get("result", {}).get("number", "0x0"), 16)
print("Block: #{}".format(block), flush=True)

# Check pending
r = rpc_call("author_pendingExtrinsics", [])
pending = r.get("result", [])
print("Pending extrinsics: {}".format(len(pending)), flush=True)
