import os
import re
import json
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

results = {}

for p in paths:
    fname = fname_for(p)
    fpath = f"audit_data/{fname}.html"
    
    if not os.path.exists(fpath):
        continue
        
    with open(fpath, "r", encoding="utf-8") as f:
        html = f.read()
        
    soup = BeautifulSoup(html, "html.parser")
    
    # Scripts
    scripts = soup.find_all("script")
    ext_scripts = [s.get("src") for s in scripts if s.get("src")]
    inline_js = "\n".join([s.string for s in scripts if s.string])
    
    # 1. Extract fetch calls
    fetch_calls = []
    # Match fetch(...) call patterns
    fetch_matches = re.finditer(r'fetch\s*\(\s*([^,\)]+)', inline_js)
    for m in fetch_matches:
        fetch_calls.append(m.group(1).strip())
        
    # 2. Extract XHR
    xhr_calls = []
    xhr_matches = re.finditer(r'XMLHttpRequest|\$\.ajax|axios|\.open\s*\(\s*[`\'"](GET|POST|PUT|DELETE)[`\'"]\s*,\s*[`\'"]([^`\'"]+)[`\'"]', inline_js)
    for m in xhr_matches:
        xhr_calls.append(m.group(0).strip())
        
    # 3. Extract WebSockets
    ws_calls = []
    ws_matches = re.finditer(r'new\s+WebSocket\s*\(\s*([^,\)]+)\)|wss?://[^\s`\'"]+', inline_js)
    for m in ws_matches:
        ws_calls.append(m.group(0).strip())
        
    # 4. Extract API variables
    api_vars = re.findall(r'(const|let|var)\s+([A-Za-z0-9_]*(?:API|RPC|WS|URL|ENDPOINT)[A-Za-z0-9_]*)\s*=\s*[`\'"]([^`\'"]+)[`\'"]', inline_js, re.I)
    
    # 5. Extract endpoints mentioned in strings
    str_endpoints = list(set(re.findall(r'[`\'"](/api/[^`\'"]*|/rpc[^`\'"]*|https?://[^\s`\'"]+|wss?://[^\s`\'"]+)[\'"]', inline_js)))

    # 6. Check for hardcoded data / static placeholders
    hardcoded = []
    if "const blocksData =" in inline_js or "const transactionsData =" in inline_js:
        hardcoded.append("Hardcoded mock block/transaction arrays in script tag")
    if "dummyHash" in html or "sample" in inline_js.lower():
        hardcoded.append("Dummy hashes or sample account addresses present")
    if "data: [" in inline_js and "chart" in html.lower():
        hardcoded.append("Hardcoded numerical data arrays for Chart.js rendering")
    if "const mock" in inline_js.lower() or "const dummy" in inline_js.lower():
        hardcoded.append("Explicit mock data variables declared in JS")
    if "<table" in html and not fetch_calls and p not in ["/whitepaper/", "/tokenomics/", "/privacy/", "/terms/", "/cookies/", "/security/", "/disclaimer/", "/docs/", "/api/"]:
        hardcoded.append("Static HTML data table with no JS fetch to populate dynamic dynamic data")

    # 7. Identify specific broken/missing endpoint issues
    issues = []
    
    # Check if page references localhost
    if "localhost:9933" in inline_js or "localhost" in html:
        issues.append("References 'http://localhost:9933' which fails in production with Connection Refused / Mixed Content CORS error.")
        
    # Check if WebSocket endpoint fails
    if "wss://verdischain.com/substrate-ws" in inline_js or "wss://verdischain.com/ws" in inline_js:
        issues.append("Uses WebSocket URL 'wss://verdischain.com/substrate-ws' or 'wss://verdischain.com/ws' which returns HTTP 200 instead of 101 Upgrade, failing browser WS connection.")
        
    # Check POST /api/governance
    if "POST" in inline_js and "/api/governance" in inline_js:
        issues.append("Calls POST '/api/governance' which returns 501 Not Implemented.")

    results[p] = {
        'title': soup.title.string.strip() if soup.title else '',
        'ext_scripts': ext_scripts,
        'fetch_calls': list(set(fetch_calls)),
        'xhr_calls': list(set(xhr_calls)),
        'ws_calls': list(set(ws_calls)),
        'api_vars': api_vars,
        'str_endpoints': str_endpoints,
        'hardcoded': hardcoded,
        'issues': issues,
        'html_len': len(html),
        'js_len': len(inline_js)
    }

print("Page audit complete.")
