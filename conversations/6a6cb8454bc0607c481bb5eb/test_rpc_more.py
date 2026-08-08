import urllib.request
import json

def call_rpc(method):
    url = "https://verdischain.com/rpc"
    payload = {"jsonrpc": "2.0", "method": method, "params": [], "id": 1}
    req = urllib.request.Request(
        url, 
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
    )
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print(f"[{method}] ->", json.dumps(data, indent=2))
    except Exception as e:
        print(f"[{method}] ERROR ->", e)

call_rpc('system_health')
call_rpc('dpos_allValidators')
