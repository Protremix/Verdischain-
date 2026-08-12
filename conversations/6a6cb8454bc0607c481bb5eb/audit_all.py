import os
import re
from bs4 import BeautifulSoup

base_dir = "./verdiscan_audit/var/www/verdiscan"

pages = [
    ("Blog", "blog/index.html"),
    ("Developers", "developers/index.html"),
    ("Download", "download/index.html"),
    ("Contact", "contact/index.html"),
    ("Referral", "referral/index.html"),
    ("Incentives", "incentives/index.html"),
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
    # Look for img src
    imgs = soup.find_all('img')
    logo_srcs = []
    for img in imgs:
        src = img.get('src', '')
        alt = img.get('alt', '')
        cls = img.get('class', [])
        # check if it's the brand logo
        if 'logo' in src.lower() or 'logo' in alt.lower() or any('logo' in c.lower() for c in cls) or (img.parent and img.parent.name == 'a'):
            logo_srcs.append(src)
    
    # Also regex for img tag in header/nav or anywhere
    raw_imgs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>', html, re.IGNORECASE)
    
    print(f"Logo images found: {logo_srcs}")
    print(f"All img src tags on page: {raw_imgs}")

    # 2. FOOTER
    footer = soup.find('footer')
    if not footer:
        # check if footer class or id
        footer = soup.find(class_=re.compile('footer', re.I)) or soup.find(id=re.compile('footer', re.I))

    if footer:
        links = footer.find_all('a')
        footer_link_dict = {}
        for a in links:
            t = a.get_text(strip=True)
            h = a.get('href', '')
            if t or h:
                footer_link_dict[t] = h
        print(f"Footer: EXISTS. Links count: {len(links)}")
        print(f"Footer links: {footer_link_dict}")
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
    # Check Ticker, Supply, Decimals, Pricing, Fake/Hardcoded data, Broken links
    vrdx_cnt = len(re.findall(r'\bVRDX\b', html))
    verdis_as_ticker = re.findall(r'(\d+\s*VERDIS|\$VERDIS\b|VERDIS\s+token|symbol:?\s*["\']?VERDIS["\']?)', html, re.IGNORECASE)
    supply_found = re.findall(r'(\b\d+[\d,.]*\s*(?:billion|B|M|million|trillion|VRDX|VERDIS)\b|\b100B\b|\b100,000,000,000\b)', html, re.IGNORECASE)
    decimals_found = re.findall(r'(\bdecimals?:?\s*\d+\b|\b9\s*decimals?\b|\b18\s*decimals?\b)', html, re.IGNORECASE)
    fake_lorem = re.findall(r'lorem\s+ipsum', html, re.IGNORECASE)
    
    # Broken links
    all_links = [a.get('href', '') for a in soup.find_all('a')]
    hash_links = [h for h in all_links if h == '#' or h == 'javascript:void(0)']
    
    print(f"Text checks:")
    print(f"  - VRDX mentions: {vrdx_cnt}")
    print(f"  - Wrong Ticker (VERDIS): {verdis_as_ticker}")
    print(f"  - Supply mentions: {supply_found[:10]}")
    print(f"  - Decimals mentions: {decimals_found}")
    print(f"  - Lorem ipsum: {len(fake_lorem)}")
    print(f"  - Empty/hash links count: {len(hash_links)} out of {len(all_links)}")

    # 5. DESIGN
    has_bg1 = "--bg-1" in html
    has_bg2 = "--bg-2" in html
    has_accent = "--accent" in html
    style_tags = soup.find_all('style')
    link_css = [l.get('href') for l in soup.find_all('link', rel=re.compile('stylesheet', re.I))]
    print(f"Design checks:")
    print(f"  - CSS vars: --bg-1={has_bg1}, --bg-2={has_bg2}, --accent={has_accent}")
    print(f"  - CSS files: {link_css}")

    # 6. PURPOSE
    body_text = soup.body.get_text(separator=' ', strip=True) if soup.body else ""
    print(f"Purpose checks:")
    print(f"  - Body text length: {len(body_text)} chars")
    print(f"  - Title: {soup.title.get_text() if soup.title else 'No title'}")

