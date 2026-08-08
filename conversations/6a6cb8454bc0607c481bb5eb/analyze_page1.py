from bs4 import BeautifulSoup
import json
import re

with open("page1_api.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

print("=== PAGE 1 META & HEAD ===")
print("Title:", soup.title.string if soup.title else "NO TITLE")
print("Meta Desc:", soup.find("meta", attrs={"name": "description"})["content"] if soup.find("meta", attrs={"name": "description"}) else "NONE")

# Find all headings
print("\n=== HEADINGS ===")
for h in soup.find_all(['h1', 'h2', 'h3', 'h4']):
    print(f"{h.name} (id={h.get('id')}): {h.get_text(strip=True)}")

# Find all endpoint code blocks / examples / URLs
print("\n=== ENDPOINT / CODE BLOCKS ===")
codes = soup.find_all(['pre', 'code'])
for c in codes:
    text = c.get_text()
    if 'http' in text or 'GET' in text or 'POST' in text or '{' in text:
        print("--- CODE BLOCK ---")
        print(text[:300])

