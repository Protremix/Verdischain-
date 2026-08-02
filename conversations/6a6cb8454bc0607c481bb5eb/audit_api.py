import urllib.request, json

base = "http://localhost:3200"
tests = [
    ("Wallet Create", "POST", "/api/wallet/create", {}, "address"),
    ("Wallet Import", "POST", "/api/wallet/import", {"privateKey":"b057f34129d35ec569d83bf5321adedea99b94a3105b26f2e1ef6af08b880e00"}, "address"),
    ("Wallet Balance", "GET", "/api/wallet/0xda89168856473f152dde8b5206213f7253e45f0d/balance", None, "balance"),
    ("Wallet Tokens", "GET", "/api/wallet/0xda89168856473f152dde8b5206213f7253e45f0d/tokens", None, "tokens"),
    ("Wallet Vesting", "GET", "/api/wallet/0xda89168856473f152dde8b5206213f7253e45f0d/vesting", None, "locked"),
    ("Wallet Txs", "GET", "/api/wallet/0xda89168856473f152dde8b5206213f7253e45f0d/transactions", None, None),
    ("Staking Summary", "GET", "/api/staking/0xda89168856473f152dde8b5206213f7253e45f0d", None, "staked"),
    ("Staking Delegations", "GET", "/api/staking/delegations/0xda89168856473f152dde8b5206213f7253e45f0d", None, "delegations"),
    ("Staking Rewards", "GET", "/api/staking/rewards/0xda89168856473f152dde8b5206213f7253e45f0d", None, "totalStaked"),
    ("DEX Pools", "GET", "/api/dex/pools", None, None),
    ("Token Market", "GET", "/api/token/market", None, "symbol"),
    ("Eco Credits", "GET", "/api/eco/credits", None, "totalCredits"),
    ("Eco Projects", "GET", "/api/eco/projects", None, "totalTrees"),
    ("Eco Validators", "GET", "/api/eco/validators", None, "avgGreenScore"),
    ("Validators", "GET", "/api/validators", None, None),
    ("Blockchain Info", "GET", "/api/blockchain/info", None, "height"),
    ("Network Info", "GET", "/api/network/info", None, "chainId"),
    ("Explorer Stats", "GET", "/api/explorer/stats", None, "blockHeight"),
    ("Security Audit", "GET", "/api/security/audit", None, None),
    ("Health", "GET", "/api/monitoring/health", None, "status"),
    ("Faucet Status", "GET", "/api/faucet/status", None, "amount"),
    ("Eco Impact", "GET", "/api/eco/impact", None, None),
    ("Green Scores", "GET", "/api/eco/green-scores", None, None),
    ("Carbon Credits", "GET", "/api/eco/carbon/credits", None, None),
]

passed = 0
failed = 0
for name, method, path, body, key in tests:
    try:
        if method == "GET":
            req = urllib.request.Request(base + path)
        else:
            req = urllib.request.Request(base + path, data=json.dumps(body).encode(), headers={"Content-Type":"application/json"}, method="POST")
        resp = urllib.request.urlopen(req, timeout=5)
        data = json.loads(resp.read())
        if key:
            val = data.get(key, "?")
            if isinstance(val, list):
                val = str(len(val)) + " items"
            print("  PASS  %-25s -> %s" % (name, val))
        else:
            if isinstance(data, list):
                print("  PASS  %-25s -> %d items" % (name, len(data)))
            else:
                print("  PASS  %-25s -> OK" % name)
        passed += 1
    except Exception as e:
        print("  FAIL  %-25s -> %s" % (name, str(e)[:50]))
        failed += 1

# Test JSON-RPC
try:
    req = urllib.request.Request(base + "/rpc", data=json.dumps({"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}).encode(), headers={"Content-Type":"application/json"})
    resp = urllib.request.urlopen(req, timeout=5)
    data = json.loads(resp.read())
    print("  PASS  %-25s -> block=%d" % ("JSON-RPC", int(data['result'],16)))
    passed += 1
except Exception as e:
    print("  FAIL  %-25s -> %s" % ("JSON-RPC", e))
    failed += 1

sep = "=" * 50
print("\n" + sep)
print("RESULTS: %d/%d passed (%d failed)" % (passed, passed+failed, failed))
