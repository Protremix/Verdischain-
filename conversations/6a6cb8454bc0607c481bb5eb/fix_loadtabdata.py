#!/usr/bin/env python3
"""Fix the broken loadTabData that has an embedded loadTokenomics"""

with open("/opt/verdis/app/dist/web/dashboard.html") as f:
    html = f.read()

# Find loadTabData function and replace everything from "function loadTabData" 
# to the closing "}}" before "// NATIVE WALLET" or the next section
start_marker = "function loadTabData(t){"
# Find the end - it ends with "}}" followed by newline before the wallet JS
# The switch statement ends with break}} 

start_idx = html.find(start_marker)
if start_idx == -1:
    print("ERROR: loadTabData not found")
    exit(1)

# Find the end of this function - look for the switch statement's closing
# The pattern is: switch(t){...break}}
# After that there should be a newline and then "// NATIVE WALLET" or similar
search_from = start_idx
# Find "switch(t){"
switch_idx = html.find("switch(t){", search_from)
if switch_idx == -1:
    print("ERROR: switch not found in loadTabData")
    exit(1)

# Find the closing }} after the switch
# Count braces from switch position
depth = 0
pos = switch_idx
while pos < len(html):
    if html[pos] == '{':
        depth += 1
    elif html[pos] == '}':
        depth -= 1
        if depth == 0:
            # This is the closing brace of switch
            # The function's closing } is the next }
            pos += 1
            while pos < len(html) and html[pos] in ' \t':
                pos += 1
            if pos < len(html) and html[pos] == '}':
                pos += 1  # Include the function closing brace
            break
    pos += 1

old_block = html[start_idx:pos]
print(f"Found loadTabData block: {len(old_block)} chars")
print(f"First 100: {repr(old_block[:100])}")
print(f"Last 100: {repr(old_block[-100:])}")

new_block = """function loadTabData(t){
    if(t==='nameservice')loadVNS();
    if(t==='tokenomics')loadTokenomics();
    if(t==='governance')loadGovernance();
    switch(t){
        case'overview':loadOverview();break;
        case'blocks':loadBlocks();break;
        case'txs':loadTxs();break;
        case'validators':loadValidators();break;
        case'dex':loadDex();break;
        case'staking':loadStaking();break;
        case'eco':loadEco();break;
        case'governance':loadGovernance();break;
        case'contracts':loadContracts();break;
        case'nft':loadNFT();break;
        case'wallet':if(wallet)loadWalletData();break;
        case'sale':loadSale();break;
        case'faucet':break;
    }
}"""

html = html[:start_idx] + new_block + html[pos:]

with open("/opt/verdis/app/dist/web/dashboard.html", "w") as f:
    f.write(html)
print("Fixed loadTabData successfully!")
