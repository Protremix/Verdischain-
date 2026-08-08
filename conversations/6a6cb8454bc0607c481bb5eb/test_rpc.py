import requests
import json

RPC_URL = "https://verdischain.com/rpc/"

methods = [
    ("chain_getHeader", []),
    ("system_properties", []),
    ("state_getStorage", ["0xaaf995822f98c19783008fced38cfdbde6a0f1f3d55c5dd789d90bb7accd9ee4"]),
    ("amm_dex_getAllPools", [])
]

for method, params in methods:
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params
    }
    try:
        res = requests.post(RPC_URL, json=payload, headers={"Content-Type": "application/json"}, timeout=5)
        print(f"=== {method} ===")
        print("Status code:", res.status_code)
        print("Response:", res.text[:500])
    except Exception as e:
        print(f"=== {method} ERROR ===")
        print(e)
