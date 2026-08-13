import urllib.request
import urllib.parse
import ssl
import re
import json
import os
from bs4 import BeautifulSoup

paths = [
    "/", "/explorer/", "/dex/", "/whitepaper/", "/wallet/", "/sale/", "/tokenomics/",
    "/faucet/", "/validators/", "/eco/", "/docs/", "/transactions/", "/analytics/",
    "/monitoring/", "/governance/", "/blog/", "/developers/", "/download/", "/referral/",
    "/incentives/", "/contact/", "/privacy/", "/terms/", "/cookies/", "/security/",
    "/disclaimer/", "/status/", "/api/"
]

base_url = "https://verdischain.com"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

os.makedirs("audit_data", exist_ok=True)

results = {}

for path in paths:
    url = f"{base_url}{path}"
    print(f"Fetching {url}...")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            status = resp.status
    except Exception as e:
        html = ""
        status = str(e)
    
    # Save raw html
    filename = path.strip("/").replace("/", "_")
    if not filename:
        filename = "home"
    with open(f"audit_data/{filename}.html", "w", encoding="utf-8") as f:
        f.write(html)
        
    results[path] = {
        'status': status,
        'html_len': len(html),
        'filename': filename
    }

print("Done fetching HTML files.")
