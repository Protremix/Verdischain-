from bs4 import BeautifulSoup
import re

with open('page_validators.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

print("=== TITLE ===")
print(soup.title.string if soup.title else "No title")

print("\n=== HEADINGS ===")
for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
    print(f"[{h.name}] {h.get_text(strip=True)}")

print("\n=== ALL TEXT BLOCKS ===")
for el in soup.find_all(['p', 'div', 'span', 'li', 'td', 'th', 'a', 'button', 'label']):
    t = el.get_text(strip=True)
    if t and len(t) > 3 and len(el.find_all()) == 0:
        print(f"[{el.name}.{el.get('class')}] {t}")

