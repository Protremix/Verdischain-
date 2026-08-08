import urllib.request
import urllib.parse
import ssl
import json

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

endpoints = [
    ("GET", "https://verdischain.com/api/v1/network/stats", None),
    ("GET", "https://verdischain.com/api/v1/block/last?limit=5", None),
    ("POST", "https://verdischain.com/rpc", json.dumps({"jsonrpc":"2.0","id":1,"method":"chain_getHeader","params":[]}).encode('utf-8'))
]

for method, url, body in endpoints:
    headers = {'User-Agent': 'Mozilla/5.0'}
    if method == "POST":
        headers['Content-Type'] = 'application/json'
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        res = urllib.request.urlopen(req, timeout=10, context=ctx)
        resp_body = res.read().decode('utf-8', errors='ignore')
        print(f"[{method}] {url} => Status: {res.status}\n  Response sample (first 200 chars): {resp_body[:200]}\n")
    except urllib.error.HTTPError as e:
        print(f"[{method}] {url} => HTTP ERROR: {e.code}\n  Response body: {e.read().decode('utf-8', errors='ignore')[:200]}\n")
    except Exception as e:
        print(f"[{method}] {url} => EXCEPTION: {e}\n")

