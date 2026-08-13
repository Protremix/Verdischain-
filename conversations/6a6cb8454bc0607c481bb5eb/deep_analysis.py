import os
import re
from bs4 import BeautifulSoup

# List of all 28 pages
pages_info = [
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

# Load external scripts
external_js = {}
js_dir = "audit_data/js"
if os.path.exists(js_dir):
    for f in os.listdir(js_dir):
        with open(os.path.join(js_dir, f), "r", encoding="utf-8") as file:
            external_js[f] = file.read()

# Let's inspect verdis.js specifically first
print("=== VERDIS.JS CONTENT SUMMARY ===")
verdis_js = external_js.get("verdis.js", "")
print("verdis.js length:", len(verdis_js))

# Regexes for fetch, XHR, WebSocket, API endpoints
fetch_pattern = re.compile(r'fetch\s*\(\s*[`\'"]([^`\'"]+)[`\'"]|\bfetch\s*\(\s*([^)]+)\)', re.IGNORECASE)
xhr_pattern = re.compile(r'XMLHttpRequest|\.open\s*\(\s*[`\'"](GET|POST|PUT|DELETE)[`\'"]\s*,\s*[`\'"]([^`\'"]+)[`\'"]', re.IGNORECASE)
ws_pattern = re.compile(r'new\s+WebSocket\s*\(\s*[`\'"]([^`\'"]+)[`\'"]|ws[s]?://[^\s`\'"]+', re.IGNORECASE)
api_endpoint_pattern = re.compile(r'[`\'"](/api/[^`\'"]*|https?://[^\s`\'"]+)[\'"]', re.IGNORECASE)

print("\n=== SEARCHING VERDIS.JS ===")
print("Fetches in verdis.js:")
for m in fetch_pattern.finditer(verdis_js):
    print("  ", m.group(0))

print("WS in verdis.js:")
for m in ws_pattern.finditer(verdis_js):
    print("  ", m.group(0))

print("API strings in verdis.js:")
for m in set(re.findall(r'[\'"](/api/[^\'"]*|https?://[^\'"]+)[\'"]', verdis_js)):
    print("  ", m)

