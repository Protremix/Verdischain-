import os
import re
import json
import urllib.request
import urllib.error
import ssl
from bs4 import BeautifulSoup

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

pages = [
    "/", "/explorer/", "/dex/", "/whitepaper/", "/wallet/", "/sale/", "/tokenomics/",
    "/faucet/", "/validators/", "/eco/", "/docs/", "/transactions/", "/analytics/",
    "/monitoring/", "/governance/", "/blog/", "/developers/", "/download/", "/referral/",
    "/incentives/", "/contact/", "/privacy/", "/terms/", "/cookies/", "/security/",
    "/disclaimer/", "/status/", "/api/"
]

def analyze_page(path):
    fname = path.strip("/").replace("/", "_")
    if not fname:
        fname = "home"
    fpath = f"audit_data/{filename_map(path)}.html"
    
    if not os.path.exists(fpath):
        return None
    
    with open(fpath, "r", encoding="utf-8") as f:
        html = f.read()
        
    soup = BeautifulSoup(html, "html.parser")
    
    # Inline scripts
    scripts = [s.string for s in soup.find_all("script") if s.string]
    full_script = "\n".join(scripts)
    
    # Fetch calls
    # Match patterns like fetch('...'), fetch("..."), fetch(`...`), fetch(URL, ...)
    fetch_calls = []
    # Find exact string parameters to fetch
    fetch_str_matches = re.findall(r'fetch\s*\(\s*[`\'"]([^`\'"]+)[`\'"]', full_script)
    fetch_var_matches = re.findall(r'fetch\s*\(\s*([a-zA-Z0-9_\.\$\{\}\/`\'"-]+)', full_script)
    
    # XHR calls
    xhr_calls = re.findall(r'new\s+XMLHttpRequest|\.open\s*\(\s*[`\'"](GET|POST|PUT|DELETE)[`\'"]\s*,\s*[`\'"]([^`\'"]+)[`\'"]|\$\.ajax\s*\(\s*\{[^}]*url\s*:\s*[`\'"]([^`\'"]+)[`\'"]', full_script)
    
    # WebSockets
    ws_calls = re.findall(r'new\s+WebSocket\s*\(\s*[`\'"]([^`\'"]+)[`\'"]|new\s+WebSocket\s*\(\s*([a-zA-Z0-9_\.]+)\)|(wss?://[^\s`\'"]+)', full_script)
    
    # API URLs / endpoints referenced in strings
    api_endpoints = re.findall(r'[`\'"](/api/[^`\'"]*|https?://[^\s`\'"]+|wss?://[^\s`\'"]+)[\'"]', html)
    
    # Look for API definitions, variables
    api_vars = re.findall(r'(const|let|var)\s+([A-Za-z0-9_]*API[A-Za-z0-9_]*|RPC[A-Za-z0-9_]*|WS[A-Za-z0-9_]*)\s*=\s*[`\'"]([^`\'"]+)[`\'"]', full_script)

    return {
        'path': path,
        'title': soup.title.string.strip() if soup.title else "No Title",
        'script_count': len(soup.find_all("script")),
        'fetch_str': list(set(fetch_str_matches)),
        'fetch_var': list(set(fetch_var_matches)),
        'xhr_calls': xhr_calls,
        'ws_calls': ws_calls,
        'api_vars': api_vars,
        'api_endpoints': list(set(api_endpoints)),
        'full_script': full_script,
        'html': html
    }

def filename_map(path):
    fname = path.strip("/").replace("/", "_")
    return fname if fname else "home"

all_data = {}
for p in pages:
    all_data[p] = analyze_page(p)

print("Analyzed pages count:", len(all_data))
