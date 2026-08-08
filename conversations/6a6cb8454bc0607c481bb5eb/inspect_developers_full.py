from bs4 import BeautifulSoup
import json
import re

html = open("dumps/developers.html", "r", encoding="utf-8").read()
soup = BeautifulSoup(html, "html.parser")

print("=== DEVELOPERS PAGE ANALYSIS ===")

# Check SDK buttons & links
print("\n--- SDK LINKS ---")
for a in soup.find_all('a'):
    href = a.get('href')
    text = a.get_text(strip=True)
    if 'sdk' in href.lower() or 'github' in href.lower() or 'subxt' in href.lower() or 'py' in href.lower() or 'download' in href.lower():
        print(f"Link Text: '{text}' | href: '{href}'")

print("\n--- CODE BLOCKS & SYNTAX ---")
for code in soup.find_all(['code', 'pre']):
    txt = code.get_text()
    if any(k in txt for k in ['npm', 'cargo', 'pip', 'curl', 'import', 'const', 'fn ']):
        print(f"Code Snippet (first 100 chars): {repr(txt[:100])}")

print("\n--- RPC METHODS TABLE & BUTTONS ---")
rpc_rows = soup.find_all(class_=re.compile(r'rpc|method|table|row', re.I))
print(f"Found {len(rpc_rows)} potential RPC rows.")

