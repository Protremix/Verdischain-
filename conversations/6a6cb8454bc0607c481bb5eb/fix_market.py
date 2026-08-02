with open("/opt/verdis/app/dist/api/server.js", "r") as f:
    c = f.read()

# Fix token market endpoint: use VRS for pool lookup but return VRDX symbol
old_market = "res.json(this.marketTracker.getMarketStats('VRDX', ts.getTotalSupply(), ts.getMaxSupply()));"
new_market = """const stats = this.marketTracker.getMarketStats('VRS', 15000000000, 100000000000);
            stats.symbol = 'VRDX';
            stats.circulatingSupply = 15000000000;
            stats.marketCap = (stats.priceUSD || 0.0005) * 15000000000;
            // Map VRS to VRDX in pool pairs
            if (stats.pools) stats.pools = stats.pools.map(p => {
                p.pair = p.pair.replace(/VRS/g, 'VRDX');
                if (p.reserves) {
                    if (p.reserves.tokenA === 'VRS') p.reserves.tokenA = 'VRDX';
                    if (p.reserves.tokenB === 'VRS') p.reserves.tokenB = 'VRDX';
                }
                return p;
            });
            res.json(stats);"""

if old_market in c:
    c = c.replace(old_market, new_market)
    print("Token market endpoint fixed")
else:
    # Try to find the actual line
    import re
    match = re.search(r"getMarketStats\('VRDX'.*?\);", c)
    if match:
        c = c.replace(match.group(0), new_market.rstrip(';'))
        print("Token market endpoint fixed (regex)")
    else:
        match2 = re.search(r"getMarketStats\('VRS'.*?\);", c)
        if match2:
            c = c.replace(match2.group(0), new_market.rstrip(';'))
            print("Token market endpoint fixed (found VRS)")
        else:
            print("ERROR: Could not find market stats call")

# Also fix the other market stats endpoint at line 921
# The blockchain info endpoint that also returns market stats
old_info = "symbol: 'VRDX',\n                circulatingSupply: 15000000000,\n                maxSupply: ts.getMaxSupply(),\n                marketCap: (price || 0.0005) * 15000000000,"
if old_info in c:
    print("Blockchain info endpoint already has VRDX")

with open("/opt/verdis/app/dist/api/server.js", "w") as f:
    f.write(c)
print("Done")
