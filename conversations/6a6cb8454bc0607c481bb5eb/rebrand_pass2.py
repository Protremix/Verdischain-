import os, re

base = 'blockchain'

# All web files (dist and src) 
web_files = []
for root_dir in ['dist/web', 'src/web']:
    for f in os.listdir(os.path.join(base, root_dir)):
        if f.endswith('.html'):
            web_files.append(os.path.join(root_dir, f))

# Also core source files
src_files = [
    'src/index.ts',
    'src/api/server.ts', 
    'src/api/jsonrpc.ts',
    'src/core/consensus.ts',
    'src/core/market.ts',
    'src/core/security.ts',
]

all_files = web_files + src_files

total_changed = 0

for fpath in all_files:
    full = os.path.join(base, fpath)
    if not os.path.exists(full):
        continue
    
    with open(full, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Catch ALL remaining VRS patterns
    
    # $VRS → $VCO (dollar-prefixed ticker)
    content = content.replace('$VRS', '$VCO')
    
    # "VRS Balance" header
    content = content.replace('VRS Balance', 'VCO Balance')
    
    # DEX swap estimate keys: 'VRS-CARBON' etc
    content = content.replace("'VRS-", "'VCO-")
    content = content.replace("-VRS'", "-VCO'")
    content = content.replace('"VRS-', '"VCO-')
    content = content.replace('-VRS"', '-VCO"')
    
    # "VRS / " in pair names (with spaces around slash)
    content = content.replace('VRS / ', 'VCO / ')
    content = content.replace('VRS/', 'VCO/')
    
    # "VRS Tokenomics"
    content = content.replace('VRS Tokenomics', 'VCO Tokenomics')
    
    # "VRS Token Price"
    content = content.replace('VRS Token Price', 'VCO Token Price')
    
    # "buy VRS" / "Buy VRS" / "BUY VRS"  
    content = content.replace('buy VRS', 'buy VCO')
    content = content.replace('Buy VRS', 'Buy VCO')
    content = content.replace('BUY VRS', 'BUY VCO')
    content = content.replace('Buy $VRS', 'Buy $VCO')
    
    # "How to buy VRS"
    content = content.replace('How to buy VRS', 'How to buy VCO')
    
    # "50,000,000,000 VRS" in AI text
    content = content.replace('000,000,000 VRS', '000,000,000 VCO')
    content = content.replace('000 VRS\n', '000 VCO\n')
    content = content.replace('1B VRS', '1B VCO')
    
    # "VRS Market Buyback"
    content = content.replace('VRS Market Buyback', 'VCO Market Buyback')
    
    # "VRS (15% Supply)"
    content = content.replace('VRS (15%', 'VCO (15%')
    
    # "Price (VRS / USD)"
    content = content.replace('Price (VRS / USD)', 'Price (VCO / USD)')
    content = content.replace('Price (VRS', 'Price (VCO')
    
    # "VRS · Native Asset"
    content = content.replace('VRS ·', 'VCO ·')
    
    # "VRS (native)"
    content = content.replace('VRS (native)', 'VCO (native)')
    
    # "vrs-carbon" / "vrs-eco" (lowercase IDs)
    content = content.replace('vrs-carbon', 'vco-carbon')
    content = content.replace('vrs-eco', 'vco-eco')
    
    # pair: 'VRS / CARBON' etc in JS objects
    content = content.replace("pair: 'VRS", "pair: 'VCO")
    content = content.replace("pair: 'VRS /", "pair: 'VCO /")
    
    # "pairs = ['VRS / CARBON'"  
    content = content.replace("'VRS /", "'VCO /")
    content = content.replace('"VRS /', '"VCO /')
    
    # "VRS Tokens" / "VRS tokens" / "VRS Token"
    content = content.replace('VRS Tokens', 'VCO Tokens')
    content = content.replace('VRS tokens', 'VCO tokens')
    content = content.replace('VRS Token', 'VCO Token')
    
    # "Allocated $VRS" already handled by $VRS replacement
    
    # "receive $VRS" already handled
    
    # Remaining standalone VRS at end of strings or in text
    content = content.replace('VRS\\n', 'VCO\\n')
    
    # Final catch-all: any remaining "VRS" that's clearly the token ticker
    # Pattern: VRS not part of a larger word, in display context
    # Replace "VRS" when preceded by space/quote/dollar and followed by space/quote/period/comma/closing-tag
    content = re.sub(r'(?<![a-zA-Z])VRS(?![a-zA-Z])', 'VCO', content)
    
    if content != original:
        with open(full, 'w', encoding='utf-8') as f:
            f.write(content)
        remaining = content.count('VRS')
        print(f"UPDATED: {fpath} (remaining VRS: {remaining})")
        total_changed += 1
    else:
        remaining = content.count('VRS')
        if remaining > 0:
            print(f"UNCHANGED but has VRS: {fpath} ({remaining})")

print(f"\nTotal files modified in pass 2: {total_changed}")

# Final verification
print("\n=== FINAL VRS CHECK ===")
for fpath in all_files:
    full = os.path.join(base, fpath)
    if not os.path.exists(full):
        continue
    with open(full, 'r') as f:
        c = f.read()
    count = c.count('VRS')
    if count > 0:
        print(f"STILL HAS VRS: {fpath} ({count} occurrences)")
        for i, line in enumerate(c.split('\n'), 1):
            if 'VRS' in line:
                print(f"  Line {i}: {line[:120]}")
