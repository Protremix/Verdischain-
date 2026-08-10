#!/usr/bin/env python3
"""Seed DEX pools using Alice via HTTP RPC with proper nonce management"""
from substrateinterface import SubstrateInterface, Keypair
import time

substrate = SubstrateInterface(url="http://127.0.0.1:9933", ss58_format=909, auto_discover=True)
signer = Keypair.create_from_uri("//Alice")
print(f"Signing as: {signer.ss58_address}")

pools = [
    ("VRDX", "TREE", 200_000_000_000, 200_000_000_000),
    ("VRDX", "GREEN", 200_000_000_000, 200_000_000_000),
    ("ECO", "CARBON", 100_000_000_000, 100_000_000_000),
    ("VRDX", "REDD", 100_000_000_000, 100_000_000_000),
]

for i, (token_a, token_b, amount_a, amount_b) in enumerate(pools):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Get fresh nonce each time
            nonce = substrate.get_account_nonce(signer.ss58_address)
            call = substrate.compose_call("AmmDex", "create_pool", {
                "token_a": token_a.encode("utf-8"),
                "token_b": token_b.encode("utf-8"),
                "amount_a": amount_a,
                "amount_b": amount_b,
            })
            extrinsic = substrate.create_signed_extrinsic(call, signer, nonce=nonce)
            result = substrate.submit_extrinsic(extrinsic, wait_for_inclusion=False)
            print(f"Pool {token_a}/{token_b}: OK (hash={result.extrinsic_hash[:16]}...)")
            time.sleep(6)  # Wait for block inclusion
            break
        except Exception as e:
            print(f"Pool {token_a}/{token_b}: attempt {attempt+1} FAILED - {e}")
            time.sleep(6)
    
# Wait for final block
time.sleep(5)

# Verify pools via HTTP RPC
import json, urllib.request
req = urllib.request.Request("http://127.0.0.1:9933", 
    data=json.dumps({"id":1,"jsonrpc":"2.0","method":"amm_getAllPools","params":[]}).encode(),
    headers={"Content-Type": "application/json"})
try:
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read())
    pools_count = len(data.get("result", []))
    print(f"\nTotal DEX pools: {pools_count}")
    for p in data.get("result", []):
        print(f"  Pool {p.get('pool_id', '?')}: {p.get('token_a', '?')}/{p.get('token_b', '?')}")
except Exception as e:
    print(f"RPC error: {e}")
