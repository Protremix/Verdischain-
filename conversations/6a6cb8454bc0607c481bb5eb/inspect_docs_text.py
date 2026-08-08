from bs4 import BeautifulSoup
import json

with open("dumps/docs.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

print("=== DOCS HEADINGS & STRUCTURE ===")
for header in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5']):
    print(f"{header.name}: {header.get_text(strip=True)} (id='{header.get('id')}')")

print("\n=== CODE BLOCKS & PRE ===")
for pre in soup.find_all('pre'):
    print("--- PRE BLOCK ---")
    print(pre.get_text())

