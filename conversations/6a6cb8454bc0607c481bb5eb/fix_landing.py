import re

with open("/var/www/verdiscan/index.html", "r") as f:
    content = f.read()

# Fix 1: Replace const blockHeight/peers with let (declared outside try)
content = content.replace(
    "const blockHeight = parseInt(blockData.result?.number || '0x0', 16);",
    "blockHeight = parseInt(blockData.result?.number || '0x0', 16);"
)
content = content.replace(
    "const peers = healthData.result?.peers || 0;",
    "peers = healthData.result?.peers || 0;"
)
# Add let declarations at the top of the function
content = content.replace(
    "async function updateLiveMetrics() {\n  const RPC = '/rpc';\n  try {",
    "async function updateLiveMetrics() {\n  const RPC = '/rpc';\n  let blockHeight = 0;\n  let peers = 0;\n  try {"
)
print("Fixed: variable scoping in updateLiveMetrics")

# Fix 2: Replace hardcoded 7 Pools Live
content = content.replace("7 Pools Live", "6 Pools Live")
print("Fixed: 7 Pools Live -> 6 Pools Live")

# Fix 3: Fix fallback in fetchDexPools
content = content.replace("'7 Pools'", "'6 Pools'")
print("Fixed: fallback 7 -> 6 pools")

with open("/var/www/verdiscan/index.html", "w") as f:
    f.write(content)
print("Done - file saved")
