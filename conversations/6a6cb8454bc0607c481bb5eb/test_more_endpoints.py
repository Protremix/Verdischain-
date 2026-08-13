import urllib.request
import urllib.error
import ssl
import json

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

test_list = [
    ("GET", "https://verdischain.com/api/governance"),
    ("POST", "https://verdischain.com/api/governance"),
    ("GET", "https://verdischain.com/api/v1/token/holders"),
    ("GET", "https://verdischain.com/api/v1/account/vrd1test"),
    ("GET", "https://verdischain.com/price-history.json"),
    ("GET", "https://verdischain.com/faucet/stats.json"),
    ("GET", "https://verdischain.com/faucet/api/stats"),
    ("POST", "https://verdischain.com/faucet/api"),
    ("POST", "https://verdischain.com/api/tx-relay"),
    ("GET", "http://localhost:9933"),
]

for method, url in test_list:
    print(f"Testing {method} {url}...")
    try:
        req = urllib.request.Request(url, headers=headers, method=method)
        if method == "POST":
            req.add_header("Content-Type", "application/json")
            data = json.dumps({"action": "test"}).encode('utf-8')
        else:
            data = None
            
        with urllib.request.urlopen(req, data=data, context=ctx, timeout=4) as resp:
            body = resp.read().decode('utf-8', errors='ignore')
            print(f"  -> SUCCESS {resp.status}: {body[:150]}")
    except urllib.error.HTTPError as e:
        print(f"  -> HTTP ERROR {e.code}: {e.read().decode('utf-8', errors='ignore')[:150]}")
    except Exception as e:
        print(f"  -> ERROR: {e}")
