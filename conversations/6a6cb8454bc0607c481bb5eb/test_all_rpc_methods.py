import httpx
import json
import re

with open("page2_script.js", "r") as f:
    js_code = f.read()

# Parse all endpoint names
matches = re.findall(r"\{g:'([^']+)',n:'([^']+)',m:'([^']+)'", js_code)

client = httpx.Client(
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Content-Type': 'application/json'},
    follow_redirects=True,
    timeout=10.0
)

url = "https://verdischain.com/rpc"

results = []

for g, n, m in matches:
    if m == "WS":
        print(f"Skipping WS method: {n} ({g})")
        continue
    
    payload = {"jsonrpc": "2.0", "id": 1, "method": n, "params": []}
    try:
        r = client.post(url, json=payload)
        res_json = r.json()
        if "error" in res_json:
            err = res_json["error"]
            print(f"[FAIL/ERROR] {g} -> {n}: Code {err.get('code')} - {err.get('message')}")
            results.append({'group': g, 'name': n, 'status': 'ERROR', 'error': err})
        else:
            print(f"[OK] {g} -> {n}")
            results.append({'group': g, 'name': n, 'status': 'OK'})
    except Exception as e:
        print(f"[EXCEPTION] {g} -> {n}: {e}")
        results.append({'group': g, 'name': n, 'status': 'EXCEPTION', 'error': str(e)})

with open("rpc_test_results.json", "w") as f:
    json.dump(results, f, indent=2)

