from bs4 import BeautifulSoup
import re

with open('page_source.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

print("==================== ALL SECTIONS AND TEXT ====================")

for idx, section in enumerate(soup.find_all(['header', 'nav', 'section', 'footer'])):
    sec_id = section.get('id', 'no-id')
    sec_class = section.get('class', [])
    print(f"\n--- SECTION {idx}: <{section.name} id='{sec_id}' class='{sec_class}'> ---")
    text = section.get_text(separator=' | ', strip=True)
    print(text[:1000])

