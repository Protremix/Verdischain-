from bs4 import BeautifulSoup
import re

with open('page.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

print("--- PAGE TITLE & METAS ---")
print("Title:", soup.title.string if soup.title else None)

print("\n--- ALL TABLES / ALLOCATION TABLES ---")
tables = soup.find_all('table')
print(f"Found {len(tables)} tables")
for i, table in enumerate(tables):
    print(f"\nTable #{i+1}:")
    for row in table.find_all('tr'):
        cols = [td.get_text(strip=True) for td in row.find_all(['th', 'td'])]
        print(cols)

# Check for allocation text outside tables if no table found or in divs
print("\n--- ALLOCATION / TOKENOMICS SECTIONS ---")
token_elements = soup.find_all(text=re.compile(r'Community|Ecosystem|Team|DEX|Treasury|Investors|Allocation|Vesting', re.I))
for elem in token_elements:
    parent = elem.parent
    # Print surrounding text
    print(f"Tag: {parent.name}, Text: {parent.get_text(strip=True)[:150]}")

