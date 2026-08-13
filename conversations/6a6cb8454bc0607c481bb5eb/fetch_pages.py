import subprocess
import os

def fetch_page(path):
    cmd = ["ssh", "-i", os.path.expanduser("~/.ssh/verdis_deploy_key"), "-o", "StrictHostKeyChecking=no", "root@91.98.160.145", f'curl -sk -H "Host: verdischain.com" https://localhost{path}']
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.stdout

pages = {
    "homepage.html": "/",
    "sale.html": "/sale/",
    "tokenomics.html": "/tokenomics/"
}

for filename, path in pages.items():
    content = fetch_page(path)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Saved {filename} ({len(content)} bytes)")
