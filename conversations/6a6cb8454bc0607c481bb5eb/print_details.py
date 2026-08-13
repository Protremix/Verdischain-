import os
import json
import re
from bs4 import BeautifulSoup

paths = [
    "/", "/explorer/", "/dex/", "/whitepaper/", "/wallet/", "/sale/", "/tokenomics/",
    "/faucet/", "/validators/", "/eco/", "/docs/", "/transactions/", "/analytics/",
    "/monitoring/", "/governance/", "/blog/", "/developers/", "/download/", "/referral/",
    "/incentives/", "/contact/", "/privacy/", "/terms/", "/cookies/", "/security/",
    "/disclaimer/", "/status/", "/api/"
]

def fname_for(p):
    f = p.strip("/").replace("/", "_")
    return f if f else "home"

for p in paths:
    fname = fname_for(p)
    fpath = f"audit_data/{fname}.html"
    with open(fpath, "r", encoding="utf-8") as f:
        html = f.read()
    soup = BeautifulSoup(html, "html.parser")
    scripts = soup.find_all("script")
    inline_js = "\n".join([s.string for s in scripts if s.string])
    
    # Extract all fetch calls with context
    fetches = re.findall(r'fetch\([^\)]+\)', inline_js)
    # Extract all ws with context
    wss = re.findall(r'WebSocket\([^\)]+\)|wss?://[^\s`\'"]+', inline_js)
    # Extract all xhr
    xhrs = re.findall(r'XMLHttpRequest|\$\.ajax|axios|\.open\(', inline_js)
    
    print(f"=== PATH: {p} ===")
    print(f"Title: {soup.title.string.strip() if soup.title else ''}")
    print(f"Script tags: {len(scripts)}")
    print(f"Fetch calls ({len(fetches)}): {fetches}")
    print(f"WS calls ({len(wss)}): {wss}")
    print(f"XHR calls ({len(xhrs)}): {xhrs}")
    print("-" * 50)
