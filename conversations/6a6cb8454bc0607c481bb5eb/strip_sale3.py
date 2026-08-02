with open('/opt/verdis/app/dist/web/dashboard.html', 'r') as f:
    lines = f.readlines()

# Find and remove the sale HTML section (lines around 1230-1270)
# Also remove the tokenomics disclosure box
remove_ranges = []

i = 0
while i < len(lines):
    line = lines[i]
    
    # Find the tokenomics disclosure box
    if 'Before You Buy' in line and 'Tokenomics' in line:
        # Find the enclosing div - go back to find the opening
        start = i
        for j in range(i, max(0, i-15), -1):
            if 'class="info-box' in lines[j] or 'style="margin' in lines[j] or '<div class="card' in lines[j]:
                start = j
                break
        # Find the end - the checkbox line + closing divs
        end = i
        for j in range(i, min(len(lines), i+50)):
            if 'reviewed the tokenomics' in lines[j]:
                end = j + 3
                break
        remove_ranges.append((start, end, 'tokenomics box'))
    
    # Find the sale section with IDO stages, sale prices, etc.
    if 'idoStages' in line and 'ido-stages-container' in line:
        start = i
        # Find the end - look for the buy form or the next section
        end = i
        for j in range(i, min(len(lines), i+80)):
            if '</div>' in lines[j] and j > i + 30:
                # Check if this is the closing of the sale section
                # Look for the next major section
                pass
            if 'class="explore-header"' in lines[j] and j > i + 3:
                end = j - 1
                break
            if '<!--' in lines[j] and ('end' in lines[j].lower() or 'block' in lines[j].lower()) and j > i + 10:
                end = j
                break
        remove_ranges.append((start, end, 'sale stages section'))
    
    # Find the "Verdis Token Sale (IDO)" heading and sale content
    if 'Verdis Token Sale (IDO)' in line:
        start = i - 2  # include the explore-header
        end = i
        for j in range(i, min(len(lines), i+100)):
            if '</div>' in lines[j] and j > i + 40:
                # Check if next line is a new section
                if j + 1 < len(lines) and ('class="explore-header"' in lines[j+1] or '<!--' in lines[j+1]):
                    end = j
                    break
            if '<!--' in lines[j] and j > i + 10:
                end = j
                break
        remove_ranges.append((start, end, 'IDO heading + content'))
    
    i += 1

# Also find the price tiles section (ETH/BNB/USD rates) and buy form
for i, line in enumerate(lines):
    if 'rateETH' in line or 'price-tile' in line:
        # Find the container
        start = i
        for j in range(i, max(0, i-5), -1):
            if 'class="price-tile' in lines[j] or 'display:flex' in lines[j] or 'price-grid' in lines[j]:
                start = j
                break
        end = i
        for j in range(i, min(len(lines), i+20)):
            if 'price-tile' not in lines[j] and '</div>' in lines[j] and j > i + 3:
                end = j
                break
        remove_ranges.append((start, end, 'price tiles'))
        break

# Find the buy form / purchase section
for i, line in enumerate(lines):
    if 'buyTokens' in line or 'purchaseAmount' in line or 'buyAmount' in line:
        start = i
        for j in range(i, max(0, i-10), -1):
            if '<div' in lines[j] and 'class=' in lines[j]:
                start = j
                break
        end = i
        for j in range(i, min(len(lines), i+30)):
            if '</div>' in lines[j] and j > i + 5:
                end = j
                break
        remove_ranges.append((start, end, 'buy form'))

# Sort ranges by start descending and remove
remove_ranges.sort(key=lambda x: x[0], reverse=True)

# Merge overlapping ranges
merged = []
for start, end, label in remove_ranges:
    if merged and start <= merged[-1][1]:
        merged[-1] = (min(merged[-1][0], start), max(merged[-1][1], end), merged[-1][2] + '+' + label)
    else:
        merged.append((start, end, label))

for start, end, label in merged:
    print(f"Removing lines {start+1}-{end+1}: {label}")
    del lines[start:end+1]

content = ''.join(lines)

# Clean up any remaining sale-related element references in JS
import re
# Remove any remaining references to sale elements that no longer exist
content = re.sub(r"document\.getElementById\(['\"](?:salePrice|saleRaised|saleSold|saleProgress|saleProgressBar|saleRemaining|idoCurrentStage|idoStagePrice|idoStageBonus|idoMinContrib|idoMaxWallet|idoStagesBar|rateETH|rateBNB|rateUSD|priceETH|priceBNB|priceUSD)['\"]\)[^;]*;", '/* removed sale element */', content)

# Also remove the "Seed Sale Price" and "Raised" statCards from the overview
content = content.replace("statCard('Seed Sale Price',s.presalePrice||'$0.0005')+", '')
content = content.replace("statCard('Raised','$'+(s.presaleRaised||0).toLocaleString());", '')

# Verify
for term in ['loadSale', 'saleStats', 'idoCurrentStage', 'salePrice', 'saleRaised', 'saleSold', 'rateETH', 'rateBNB', 'rateUSD', 'data-tab="sale"']:
    count = content.count(term)
    if count > 0:
        print(f"WARNING: {term} still appears {count} times")

with open('/opt/verdis/app/dist/web/dashboard.html', 'w') as f:
    f.write(content)

print(f"\nFinal size: {len(content)} chars")
print("Done!")
