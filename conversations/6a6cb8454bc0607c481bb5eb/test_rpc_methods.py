import urllib.request
import ssl
import json

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

rpc_url = "https://verdischain.com/rpc"
headers = {'Content-Type': 'application/json'}

methods_to_test = [
    "chain_getHeader",
    "chain_getBlock",
    "system_health",
    "dpos_activeValidators",
    "dpos_validatorName",
    "dpos_validatorStake",
    "eco_getGreenScore",
    "amm_dex_getAllPools",
    "amm_dex_getPoolCount",
    "system_name",
    "system_version"
]

print("=== TESTING RPC METHODS AT https://verdischain.com/rpc ===")
for m in methods_to_test:
    req = urllib.request.Request(
        rpc_url,
        data=json.dumps({"jsonrpc": "2.0", "method": m, "params": [], "id": 1}).encode('utf-8'),
        headers=headers,
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if "error" in data:
                print(f"  ❌ {m}: ERROR -> {data['error']}")
            else:
                print(f"  ✅ {m}: SUCCESS -> {str(data['result'])[:100]}")
    except Exception as e:
        print(f"  ❌ {m}: HTTP/NET ERROR -> {e}")

