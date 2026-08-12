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

REQUIRED_FOOTER_LINKS = [
    ("Home", ["/", "/index.html"]),
    ("Explorer", ["/explorer/", "/explorer"]),
    ("DEX", ["/dex/", "/dex"]),
    ("Whitepaper", ["/whitepaper/", "/whitepaper"]),
    ("Wallet", ["/wallet/", "/wallet"]),
    ("Sale", ["/sale/", "/sale"]),
    ("Tokenomics", ["/tokenomics/", "/tokenomics"]),
    ("Faucet", ["/faucet/", "/faucet"]),
    ("Validators", ["/validators/", "/validators"]),
    ("Eco", ["/eco/", "/eco"]),
    ("Docs", ["/docs/", "/docs"]),
    ("Governance", ["/governance/", "/governance"]),
    ("GitHub", ["github.com", "https://github.com"])
]

def detailed_check(title, rel_path):
    filepath = os.path.join(base_dir, rel_path)
    if not os.path.exists(filepath):
        print(f"=== {title}: FILE NOT FOUND ===")
        return

    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')

    print(f"\n==================================================================")
    print(f"AUDIT REPORT FOR: {title} ({rel_path})")
    print(f"==================================================================")

    # --- LOGO ---
    imgs = soup.find_all('img')
    img_srcs = [img.get('src', '') for img in imgs]
    print(f"1. LOGO ANALYSIS:")
    print(f"   - Total img tags: {len(imgs)}")
    print(f"   - All img srcs: {img_srcs}")
    logo_file = None
    for src in img_srcs:
        if 'verdis' in src.lower() or 'logo' in src.lower():
            logo_file = src
            break
    print(f"   - Detected Logo File: {logo_file if logo_file else 'NONE'}")
    if logo_file == "/assets/verdis-logo-black.png":
        print(f"   - Logo Check: OK (verdis-logo-black.png used)")
    else:
        print(f"   - Logo Check: ISSUE (Expected '/assets/verdis-logo-black.png', found '{logo_file}')")

    # --- FOOTER ---
    footer = soup.find('footer') or soup.find(class_=re.compile('footer', re.I))
    print(f"\n2. FOOTER ANALYSIS:")
    if not footer:
        print("   - Footer Check: ISSUE - Footer element NOT FOUND")
    else:
        footer_links = footer.find_all('a')
        footer_hrefs = [a.get('href', '') for a in footer_links]
        footer_texts = [a.get_text(strip=True) for a in footer_links]
        print(f"   - Footer Exists: YES ({len(footer_links)} links found)")
        
        # Check presence of required standard links
        missing_footer = []
        for name, patterns in REQUIRED_FOOTER_LINKS:
            found = False
            for text, href in zip(footer_texts, footer_hrefs):
                if any(p.lower() in href.lower() for p in patterns) or name.lower() in text.lower():
                    found = True
                    break
            if not found:
                missing_footer.append(name)
        
        if missing_footer:
            print(f"   - Footer Check: ISSUE - Missing links to: {missing_footer}")
        else:
            print(f"   - Footer Check: OK - Matches standard footer links")

    # --- NAV ---
    nav = soup.find('nav') or soup.find('header') or soup.find(class_=re.compile('nav|header', re.I))
    print(f"\n3. NAV ANALYSIS:")
    if not nav:
        print("   - Nav Check: ISSUE - Navigation header NOT FOUND")
    else:
        nav_links = nav.find_all('a')
        nav_hrefs = [a.get('href', '') for a in nav_links]
        nav_texts = [a.get_text(strip=True) for a in nav_links]
        print(f"   - Nav Exists: YES ({len(nav_links)} links found)")
        print(f"   - Nav Links: {list(zip(nav_texts, nav_hrefs))}")

    # --- TEXT ---
    print(f"\n4. TEXT & CONTENT ANALYSIS:")
    # Check wrong ticker
    # Look for 'VERDIS' used as ticker name in contexts where VRDX should be used
    verdis_ticker_issues = re.findall(r'(\$\s*VERDIS\b|\bVERDIS\s+token\b|\bVERDIS\s+coins?\b|\bVERDIS\s+ticker\b|symbol:?\s*["\']?VERDIS["\']?)', html, re.IGNORECASE)
    # Check ticker symbol definitions or text like "100 VERDIS"
    verdis_amount = re.findall(r'(\d+[\d,.]*\s*VERDIS\b)', html)
    print(f"   - VRDX count: {len(re.findall(r'VRDX', html))}")
    print(f"   - Ticker issues found: {verdis_ticker_issues}")
    print(f"   - 'VERDIS' used with amounts: {verdis_amount}")

    # Supply check
    supplies = re.findall(r'(\b\d+[\d,.]*\s*(?:billion|B|M|million|trillion|VRDX|VERDIS|tokens?)\b|\b100B\b|\b100,000,000,000\b)', html, re.IGNORECASE)
    print(f"   - Supply mentions: {supplies[:10]}")

    # Decimals check
    decimals = re.findall(r'(\bdecimals?:?\s*\d+|\b9\s*decimals?\b|\b18\s*decimals?\b)', html, re.IGNORECASE)
    print(f"   - Decimals mentions: {decimals}")

    # Hardcoded pricing / fake data / stale prices
    prices = re.findall(r'(\$\d+\.?\d*|\b0\.\d+\s*USDT\b|\b\d+\.?\d*\s*USDT\b)', html)
    print(f"   - Price mentions: {prices[:10]}")

    # Typos / placeholder
    lorem = re.findall(r'lorem\s+ipsum', html, re.IGNORECASE)
    print(f"   - Lorem ipsum count: {len(lorem)}")

    # Broken links
    broken_links = [a.get('href') for a in soup.find_all('a') if not a.get('href') or a.get('href') == '#' or 'javascript:void(0)' in a.get('href', '')]
    print(f"   - Broken/empty links: {len(broken_links)}")

    # --- DESIGN ---
    print(f"\n5. DESIGN ANALYSIS:")
    has_bg1 = "--bg-1" in html
    has_bg2 = "--bg-2" in html
    has_accent = "--accent" in html
    print(f"   - CSS variables check: --bg-1: {has_bg1}, --bg-2: {has_bg2}, --accent: {has_accent}")
    hardcoded_hex = re.findall(r'#(?:[0-9a-fA-F]{3}){1,2}\b', html)
    print(f"   - Hardcoded hex colors count: {len(hardcoded_hex)}")

    # --- PURPOSE ---
    print(f"\n6. PAGE PURPOSE & FUNCTIONALITY:")
    text_len = len(soup.get_text(strip=True))
    print(f"   - Text length: {text_len} chars")
    print(f"   - Form elements: {len(soup.find_all(['form', 'input', 'button', 'textarea']))}")
    print(f"   - JS script tags: {len(soup.find_all('script'))}")

for t, r in pages:
    detailed_check(t, r)

