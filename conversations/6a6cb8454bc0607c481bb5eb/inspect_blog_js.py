from bs4 import BeautifulSoup
import json
import re

soup = BeautifulSoup(open("dumps/blog.html", "r", encoding="utf-8"), "html.parser")

print("=== BLOG SCRIPTS & MODALS ===")
for s in soup.find_all('script'):
    print("--- SCRIPT BLOCK ---")
    print(s.string)

print("\n=== ALL BLOG ARTICLES CONTENT & DATES ===")
# Extract text of all articles
for card in soup.find_all(['div', 'article'], class_=re.compile(r'featured|card|post', re.I)):
    title = card.find(['h2', 'h3', 'h4'])
    title_text = title.get_text(strip=True) if title else "NO TITLE"
    meta = card.find(class_=re.compile(r'meta|date|author', re.I))
    meta_text = meta.get_text(strip=True) if meta else "NO META"
    desc = card.find('p')
    desc_text = desc.get_text(strip=True) if desc else "NO DESC"
    print(f"TITLE: {title_text}\n  META: {meta_text}\n  DESC: {desc_text}\n")

