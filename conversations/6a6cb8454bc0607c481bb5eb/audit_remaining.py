import os
import re
from bs4 import BeautifulSoup

base_dir = "./verdiscan_audit/var/www/verdiscan"

pages = [
    ("Disclaimer", "legal/disclaimer.html"),
    ("Privacy", "legal/privacy.html"),
    ("Terms", "legal/terms.html"),
    ("404", "404/index.html"),
    ("Token Sale", "token-sale/index.html"),
]

for title, rel_path in pages:
    filepath = os.path.join(base_dir, rel_path)
    if not os.path.exists(filepath):
        print(f"=== {title} ({rel_path}): NOT FOUND ===")
        continue

    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')
    
    print(f"\n==================================================")
    print(f"PAGE: {title} ({rel_path})")
    print(f"==================================================")

    # 1. LOGO
    imgs = soup.find_all('img')
    logo_srcs = [img.get('src', '') for img in imgs]
    print(f"Logo images / All img src: {logo_srcs}")

    # 2. FOOTER
    footer = soup.find('footer') or soup.find(class_=re.compile('footer', re.I))
    if footer:
        links = footer.find_all('a')
        footer_links = {a.get_text(strip=True): a.get('href', '') for a in links}
        print(f"Footer: EXISTS. Links count: {len(links)}")
        print(f"Footer links: {footer_links}")
    else:
        print("Footer: NOT FOUND")

    # 3. NAV
    nav = soup.find('nav') or soup.find('header') or soup.find(class_=re.compile('nav|header', re.I))
    if nav:
        nav_links = nav.find_all('a')
        nav_dict = {a.get_text(strip=True): a.get('href', '') for a in nav_links}
        print(f"Nav: EXISTS. Links count: {len(nav_links)}")
        print(f"Nav links: {nav_dict}")
    else:
        print("Nav: NOT FOUND")

    # 4. TEXT
    vrdx_cnt = len(re.findall(r'\bVRDX\b', html))
    verdis_as_ticker = re.findall(r'(\d+\s*VERDIS|\$VERDIS\b|VERDIS\s+token|symbol:?\s*["\']?VERDIS["\']?)', html, re.IGNORECASE)
    supply_found = re.findall(r'(\b\d+[\d,.]*\s*(?:billion|B|M|million|trillion|VRDX|VERDIS)\b|\b100B\b|\b100,000,000,000\b)', html, re.IGNORECASE)
    decimals_found = re.findall(r'(\bdecimals?:?\s*\d+\b|\b9\s*decimals?\b|\b18\s*decimals?\b)', html, re.IGNORECASE)
    
    print(f"Text checks:")
    print(f"  - VRDX mentions: {vrdx_cnt}")
    print(f"  - Wrong Ticker (VERDIS): {verdis_as_ticker}")
    print(f"  - Supply mentions: {supply_found}")
    print(f"  - Decimals mentions: {decimals_found}")

    # 5. DESIGN
    has_bg1 = "--bg-1" in html
    has_bg2 = "--bg-2" in html
    has_accent = "--accent" in html
    link_css = [l.get('href') for l in soup.find_all('link', rel=re.compile('stylesheet', re.I))]
    print(f"Design checks:")
    print(f"  - CSS vars: --bg-1={has_bg1}, --bg-2={has_bg2}, --accent={has_accent}")
    print(f"  - CSS files: {link_css}")

    # 6. PURPOSE
    body_text = soup.body.get_text(separator=' ', strip=True) if soup.body else ""
    print(f"Purpose checks:")
    print(f"  - Body text length: {len(body_text)} chars")
    print(f"  - Title: {soup.title.get_text() if soup.title else 'No title'}")

