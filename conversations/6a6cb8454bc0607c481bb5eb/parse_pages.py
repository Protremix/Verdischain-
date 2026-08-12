import os
import re
from bs4 import BeautifulSoup

base_dir = "./verdiscan_audit/var/www/verdiscan"

pages = [
    ("1. Blog", "blog/index.html"),
    ("2. Developers", "developers/index.html"),
    ("3. Download", "download/index.html"),
    ("4. Contact", "contact/index.html"),
    ("5. Referral", "referral/index.html"),
    ("6. Incentives", "incentives/index.html"),
    ("7. Disclaimer", "legal/disclaimer.html"),
    ("8. Privacy", "legal/privacy.html"),
    ("9. Terms", "legal/terms.html"),
    ("10. 404", "404/index.html"),
    ("11. Token Sale", "token-sale/index.html"),
]

main_page = ("0. Main Index", "../index_main.html")

REQUIRED_FOOTER_KEYWORDS = [
    "Home", "Explorer", "DEX", "Whitepaper", "Wallet", 
    "Sale", "Tokenomics", "Faucet", "Validators", 
    "Eco", "Docs", "Governance", "GitHub"
]

def analyze_page(name, rel_path):
    filepath = os.path.join(base_dir, rel_path)
    if not os.path.exists(filepath):
        print(f"File NOT found: {filepath}")
        return
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')
    
    print(f"\n==========================================")
    print(f"PAGE: {name} ({rel_path})")
    print(f"File size: {len(html)} bytes")
    print(f"==========================================")
    
    # 1. LOGO
    print("\n--- 1. LOGO ---")
    imgs = soup.find_all('img')
    logo_imgs = [img for img in imgs if 'logo' in img.get('src', '').lower() or 'logo' in img.get('class', '') or 'logo' in img.get('alt', '').lower() or (img.parent and img.parent.name == 'a' and ('nav' in img.parent.get('class', []) or 'brand' in img.parent.get('class', []) or 'logo' in img.parent.get('class', [])))]
    if not logo_imgs:
        # search any img inside nav or header
        nav_or_header = soup.find('nav') or soup.find('header')
        if nav_or_header:
            logo_imgs = nav_or_header.find_all('img')
            
    print(f"Logo images found: {len(logo_imgs)}")
    for img in logo_imgs:
        print(f"  src='{img.get('src')}' alt='{img.get('alt')}' class='{img.get('class')}'")
    
    # Also grep logo strings in raw HTML
    logo_matches = re.findall(r'src=["\'][^"\']*logo[^"\']*["\']', html, re.IGNORECASE)
    print(f"  Raw HTML logo src regex matches: {logo_matches}")

    # 2. FOOTER
    print("\n--- 2. FOOTER ---")
    footer = soup.find('footer')
    if footer:
        print("  Footer element EXISTS.")
        footer_links = footer.find_all('a')
        link_data = []
        for a in footer_links:
            text = a.get_text(strip=True)
            href = a.get('href', '')
            link_data.append((text, href))
        print(f"  Total links in footer: {len(link_data)}")
        print("  Links found in footer:")
        for text, href in link_data:
            print(f"    - '{text}': {href}")
            
        # Check required keywords
        footer_text = footer.get_text()
        missing_kw = []
        for kw in REQUIRED_FOOTER_KEYWORDS:
            # Check either link text or full footer text
            found = any(kw.lower() in t.lower() for t, h in link_data) or (kw.lower() in footer_text.lower())
            if not found:
                missing_kw.append(kw)
        if missing_kw:
            print(f"  MISSING required footer keywords/links: {missing_kw}")
        else:
            print("  ALL required footer keywords/links present!")
    else:
        print("  Footer element NOT FOUND!")

    # 3. NAVIGATION
    print("\n--- 3. NAVIGATION ---")
    nav = soup.find('nav') or soup.find('header')
    if nav:
        print("  Nav/Header element EXISTS.")
        nav_links = nav.find_all('a')
        print(f"  Nav links count: {len(nav_links)}")
        for a in nav_links:
            print(f"    - '{a.get_text(strip=True)}': {a.get('href')}")
    else:
        print("  Nav/Header element NOT FOUND!")

    # 4. TEXT & DATA CHECKS
    print("\n--- 4. TEXT & DATA CHECKS ---")
    # Ticker checks
    vrdx_matches = len(re.findall(r'\bVRDX\b', html))
    verdis_ticker = re.findall(r'(\d+\s*VERDIS|\$VERDIS|VERDIS\s*token|ticker:?\s*VERDIS)', html, re.IGNORECASE)
    print(f"  'VRDX' mentions: {vrdx_matches}")
    if verdis_ticker:
        print(f"  ISSUE? 'VERDIS' used as ticker/token: {verdis_ticker}")

    # Supply checks
    supply_matches = re.findall(r'(\b\d+[\d,.]*\s*(?:billion|B|M|million|trillion|VRDX|VERDIS)\b|\b100B\b|\b100,000,000,000\b)', html, re.IGNORECASE)
    print(f"  Supply mentions: {supply_matches[:10]}")

    # Decimals checks
    decimal_matches = re.findall(r'(\bdecimals?:?\s*\d+\b|\b9\s*decimals?\b|\b18\s*decimals?\b)', html, re.IGNORECASE)
    print(f"  Decimals mentions: {decimal_matches}")

    # Pricing mentions
    price_matches = re.findall(r'(\$\d+\.?\d*|\d+\.?\d*\s*USDT|\bprice:?\s*\$?\d+[\d.]*)', html, re.IGNORECASE)
    print(f"  Price mentions: {price_matches[:10]}")

    # Hardcoded/Lorem ipsum
    lorem = re.findall(r'lorem\s+ipsum', html, re.IGNORECASE)
    if lorem:
        print(f"  ISSUE: Lorem ipsum found ({len(lorem)} times)")

    # 5. DESIGN & CSS
    print("\n--- 5. DESIGN & CSS ---")
    has_bg1 = "--bg-1" in html
    has_bg2 = "--bg-2" in html
    has_accent = "--accent" in html
    print(f"  CSS Vars: --bg-1: {has_bg1}, --bg-2: {has_bg2}, --accent: {has_accent}")
    
    # Check styles / class names / CSS links
    css_links = [link.get('href') for link in soup.find_all('link', rel=re.compile('stylesheet', re.I))]
    print(f"  Stylesheet links: {css_links}")
    
    style_tags = soup.find_all('style')
    print(f"  Inline style tags count: {len(style_tags)}")

    # 6. PURPOSE & CONTENT SUMMARY
    print("\n--- 6. PURPOSE & CONTENT SUMMARY ---")
    body_text = soup.body.get_text(strip=True) if soup.body else ""
    print(f"  Body text length: {len(body_text)} chars")
    print(f"  First 200 chars of body text: {body_text[:200]}...")

for name, rel in [main_page] + pages:
    analyze_page(name, rel)
