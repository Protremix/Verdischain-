from bs4 import BeautifulSoup
import re

with open('page_eco.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

print("=== TITLE & META ===")
print("Title:", soup.title.string if soup.title else "No title")

print("\n=== HEADER / NAV LINKS ===")
nav = soup.find('nav')
if nav:
    for a in nav.find_all('a'):
        print(f"Nav Link: text='{a.get_text(strip=True)}', href='{a.get('href')}'")

print("\n=== HERO SECTION ===")
hero = soup.find('section') or soup.find('header') or soup.find(class_=re.compile('hero', re.I))
if hero:
    print(hero.get_text(separator=' | ', strip=True))

print("\n=== ALL HEADINGS ===")
for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
    print(f"[{h.name}] {h.get_text(strip=True)}")

print("\n=== ALL PARAGRAPHS & SPANS WITH TEXT ===")
for p in soup.find_all(['p', 'span', 'div', 'td', 'th']):
    # Only print element if direct text exists or interesting
    text = p.get_text(strip=True)
    if text and len(text) > 5 and len(p.find_all()) == 0:
        print(f"[{p.name}.{p.get('class')}] {text}")

