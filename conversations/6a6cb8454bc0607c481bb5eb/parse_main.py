import os, re
from bs4 import BeautifulSoup

with open('./verdiscan_audit/index_main.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

print("=== MAIN INDEX PAGE ===")
# Logo
imgs = soup.find_all('img')
print("All img src in main index:", [img.get('src') for img in imgs])

# Header / Nav
nav = soup.find('nav') or soup.find('header')
if nav:
    print("Nav links in main index:")
    for a in nav.find_all('a'):
        print(f"  '{a.get_text(strip=True)}': {a.get('href')}")

# Footer
footer = soup.find('footer')
if footer:
    print("Footer links in main index:")
    for a in footer.find_all('a'):
        print(f"  '{a.get_text(strip=True)}': {a.get('href')}")

# CSS vars
print("CSS vars in main index:")
print("  --bg-1:", "--bg-1" in html)
print("  --bg-2:", "--bg-2" in html)
print("  --accent:", "--accent" in html)

# Ticker, supply, decimals
print("VRDX count:", len(re.findall(r'\bVRDX\b', html)))
print("VERDIS ticker matches:", re.findall(r'(\d+\s*VERDIS|\$VERDIS\b|VERDIS\s+token|symbol:?\s*["\']?VERDIS["\']?)', html, re.IGNORECASE))
print("Supply matches:", re.findall(r'(\b\d+[\d,.]*\s*(?:billion|B|M|million|trillion|VRDX|VERDIS)\b|\b100B\b|\b100,000,000,000\b)', html, re.IGNORECASE))
print("Decimals matches:", re.findall(r'(\bdecimals?:?\s*\d+\b|\b9\s*decimals?\b|\b18\s*decimals?\b)', html, re.IGNORECASE))
