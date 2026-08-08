from bs4 import BeautifulSoup
import json
import re

with open("page2_api_docs.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

print("=== PAGE 2 META & HEAD ===")
print("Title:", soup.title.string if soup.title else "NO TITLE")
print("Meta Desc:", soup.find("meta", attrs={"name": "description"})["content"] if soup.find("meta", attrs={"name": "description"}) else "NONE")

# Headings
print("\n=== HEADINGS ===")
for h in soup.find_all(['h1', 'h2', 'h3', 'h4']):
    print(f"{h.name} (id={h.get('id')}): {h.get_text(strip=True)}")

# Find all scripts
print("\n=== SCRIPTS ===")
scripts = soup.find_all('script')
for idx, s in enumerate(scripts):
    if s.string:
        print(f"--- Script {idx} ({len(s.string)} chars) ---")
        print(s.string[:500])

