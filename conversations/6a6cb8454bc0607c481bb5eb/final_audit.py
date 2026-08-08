#!/usr/bin/env python3
"""Final audit: verify all pages return 200, check for remaining stale data, compile summary."""
import urllib.request, ssl, json, re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

base = "https://verdischain.com"
pages = [
    "/", "/explorer/", "/dex/", "/wallet/", "/sale/", "/tokenomics/", "/faucet/",
    "/whitepaper/", "/validators/", "/eco/", "/referral/", "/incentives/",
    "/docs/", "/blog/", "/developers/", "/download/", "/contact/", "/status/",
    "/legal/disclaimer.html", "/legal/privacy.html", "/legal/terms.html",
    "/api/", "/api/docs/", "/privacy/", "/terms/"
]

results = {"pass": [], "fail": [], "issues": []}

for page in pages:
    url = base + page + ("?nocache=99999" if "?" not in page else "&nocache=99999")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, context=ctx, timeout=10)
        status = resp.status
        content = resp.read().decode("utf-8", errors="replace")
        
        # Check for stale pricing
        if "$0.010" in content and page not in ["/", "/whitepaper/"]:
            results["issues"].append(f"{page}: STALE $0.010 price found")
        
        # Check for 20% bonus in buy section (should be 30% for Phase 1)
        if "incl. 20% bonus" in content and page == "/sale/":
            results["issues"].append(f"{page}: STALE 20% bonus in buy section")
        
        # Check for old GitHub URLs
        if "github.com/verdischain/" in content:
            results["issues"].append(f"{page}: OLD GitHub URL verdischain/")
        
        # Check for old green color on non-homepage
        if "#00ff88" in content and page not in ["/", "/404/", "/_not-found/"]:
            results["issues"].append(f"{page}: OLD GREEN #00ff88")
        
        # Check for fake tree count
        if "526,000" in content:
            results["issues"].append(f"{page}: OLD TREE COUNT 526,000")
        
        # Check for wrong vesting amount
        if "312,500,000" in content or "312.5M VRDX" in content:
            results["issues"].append(f"{page}: OLD VESTING 312.5M/mo")
        
        # Check for +900% ROI
        if "+900%" in content:
            results["issues"].append(f"{page}: STALE ROI +900%")
        
        # Check for VRD ticker (without X)
        if re.search(r'\bVRD\b(?!X)', content):
            results["issues"].append(f"{page}: WRONG TICKER VRD")
        
        results["pass"].append(f"{page} [{status}]")
    except Exception as e:
        results["fail"].append(f"{page} [{str(e)[:50]}]")

print("=== PAGE STATUS ===")
for p in results["pass"]:
    print(f"  ✓ {p}")
for f in results["fail"]:
    print(f"  ✗ {f}")

print(f"\n=== ISSUES FOUND ===")
if results["issues"]:
    for issue in sorted(set(results["issues"])):
        print(f"  ! {issue}")
else:
    print("  No issues found")

# Check RPC
try:
    rpc_url = "https://verdischain.com/rpc"
    data = json.dumps({"jsonrpc":"2.0","id":1,"method":"chain.getHeader","params":[]}).encode()
    req = urllib.request.Request(rpc_url, data=data, headers={"Content-Type":"application/json"})
    resp = urllib.request.urlopen(req, context=ctx, timeout=10)
    rpc_result = json.loads(resp.read().decode())
    if "result" in rpc_result:
        print(f"\n=== NODE STATUS ===")
        print(f"  Block: #{int(rpc_result['result']['number'], 16)}")
    else:
        print(f"\n=== NODE STATUS ===")
        print(f"  RPC Error: {rpc_result.get('error', 'unknown')}")
except Exception as e:
    print(f"\n=== NODE STATUS ===")
    print(f"  RPC Error: {str(e)[:50]}")
