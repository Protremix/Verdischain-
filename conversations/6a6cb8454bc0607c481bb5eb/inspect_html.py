import os
import re

WEB_DIR = "/opt/verdis/app/dist/web"
files = sorted([f for f in os.listdir(WEB_DIR) if f.endswith(".html")])

for fname in files:
    fpath = os.path.join(WEB_DIR, fname)
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    
    logos = re.findall(r'<a[^>]*class=["\'][^"\']*logo[^"\']*["\'][^>]*>[\s\S]*?</a>', content, re.IGNORECASE)
    favicons = re.findall(r'<link[^>]*rel=["\'][^"\']*icon[^"\']*["\'][^>]*>', content, re.IGNORECASE)
    apple_icons = re.findall(r'<link[^>]*rel=["\'][^"\']*apple-touch-icon[^"\']*["\'][^>]*>', content, re.IGNORECASE)
    print(f"=== {fname} ===")
    print(f"Favicons found ({len(favicons)}): {favicons}")
    print(f"Apple touch icons found ({len(apple_icons)}): {apple_icons}")
    print(f"Logo anchors found ({len(logos)}):")
    for l in logos:
        print("  ---", repr(l[:150]))
