import os
import re

WEB_DIR = "/opt/verdis/app/dist/web"
files = [
    "landing.html", "dashboard.html", "whitepaper.html", "api-docs.html",
    "status.html", "ecosystem.html", "templates.html", "token-sale.html",
    "bridge.html", "markets.html", "explorer.html", "download.html"
]

for fname in files:
    fpath = os.path.join(WEB_DIR, fname)
    if not os.path.exists(fpath):
        print(f"MISSING: {fname}")
        continue
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    
    print(f"=== {fname} ===")
    head_match = re.search(r'<head>([\s\S]*?)</head>', content, re.IGNORECASE)
    if head_match:
        print("HEAD (first 500 chars):")
        print(head_match.group(1)[:500])
    
    print("NAV / HEADER / LOGO LINES:")
    for line in content.splitlines():
        if any(k in line.lower() for k in ["logo", "<svg", "<nav", "<header"]):
            if len(line.strip()) > 0:
                print("  ", line.strip()[:120])
