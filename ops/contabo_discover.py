#!/usr/bin/env python
"""Discover which Contabo API endpoints expose the Verdis dedicated servers.

/compute/instances returned empty: 213.136.78.63 is an AMD Ryzen 9 7900 DEDICATED
server, and Contabo's public API historically covers VPS/VDS instances. Probe the
documented and plausible endpoints to find where dedicated hardware lives, and
whether any of them lets us push an SSH key without a reboot.
"""
import json
import os
import urllib.error
import urllib.parse
import urllib.request
import uuid

SEC = os.path.join(os.environ["LOCALAPPDATA"], "hermes", "profiles", "verdis", "secrets",
                   "contabo_api.env")
cfg = dict(l.strip().split("=", 1) for l in open(SEC) if "=" in l)
API = "https://api.contabo.com/v1"


def token():
    data = urllib.parse.urlencode({
        "client_id": cfg["CONTABO_CLIENT_ID"],
        "client_secret": cfg["CONTABO_CLIENT_SECRET"],
        "username": cfg["CONTABO_USER"],
        "password": cfg["CONTABO_API_PASSWORD"],
        "grant_type": "password",
    }).encode()
    req = urllib.request.Request(
        "https://auth.contabo.com/auth/realms/contabo/protocol/openid-connect/token",
        data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["access_token"]


def call(tok, path, method="GET", body=None):
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(f"{API}{path}", data=data, method=method, headers={
        "Authorization": f"Bearer {tok}",
        "x-request-id": str(uuid.uuid4()),
        "Content-Type": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=35) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:200]
    except Exception as e:
        return 0, f"{type(e).__name__}: {e}"


tok = token()
print(f"token ok ({len(tok)} chars)\n")

paths = [
    "/compute/instances?size=50",
    "/compute/instances?size=50&page=1",
    "/dedicated/servers?size=50",
    "/dedicated-servers?size=50",
    "/servers?size=50",
    "/baremetal/servers?size=50",
    "/compute/dedicated?size=50",
    "/users",
    "/roles",
    "/tags",
    "/secrets?size=50",
    "/compute/ssh-keys?size=50",
]
for p in paths:
    st, body = call(tok, p)
    if isinstance(body, dict):
        n = len(body.get("data", [])) if "data" in body else "-"
        preview = json.dumps(body)[:130]
        print(f"{st}  {p:42} items={n}  {preview}")
    else:
        print(f"{st}  {p:42} {str(body)[:110]}")
