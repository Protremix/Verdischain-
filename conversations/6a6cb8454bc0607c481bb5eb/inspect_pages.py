import os
import re
import json
import urllib.request
import ssl
from bs4 import BeautifulSoup

paths_and_files = [
    ("/", "home.html"),
    ("/explorer/", "explorer.html"),
    ("/dex/", "dex.html"),
    ("/whitepaper/", "whitepaper.html"),
    ("/wallet/", "wallet.html"),
    ("/sale/", "sale.html"),
    ("/tokenomics/", "tokenomics.html"),
    ("/faucet/", "faucet.html"),
    ("/validators/", "validators.html"),
    ("/eco/", "eco.html"),
    ("/docs/", "docs.html"),
    ("/transactions/", "transactions.html"),
    ("/analytics/", "analytics.html"),
    ("/monitoring/", "monitoring.html"),
    ("/governance/", "governance.html"),
    ("/blog/", "blog.html"),
    ("/developers/", "developers.html"),
    ("/download/", "download.html"),
    ("/referral/", "referral.html"),
    ("/incentives/", "incentives.html"),
    ("/contact/", "contact.html"),
    ("/privacy/", "privacy.html"),
    ("/terms/", "terms.html"),
    ("/cookies/", "cookies.html"),
    ("/security/", "security.html"),
    ("/disclaimer/", "disclaimer.html"),
    ("/status/", "status.html"),
    ("/api/", "api.html")
]

all_endpoints = set()
page_details = {}

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

for path, fname in paths_and_files:
    fpath = os.path.join("audit_data", fname)
    if not os.path.exists(fpath):
        print(f"File missing: {fpath}")
        continue
    
    with open(fpath, "r", encoding="utf-8") as f:
        html = f.read()
    
    soup = BeautifulSoup(html, "html.parser")
    
    # Extract scripts
    inline_scripts = [s.string for s in soup.find_all("script") if s.string]
    all_js = "\n".join(inline_scripts)
    
    # Regex search in inline JS
    fetches = []
    # match fetch('...') or fetch("...") or fetch(`...`) or fetch(var)
    fetch_matches = re.findall(r'fetch\s*\(\s*([`\'"][^`\'"]+[`\'"]|[a-zA-Z0-9_\.]+)', all_js)
    for m in fetch_matches:
        fetches.append(m)
        
    xhrs = re.findall(r'XMLHttpRequest|\$\.ajax|axios|\.open\s*\(\s*[`\'"](GET|POST)[`\'"]\s*,\s*[`\'"]([^`\'"]+)[`\'"]', all_js)
    
    wss = re.findall(r'new\s+WebSocket\s*\(\s*[`\'"]([^`\'"]+)[`\'"]|ws[s]?://[^\s`\'"]+', all_js)
    
    # Also search for endpoint strings in HTML & JS
    endpoints_found = re.findall(r'[`\'"](/api/[^`\'"]*|https?://[^\s`\'"]+|wss?://[^\s`\'"]+)[\'"]', html)
    
    # Check for hardcoded tables/data/mock objects in JS
    mock_patterns = re.findall(r'(mock[A-Za-z0-9_]*|dummy[A-Za-z0-9_]*|sample[A-Za-z0-9_]*|hardcoded|fake[A-Za-z0-9_]*|const\s+[A-Za-z0-9_]*data\s*=\s*\[)', all_js, re.IGNORECASE)

    page_details[path] = {
        'html_size': len(html),
        'title': soup.title.string if soup.title else "No Title",
        'fetches': fetches,
        'xhrs': xhrs,
        'wss': wss,
        'endpoints': list(set(endpoints_found)),
        'mock_patterns': mock_patterns,
        'inline_script_count': len(soup.find_all("script")),
        'inline_script_length': len(all_js)
    }
    
    for ep in endpoints_found:
        all_endpoints.add(ep)

print(json.dumps(page_details, indent=2))
