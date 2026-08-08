from bs4 import BeautifulSoup
import re

with open("/tmp/sale_page.html", "r", encoding="utf-8") as f:
    html_doc = f.read()

soup = BeautifulSoup(html_doc, 'html.parser')

print("=== TITLE ===")
print(soup.title.string if soup.title else "No Title")

print("\n=== STYLESHEET / CSS SUMMARY ===")
styles = soup.find_all('style')
for i, s in enumerate(styles):
    print(f"--- Style Block {i+1} ---")
    print(s.string[:500] if s.string else "Empty")

print("\n=== BODY HEADINGS & PARAGRAPHS ===")
for elem in soup.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'table', 'ul', 'ol', 'button', 'a']):
    text = elem.get_text(strip=True)
    if text:
        print(f"<{elem.name} class='{elem.get('class')}' id='{elem.get('id')}'> {text[:120]}")

