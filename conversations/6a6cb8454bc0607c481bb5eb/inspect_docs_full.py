from bs4 import BeautifulSoup
import re

html = open("dumps/docs.html", "r", encoding="utf-8").read()
soup = BeautifulSoup(html, "html.parser")

print("=== 1. DOCS BROKEN / FAKE LINKS ===")
for a in soup.find_all('a'):
    href = a.get('href')
    text = a.get_text(strip=True)
    if not href:
        print(f"Empty href link: text='{text}'")
    elif href == '#':
        print(f"Dummy link '#': text='{text}'")

print("\n=== 2. DOCS CODE SNIPPETS & SDK REFERENCES ===")
for code in soup.find_all('code'):
    txt = code.get_text()
    if 'npm' in txt or 'github.com' in txt or 'import' in txt or 'curl' in txt:
        print(f"CODE: {txt.strip()}\n")

print("\n=== 3. DOCS NUMBERS & METRICS IN TEXT ===")
# Check network parameters, tokenomics numbers, opcode counts
for el in soup.find_all(['p', 'div', 'li', 'td']):
    t = el.get_text(strip=True)
    if 'ss58Format' in t or 'totalSupply' in t or 'tokenDecimals' in t or '143' in t or '100' in t:
        print(f"METRIC TEXT: {t}")

