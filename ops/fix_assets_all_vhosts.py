#!/usr/bin/env python
"""Fix the broken /assets/ logo path on every subdomain that has it.

The bug: each subdomain vhost has its own root (e.g. /var/www/verdiscan/wallet), but the
shared HTML header references src="/assets/verdis-logo-black.png". That resolves to
<root>/assets/... which does not exist, so the header logo 404s on wallet, dex, faucet,
blog, docs, developers and validators. Confirmed in the browser: every one of those
pages reported exactly 1 image that failed to load.

The artwork is NOT touched - the user asked for logo and design to be left alone. This
only makes the existing URL resolve to the existing file at /var/www/verdiscan/assets/.

Critical nginx detail learned on the explorer vhost: a plain `location /assets/` loses
to the existing `location ~* \\.(js|css|png|...)$` regex block, because regex locations
are evaluated before prefix locations. The fix must use `^~` so the prefix match wins
outright. Without `^~` the alias silently has no effect and the file still 404s.

Each file is backed up, `nginx -t` must pass, and every logo URL is verified over HTTPS
afterwards. On a config error everything is rolled back.
"""
import base64
import os
import subprocess
import sys
import time

HOST = "91.98.160.145"
KEY = os.path.expanduser("~/.ssh/id_ed25519")
ASSETS = "/var/www/verdiscan/assets"
TS = time.strftime("%Y%m%d-%H%M%S")

VHOSTS = {
    "blog-verdischain-com.conf": "blog.verdischain.com",
    "developers-verdischain-com.conf": "developers.verdischain.com",
    "dex-verdischain-com.conf": "dex.verdischain.com",
    "docs-verdischain-com.conf": "docs.verdischain.com",
    "faucet-verdischain-com.conf": "faucet.verdischain.com",
    "validators-verdischain-com.conf": "validators.verdischain.com",
    "wallet-verdischain-com.conf": "wallet.verdischain.com",
}


def ssh(cmd, timeout=280):
    p = subprocess.run(
        ["ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no",
         "-o", "ConnectTimeout=15", "-i", KEY, f"root@{HOST}", cmd],
        capture_output=True, text=True, timeout=timeout)
    return p.stdout.strip()


def logo_status(domain):
    return subprocess.run(
        ["curl", "-s", "-o", os.devnull, "-m", "15", "-w", "%{http_code}",
         f"https://{domain}/assets/verdis-logo-black.png"],
        capture_output=True, text=True, timeout=40).stdout


print("=== before ===")
for conf, dom in VHOSTS.items():
    print(f"  {dom:<32} {logo_status(dom)}")

block = f'''
    # Shared brand assets live outside this vhost's root, so /assets/* used to 404 and
    # the header logo was broken. `^~` is required: a plain prefix location loses to the
    # existing `location ~* \\.(png|...)$` regex block and the alias would never apply.
    location ^~ /assets/ {{
        alias {ASSETS}/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }}
'''
enc = base64.b64encode(block.encode()).decode()
ssh(f"echo {enc} | base64 -d > /tmp/assets_block.conf")

print("\n=== applying ===")
touched = []
for conf, dom in VHOSTS.items():
    path = f"/etc/nginx/sites-enabled/{conf}"
    if not ssh(f"test -f {path} && echo y"):
        print(f"  {conf}: not found, skipped")
        continue
    if ssh(f"grep -c 'location ^~ /assets/' {path}") != "0":
        print(f"  {conf}: already has the alias")
        continue
    ssh(f"cp {path} {path}.bak-assets-{TS}")
    # insert before the SPA/static catch-all so it sits inside the TLS server block
    ln = ssh(f"grep -n 'location / {{' {path} | tail -1 | cut -d: -f1")
    if not ln:
        print(f"  {conf}: no 'location / {{' found, skipped")
        continue
    ssh(f"sed -i '{int(ln)-1}r /tmp/assets_block.conf' {path}")
    touched.append((path, conf))
    print(f"  {conf}: alias inserted before line {ln}")

print("\n=== nginx -t ===")
test = ssh("nginx -t 2>&1 | grep -E 'successful|emerg' | tail -3")
print("  " + test.replace("\n", "\n  "))
if "successful" not in test:
    print("  INVALID - rolling back everything")
    for path, conf in touched:
        ssh(f"cp {path}.bak-assets-{TS} {path}")
    ssh("nginx -t && systemctl reload nginx")
    sys.exit(1)

ssh("systemctl reload nginx")
time.sleep(4)
print(f"  nginx: {ssh('systemctl is-active nginx')}")

print("\n=== after (from the internet) ===")
fail = 0
for conf, dom in VHOSTS.items():
    code = logo_status(dom)
    ok = code == "200"
    if not ok:
        fail += 1
    print(f"  {'OK ' if ok else 'BAD'} {dom:<32} {code}")

print("\n=== all pages still up ===")
for dom in list(VHOSTS.values()) + ["verdischain.com", "explorer.verdischain.com",
                                    "api.verdischain.com", "rpc.verdischain.com"]:
    code = subprocess.run(
        ["curl", "-s", "-o", os.devnull, "-m", "15", "-w", "%{http_code}",
         f"https://{dom}"], capture_output=True, text=True, timeout=40).stdout
    print(f"  {dom:<32} {code}")

print(f"\nlogos still broken: {fail}")
