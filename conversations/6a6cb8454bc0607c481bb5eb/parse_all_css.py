import re
from bs4 import BeautifulSoup

with open('page.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

css = "".join([s.get_text() for s in soup.find_all('style')])

media_blocks = re.findall(r'(@media[^{]+\{(?:[^{}]+|\{[^{}]*\})+\})', css)
print(f"Found {len(media_blocks)} media queries:")
for mb in media_blocks:
    print("="*60)
    print(mb)

