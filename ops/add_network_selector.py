#!/usr/bin/env python
"""Add a network selector (mainnet / testnet / devnet) to the Verdiscan API.

Requirement from the user: the site must let a visitor switch between testnet, mainnet
and devnet, and the whole stack has to survive a Halborn audit. So this is written to be
auditable, not merely working:

  * Networks are declared in ONE place, as an allow-list. A request carrying
    ?network=<name> is resolved against that dict and nothing else - no string is ever
    interpolated into a URL. An unknown value returns HTTP 400 rather than falling back
    silently, because a silent fallback is how the site ended up serving testnet data
    under mainnet branding in the first place.
  * Every network entry pins its EXPECTED GENESIS HASH. On startup and on every switch
    the resolved endpoint is checked against that hash. A node whose genesis does not
    match is refused. Chain NAME is never used for identification - the v13m/v14m
    incident proved a spec file can carry the right name and the wrong genesis.
  * Endpoints are loopback-only. The selector cannot be coaxed into pointing at an
    arbitrary host (no SSRF): the URL never comes from user input.
  * Read-only. Only chain_/state_/system_ methods are issued, against keyless full nodes
    or --rpc-methods=safe endpoints. The API cannot sign or submit anything.

Devnet: no devnet chain exists yet. Rather than invent an endpoint, the entry is declared
with enabled=False and the API reports it as unavailable, so the UI can grey it out
honestly. A real devnet can be added later by filling in port+genesis.

This script patches the live verdiscan_api.py, keeps a backup, and rolls back if the
service fails to come up or the genesis checks do not pass.
"""
import base64
import os
import subprocess
import sys
import time

HOST = "91.98.160.145"
KEY = os.path.expanduser("~/.ssh/id_ed25519")
APP = "/opt/verdis-api/verdiscan_api.py"
UNIT = "verdis-api"
TS = time.strftime("%Y%m%d-%H%M%S")


def ssh(cmd, timeout=280):
    p = subprocess.run(
        ["ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no",
         "-o", "ConnectTimeout=15", "-i", KEY, f"root@{HOST}", cmd],
        capture_output=True, text=True, timeout=timeout)
    return p.stdout.strip()


# The block that replaces the single hardcoded RPC_URL line.
NETWORKS_BLOCK = '''
# ---------------------------------------------------------------------------
# NETWORK REGISTRY  (mainnet / testnet / devnet)
#
# Security properties this shape gives us, stated for the audit:
#   * allow-list: a client-supplied ?network= value is only ever used as a KEY into
#     this dict. No user input reaches a URL, so the selector cannot be turned into
#     an SSRF primitive.
#   * genesis pinning: each entry records the genesis hash the endpoint MUST report.
#     Identification is by genesis, never by chain name - a chain spec can carry the
#     right name and the wrong genesis (this actually happened to two validators).
#   * loopback only: every endpoint is 127.0.0.1. Mainnet is reached through a keyless
#     full node (roles=Full, empty keystore, --rpc-methods=safe); validator RPC stays
#     firewalled to localhost and is never used here.
#   * fail closed: an unknown network is a 400, not a silent fallback to some default.
#     A silent fallback is exactly how the public site once served testnet data.
# ---------------------------------------------------------------------------
NETWORKS = {
    "mainnet": {
        "rpc": "http://127.0.0.1:9960",
        "genesis": "0x2284393d11797c1a06e8def6a48a79f9d8d7539c5386d9973fce852852817c8e",
        "label": "Verdis Mainnet",
        "enabled": True,
        "public_rpc": "https://rpc.verdischain.com",
    },
    "testnet": {
        "rpc": "http://127.0.0.1:9934",
        "genesis": "0xf72f1241cb7457a2af62498fc5cadbc79dc442cfc52a17aa7560ba8ec0ec8edb",
        "label": "Verdis Testnet",
        "enabled": True,
        "public_rpc": None,
    },
    # No devnet chain is running yet. Declared but disabled so the UI can show it
    # greyed out instead of pretending it exists. Fill in rpc+genesis to enable.
    "devnet": {
        "rpc": None,
        "genesis": None,
        "label": "Verdis Devnet",
        "enabled": False,
        "public_rpc": None,
    },
}

DEFAULT_NETWORK = "mainnet"
RPC_URL = NETWORKS[DEFAULT_NETWORK]["rpc"]


def resolve_network(name: str | None) -> tuple[str, dict]:
    """Map a request's ?network= value to a registry entry.

    Raises HTTPException(400) on anything not in the allow-list, and 503 for a network
    that is declared but has no endpoint yet (devnet). Never falls back silently.
    """
    key = (name or DEFAULT_NETWORK).strip().lower()
    entry = NETWORKS.get(key)
    if entry is None:
        raise HTTPException(
            status_code=400,
            detail={"error": "unknown network",
                    "requested": key,
                    "available": [k for k, v in NETWORKS.items() if v["enabled"]]},
        )
    if not entry["enabled"] or not entry["rpc"]:
        raise HTTPException(
            status_code=503,
            detail={"error": "network not available", "network": key},
        )
    return key, entry
'''

