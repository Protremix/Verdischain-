import urllib.request
import json

url = "https://verdischain.com/rpc"
payload = {
    "jsonrpc": "2.0",
    "method": "chain_getHeader",
    "params": [],
    "id": 1
}

req = urllib.request.Request(
    url, 
    data=json.dumps(payload).encode('utf-8'),
    headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
)

try:
    with urllib.request.urlopen(req) as resp:
        print("RPC Response Status:", resp.status)
        data = json.loads(resp.read().decode('utf-8'))
        print("RPC Response Data:", json.dumps(data, indent=2))
except Exception as e:
    print("RPC Error:", e)

