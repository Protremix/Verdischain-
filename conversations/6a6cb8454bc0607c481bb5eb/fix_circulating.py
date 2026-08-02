#!/usr/bin/env python3
"""Fix circulating supply display in explorer.html - use mkt.circulatingSupply instead of missing tkn.circulating"""

filepath = "/opt/verdis/app/dist/web/explorer.html"
with open(filepath, "r") as f:
    content = f.read()

# Fix 1: Add circulating supply from mkt (token/market) instead of tkn (tokenomics/stats which doesn't exist)
old = """  if(tkn){
    document.getElementById('stat-circulating').textContent=fmt(tkn.circulating||0,0);
    tokenomicsCache=tkn;
  }"""

new = """  if(mkt){
    document.getElementById('stat-circulating').textContent=fmt(mkt.circulatingSupply||0,0);
  }
  if(tkn){
    tokenomicsCache=tkn;
  }"""

if old in content:
    content = content.replace(old, new)
    with open(filepath, "w") as f:
        f.write(content)
    print("OK: Fixed circulating supply to use mkt.circulatingSupply from /api/token/market")
else:
    print("FAILED: Could not find target block")
