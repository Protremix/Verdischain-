import httpx
import json

client = httpx.Client(
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Content-Type': 'application/json'},
    follow_redirects=True,
    timeout=10.0
)

# Test a few methods
methods = [
    "chain_getBlock",
    "chain_getBlockHash",
    "system_health",
    "system_chain",
    "amm_dex_getAllPools",
    "non_existent_method"
]

url = "https://verdischain.com/rpc"

for m in methods:
    payload = {"jsonrpc": "2.0", "id": 1, "method": m, "params": []}
    try:
        r = client.post(url, json=payload)
        print(f"Method: {m} | Status: {r.status_code}")
        print("Response:", r.text[:300])
        print("-" * 50)
    except Exception as e:
        print(f"Method: {m} | Error: {e}")

