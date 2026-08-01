import os
import re

base = 'blockchain'

# Files to process - both src/ and dist/web/ (and dist/ for compiled JS)
files_to_process = [
    # Core source
    'src/index.ts',
    'src/api/server.ts',
    'src/api/jsonrpc.ts',
    'src/core/consensus.ts',
    'src/core/market.ts',
    'src/core/security.ts',
    # Web pages (dist/web - what's served)
    'dist/web/landing.html',
    'dist/web/dashboard.html',
    'dist/web/whitepaper.html',
    'dist/web/api-docs.html',
    'dist/web/status.html',
    'dist/web/ecosystem.html',
    'dist/web/templates.html',
    'dist/web/token-sale.html',
    'dist/web/bridge.html',
    'dist/web/markets.html',
    'dist/web/explorer.html',
    # Web pages (src/web - source copies)
    'src/web/landing.html',
    'src/web/dashboard.html',
    'src/web/whitepaper.html',
    'src/web/ecosystem.html',
    'dist/web/explorer.html',
    'src/web/explorer.html',
    'src/web/markets.html',
    'src/web/token-sale.html',
    'src/web/bridge.html',
]

total_replacements = 0

for fpath in files_to_process:
    full_path = os.path.join(base, fpath)
    if not os.path.exists(full_path):
        print(f"SKIP (not found): {fpath}")
        continue
    
    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Variable/function name replacements (case-sensitive)
    content = content.replace('addVRSToken', 'addVCOToken')
    content = content.replace('priceVRS', 'priceVCO')
    content = content.replace('bonusVRS', 'bonusVCO')
    content = content.replace('baseVRS', 'baseVCO')
    content = content.replace('totalVRS', 'totalVCO')
    
    # Token symbol in code (with quotes)
    content = content.replace("'VRS'", "'VCO'")
    content = content.replace('"VRS"', '"VCO"')
    
    # Governance token $sVRS → $sVCO
    content = content.replace('$sVRS', '$sVCO')
    
    # Display text: " VRS" (space before VRS, used in UI like "1000 VRS", "VRS Supply", etc.)
    content = content.replace(' VRS ', ' VCO ')
    content = content.replace(' VRS.', ' VCO.')
    content = content.replace(' VRS,', ' VCO,')
    content = content.replace(' VRS)', ' VCO)')
    content = content.replace(' VRS\n', ' VCO\n')
    content = content.replace(' VRS</', ' VCO</')
    content = content.replace(' VRS"', ' VCO"')
    content = content.replace(' VRS\'', ' VCO\'')
    content = content.replace(' VRS;', ' VCO;')
    content = content.replace(' VRS:', ' VCO:')
    content = content.replace(' VRS+', ' VCO+')
    content = content.replace(' VRS=', ' VCO=')
    content = content.replace(' VRS}', ' VCO}')
    content = content.replace(' VRS|', ' VCO|')
    content = content.replace('(VRS)', '(VCO)')
    
    # "VRS/" for DEX pairs like VRS/CARBON, VRS/ECO
    content = content.replace('VRS/', 'VCO/')
    content = content.replace('/VRS', '/VCO')
    
    # "VRS " at start of strings or after special chars
    content = content.replace('→ VRS', '→ VCO')
    content = content.replace('= VRS', '= VCO')
    content = content.replace('+ VRS', '+ VCO')
    content = content.replace('• VRS', '• VCO')
    
    # Meta tags and titles: "Verdis (VRS)" → "Verdis (VCO)"
    content = content.replace('Verdis (VRS)', 'Verdis (VCO)')
    
    # Standalone "VRS" in comments or labels (surrounded by non-word chars or at string boundaries)
    # Be careful: only replace VRS that's clearly the token ticker
    # Pattern: VRS preceded by start-of-line, space, or special char AND followed by space, punctuation, or end
    # But we've already handled most cases above. Let's catch remaining standalone VRS
    
    # "Symbol: VRS" or "Symbol:</strong> VRS"
    content = content.replace('>VRS<', '>VCO<')
    content = content.replace(': VRS<', ': VCO<')
    
    # "VRS Supply" label
    content = content.replace('VRS Supply', 'VCO Supply')
    content = content.replace('VRS Supply', 'VCO Supply')
    
    # "VRS tokens" / "VRS token"
    content = content.replace('VRS tokens', 'VCO tokens')
    content = content.replace('VRS token', 'VCO token')
    
    # "VRS per" (block, tx, validator)
    content = content.replace('VRS per', 'VCO per')
    
    # "VRS is the native"
    content = content.replace('VRS is the', 'VCO is the')
    
    # "VRS has 18 decimals"
    content = content.replace('VRS has', 'VCO has')
    
    # "1 VRS" or "1B VRS" patterns already handled by " VRS " replacement
    # But "VRS" at end of template literals like `... VRS`
    content = content.replace('VRS`', 'VCO`')
    
    # "Cannot mint VRS"
    content = content.replace('Cannot mint VRS', 'Cannot mint VCO')
    content = content.replace('VRS is the native token', 'VCO is the native token')
    
    # "MAX_TX_AMOUNT} VRS" in security messages
    content = content.replace('} VRS', '} VCO')
    
    # Remaining standalone VRS in backtick strings or code comments
    # "VRS each" "VRS staked" "VRS total"
    content = content.replace('VRS each', 'VCO each')
    content = content.replace('VRS staked', 'VCO staked')
    content = content.replace('VRS total', 'VCO total')
    
    # "per VRS" (like "1 VRS = 0.5 CARBON")
    content = content.replace('per VRS', 'per VCO')
    content = content.replace('1 VRS', '1 VCO')
    content = content.replace('2 VRS', '2 VCO')
    
    # Check remaining VRS that we might have missed
    remaining = content.count('VRS')
    if remaining > 0:
        # Find context for remaining
        for i, line in enumerate(content.split('\n'), 1):
            if 'VRS' in line:
                # Try to replace remaining patterns
                pass
    
    if content != original:
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        changes = sum(1 for a, b in zip(original, content) if a != b)
        remaining_vrs = content.count('VRS')
        print(f"UPDATED: {fpath} (remaining VRS: {remaining_vrs})")
        total_replacements += 1
    else:
        print(f"NO CHANGES: {fpath}")

print(f"\nTotal files modified: {total_replacements}")
