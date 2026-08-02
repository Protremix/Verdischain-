import re

with open('/opt/verdis/app/dist/web/dashboard.html', 'r') as f:
    content = f.read()

# 1. Remove the sale tab HTML panel content
# Find the sale tab panel - it contains "Verdis Token Sale (IDO)" and all the sale elements
# Look for the tab-panel that contains the sale content
lines = content.split('\n')
sale_start = None
sale_end = None

for i, line in enumerate(lines):
    if 'Verdis Token Sale (IDO)' in line and sale_start is None:
        # Find the enclosing tab-panel div
        for j in range(i, max(0, i-20), -1):
            if 'tab-panel' in lines[j] or 'tab-content' in lines[j]:
                sale_start = j
                break
        if sale_start is None:
            sale_start = i - 5  # approximate
    
    if sale_start is not None and sale_end is None:
        # Find the end of this tab panel - look for the next tab-panel or closing comment
        if i > sale_start + 5:
            if 'tab-panel' in line or 'tab-content' in line or '<!-- end' in line.lower():
                if 'sale' not in line and 'tab-panel' in line:
                    sale_end = i
                    break

# Also look for the tokenomics disclosure box that's part of the sale section
tok_start = None
for i, line in enumerate(lines):
    if 'Before You Buy' in line and 'Tokenomics' in line:
        for j in range(i, max(0, i-10), -1):
            if 'class="feature-card"' in lines[j] or 'class="info-box"' in lines[j] or 'style="margin' in lines[j]:
                tok_start = j
                break
        if tok_start is None:
            tok_start = i - 3
        break

print(f"Sale HTML panel: lines {sale_start}-{sale_end}")
print(f"Tokenomics box: starts at line {tok_start}")

# Remove sections by line numbers (work backwards to preserve indices)
sections_to_remove = []
if sale_start is not None and sale_end is not None:
    sections_to_remove.append((sale_start, sale_end))
if tok_start is not None:
    # Find where tokenomics box ends - look for the closing div
    tok_end = None
    for i in range(tok_start, min(len(lines), tok_start + 100)):
        if '</div>' in lines[i] and i > tok_start + 5:
            # Count div balance
            pass
    # Simpler: look for the checkbox line and go a few lines after
    for i in range(tok_start, min(len(lines), tok_start + 100)):
        if 'checkbox' in lines[i] and 'reviewed the tokenomics' in lines[i]:
            tok_end = i + 3  # a few lines after
            break
    if tok_end:
        sections_to_remove.append((tok_start, tok_end))
        print(f"Tokenomics box: lines {tok_start}-{tok_end}")

# Sort by start line descending and remove
sections_to_remove.sort(key=lambda x: x[0], reverse=True)
for start, end in sections_to_remove:
    del lines[start:end+1]
    print(f"Removed lines {start}-{end}")

content = '\n'.join(lines)

# 2. Remove JS: loadSale function
content = re.sub(
    r'async function loadSale\(\)\{.*?(?=\nasync function |\nfunction |\nconst [A-Z]|\nlet [a-z]|\nwindow\.|\nsetTimeout)',
    '',
    content,
    flags=re.DOTALL
)

# 3. Remove JS: updateSaleUI function
content = re.sub(
    r'function updateSaleUI\(\)\{.*?(?=\nasync function |\nfunction |\nconst [A-Z]|\nlet [a-z]|\nwindow\.|\n//)',
    '',
    content,
    flags=re.DOTALL
)

# 4. Remove JS: buyTokens function (if it exists)
content = re.sub(
    r'(async )?function buyTokens\([^)]*\)\{.*?(?=\nasync function |\nfunction |\nconst [A-Z]|\nlet [a-z]|\nwindow\.|\n//)',
    '',
    content,
    flags=re.DOTALL
)

# 5. Remove any remaining saleStats references
content = re.sub(r'if\(r2 && !r2\.error && !saleStats\.sold\).*?updateSaleUI\(\);\s*}', '', content, flags=re.DOTALL)
content = re.sub(r'typeof saleStats !== \'undefined\' && saleStats\.[a-zA-Z]+ && saleStats\.[a-zA-Z]+\[[a-zA-Z]+\]', '1000', content)
content = re.sub(r'typeof saleStats !== \'undefined\' && saleStats\.bonusPct', '10', content)
content = re.sub(r'saleStats\.livePrices&&saleStats\.livePrices\[[a-zA-Z]+\]', '1', content)
content = re.sub(r'saleStats\.[a-zA-Z]+', '0', content)

# 6. Remove the sale feature card from the overview grid
content = re.sub(
    r'<div class="feature-card" onclick="switchTab\(\'sale\'\)">.*?</div>\s*</div>\s*</div>',
    '',
    content,
    flags=re.DOTALL
)

# Verify
remaining = content.count('loadSale')
print(f"\nRemaining loadSale: {remaining}")
remaining_stats = content.count('saleStats')
print(f"Remaining saleStats: {remaining_stats}")
remaining_nav = content.count('data-tab="sale"')
print(f"Remaining data-tab=sale: {remaining_nav}")
remaining_ido = content.count('idoCurrentStage')
print(f"Remaining idoCurrentStage: {remaining_ido}")

with open('/opt/verdis/app/dist/web/dashboard.html', 'w') as f:
    f.write(content)

print(f"\nFinal size: {len(content)} chars")
print("Done!")