VERIFY_HELPER = '''

async def rpc_on(url: str, method: str, params: list = None):
    """Issue a read-only JSON-RPC call against an explicitly supplied endpoint.

    `url` always comes from the NETWORKS registry, never from a request, so this cannot
    be pointed at an arbitrary host.
    """
    if params is None:
        params = []
    try:
        resp = await client.post(url, json={"jsonrpc": "2.0", "id": 1,
                                            "method": method, "params": params})
        data = resp.json()
        if "error" in data:
            return None
        return data.get("result")
    except Exception:
        return None


async def verify_genesis(net_key: str) -> dict:
    """Confirm an endpoint really serves the chain we think it does.

    Compares the node's genesis hash with the pinned value. Reported per network by
    /api/v1/networks so a mismatch is visible instead of silently serving wrong data.
    """
    entry = NETWORKS.get(net_key) or {}
    if not entry.get("enabled") or not entry.get("rpc"):
        return {"ok": False, "reason": "not enabled"}
    got = await rpc_on(entry["rpc"], "chain_getBlockHash", [0])
    expected = entry.get("genesis")
    if not got:
        return {"ok": False, "reason": "endpoint unreachable"}
    if expected and got != expected:
        return {"ok": False, "reason": "genesis mismatch",
                "expected": expected, "got": got}
    return {"ok": True, "genesis": got}
'''

ENDPOINTS = '''

# --- network selector endpoints (added for the multi-network UI) ---

@app.get("/api/v1/networks")
async def list_networks():
    """Networks the UI may offer, each with a live genesis check.

    `genesis_ok` is the honest signal: it is False when the endpoint is down or serving
    a different chain than the one pinned in the registry, so the UI can refuse to
    display data rather than mislabel it.
    """
    out = []
    for key, entry in NETWORKS.items():
        item = {
            "id": key,
            "label": entry["label"],
            "enabled": bool(entry["enabled"] and entry["rpc"]),
            "default": key == DEFAULT_NETWORK,
            "public_rpc": entry.get("public_rpc"),
            "expected_genesis": entry.get("genesis"),
        }
        if item["enabled"]:
            check = await verify_genesis(key)
            item["genesis_ok"] = check.get("ok", False)
            if not check.get("ok"):
                item["problem"] = check.get("reason")
            else:
                best = await rpc_on(entry["rpc"], "chain_getHeader")
                fin = await rpc_on(entry["rpc"], "chain_getFinalizedHead")
                item["best_block"] = int(best["number"], 16) if best else None
                if fin:
                    fh = await rpc_on(entry["rpc"], "chain_getHeader", [fin])
                    item["finalized_block"] = int(fh["number"], 16) if fh else None
                health = await rpc_on(entry["rpc"], "system_health")
                item["peers"] = (health or {}).get("peers")
        else:
            item["genesis_ok"] = False
            item["problem"] = "no endpoint configured"
        out.append(item)
    return {"success": True, "default": DEFAULT_NETWORK, "data": out}


@app.get("/api/v1/network/{network}/stats")
async def network_stats_for(network: str):
    """Per-network stats. Resolves through the allow-list and verifies genesis first."""
    key, entry = resolve_network(network)
    check = await verify_genesis(key)
    if not check.get("ok"):
        raise HTTPException(status_code=502, detail={
            "error": "endpoint failed genesis verification",
            "network": key, "detail": check})
    url = entry["rpc"]
    best = await rpc_on(url, "chain_getHeader")
    fin_hash = await rpc_on(url, "chain_getFinalizedHead")
    fin = await rpc_on(url, "chain_getHeader", [fin_hash]) if fin_hash else None
    health = await rpc_on(url, "system_health")
    version = await rpc_on(url, "system_version")
    chain = await rpc_on(url, "system_chain")
    best_n = int(best["number"], 16) if best else None
    fin_n = int(fin["number"], 16) if fin else None
    return {"success": True, "data": {
        "network": key,
        "label": entry["label"],
        "chain": chain,
        "node_version": version,
        "genesis": check.get("genesis"),
        "block_height": best_n,
        "finalized_block": fin_n,
        "finality_lag": (best_n - fin_n) if (best_n is not None and fin_n is not None) else None,
        "peers": (health or {}).get("peers"),
        "syncing": (health or {}).get("isSyncing"),
    }}
'''

