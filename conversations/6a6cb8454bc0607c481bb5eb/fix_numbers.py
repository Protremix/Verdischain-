#!/usr/bin/env python3
"""Fix all token symbols and numbers on the Verdis blockchain server."""

import re
import os
import shutil

BASE = '/opt/verdis/app/dist'

def fix_file(filepath, replacements):
    """Apply a list of (old, new) replacements to a file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    original = content
    for old, new in replacements:
        content = content.replace(old, new)
    
    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"  ✅ Fixed: {filepath}")
        return True
    print(f"  ⏭️  No changes: {filepath}")
    return False

def main():
    print("🔧 Verdis Number Fix — Making numbers real\n")
    
    # === 1. Fix dist/api/server.js ===
    print("📄 Fixing dist/api/server.js...")
    server_path = os.path.join(BASE, 'api/server.js')
    
    with open(server_path, 'r') as f:
        content = f.read()
    
    # Fix 1: Circulating supply — replace ts.getTotalSupply() with 15000000000 in the token/info endpoint
    # The line is: circulatingSupply: ts.getTotalSupply(),
    content = content.replace(
        "circulatingSupply: ts.getTotalSupply(),",
        "circulatingSupply: 15000000000,"
    )
    
    # Fix 2: Market cap — replace price * ts.getTotalSupply() with price * 15000000000
    # The line is: marketCap: price * ts.getTotalSupply(),
    content = content.replace(
        "marketCap: price * ts.getTotalSupply(),",
        "marketCap: price * 15000000000,"
    )
    
    # Fix 3: Pool display — remove the VRS→VRDX mapping
    # Old: pair: `${p.tokenA === 'VRS' ? 'VRDX' : p.tokenA}/${p.tokenB === 'VRS' ? 'VRDX' : p.tokenB}`
    # New: pair: `${p.tokenA}/${p.tokenB}`
    content = content.replace(
        "pair: `${p.tokenA === 'VRS' ? 'VRDX' : p.tokenA}/${p.tokenB === 'VRS' ? 'VRDX' : p.tokenB}`",
        "pair: `${p.tokenA}/${p.tokenB}`"
    )
    
    # Fix 4: Remove market stats symbol override
    # Old: mStats.symbol = 'VRDX'; mStats.pools.forEach(p => p.pair = p.pair.replace('VRS', 'VRDX')); res.json(mStats);
    # New: res.json(mStats);
    content = content.replace(
        "mStats.symbol = 'VRDX'; mStats.pools.forEach(p => p.pair = p.pair.replace('VRS', 'VRDX')); res.json(mStats);",
        "mStats.symbol = 'VRS'; res.json(mStats);"
    )
    
    # Fix 5: Token minting guard — remove VRDX alias
    content = content.replace(
        "if (token === 'VRS' || token === 'VRDX') {",
        "if (token === 'VRS') {"
    )
    content = content.replace(
        "res.status(400).json({ success: false, error: 'Cannot mint VRDX. VRDX is the native token.' });",
        "res.status(400).json({ success: false, error: 'Cannot mint VRS. VRS is the native token.' });"
    )
    
    # Fix 6: DEX swap/remove liquidity — remove VRDX→VRS aliasing
    content = content.replace(
        "const tA = tokenA === 'VRDX' ? 'VRS' : tokenA;",
        "const tA = tokenA;"
    )
    content = content.replace(
        "const tB = tokenB === 'VRDX' ? 'VRS' : tokenB;",
        "const tB = tokenB;"
    )
    content = content.replace(
        "const tIn = tokenIn === 'VRDX' ? 'VRS' : tokenIn;",
        "const tIn = tokenIn;"
    )
    content = content.replace(
        "const tOut = tokenOut === 'VRDX' ? 'VRS' : tokenOut;",
        "const tOut = tokenOut;"
    )
    
    # Fix 7: EVM info symbol
    content = content.replace(
        "symbol: 'VRDX',\n                decimals: 18,\n                explorer: 'https://verdischain.com/explorer'",
        "symbol: 'VRS',\n                decimals: 18,\n                explorer: 'https://verdischain.com/explorer'"
    )
    
    # Fix 8: Network info symbol
    content = content.replace(
        "symbol: 'VRDX',\n                tagline: 'The Eco-Friendly Blockchain'",
        "symbol: 'VRS',\n                tagline: 'The Eco-Friendly Blockchain'"
    )
    
    # Fix 9: API info symbol
    content = content.replace(
        'symbol: "VRDX",',
        'symbol: "VRS",'
    )
    
    # Fix 10: Fallback dashboard — fix VCO symbol and VRDX references
    content = content.replace("<strong>Symbol:</strong> VCO", "<strong>Symbol:</strong> VRS")
    
    # Fix 11: Fallback dashboard meta description
    content = content.replace(
        "Verdis (VRDX) is a fully functional",
        "Verdis (VRS) is a fully functional"
    )
    content = content.replace("VRDX Supply", "VRS Supply")
    content = content.replace("VRDX/CARBON, VRDX/ECO", "VRS/CARBON, VRS/ECO")
    
    # Fix 12: IDO stage comments
    content = content.replace("$0.0005/VRDX", "$0.0005/VRS")
    content = content.replace("$0.0008/VRDX", "$0.0008/VRS")
    content = content.replace("$0.001/VRDX", "$0.001/VRS")
    content = content.replace("$0.0015/VRDX", "$0.0015/VRS")
    content = content.replace("// Total: 15B VRDX", "// Total: 12B VRS")
    content = content.replace("// Total: 15B", "// Total: 12B")
    
    # Fix 13: IDO purchase endpoints
    content = content.replace("pricePerVRDX:", "pricePerVRS:")
    content = content.replace("amountVRDX:", "amountVRS:")
    content = content.replace("// Calculate VRDX per unit", "// Calculate VRS per unit")
    content = content.replace("// Calculate base VRDX from USD", "// Calculate base VRS from USD")
    content = content.replace(" VRDX. You have already purchased", " VRS. You have already purchased")
    content = content.replace("' VRDX, '", "' VRS, '")
    
    # Fix 14: Tokenomics endpoint
    content = content.replace("VRDX per block to active validators", "VRS per block to active validators")
    content = content.replace("VRDX allocated for per-block staking emissions", "VRS allocated for per-block staking emissions")
    content = content.replace("blockReward + ' VRDX'", "blockReward + ' VRS'")
    
    # Fix 15: Bridge endpoints
    content = content.replace("Insufficient VRDX balance", "Insufficient VRS balance")
    content = content.replace("VRDX locked. Bridge operator will mint wVRDX on BSC.", "VRS locked. Bridge operator will mint wVRS on BSC.")
    content = content.replace("VRDX unlocked and sent to", "VRS unlocked and sent to")
    content = content.replace("Add VCO back to user on Verdis chain", "Add VRS back to user on Verdis chain")
    content = content.replace("Undelegated \" + amount + \" VCO", "Undelegated \" + amount + \" VRS")
    
    # Fix 16: AI support bot responses
    content = content.replace("Ask me about VRDX tokens", "Ask me about VRS tokens")
    content = content.replace("VRDX tokens are available in our Seed Sale at $0.0005 per VRDX", "VRS tokens are available in our Seed Sale at $0.0005 per VRS")
    content = content.replace("stake VRDX with green validators", "stake VRS with green validators")
    content = content.replace("stake VRDX", "stake VRS")
    content = content.replace("delegate your VRDX", "delegate your VRS")
    content = content.replace("Minimum stake is 1 VRDX", "Minimum stake is 1 VRS")
    content = content.replace("VRDX/CARBON, VRDX/ECO, CARBON/ECO, TREE/VRDX, GREEN/VRDX, and REDD/VRDX", "VRS/CARBON, VRS/ECO, CARBON/ECO, TREE/VRS, GREEN/VRS, and REDD/VRS")
    content = content.replace("wrapping VRDX for use on Ethereum", "wrapping VRS for use on Ethereum")
    content = content.replace("Treasury/DAO (20B VRDX)", "Treasury/DAO (20B VRS)")
    content = content.replace("claim 1000 VRDX from the faucet", "claim 1000 VRS from the faucet")
    content = content.replace("Claim 1000 VRDX", "Claim 1000 VRS")
    content = content.replace("VRDX max supply is 100,000,000,000", "VRS max supply is 100,000,000,000")
    content = content.replace("Token price: $0.0005/VRDX", "Token price: $0.0005/VRS")
    content = content.replace("buy VRDX?", "buy VRS?")
    content = content.replace("about VRDX tokens, staking", "about VRS tokens, staking")
    
    # Fix 17: Explorer URL in token info
    content = content.replace(
        "explorer: 'http://localhost:3200',",
        "explorer: 'https://verdischain.com/explorer',"
    )
    
    # Fix 18: Website in token info  
    content = content.replace(
        "website: 'https://verdis.eco',",
        "website: 'https://verdischain.com',"
    )
    
    with open(server_path, 'w') as f:
        f.write(content)
    print(f"  ✅ Fixed: {server_path}")
    
    # === 2. Fix dist/core/security.js ===
    print("\n📄 Fixing dist/core/security.js...")
    sec_path = os.path.join(BASE, 'core/security.js')
    fix_file(sec_path, [
        ("1B VRDX max per tx", "1B VRS max per tx"),
        ("VRDX)", "VRS)"),
        ("VRDX per transaction", "VRS per transaction"),
    ])
    
    # === 3. Fix dist/index.js — Remove auto-trade bot ===
    print("\n📄 Fixing dist/index.js (removing auto-trade bot)...")
    index_path = os.path.join(BASE, 'index.js')
    with open(index_path, 'r') as f:
        index_content = f.read()
    
    # Find and remove the auto-trade bot section
    # It starts with "// === Auto-trade bot" and ends before the last section
    trade_bot_pattern = r'// === Auto-trade bot: keeps DEX active with periodic swaps ===.*?setInterval\(autoTradeBot, 10000\);\n'
    match = re.search(trade_bot_pattern, index_content, re.DOTALL)
    if match:
        index_content = re.sub(trade_bot_pattern, '', index_content, flags=re.DOTALL)
        print("  ✅ Removed auto-trade bot from index.js")
    else:
        # Try a more flexible pattern
        lines = index_content.split('\n')
        new_lines = []
        skip = False
        for line in lines:
            if 'Auto-trade bot' in line and '===' in line:
                skip = True
                continue
            if skip and 'setInterval(autoTradeBot' in line:
                skip = False
                continue
            if skip:
                continue
            new_lines.append(line)
        index_content = '\n'.join(new_lines)
        print("  ✅ Removed auto-trade bot from index.js (fallback method)")
    
    with open(index_path, 'w') as f:
        f.write(index_content)
    
    # === 4. Fix all HTML files in dist/web/ ===
    print("\n📄 Fixing HTML files in dist/web/...")
    web_dir = os.path.join(BASE, 'web')
    if os.path.isdir(web_dir):
        for filename in os.listdir(web_dir):
            if filename.endswith('.html'):
                filepath = os.path.join(web_dir, filename)
                with open(filepath, 'r') as f:
                    html_content = f.read()
                
                original = html_content
                
                # Global VRDX → VRS replacement
                html_content = html_content.replace('VRDX', 'VRS')
                html_content = html_content.replace('VCO', 'VRS')
                
                # Fix ecosystem.html specific mappings
                html_content = html_content.replace("const tokenA = p.reserves.tokenA === 'VRS' ? 'VRS' : p.reserves.tokenA;", 
                    "const tokenA = p.reserves.tokenA;")
                html_content = html_content.replace("const tokenB = p.reserves.tokenB === 'VRS' ? 'VRS' : p.reserves.tokenB;",
                    "const tokenB = p.reserves.tokenB;")
                
                if html_content != original:
                    with open(filepath, 'w') as f:
                        f.write(html_content)
                    print(f"  ✅ Fixed: {filename}")
                else:
                    print(f"  ⏭️  No changes: {filename}")
    
    # === 5. Fix any remaining VRDX references in JSON-RPC ===
    print("\n📄 Fixing dist/api/jsonrpc.js...")
    jsonrpc_path = os.path.join(BASE, 'api/jsonrpc.js')
    if os.path.exists(jsonrpc_path):
        fix_file(jsonrpc_path, [
            ("VRDX", "VRS"),
            ("VCO", "VRS"),
        ])
    
    # === 6. Fix dist/core/market.js if needed ===
    print("\n📄 Checking dist/core/market.js...")
    market_path = os.path.join(BASE, 'core/market.js')
    if os.path.exists(market_path):
        fix_file(market_path, [
            ("VRDX", "VRS"),
            ("VCO", "VRS"),
        ])
    
    # === 7. Fix dist/core/dex.js if needed ===
    print("\n📄 Checking dist/core/dex.js...")
    dex_path = os.path.join(BASE, 'core/dex.js')
    if os.path.exists(dex_path):
        fix_file(dex_path, [
            ("VRDX", "VRS"),
            ("VCO", "VRS"),
        ])
    
    print("\n✅ All fixes applied! Restarting Verdis service...")
    os.system('systemctl restart verdis.service')
    print("✅ Service restarted!")
    
    # Verify
    print("\n📊 Verification:")
    os.system('sleep 3 && curl -s http://localhost:3200/api/token/info 2>/dev/null | python3 -m json.tool 2>/dev/null | head -20')

if __name__ == '__main__':
    main()
