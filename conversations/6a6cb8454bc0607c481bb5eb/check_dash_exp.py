import os

WEB_DIR = "/opt/verdis/app/dist/web"

for fname in ["dashboard.html", "explorer.html"]:
    fpath = os.path.join(WEB_DIR, fname)
    if os.path.exists(fpath):
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        print(f"=== {fname} ===")
        print("Header / Nav snippet (first 2000 chars):")
        print(content[:2000])
