from bs4 import BeautifulSoup
import re

with open('page.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

# Extract text block by block
blocks = []
for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'th', 'td', 'span', 'div']):
    # get direct text or non-empty child text
    txt = tag.get_text(separator=' ', strip=True)
    if txt and len(txt) > 3:
        blocks.append((tag.name, tag.attrs, txt))

for name, attrs, txt in blocks:
    # Print suspicious text or all text sections for manual inspection
    print(f"<{name} class='{attrs.get('class', '')}'> {txt}")

