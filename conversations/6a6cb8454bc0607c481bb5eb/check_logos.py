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
    if not os.path.exists(fpath): continue
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    
    print(f"==================== {fname} ====================")
    # Find header/nav logo elements
    matches = re.findall(r'<a[^>]*class=["\'][^"\']*(logo|brand|nav)[^"\']*["\'][^>]*>[\s\S]*?</a>', content, re.IGNORECASE)
    for m in matches:
        # print match
        full_matches = [x for x in re.finditer(r'<a[^>]*class=["\'][^"\']*(logo|brand|nav)[^"\']*["\'][^>]*>[\s\S]*?</a>', content, re.IGNORECASE)]
        for fm in full_matches:
            if "verdis" in fm.group(0).lower() or "logo" in fm.group(0).lower():
                print("LOGO ANCHOR:")
                print(fm.group(0))
                print("-" * 40)

    # Find favicon links
    favs = re.findall(r'<link[^>]*rel=["\'][^"\']*(icon|shortcut|apple)[^"\']*["\'][^>]*>', content, re.IGNORECASE)
    print("FAVICON TAGS:", favs)
