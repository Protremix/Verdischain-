#!/usr/bin/env python
"""Contabo API helper: get an OAuth token and install our SSH key on the
Verdis validator hosts WITHOUT rebooting them.

The token is a long JWT; never print it. Credentials come from
secrets/contabo_api.env (mode 600).
"""
import json
import os
import subprocess
import sys
import urllib.parse
import urllib.request

SEC_DIR = os.path.join(os.environ["LOCALAPPDATA"], "hermes", "profiles", "verdis", "secrets")
ENV = os.path.join(SEC_DIR, "contabo_api.env")

cfg = {}
for line in open(ENV):
    if "=" in line:
        k, v = line.strip().split("=", 1)
        cfg[k] = v

TOKEN_URL = "https://auth.contabo.com/auth/realms/contabo/protocol/openid-connect/token"
API = "https://api.contabo.com/v1"


def get_token():
    data = urllib.parse.urlencode({
        "client_id": cfg["CONTABO_CLIENT_ID"],
        "client_secret": cfg["CONTABO_CLIENT_SECRET"],
        "username": cfg["CONTABO_USER"],
        "password": cfg["CONTABO_API_PASSWORD"],
        "grant_type": "password",
    }).encode()
    req = urllib.request.Request(TOKEN_URL, data=data,
                                headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.load(r)
    t = d["access_token"]
    print(f"token acquired: {len(t)} chars, JWT={t.count('.') == 2}, expires_in={d.get('expires_in')}s")
    return t


def api(tok, path, method="GET", body=None):
    import uuid
    url = f"{API}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Bearer {tok}",
        "x-request-id": str(uuid.uuid4()),
        "Content-Type": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        return {"_http_error": e.code, "_body": e.read().decode()[:400]}


if __name__ == "__main__":
    tok = get_token()

    print("\n=== INSTANCES ===")
    inst = api(tok, "/compute/instances?size=50")
    if "_http_error" in inst:
        print(" ", inst)
    else:
        for i in inst.get("data", []):
            ips = [x.get("ip") for x in (i.get("ipConfig", {}).get("v4") and [i["ipConfig"]["v4"]] or [])]
            print(f"  id={i.get('instanceId')} name={i.get('displayName')} "
                  f"status={i.get('status')} ip={ips} region={i.get('region')} "
                  f"product={i.get('productId')}")

    print("\n=== SSH KEYS (secrets of type ssh) ===")
    sec = api(tok, "/secrets?type=ssh&size=50")
    if "_http_error" in sec:
        print(" ", sec)
    else:
        for s in sec.get("data", []):
            print(f"  id={s.get('secretId')} name={s.get('name')} type={s.get('type')}")
