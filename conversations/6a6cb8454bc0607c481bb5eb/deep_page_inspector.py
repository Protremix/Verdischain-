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

def get_filename(p):
    f = p.strip("/").replace("/", "_")
    return f if f else "home"

page_reports = {}

for p in paths:
    fname = get_filename(p)
    fpath = f"audit_data/{fname}.html"
    if not os.path.exists(fpath):
        continue
    with open(fpath, "r", encoding="utf-8") as f:
        html = f.read()
    
    soup = BeautifulSoup(html, "html.parser")
    scripts = [s.string for s in soup.find_all("script") if s.string]
    script_srcs = [s.get("src") for s in soup.find_all("script") if s.get("src")]
    
    full_js = "\n// --- NEW SCRIPT TAG ---\n".join(scripts)
    
    page_reports[p] = {
        'title': soup.title.string.strip() if soup.title else '',
        'script_srcs': script_srcs,
        'full_js': full_js,
        'html': html
    }

# Print details of specific pages or write to files for analysis
with open("all_page_js.json", "w", encoding="utf-8") as f:
    json.dump({p: {'title': v['title'], 'script_srcs': v['script_srcs'], 'js_len': len(v['full_js'])} for p, v in page_reports.items()}, f, indent=2)

print("Saved all_page_js.json")
