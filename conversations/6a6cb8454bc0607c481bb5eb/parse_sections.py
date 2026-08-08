import re
from bs4 import BeautifulSoup

with open("whitepaper.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

print("=== PAGE TITLE & METAS ===")
print("Title:", soup.title.string if soup.title else None)
for meta in soup.find_all('meta'):
    if meta.get('name') or meta.get('property'):
        print(meta.get('name') or meta.get('property'), '-->', meta.get('content'))

print("\n=== NAV LINKS ===")
for nav_a in soup.find_all('nav'):
    for a in nav_a.find_all('a'):
        print(f"'{a.text.strip()}' -> href='{a.get('href')}'")

print("\n=== FOOTER LINKS ===")
for footer_a in soup.find_all('footer'):
    for a in footer_a.find_all('a'):
        print(f"'{a.text.strip()}' -> href='{a.get('href')}'")

print("\n=== ALL HEADINGS ===")
for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
    print(f"{h.name.upper()}: {h.text.strip()}")

