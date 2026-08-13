import os
import re
import urllib.request
import ssl
from bs4 import BeautifulSoup

base_url = "https://verdischain.com"
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

# Download all external js files found
js_files = set()

for fname in os.listdir("audit_data"):
    if not fname.endswith(".html"):
        continue
    with open(f"audit_data/{fname}", "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
        for script in soup.find_all("script"):
            src = script.get("src")
            if src:
                if src.startswith("//"):
                    src = "https:" + src
                elif src.startswith("/"):
                    src = base_url + src
                elif not src.startswith("http"):
                    src = base_url + "/" + src
                js_files.add(src)

print("Found script sources:", js_files)

os.makedirs("audit_data/js", exist_ok=True)
for js_url in js_files:
    js_name = js_url.split("/")[-1].split("?")[0]
    if not js_name:
        js_name = "script.js"
    print(f"Fetching JS {js_url}...")
    try:
        req = urllib.request.Request(js_url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
            with open(f"audit_data/js/{js_name}", "w", encoding="utf-8") as f:
                f.write(content)
    except Exception as e:
        print(f"Failed {js_url}: {e}")

