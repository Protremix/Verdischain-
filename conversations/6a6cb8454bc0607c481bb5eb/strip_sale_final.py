with open('/opt/verdis/app/dist/web/dashboard.html', 'r') as f:
    lines = f.readlines()

# Track what we remove
removals = []

# 1. Remove nav tab: line 1079 (0-indexed: 1078)
for i, line in enumerate(lines):
    if 'data-tab="sale"' in line and 'Token Sale' in line:
        removals.append((i, i, 'nav tab'))
        break

# 2. Remove HTML sale section: from "<!-- TOKEN SALE -->" to just before "<!-- BLOCKS -->"
sale_html_start = None
sale_html_end = None
for i, line in enumerate(lines):
    if '<!-- TOKEN SALE -->' in line:
        sale_html_start = i
    if sale_html_start is not None and '<!-- BLOCKS -->' in line:
        sale_html_end = i
        break
if sale_html_start is not None and sale_html_end is not None:
    removals.append((sale_html_start, sale_html_end - 1, 'sale HTML section'))

# 3. Remove case 'sale':loadSale();break; from loadTabData
for i, line in enumerate(lines):
    if "case'sale':loadSale();break;" in line:
        # Just replace that part, keep the rest of the line
        lines[i] = line.replace("case'sale':loadSale();break;", "")
        print(f"Removed case'sale' from line {i+1}")
        break

# 4. Remove sale JS block: from "// TOKEN SALE" comment to "// MONITORING" comment
sale_js_start = None
sale_js_end = None
for i, line in enumerate(lines):
    if '// TOKEN SALE' in line and 'let saleStats' in lines[i+1] if i+1 < len(lines) else False:
        sale_js_start = i
    if sale_js_start is not None and '// MONITORING' in line:
        sale_js_end = i
        break
if sale_js_start is not None and sale_js_end is not None:
    removals.append((sale_js_start, sale_js_end - 1, 'sale JS block'))

# 5. Remove "if(a==='sale')loadSale();" 
for i, line in enumerate(lines):
    if "if(a==='sale')loadSale();" in line:
        lines[i] = line.replace("if(a==='sale')loadSale();", "")
        print(f"Removed if(a==='sale')loadSale() from line {i+1}")
        break

# 6. Update AI assistant answer about token sale location (line ~3971)
for i, line in enumerate(lines):
    if 'The token sale is live on the Dashboard' in line:
        lines[i] = line.replace(
            'The token sale is live on the Dashboard → Token Sale tab',
            'The token sale is live at verdischain.com/token-sale'
        )
        print(f"Updated AI answer at line {i+1}")
        break

# Sort removals by start descending and apply
removals.sort(key=lambda x: x[0], reverse=True)
for start, end, label in removals:
    print(f"Removing lines {start+1}-{end+1}: {label} ({end-start+1} lines)")
    del lines[start:end+1]

content = ''.join(lines)

# Verify
for term in ['loadSale', 'saleStats', 'data-tab="sale"', 'idoCurrentStage', 'salePrice', 'rateETH']:
    count = content.count(term)
    if count > 0:
        print(f"WARNING: '{term}' still appears {count} times")

with open('/opt/verdis/app/dist/web/dashboard.html', 'w') as f:
    f.write(content)

print(f"\nFinal size: {len(content)} chars (was 250494)")
print("Done!")
