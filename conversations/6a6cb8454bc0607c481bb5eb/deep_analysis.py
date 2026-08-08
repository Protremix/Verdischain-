from bs4 import BeautifulSoup
import json

with open('page.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

print("=================== 1. ALLOCATION TABLE ===================")
# Find allocation table or allocation section
alloc_section = soup.find(id=lambda x: x and 'alloc' in x) or soup.find(class_=lambda x: x and 'alloc' in x)
if not alloc_section:
    # search for section headers with "Token Distribution" or "Allocation"
    for h in soup.find_all(['h2', 'h3', 'h4']):
        if 'alloc' in h.get_text().lower() or 'distribution' in h.get_text().lower() or 'tokenomics' in h.get_text().lower():
            print("HEADER:", h.get_text())
            parent = h.find_parent('section') or h.find_parent('div')
            print(parent.get_text(separator='\n', strip=True))
            print("-" * 50)

print("\n=================== 2. PIE CHART SVG / DATA ===================")
pie_svg = soup.find('svg', class_='pie-svg') or soup.find(lambda tag: tag.name == 'svg' and 'pie' in tag.get('class', []))
if pie_svg:
    print("PIE SVG HTML:")
    print(pie_svg.prettify())
else:
    print("Searching all SVGs for pie-seg or circles:")
    for svg in soup.find_all('svg'):
        if svg.find_all('circle'):
            print(svg.prettify())

# Check pie chart legend / labels
pie_container = soup.find(class_=lambda x: x and 'pie' in x) if soup.find(class_=lambda x: x and 'pie' in x) else None
if pie_container:
    print("PIE CONTAINER TEXT:")
    print(pie_container.get_text(separator='\n', strip=True))

print("\n=================== 3. ROADMAP SECTION ===================")
roadmap_sec = soup.find(id=lambda x: x and 'roadmap' in x)
if not roadmap_sec:
    for h in soup.find_all(['h1', 'h2', 'h3']):
        if 'roadmap' in h.get_text().lower():
            roadmap_sec = h.find_parent('section') or h.find_parent('div')
            break
if roadmap_sec:
    print(roadmap_sec.get_text(separator='\n', strip=True))
else:
    print("Roadmap section not found by ID/Header")

print("\n=================== 4. VESTING CARD ===================")
vesting_sec = soup.find(id=lambda x: x and 'vesting' in x)
if not vesting_sec:
    for h in soup.find_all(['h1', 'h2', 'h3']):
        if 'vesting' in h.get_text().lower():
            vesting_sec = h.find_parent('section') or h.find_parent('div')
            break
if vesting_sec:
    print(vesting_sec.get_text(separator='\n', strip=True))

print("\n=================== 5 & 6. STORY TIMELINE ===================")
story_sec = None
for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'div', 'p']):
    txt = h.get_text().lower()
    if 'story' in txt or 'our journey' in txt or 'timeline' in txt or 'history' in txt:
        p = h.find_parent('section') or h.find_parent('div')
        if p and len(p.get_text()) > 200:
            print(f"FOUND STORY/TIMELINE HEADER ({h.get_text().strip()}):")
            print(p.get_text(separator='\n', strip=True))
            print("="*40)

