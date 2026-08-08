from bs4 import BeautifulSoup
import re

with open("/tmp/sale_page.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

print("=== 1. HERO SECTION CHECK ===")
hero = soup.find('section', class_='hero')
if hero:
    print("Hero Text:\n", hero.get_text(separator=' | ', strip=True))

print("\n=== 2. SALE PHASES GRID CHECK ===")
phases = soup.find('div', class_='phases-grid')
if phases:
    cards = phases.find_all('div', class_='phase-card')
    for idx, card in enumerate(cards):
        print(f"--- Phase Card {idx+1} ---")
        print(card.get_text(separator=' | ', strip=True))

print("\n=== 3. BUY SECTION CHECK ===")
buy = soup.find('div', id='buySection')
if buy:
    print(buy.get_text(separator=' | ', strip=True))

print("\n=== 4. TOKEN ALLOCATION CHECK ===")
alloc = soup.find('div', class_='alloc-section')
if alloc:
    print(alloc.get_text(separator=' | ', strip=True))

print("\n=== 5. VESTING SCHEDULE TABLE CHECK ===")
vesting = soup.find('div', class_='vesting-section')
if vesting:
    table = vesting.find('table')
    if table:
        for row in table.find_all('tr'):
            cells = [c.get_text(strip=True) for c in row.find_all(['th', 'td'])]
            print("TR:", " | ".join(cells))

print("\n=== 6. WHITELIST SECTION CHECK ===")
wl = soup.find('div', class_='whitelist-section')
if wl:
    print(wl.get_text(separator=' | ', strip=True))

print("\n=== 7. FAQ SECTION CHECK ===")
faq = soup.find('div', class_='faq-section')
if faq:
    for item in faq.find_all('div', class_='faq-item'):
        print("FAQ ITEM:", item.get_text(separator=' | ', strip=True))

