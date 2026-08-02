import re

with open('/opt/verdis/app/dist/web/dashboard.html', 'r') as f:
    content = f.read()

# 1. Remove the Token Sale nav tab
content = content.replace(
    '<div class="nav-tab" data-tab="sale">\U0001f680 Token Sale</div>\n',
    ''
)

# 2. Remove the feature card that links to sale
content = re.sub(
    r'<div class="feature-card" onclick="switchTab\(\'sale\'\)">.*?</div>\s*</div>\s*</div>',
    '',
    content,
    flags=re.DOTALL
)

# 3. Remove the sale tab content div (the entire tab-panel for sale)
# Find the sale tab panel and remove it
sale_panel_pattern = r'<div class="tab-panel"[^>]*data-tab="sale"[^>]*>.*?</div>\s*<!--\s*end sale\s*-->'
content = re.sub(sale_panel_pattern, '', content, flags=re.DOTALL)

# Also try a more generic approach - find the sale section between markers
# Look for the sale tab content
sale_section_match = re.search(
    r'(<!--\s*SALE TAB\s*-->|<div[^>]*id="tab-sale"[^>]*>).*?(<!--\s*end.*?sale|<!--\s*BLOCKS)',
    content,
    flags=re.DOTALL
)

# 4. Remove the case 'sale':loadSale();break; from loadTabData
content = re.sub(r"case'sale':loadSale\(\);break;", '', content)
content = re.sub(r"case\s*'sale'\s*:\s*loadSale\s*\(\s*\)\s*;?\s*break\s*;", '', content)

# 5. Remove loadSale function and all related JS
# Find and remove the loadSale function
loadsale_match = re.search(r'(let saleStats=.*?(?=\nconst |\nlet |\nvar |\nasync function [^l])|async function loadSale\(\)\{.*?(?=\nasync function |\nfunction |\nconst |\nlet |\nvar ))', content, flags=re.DOTALL)

# More targeted: remove from "let saleStats" to the end of the sale-related code block
sale_js_start = content.find('let saleStats=')
if sale_js_start < 0:
    sale_js_start = content.find('let saleStats =')
if sale_js_start < 0:
    sale_js_start = content.find('saleStats={')

if sale_js_start >= 0:
    # Find where the sale JS ends - look for the next function or const that's not sale-related
    # The sale JS block includes: saleStats, saleRates, loadSale, updateSaleUI, buyTokens
    sale_js_end = content.find('\nasync function ', sale_js_start + 100)
    if sale_js_end < 0:
        sale_js_end = content.find('\nfunction ', sale_js_start + 100)
    if sale_js_end < 0:
        sale_js_end = content.find('\nconst ', sale_js_start + 100)
    
    if sale_js_end >= 0:
        # Check if the next function is NOT sale-related
        next_block = content[sale_js_end:sale_js_end + 100]
        print(f"Sale JS starts at {sale_js_start}, ends at {sale_js_end}")
        print(f"Next block: {next_block[:80]}")
        
        # Remove the sale JS block
        content = content[:sale_js_start] + '\n' + content[sale_js_end:]
        print("Removed sale JS block")
    else:
        print(f"Could not find end of sale JS (started at {sale_js_start})")
else:
    print("Could not find saleStats declaration")

# 6. Remove the auto-load call for loadSale
content = re.sub(
    r"setTimeout\(function\(\)\{if\(typeof loadSale[^;]*;[^;]*;\s*\},\s*\d+\);",
    '',
    content
)
content = re.sub(
    r'setTimeout\(function\(\)\{ ?if\(typeof loadSale === "function"\) ?\{ ?loadSale\(\);[^}]*\} ?\}, ?\d+\);',
    '',
    content
)

# 7. Remove the direct IDO loader script I added earlier
direct_ido_pattern = r'<script>\s*// Direct IDO loader.*?</script>'
content = re.sub(direct_ido_pattern, '', content, flags=re.DOTALL)

# 8. Remove any remaining references to loadSale, saleStats, saleRates, idoCurrentStage in JS
# (but keep HTML elements that might be referenced elsewhere)
# Actually, remove the HTML elements too since the tab is gone
# Remove the tokenomics disclosure box if it's in the sale tab

# 9. Remove "if(a==='sale')loadSale();" 
content = re.sub(r"if\(a==='sale'\)loadSale\(\);", '', content)

# 10. Remove "loadSale(); // Refresh sale stats"
content = re.sub(r"loadSale\(\); ?// Refresh sale stats", '', content)

# Verify no more loadSale references remain
remaining = content.count('loadSale')
print(f"Remaining loadSale references: {remaining}")

remaining_stats = content.count('saleStats')
print(f"Remaining saleStats references: {remaining_stats}")

# Verify the sale nav tab is gone
remaining_nav = content.count('data-tab="sale"')
print(f"Remaining data-tab=sale: {remaining_nav}")

with open('/opt/verdis/app/dist/web/dashboard.html', 'w') as f:
    f.write(content)

print(f"Dashboard file size: {len(content)} chars")
print("Done!")
