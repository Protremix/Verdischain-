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

report_data = []

for p in paths:
    fname = fname_for(p)
    fpath = f"audit_data/{fname}.html"
    if not os.path.exists(fpath):
        print(f"File not found: {fpath}")
        continue
        
    with open(fpath, "r", encoding="utf-8") as f:
        html = f.read()
        
    soup = BeautifulSoup(html, "html.parser")
    
    # Extract scripts
    script_tags = soup.find_all("script")
    external_scripts = [s.get("src") for s in script_tags if s.get("src")]
    inline_scripts = [s.string for s in script_tags if s.string]
    all_inline = "\n".join(inline_scripts)
    
    # 1. Extract fetch calls
    # Match fetch(...) patterns
    fetches = []
    # match fetch('url', ...) or fetch("url", ...) or fetch(`url`, ...)
    f_matches = re.finditer(r'fetch\s*\(\s*([`\'"]([^`\'"]+)[`\'"]|([a-zA-Z0-9_\.\$\{\}\/`\'"-]+))', all_inline)
    for m in f_matches:
        raw = m.group(0)
        arg = m.group(1)
        fetches.append(arg)
        
    # Also check external scripts if applicable or global script verdis.js
    
    # 2. Extract XHR calls
    xhrs = []
    x_matches = re.finditer(r'new\s+XMLHttpRequest|\.open\s*\(\s*[`\'"](GET|POST|PUT|DELETE)[`\'"]\s*,\s*[`\'"]([^`\'"]+)[`\'"]|\$\.ajax', all_inline)
    for m in x_matches:
        xhrs.append(m.group(0))
        
    # 3. Extract WebSocket calls
    wss = []
    w_matches = re.finditer(r'new\s+WebSocket\s*\(\s*[`\'"]([^`\'"]+)[`\'"]|new\s+WebSocket\s*\(\s*([a-zA-Z0-9_\.\$\{\}]+)\)|(wss?://[^\s`\'"]+)', all_inline)
    for m in w_matches:
        wss.append(m.group(0))
        
    # 4. Extract API variables / constants in JS
    api_vars = re.findall(r'(const|let|var)\s+([A-Za-z0-9_]*API[A-Za-z0-9_]*|RPC[A-Za-z0-9_]*|WS[A-Za-z0-9_]*|RELAY[A-Za-z0-9_]*|URL[A-Za-z0-9_]*)\s*=\s*[`\'"]([^`\'"]+)[`\'"]', all_inline)

    # 5. Find all URL string patterns in inline script
    urls_in_script = set(re.findall(r'[`\'"](/api/[^`\'"]*|/rpc[^`\'"]*|https?://[^\s`\'"]+|wss?://[^\s`\'"]+)[\'"]', all_inline))

    # 6. Hardcoded data check
    # Check for hardcoded arrays of transactions, blocks, balances, validators, charts, stats
    hardcoded_notes = []
    if "const blocksData =" in all_inline or "const transactionsData =" in all_inline:
        hardcoded_notes.append("Hardcoded blocks/transactions mock data array in JS")
    if "dummyHash" in html or "sample" in all_inline.lower() and "sample" in html:
        hardcoded_notes.append("Dummy/sample addresses or mock hashes hardcoded")
    if "data-counter" in html and not fetches and "loadLiveStats" not in html and "fetchRpc" not in html:
        hardcoded_notes.append("Static HTML counter attributes rendered without live API data fetch")
    if "chart" in html.lower() and ("const chartData" in html or "data: [" in html):
        hardcoded_notes.append("Chart rendering uses static hardcoded data points")

    report_data.append({
        'path': p,
        'title': soup.title.string.strip() if soup.title else '',
        'external_scripts': external_scripts,
        'fetches': list(set(fetches)),
        'xhrs': xhrs,
        'wss': list(set(wss)),
        'api_vars': api_vars,
        'urls_in_script': list(urls_in_script),
        'hardcoded_notes': hardcoded_notes,
        'has_verdis_js': any('verdis.js' in s for s in external_scripts)
    })

with open("audit_summary.json", "w", encoding="utf-8") as f:
    json.dump(report_data, f, indent=2)

print("Saved audit_summary.json")
