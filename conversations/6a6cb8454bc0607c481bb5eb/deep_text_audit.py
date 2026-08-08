from bs4 import BeautifulSoup
import re

with open('page.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

print("--- ALL TEXT NODES WITH NUMBERS OR PERCENTAGES ---")
for text in soup.find_all(text=True):
    parent = text.parent.name
    if parent in ['script', 'style']:
        continue
    txt = text.strip()
    if txt and any(c.isdigit() for c in txt):
        print(f"[{parent}] {txt}")

