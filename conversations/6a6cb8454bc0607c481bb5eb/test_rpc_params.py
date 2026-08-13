import urllib.request
import ssl
import json

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

rpc_url = "https://verdischain.com/rpc"
headers = {'Content-Type': 'application/json'}
val_addr = "5CiPPseXPECbkjWCa6MnjNokrgYjMqmKndv2rSnekmSK2DjL"

tests = [
    ("dpos_validatorName", [val_addr]),
    ("dpos_validatorStake", [val_addr]),
    ("eco_getGreenScore", [val_addr]),
]

for m, params in tests:
    req = urllib.request.Request(
        rpc_url,
        data=json.dumps({"jsonrpc": "2.0", "method": m, "params": params, "id": 1}).encode('utf-8'),
        headers=headers,
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if "error" in data:
                print(f"  ❌ {m} with param: ERROR -> {data['error']}")
            else:
                print(f"  ✅ {m} with param: SUCCESS -> {data['result']}")
    except Exception as e:
        print(f"  ❌ {m} with param: HTTP/NET ERROR -> {e}")
