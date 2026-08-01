import os, re

WEB_DIR = "/opt/verdis/app/dist/web"

for fname in ["dashboard.html", "explorer.html"]:
    fpath = os.path.join(WEB_DIR, fname)
    if os.path.exists(fpath):
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        print(f"=== {fname} BODY LOGO SEARCH ===")
        # search for verdis or logo or nav in body
        body_start = content.find("<body")
        if body_start != -1:
            body_text = content[body_start:body_start+3000]
            print(body_text)
