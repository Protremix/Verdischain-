#!/usr/bin/env python
"""Route /api/v1 and /rpc on the explorer vhost to the live backend.

The gap that made the explorer look broken: verdis-api on 127.0.0.1:4400 was answering
correctly, but explorer-verdischain-com.conf only had `root /var/www/verdiscan/explorer`
and a SPA fallback. So every frontend fetch('/api/v1/...') matched the static location,
fell through to index.html and came back as content-type text/html with status 200 -
which is why the page sat on "Loading..." forever with BLOCK HEIGHT "—". And fetch('/rpc')
returned 405 because only the apex vhost proxies the node.

Adds to the explorer vhost:
  location /api/v1/ -> 127.0.0.1:4400   (read-only mainnet API)
  location = /rpc   -> 127.0.0.1:9960   (keyless full node, rpc-methods=safe)

Also adds a small proxy cache so repeated block/stat queries do not hammer the node,
and keeps CORS off (the API sets allow_origins itself).

Safety: config is backed up, `nginx -t` must pass before reload, and on failure the
backup is restored and nginx reloaded again, so the site cannot be left down.
"""
import os
import subprocess
import sys
import time

HOST = "91.98.160.145"
KEY = os.path.expanduser("~/.ssh/id_ed25519")
CONF = "/etc/nginx/sites-enabled/explorer-verdischain-com.conf"
TS = time.strftime("%Y%m%d-%H%M%S")


def ssh(cmd, timeout=280):
    p = subprocess.run(
        ["ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no",
         "-o", "ConnectTimeout=15", "-i", KEY, f"root@{HOST}", cmd],
        capture_output=True, text=True, timeout=timeout)
    return p.stdout.strip()


print("=== current explorer vhost ===")
print(ssh(f"grep -nE 'server_name|location|proxy_pass|root ' {CONF} | head -20"))

ssh(f"cp {CONF} {CONF}.bak-{TS}")
print(f"\nbackup: {CONF}.bak-{TS}")

# Build the location blocks. Inserted just before the SPA catch-all so they win.
block = r'''
    # --- live mainnet data (added during the site audit) ---
    # The explorer frontend fetches /api/v1/*. Without these blocks the requests fell
    # through to the static root and returned index.html as text/html, which is why
    # every metric showed "Loading..." forever.
    location /api/v1/ {
        proxy_pass http://127.0.0.1:4400;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 30s;
        proxy_connect_timeout 5s;
        # short cache: block height changes every 6s, so 3s keeps the node calm
        # without the UI looking stale
        proxy_cache verdis_api_cache;
        proxy_cache_valid 200 3s;
        proxy_cache_use_stale error timeout updating;
        add_header X-Cache-Status $upstream_cache_status always;
    }

    # JSON-RPC for the parts of the UI that talk to the chain directly.
    # Points at the KEYLESS full node (127.0.0.1:9960, --rpc-methods=safe).
    # Never point this at a validator: those are firewalled to localhost deliberately.
    location = /rpc {
        proxy_pass http://127.0.0.1:9960;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 60s;
        client_max_body_size 512k;
    }
'''

import base64
enc = base64.b64encode(block.encode()).decode()
ssh(f"echo {enc} | base64 -d > /tmp/api_block.conf")

# cache zone must live in the http context
cache_dir = "/etc/nginx/conf.d/verdis_api_cache.conf"
cache = ('proxy_cache_path /var/cache/nginx/verdis_api levels=1:2 '
         'keys_zone=verdis_api_cache:10m max_size=200m inactive=60s use_temp_path=off;\n')
ssh(f"mkdir -p /var/cache/nginx/verdis_api && chown -R www-data:www-data /var/cache/nginx/verdis_api")
if not ssh(f"test -f {cache_dir} && echo yes"):
    ssh(f"echo {base64.b64encode(cache.encode()).decode()} | base64 -d > {cache_dir}")
    print(f"  added cache zone: {cache_dir}")

# insert before the SPA fallback `location / {`
already = ssh(f"grep -c 'location /api/v1/' {CONF}")
if already != "0":
    print("  /api/v1 block already present - not duplicating")
else:
    ln = ssh(f"grep -n 'location / {{' {CONF} | head -1 | cut -d: -f1")
    if not ln:
        print("  could not find the SPA fallback location - aborting")
        sys.exit(1)
    print(f"  inserting before line {ln} (the SPA fallback)")
    ssh(f"sed -i '{int(ln)-1}r /tmp/api_block.conf' {CONF}")

print("\n=== nginx -t ===")
test = ssh("nginx -t 2>&1 | tail -4")
print(test)
if "successful" not in test:
    print("  CONFIG INVALID - restoring backup")
    ssh(f"cp {CONF}.bak-{TS} {CONF} && nginx -t 2>&1 | tail -2 && systemctl reload nginx")
    sys.exit(1)

ssh("systemctl reload nginx")
time.sleep(4)
print(f"  nginx: {ssh('systemctl is-active nginx')}")

print("\n=== verify from the internet ===")
for path, expect in (("/api/v1/network/stats", "json"),
                     ("/api/v1/block/last", "json"),
                     ("/api/v1/validators", "json"),
                     ("/api/v1/token/info", "json")):
    out = subprocess.run(
        ["curl", "-s", "-m", "20", "-w", "|%{http_code}|%{content_type}",
         f"https://explorer.verdischain.com{path}"],
        capture_output=True, text=True, timeout=60).stdout
    parts = out.rsplit("|", 2)
    body = parts[0][:120] if parts else ""
    code = parts[1] if len(parts) > 2 else "?"
    ct = parts[2] if len(parts) > 2 else "?"
    flag = "OK " if "json" in ct else "STILL HTML"
    print(f"  {flag} {path:<28} {code} {ct}")
    print(f"      {body}")

rpc = subprocess.run(
    ["curl", "-s", "-m", "20", "-H", "Content-Type: application/json",
     "-d", '{"jsonrpc":"2.0","id":1,"method":"system_chain","params":[]}',
     "https://explorer.verdischain.com/rpc"],
    capture_output=True, text=True, timeout=60).stdout[:120]
print(f"  /rpc -> {rpc}")