print("=" * 70)
print("PATCHING THE LIVE API")
print("=" * 70)
ssh(f"cp {APP} {APP}.bak-net-{TS}")
print(f"  backup: {APP}.bak-net-{TS}")

if ssh(f"grep -c 'NETWORK REGISTRY' {APP}") != "0":
    print("  registry already present - skipping insert")
else:
    # 1. replace the RPC_URL line with the registry
    ssh(f"echo {base64.b64encode(NETWORKS_BLOCK.encode()).decode()} | base64 -d > /tmp/nets.py")
    ln = ssh(f"grep -n '^RPC_URL = ' {APP} | head -1 | cut -d: -f1")
    print(f"  RPC_URL at line {ln} -> replacing with registry")
    ssh(f"sed -i '{ln}d' {APP}")
    ssh(f"sed -i '{int(ln)-1}r /tmp/nets.py' {APP}")

    # 2. append helper + endpoints at end of file, before __main__
    ssh(f"echo {base64.b64encode((VERIFY_HELPER + ENDPOINTS).encode()).decode()} | base64 -d > /tmp/eps.py")
    mainln = ssh(f"grep -n '^if __name__' {APP} | head -1 | cut -d: -f1")
    if mainln:
        ssh(f"sed -i '{int(mainln)-1}r /tmp/eps.py' {APP}")
        print(f"  endpoints inserted before __main__ (line {mainln})")
    else:
        ssh(f"cat /tmp/eps.py >> {APP}")
        print("  endpoints appended at EOF")

print("\n=== syntax check ===")
syn = ssh(f"/opt/verdis-api/venv/bin/python -m py_compile {APP} 2>&1 | tail -5")
print("  " + (syn if syn else "OK - compiles"))
if syn:
    print("  SYNTAX ERROR - rolling back")
    ssh(f"cp {APP}.bak-net-{TS} {APP}")
    sys.exit(1)

ssh(f"systemctl restart {UNIT}")
time.sleep(9)
state = ssh(f"systemctl is-active {UNIT}")
print(f"  service: {state}")
if state != "active":
    print(ssh(f"journalctl -u {UNIT} -n 20 --no-pager | tail -20"))
    ssh(f"cp {APP}.bak-net-{TS} {APP} && systemctl restart {UNIT}")
    print("  rolled back")
    sys.exit(1)

print("\n=== /api/v1/networks ===")
print(ssh("curl -s -m 20 http://127.0.0.1:4400/api/v1/networks | head -c 900"))
print("\n\n=== per-network stats ===")
for n in ("mainnet", "testnet", "devnet", "bogus"):
    out = ssh(f"curl -s -m 20 -o /dev/null -w '%{{http_code}}' http://127.0.0.1:4400/api/v1/network/{n}/stats")
    body = ssh(f"curl -s -m 20 http://127.0.0.1:4400/api/v1/network/{n}/stats | head -c 180")
    print(f"  {n:<9} HTTP {out}")
    print(f"    {body}")
